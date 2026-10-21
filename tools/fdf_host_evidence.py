#!/usr/bin/env python3
"""UAC-012 evidence *intake*, not witness attestation or owner authorization.

Reads two explicitly provided, bounded local JSON files; never writes, fetches,
executes a caller script, or authenticates an IDE. Output omits raw source data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

WITNESS = 'fdf.projectdna.local_witness/0.1'
OBSERVATION = 'fdf.host_admission.owner_observation/0.1'
HOSTS = {'antigravity','cursor','codex','gemini-cli','ai-studio','chatgpt-project'}
REQUIRED_FLAGS = (
 'real_workspace_confirmed_by_owner',
 'host_global_and_project_rules_checked',
 'native_skill_discovery_observed',
 'native_skill_activation_observed',
 'one_read_only_proposal_verified',
 'git_status_before_after_reviewed',
 'private_evidence_stored_outside_public_repo',
)
HEX64 = re.compile(r'^[a-f0-9]{64}$')
MAX_BYTES = 128*1024


def read_json(path: str) -> dict:
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise ValueError('HOLD: unsafe, nonexistent or oversized evidence path')
    data = p.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError('HOLD: oversized evidence')
    doc = json.loads(data)
    if not isinstance(doc,dict):
        raise ValueError('HOLD: evidence must be a JSON object')
    return doc


def witness_hash(witness: dict) -> str:
    claim = witness.get('witness_sha256')
    if not isinstance(claim,str) or not HEX64.fullmatch(claim):
        raise ValueError('HOLD: missing or malformed witness digest')
    payload = dict(witness)
    payload.pop('witness_sha256')
    serialized=(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode('utf-8')
    if hashlib.sha256(serialized).hexdigest() != claim:
        raise ValueError('HOLD: ProjectDNA witness changed since hash calculation')
    return claim


def triage(witness: dict, observation: dict) -> dict:
    if witness.get('schema') != WITNESS:
        raise ValueError('HOLD: unsupported UAC-010 witness schema')
    digest = witness_hash(witness)
    if witness.get('owner_approval') != 'NOT_OBSERVED' or witness.get('skill_loading') != 'UNKNOWN_NOT_WITNESSED':
        raise ValueError('HOLD: edited baseline admission boundary')
    if observation.get('schema') != OBSERVATION:
        raise ValueError('HOLD: unsupported UAC-011 observation schema')
    host = observation.get('host')
    if host not in HOSTS or witness.get('host_self_declared') != host:
        raise ValueError('HOLD: host mismatch or unsupported declared host')
    ref = observation.get('projectdna_witness_redacted_reference')
    if ref not in (digest,'sha256:'+digest):
        raise ValueError('HOLD: local observation has no matching ProjectDNA witness reference')
    skill=observation.get('reviewed_first_party_skill')
    if not isinstance(skill,str) or not re.fullmatch(r'fdf-[a-z0-9-]{1,64}',skill):
        raise ValueError('HOLD: malformed first-party skill identifier')
    missing=[]
    for key in REQUIRED_FLAGS:
        if observation.get(key) is not True:
            missing.append(key)
    commit = observation.get('skill_source_commit')
    if not isinstance(commit,str) or not re.fullmatch(r'[a-f0-9]{40}',commit):
        missing.append('skill_source_commit')
    if observation.get('independent_review') not in ('PENDING','REQUESTED','EXTERNALLY_COMPLETED_NOT_AUTHENTICATED'):
        missing.append('independent_review')
    # This tool does not possess authentic host logs, signatures, session authority, or review identity.
    return {
        'schema':'fdf.host_admission.intake_result/0.1',
        'source':'UAC011_USER_SUPPLIED_SELF_REPORT',
        'reported_host':host,
        'reported_first_party_skill':skill,
        'field_checks_complete':not missing,
        'missing_fields':missing,
        'witness_digest_matches_local_file':True,
        'live_host_discovery_independently_confirmed':False,
        'live_skill_activation_independently_confirmed':False,
        'independent_reviewer_identity_verified':False,
        'owner_approval_authenticated':False,
        'result':'EVIDENCE_INTAKE_REVIEW_REQUIRED' if not missing else 'INCOMPLETE_EVIDENCE_HOLD',
        'permission_to_install':False,
        'permission_to_merge':False,
        'permission_to_deploy':False,
        'release':'HOLD',
    }


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['review'])
    p.add_argument('--projectdna',required=True)
    p.add_argument('--observation',required=True)
    a=p.parse_args(argv)
    try:
        result=triage(read_json(a.projectdna),read_json(a.observation))
    except (ValueError,OSError,json.JSONDecodeError) as err:
        print(str(err),file=sys.stderr)
        return 2
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
