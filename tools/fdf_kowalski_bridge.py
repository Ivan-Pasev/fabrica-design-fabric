"""Read-only routing of pinned external design skills into FDF KBI. No network or mutations."""
import argparse
import json
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "registry" / "upstream-emil-kowalski.v1.json"
ROUTES = {
    "motion-build": ("animate", "animation-performance"),
    "expo-motion-build": ("animate-expo",),
    "motion-audit": ("improve-animations", "animation-performance"),
    "motion-discover": ("find-animation-opportunities",),
    "motion-review": ("review-animations",),
    "motion-vocabulary": ("animation-vocabulary",),
    "design-critique": ("emil-design-eng",),
    "ui-stress": ("break-ui",),
    "mobile-web": ("mobile-native",),
    "apple-style": ("apple-design",),
    "ui-library-choice": ("pick-ui-library",),
    "prototype-variants": ("prototype",),
    "sonner-toasts": ("ask-sonner",),
    "swift-code": ("write-swift",),
}
WEB = {"web", "react", "nextjs"}
FRAMEWORKS = WEB | {"expo", "swift", "unknown"}

def route(framework: str, intent: str, *, explicit: bool = False, project_known: bool = False) -> dict:
    if framework not in FRAMEWORKS:
        raise ValueError("unknown framework; use web/react/nextjs/expo/swift/unknown")
    if intent not in ROUTES:
        raise ValueError("unknown intent")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    lookup = {item["id"]: item for item in registry["skills"]}
    chosen = [lookup[k] for k in ROUTES[intent]]
    source = registry["upstream"]
    def result(status, refs=()):
        return {
            "schema": "fdf.kbi.external-reference-route/0.1",
            "status": status,
            "mode": "PROPOSE_ONLY",
            "owner_authorized": False,
            "writes_performed": False,
            "executed_upstream": False,
            "installed_dependencies": False,
            "target": "CALLER_IDE_ACTIVE_WORKSPACE",
            "framework": framework,
            "intent": intent,
            "upstream_commit": source["commit"],
            "license": source["license"],
            "source_mode": "PINNED_REFERENCE_NOT_VENDORED",
            "selected": [
                {"id": x["id"], "git_blob_sha": x["git_blob_sha"],
                 "url": f'https://github.com/{source["repo"]}/blob/{source["commit"]}/{x["source_path"]}',
                 "admission": x["admission"]} for x in refs
            ],
            "next_action": "VERIFY_CALLER_PROJECT_THEN_HUMAN_DECISION",
            "release_admission": "HOLD",
        }
    if not project_known or framework == "unknown":
        return result("HOLD_PROJECT_CONTEXT")
    if intent == "expo-motion-build" and framework != "expo":
        return result("HOLD_FRAMEWORK_MISMATCH")
    if intent == "swift-code" and framework != "swift":
        return result("HOLD_FRAMEWORK_MISMATCH")
    if intent in {"motion-build","motion-audit","motion-discover","motion-review","motion-vocabulary",
                  "design-critique","ui-stress","mobile-web","apple-style","ui-library-choice","prototype-variants"} and framework not in WEB:
        return result("HOLD_FRAMEWORK_MISMATCH")
    if intent == "sonner-toasts" and framework not in {"react","nextjs"}:
        return result("HOLD_FRAMEWORK_MISMATCH")
    if any(x["explicit_only"] for x in chosen) and not explicit:
        return result("HOLD_EXPLICIT_USER_INVOCATION")
    return result("REFERENCE_SELECTED_PROPOSAL_ONLY", chosen)

def main():
    parser = argparse.ArgumentParser(description="Read-only, pinned source-reference routing for FDF KBI")
    parser.add_argument("--framework", required=True, choices=sorted(FRAMEWORKS))
    parser.add_argument("--intent", required=True, choices=sorted(ROUTES))
    parser.add_argument("--explicit-user-invocation", action="store_true")
    parser.add_argument("--project-known", action="store_true")
    args = parser.parse_args()
    print(json.dumps(route(args.framework,args.intent,explicit=args.explicit_user_invocation,
                           project_known=args.project_known),indent=2,sort_keys=True))
if __name__ == "__main__":
    main()
