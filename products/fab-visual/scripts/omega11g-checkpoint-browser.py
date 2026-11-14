#!/usr/bin/env python3
"""Ω11G exact third-applied-update Chromium checkpoint, **not** GPU-present proof."""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("omega11g_checkpoint",HERE/"omega11g-checkpoint-derivative.py")
K=importlib.util.module_from_spec(sp);sp.loader.exec_module(K)
SCENES=("raptor-light","turning-light")
SIDES=("original","minimal","observing")
PROCESSES=2


def sha(b):
    return hashlib.sha256(b).hexdigest()


def verify_checkpoint(scene,mode,control):
    if not isinstance(control,dict):return "FAIL_MISSING_CHECKPOINT"
    if control.get("schema")!="fab.visual.omega11g.control.v1":
        return "FAIL_SCHEMA"
    if control.get("scene")!=scene:
        return "FAIL_SCENE"
    expected={"minimal":"MINIMAL_CHECKPOINT","observing":"OBSERVING_CHECKPOINT"}.get(mode)
    if control.get("mode")!=expected:return "FAIL_WRONG_MODE"
    if control.get("target")!=3 or type(control.get("serial"))!=int or control["serial"]!=3:
        return "FAIL_WRONG_APPLIED_ORDINAL"
    if control.get("done") is not True:return "FAIL_NOT_FROZEN_AT_ORDINAL"
    if control.get("actual_renderer_frame")!="NOT_ADMITTED" or control.get("actual_mesh_depth")!="NOT_RUN":
        return "FAIL_FORGED_FRAME_DEPTH_ADMISSION"
    events=control.get("events")
    if not isinstance(events,list):return "FAIL_EVENTS_SCHEMA"
    if mode=="minimal" and events:
        return "FAIL_MINIMAL_NOT_MINIMAL"
    if mode=="observing":
        if len(events)!=3 or [e.get("serial") for e in events]!=[1,2,3]:
            return "FAIL_EVENT_SEQUENCE"
        for event in events:
            if event.get("renderer_present_barrier")!="NOT_AVAILABLE":
                return "FAIL_FORGED_PRESENT_BARRIER"
            v=event.get("applied_state")
            if not isinstance(v,dict):return "FAIL_MISSING_APPLIED_STATE"
            if scene=="turning-light":
                if sorted(v.get("applied_controller_state",{}))!=["lift","table","time"]:
                    return "FAIL_CONTROLLER_STATE"
            elif scene=="raptor-light":
                if not isinstance(v.get("springs"),dict) or not isinstance(v.get("burn"),dict):
                    return "FAIL_RAPTOR_STATE"
    return "PASS_FIXED_APPLICATION_ORDINAL_ONLY"


async def observe(browser,root,scene,side,process,directory):
    from playwright.async_api import TimeoutError as BrowserTimeout
    meta=K.D.SCENES[scene]
    page_path=(root/meta["relative"]).resolve()
    ctx=await browser.new_context(viewport={"width":1280 if scene=="raptor-light" else 390,"height":850},
          locale="en-US",timezone_id="UTC",device_scale_factor=1,
          reduced_motion="no-preference",color_scheme="light")
    page=await ctx.new_page()
    errors=[]; blocked=[]
    page.on("pageerror",lambda err:errors.append(str(err)[:300]))
    async def route_guard(route):
        url=route.request.url
        if url.startswith(("file://","data:")):
            await route.continue_()
        else:
            blocked.append(url[:150])
            await route.abort()
    await page.route("**/*",route_guard)
    try:
        await page.goto(page_path.as_uri(),wait_until="load",timeout=50000)
        stage=page.locator(meta["stage"])
        if await stage.count()!=1:raise ValueError("wrong or duplicate actual stage")
        await stage.scroll_into_view_if_needed()
        if side!="original":
            try:
                await page.wait_for_function("()=>window.__fab11gControl?.done===true",timeout=20000)
            except BrowserTimeout:
                errors.append("exact update checkpoint not reached")
        else:
            await page.wait_for_timeout(250)
        control=await page.evaluate("()=>window.__fab11gControl || null")
        info=await page.evaluate("""selector=>{
         const s=document.querySelector(selector);const b=s.getBoundingClientRect();
         return {selector,rect:[b.x,b.y,b.width,b.height],
           svgs:s.querySelectorAll('svg').length,canvas:s.querySelectorAll('canvas').length,
           aria:s.getAttribute('aria-valuenow')};
        }""",meta["stage"])
        stage_html=await page.evaluate("selector=>document.querySelector(selector).outerHTML",meta["stage"])
        directory.mkdir(parents=True,exist_ok=True)
        image=directory/f"{scene}-{side}-process{process}.png"
        await page.screenshot(path=str(image),animations="disabled",caret="hide")
        classification=("PASS_ORIGINAL_UNINSTRUMENTED" if control is None
                        else "FAIL_ORIGINAL_INSTRUMENTED") if side=="original" else verify_checkpoint(scene,side,control)
        return {"scene":scene,"side":side,"process":process,
                "html_sha256":sha(page_path.read_bytes()),
                "checkpoint":control,
                "source_defined_stage":info,"stage_dom_sha256":sha(stage_html.encode()),
                "image_sha256":sha(image.read_bytes()),
                "classification":classification,"errors":errors,
                "blocked_external_requests":blocked}
    finally:
        await ctx.close()


