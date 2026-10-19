#!/usr/bin/env python3
"""FDF Universal Adoption v0.1: additive, source-only host adapter planner.

No execution of caller scripts, network calls or framework build commands.
Default subcommand 'plan' does not write to project. Apply requires exact digest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

SCHEMA = "fdf.universal-adoption/0.2"
MANIFEST = ".fabrica/ADOPTION_MANIFEST.json"
BEGIN = "<!-- FDF UNIVERSAL ADOPTION BEGIN v0.2 -->"
END = "<!-- FDF UNIVERSAL ADOPTION END v0.2 -->"
POLICIES = ["AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "GEMINI.md", "AI_CRITICAL.md", ".cursorrules", ".github/copilot-instructions.md", "PLANS.md", "GOALS.md", "PROMPTS.md"]
PLATFORMS = ("codex", "cursor", "antigravity", "gemini", "chatgpt", "aistudio")
SKIP = {"node_modules", "vendor", "dist", "build", ".git", ".venv", "venv", ".next", ".turbo", "__pycache__", "target", ".fabrica"}
MAX_POLICY_SIZE = 1024 * 1024


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: bytes | str):
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def require_root(project):
    root = Path(project).absolute()
    if not root.is_dir() or root.is_symlink():
        raise ValueError("HOLD: project root missing or symlinked")
    return root


def safe_path(root, relative):
    if not relative or relative.startswith("/") or "\\" in relative or "\x00" in relative:
        raise ValueError("HOLD: invalid relative target path")
    parts = relative.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise ValueError("HOLD: path traversal")
    cur = root
    for piece in parts:
        cur = cur / piece
        if cur.is_symlink():
            raise ValueError("HOLD: symlink in project path: " + relative)
    return cur


def read_bounded(path, max_bytes=MAX_POLICY_SIZE):
    if path.is_symlink():
        raise ValueError("HOLD: linked files cannot be modified or inspected")
    if not path.exists():
        return None
    st = path.stat()
    if not stat.S_ISREG(st.st_mode) or st.st_size > max_bytes:
        raise ValueError("HOLD: non-regular or oversized file")
    data = path.read_bytes()
    if len(data) > max_bytes:
        raise ValueError("HOLD: file changed or oversized")
    return data


def detect(root):
    # Only static filenames and bounded top-level manifests; never load .env or run code.
    signals = {
      "node": "package.json", "python": "pyproject.toml", "rust": "Cargo.toml", "go": "go.mod",
      "dotnet": "*.sln", "java": "pom.xml", "android": "build.gradle", "swift": "Package.swift"
    }
    found = []
    entries = list(root.iterdir())[:2000]
    names = {p.name for p in entries if not p.is_symlink()}
    for typ, mark in signals.items():
        if mark.startswith("*"):
            if any(n.endswith(mark[1:]) for n in names): found.append(typ)
        elif mark in names and (root / mark).is_file(): found.append(typ)
    frontend = []
    if "package.json" in names:
        data = read_bounded(safe_path(root, "package.json"), 128 * 1024)
        if data is not None:
            try:
                package = json.loads(data)
                both = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
                for p in ("react", "next", "vue", "svelte", "vite", "expo", "@angular/core"):
                    if p in both: frontend.append(p)
            except (ValueError, AttributeError, TypeError):
                frontend.append("package_json_unparsed")
    if any(n in names for n in ("index.html", "src", "app", "pages", "public")) and "web" not in found: frontend.append("possible_web_ui")
    phase = "seed" if len(entries) < 8 else "active"
    if (root / ".git").exists():
        try:
            out = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=3, check=True)
            if Path(out.stdout.strip()).resolve() == root.resolve():
                st = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, timeout=3)
                git_state = "tracked_changes_present" if st.stdout.strip() else "tracked_clean"
            else: git_state = "nested_git_root_unknown"
        except (OSError, subprocess.SubprocessError): git_state = "git_not_verified"
    else: git_state = "no_git_metadata_at_root"
    policies=[]
    for rel in POLICIES:
        path = safe_path(root, rel)
        if path.exists():
            raw = read_bounded(path)
            policies.append({"path":rel, "sha256":digest(raw), "bytes":len(raw)})
    for sub, name in ((".cursor/rules", "cursor_rule_entries"),( ".agents/rules", "antigravity_rule_entries"),
                      (".agents/workflows", "antigravity_workflow_entries"), (".agents/skills", "workspace_skill_entries"),
                      (".gemini/skills", "gemini_skill_entries")):
        d = safe_path(root, sub)
        if d.exists():
            if not d.is_dir(): raise ValueError("HOLD: expected directory exists as file")
            policies.append({"path":sub,"entries":min(200,len(list(d.iterdir())))})
    return {"schema":"fdf.projectdna.surface/0.1","phase_guess":phase, "tech_signals":sorted(found),
            "ui_signals":sorted(set(frontend)), "domain_hints":sorted({"research","papers","publication","notebooks"}.intersection(names)), "git_state":git_state, "known_policies":policies,
            "policy_semantics_read":False,"actual_ide_verified":False,"protected_paths_examined":False,
            "fdf_release_authorized":False}


def contract():
    return """# Fabric – additive project design intelligence

