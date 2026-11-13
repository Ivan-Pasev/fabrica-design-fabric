/**
 * FAB.VISUAL Ω7: independent conservative screen-space clearance assessment for
 * straight DECORATIVE links in the source-locked Anatomy isometric renderer.
 * This is NOT a tube/wire geometry audit, routed cable verifier, collision
 * proof, 3D occlusion proof, or permission to assert full-scene clearance.
 */
import * as K from '../../vendor/anatomy/kit/iso-kit.mjs';
import {assertScene} from '../visual/contract.mjs';
const finite2=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
/** Liang–Barsky inclusive segment/rectangle overlap. Conservative on tangency. */
export function segmentIntersectsAabb2d(a,b,rect,epsilon=1e-8) {
  if(!finite2(a)||!finite2(b)|| !rect || ![rect.x0,rect.y0,rect.x1,rect.y1].every(Number.isFinite))
    throw Error('invalid projected coordinates');
  if(!Number.isFinite(epsilon)||epsilon<0)throw Error('invalid epsilon');
  const left=rect.x0-epsilon,right=rect.x1+epsilon,top=rect.y0-epsilon,bottom=rect.y1+epsilon;
  if(left>right||top>bottom)throw Error('invalid projected bounds');
  const d=[b[0]-a[0],b[1]-a[1]];
  let t0=0,t1=1;
  const edges=[[-d[0],a[0]-left],[d[0],right-a[0]],[-d[1],a[1]-top],[d[1],bottom-a[1]]];
  for(const [p,q] of edges) {
    if(Math.abs(p)<1e-15){if(q<0)return false;continue;}
    const t=q/p;
    if(p<0)t0=Math.max(t0,t);
    else t1=Math.min(t1,t);
    if(t0>t1)return false;
  }
  return true;
}
/** Screen AABB of all eight corners of each visual-only extruded part. */
export function projectedPartBounds(part,projection,height3d=28) {
  if(!Number.isFinite(height3d)||height3d<=0)throw Error('height must be positive finite');
  const points=[];
  for(const x of [part.x,part.x+part.w])
    for(const y of [part.y,part.y+part.h])
      for(const z of [0,height3d])points.push(K.iso([x,y,z],projection));
  if(points.some(p=>!finite2(p)))throw Error('nonfinite projected corner');
  return {
    x0:Math.min(...points.map(p=>p[0])),y0:Math.min(...points.map(p=>p[1])),
    x1:Math.max(...points.map(p=>p[0])),y1:Math.max(...points.map(p=>p[1]))
  };
}
/**
 * A crossing is a possible overlap, not proof of actual depth occlusion.
 * No crossing conservatively excludes straight center-to-center link projection
 * from every non-endpoint solid's screen AABB, for the given camera only.
 */
export function analyzeProjectedLinks(scene,projection,{height3d=28,epsilon=1e-8}={}) {
  assertScene(scene);
  const parts=new Map(scene.parts.map(p=>[p.id,p]));
  const bounds=new Map(scene.parts.map(p=>[p.id,projectedPartBounds(p,projection,height3d)]));
  const mid=id=>{const p=parts.get(id);return K.iso([p.x+p.w/2,p.y+p.h/2,height3d/2],projection)};
  const crossings=[];const links=scene.links||[];
  links.forEach((link,index)=>{
    const a=mid(link.from),b=mid(link.to);
    for(const part of scene.parts){
      if(part.id===link.from||part.id===link.to)continue;
      if(segmentIntersectsAabb2d(a,b,bounds.get(part.id),epsilon))crossings.push({index,from:link.from,to:link.to,possibleObstruction:part.id});
    }
  });
  return {
    status:crossings.length?'INCONCLUSIVE':'PASS',
    scope:'PROJECTED_STRAIGHT_LINK_VS_NONENDPOINT_SOLID_AABB_ONLY',
    assessedLinks:links.length,
    assessedThirdPartyPairs:links.length*Math.max(0,scene.parts.length-2),
    possibleObstructions:crossings,
    true3dRouteAndWireToWire:'NOT_RUN',
    endpointClearance:'NOT_RUN',
    note:'AABB test is conservative in screen space; it does not certify 3D tube/wire routing, depth, endpoint attachment, or wire-wire clearance.'
  };
}