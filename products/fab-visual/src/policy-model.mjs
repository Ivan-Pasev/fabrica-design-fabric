// Independent FAB.VISUAL demonstrator, not copied from CodexStation or Anatomy.
const allowed = {
  RECEIVED: ['START'],
  EVALUATING: ['POLICY_ALLOW', 'POLICY_BLOCK', 'POLICY_ESCALATE'],
  AWAITING_HUMAN: ['HUMAN_APPROVE', 'HUMAN_REJECT'],
  ALLOWED: ['RELEASE'],
  BLOCKED: [], ESCALATED: [], RELEASED: []
};
export function initial() { return { phase: 'RECEIVED', authorized: false, policyEvaluated: false, humanApproved: false, released: false, trace: [] }; }
export function transition(current, event) {
  if (!allowed[current.phase]?.includes(event.type)) throw new Error(`Invalid transition ${current.phase} -> ${event.type}`);
  const s = { ...current, trace: [...current.trace, event.type] };
  if (event.type === 'START') s.phase = 'EVALUATING';
  else if (event.type === 'POLICY_ALLOW') Object.assign(s, { phase: 'ALLOWED', authorized: true, policyEvaluated: true });
  else if (event.type === 'POLICY_BLOCK') Object.assign(s, { phase: 'BLOCKED', authorized: false, policyEvaluated: true });
  else if (event.type === 'POLICY_ESCALATE') Object.assign(s, { phase: 'AWAITING_HUMAN', authorized: false, policyEvaluated: true });
  else if (event.type === 'HUMAN_APPROVE') Object.assign(s, { phase: 'ALLOWED', authorized: true, humanApproved: true });
  else if (event.type === 'HUMAN_REJECT') Object.assign(s, { phase: 'BLOCKED', authorized: false, humanApproved: false });
  else if (event.type === 'RELEASE') {
    if (!s.authorized || !s.policyEvaluated) throw new Error('Unauthorized release');
    Object.assign(s, { phase: 'RELEASED', released: true });
  }
  return s;
}
export function observable(s) { return { phase: s.phase, released: s.released, authorized: s.authorized, humanApproved: s.humanApproved }; }
export function explanation(s) {
  const v = observable(s);
  return `Policy phase: ${v.phase}; released=${v.released}; authorization=${v.authorized}; human approval=${v.humanApproved}.`;
}
export function sceneIR(s) {
  return { representation: 'ANALOGICAL', geometryAuthority: 'conceptual only', currentState: observable(s), movingTarget: null, parts: [ { id: 'intake', role:'RECEIVED' }, {id:'policy',role:'EVALUATING'}, {id:'human',role:'AWAITING_HUMAN'}, {id:'release',role:'RELEASED'} ] };
}
export function invariant(s) {
  return !(s.released && (!s.authorized || !s.policyEvaluated || s.phase !== 'RELEASED')) && !(s.phase === 'BLOCKED' && s.authorized);
}
