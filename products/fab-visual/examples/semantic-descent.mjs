import {writeFileSync, mkdirSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {policyScene} from '../src/visual/fixture.mjs';
import {renderSemanticDrilldown} from '../src/visual/semantic-drilldown.mjs';
const parent=policyScene();parent.id='synthetic-energy-system';parent.model={id:'fab.energy.synthetic',revision:'r1',authority:'synthetic educational model'};
parent.parts=[{id:'rack',label:'Battery rack',x:70,y:160,w:320,h:180,status:'NEUTRAL'}];parent.links=[];
parent.observables=[{id:'rack_energy',value:24,unit:'kWh',source:'synthetic arithmetic'}];
parent.claim={status:'EXPLANATORY',interpretation:'Synthetic energy arithmetic only; no measured or verified battery hardware'};
const child=structuredClone(parent);child.id='synthetic-energy-components';child.parts=[
 {id:'moduleA',label:'Module A',x:40,y:110,w:150,h:100},{id:'moduleB',label:'Module B',x:300,y:110,w:150,h:100}
];child.observables=[{id:'moduleA_energy',value:10,unit:'kWh',source:'synthetic arithmetic'},{id:'moduleB_energy',value:14,unit:'kWh',source:'synthetic arithmetic'}];
const refinement={schema:'fab.refinement.v0.1',parentSceneId:parent.id,childSceneId:child.id,childToParent:{moduleA:'rack',moduleB:'rack'},aggregates:[{parentId:'rack_energy',childIds:['moduleA_energy','moduleB_energy'],op:'sum',unit:'kWh',absTolerance:0.001}]};
const html=renderSemanticDrilldown(parent,child,refinement);
const out=resolve(process.argv[2]||'dist/semantic-descent.html');mkdirSync(dirname(out),{recursive:true});writeFileSync(out,html);console.log(JSON.stringify({output:out,scope:'SYNTHETIC_ANALOGY',verifiedRefinement:'PASS',production:'HOLD'}));
