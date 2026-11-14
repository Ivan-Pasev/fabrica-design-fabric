/**
 * FAB.VISUAL Ω11Q-M1: fixed first-party synthetic microgrid equation evaluator.
 * Independent execution of an explicit reviewed equation, NOT independent
 * scientific validation, hardware measurement, renderer proof or release.
 * NO dynamic code, network access, installation or filesystem effects.
 */
import {assertScene} from './contract.mjs';
import {sha256,canonicalJSON} from './provenance.mjs';
import {getUnit} from './quantitative-audit.mjs';

const fail=why=>{throw Error('MODEL_EVALUATOR_REJECT: '+why);};
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const keys=(x,allowed,required=allowed)=>obj(x)&&
  Object.keys(x).every(k=>allowed.includes(k))&&required.every(k=>Object.hasOwn(x,k));
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const MODEL='fab.visual.omega11l.energy';
const REV='0.6.0-alpha.0';
const SCHEMA='fab.visual.independent-model-evaluation.v1';
const EQUATION='SYNTHETIC_MICROGRID_BUS_BALANCE_V1';
const POWER_UNITS=new Set(['W','kW','MW']);
const TIME_UNITS=new Set(['s','ms','h']);
const ENERGY_UNITS=new Set(['J','Wh','kWh']);
function quantity(q,units,dimension,positiveOnly=false){
  if(!keys(q,['value','unit'])||!finite(q.value)||q.value<0||
     (positiveOnly&&q.value===0)||!units.has(q.unit))
    fail('finite nonnegative explicit SI-compatible quantity required');
  const u=getUnit(q.unit);
  if(u.dimension!==dimension)fail('dimension mismatch');
  const result=q.value*u.toSI;
  if(!finite(result)||result>1e15)fail('SI quantity outside bounded evaluator range');
  return result;
}
function assertion(a,units,dimension){
  if(!keys(a,['value','unit','tolerance'])||!finite(a.value)||
     !finite(a.tolerance)||a.tolerance<0||!units.has(a.unit))
    fail('bounded expected result and tolerance required');
  const u=getUnit(a.unit);
  if(u.dimension!==dimension)fail('asserted dimension mismatch');
  const expected=a.value*u.toSI,tolerance=a.tolerance*u.toSI;
  if(!finite(expected)||!finite(tolerance)||Math.abs(expected)>1e18||
     tolerance>1e18)fail('assertion outside bounded SI range');
  return {expected,tolerance};
}
function check(actual,a,units,dimension){
  const {expected,tolerance}=assertion(a,units,dimension);
  const residual=actual-expected;
  if(!finite(residual))fail('nonfinite assertion residual');
  return {actualSI:actual,expectedSI:expected,toleranceSI:tolerance,
    residualSI:residual,status:Math.abs(residual)<=tolerance?'PASS':'FAIL'};
}
export function evaluateIndependentMicrogrid(scene,spec){
  assertScene(scene);
  if(!keys(spec,['schema','scope','sourceSceneDigest','sourceSceneId','sourceModel',
      'equation','inputs','expected'])||spec.schema!==SCHEMA||
      spec.scope!=='FIRST_PARTY_SYNTHETIC_EQUATION_ONLY'||
      spec.equation!==EQUATION)
    fail('exact reviewed equation and schema required');
  if(typeof spec.sourceSceneDigest!=='string'||
     !/^sha256:[a-f0-9]{64}$/.test(spec.sourceSceneDigest)||
     spec.sourceSceneDigest!=='sha256:'+sha256(canonicalJSON(scene)))
    fail('source SceneIR hash mismatch');
  if(spec.sourceSceneId!==scene.id||
     !keys(spec.sourceModel,['id','revision'])||
     spec.sourceModel.id!==MODEL||spec.sourceModel.revision!==REV||
     scene.model?.id!==MODEL||scene.model?.revision!==REV||
     scene.model?.synthetic!==true||scene.representation!=='ANALOGICAL')
    fail('unreviewed or mismatched model identity/representation');
  if(!keys(spec.inputs,['pv','batteryDischarge','load','conversionLoss','duration'])||
     !keys(spec.expected,['netPower','netEnergy']))
    fail('exact microgrid inputs and expected outputs required');
  const pv=quantity(spec.inputs.pv,POWER_UNITS,'POWER');
  const battery=quantity(spec.inputs.batteryDischarge,POWER_UNITS,'POWER');
  const load=quantity(spec.inputs.load,POWER_UNITS,'POWER');
  const loss=quantity(spec.inputs.conversionLoss,POWER_UNITS,'POWER');
  const duration=quantity(spec.inputs.duration,TIME_UNITS,'TIME',true);
  const netPowerW=(pv+battery)-(load+loss);
  const netEnergyJ=netPowerW*duration;
  if(!finite(netPowerW)||!finite(netEnergyJ)||Math.abs(netEnergyJ)>1e18)
    fail('equation result overflow');
  const power=check(netPowerW,spec.expected.netPower,POWER_UNITS,'POWER');
  const energy=check(netEnergyJ,spec.expected.netEnergy,ENERGY_UNITS,'ENERGY');
  const obs=(scene.observables||[]).filter(o=>o.id==='site_export_power');
  let renderedReadout={status:'NOT_RUN',reason:'SOURCE_NUMERIC_READOUT_NOT_AVAILABLE'};
  if(obs.length===1&&finite(obs[0].value)&&POWER_UNITS.has(obs[0].unit)){
    const actual=quantity({value:obs[0].value,unit:obs[0].unit},POWER_UNITS,'POWER');
    renderedReadout={status:Math.abs(actual-netPowerW)<=1e-8?'PASS':'FAIL',
      sourceValueW:actual,computedValueW:netPowerW,
      limitation:'SOURCE_OBSERVABLE_IS_NOT_A_GPU_OR_RENDERED_FRAME_ATTESTATION'};
  }
  const status=power.status==='FAIL'||energy.status==='FAIL'||
    renderedReadout.status==='FAIL'?'FAIL':'PASS_BOUNDED_SYNTHETIC_EQUATION';
  return {schema:'fab.visual.independent-model-evaluation-report.v1',
    equation:EQUATION,status,model:{id:MODEL,revision:REV},
    sourceSceneDigest:spec.sourceSceneDigest,
    equationDefinition:'(PV_W + BATTERY_DISCHARGE_W - LOAD_W - CONVERSION_LOSS_W) * DURATION_S',
    power,energy,renderedReadout,
    computation:'FIXED_REVIEWED_FIRST_PARTY_EQUATION_NOT_SOURCE_OBSERVABLE_ECHO',
    numericalPrecision:'BINARY64_FINITE_ARITHMETIC_NOT_EXACT_DECIMAL_PROOF',
    inputAuthority:'FIRST_PARTY_SYNTHETIC_DECLARATIONS_NOT_MEASUREMENTS',
    empiricalCalibration:'NOT_RUN',physicalValidation:'NOT_RUN',formalProof:'NOT_RUN',
    externalPublisherSignature:'NOT_PRESENT',hostAuthorization:'NOT_RUN',
    actualRendererFrame:'NOT_ADMITTED',release:'HOLD'};
}
