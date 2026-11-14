/**
 * FAB.VISUAL Ω11O — deterministic dimensional, balance and finite-graph audit.
 * Pure first-party mathematics. No empirical model, physical truth, signature,
 * live device authorization, privileged tool, or deployment is established.
 */
const DIM={
  DIMENSIONLESS:[0,0,0,0,0,0,0],
  LENGTH:[0,1,0,0,0,0,0],
  TIME:[0,0,1,0,0,0,0],
  MASS:[1,0,0,0,0,0,0],
  MASS_RATE:[1,0,-1,0,0,0,0],
  CURRENT:[0,0,0,1,0,0,0],
  TEMPERATURE:[0,0,0,0,1,0,0],
  FREQUENCY:[0,0,-1,0,0,0,0],
  SPEED:[0,1,-1,0,0,0,0],
  ACCELERATION:[0,1,-2,0,0,0,0],
  FORCE:[1,1,-2,0,0,0,0],
  PRESSURE:[1,-1,-2,0,0,0,0],
  ENERGY:[1,2,-2,0,0,0,0],
  POWER:[1,2,-3,0,0,0,0],
  VOLTAGE:[1,2,-3,-1,0,0,0],
  CHARGE:[0,0,1,1,0,0,0]
};
const SI={
  '1':['DIMENSIONLESS',1],'%':['DIMENSIONLESS',0.01],
  m:['LENGTH',1],mm:['LENGTH',0.001],km:['LENGTH',1000],
  s:['TIME',1],ms:['TIME',0.001],h:['TIME',3600],
  kg:['MASS',1],g:['MASS',0.001],
  'kg/s':['MASS_RATE',1],
  A:['CURRENT',1],K:['TEMPERATURE',1],
  Hz:['FREQUENCY',1],kHz:['FREQUENCY',1000],
  'm/s':['SPEED',1],'m/s^2':['ACCELERATION',1],
  N:['FORCE',1],Pa:['PRESSURE',1],kPa:['PRESSURE',1000],
  J:['ENERGY',1],kJ:['ENERGY',1000],Wh:['ENERGY',3600],kWh:['ENERGY',3600000],
  W:['POWER',1],kW:['POWER',1000],MW:['POWER',1000000],
  V:['VOLTAGE',1],kV:['VOLTAGE',1000],
  C:['CHARGE',1]
};
const float=x=>typeof x==='number'&&Number.isFinite(x);
const fail=reason=>{throw Error('QUANTITATIVE_CONTRACT_REJECT: '+reason)};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const identifier=x=>typeof x==='string'&&/^[a-z][a-z0-9_-]{0,55}$/.test(x);
export function getUnit(unit){
  if(!Object.hasOwn(SI,unit))fail('unknown unit '+String(unit)+'; no inferred conversions');
  const [dimension,factor]=SI[unit];
  return {unit,dimension,exponents:[...DIM[dimension]],toSI:factor};
}
export function auditAnatomyProjectionBasis(camera){
  if(!camera||!float(camera.azimuth)||!float(camera.elevation)||
     !float(camera.scale)||camera.scale<=0||camera.scale>1000||
     camera.elevation<=0||camera.elevation>=90||
     !Array.isArray(camera.origin)||camera.origin.length!==2||
     !camera.origin.every(float))fail('finite projection camera with elevation (0,90) required');
  const a=camera.azimuth*Math.PI/180,e=camera.elevation*Math.PI/180;
  const sinA=Math.sin(a),cosA=Math.cos(a),sinE=Math.sin(e),cosE=Math.cos(e);
  const right=[sinA,-cosA,0],down=[cosA*sinE,sinA*sinE,-cosE],
    depth=[cosA*cosE,sinA*cosE,sinE];
  const dot=(x,y)=>x.reduce((n,v,i)=>n+v*y[i],0);
  const orthogonality=Math.max(Math.abs(dot(right,down)),Math.abs(dot(right,depth)),
    Math.abs(dot(down,depth)),Math.abs(dot(right,right)-1),
    Math.abs(dot(down,down)-1),Math.abs(dot(depth,depth)-1));
  const cross=[right[1]*down[2]-right[2]*down[1],
    right[2]*down[0]-right[0]*down[2],right[0]*down[1]-right[1]*down[0]];
  const orientation=dot(cross,depth);
  const status=orthogonality<1e-12&&Math.abs(orientation-1)<1e-12?'PASS':'FAIL';
  return {schema:'fab.visual.projection-basis.v1',status,right,down,depth,
    orthogonalityResidual:orthogonality,orientation,
    cameraModel:'UPSTREAM_ISOMETRIC_ORTHOGRAPHIC',
    projectionKernel:[camera.scale*Math.sqrt(1.6),camera.origin],
    informationLoss:'3D_TO_2D_NON_INJECTIVE_NO_REAL_DEPTH_RECOVERY',
    validation:'FINITE_ANALYTIC_CAMERA_BASIS_ONLY',release:'HOLD'};
}
export function auditQuantitativeContract(input){
  if(!input||input.schema!=='fab.visual.quantitative.v1'||
     input.scope!=='SOURCE_DEFINED_NUMERICAL_CONSISTENCY_ONLY')
    fail('exact quantitative schema and nonphysical scope required');
  if(Object.keys(input).some(k=>!['schema','scope','source','balances','logic'].includes(k)))
    fail('unreviewed top-level claims or fields forbidden');
  if(Object.keys(input.source||{}).some(k=>!['id','kind'].includes(k)))
    fail('unknown source authority fields forbidden');
  if(!Array.isArray(input.balances)||input.balances.length<1||input.balances.length>24)
    fail('1–24 explicit numerical balances required');
  if(!input.source||typeof input.source.id!=='string'||input.source.id.length>250||
    typeof input.source.kind!=='string'||!['SYNTHETIC_EXAMPLE','MODEL_ASSUMPTION','UNVERIFIED_MEASUREMENT'].includes(input.source.kind))
    fail('explicit source reference and provenance kind required');
  const ids=new Set(),results=[];
  for(const b of input.balances){
    if(!identifier(b?.id)||ids.has(b.id))fail('unique bounded balance IDs required');
    if(Object.keys(b).some(k=>!['id','dimension','terms','tolerance'].includes(k)))
      fail('unknown numerical balance claim field');
    ids.add(b.id);
    if(!Object.hasOwn(DIM,b.dimension))fail('unknown expected SI dimension');
    if(!Array.isArray(b.terms)||b.terms.length<2||b.terms.length>40)
      fail('2–40 signed terms required');
    if(!b.tolerance||!float(b.tolerance.absolute)||b.tolerance.absolute<0||
       !float(b.tolerance.relative)||b.tolerance.relative<0||b.tolerance.relative>1)
      fail('explicit finite nonnegative absolute and relative tolerances required');
    const tolerance=getUnit(b.tolerance.unit);
    if(tolerance.dimension!==b.dimension)fail('tolerance must match target SI dimension');
    let sum=0,scale=0,uncertainty=0;
    const termIds=new Set(),provenance=[];
    for(const t of b.terms){
      if(!identifier(t?.id)||termIds.has(t.id))fail('unique bounded term IDs required');
      if(Object.keys(t).some(k=>!['id','value','unit','direction','uncertainty','source'].includes(k)))
        fail('unknown term authority field');
      termIds.add(t.id);
      if(!float(t.value)||t.value<0||!['IN','OUT'].includes(t.direction))
        fail('finite signed contributions with IN/OUT required');
      const u=getUnit(t.unit);
      if(u.dimension!==b.dimension)fail('incommensurate unit: '+t.id);
      if(!float(t.uncertainty)||t.uncertainty<0)
        fail('nonnegative finite absolute uncertainty required: '+t.id);
      if(!t.source||typeof t.source!=='string'||!t.source.trim()||t.source.length>250)
        fail('term source reference required: '+t.id);
      const value=t.value*u.toSI,delta=t.uncertainty*u.toSI;
      if(!float(value)||!float(delta))fail('SI conversion overflow');
      sum+=(t.direction==='IN'?1:-1)*value;
      scale+=Math.abs(value);
      uncertainty+=delta;
      if(![sum,scale,uncertainty].every(float))fail('SI accumulated value overflow');
      provenance.push({id:t.id,direction:t.direction,SI:value,source:t.source});
    }
    const bound=Math.max(b.tolerance.absolute*tolerance.toSI,
      b.tolerance.relative*scale);
    if(!float(bound))fail('SI tolerance overflow');
    const pass=Math.abs(sum)<=bound;
    results.push({id:b.id,dimension:b.dimension,
      dimensionExponents:[...DIM[b.dimension]],status:pass?'PASS':'FAIL',
      residualSI:sum,absoluteResidualSI:Math.abs(sum),
      toleranceSI:bound,uncertaintyWorstCaseSI:uncertainty,
      uncertaintyRule:'TRIANGLE_INEQUALITY_NO_INDEPENDENCE_ASSUMED',
      termCount:b.terms.length,terms:provenance,
      interpretation:'DECLARED_INPUT_NUMERICAL_BALANCE_ONLY'});
  }
  let graph=null;
  if(input.logic!==undefined){
    const g=input.logic;
    if(g?.schema!=='fab.visual.finite-release-graph.v1'||
       !Array.isArray(g.states)||g.states.length<1||g.states.length>100||
       !Array.isArray(g.transitions)||g.transitions.length>300||!identifier(g.initial))
      fail('bounded finite transition graph schema required');
    const states=new Map();
    for(const state of g.states){
      if(!identifier(state?.id)||states.has(state.id)||
         typeof state.released!=='boolean'||
         !['HOLD','NOT_RUN','APPROVED'].includes(state.authorization)||
         !['PASS','FAIL','NOT_RUN','INCONCLUSIVE'].includes(state.evidence))
        fail('invalid or duplicated finite graph state');
      states.set(state.id,state);
    }
    if(!states.has(g.initial))fail('graph initial state missing');
    const problems=[];
    for(const state of states.values()){
      if(state.released&&(state.authorization!=='APPROVED'||state.evidence!=='PASS'))
        problems.push(state.id+': released without declared authorization and evidence');
    }
    const edges=new Map([...states.keys()].map(id=>[id,[]]));
    for(const t of g.transitions){
      if(!states.has(t?.from)||!states.has(t?.to)||
         !['SUBMIT','HUMAN_APPROVAL','RELEASE_REQUEST','REVOKE','REJECT','RESET'].includes(t.event))
        fail('unknown graph transition endpoint or event');
      const from=states.get(t.from),to=states.get(t.to);
      if(from.authorization!=='APPROVED'&&to.authorization==='APPROVED'&&
         t.event!=='HUMAN_APPROVAL')
        problems.push(t.from+'->'+t.to+': approval without declared human approval event');
      if(!from.released&&to.released&&t.event!=='RELEASE_REQUEST')
        problems.push(t.from+'->'+t.to+': released without declared release request event');
      edges.get(t.from).push(t.to);
    }
    const reached=new Set([g.initial]),queue=[g.initial];
    while(queue.length){
      const id=queue.shift();
      for(const to of edges.get(id))if(!reached.has(to)){reached.add(to);queue.push(to);}
    }
    const unreachable=[...states.keys()].filter(id=>!reached.has(id));
    graph={schema:g.schema,status:problems.length?'FAIL':'PASS',
      checkedStates:states.size,checkedTransitions:g.transitions.length,
      reachableStates:reached.size,unreachableStates:unreachable,
      problems,assurance:'EXHAUSTIVE_ONLY_OVER_DECLARED_FINITE_GRAPH',
      realHumanApproval:'NOT_VERIFIED',release:'HOLD'};
  }
  return {
    schema:'fab.visual.quantitative-report.v1',
    status:results.every(x=>x.status==='PASS')&&(!graph||graph.status==='PASS')?'PASS':'FAIL',
    scope:input.scope,source:input.source,
    balances:results,logic:graph,
    physicalValidation:'NOT_RUN',empiricalInstrumentCalibration:'NOT_RUN',
    scientificCertification:'NOT_RUN',independentRendererValidation:'NOT_RUN',
    hostAuthorization:'NOT_RUN',publisherSignature:'NOT_PRESENT',
    resultMeaning:'MATHEMATICAL_INTERNAL_CONSISTENCY_NOT_PHYSICAL_TRUTH',
    release:'HOLD'};
}
