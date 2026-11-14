#!/usr/bin/env python3
"""Ω11H bounded virtual RAF and source-applied state experiment.

A custom test-only pre-page clock replaces requestAnimationFrame and
IntersectionObserver and, if writable, performance.now. This changes browser
semantics and MUST NEVER be called unchanged original production runtime.
Real GPU present, physical mesh/depth and true observer nonperturbation remain
unadmitted. Browser and source identity are separately recorded.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("omega11h_checkpoint",HERE/"omega11g-checkpoint-derivative.py")
K=importlib.util.module_from_spec(sp);sp.loader.exec_module(K)
sp2=importlib.util.spec_from_file_location("omega11h_assess",HERE/"omega11g-checkpoint-browser.py")
B=importlib.util.module_from_spec(sp2);sp2.loader.exec_module(B)
PIN=K.PIN
CLOCK_TIMES=(1000/60,2000/60,3000/60)
SCRIPT=r"""(()=>{
  'use strict';
  const state={
    schema:'fab.visual.omega11h.synthetic-raf.v1',
    now:0,steps:[],queue:[],nextId:1,intersections:0,
    performance_now_virtualized:false,script_kind:'TEST_ONLY_PRE_PAGE',
    renderer_presented_frame:'NOT_ADMITTED'
  };
  const priorNow=performance.now.bind(performance);
  try {
    Object.defineProperty(performance,'now',{configurable:true,value:()=>state.now});
    state.performance_now_virtualized=performance.now()===0;
  }catch(error){state.performance_now_virtualized=false;}
  window.requestAnimationFrame=(callback)=>{
    if(typeof callback!=='function')throw new TypeError('RAF must be a function');
    const id=state.nextId++;state.queue.push({id,callback});return id;
  };
  window.cancelAnimationFrame=(id)=>{state.queue=state.queue.filter(entry=>entry.id!==id);};
  window.IntersectionObserver=class ControlledIntersectionObserver {
    constructor(callback){if(typeof callback!=='function')throw new TypeError('IO callback');this.cb=callback;}
    observe(target){
      if(!target)throw new Error('observer target required');
      state.intersections++;
      this.cb([{target,isIntersecting:true,intersectionRatio:1}],this);
    }
    unobserve(){}disconnect(){}takeRecords(){return[];}
  };
  state.step=(now)=>{
    if(!Number.isFinite(now)||now<=state.now)throw new Error('nonmonotonic or invalid RAF timestamp');
    state.now=now;const batch=state.queue;state.queue=[];
    if(batch.length>400)throw new Error('virtual RAF oversubscribed');
    for(const item of batch){item.callback(now);}
    state.steps.push({now,delivered:batch.length,remaining:state.queue.length});
    return state.steps[state.steps.length-1];
  };
  window.__fab11hClock=state;
})();"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_clock(clock):
    if not isinstance(clock,dict) or clock.get("schema")!="fab.visual.omega11h.synthetic-raf.v1":
        return "FAIL_CLOCK_IDENTITY"
    if clock.get("performance_now_virtualized") is not True:
        return "FAIL_UNCONTROLLED_PERFORMANCE_NOW"
    steps=clock.get("steps")
    if not isinstance(steps,list) or len(steps)!=3:
        return "FAIL_INCOMPLETE_VIRTUAL_INPUT"
    for i,s in enumerate(steps):
        if abs(s.get("now",0)-CLOCK_TIMES[i])>1e-7 or type(s.get("delivered"))!=int:
            return "FAIL_NONMONOTONIC_OR_WRONG_RAF_SCHEDULE"
    if clock.get("renderer_presented_frame")!="NOT_ADMITTED":
        return "FAIL_FORGED_RENDERER_FRAME"
    if clock.get("intersections",0)<1:
        return "FAIL_SOURCE_VISIBILITY_GATE"
    return "PASS_TEST_ONLY_CLOCK_DRIVER"


