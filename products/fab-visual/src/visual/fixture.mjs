import { initial, transition, observable } from '../policy-model.mjs';
export function policyScene(events=['START','POLICY_ESCALATE']) {
  let state = initial();
  for (const type of events) state = transition(state,{type});
  const obs = observable(state);
  return {
    schema:'fab.scene.v0.2',id:'codexstation-policy-machine',representation:'ANALOGICAL',
    model:{id:'fab.policy.reference',revision:'v0.2',authority:'local demonstration only'},
    parts:[
      {id:'intake',label:'Intake',x:40,y:120,w:180,h:85,ports:[{id:'out',flow:'control'}]},
      {id:'policy',label:'Policy gate',x:295,y:120,w:180,h:85,ports:[{id:'in',flow:'control'},{id:'out',flow:'control'}],status:obs.phase==='BLOCKED'?'BLOCKED':undefined},
      {id:'human',label:'Human decision',x:550,y:120,w:180,h:85,ports:[{id:'in',flow:'control'},{id:'out',flow:'control'}],status:obs.humanApproved?'PASS':undefined},
      {id:'release',label:'Release',x:805,y:120,w:180,h:85,ports:[{id:'in',flow:'control'}],status:obs.released?'RELEASED':'BLOCKED'}
    ],
    links:[{from:'intake',to:'policy',flow:'control',fromPort:'out',toPort:'in'},
      {from:'policy',to:'human',flow:'control',fromPort:'out',toPort:'in'},
      {from:'human',to:'release',flow:'control',fromPort:'out',toPort:'in'}],
    observables:[{id:'phase',value:obs.phase,source:'fab.policy.reference'},
      {id:'authorized',value:obs.authorized,source:'fab.policy.reference'},
      {id:'released',value:obs.released,source:'fab.policy.reference'}],
    claim:{status:'EXPLANATORY',interpretation:'Analogy showing a synthetic policy transition; not an actual CodexStation authorization or release'}
  };
}
