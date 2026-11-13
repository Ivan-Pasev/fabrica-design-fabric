#!/usr/bin/env node
/** Read-only, bounded CodexStation host ABI preflight. Never emits private file contents. */
import {existsSync,lstatSync,readFileSync,realpathSync} from 'node:fs';
import {basename,join,resolve,relative,sep,dirname} from 'node:path';
import {createHash} from 'node:crypto';
const argv=process.argv.slice(2);
const get=flag=>{const i=argv.indexOf(flag);return i>=0?argv[i+1]:null;};
const rootArg=get('--root');
const requested=get('--profile')||'generic';
const PROFILE=new Set(['generic','codexcodingstation','omega-next','antigravity']);
if(!rootArg||!PROFILE.has(requested)) {console.error('usage: host-abi-doctor --root <existing host> [--profile generic|codexcodingstation|omega-next|antigravity]');process.exit(2);}
const path=resolve(rootArg);
if(!existsSync(path)||lstatSync(path).isSymbolicLink()||!lstatSync(path).isDirectory()){console.error('HOLD: host path is not a genuine existing directory');process.exit(2);}
const root=realpathSync(path);
const look=['AGENTS.md','GEMINI.md','START_HERE.md','CONSTITUTION.md','package.json','.cs/STATE_AND_NEXT.md','.agents/skills','.agents/rules','.codexstation/extensions','.github','src/core.mjs','plugin/orca-plugin.json'];
const artifacts={};
for (const rel of look) {
  const full=join(root,rel);
  // Check each ancestor including target; never follow a symlink to host-private data.
  let cursor=full, unsafe=false;
  while(cursor!==root){if(existsSync(cursor)&&lstatSync(cursor).isSymbolicLink()){unsafe=true;break;}cursor=dirname(cursor);}
  if(unsafe){artifacts[rel]={present:true,kind:'SYMLINK_REJECTED'};continue;}
  if(!existsSync(full)){artifacts[rel]={present:false};continue;}
  const st=lstatSync(full);
  if(st.isDirectory())artifacts[rel]={present:true,kind:'DIRECTORY'};
  else if(st.isFile()){
    // Bound reads and expose only SHA and size; no file body or secrets.
    if(st.size>1024*1024){artifacts[rel]={present:true,kind:'OVERSIZE_FILE_REJECTED'};continue;}
    const b=readFileSync(full);
    artifacts[rel]={present:true,kind:'FILE',bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')};
  } else artifacts[rel]={present:true,kind:'UNSUPPORTED_FILE_TYPE'};
}
const bad=Object.entries(artifacts).filter(([,v])=>v.kind?.includes('REJECTED')||v.kind==='UNSUPPORTED_FILE_TYPE').map(([k])=>k);
const hasPolicy=artifacts['AGENTS.md'].kind==='FILE'||artifacts['GEMINI.md'].kind==='FILE'||artifacts['CONSTITUTION.md'].kind==='FILE';
const collision=existsSync(join(root,'.agents/skills/fab-visual'))||existsSync(join(root,'.codexstation/extensions/fab-visual'));
const codeMarker=artifacts['package.json'].kind==='FILE'&&artifacts['src/core.mjs'].kind==='FILE';
const status=bad.length?'HOLD_UNSAFE_ENTRY':collision?'HOLD_COLLISION':!hasPolicy?'HOLD_POLICY_UNRESOLVED':'CANDIDATE_ONLY';
const out={schema:'fab.visual.host-abi-preflight.v0.1',status,requestedProfile:requested,profileEvidence:requested==='codexcodingstation'&&codeMarker?'STRUCTURAL_MARKERS_ONLY':'DECLARED_PROFILE_ONLY',hostLabel:basename(root),rootRedacted:true,hostAuthority:'NOT_GRANTED',installAuthorization:'NOT_GRANTED',liveHostTest:'NOT_CLAIMED',detected:artifacts,blockedEntries:bad,collisions:collision,action:'read-only preflight; review host constitution and source before any explicit opt-in installation'};
console.log(JSON.stringify(out,null,2));
if(status.startsWith('HOLD'))process.exitCode=2;