This is a lower-priority **advisory** capability. Run `FDF()` to inspect, plan and guide project-specific evolution after owner-gated installation. Respect existing project AGENTS.md, GEMINI.md, CLAUDE.md, Cursor rules, nested rules, host/global policies, security instructions, owner intent, ongoing tasks and domain identity. Existing host authority always wins. If these instructions conflict, report HOLD, do not reconcile by silently replacing host law.

## Core loop
STATUS → discover actual source and current owner task → ProjectDNA → locate one observable design issue → route minimal FDF skill(s) → ProposalDNA with exact file paths and tests → owner accept/revise/reject. Default PROPOSE_ONLY. No edits, installs, browser requests, commits, network fetch, PR, CONTINUE, PUBLISH or DEPLOY without separately valid host-native user authorization. Source observations and hashes are not semantic policy acceptance or user approval.

## Compatibility
Use the platform's own instructions and skills system where supported. Do not claim files uploaded to ChatGPT or GitHub URLs are automatically mounted, read or executed. No copying of third-party upstream skill text; consult licensed, pinned references only when specifically authorized. FDF/EK adapter is optional, source-pinned, and not a license to automatically install dependencies.

## Evidence
Preserve root project identity, real source baseline, rollback, a11y (including reduced motion), responsiveness, performance and rendered/functional evidence. Missing evidence => HOLD, not PASS. Do not fabricate tests, human reviews, or IDE sessions.
"""


def bridge_line():
    return "Fabric is optional advisory design intelligence. On a design task, read `.fabrica/CONTRACT.md` and `.fabrica/PROJECT_DNA.json` after the host's own instructions. Keep local law and work-in-progress authoritative. No edits without fresh scoped owner approval."


def snippet():
    return (f"{BEGIN}\n" + bridge_line() + "\n" + f"{END}\n")


def templates(profile, platforms):
    data = {}
    data[".fabrica/CONTRACT.md"] = contract()
    data[".fabrica/PROJECT_DNA.json"] = json.dumps(profile, indent=2, sort_keys=True) + "\n"
    data[".fabrica/README.md"] = """# FABRICA.DESIGN.FABRIC – optional integration

