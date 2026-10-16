#!/usr/bin/env python3
"""FDF KBI ProposalDNA v0.2: read-only, coverage-bound source proposals.

This is a bounded evidence compiler, not a code editor or security sandbox.
Input receipts must be generated from the same caller workspace and are fully
rechecked against an actual fresh scan before any proposals are emitted.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.fdf_workspace_probe import scan

SUPPORTED = {
    'img_missing_alt': {
        'kernel': 'fdf-accessibility-warden',
        'intent': 'Review the actual image purpose and supply an appropriate alt attribute.',
        'implementation': 'At the observed <img> tag, add alt={APPROVED_DESCRIPTION} or alt="" for genuinely decorative content.',
        'requires_decision': ['Is this image informative, functional or decorative?', 'What exact description is supported by surrounding context?'],
        'validation': ['Review the rendered image and context with a human.', 'Verify the computed accessible name and assistive-technology output.'],
    },
    'icon_button_name': {
        'kernel': 'fdf-accessibility-warden',
        'intent': 'Determine and expose the button action to assistive technology.',
        'implementation': 'At the observed icon button, provide an approved accessible action name via visible text or aria-label.',
        'requires_decision': ['What action does this button actually invoke?', 'Is a visible text label preferable to aria-label?'],
        'validation': ['Check keyboard focus, activation and disabled/loading states.', 'Inspect computed accessible name and action semantics.'],
    },
    'reduced_motion_equivalence': {
        'kernel': 'fdf-motion-director',
        'intent': 'Make nonessential motion optional while preserving the intended information.',
        'implementation': 'After identifying the specific animated selector, add a scoped prefers-reduced-motion alternative; preserve meaningful state cues.',
        'requires_decision': ['Which exact animations are nonessential?', 'What alternative preserves state and affordance?'],
        'validation': ['Test both reduced and normal motion with keyboard interactions.', 'Measure observed CSS behavior and focus visibility on representative devices.'],
    },
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def stable_json(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')

def _observed(receipt):
    a = receipt.get('candidate_changes', [])
    return sorted((x.get('path'), x.get('line'), x.get('rule'), x.get('source_excerpt_sha256')) for x in a)

def compile_plan(project, receipt):
    if not isinstance(receipt, dict) or receipt.get('schema') != 'fdf.caller-project-design-proposal/0.1':
        raise ValueError('unsupported receipt schema')
    if receipt.get('mode') != 'PROPOSE_ONLY' or receipt.get('mutations_performed') is not False:
        raise ValueError('receipt must be non-mutating')
    if receipt.get('target', receipt.get('target_role')) != 'CALLER_IDE_ACTIVE_WORKSPACE':
        raise ValueError('wrong target role')
    if receipt.get('approval_required_for_mutation', True) is not True:
        raise ValueError('receipt cannot relax the human authorization gate')
    if receipt.get('tests_executed', []) != []:
        raise ValueError('scanner receipts cannot assert executed tests')
    original = receipt.get('observed_files')
    candidates = receipt.get('candidate_changes')
    if not isinstance(original, list) or not isinstance(candidates, list) or len(original) > 120 or len(candidates) > 600:
        raise ValueError('unbounded source claims')
    live = scan(project)
    actual_files = live['observed_files']
    if sorted((f.get('path'), f.get('sha256'), f.get('bytes')) for f in original) != sorted((f['path'], f['sha256'], f['bytes']) for f in actual_files):
        raise ValueError('source identity stale or fabricated')
    if _observed(receipt) != _observed(live):
        raise ValueError('proposal anchors stale or fabricated')
    if len(set(_observed(live))) != len(candidates):
        raise ValueError('duplicate candidate anchors')

    # Every coverage claim is checked against a newly measured live scan.
    # R28 receipts without coverage remain readable but are never promoted
    # to complete, even when today's scan covers all eligible source files.
    current_coverage = live['coverage']
    has_coverage = 'coverage' in receipt
    if has_coverage:
        if (not isinstance(receipt['coverage'], dict)
                or receipt['coverage'] != current_coverage):
            raise ValueError('coverage stale, forged or incompatible')
        if receipt.get('skipped') != live['skipped']:
            raise ValueError('coverage skipped-file evidence mismatch')
    if not current_coverage['complete']:
        admission = 'HOLD_INCOMPLETE'
        effective_verdict = 'INCOMPLETE'
    elif not has_coverage:
        admission = 'HOLD_UNKNOWN_LEGACY'
        effective_verdict = 'UNKNOWN_LEGACY'
    else:
        admission = 'PASS_SCOPED'
        effective_verdict = 'COMPLETE_WITHIN_DECLARED_SCOPE'
    coverage_binding = {
        'schema': 'fdf.kbi.coverage-binding/0.1',
        'admission': admission,
        'verdict': effective_verdict,
        'receipt_kind': 'R30_COVERAGE' if has_coverage else 'R28_LEGACY_NO_COVERAGE',
        'fresh_scan_sha256': digest(stable_json(current_coverage)),
        'receipt_coverage_sha256': digest(stable_json(receipt['coverage'])) if has_coverage else None,
        'current_scan': current_coverage,
        'scope_limited': True,
        'complete_project_audit': False,
        'owner_authorized': False,
        'reason': ('Source survey is complete only for the scanner declared eligible scope.'
                   if admission == 'PASS_SCOPED' else
                   'Fresh scan proves source survey incomplete.'
                   if admission == 'HOLD_INCOMPLETE' else
                   'Legacy receipt has no coverage attestation; no completeness promotion.'),
    }

    items = []
    for x in sorted(candidates, key=lambda x:(x['path'],x['line'],x['rule'])):
        rule=x['rule']
        if rule not in SUPPORTED or x.get('status') != 'HUMAN_REVIEW_REQUIRED':
            raise ValueError('unknown or inflated finding')
        kind=SUPPORTED[rule]
        items.append({
          'path':x['path'], 'line':x['line'],'source_excerpt_sha256':x['source_excerpt_sha256'],
          'rule':rule,'kernel':kind['kernel'],'intent':kind['intent'],
          'implementation_guidance_not_patch':kind['implementation'],
          'semantic_questions':kind['requires_decision'], 'required_validation':kind['validation'],
          'status':'PENDING_HUMAN_CONTEXT','executable_patch':None, 'owner_authorized':False,
          'rollback':'Restore the recorded original file bytes from the owner-approved baseline if implementation is later authorized.'
        })
    return {
       'schema':'fdf.kbi.proposaldna/0.2', 'target':'CALLER_IDE_ACTIVE_WORKSPACE',
       'mode':'PROPOSE_ONLY','source_files':actual_files,
       'observations_sha256':digest(stable_json(live)),
       'coverage_binding':coverage_binding, 'coverage_admission':admission,
       'proposals':items,'mutations_performed':False,'owner_approval_required':True,
       'all_runtime_checks':'NOT_EXECUTED',
       'limitations':['No executable patches until contextual human decisions are resolved.',
           'Regex source analysis is incomplete and may produce false positives or negatives.',
           'No browser, assistive technology, IDE integration, design jury or production tests executed.',
           'Source content hashes are integrity markers, not authenticated project provenance.',
           'Coverage PASS_SCOPED refers only to selected extensions, allowed directories and scanner limits.',
           'Incomplete or legacy-unknown coverage cannot authorize mutations or certify whole-project design quality.']
    }

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',required=True)
    evidence=parser.add_mutually_exclusive_group(required=True)
    evidence.add_argument('--observations')
    evidence.add_argument('--live',action='store_true',help='Generate/recheck observations entirely in memory; no receipt file write')
    args=parser.parse_args()
    if not args.live:
        rp=Path(args.observations)
        if rp.is_symlink() or not rp.is_file() or rp.stat().st_size > 512*1024:
            raise SystemExit('HOLD: invalid receipt input')
    try:
        receipt=scan(args.project) if args.live else json.loads(rp.read_text('utf-8'))
        print(json.dumps(compile_plan(args.project,receipt),indent=2,sort_keys=True))
    except (OSError,UnicodeError,ValueError,TypeError,KeyError) as ex:
        raise SystemExit('HOLD: '+str(ex))