async def execute(args):
    from playwright.async_api import async_playwright
    original=args.original.resolve(strict=True)
    paths={"original":original,"minimal":args.minimal.resolve(strict=True),
           "observing":args.observing.resolve(strict=True)}
    manifest=json.loads(args.manifest.read_text())
    if manifest.get("source_commit")!=K.PIN or manifest.get("checkpoint_target")!=3:
        raise ValueError("invalid source pin or checkpoint manifest")
    if manifest.get("frame_attestation")!="NOT_ADMITTED" or manifest.get("release")!="HOLD":
        raise ValueError("cannot promote frame or release from derivative")
    for scene,meta in K.D.SCENES.items():
        K.D.checked_file(original,meta["relative"],meta["sha"])
        for mode in ("minimal","observing"):
            key=scene+"|"+("MINIMAL_CHECKPOINT" if mode=="minimal" else "OBSERVING_CHECKPOINT")
            entry=manifest["variants"].get(key)
            if not entry:
                raise ValueError("missing derivative manifest")
            K.D.checked_file(paths[mode],meta["relative"],entry["derivative_html_sha256"])
    args.output.mkdir(parents=True,exist_ok=True)
    r={"schema":"fab.visual.omega11g.chromium-application-checkpoint.v1",
       "source_commit":K.PIN,"parent_derivative_manifest_sha256":sha(args.manifest.read_bytes()),
       "checkpoint_ordinal":3,"observer_modes":["ORIGINAL","MINIMAL_CHECKPOINT","OBSERVING_CHECKPOINT"],
       "processes_per_side":PROCESSES,"observations":[],
       "fixed_applied_update_gate":"NOT_RUN",
       "applied_state_equivalence":"INCONCLUSIVE_UNCONTROLLED_RAF_TIME",
       "observer_perturbation":"MEASURED_ONLY_NO_CAUSAL_EQUIVALENCE",
       "renderer_presented_frame":"NOT_ADMITTED",
       "real_camera_projection":"NOT_ADMITTED",
       "real_anatomy_geometry_depth":"NOT_RUN",
       "historical_byte_parity":"FAIL",
       "historical_visual_reproducibility":"FAIL",
       "release":"HOLD"}
    async with async_playwright() as playwright:
        for scene in SCENES:
            for side in SIDES:
                for process in range(PROCESSES):
                    browser=await playwright.chromium.launch(headless=True,
                        args=["--disable-background-networking","--disable-dev-shm-usage"])
                    try:
                        r["browser_version"]=browser.version
                        r["observations"].append(await observe(browser,paths[side],scene,side,process,
                                                               args.output/"screenshots"))
                    finally:await browser.close()
    errors=[]
    for row in r["observations"]:
        if row["errors"] or row["blocked_external_requests"]:
            errors.append(row["scene"]+":"+row["side"]+":JS_OR_RESOURCE")
        if row["classification"] not in ("PASS_FIXED_APPLICATION_ORDINAL_ONLY",
                                          "PASS_ORIGINAL_UNINSTRUMENTED"):
            errors.append(row["scene"]+":"+row["side"]+":"+row["classification"])
    if len(r["observations"])!=12:
        errors.append("MISSING_PROCESS_COVERAGE")
    r["fixed_applied_update_gate"]="PASS_DERIVATIVE_ORDINAL_ONLY" if not errors else "FAIL_OR_INCONCLUSIVE"
    r["issues"]=errors
    r["scope"]="Per-derivative source-applied update serial N=3, not equal RAF times or GPU present."
    (args.output/"OMEGA11G_CHECKPOINT_BROWSER.json").write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"cases":len(r["observations"]),"classification":r["fixed_applied_update_gate"],
       "rendered_frame":r["renderer_presented_frame"],"release":r["release"]}))
    return 0 if not errors else 2


def main():
    ap=argparse.ArgumentParser()
    for field in ("original","minimal","observing","manifest","output"):
        ap.add_argument("--"+field,type=Path,required=True)
    args=ap.parse_args()
    return asyncio.run(execute(args))


if __name__=="__main__":
    raise SystemExit(main())
