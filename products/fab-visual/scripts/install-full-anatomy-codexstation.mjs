#!/usr/bin/env node
import { existsSync, lstatSync, mkdirSync, cpSync, renameSync, rmSync, realpathSync, readFileSync, readdirSync, writeFileSync, statSync } from 'node:fs';
import { dirname, join, resolve, parse } from 'node:path';
import { fileURLToPath } from 'node:url';
import { inspectFullAnatomy, ANATOMY_ROOT, PIN, EXPECTED_BLOBS, gitBlobSha } from './full-anatomy-source.mjs';
import { execFileSync } from 'node:child_process';

const argv=process.argv.slice(2), n=argv.indexOf('--root'), apply=argv.includes('--apply');
const rootArg=n>=0?argv[n+1]:null;
if(!rootArg||!existsSync(rootArg)||!lstatSync(rootArg).isDirectory())throw new Error('Provide an existing host via --root <absolute-path>');
if(!resolve(rootArg).startsWith('/'))throw new Error('absolute host required');
const target=realpathSync(rootArg);
if(target===parse(target).root||target===resolve(dirname(fileURLToPath(import.meta.url)),'..'))throw new Error('unsafe target');
const destination=join(target,'.agents','skills','anatomy');
const receiptPath=join(target,'.codexstation','evidence','fab-visual-anatomy-full.json');
function guard(p){let current=dirname(p);while(current!==target){if(!current.startsWith(target+'/'))throw new Error('path escapes host');if(existsSync(current)&&lstatSync(current).isSymbolicLink())throw new Error('symlink ancestor '+current);current=dirname(current);}}
for(const p of [destination,receiptPath])guard(p);
const collisions=[destination,receiptPath].filter(existsSync);
if(collisions.length){console.error(JSON.stringify({status:'HOLD_COLLISION',collisions},null,2));process.exit(2);}
const assessment=inspectFullAnatomy({root:ANATOMY_ROOT,verifyBytes:true,clean:true});
if(assessment.status!=='SOURCE_PARITY_PASS'){console.error(JSON.stringify({status:'HOLD_SOURCE',assessment},null,2));process.exit(2);}
const proposal={status:apply?'INSTALL_CANDIDATE':'DRY_RUN',host:target,destination,upstreamCommit:PIN,blobCount:EXPECTED_BLOBS,contents:'FULL_ORIGINAL_SKILL_NOT_MODIFIED',authority:'INSTALLED_NOT_AUTHORIZED'};
if(!apply){console.log(JSON.stringify(proposal,null,2));process.exit(0);}
const stage=destination+'.stage-'+process.pid;
if(existsSync(stage))throw new Error('stage path collision');
try{
  mkdirSync(dirname(destination),{recursive:true});
  cpSync(ANATOMY_ROOT,stage,{recursive:true,force:false,errorOnExist:true,filter:(path)=>!(['.git'].includes(path.split('/').at(-1)))});
  const rows=execFileSync('git',['-C',ANATOMY_ROOT,'ls-tree','-r','-l','HEAD'],{encoding:'utf8'}).trim().split('\n');
  let count=0;
  for(const row of rows){const m=/^100644 blob ([0-9a-f]{40}) ([0-9]+)\t(.+)$/.exec(row);if(!m)throw new Error('tree parse');const file=join(stage,m[3]);const buf=readFileSync(file);if(buf.length!==Number(m[2])||gitBlobSha(buf)!==m[1])throw new Error('stage mismatch '+m[3]);count++;}
  if(count!==EXPECTED_BLOBS)throw new Error('staged file count wrong');
  renameSync(stage,destination);
  mkdirSync(dirname(receiptPath),{recursive:true});
  writeFileSync(receiptPath,JSON.stringify({...proposal,status:'INSTALLED_NOT_AUTHORIZED',verifiedFiles:count,installedAt:new Date().toISOString()},null,2)+'\n');
  console.log(JSON.stringify({status:'INSTALLED_NOT_AUTHORIZED',destination,verifiedFiles:count,receiptPath},null,2));
}catch(e){if(existsSync(stage))rmSync(stage,{recursive:true,force:true});throw e;}
