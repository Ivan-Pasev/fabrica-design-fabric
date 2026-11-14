/**
 * Ω11P First-party local IDE skill packaging, no remote execution.
 * --dry-run is zero-write. --write is an explicit human-invoked request
 * and creates an isolated previously absent directory only.
 */
import {lstatSync,readFileSync,mkdirSync,writeFileSync,renameSync,rmSync} from 'node:fs';
import {resolve,relative,dirname,parse,join,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const fail=s=>{throw Error('IDE_PACKAGE_HOLD: '+s)};
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const sources=[
{src:'skills/fab-visual-ide/SKILL.md',dst:'SKILL.md'},
{src:'IDE_START_HERE_FAB_VISUAL.md',dst:'IDE_START_HERE_FAB_VISUAL.md'},
{src:'products/fab-visual/agents/capability-manifest.v1.json',dst:'capability-manifest.v1.json'},
{src:'products/fab-visual/CONSTITUTION.md',dst:'CONSTITUTION.md'},
{src:'products/fab-visual/UPSTREAM_LOCK.json',dst:'UPSTREAM_LOCK.json'}
];
function stat(path){try{return lstatSync(path)}catch(e){if(e.code==='ENOENT')return null;throw e}}
function lockedAncestor(path){
 const full=resolve(path);let current=parse(full).root;
 const rest=full.slice(current.length).split(/[\\/]/).filter(Boolean);
 for(const part of rest){
   current=join(current,part);
   const f=stat(current);
   if(f?.isSymbolicLink())fail('symlink ancestor or destination forbidden: '+current);
   if(f&&!f.isDirectory()&&current!==full)fail('non-directory ancestor: '+current);
 }
}
function inTree(path,tree){
 const d=relative(tree,path);
 return d===''||(!d.startsWith('..')&&!isAbsolute(d));
}
export function planIdePackage(destination,{mode='dry-run'}={}){
 if(!['dry-run','write'].includes(mode)||typeof destination!=='string'||!destination.trim())
   fail('explicit destination and dry-run/write mode required');
 if(destination.includes('\0'))fail('NUL destination forbidden');
 const target=resolve(destination);
 const parent=dirname(target);
 if(inTree(target,root))fail('cannot overwrite or place installer inside source repository');
 if(target===parse(target).root||target===parent)fail('unsafe filesystem root');
 lockedAncestor(parent);
 if(stat(target))fail('destination already exists; no overwrite or collision');
 if(!stat(parent)?.isDirectory())fail('parent directory must already exist and be a directory');
 const files=sources.map(item=>{
   const path=resolve(root,item.src);
   if(!inTree(path,root))fail('source escape');
   const f=stat(path);
   if(!f?.isFile()||f.isSymbolicLink())fail('source missing or symlinked: '+item.src);
   const bytes=readFileSync(path);
   if(bytes.length<50||bytes.length>500000)fail('bounded source size check: '+item.src);
   return {source:item.src,destination:item.dst,sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length};
 });
 const evidence={
   schema:'fab.visual.ide-package-plan.v1',
   mode,destination:target,files,sourceRef:'EXACT_INSTALLED_SOURCE_COMMIT_MUST_BE_CHECKED_SEPARATELY',
   originalAnatomyCommit:'1482e8469b0a9e0d8cc18ea2740a01423d29ae80',
   installScope:'REFERENCE_SKILL_FILES_ONLY_NO_RUNTIME_BINARY',
   noNetwork:true,executesFetchedCode:false,hostAuthorization:'REQUIRED',
   publisherSignature:'NOT_PRESENT',scientificAdmission:'NOT_RUN',release:'HOLD'
 };
 if(mode==='dry-run')return {...evidence,wroteFiles:false};
 // Explicit write only. Stage in an exclusive, temporary sibling then atomically rename.
 const staging=target+'.fab-visual-stage-'+process.pid;
 if(stat(staging))fail('temporary staging path collision');
 let made=false;
 try{
   mkdirSync(staging,{recursive:false,mode:0o700});made=true;
   for(const item of sources){
     const source=resolve(root,item.src);
     writeFileSync(join(staging,item.dst),readFileSync(source),{flag:'wx',mode:0o600});
   }
   writeFileSync(join(staging,'PACKAGE_EVIDENCE.json'),
     JSON.stringify({...evidence,wroteFiles:true},null,2)+'\n',{flag:'wx',mode:0o600});
   if(stat(target))fail('destination race/collision');
   renameSync(staging,target);
   made=false;
   return {...evidence,wroteFiles:true};
 }finally{if(made)rmSync(staging,{recursive:true,force:true})}
}
