"""FDF 0.2 first-party kernel and skill lattice. Pure template generation, no IO."""
from __future__ import annotations
import json

KERNEL_SCHEMA = "fdf.kernel-lattice/0.2"
UPSTREAM_EK_PIN = "2d228630ba1446365f614a108cb8252f1feda202"

# First-party original skills; no vendor text or external executable code.
CATALOG = {
 "fdf-project-observer": ("Observe an existing project's policies, code signals and active task before planning changes.", "Observe only bounded source and source metadata. Identify active work, protected paths and unresolved constraints; report unknown global or nested instructions as UNKNOWN rather than inventing authority."),
 "fdf-governance-gate": ("Check permissions, policy precedence, evidence provenance and human decision gates.", "Preserve host authority. Require exact source scope and recorded accept/reject before edits; fail closed for missing policies, tests, approval or permission."),
 "fdf-evolution-planner": ("Build reversible ProposalDNA and maintain guided, versioned project improvement cycles.", "Propose one project-specific next cycle with source-bound intent, impact, verification, rollback and next handoff. No self-promoting autonomous changes."),
 "fdf-verification-engine": ("Derive reproducible regression, security and release gates for proposed changes.", "Identify available real project tests. Propose verification first; run only with the host's explicit authorization. Do not claim test execution without logs."),
 "fdf-design-critic": ("Assess actual UI hierarchy, coherence, content and responsiveness while retaining brand identity.", "Source-ground the critique; do not replace existing design identity. Prefer a small reversible improvement with rendered evidence."),
 "fdf-accessibility-review": ("Audit keyboard, semantics, contrast, reduced motion and touch behavior for an existing UI.", "List specific test conditions; static heuristics do not establish WCAG conformance. Require real runtime evidence before PASS."),
 "fdf-motion-director": ("Plan purposeful accessible motion and animation performance for interfaces.", "Use purposeful motion only. Reduced-motion path and measurements are mandatory; do not add animation dependencies automatically."),
 "fdf-runtime-architecture": ("Map service boundaries, dependencies, invariants and operational risk in a software runtime.", "Map current architecture before proposing extensions. Existing domain and security invariants outrank optimizations."),
 "fdf-research-provenance": ("Trace research, data and publication claims to reproducible sources.", "Protect distinction among hypothesis, simulation, proof, measurement, and external validation. Never promote scientific claims by rewriting prose."),
}

ALWAYS = ("fdf-project-observer", "fdf-governance-gate", "fdf-evolution-planner", "fdf-verification-engine")

def select(profile):
    ui = bool(profile.get("ui_signals"))
    code = bool(profile.get("tech_signals"))
    phase = profile.get("phase_guess", "unknown")
    policy_paths = {p["path"] for p in profile.get("known_policies",[]) if isinstance(p,dict) and "path" in p}
    orchestration = sorted(policy_paths.intersection({"AGENTS.md","GEMINI.md","CLAUDE.md","AI_CRITICAL.md",".cursor/rules",".agents/rules",".agents/skills"}))
    # Existing files indicate a probable kernel surface, not semantic acceptance.
    mode = "AUGMENT_EXISTING_UNVERIFIED" if orchestration else "SCAFFOLD_ADVISORY_KERNEL"
    selected=[]
    for k in ALWAYS: selected.append({"name":k,"score":100,"reason":"constitutional universal default"})
    if ui:
        selected.extend(({"name":"fdf-design-critic","score":90,"reason":"UI/front-end source signals"},
                         {"name":"fdf-accessibility-review","score":90,"reason":"UI/front-end source signals"},
                         {"name":"fdf-motion-director","score":65,"reason":"UI motion relevance; use only for motion tasks"}))
    if code:
        selected.append({"name":"fdf-runtime-architecture","score":78,"reason":"software stack detected"})
    # Scientific/academic domain cannot be established from top-level filenames alone.
    hints=sorted({"research","papers","publication","notebooks"}.intersection(set(profile.get("domain_hints",[]))))
    if hints:
        selected.append({"name":"fdf-research-provenance","score":82,"reason":"explicit research-domain signal"})
    return {"schema":KERNEL_SCHEMA,"mode":mode,"observed_orchestration_paths":orchestration,
            "stage_guess":phase,"selected":selected,
            "upstream_optional":{"repo":"emilkowalski/skills","commit":UPSTREAM_EK_PIN,
                "mode":"REFERENCE_ONLY_NOT_INSTALLED","requires_license_review":True},
            "authority":"PROJECT_AND_HOST_FIRST","all_skills_auto_executed":False,
            "auto_evolution":"GUIDED_PROPOSAL_ONLY","actual_host_semantics_verified":False,
            "model_weights_finetuned":False,"release":"HOLD"}

