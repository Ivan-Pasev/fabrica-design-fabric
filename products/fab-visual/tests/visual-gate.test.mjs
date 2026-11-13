import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gate } from '../src/gate.mjs';
const seed=JSON.parse(readFileSync(new URL('../examples/codexstation-policy/manifest.json',import.meta.url)));
test('incomplete evidence blocks release',()=>{assert.equal(gate(seed).status,'BLOCKED');});
test('analogy cannot assert scientific certification',()=>{const a=structuredClone(seed);a.claims.scientifically_validated=true;assert.match(gate(a).violations.join(' '),/Analogy cannot self-certify/);});
test('exception not silently admitted',()=>{const a=structuredClone(seed);for(const k in a.evidence)a.evidence[k]='PASS';a.evidence.geometry='EXCEPTION';assert.equal(gate(a).status,'BLOCKED');});
test('complete evidence makes a candidate eligible, not published',()=>{const a=structuredClone(seed);for(const k in a.evidence)a.evidence[k]='PASS';assert.equal(gate(a).status,'ELIGIBLE_FOR_AUTHORIZED_RELEASE');});