This directory describes a project-scoped, reversible design-advice integration, not an imported policy authority. ProjectDNA is a bounded static signal inventory and may be incomplete. Use `CONTRACT.md` as the common platform-neutral behavior; manual cloud adapters are not auto-loaded into ChatGPT/AI Studio. An existing project's own rules remain authoritative. To check source drift use the FDF adopter's `verify` subcommand. Never copy secrets into artifacts.
"""
    if "cursor" in platforms:
        data[".cursor/rules/fabrica-design-fabric.mdc"] = "---\ndescription: Optional design-fabric source-grounded UX review and proposal\nalwaysApply: false\n---\n\n"+bridge_line()+"\n"
    if "antigravity" in platforms:
        data[".agents/rules/fabrica-design-fabric.md"] = "---\ntrigger: model_decision\ndescription: Optional FDF project-scoped design intelligence\n---\n\n# FDF optional workspace rule\n\n"+bridge_line()+"\n"
        data[".agents/skills/fabrica-design-fabric/SKILL.md"] = "---\nname: fabrica-design-fabric\ndescription: Optional source-bound design critique, motion and UI review on the active project, respecting host authority.\n---\n\n# FABRICA.DESIGN.FABRIC\n"+bridge_line()+"\n"
    if "gemini" in platforms:
        data[".gemini/skills/fabrica-design-fabric/SKILL.md"] = "---\nname: fabrica-design-fabric\ndescription: Source-grounded, host-first UI design review and reversible proposal without changing files.\n---\n\n# Fabric Design Review\n"+bridge_line()+"\n"
    if "codex" in platforms:
        data[".fabrica/CODEX_ADOPTION.md"] = "# Codex\n\nCodex reads applicable AGENTS.md context. If root AGENTS.md already exists, do not replace it; optionally append the plan-locked FDF managed block via `--root-hooks append`. Otherwise manually cite `.fabrica/CONTRACT.md` in a task, or enable a root hook with separate approval. An optional skill directory is not equivalent to automatic context loading.\n"
    if "chatgpt" in platforms:
        data[".fabrica/CHATGPT_PROJECT_INSTRUCTIONS.md"] = "# ChatGPT Project – manual project instructions\n\n"+bridge_line()+"\n\nPaste or adapt the above into ChatGPT Project settings, then add project files or approved Drive links as sources. Files in the git repo do NOT automatically change ChatGPT's project configuration. Do not expose private rules or secret files through project sharing.\n"
    if "aistudio" in platforms:
        data[".fabrica/AI_STUDIO_BUILD_PROMPT.md"] = "# Google AI Studio Build – manual setup\n\nBefore prompting Build mode, import/sync the authorized GitHub repository or project snapshot. Ask the agent to review current project files and preserve existing instructions, then consult `.fabrica/CONTRACT.md` for advisory UX proposal only. GitHub sync and Build prompts may modify code; inspect preview/diff and avoid deploy or push without explicit user approval. This file is a copyable prompt, not a verified auto-loaded AI Studio rule.\n"
    srcdir = str(Path(__file__).resolve().parent)
    if srcdir not in sys.path: sys.path.insert(0, srcdir)
    from fdf_kernel import fitted_files
    data.update(fitted_files(profile, platforms))
    return data


def generate_plan(root, platforms, root_hooks):
    if not platforms or set(platforms) - set(PLATFORMS): raise ValueError("HOLD: unsupported adapter requested")
    if root_hooks not in ("none", "append"): raise ValueError("HOLD: invalid root-hook mode")
    context = detect(root)
    files = templates(context, platforms)
    actions = []
    collisions = []
    for rel, content in sorted(files.items()):
        path = safe_path(root, rel)
        prior = read_bounded(path)
        bytes_ = content.encode("utf-8")
        status = "ADD" if prior is None else "ALREADY_PRESENT" if prior == bytes_ else "CONFLICT"
        if status == "CONFLICT": collisions.append(rel)
        actions.append({"path":rel,"kind":"managed_new","status":status,"before":None if prior is None else digest(prior),"after":digest(bytes_),"bytes":len(bytes_)})
    if root_hooks == "append":
        for rel in ("AGENTS.md","GEMINI.md"):
            # Root hook only when the respective adapter needs it.
            if (rel == "AGENTS.md" and "codex" not in platforms) or (rel=="GEMINI.md" and not ("gemini" in platforms or "antigravity" in platforms)):
                continue
            path=safe_path(root,rel); prior=read_bounded(path)
            if prior is not None and (BEGIN.encode() in prior or END.encode() in prior):
                status="CONFLICT";new=b"";collisions.append(rel)
            else:
                # preserve bytes and line endings exactly; add delimited block
                new = (prior or b"") + (b"\n" if prior and not prior.endswith((b"\n",b"\r")) else b"") + snippet().encode("utf-8")
                status="APPEND" if prior else "ADD"
            actions.append({"path":rel,"kind":"root_hook","status":status,"before":None if prior is None else digest(prior),"after":digest(new) if status!="CONFLICT" else None,"bytes":len(new)})
    manifest = safe_path(root, MANIFEST)
    if manifest.exists(): collisions.append(MANIFEST)
    plan={"schema":SCHEMA,"mode":"PLAN_NO_WRITES","platforms":sorted(set(platforms)),"root_hooks":root_hooks,
          "project_root_fingerprint":digest(str(root.resolve())),"projectdna":context,"actions":actions,
          "collisions":sorted(set(collisions)),"permissions":"OWNER_DIGEST_APPROVAL_REQUIRED",
          "real_ide_verified":False,"semantics_accepted":False,"release":"HOLD"}
    plan["plan_sha256"]=digest(dump(plan))
    return plan, files


def atomic_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # O_EXCL: never silently overwrite / follow an existing destination
    fd=os.open(path, os.O_CREAT|os.O_EXCL|os.O_WRONLY|getattr(os,"O_NOFOLLOW",0), 0o644)
    with os.fdopen(fd,"wb") as f:
        f.write(data);f.flush();os.fsync(f.fileno())


def apply(root, plan_sha, platforms, root_hooks):
    plan,files=generate_plan(root,platforms,root_hooks)
    if plan["collisions"]: raise ValueError("HOLD: conflicts: "+", ".join(plan["collisions"]))
    if plan_sha!=plan["plan_sha256"]:raise ValueError("HOLD: plan changed since approval")
    if safe_path(root,MANIFEST).exists():raise ValueError("HOLD: already installed; use verify/rollback")
    # fail fast precondition check before any new writes
    for a in plan["actions"]:
        prior=read_bounded(safe_path(root,a["path"]))
        if (None if prior is None else digest(prior))!=a["before"]:raise ValueError("HOLD: drift on "+a["path"])
    written=[]
    try:
        for a in plan["actions"]:
            p=safe_path(root,a["path"])
            if a["status"]=="ALREADY_PRESENT": continue
            if a["kind"]=="root_hook":
                prior=read_bounded(p)
                tail=(b"\n" if prior and not prior.endswith((b"\n",b"\r")) else b"")+snippet().encode("utf-8")
                if prior is not None:
                    # Existing root is not overwritten: append only after exact digest recheck
                    if digest(prior)!=a["before"]:raise ValueError("HOLD: root drift")
                    with open(p,"ab") as out:out.write(tail);out.flush();os.fsync(out.fileno())
                    written.append((p,prior,True))
                else:
                    atomic_new(p,tail);written.append((p,None,False))
            else:
                atomic_new(p,files[a["path"]].encode("utf-8"));written.append((p,None,False))
        record={"schema":SCHEMA,"plan_sha256":plan_sha,"paths":plan["actions"],"platforms":plan["platforms"],
                "root_hooks":root_hooks,"state":"ADD_ONLY_NO_IDE_ATTESTATION","release":"HOLD"}
        atomic_new(safe_path(root,MANIFEST),(json.dumps(record,indent=2,sort_keys=True)+"\n").encode())
    except Exception:
        # Best-effort rollback of this single local operation; report failure rather than silently claim success
        for p,old,appended in reversed(written):
            try:
                if appended:
                    with open(p,"r+b") as f:f.truncate(len(old))
                else:p.unlink()
            except OSError:pass
        raise
    return {"applied":True,"files_new":len([x for x in written if not x[2]]),"root_hooks_appended":len([x for x in written if x[2]]),
            "release":"HOLD","ide_execution_proven":False}


def manifest_data(root):
    m=read_bounded(safe_path(root,MANIFEST))
    if not m:raise ValueError("HOLD: installation manifest missing")
    d=json.loads(m)
    if d.get("schema")!=SCHEMA or not isinstance(d.get("paths"),list):raise ValueError("HOLD: unsupported manifest")
    return d


def verify(root):
    m=manifest_data(root)
    changed=[]
    for a in m["paths"]:
        p=safe_path(root,a["path"])
        raw=read_bounded(p)
        if raw is None or digest(raw)!=a["after"]:changed.append(a["path"])
    return {"schema":SCHEMA,"verdict":"HOLD_FILES_MODIFIED" if changed else "INSTALLED_SOURCE_HASHES_MATCH",
            "changed":changed,"release":"HOLD","actual_ide_verified":False,"host_policy_authority":"NOT_ATTESTED"}


def rollback(root, exact_sha):
    m=manifest_data(root)
    if m["plan_sha256"]!=exact_sha:raise ValueError("HOLD: wrong installation plan id")
    result=verify(root)
    if result["changed"]:raise ValueError("HOLD: modified install paths, do not destroy user edits")
    for a in reversed(m["paths"]):
        if a["status"]=="ALREADY_PRESENT":continue
        p=safe_path(root,a["path"])
        if a["kind"]=="root_hook" and a["before"] is not None:
            data=read_bounded(p)
            tail=snippet().encode("utf-8")
            if not data.endswith(tail):raise ValueError("HOLD: root managed block changed")
            trimmed=data[:-len(tail)]
            if digest(trimmed)!=a["before"]:
                if trimmed.endswith(b"\n") and digest(trimmed[:-1])==a["before"]:trimmed=trimmed[:-1]
                else:raise ValueError("HOLD: prefix was modified")
            with open(p,"wb") as f:f.write(trimmed)
        else:p.unlink()
    safe_path(root,MANIFEST).unlink()
    return {"rolled_back":True,"release":"HOLD","user_existing_files_preserved":True}


def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("command",choices=("inspect","plan","apply","verify","rollback"))
    a.add_argument("--project",required=True)
    a.add_argument("--platforms",default=",".join(PLATFORMS))
    a.add_argument("--root-hooks",choices=("none","append"),default="none")
    a.add_argument("--approve-plan",default=None)
    args=a.parse_args(argv)
    try:
        root=require_root(args.project)
        platforms=[x.strip() for x in args.platforms.split(",") if x.strip()]
        if len(platforms)!=len(set(platforms)):raise ValueError("HOLD: duplicate platform name")
        if args.command=="inspect":value=detect(root)
        elif args.command=="plan":value=generate_plan(root,platforms,args.root_hooks)[0]
        elif args.command=="apply":
            if not args.approve_plan:raise ValueError("HOLD: apply requires --approve-plan <plan_sha256>")
            value=apply(root,args.approve_plan,platforms,args.root_hooks)
        elif args.command=="verify":value=verify(root)
        else:
            if not args.approve_plan:raise ValueError("HOLD: rollback needs approved installation plan id")
            value=rollback(root,args.approve_plan)
        print(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True))
    except (ValueError,OSError,json.JSONDecodeError,UnicodeError,subprocess.SubprocessError) as e:
        print("HOLD: "+str(e),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":sys.exit(main())
