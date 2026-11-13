import { initial, transition, explanation, sceneIR } from '../../src/policy-model.mjs';
let state = initial();
for (const type of ['START', 'POLICY_ESCALATE', 'HUMAN_APPROVE', 'RELEASE']) {
  state = transition(state, { type });
  console.log(explanation(state));
}
console.log(JSON.stringify(sceneIR(state), null, 2));
