#!/usr/bin/env python3
"""Bounded source observations for the currently open IDE project.

This is a heuristic read-only scanner, NOT a source parser, OS sandbox, or
WCAG certification. Coverage is explicitly qualified for every invocation.
"""
import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

SKIP = {'.git', '.next', '.nuxt', '.svelte-kit', 'node_modules', 'dist',
        'build', 'coverage', '.venv', 'venv', 'vendor', '.secrets', '.cache',
        '.idea', '.vscode', '__tests__'}
EXT = {'.tsx', '.jsx', '.html', '.vue', '.svelte', '.css'}
MAX_BYTES = 65536
MAX_FILES = 120
MAX_DEPTH = 5
MAX_FINDINGS_PER_RULE = 5


def _canonical_authorized_root(project):
    """Deny symlinks in supplied project path (including ancestors).

    This rejects paths whose *spelling* involves a symlink, even when the
    resulting realpath is legitimate. It is NOT a sandbox or ownership test.
    """
    requested = Path(project).expanduser()
    if '..' in requested.parts:
        raise ValueError('HOLD: parent traversal in project path')
    root = Path(os.path.abspath(str(requested)))
    for node in (*reversed(root.parents), root):
        if node.is_symlink():
            raise ValueError('HOLD: symlinked project path component')
    if not root.is_dir():
        raise ValueError('Expected real, non-symlink project directory')
    return root


def _bounded_regular_file(path):
    """Return bytes, or (None, explicit reason); never read >MAX_BYTES+1."""
    try:
        if path.is_symlink():
            return None, 'symlink'
        # O_NOFOLLOW closes the final symlink substitution case on POSIX.
        # Where unavailable, this function does not claim strong containment.
        flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0)
        if hasattr(os, 'O_NOFOLLOW'):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                return None, 'not_regular'
            if info.st_size > MAX_BYTES:
                return None, 'oversized'
            data = stream.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                return None, 'oversized'
        if b'\0' in data:
            return None, 'binary'
        return data, None
    except OSError:
        return None, 'unreadable'


def _css_without_comments(content):
    """Remove CSS block comments; preserve line breaks for approximate audit."""
    return re.sub(r'/\*[\s\S]*?\*/', lambda m: '\n' * m.group().count('\n'), content)


def _has_reduced_motion_override(content):
    """Require a reduction declaration INSIDE a balanced matching media block.

    This source heuristic does not prove selector equivalence or computed CSS.
    """
    media = re.compile(r'@media\s*[^{}]*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)\s*\{', re.I)
    reducer = re.compile(r'(?<![\w-])(?:animation|transition)\s*:\s*none\b|'
                         r'(?<![\w-])animation-duration\s*:\s*0(?:s|ms)\b', re.I)
    for match in media.finditer(content):
        depth = 1
        close = match.end()
        while close < len(content) and depth:
            if content[close] == '{': depth += 1
            elif content[close] == '}': depth -= 1
            close += 1
        if depth == 0 and reducer.search(content[match.end():close-1]):
            return True
    return False


def _skip_jsx_expression(tag, start):
    """Skip balanced {...} expression with quoted literals; not a JSX parser."""
    depth, index, quote = 1, start + 1, None
    while index < len(tag):
        char = tag[index]
        if quote:
            if char == '\\':
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in ('"', "'", '`'):
            quote = char
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if not depth:
                return index + 1
        index += 1
    return None


