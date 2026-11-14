#!/usr/bin/env python3
"""Ω11I browser API observation of source-locked Anatomy render calls.

TEST-HARNESS ONLY.  Canvas/WebGL API method calls (even on success) are not
a GPU compositor-presented frame, framebuffer provenance or real 3D depth.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("omega11i_clock_base",HERE/"omega11h-virtual-raf.py")
H=importlib.util.module_from_spec(sp);sp.loader.exec_module(H)
K=H.K

PROBE=r"""(()=>{
  const state={schema:'fab.visual.omega11i.render-api-observer.v1',
    context_requests:[],draw_calls:[],probe_kind:'TEST_ONLY_MONKEYPATCH',
    actual_presented_frame:'NOT_ADMITTED',framebuffer_readback:'NOT_RUN'};
  const originalGetContext=HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext=function(type,...args){
    const value=originalGetContext.call(this,type,...args);
    state.context_requests.push({type:String(type),granted:Boolean(value)});
    return value;
  };
  const candidates=[
    ['webgl1',typeof WebGLRenderingContext!=='undefined'?WebGLRenderingContext.prototype:null],
    ['webgl2',typeof WebGL2RenderingContext!=='undefined'?WebGL2RenderingContext.prototype:null]
  ];
  for(const [api,proto] of candidates){
    if(!proto) continue;
    for(const name of ['drawArrays','drawElements']){
      const original=proto[name];
      if(typeof original!=='function') continue;
      try{
        Object.defineProperty(proto,name,{configurable:true,writable:true,value:function(...args){
          const value=original.apply(this,args);
          state.draw_calls.push({api,method:name});
          return value;
        }});
      }catch(e){state["wrap_error_"+api+"_"+name]=String(e).slice(0,150);}
    }
  }
  window.__fab11iRenderObserver=state;
})();"""

def sha(b):
    return hashlib.sha256(b).hexdigest()

def classify_draw_calls(value):
    if not isinstance(value,dict) or value.get("schema")!="fab.visual.omega11i.render-api-observer.v1":
        return "FAIL_WRONG_RENDER_OBSERVER"
    if value.get("actual_presented_frame")!="NOT_ADMITTED" or value.get("framebuffer_readback")!="NOT_RUN":
        return "FAIL_FORGED_GPU_OR_DEPTH_ATTESTATION"
    if value.get("probe_kind")!="TEST_ONLY_MONKEYPATCH":
        return "FAIL_INSTRUMENTATION_UNDISCLOSED"
    contexts=value.get("context_requests")
    draws=value.get("draw_calls")
    if not isinstance(contexts,list) or not isinstance(draws,list):
        return "FAIL_RENDER_EVENTS_MISSING"
    if any(not isinstance(x,dict) or x.get("method") not in ("drawArrays","drawElements")
           or x.get("api") not in ("webgl1","webgl2") for x in draws):
        return "FAIL_RENDER_METHOD_PROVENANCE"
    if any(not isinstance(x,dict) or type(x.get("granted"))!=bool for x in contexts):
        return "FAIL_CONTEXT_PROVENANCE"
    return "PASS_BOUNDED_API_CALL_CAPTURE_NOT_GPU_PRESENT"

async def one(browser,root,scene,side,process,out):
    meta=K.D.SCENES[scene]
    context=await browser.new_context(viewport={"width":1280 if scene=="raptor-light" else 390,"height":850},
        device_scale_factor=1,locale="en-US",timezone_id="UTC",
        reduced_motion="no-preference",color_scheme="light")
    # Different prepage injections are independent of each other's order.
    await context.add_init_script(H.SCRIPT)
    await context.add_init_script(PROBE)
    page=await context.new_page()
    errors=[];blocked=[]
    page.on("pageerror",lambda exc:errors.append(str(exc)[:220]))
    async def deny_external(route):
        url=route.request.url
        if url.startswith(("file://","data:")):await route.continue_()
        else:
            blocked.append(url[:200]);await route.abort()
    await page.route("**/*",deny_external)
    file=(root/meta["relative"]).resolve()
    try:
        await page.goto(file.as_uri(),wait_until="load",timeout=55000)
        locator=page.locator(meta["stage"])
        if await locator.count()!=1:raise ValueError("actual source stage missing/ambiguous")
        for t in H.CLOCK_TIMES:
            await page.evaluate("(t)=>window.__fab11hClock.step(t)",t)
        observed=await page.evaluate("""selector=>{
          const node=document.querySelector(selector),stage=node.getBoundingClientRect();
          const p=window.__fab11iRenderObserver;
          const c=window.__fab11hClock;
          return {
            probe:p?JSON.parse(JSON.stringify(p)):null,
            clock:{schema:c.schema,steps:c.steps,intersections:c.intersections,
                   performance_now_virtualized:c.performance_now_virtualized,
                   renderer_presented_frame:c.renderer_presented_frame},
            stage:{selector,rect:[stage.x,stage.y,stage.width,stage.height],
                   canvases:node.querySelectorAll('canvas').length,
                   svg:node.querySelectorAll('svg').length},
            derivative:window.__fab11gControl||null,
            html:node.outerHTML
          };
        }""",meta["stage"])
        if not isinstance(observed["stage"]["rect"],list) or observed["stage"]["rect"][2]<20 or observed["stage"]["rect"][3]<20:
            raise ValueError("wrong full-size target stage")
        out.mkdir(parents=True,exist_ok=True)
        screen=out/f"{scene}-{side}-p{process}.png"
        await page.screenshot(path=str(screen),animations="disabled",caret="hide")
        return {"scene":scene,"side":side,"process":process,"source_html_sha256":sha(file.read_bytes()),
         "probe":observed["probe"],"probe_grade":classify_draw_calls(observed["probe"]),
         "clock_grade":H.strict_clock(observed["clock"]),
         "stage":observed["stage"],"stage_html_sha256":sha(observed["html"].encode()),
         "screenshot_sha256":sha(screen.read_bytes()),
         "source_applied_grade":"PASS_ORIGINAL_UNINSTRUMENTED_TEST_CLOCK" if side=="original" and observed["derivative"] is None
           else H.B.verify_checkpoint(scene,side,observed["derivative"]) if side!="original"
           else "FAIL_ORIGINAL_DERIVATIVE_HOOK",
         "page_errors":errors,"blocked_external_urls":blocked}
    finally:
        await context.close()

async def run(args):
    from playwright.async_api import async_playwright
    roots={key:getattr(args,key).resolve(strict=True) for key in ("original","minimal","observing")}
    manifest=json.loads(args.manifest.read_text())
    if manifest.get("source_commit")!=K.PIN or manifest.get("frame_attestation")!="NOT_ADMITTED" or manifest.get("release")!="HOLD":
        raise ValueError("untrusted source/derivative manifest")
    for scene,meta in K.D.SCENES.items():
        K.D.checked_file(roots["original"],meta["relative"],meta["sha"])
        for side in ("minimal","observing"):
            mode="MINIMAL_CHECKPOINT" if side=="minimal" else "OBSERVING_CHECKPOINT"
            record=manifest.get("variants",{}).get(scene+"|"+mode)
            if not record or record.get("original_html_sha256")!=meta["sha"]:
                raise ValueError("missing original source lineage")
            K.D.checked_file(roots[side],meta["relative"],record["derivative_html_sha256"])
    receipt={"schema":"fab.visual.omega11i.draw-api-boundary.v1",
       "source_pin":K.PIN,"probe_script_sha256":sha(PROBE.encode()),
       "virtual_clock_script_sha256":sha(H.SCRIPT.encode()),
       "browser_clock_grade":"SYNTHETIC_TEST_ONLY",
       "source_page_html_mutation":"NONE",
       "observer_mutation":"TEST_ONLY_RUNTIME_JS_PROTOTYPE_INTERCEPTION",
       "actual_gpu_present":"NOT_ADMITTED",
       "geometry_or_depth":"NOT_RUN",
       "webgl_api_calls_mean_presented_frame":False,
       "actual_renderer_equivalence":"NOT_ADMITTED",
       "source_static_audit_scope":"PINNED_ANATOMY_ORIGINAL",
       "release":"HOLD","observations":[]}
    args.output.mkdir(parents=True,exist_ok=True)
    async with async_playwright() as p:
        for scene in K.D.SCENES:
            for side in ("original","minimal","observing"):
                for proc in (0,1):
                    browser=await p.chromium.launch(headless=True,args=["--disable-background-networking","--disable-dev-shm-usage"])
                    try:
                        receipt["browser_version"]=browser.version
                        receipt["observations"].append(await one(browser,roots[side],scene,side,proc,args.output/"screenshots"))
                    finally:await browser.close()
    errors=[]
    for r in receipt["observations"]:
        if r["probe_grade"]!="PASS_BOUNDED_API_CALL_CAPTURE_NOT_GPU_PRESENT" or r["clock_grade"]!="PASS_TEST_ONLY_CLOCK_DRIVER":
            errors.append(r["scene"]+":"+r["side"]+":grade")
        if r["page_errors"] or r["blocked_external_urls"]:
            errors.append(r["scene"]+":"+r["side"]+":JS_external")
        if r["source_applied_grade"] not in ("PASS_ORIGINAL_UNINSTRUMENTED_TEST_CLOCK","PASS_FIXED_APPLICATION_ORDINAL_ONLY"):
            errors.append(r["scene"]+":"+r["side"]+":app")
    receipt["execution"]="PASS_FINITE_API_INTERCEPTION_ONLY" if not errors else "FAIL_OR_INCONCLUSIVE"
    receipt["errors"]=errors
    receipt["side_summary"]=[]
    for scene in K.D.SCENES:
        for side in ("original","minimal","observing"):
            subset=[r for r in receipt["observations"] if r["scene"]==scene and r["side"]==side]
            receipt["side_summary"].append({"scene":scene,"side":side,
                "processes":len(subset),
                "draw_api_calls":[len(x["probe"]["draw_calls"]) for x in subset],
                "canvas_context_requests":[len(x["probe"]["context_requests"]) for x in subset],
                "screenshot_sha_equal":len({x["screenshot_sha256"] for x in subset})==1,
                "gpu_present":"NOT_ADMITTED"})
    (args.output/"OMEGA11I_RENDER_API_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"processes":len(receipt["observations"]),
        "summary":receipt["side_summary"],"grade":receipt["execution"],
        "gpu_present":"NOT_ADMITTED","release":"HOLD"}))
    return 0 if not errors else 2

def main():
    p=argparse.ArgumentParser()
    for k in ("original","minimal","observing","manifest","output"):
        p.add_argument("--"+k,type=Path,required=True)
    raise SystemExit(asyncio.run(run(p.parse_args())))

if __name__=="__main__":main()
