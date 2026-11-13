/** Geometry oracle independent of the Anatomy raster auditor. */
import { assertScene } from '../visual/contract.mjs';
import * as A from '../../vendor/anatomy/kit/audit.mjs';

export function rayBoxIntersection(origin, direction, min, max, tolerance=1e-12) {
  let enter=-Infinity,leave=Infinity;
  for(let i=0;i<3;i++) {
    if(Math.abs(direction[i])<=tolerance) {
      if(origin[i]<min[i]-tolerance||origin[i]>max[i]+tolerance)return null;
      continue;
    }
    const a=(min[i]-origin[i])/direction[i],b=(max[i]-origin[i])/direction[i];
    enter=Math.max(enter,Math.min(a,b));leave=Math.min(leave,Math.max(a,b));
    if(leave<enter)return null;
  }
  return leave>Math.max(enter,0) ? {enter:Math.max(enter,0),leave} : null;
}
function mid(a,b){return a.map((v,i)=>(v+b[i])/2);}
/** Verify that a world-space thin segment truly hides behind an AABB from the camera. */
export function sampleTubeOcclusion({plateMin,plateMax,points,radius,projection,step=0.25}) {
  const V=A.cameraBasis(projection).V;
  const center=mid(points[0],points[points.length-1]);
  const hit=rayBoxIntersection(center,V,plateMin,plateMax);
  const panel=A.box(plateMin,plateMax,{name:'plate'});
  const tube=A.tube(points,radius,{name:'tube'});
  const overlaps=A.overlapsOf([
    {name:'plate',key:1,shapes:[panel]},
    {name:'tube',key:0,shapes:[tube]}
  ],projection,{step});
  const screenWidth=2*radius*projection.scale*Math.sqrt(1.6);
  const uncertain=screenWidth < 3*step || (!!hit && !overlaps.pairs.length);
  return {
    analyticOccluded:!!hit,
    analyticHit:hit,
    upstreamPairs:overlaps.pairs.length,
    sampledDepthAreas:overlaps.pairs.map(p=>p.front.map(x=>x.area)),
    screenWidth,
    threshold:3*step,
    assurance:uncertain?'INCONCLUSIVE':(hit && !overlaps.pairs.length?'FAIL':'BOUNDED_SAMPLED'),
    note:'Analytic center-ray AABB intersection compared with upstream sampled raster; not complete tube/plate surface intersection.'
  };
}
export function checkSceneAabbIndependently(scene, {height=28}={}) {
  assertScene(scene);
  const problems=[];
  const boxes=scene.parts.map(p=>({id:p.id,min:[p.x,p.y,0],max:[p.x+p.w,p.y+p.h,height]}));
  for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
    const a=boxes[i],b=boxes[j];
    const along=a.min.every((v,k)=> Math.min(a.max[k],b.max[k])-Math.max(v,b.min[k])>1e-8);
    if(along)problems.push({kind:'AABB_INTERSECTION',a:a.id,b:b.id});
  }
  return {ok:problems.length===0, problems, check:'INDEPENDENT_ANALYTIC_AABB_INTERSECTION',scope:'Visual metaphor boxes, not real-world physical solids'};
}