def skill_text(name):
    desc, body = CATALOG[name]
    return (f"---\nname: {name}\ndescription: {desc}\n---\n\n"
            f"# {name}\n\n{body}\n\n"
            "## FDF() orchestration\n"
            "Read `.fabrica/KERNEL.md`, `.fabrica/SKILL_LATTICE.json` and active project rules first. "
            "Use STATUS → ProjectDNA → one evidence-grounded ProposalDNA → human decision → host-authorized changes → tests → handoff. "
            "No install, edit, network call, merge, publish or deploy merely because this skill is discovered.\n")

def common_kernel(lattice):
    return ("# FABRICA.DESIGN.FABRIC · Project Kernel 0.2\n\n"
      "Entry: `FDF()` (in a model chat) or `python tools/fdf.py FDF --project PATH` from a separate installer checkout.\n\n"
      f"Intake mode: **{lattice['mode']}** (static signal only; original host instructions have not been interpreted).\n\n"
      "Host/global/nested AGENTS.md, GEMINI.md, CLAUDE.md, IDE policies, security rules, tests, Git state, and human permissions take precedence. "
      "Do not override an existing intelligence kernel. If none was detected, this is a minimal *advisory* kernel, not self-authorized governance.\n\n"
      "## Execution protocol\n"
      "FDF() → STATUS → MAP → CLASSIFY → SELECT SKILLS → BUILD PROPOSAL → HUMAN APPROVE/REVISE/REJECT → "
      "HOST-BOUND EXECUTION (optional) → TEST / WITNESS → RECORD HANDOFF → NEXT().\n\n"
      "Autonomous means proactive *analysis and proposals*, never unapproved writes, installations, deployments or self-modification. "
      "No change to model weights. Human-approved updates use versioned review and explicit rollback.\n")

def fitted_files(profile, platforms):
    lattice=select(profile)
    out={
      ".fabrica/KERNEL.md":common_kernel(lattice),
      ".fabrica/SKILL_LATTICE.json":json.dumps(lattice,indent=2,sort_keys=True)+"\n",
      ".fabrica/EVOLUTION_POLICY.md":("# FDF guided evolution\n\nFDF() may autonomously inspect available evidence and propose a cycle. "
       "Never auto-apply changes, install third-party skills or write back to canonical R&D documents without separately approved scope. "
       "For each cycle record source hash, law conflicts, exact change, test evidence, rollback and human decision. "
       "A new owner-approved version may be planned and migrated; avoid overwriting prior managed files.\n"),
      ".fabrica/STATE_AND_HANDOFF.md":("# Fabric project-local handoff\n\nStatus: BOOTSTRAPPED_ADVISORY_ONLY\n"
       "Project policies: NOT_SEMANTICALLY_ATTESTED\nSkills: FIT_RANKED_NOT_AUTO_ACTIVATED\n"
       "Owner adoption: PLAN-DIGEST_ONLY_NOT_IDENTITY_ATTESTATION\n"
       "Next: run host-native STATUS, inspect selected rules and offer one reversible ProposalDNA.\n"),
      ".fabrica/PROPOSAL_TEMPLATE.md":("# ProposalDNA\n\nObserved files/commit: UNKNOWN\nHost laws inspected: UNKNOWN\n"
       "One design/runtime/research objective: UNDECIDED\n"
       "Affected files and data permissions: UNDECIDED\nRisk and rollback: UNDECIDED\n"
       "Validation: NOT_RUN\nOwner decision: PENDING_NOT_GIVEN\n")
    }
    chosen=[x["name"] for x in lattice["selected"]]
    if "codex" in platforms or "antigravity" in platforms:
        for name in chosen:out[f".agents/skills/{name}/SKILL.md"]=skill_text(name)
    if "gemini" in platforms:
        for name in chosen:out[f".gemini/skills/{name}/SKILL.md"]=skill_text(name)
    if "chatgpt" in platforms:
        out[".fabrica/CHATGPT_FDF_INJECTION.md"]=("# ChatGPT Project — FDF() manual bootstrap\n"
          "Paste this into project instructions only after checking existing project law: FDF() means inspect uploaded/connected sources, "
          "honor native project instructions, read PROJECT_DNA and KERNEL; propose one grounded change for approval. "
          "Never treat a local file as magically attached.\n")
    if "aistudio" in platforms:
        out[".fabrica/AISTUDIO_FDF_INJECTION.md"]=("# Google AI Studio Build — FDF() manual bootstrap\n"
          "Import approved project snapshot via GitHub and use this prompt before making changes: "
          "FDF() inspect the repository and current Build prompt context, identify existing rules and component design, "
          "propose an additive fit-ranked skill set and a single bounded change. Stop before code edits, pushes, secrets, or deployment. "
          "Host user must review every suggested edit.\n")
    return out
