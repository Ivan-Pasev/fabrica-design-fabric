import { existsSync, readFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { assertScene } from '../visual/contract.mjs';
export const PIN = '1482e8469b0a9e0d8cc18ea2740a01423d29ae80';
export const UPSTREAM='https://github.com/wheresryan22/anatomy';
export function inspectAnatomy(root) {
  const dir=resolve(root);
  const kit=join(dir,'kit','iso-kit.mjs'); const license=join(dir,'LICENSE');
  const errors=[];
  if (!existsSync(kit) || !existsSync(license)) errors.push('missing Anatomy kit and/or LICENSE');
  else if (!readFileSync(license,'utf8').includes('MIT License')) errors.push('upstream MIT license not detected');
  let commit=null;
  if (existsSync(join(dir,'.git'))) {
    try { commit=execFileSync('git',['-C',dir,'rev-parse','HEAD'],{encoding:'utf8',timeout:3000}).trim(); }
    catch { errors.push('git revision cannot be verified'); }
    if (commit !== null && commit !== PIN) errors.push(`revision mismatch ${commit}`);
  } else errors.push('no .git metadata: revision cannot be authenticated');
  return {ok:errors.length===0,commit,pin:PIN,kit,errors};
}
export function anatomyPlan(scene) {
  assertScene(scene);
  return {adapter:'anatomy-skill',source:`${UPSTREAM}/tree/${PIN}`,commit:PIN,
    integration:'External pinned source; requires explicit installed clone and source verification before renderer invocation',
    scene:scene.id,parts:scene.parts.map(p=>({id:p.id,label:p.label,role:p.status||'neutral'})),
    requiredChecks:['A.auditOrExit','scripts/lines.mjs','scripts/capture.mjs','model-observable-parity','sandbox-safety'],status:'HOLD_UNTIL_UPSTREAM_VERIFIED'};
}
// Intentionally no untrusted code execution or automatic network clone.