async def single(browser,root,scene,side,proc,out):
    meta=K.D.SCENES[scene]
    page_path=(root/meta["relative"]).resolve()
    ctx=await browser.new_context(viewport={"width":1280 if scene=="raptor-light" else 390,"height":850},
       device_scale_factor=1,color_scheme="light",locale="en-US",timezone_id="UTC",
       reduced_motion="no-preference")
    await ctx.add_init_script(SCRIPT)
    page=await ctx.new_page()
    errors=[];blocked=[]
    page.on("pageerror",lambda e:errors.append(str(e)[:240]))
    async def guard(route):
        url=route.request.url
        if url.startswith(("file://","data:")): await route.continue_()
        else:
            blocked.append(url[:180]);await route.abort()
    await page.route("**/*",guard)
    try:
        await page.goto(page_path.as_uri(),wait_until="load",timeout=50000)
        if await page.locator(meta["stage"]).count()!=1:
            raise ValueError("original full stage missing or duplicated")
        # Controlled virtual clock: no native RAF is permitted to advance here.
        # Clock input is explicit and equal across each source/derivative process.
        for tick in CLOCK_TIMES:
            await page.evaluate("(ms)=>window.__fab11hClock.step(ms)",tick)
        info=await page.evaluate("""(selector)=>{
          const c=window.__fab11hClock;
          const s=document.querySelector(selector),r=s.getBoundingClientRect();
          return {
             clock:{schema:c.schema,steps:c.steps,intersections:c.intersections,
                    performance_now_virtualized:c.performance_now_virtualized,
                    renderer_presented_frame:c.renderer_presented_frame},
             stage:{selector,rect:[r.x,r.y,r.width,r.height],
                    aria:s.getAttribute('aria-valuenow'),svg:s.querySelectorAll('svg').length},
             stage_html:s.outerHTML,
             derivative:window.__fab11gControl||null
          };
        }""",meta["stage"])
        out.mkdir(parents=True,exist_ok=True)
        png=out/f"{scene}-{side}-p{proc}.png"
        await page.screenshot(path=str(png),animations="disabled",caret="hide")
        witness=info["derivative"]
        if side=="original":
            classification=("PASS_TEST_CLOCK_UNMODIFIED_SOURCE" if witness is None
                            else "FAIL_ORIGINAL_PAGE_CONTAMINATED")
        else:
            classification=B.verify_checkpoint(scene,side,witness)
        return {"scene":scene,"side":side,"process":proc,
          "source_html_sha256":sha(page_path.read_bytes()),
          "clock":info["clock"],"clock_grade":strict_clock(info["clock"]),
          "stage":info["stage"],"stage_dom_sha256":sha(info["stage_html"].encode()),
          "screenshot_sha256":sha(png.read_bytes()),
          "checkpoint":witness,
          "classification":classification,"errors":errors,
          "blocked_requests":blocked}
    finally:
        await ctx.close()


