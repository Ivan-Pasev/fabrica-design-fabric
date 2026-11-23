import hashlib
import importlib.util
import json
import pathlib
import unittest

root = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("evidence", root / "tools" / "fdf_host_evidence.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def witness():
    item = {"schema": module.WITNESS, "owner_approval": "NOT_OBSERVED", "skill_loading": "UNKNOWN_NOT_WITNESSED", "host_self_declared": "cursor"}
    raw = (json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n").encode()
    item["witness_sha256"] = hashlib.sha256(raw).hexdigest()
    return item


def observation(w):
    o = {"schema": module.OBSERVATION, "host": "cursor", "projectdna_witness_redacted_reference": "sha256:" + w["witness_sha256"], "reviewed_first_party_skill": "fdf-universal-bootstrap", "skill_source_commit": "0" * 40, "independent_review": "PENDING"}
    for name in module.REQUIRED_FLAGS:
        o[name] = True
    return o


class EvidenceAdmissionTests(unittest.TestCase):
    def test_report_not_authority(self):
        r = module.triage(witness(), observation(witness()))
        self.assertEqual(r["release"], "HOLD")
        self.assertFalse(r["owner_approval_authenticated"])
        self.assertFalse(r["live_skill_activation_independently_confirmed"])

    def test_missing_observation_holds(self):
        w = witness()
        o = observation(w)
        o["native_skill_discovery_observed"] = None
        self.assertEqual(module.triage(w, o)["result"], "INCOMPLETE_EVIDENCE_HOLD")

    def test_mismatched_witness_rejected(self):
        w = witness()
        o = observation(w)
        o["projectdna_witness_redacted_reference"] = "sha256:" + "f" * 64
        with self.assertRaises(ValueError):
            module.triage(w, o)

    def test_invalid_host_rejected(self):
        w = witness()
        o = observation(w)
        o["host"] = "unknown"
        with self.assertRaises(ValueError):
            module.triage(w, o)


if __name__ == "__main__":
    unittest.main()



# UAC-013 adversarial admission and malformed-input regression additions.
import os
import tempfile

class EvidenceHardeningTests(unittest.TestCase):
    def setUp(self):
        self.w = witness()
        self.o = observation(self.w)

    def test_unhashable_host_list_fails_closed(self):
        self.o["host"] = ["cursor"]
        with self.assertRaisesRegex(ValueError, "host mismatch"):
            module.triage(self.w, self.o)

    def test_unhashable_host_dict_fails_closed(self):
        self.o["host"] = {"name": "cursor"}
        with self.assertRaisesRegex(ValueError, "host mismatch"):
            module.triage(self.w, self.o)

    def test_duplicate_json_fields_are_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "observation.json"
            p.write_text('{"host":"cursor","host":"antigravity"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                module.read_json(str(p))

    def test_duplicate_nested_json_fields_are_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "observation.json"
            p.write_text('{"observation":{"evidence":"A","evidence":"B"}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                module.read_json(str(p))

    def test_nonfinite_json_numbers_are_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "observation.json"
            p.write_text('{"host":"cursor","score":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite"):
                module.read_json(str(p))

    def test_invalid_utf8_file_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "observation.json"
            p.write_bytes(b'{"v":"\xff"}')
            with self.assertRaises(UnicodeError):
                module.read_json(str(p))

    def test_nonobject_json_file_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "observation.json"
            p.write_text('["not", "an", "object"]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON object"):
                module.read_json(str(p))

    def test_oversized_evidence_file_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "observation.json"
            p.write_bytes(b" " * (module.MAX_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "oversized"):
                module.read_json(str(p))

    def test_symlink_to_evidence_file_is_refused(self):
        if os.name == "nt":
            self.skipTest("Windows symlink privileges not guaranteed")
        with tempfile.TemporaryDirectory() as t:
            target = pathlib.Path(t) / "target.json"
            alias = pathlib.Path(t) / "alias.json"
            target.write_text('{"safe":true}', encoding="utf-8")
            alias.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "unsafe"):
                module.read_json(str(alias))

    def test_unserializable_witness_set_fails_closed(self):
        self.w["unexpected"] = {"unserializable-set"}
        with self.assertRaisesRegex(ValueError, "unserializable"):
            module.witness_hash(self.w)

    def test_witness_invalid_unicode_fails_closed(self):
        self.w["unexpected"] = "\ud800"
        with self.assertRaisesRegex(ValueError, "unserializable"):
            module.witness_hash(self.w)

    def test_self_consistent_owner_promotion_still_rejected(self):
        self.w["owner_approval"] = "APPROVED_BY_SELF_REPORT"
        src = dict(self.w)
        del src["witness_sha256"]
        raw = (json.dumps(src, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        self.w["witness_sha256"] = hashlib.sha256(raw).hexdigest()
        self.o["projectdna_witness_redacted_reference"] = "sha256:" + self.w["witness_sha256"]
        with self.assertRaisesRegex(ValueError, "baseline admission boundary"):
            module.triage(self.w, self.o)

    def test_reported_independent_review_not_authentication(self):
        self.o["independent_review"] = "EXTERNALLY_COMPLETED_NOT_AUTHENTICATED"
        self.o["owner_release_approval"] = True
        result = module.triage(self.w, self.o)
        self.assertFalse(result["independent_reviewer_identity_verified"])
        self.assertFalse(result["owner_approval_authenticated"])
        self.assertFalse(result["permission_to_merge"])
        self.assertEqual(result["release"], "HOLD")

    def test_malformed_git_commit_keeps_hold(self):
        self.o["skill_source_commit"] = "main"
        result = module.triage(self.w, self.o)
        self.assertIn("skill_source_commit", result["missing_fields"])
        self.assertFalse(result["permission_to_install"])

    def test_private_witness_metadata_is_omitted(self):
        self.w["project_name"] = "SENSITIVE_PROJECT_ALIAS_FOR_TEST"
        src = dict(self.w)
        del src["witness_sha256"]
        self.w["witness_sha256"] = hashlib.sha256(
            (json.dumps(src, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        ).hexdigest()
        self.o["projectdna_witness_redacted_reference"] = "sha256:" + self.w["witness_sha256"]
        output = json.dumps(module.triage(self.w, self.o))
        self.assertNotIn("SENSITIVE_PROJECT_ALIAS_FOR_TEST", output)
        self.assertNotIn(self.w["witness_sha256"], output)

    def test_external_skill_identifier_rejected(self):
        self.o["reviewed_first_party_skill"] = "untrusted/external-skill"
        with self.assertRaisesRegex(ValueError, "malformed first-party"):
            module.triage(self.w, self.o)

    def test_invalid_witness_schema_rejected(self):
        self.w["schema"] = "unauthorized"
        with self.assertRaisesRegex(ValueError, "unsupported UAC-010"):
            module.triage(self.w, self.o)

    def test_unchecked_flags_never_pass(self):
        for flag in module.REQUIRED_FLAGS:
            self.o[flag] = None
        result = module.triage(self.w, self.o)
        self.assertEqual(result["result"], "INCOMPLETE_EVIDENCE_HOLD")
        self.assertFalse(result["field_checks_complete"])
