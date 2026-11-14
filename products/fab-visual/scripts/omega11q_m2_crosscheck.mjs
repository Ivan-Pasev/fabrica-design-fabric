/**
 * Ω11Q-M2 reproducible cross-language exact rational comparison.
 * Vectors are seeded first-party synthetic inputs, not empirical data.
 */
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {exactModelInterval,jsonExact} from '../src/visual/exact-interval.mjs';
const fail=s=>{throw Error('M2_CROSS_LANGUAGE_REJECT: '+s)};
const K=10000;
let seed=0x5eed1141;
function rng(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;}
const powerUnits=['W','kW','MW'],timeUnits=['s','ms','h'];
function vec(i){
 const terms=Array.from({length:4},(_,j)=>({
  id:'term_'+j,
  magnitude:String(1+rng()%5000)+'.'+String(rng()%1000).padStart(3,'0'),
  uncertainty:'0.'+String(rng()%100).padStart(3,'0'),
  unit:powerUnits[rng()%3],
  direction:rng()%2?'IN':'OUT'
 }));
 return {id:i,terms,duration:{value:String(1+rng()%15),unit:timeUnits[rng()%3]}};
}
const json=x=>JSON.stringify(x,null,2)+'\n';
const [mode,...args]=process.argv.slice(2);
if(mode==='generate'){
 if(args.length)fail('generate takes no arguments');
 process.stdout.write(json({schema:'fab.visual.exact-rational-vectors.v1',
  seed:'0x5eed1141',count:K,vectors:Array.from({length:K},(_,i)=>vec(i))}));
}else if(mode==='verify'){
 if(args.length!==2)fail('verify <vectors.json> <independent-python-results.json>');
 const bytes=readFileSync(args[0]),vectors=JSON.parse(bytes.toString('utf8'));
 const python=JSON.parse(readFileSync(args[1],'utf8'));
 const digest=createHash('sha256').update(bytes).digest('hex');
 if(vectors.schema!=='fab.visual.exact-rational-vectors.v1'||
    vectors.seed!=='0x5eed1141'||vectors.count!==K||
    vectors.vectors?.length!==K||python.vectorSha256!==digest||
    python.count!==K||python.results?.length!==K)
   fail('vector identity/oracle length/digest mismatch');
 const get=o=>({lo:jsonExact(o.lo),hi:jsonExact(o.hi),nominal:jsonExact(o.nominal)});
 for(let i=0;i<K;i++){
  const v=vectors.vectors[i],actual=exactModelInterval(v.terms,v.duration);
  const expect=python.results[i];
  if(v.id!==i||expect.id!==i||
     JSON.stringify({power:get(actual.power),energy:get(actual.energy)})!==
     JSON.stringify({power:expect.power,energy:expect.energy}))
   fail('independent Fraction oracle disagreement at vector '+i);
 }
 process.stdout.write(json({schema:'fab.visual.exact-rational-crosslanguage.v1',
   status:'PASS',count:K,vectorSha256:digest,
   twoImplementations:'NODE_BIGINT_VS_PYTHON_DECIMAL_FRACTION',
   finiteTestScope:'SEEDED_10000_SYNTHETIC_CASES_NOT_A_UNIVERSAL_PROOF',
   physicalValidation:'NOT_RUN',formalProof:'NOT_RUN',release:'HOLD'}));
}else fail('usage: generate | verify <vectors.json> <python-results.json>');
