import { test } from 'node:test';
import assert from 'node:assert/strict';
import { initial, transition, observable, explanation, sceneIR, invariant } from '../src/policy-model.mjs';
const run = (types) => types.reduce((s, type) => transition(s, {type}), initial());
test('release prohibited before policy', () => { assert.throws(() => transition(initial(), {type:'RELEASE'})); });
test('escalation requires human approval', () => { const s=run(['START','POLICY_ESCALATE']); assert.throws(()=>transition(s,{type:'RELEASE'})); });
test('blocked path cannot release', () => { const s=run(['START','POLICY_BLOCK']); assert.equal(s.phase,'BLOCKED'); assert.throws(()=>transition(s,{type:'RELEASE'})); });
test('authorized human sequence', () => { const s=run(['START','POLICY_ESCALATE','HUMAN_APPROVE','RELEASE']); assert.ok(invariant(s)); assert.equal(s.phase,'RELEASED'); });
test('model/IR/readout consistency', () => { const s=run(['START','POLICY_ESCALATE']); assert.deepEqual(sceneIR(s).currentState, observable(s)); assert.match(explanation(s), /AWAITING_HUMAN/); });
test('all reachable branches preserve policy invariant', () => {
  const eventTypes=['START','POLICY_ALLOW','POLICY_BLOCK','POLICY_ESCALATE','HUMAN_APPROVE','HUMAN_REJECT','RELEASE'];
  const visit=(s,depth) => { assert.ok(invariant(s)); if(depth>=6)return; for(const type of eventTypes) { try { visit(transition(s,{type}),depth+1); } catch(e) { if(!e.message.startsWith('Invalid transition')) throw e; } } };
  visit(initial(),0);
});
