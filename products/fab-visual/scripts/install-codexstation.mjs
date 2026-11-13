#!/usr/bin/env node
import {existsSync, realpathSync, mkdirSync, cpSync, readFileSync, writeFileSync, lstatSync} from 'node:fs';
import {join, resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const packageRoot=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const argv=process.argv.slice(2);
function get(flag){const at=argv.indexOf(flag);return at>=0?argv[at+1]:undefined;}
const targetArg=get('--root');
const apply=argv.includes('--apply');
const replace=argv.includes('--replace');
if(!targetArg || !existsSync(targetArg) || !lstatSync(targetArg).isDirectory()) {console.error('usage: --root <existing deployment dir> [--apply] [--replace]');process.exit(2);}
const target=realpathSync(targetArg);
if(target==='/'||target===packageRoot) {console.error('invalid install target');process.exit(2);}
const extension=join(target,'.codexstation','extensions','fab-visual');
const skill=join(target,'.agents','skills','fab-visual');
const items=[['src',join(extension,'src')],['bin',join(extension,'bin')],['skills/fab-visual/SKILL.md',join(skill,'SKILL.md')],['extensions/codexstation-fab-visual/AGENTS.md',join(extension,'AGENTS.md')],['UPSTREAM_LOCK.json',join(extension,'UPSTREAM_LOCK.json')]];
const collisions=items.filter(([,dst])=>existsSync(dst)).map(([,dst])=>dst);
if(collisions.length && !replace){console.error(JSON.stringify({status:'HOLD_COLLISION',paths:collisions},null,2));process.exit(2);}
const proposal={status:apply?'CANDIDATE_INSTALL':'DRY_RUN',root:target,extension,skill,items:items.map(([src,dst])=>({src,dst})),collisions};
if(!apply){console.log(JSON.stringify(proposal,null,2));process.exit(0);}
if(replace){console.error('Replacement is forbidden: superseded content must be migrated via a separately reviewed operation');process.exit(2);}
for(const [src,dst] of items){mkdirSync(dirname(dst),{recursive:true});cpSync(join(packageRoot,src),dst,{recursive:true,errorOnExist:true,force:false});}
const digest=createHash('sha256').update(JSON.stringify(proposal.items)).digest('hex');
const witness={...proposal,status:'INSTALLED_NOT_AUTHORIZED',digest,installedAt:new Date().toISOString()};
writeFileSync(join(extension,'INSTALL_RECEIPT.json'),JSON.stringify(witness,null,2)+'\n');
console.log(JSON.stringify({status:witness.status,extension,skill,receipt:join(extension,'INSTALL_RECEIPT.json')},null,2));
