/**
 * FAB.VISUAL Ω11Q-M2: bounded decimal-string → exact BigInt rational interval oracle.
 * Mathematical internal consistency only. This does not certify measurement,
 * correlation models, external provenance, physics, formal proof or release.
 */
import {assertScene} from './contract.mjs';
import {sha256,canonicalJSON} from './provenance.mjs';

const reject=x=>{throw Error('EXACT_INTERVAL_REJECT: '+x)};
const plain=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const shape=(x,ks)=>plain(x)&&Object.keys(x).length===ks.length&&
  ks.every(k=>Object.hasOwn(x,k));
const MAX_DIGITS=120;
const digits=x=>x.toString().replace('-','').length;
const check=(a,b)=>{if(b<=0n||digits(a)>MAX_DIGITS||digits(b)>MAX_DIGITS)
  reject('rational numerator/denominator size limit exceeded')};
const abs=x=>x<0n?-x:x;
function gcd(a,b){a=abs(a);b=abs(b);while(b){const t=a%b;a=b;b=t;}return a;}
export function rational(n,d=1n){
  if(typeof n!=='bigint'||typeof d!=='bigint'||d===0n)reject('exact BigInt rational required');
  if(d<0n){n=-n;d=-d;}
  check(n,d);
  if(n===0n)return {n:0n,d:1n};
  const g=gcd(n,d);return {n:n/g,d:d/g};
}
export function addExact(a,b){return rational(a.n*b.d+b.n*a.d,a.d*b.d);}
export function negExact(a){return {n:-a.n,d:a.d};}
export function subExact(a,b){return addExact(a,negExact(b));}
export function mulExact(a,b){return rational(a.n*b.n,a.d*b.d);}
export function cmpExact(a,b){const x=a.n*b.d,y=b.n*a.d;return x<y?-1:x>y?1:0;}
export function jsonExact(a){return {numerator:a.n.toString(),denominator:a.d.toString()};}
const ZERO=rational(0n),UNIT=rational(1n);
const DEC=/^([+-]?)(0|[1-9][0-9]*)(?:\.([0-9]+))?(?:[eE]([+-]?(?:0|[1-9][0-9]*)))?$/;
/** Strings only: never convert an already-rounded JSON number to "exact". */
export function parseExactDecimal(token){
  if(typeof token!=='string'||token.length>80)reject('decimal must be bounded raw string');
  const m=DEC.exec(token);
  if(!m)reject('noncanonical or malformed decimal token');
  const coefficient=m[2]+(m[3]||'');
  if(coefficient.length>40)reject('decimal coefficient too long');
  const exp=m[4]===undefined?0:Number(m[4]);
  if(!Number.isSafeInteger(exp)||Math.abs(exp)>24)reject('decimal exponent out of range');
  const scale=(m[3]||'').length-exp;
  if(Math.abs(scale)>48)reject('decimal scale out of range');
  let n=BigInt(coefficient);
  if(m[1]==='-')n=-n;
  return scale>=0?rational(n,10n**BigInt(scale)):
    rational(n*10n**BigInt(-scale));
}
const SI=Object.freeze({
  W:['POWER',UNIT],kW:['POWER',rational(1000n)],MW:['POWER',rational(1000000n)],
  J:['ENERGY',UNIT],Wh:['ENERGY',rational(3600n)],kWh:['ENERGY',rational(3600000n)],
  s:['TIME',UNIT],ms:['TIME',rational(1n,1000n)],h:['TIME',rational(3600n)],
  '1':['DIMENSIONLESS',UNIT]
});
function quantity(token,unit,dimension,nonnegative=true,positive=false){
  if(typeof unit!=='string'||!Object.hasOwn(SI,unit)||SI[unit][0]!==dimension)
    reject('unknown or dimensionally incompatible SI unit');
  const x=parseExactDecimal(token);
  if(nonnegative&&cmpExact(x,ZERO)<0||positive&&cmpExact(x,ZERO)<=0)
    reject('nonnegative/positive declared exact quantity required');
  return mulExact(x,SI[unit][1]);
}
const TERM_KEYS=['id','magnitude','uncertainty','unit','direction'];
const IS_ID=x=>typeof x==='string'&&/^[a-z][a-z0-9_-]{0,55}$/.test(x);
function checkedTerms(terms){
  if(!Array.isArray(terms)||terms.length<2||terms.length>16)
    reject('2–16 terms required');
  const seen=new Set();let lo=ZERO,hi=ZERO,nominal=ZERO;
  for(const t of terms){
    if(!shape(t,TERM_KEYS)||!IS_ID(t.id)||seen.has(t.id)||
       !['IN','OUT'].includes(t.direction))
      reject('exact unique signed term schema required');
    seen.add(t.id);
    const m=quantity(t.magnitude,t.unit,'POWER');
    const u=quantity(t.uncertainty,t.unit,'POWER');
    const lower=subExact(m,u),upper=addExact(m,u);
    if(t.direction==='IN'){
      lo=addExact(lo,lower);hi=addExact(hi,upper);
      nominal=addExact(nominal,m);
    }else{
      lo=subExact(lo,upper);hi=subExact(hi,lower);
      nominal=subExact(nominal,m);
    }
  }
  if(cmpExact(lo,hi)>0)reject('reversed interval');
  return {lo,hi,nominal};
}
export function exactModelInterval(terms,duration){
  if(!shape(duration,['value','unit']))reject('exact duration schema required');
  const power=checkedTerms(terms);
  const t=quantity(duration.value,duration.unit,'TIME',true,true);
  return {power,energy:{lo:mulExact(power.lo,t),hi:mulExact(power.hi,t),
    nominal:mulExact(power.nominal,t)}};
}
function classification(lo,hi,tolerance){
  const lower=negExact(tolerance);
  if(cmpExact(lo,lower)>=0&&cmpExact(hi,tolerance)<=0)
    return 'WITHIN_DECLARED_BOUNDS';
  if(cmpExact(lo,tolerance)>0||cmpExact(hi,lower)<0)
    return 'OUTSIDE_DECLARED_BOUNDS';
  return 'INCONCLUSIVE_OVERLAP';
}
function reported(x,t,expected=ZERO){
  const lo=subExact(x.lo,expected),hi=subExact(x.hi,expected);
  return {nominalSI:jsonExact(subExact(x.nominal,expected)),
    intervalLoSI:jsonExact(lo),intervalHiSI:jsonExact(hi),
    toleranceSI:jsonExact(t),
    classification:classification(lo,hi,t)};
}
const MODEL='fab.visual.omega11l.energy',REV='0.6.0-alpha.0';
export function auditExactInterval(scene,input){
  assertScene(scene);
  if(!shape(input,['schema','scope','sourceSceneDigest','sourceSceneId',
      'sourceModel','sourceRepresentation','equation','terms','duration',
      'absoluteTolerance','expectedEnergy'])||
      input.schema!=='fab.visual.exact-interval.v1'||
      input.scope!=='FIRST_PARTY_SYNTHETIC_DECIMAL_INTERNAL_CONSISTENCY'||
      input.equation!=='SYNTHETIC_MICROGRID_BUS_BALANCE_V1')
    reject('unknown or unreviewed exact model schema');
  if(JSON.stringify(input).length>4096)reject('exact sidecar exceeds 4096 bytes');
  if(typeof input.sourceSceneDigest!=='string'||
     !/^sha256:[a-f0-9]{64}$/.test(input.sourceSceneDigest)||
     input.sourceSceneDigest!=='sha256:'+sha256(canonicalJSON(scene)))
    reject('source SceneIR digest drift');
  if(!shape(input.sourceModel,['id','revision'])||
      input.sourceModel.id!==MODEL||input.sourceModel.revision!==REV||
      input.sourceSceneId!==scene.id||
      input.sourceRepresentation!=='ANALOGICAL'||
      scene.model?.id!==MODEL||scene.model?.revision!==REV||
      scene.model?.synthetic!==true||scene.representation!=='ANALOGICAL')
    reject('model identity/revision/representation drift');
  if(!shape(input.absoluteTolerance,['value','unit'])||
     !shape(input.expectedEnergy,['value','unit','tolerance']))
    reject('exact absolute tolerance and energy comparison required');
  const tPower=quantity(input.absoluteTolerance.value,input.absoluteTolerance.unit,'POWER');
  const expectedEnergy=quantity(input.expectedEnergy.value,input.expectedEnergy.unit,'ENERGY',false);
  const tEnergy=quantity(input.expectedEnergy.tolerance,input.expectedEnergy.unit,'ENERGY');
  const {power,energy}=exactModelInterval(input.terms,input.duration);
  const p=reported(power,tPower),e=reported(energy,tEnergy,expectedEnergy);
  const classes=[p.classification,e.classification];
  const status=classes.includes('OUTSIDE_DECLARED_BOUNDS')?'FAIL':
    classes.includes('INCONCLUSIVE_OVERLAP')?'INCONCLUSIVE':'PASS_BOUNDED_EXACT_ARITHMETIC';
  return {schema:'fab.visual.exact-interval-report.v1',status,
    sourceSceneDigest:input.sourceSceneDigest,
    model:{id:MODEL,revision:REV},power:p,energy:e,
    inputAuthority:'FIRST_PARTY_SYNTHETIC',
    exactness:'CANONICAL_DECIMAL_STRING_TO_REDUCED_BIGINT_RATIONAL',
    toleranceMethod:'EXPLICIT_ABSOLUTE_EXACT_CLOSED_INTERVAL_ONLY',
    correlation:'NO_STATISTICAL_INDEPENDENCE_ASSUMED',
    renderedReadout:'NOT_RUN',physicalValidation:'NOT_RUN',
    empiricalCalibration:'NOT_RUN',formalProof:'NOT_RUN',
    externalSignature:'NOT_PRESENT',hostAuthorization:'NOT_RUN',release:'HOLD'};
}