async def run(args):
    from playwright.async_api import async_playwright
    roots={x:getattr(args,x).resolve(strict=True) for x in ("original","minimal","observing")}
    manifest=json.loads(args.manifest.read_text())
    if manifest.get("source_commit")!=PIN or manifest.get("release")!="HOLD":
        raise ValueError("wrong source pin or release boundary")
    for scene,meta in K.D.SCENES.items():
        K.D.checked_file(roots["original"],meta["relative"],meta["sha"])
        for side in ("minimal","observing"):
            mode="MINIMAL_CHECKPOINT" if side=="minimal" else "OBSERVING_CHECKPOINT"
            entry=manifest["variants"].get(scene+"|"+mode)
            if not entry or entry["original_html_sha256"]!=meta["sha"]:
                raise ValueError("source/derivative manifest missing")
            K.D.checked_file(roots[side],meta["relative"],entry["derivative_html_sha256"])
    args.output.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"fab.visual.omega11h.synthetic-clock-experiment.v1",
      "source_commit":PIN,"original_source_untouched":True,
      "script_sha256":sha(SCRIPT.encode()),
      "clock_input_ms":list(CLOCK_TIMES),
      "original_browser_semantics":"INTENTIONALLY_CHANGED_IN_TEST_HARNESS",
      "performance_now":"VIRTUALIZED_TEST_ONLY",
      "intersection_observer":"VIRTUALIZED_ALWAYS_INTERSECTING_TEST_ONLY",
      "normal_browser_runtime_equivalence":"NOT_ESTABLISHED",
      "observer_nonperturbation":"NOT_ESTABLISHED",
      "gpu_presented_frame":"NOT_ADMITTED",
      "real_mesh_depth":"NOT_RUN",
      "release":"HOLD","observations":[]}
    async with async_playwright() as p:
        for scene in K.D.SCENES:
            for side in ("original","minimal","observing"):
                for proc in (0,1):
                    browser=await p.chromium.launch(headless=True,args=["--disable-background-networking","--disable-dev-shm-usage"])
                    try:
                        receipt["browser_version"]=browser.version
                        receipt["observations"].append(await single(browser,roots[side],scene,side,proc,args.output/"images"))
                    finally:await browser.close()
    errors=[]
    for x in receipt["observations"]:
        if x["errors"] or x["blocked_requests"]:
            errors.append(x["scene"]+"/"+x["side"]+":browser errors")
        if x["clock_grade"]!="PASS_TEST_ONLY_CLOCK_DRIVER":
            errors.append(x["scene"]+"/"+x["side"]+":"+x["clock_grade"])
        if x["classification"] not in ("PASS_TEST_CLOCK_UNMODIFIED_SOURCE","PASS_FIXED_APPLICATION_ORDINAL_ONLY"):
            errors.append(x["scene"]+"/"+x["side"]+":"+x["classification"])
    receipt["source_applied_ordinal_gate"]=("PASS_TEST_ONLY" if not errors else "FAIL_OR_INCONCLUSIVE")
    receipt["errors"]=errors
    # Never interpret identical stage pixels as a scientific renderer proof.
    derived=[]
    for scene in K.D.SCENES:
        controls=[x for x in receipt["observations"] if x["scene"]==scene]
        observed=[x for x in controls if x["side"]=="observing"]
        minimal=[x for x in controls if x["side"]=="minimal"]
        sigs=[]
        for x in observed:
            c=x["checkpoint"]
            if c and len(c.get("events",[]))==3:
                v=c["events"][-1]["applied_state"]
                sigs.append(sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()))
        derived.append({
         "scene":scene,"observed_state_sha256":sigs,
         "observed_state_repeatability":"MATCH" if len(sigs)==2 and len(set(sigs))==1 else "MISMATCH_OR_MISSING",
         "minimal_vs_observed_stage_dom":"MATCH" if
             len({x["stage_dom_sha256"] for x in minimal+observed})==1 else "MISMATCH",
         "minimal_vs_observed_screenshots":"MATCH" if
             len({x["screenshot_sha256"] for x in minimal+observed})==1 else "MISMATCH",
         "source_equivalence":"NOT_ADMITTED",
         "causal_observer_impact":"NOT_ESTABLISHED"
        })
    receipt["controlled_state_comparisons"]=derived
    (args.output/"OMEGA11H_CLOCK_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"case_count":len(receipt["observations"]),
                       "ordinal_gate":receipt["source_applied_ordinal_gate"],
                       "comparisons":derived,
                       "frame":"NOT_ADMITTED","release":"HOLD"}))
    return 0 if not errors else 2


def main():
    a=argparse.ArgumentParser()
    for key in ("original","minimal","observing","manifest","output"):
        a.add_argument("--"+key,type=Path,required=True)
    raise SystemExit(asyncio.run(run(a.parse_args())))


if __name__=="__main__":main()
