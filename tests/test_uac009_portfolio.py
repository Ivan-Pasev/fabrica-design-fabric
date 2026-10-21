"""UAC-009: portfolio source cardinality, provenance, fit, and negative admission tests."""
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fdf_portfolio", ROOT / "tools" / "fdf_portfolio.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class PortfolioTest(unittest.TestCase):
    def test_exact_repository_count(self):
        self.assertEqual(mod.audit()["repositories"], 30)

    def test_emil_manifest_fifteen(self):
        self.assertEqual(mod.audit()["emil_skill_refs"], 15)

    def test_unique_source_names(self):
        rows = mod.load(mod.REGISTRY)["repositories"]
        self.assertEqual(len({r["repo"] for r in rows}), 30)

    def test_explicit_not_installed(self):
        for r in mod.load(mod.REGISTRY)["repositories"]:
            self.assertFalse(r["installed_in_owner_ide"])
            self.assertFalse(r["host_verified"])
            self.assertFalse(r["owner_approved_install"])

    def test_mutated_host_claim_rejected(self):
        j = copy.deepcopy(mod.load(mod.REGISTRY))
        j["repositories"][0]["host_verified"] = True
        with self.assertRaisesRegex(ValueError, "improperly asserts"):
            mod.audit(registry=j)

    def test_duplicate_rejected(self):
        j = copy.deepcopy(mod.load(mod.REGISTRY))
        j["repositories"][1]["repo"] = j["repositories"][0]["repo"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            mod.audit(registry=j)

    def test_malformed_pin_rejected(self):
        j = copy.deepcopy(mod.load(mod.REGISTRY))
        j["repositories"][0]["source_commit"] = "main"
        with self.assertRaisesRegex(ValueError, "malformed historical"):
            mod.audit(registry=j)

    def test_third_party_content_not_bundled(self):
        j = copy.deepcopy(mod.load(mod.REGISTRY))
        j["repositories"][0]["distribution"] = "VENDORED"
        with self.assertRaisesRegex(ValueError, "redistribution"):
            mod.audit(registry=j)

    def test_emil_pin_mismatch_rejected(self):
        j = copy.deepcopy(mod.load(mod.REGISTRY))
        r = next(x for x in j["repositories"] if x["repo"] == "emilkowalski/skills")
        r["source_commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "inconsistent upstream"):
            mod.audit(registry=j)

    def test_license_restrictions_hold(self):
        j = mod.audit()
        self.assertIn("DavidHDev/react-bits", j["license_holds"])
        self.assertIn("vercel-labs/agent-skills", j["license_holds"])

    def test_select_motion_includes_pinned_bridges(self):
        j = mod.select("motion", limit=30)
        names = {x["repo"] for x in j["recommended_references"]}
        self.assertTrue({"emilkowalski/skills", "greensock/gsap-skills", "iart-ai/web-animation-skills"} <= names)
        self.assertEqual(j["owner_ide_activation"], "UNKNOWN_NOT_OBSERVED")

    def test_restricted_component_is_deferred(self):
        j = mod.select("components", 30)
        self.assertNotIn("DavidHDev/react-bits", {x["repo"] for x in j["recommended_references"]})
        self.assertIn("DavidHDev/react-bits", {x["repo"] for x in j["deferred"]})

    def test_unknown_license_remains_deferred(self):
        j = mod.select("runtime", 30)
        self.assertIn("vercel-labs/agent-skills", {x["repo"] for x in j["deferred"]})

    def test_limits_are_validated(self):
        with self.assertRaisesRegex(ValueError, "invalid result"):
            mod.select("design", 100)

    def test_no_write_authority(self):
        j = mod.select("design")
        self.assertEqual(j["release"], "HOLD")
        self.assertIn("ROOT_POLICY_EDIT", j["prohibited_effects"])
        self.assertIn("INSTALL", j["prohibited_effects"])

    def test_cli_subprocess_read_only(self):
        cmd = [sys.executable, str(ROOT / "tools" / "fdf_portfolio.py"), "audit"]
        run = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["repositories"], 30)


if __name__ == "__main__":
    unittest.main()
