#!/usr/bin/env node
/** Bounded, dependency-free Chromium CDP smoke acceptance for generated FAB.VISUAL synthetic timeline.
 * Trust boundary: only render generated local HTML under a fresh, disposable browser profile.
 * No external URLs, privileged source browsing or scientific/certification assertions.
 */
import {spawn, spawnSync} from 'node:child_process';
import {mkdtempSync, readFileSync, rmSync, mkdirSync, writeFileSync, existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
// No navigation needed: inject trusted generated HTML into isolated about:blank target.
const html=resolve(process.argv[2]||'dist/anatomy-timeline.html');
const evidence=resolve(process.argv[3]||'dist/browser-acceptance');
if(!existsSync(html))throw Error('Missing built synthetic timeline: '+html);
const chrome=[process.env.CHROME_BIN,'google-chrome','chromium','chromium-browser','google-chrome-stable'].filter(Boolean).find(x=>spawnSync('which',[x],{encoding:'utf8'}).status===0);
if(!chrome)throw Error('Chromium not found: set CHROME_BIN');
const profile=mkdtempSync(join(tmpdir(),'fab-visual-browser-'));
const args=['--headless=new','--disable-gpu','--disable-background-networking','--no-first-run','--no-default-browser-check','--disable-dev-shm-usage','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'];
if(process.getuid?.()===0)args.splice(1,0,'--no-sandbox'); // local root test only; CI runner should retain browser sandbox
let proc=null,ws=null;
const results=[];
const assert=(name,ok,details={})=>{results.push({name,status:ok?'PASS':'FAIL',details});if(!ok)throw Error(name+': '+JSON.stringify(details));};
const sleep=ms=>new Promise(done=>setTimeout(done,ms));
const pending=new Map();
let seq=0;
async function cmd(method,params={}){
 const id=++seq;const promise=new Promise((resolve,reject)=>{const timeout=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},10000);pending.set(id,{resolve:x=>{clearTimeout(timeout);resolve(x)},reject:e=>{clearTimeout(timeout);reject(e)}})});
 ws.send(JSON.stringify({id,method,params}));return promise;
}
async function evaluate(expression){const r=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error('browser exception '+JSON.stringify(r.exceptionDetails));return r.result?.value;}
async function key(key,keyCode){await cmd('Input.dispatchKeyEvent',{type:'rawKeyDown',key,code:key,windowsVirtualKeyCode:keyCode,nativeVirtualKeyCode:keyCode,text:key==='Enter'?'\r':undefined,unmodifiedText:key==='Enter'?'\r':undefined});await cmd('Input.dispatchKeyEvent',{type:'char',text:key==='Enter'?'\r':'',key,code:key,windowsVirtualKeyCode:keyCode});await cmd('Input.dispatchKeyEvent',{type:'keyUp',key,code:key,windowsVirtualKeyCode:keyCode});}
async function run(){
 proc=spawn(chrome,args,{stdio:'ignore'});
 const portfile=join(profile,'DevToolsActivePort');
 for(let i=0;i<140&&!existsSync(portfile);i++){if(proc.exitCode!==null)throw Error('Chrome exited '+proc.exitCode);await sleep(100)}
 if(!existsSync(portfile))throw Error('Chrome debugger did not start');
 const port=Number(readFileSync(portfile,'utf8').split('\n')[0]);
 let tabs=await (await fetch(`http://127.0.0.1:${port}/json`)).json();
 const tab=tabs.find(t=>t.type==='page'&&t.webSocketDebuggerUrl);
 if(!tab)throw Error('No browser target');
 ws=new WebSocket(tab.webSocketDebuggerUrl);
 await new Promise((ok,fail)=>{ws.onopen=ok;ws.onerror=fail});
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}};
 await cmd('Page.enable');await cmd('Runtime.enable');
 const frames=await cmd('Page.getFrameTree');
 await cmd('Page.setDocumentContent',{frameId:frames.frameTree.frame.id,html:readFileSync(html,'utf8')});
 let state='';for(let i=0;i<100;i++){state=await evaluate(`document.readyState === 'complete' && Boolean(document.querySelector('#phase')) && Boolean(document.querySelector('#stage svg'))`).catch(()=>false);if(state)break;await sleep(80)}
 if(!state){const debug=await evaluate(`({url:location.href,ready:document.readyState,body:document.body?.outerHTML?.slice(0,500),phase:!!document.querySelector('#phase'),stage:!!document.querySelector('#stage svg')})`).catch(e=>({error:e.message}));console.error('DEBUG',JSON.stringify(debug));}
 assert('initial page ready',Boolean(state));
 const initial=await evaluate(`({phase:document.querySelector('#phase')?.textContent,svg:!!document.querySelector('#stage svg'),buttons:[...document.querySelectorAll('button')].map(b=>b.textContent),slider:document.querySelector('#seek')?.getAttribute('aria-label')})`);
 assert('semantic controls and SVG',initial.svg && initial.buttons.includes('Next')&&initial.buttons.includes('Previous')&&Boolean(initial.slider),initial);
 assert('timeline begins at first state',/Frame 1 of 5/.test(initial.phase),{phase:initial.phase});
 await cmd('Page.bringToFront'); await evaluate(`document.querySelector('#next').focus();true`);await key('Enter',13);await sleep(150);
 const next=await evaluate(`document.querySelector('#phase').textContent`);
 assert('keyboard Next activates subsequent frame',/Frame 2 of 5/.test(next),{phase:next});
 await evaluate(`document.querySelector('#prev').focus();true`);await key('Enter',13);await sleep(150);
 assert('keyboard Previous reverses frame',/Frame 1 of 5/.test(await evaluate(`document.querySelector('#phase').textContent`)));
 await evaluate(`document.querySelector('#seek').focus();true`);await key('End',35);await sleep(100);
 const end=await evaluate(`({phase:document.querySelector('#phase').textContent,release:document.querySelector('[data-part="release"]')?.getAttribute('data-status'),range:document.querySelector('#seek').value})`);
 assert('keyboard End changes state and release geometry together',end.range==='4'&&/Frame 5 of 5/.test(end.phase)&&end.release==='RELEASED',end);
 await cmd('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
 assert('browser recognizes reduced motion preference',await evaluate(`matchMedia('(prefers-reduced-motion: reduce)').matches`)===true);
 await cmd('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await sleep(100);
 const narrow=await evaluate(`({innerWidth:innerWidth,docWidth:document.documentElement.scrollWidth,controls:[...document.querySelectorAll('.ctrl button,.ctrl input')].map(e=>e.getBoundingClientRect().width)})`);
 assert('390px viewport avoids document overflow',narrow.docWidth<=narrow.innerWidth+2,narrow);
 const ax=await cmd('Accessibility.getFullAXTree');
 const names=(ax.nodes||[]).map(n=>({role:n.role?.value,name:n.name?.value})).filter(n=>n.name);
 assert('AX tree contains named transport controls',names.some(n=>n.name==='Next'&&n.role==='button')&&names.some(n=>n.name==='Previous'&&n.role==='button')&&names.some(n=>n.name==='Synthetic model state'),{found:names.slice(0,20)});
 const shot=await cmd('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 mkdirSync(evidence,{recursive:true});writeFileSync(join(evidence,'omega7-mobile-final.png'),Buffer.from(shot.data,'base64'));
 return {result:'PASS_BOUNDED',browser:chrome,node:process.version,tests:results,scope:'synthetic local timeline/one Chromium build; keyboard Next/Previous/End, AX labels, responsive 390px, reduced motion media state, screenshot',limitations:['No real host','Not screenreader assistive technology evaluation','Not cross-browser validation','No scientific or hardware claims']};
}
try{const report=await run();mkdirSync(evidence,{recursive:true});writeFileSync(join(evidence,'omega7-browser-receipt.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));}
catch(e){const report={result:'FAIL',error:e.message,node:process.version,tests:results};mkdirSync(evidence,{recursive:true});writeFileSync(join(evidence,'omega7-browser-receipt.json'),JSON.stringify(report,null,2)+'\n');console.error(JSON.stringify(report));process.exitCode=1;}
finally{ws?.close();proc?.kill('SIGTERM');await sleep(150);rmSync(profile,{recursive:true,force:true});}