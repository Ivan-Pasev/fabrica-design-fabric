/**
 * Ω11P Source-bound numerical and finite-model evidence.
 * No independent physics, metrology, human approval or publisher authentication.
 */
import {createHash} from 'node:crypto';
import {assertScene} from './contract.mjs';
import {sha256,canonicalJSON} from './provenance.mjs';
import {getUnit,auditQuantitativeContract} from './quantitative-audit.mjs';

const fail=s=>{throw Error('BOUND_QUANTITATIVE_REJECT: '+s)};
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const id=x=>typeof x==='string'&&/^[a-z][a-z0-9_-]{0,55}$/.test(x);
const keys=(x,allowed)=>x&&typeof x==='object'&&!Array.isArray(x)&&
 Object.keys(x).every(k=>allowed.includes(k));
const buffer=new ArrayBuffer(8),view=new DataView(buffer);
function nextUp(x){
  if(!finite(x))fail('outward float range overflow');
  if(x===0)return Number.MIN_VALUE;
  view.setFloat64(0,x,false);
  let bits=view.getBigUint64(0,false);
  bits=x>0?bits+1n:bits-1n;
  view.setBigUint64(0,bits,false);
  const value=view.getFloat64(0,false);
  if(!finite(value))fail('outward interval overflow');
  return value;
}
function nextDown(x){
  if(!finite(x))fail('outward float range overflow');
  if(x===0)return -Number.MIN_VALUE;
  view.setFloat64(0,x,false);
  let bits=view.getBigUint64(0,false);
  bits=x>0?bits-1n:bits+1n;
  view.setBigUint64(0,bits,false);
  const value=view.getFloat64(0,false);
  if(!finite(value))fail('outward interval overflow');
  return value;
}
const addDown=(a,b)=>nextDown(a+b);
const addUp=(a,b)=>nextUp(a+b);
function enclose(term){
  const factor=getUnit(term.unit).toSI;
  if(!finite(term.value)||!finite(term.uncertainty)||term.value<0||term.uncertainty<0)
    fail('finite nonnegative value and uncertainty required');
  const low=nextDown(term.value-term.uncertainty);
  const high=nextUp(term.value+term.uncertainty);
  if(!finite(low*factor)||!finite(high*factor))fail('finite unit conversion required');
  const lo=nextDown(low*factor),hi=nextUp(high*factor);
  return term.direction==='IN'?[lo,hi]:[-hi,-lo];
}
export function intervalBalance(balance,nominal){
  if(!balance||!Array.isArray(balance.terms)||!nominal||!finite(nominal.toleranceSI))
    fail('validated balance and nominal receipt required');
  let lo=0,hi=0;
  for(const term of balance.terms){
    const [a,b]=enclose(term);
    lo=addDown(lo,a);hi=addUp(hi,b);
  }
  const t=nextUp(nominal.toleranceSI);
  const classification=lo>=-t&&hi<=t?'WITHIN_DECLARED_BOUNDS':
    lo>t||hi<-t?'OUTSIDE_DECLARED_BOUNDS':'INCONCLUSIVE_OVERLAP';
  return {id:balance.id,dimension:nominal.dimension,loSI:lo,hiSI:hi,
    nominalResidualSI:nominal.residualSI,declaredToleranceSI:nominal.toleranceSI,
    classification,
    method:'BINARY64_OUTWARD_ROUNDED_TERM_INTERVAL_AND_SUM',
    assumption:'DECLARED_BINARY64_INPUTS_AND_UNCERTAINTIES_NOT_VALIDATED_REAL_MEASUREMENTS',
    decimalInputEnclosure:'NOT_CERTIFIED',
    correlatedErrorIndependence:'NOT_ASSUMED',scientificValidation:'NOT_RUN',release:'HOLD'};
}
function matchReadout(scene,spec){
  if(!keys(spec,['id','evaluator','expected','unit','tolerance','observableId'])||
     !id(spec.id)||!['PART_COUNT','LINK_COUNT','NUMERIC_SOURCE_OBSERVABLE'].includes(spec.evaluator)||
     !finite(spec.expected)||!finite(spec.tolerance)||spec.tolerance<0)
    fail('invalid explicit bounded evaluator and expected value');
  const unit=getUnit(spec.unit);
  let measured,measuredUnit,scope;
  if(spec.evaluator==='PART_COUNT'){
    if(spec.observableId!==undefined)fail('structural count cannot nominate observable');
    measured=scene.parts.length;measuredUnit=getUnit('1');
    scope='INDEPENDENT_SCENE_STRUCTURE_COUNT';
  }else if(spec.evaluator==='LINK_COUNT'){
    if(spec.observableId!==undefined)fail('structural count cannot nominate observable');
    measured=(scene.links||[]).length;measuredUnit=getUnit('1');
    scope='INDEPENDENT_SCENE_STRUCTURE_COUNT';
  }else{
    if(!id(spec.observableId))fail('source observable ID required');
    const items=(scene.observables||[]).filter(o=>o.id===spec.observableId);
    if(items.length!==1||!finite(items[0].value)||!items[0].unit)
      fail('finite exact source observable required');
    measured=items[0].value;measuredUnit=getUnit(items[0].unit);
    scope='DECLARED_SOURCE_VALUE_COMPARISON_NOT_INDEPENDENT_MODEL_EVALUATION';
  }
  if(unit.dimension!==measuredUnit.dimension)
    fail('evaluator unit dimension mismatch: '+spec.id);
  const actualSI=measured*measuredUnit.toSI;
  const expectedSI=spec.expected*unit.toSI;
  const toleranceSI=spec.tolerance*unit.toSI;
  if(![actualSI,expectedSI,toleranceSI].every(finite))
    fail('readout conversion overflow');
  return {id:spec.id,evaluator:spec.evaluator,scope,
    actualSI,expectedSI,toleranceSI,
    status:Math.abs(actualSI-expectedSI)<=toleranceSI?'PASS':'FAIL',
    physicalValidation:'NOT_RUN',release:'HOLD'};
}
export function auditBoundQuantitative(scene,envelope){
  assertScene(scene);
  if(!keys(envelope,['schema','scope','sourceSceneDigest','sourceSceneId',
    'sourceModel','sourceRepresentation','quantitative','readouts'])||
    envelope.schema!=='fab.visual.bound-quantitative.v1'||
    envelope.scope!=='SOURCE_LOCKED_INTERNAL_CONSISTENCY_ONLY')
    fail('exact source-bound envelope schema/scope required');
  if(typeof envelope.sourceSceneDigest!=='string'||
     !/^sha256:[a-f0-9]{64}$/.test(envelope.sourceSceneDigest))
    fail('original canonical SHA-256 required');
  const actualDigest='sha256:'+sha256(canonicalJSON(scene));
  if(actualDigest!==envelope.sourceSceneDigest)
    fail('source scene digest drift');
  if(envelope.sourceSceneId!==scene.id||
     !keys(envelope.sourceModel,['id','revision'])||
     envelope.sourceModel.id!==scene.model.id||
     envelope.sourceModel.revision!==scene.model.revision||
     envelope.sourceRepresentation!==scene.representation)
    fail('model identity/revision/representation mismatch');
  if(scene.model.synthetic===true&&envelope.quantitative?.source?.kind!=='SYNTHETIC_EXAMPLE')
    fail('synthetic original scene cannot claim real measurement provenance');
  const prior=auditQuantitativeContract(envelope.quantitative);
  if(!Array.isArray(envelope.readouts)||envelope.readouts.length<1||
     envelope.readouts.length>24)fail('1–24 derived readout assertions required');
  const seen=new Set(),readouts=[];
  for(const spec of envelope.readouts){
    if(!id(spec?.id)||seen.has(spec.id))fail('unique readout IDs required');
    seen.add(spec.id);
    readouts.push(matchReadout(scene,spec));
  }
  const intervals=envelope.quantitative.balances.map((b,i)=>intervalBalance(b,prior.balances[i]));
  const inconsistent=intervals.some(x=>x.classification==='OUTSIDE_DECLARED_BOUNDS');
  const inconclusive=intervals.some(x=>x.classification==='INCONCLUSIVE_OVERLAP');
  return {schema:'fab.visual.bound-quantitative-report.v1',sourceSceneDigest:actualDigest,
    sourceSceneId:scene.id,sourceModel:{id:scene.model.id,revision:scene.model.revision},
    sourceRepresentation:scene.representation,nominal:prior,intervals,readouts,
    status:prior.status!=='PASS'||readouts.some(x=>x.status==='FAIL')||inconsistent?'FAIL':
      inconclusive?'INCONCLUSIVE':'PASS',
    boundEvidence:'SHA256_MATCH_TO_SUPPLIED_TRUSTED_SCENE_NOT_EXTERNAL_AUTHENTICATION',
    modelEvaluation:'COUNTS_INDEPENDENT_SOURCE_OBSERVABLES_DECLARED_ONLY',
    formalProof:'NOT_RUN',physicalValidation:'NOT_RUN',
    externalSourceAuthentication:'NOT_PRESENT',hostAuthorization:'NOT_RUN',
    release:'HOLD'};
}
