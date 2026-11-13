#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const PRODUCT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const ANATOMY_ROOT = join(PRODUCT_ROOT, 'upstream', 'anatomy');
export const PIN = '1482e8469b0a9e0d8cc18ea2740a01423d29ae80';
export const TREE_PIN = '89299cdfce386a71723a7e57bb9fe219875582fc';
export const EXPECTED_BLOBS = 173;
export const EXPECTED_BYTES = 27648351;
export const KNOWN_BLOBS = Object.freeze({
  'kit/iso-kit.mjs': '248ee01cc00dfaeee9d693f49f63e32913f03115',
  'kit/lathe.mjs': 'b2fb74dfda69aa6296152d76ec70f314ce2955f1',
  'kit/tube.mjs': '94d1c84a7b7a1d1b1000de9ae3c84f53d093901a',
  'kit/audit.mjs': '7fc329342210e9130f3dcdac2537cb9022c36e56',
  'LICENSE': 'aa20733917ffc919b6b04834e6a6e22909df7c76',
});

export const GROUPS = Object.freeze({
  skill: ['SKILL.md','agents/openai.yaml','README.md'],
  svg: ['kit/iso-kit.mjs','kit/iso-kit.ts','kit/iso.css','kit/lathe.mjs','kit/tube.mjs'],
  audit: ['kit/audit.mjs','scripts/lines.mjs','scripts/line-ends.mjs'],
  webgl: ['kit/gl.mjs','kit/gl-shared.mjs'],
  react: ['kit/react/draw.tsx','kit/react/live.tsx'],
  beta3d: ['kit/turn.mjs','kit/turn-fixed.mjs','kit/turn-build.mjs','kit/turn-audit.mjs'],
  canvas: ['kit/canvas-painter.mjs'],
  print: ['scripts/print.mjs','scripts/print-sheet.mjs','kit/pdf-button.mjs'],
  publish: ['scripts/publish.mjs','scripts/session.mjs','scripts/fingerprint.mjs'],
  browser: ['scripts/capture.mjs','scripts/drive.mjs','scripts/turn-check.mjs'],
  references: ['references/kit.md','references/craft.md','references/motion.md','references/verify.md','references/webgl.md','references/3d.md','references/print.md','references/publish.md'],
  cases: ['examples/arcade-cabinet/build.mjs','examples/desk-computer/build.mjs','examples/dial-indicator/build.mjs','examples/push-button/build.mjs','examples/raptor-engine/build.mjs','examples/ripple-tank/build.mjs','examples/turning-dial/build.mjs','examples/test-rig/figure.tsx','examples/spot-plate/figure.tsx'],
});
export function gitBlobSha(bytes) {
  const header=Buffer.from(`blob ${bytes.length}\0`);
  return createHash('sha1').update(header).update(bytes).digest('hex');
}
export function parseLsTree(output) {
  return String(output).split('\n').filter(Boolean).map(line=>{
    const m=/^100644\s+blob\s+([0-9a-f]{40})\s+([0-9]+)\t(.+)$/.exec(line);
    if(!m)throw new Error('unexpected upstream git tree entry: '+line.slice(0,100));
    return {path:m[3],sha:m[1],size:Number(m[2])};
  });
}
export function inspectFullAnatomy({root=ANATOMY_ROOT, verifyBytes=true, clean=false}={}) {
  const result={status:'NOT_RUN',root,pin:PIN,expectedTree:TREE_PIN,requiredCount:EXPECTED_BLOBS,requiredBytes:EXPECTED_BYTES,checked:0,groups:{},errors:[],scope:'PINNED_UPSTREAM_COMPLETE_GIT_TREE',executedOriginalTests:false};
  if(!existsSync(join(root,'.git'))) {result.status='BLOCKED_NO_FULL_CHECKOUT';result.errors.push('Missing complete pinned git submodule; run git submodule update --init --recursive');return result;}
  const run=(args)=>execFileSync('git',['-C',root,...args],{encoding:'utf8',timeout:25000,stdio:['ignore','pipe','pipe']}).trim();
  let entries=[];
  try{
    result.head=run(['rev-parse','HEAD']);
    result.tree=run(['rev-parse','HEAD^{tree}']);
    if(result.tree!==TREE_PIN)result.errors.push(`wrong root tree ${result.tree}`);
    if(result.head!==PIN)result.errors.push(`wrong git commit ${result.head}`);
    entries=parseLsTree(run(['ls-tree','-r','-l','HEAD']));
    result.count=entries.length;result.bytes=entries.reduce((sum,x)=>sum+x.size,0);
    if(result.count!==EXPECTED_BLOBS)result.errors.push(`blob count ${result.count} expected ${EXPECTED_BLOBS}`);
    if(result.bytes!==EXPECTED_BYTES)result.errors.push(`blob bytes ${result.bytes} expected ${EXPECTED_BYTES}`);
    const map=new Map(entries.map(x=>[x.path,x]));
    for(const [path,sha] of Object.entries(KNOWN_BLOBS))if(map.get(path)?.sha!==sha)result.errors.push(`known git object mismatch: ${path}`);
    for(const [group,paths] of Object.entries(GROUPS))result.groups[group]={paths:paths.length,present:paths.filter(path=>map.has(path)).length,role:'PRESENT_ONLY_NOT_FUNCTIONALLY_TESTED'};
    for(const [group,info] of Object.entries(result.groups))if(info.present!==info.paths)result.errors.push('group missing files '+group);
    if(verifyBytes){
      for(const e of entries){
        const file=join(root,e.path);
        if(!existsSync(file)||!statSync(file).isFile()){result.errors.push('missing working-tree file '+e.path);continue;}
        const buf=readFileSync(file);
        if(buf.length!==e.size||gitBlobSha(buf)!==e.sha)result.errors.push('byte mismatch '+e.path);
        result.checked++;
      }
    }
    if(clean){const s=run(['status','--porcelain']);if(s)result.errors.push('upstream working tree has local modifications');}
  }catch(err){result.errors.push('git inspection failed: '+String(err.message).slice(0,320));}
  result.status=result.errors.length?'FAIL':'SOURCE_PARITY_PASS';
  return result;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const result=inspectFullAnatomy({verifyBytes:!process.argv.includes('--metadata-only'),clean:process.argv.includes('--clean')});
  const out=process.argv.indexOf('--out');
  if(out>=0&&process.argv[out+1])writeFileSync(process.argv[out+1],JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
  if(result.status!=='SOURCE_PARITY_PASS')process.exitCode=2;
}
