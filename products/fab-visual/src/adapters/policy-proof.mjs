/** Validate synthetic policy snapshots against the independently specified state machine. */
import {initial,transition,invariant,observable} from '../policy-model.mjs';
import {assertScene} from '../visual/contract.mjs';

export function verifySyntheticPolicySnapshot(scene) {
  assertScene(scene);
  if(scene.model.id!=='fab.policy.reference')return {status:'NOT_APPLICABLE',message:'Not a policy reference model'};
  const trace=scene.model.trace;
  if(!Array.isArray(trace)||trace.length>40||trace.some(x=>typeof x!=='string'))return {status:'INCONCLUSIVE',message:'Missing or invalid replayable model event trace'};
  let s=initial();
  try { for(const type of trace)s=transition(s,{type}); }
  catch(e) { return {status:'FAIL',message:'Invalid event trace: '+e.message}; }
  if(!invariant(s))return {status:'FAIL',message:'Replay violated synthetic model invariant'};
  const truth=observable(s);
  const shown=Object.fromEntries(scene.observables.map(x=>[x.id,x.value]));
  for(const key of ['phase','released','authorized']) if(shown[key]!==truth[key])return {status:'FAIL',message:'Observable '+key+' does not match replay'};
  const release=scene.parts.find(p=>p.id==='release');
  if(release && release.status !== (truth.released?'RELEASED':'BLOCKED'))return {status:'FAIL',message:'Release geometry status contradicts model replay'};
  return {status:'PASS',phase:s.phase,events:trace.length,checkedObservables:['phase','released','authorized'],releasePartChecked:Boolean(release)};
}
export function verifyPolicyTimeline(scenes) {
  const witnesses=scenes.map(verifySyntheticPolicySnapshot);
  for(let i=0;i<witnesses.length;i++) if(witnesses[i].status!=='PASS')return {status:'FAIL',frame:i,witnesses};
  for(let i=1;i<scenes.length;i++) {
    const past=scenes[i-1].model.trace;
    const next=scenes[i].model.trace;
    if(next.length!==past.length+1 || past.some((v,j)=>next[j]!==v))return {status:'FAIL',frame:i,reason:'Timeline event trace not an append-only one-transition continuation',witnesses};
  }
  return {status:'PASS',witnesses};
}
