/**
 * FAB.VISUAL Ω6 — bounded recursive semantic descent and observable refinement.
 * Independent first-party implementation; never interprets analogies as metrology.
 * Containment is well-founded; signal/control feedback may be cyclic.
 */
import {assertScene} from './contract.mjs';
const text = x => typeof x === 'string' && x.trim().length > 0;
const finite = x => typeof x === 'number' && Number.isFinite(x);
const status = (value, problems, checks, scope) => ({status:problems.length?'FAIL':'PASS',scope,checks,problems});
export function containmentIndex(scene) {
  assertScene(scene);
  const byId = new Map(scene.parts.map(p => [p.id,p]));
  const children = new Map(scene.parts.map(p=>[p.id,[]]));
  for (const part of scene.parts) if (part.parent) children.get(part.parent).push(part.id);
  const roots=scene.parts.filter(p=>!p.parent).map(p=>p.id);
  const ranks=new Map();
  function visit(id,depth,stack) {
    if(stack.has(id))throw Error('containment cycle: '+id);
    const next=new Set(stack);next.add(id);
    ranks.set(id,depth);
    for(const child of children.get(id))visit(child,depth+1,next);
  }
  roots.forEach(id=>visit(id,0,new Set()));
  if(ranks.size!==scene.parts.length)throw Error('unreachable part or cycle');
  return {roots,children:Object.fromEntries([...children].map(([k,v])=>[k,[...v].sort()])),ranks:Object.fromEntries(ranks)};
}
/**
 * A refinement is a relation between two separate SceneIR views of the SAME
 * authoritative model revision. No physics claim is inferred from either view.
 * Invariant: each child has a unique parent in the parent's SceneIR, and each
 * tested numeric aggregate uses a declared unit and finite absolute tolerance.
 */
export function verifyRefinement(parent,child,contract) {
  const errors=[]; const checks=[];
  try {assertScene(parent);assertScene(child);}catch(e){return status(null,[`invalid scene: ${e.message}`],checks,'MODEL_REFINEMENT_ONLY');}
  if(!contract||contract.schema!=='fab.refinement.v0.1')errors.push('contract schema unsupported');
  if(parent.id===child.id)errors.push('parent and child scene IDs must differ');
  if(parent.model.id!==child.model.id||parent.model.revision!==child.model.revision)errors.push('model lineage mismatch');
  if(parent.representation!==child.representation)errors.push('representation class mismatch');
  if(contract?.parentSceneId!==parent.id||contract?.childSceneId!==child.id)errors.push('scene identity binding mismatch');
  const parents=new Map(parent.parts.map(p=>[p.id,p]));
  const children=new Set(child.parts.map(p=>p.id));
  const map=contract?.childToParent;
  if(!map||typeof map!=='object'||Array.isArray(map))errors.push('missing child-to-parent identity map');
  else {
    if(Object.keys(map).length!==children.size)errors.push('every child must map exactly once');
    for(const [id,owner] of Object.entries(map)) {
      if(!children.has(id))errors.push(`unknown child ${id}`);
      if(!parents.has(owner))errors.push(`unknown parent ${owner}`);
      if(!text(owner)||id===owner)errors.push(`invalid self or blank mapping ${id}`);
    }
  }
  const pObs=new Map((parent.observables||[]).map(o=>[o.id,o]));
  const cObs=new Map((child.observables||[]).map(o=>[o.id,o]));
  const assertions=contract?.aggregates;
  if(!Array.isArray(assertions)||assertions.length===0)errors.push('at least one observable contract required');
  else for(const [i,a] of assertions.entries()) {
    const prefix=`aggregates[${i}]`;
    if(!a||!['sum','identity','mean'].includes(a.op)) {errors.push(`${prefix}: unknown operation`);continue;}
    if(!text(a.parentId)||!Array.isArray(a.childIds)||!a.childIds.length||a.childIds.some(id=>!text(id))) {errors.push(`${prefix}: invalid observable mapping`);continue;}
    if(new Set(a.childIds).size!==a.childIds.length){errors.push(`${prefix}: duplicate child observable`);continue;}
    if(!finite(a.absTolerance)||a.absTolerance<0){errors.push(`${prefix}: invalid tolerance`);continue;}
    if(a.op==='identity'&&a.childIds.length!==1){errors.push(`${prefix}: identity requires one source`);continue;}
    const po=pObs.get(a.parentId),co=a.childIds.map(id=>cObs.get(id));
    if(!po||co.some(x=>!x)){errors.push(`${prefix}: missing declared observable`);continue;}
    if(!finite(po.value)||co.some(x=>!finite(x.value))){errors.push(`${prefix}: nonnumeric data`);continue;}
    if(!text(a.unit)||po.unit!==a.unit||co.some(x=>x.unit!==a.unit)){errors.push(`${prefix}: unit mismatch`);continue;}
    const vals=co.map(o=>o.value);
    const derived=a.op==='sum'?vals.reduce((a,b)=>a+b,0):a.op==='mean'?vals.reduce((a,b)=>a+b,0)/vals.length:vals[0];
    const delta=Math.abs(derived-po.value);
    const pass=delta<=a.absTolerance;
    checks.push({parentId:a.parentId,childIds:a.childIds,op:a.op,unit:a.unit,tolerance:a.absTolerance,parentValue:po.value,derived,delta,status:pass?'PASS':'FAIL'});
    if(!pass)errors.push(`${prefix}: observable disagreement ${delta} > ${a.absTolerance}`);
  }
  return status(null,errors,checks,'DECLARED_NUMERIC_REFINEMENT_NOT_EMPIRICAL_VALIDATION');
}
export function requireRefinement(parent,child,contract){const r=verifyRefinement(parent,child,contract);if(r.status!=='PASS')throw Error('semantic refinement rejected: '+JSON.stringify(r.problems));return r;}
