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
