"""FDF/EK pinned-reference contract regressions; no network or target writes."""
import json
import unittest
from tools.fdf_kowalski_bridge import REGISTRY, ROUTES, route

class KowalskiBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_inventory(self):
        a = self.m["skills"]
        self.assertEqual(len(a), 15)
        self.assertEqual(len({x["id"] for x in a}), 15)
        self.assertEqual(len(self.m["supporting_references"]),8)
        self.assertTrue(all(len(x["git_blob_sha"]) == 40 for x in a))

    def test_license_commit_source_policy(self):
        self.assertEqual(self.m["upstream"]["license"], "MIT")
        self.assertEqual(self.m["upstream"]["commit"], "2d228630ba1446365f614a108cb8252f1feda202")
        self.assertEqual(self.m["upstream"]["source_mode"],"PINNED_REFERENCE_NOT_VENDORED")
        self.assertFalse(self.m["security"]["auto_install"])
        self.assertFalse(self.m["security"]["auto_execute"])

    def test_web_motion_routing(self):
        v=route("react","motion-build",project_known=True)
        self.assertEqual([x["id"] for x in v["selected"]],["animate","animation-performance"])
        self.assertEqual(v["mode"],"PROPOSE_ONLY")
        self.assertFalse(v["owner_authorized"])
        self.assertFalse(v["writes_performed"])

    def test_expo_fails_on_web(self):
        self.assertEqual(route("web","expo-motion-build",project_known=True)["status"],"HOLD_FRAMEWORK_MISMATCH")

    def test_swift_fails_on_web(self):
        self.assertEqual(route("web","swift-code",project_known=True)["status"],"HOLD_FRAMEWORK_MISMATCH")

    def test_sonner_requires_react(self):
        self.assertEqual(route("web","sonner-toasts",project_known=True)["status"],"HOLD_FRAMEWORK_MISMATCH")
        self.assertEqual(route("react","sonner-toasts",project_known=True)["selected"][0]["id"],"ask-sonner")

    def test_unknown_caller_holds(self):
        self.assertEqual(route("unknown","design-critique",project_known=True)["status"],"HOLD_PROJECT_CONTEXT")
        self.assertEqual(route("react","design-critique")["status"],"HOLD_PROJECT_CONTEXT")

    def test_explicit_only_review_prototype_library_and_apple(self):
        for intent in ("motion-review","prototype-variants","ui-library-choice","apple-style"):
            self.assertEqual(route("react",intent,project_known=True)["status"],"HOLD_EXPLICIT_USER_INVOCATION")
            self.assertEqual(route("react",intent,project_known=True,explicit=True)["status"],"REFERENCE_SELECTED_PROPOSAL_ONLY")

    def test_all_intents_never_execute(self):
        for intent in ROUTES:
            framework="swift" if intent=="swift-code" else "expo" if intent=="expo-motion-build" else "react"
            v=route(framework,intent,project_known=True,explicit=True)
            self.assertFalse(v["writes_performed"])
            self.assertFalse(v["executed_upstream"])
            self.assertFalse(v["installed_dependencies"])
            self.assertEqual(v["release_admission"],"HOLD")

    def test_pinned_urls(self):
        v=route("react","motion-build",project_known=True)
        self.assertTrue(all("/blob/2d228630ba1446365f614a108cb8252f1feda202/" in x["url"] for x in v["selected"]))
        self.assertNotIn("/main/",v["selected"][0]["url"])

    def test_invalid_input_refused(self):
        with self.assertRaises(ValueError): route("../../secret","motion-build",project_known=True)
        with self.assertRaises(ValueError): route("web","install-all",project_known=True)

if __name__ == "__main__":
    unittest.main()