def _attribute_present(tag, name):
    """Find an explicit attribute assignment on the opening tag only.

    Skip other attributes' quoted/unquoted values and JSX {...} expressions:
    text resembling alt= or aria-label= inside a value must not count.
    Heuristic only; spreads, templates, malformed tags and component semantics
    require host-project contextual review.
    """
    opening = re.match(r'<[a-z][\w:-]*\b', tag, re.I)
    if not opening:
        return False
    index, length = opening.end(), len(tag)
    while index < length:
        while index < length and tag[index].isspace():
            index += 1
        if index >= length or tag[index] in '/>':
            return False
        if tag[index] == '{':
            index = _skip_jsx_expression(tag, index)
            if index is None:
                return False
            continue
        start = index
        while index < length and not tag[index].isspace() and tag[index] not in '=/>{"\'':
            index += 1
        if start == index:
            return False
        attribute = tag[start:index]
        while index < length and tag[index].isspace():
            index += 1
        if index >= length or tag[index] != '=':
            continue
        index += 1
        while index < length and tag[index].isspace():
            index += 1
        if index >= length or tag[index] == '>':
            return False
        if attribute.lower() == name.lower():
            return True
        if tag[index] in ('"', "'"):
            quote = tag[index]
            index += 1
            while index < length:
                if tag[index] == '\\':
                    index += 2
                elif tag[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
            else:
                return False
        elif tag[index] == '{':
            index = _skip_jsx_expression(tag, index)
            if index is None:
                return False
        else:
            while index < length and not tag[index].isspace() and tag[index] != '>':
                index += 1
    return False


def scan(project):
    root = _canonical_authorized_root(project)
    observed, changes, skipped = [], [], []
    eligible = 0
    skipped_count = 0
    limit_hit = False
    depth_limited = False
    symlink_dirs_skipped = 0
    walk_error_count = 0
    walk_unvisited = set()
    walk_error_examples = []

    def note_walk_error(error):
        nonlocal walk_error_count
        walk_error_count += 1
        if len(walk_error_examples) < 8:
            # Store only an error class; never emit absolute caller filesystem paths.
            walk_error_examples.append(type(error).__name__)

    for base, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=note_walk_error):
        here = Path(base)
        depth = len(here.relative_to(root).parts)
        walk_unvisited.discard(here.relative_to(root).as_posix())
        if depth >= MAX_DEPTH:
            # Don't claim all eligible descendants were examined.
            if any(d not in SKIP and not d.startswith('.') for d in dirs):
                depth_limited = True
            dirs[:] = []
        else:
            admissible = [d for d in dirs if d not in SKIP and not d.startswith('.')]
            symlink_dirs_skipped += sum((here / d).is_symlink() for d in admissible)
            dirs[:] = sorted(d for d in admissible if not (here / d).is_symlink())
            walk_unvisited.update((here / d).relative_to(root).as_posix() for d in dirs)
        for name in sorted(files):
            path = here / name
            rel = path.relative_to(root).as_posix()
            if (path.suffix.lower() not in EXT or
                any(part in SKIP or part.startswith('.') for part in Path(rel).parts)):
                continue
            eligible += 1
            if len(observed) >= MAX_FILES:
                limit_hit = True
                skipped_count += 1
                if len(skipped) < 128:
                    skipped.append({'path': rel, 'reason': 'file_cap'})
                # Stop at first proof of truncation, bounding discovery effort.
                break
            data, reason = _bounded_regular_file(path)
            if reason:
                skipped_count += 1
                if len(skipped) < 128:
                    skipped.append({'path': rel, 'reason': reason})
                continue
            try:
                content = data.decode('utf-8')
            except UnicodeError:
                skipped_count += 1
                if len(skipped) < 128:
                    skipped.append({'path': rel, 'reason': 'invalid_utf8'})
                continue
            digest = hashlib.sha256(data).hexdigest()
            observed.append({'path': rel, 'bytes': len(data), 'sha256': digest})
            if path.suffix.lower() == '.css':
                clean = _css_without_comments(content)
                if (re.search(r'\banimation\s*:|@keyframes\b', clean, re.I)
                        and not _has_reduced_motion_override(clean)):
                    changes.append({'path': rel, 'line': 1,
                        'rule': 'reduced_motion_equivalence',
                        'proposal': 'Audit CSS animations; provide prefers-reduced-motion functional parity.',
                        'source_excerpt_sha256': digest,
                        'status': 'HUMAN_REVIEW_REQUIRED'})
                continue
            for m in list(re.finditer(r'<img\b[^>]*>', content, re.I | re.S))[:MAX_FINDINGS_PER_RULE]:
                if not _attribute_present(m.group(), 'alt'):
                    changes.append({'path': rel,
                        'line': content.count('\n', 0, m.start()) + 1,
                        'rule': 'img_missing_alt',
                        'proposal': 'Determine image purpose; supply accurate alt text or alt="" when decorative.',
                        'source_excerpt_sha256': hashlib.sha256(m.group().encode()).hexdigest(),
                        'status': 'HUMAN_REVIEW_REQUIRED'})
            for m in list(re.finditer(r'<button\b[^>]*>\s*(?:<svg\b[\s\S]*?</svg>\s*)+</button\s*>', content, re.I))[:MAX_FINDINGS_PER_RULE]:
                if not (_attribute_present(m.group(), 'aria-label') or _attribute_present(m.group(), 'aria-labelledby')):
                    changes.append({'path': rel,
                        'line': content.count('\n', 0, m.start()) + 1,
                        'rule': 'icon_button_name',
                        'proposal': 'Add a meaningful accessible name that describes the button action.',
                        'source_excerpt_sha256': hashlib.sha256(m.group().encode()).hexdigest(),
                        'status': 'HUMAN_REVIEW_REQUIRED'})
        if limit_hit:
            break

    coverage_complete = not (limit_hit or depth_limited or skipped_count or symlink_dirs_skipped or walk_error_count or walk_unvisited)
    coverage = {
        'complete': bool(coverage_complete),
        'eligible_files_at_least': eligible,
        'observed_files': len(observed),
        'skipped_files_recorded': skipped_count,
        'file_cap_reached': bool(limit_hit),
        'depth_cap_reached': bool(depth_limited),
        'symlink_directories_skipped': symlink_dirs_skipped,
        'walk_errors': walk_error_count,
        'walk_error_types': walk_error_examples,
        'unvisited_directories': len(walk_unvisited),
        'counts_are_lower_bounds_when_capped': bool(limit_hit or depth_limited),
        'scope': 'eligible .tsx/.jsx/.html/.vue/.svelte/.css outside configured exclusion directories',
        'verdict': 'COMPLETE_WITHIN_DECLARED_SCOPE' if coverage_complete else 'INCOMPLETE',
    }
    return {
        'schema': 'fdf.caller-project-design-proposal/0.1',
        'target': 'CALLER_IDE_ACTIVE_WORKSPACE',
        'mode': 'PROPOSE_ONLY',
        'observed_files': observed,
        'candidate_changes': changes,
        'skipped': skipped,
        'coverage': coverage,
        'mutations_performed': False,
        'tests_executed': [],
        'approval_required_for_mutation': True,
        'limitations': [
            'Regex heuristics, not AST or complete design audit',
            'No file mutation or target code execution',
            'Only source hashes and file anchors emitted, not source contents',
            'Coverage_complete is limited to eligible extensions and exclusion policy, not full-project semantic coverage',
            'Race resistance is best effort; the scanner is not a filesystem sandbox',
            'R39 quote-aware attributes and reduced-motion checks remain heuristics, not AST/DOM proofs',
            'Real IDE URL handoff and actual quality improvement still unverified',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', default='.')
    print(json.dumps(scan(parser.parse_args().project), indent=2, sort_keys=True))
