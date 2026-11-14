#!/usr/bin/env python3
"""Ω11F bounded, two-process original-vs-derived Chromium provenance witness.

It validates a test-only renderer-update *readout*. It does NOT attest actual
presented frames, static source camera as dynamic pose, or model mesh depth.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

THIS=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("omega11f_derivative",THIS/"omega11f-derivative.py")
D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
PROCESSES=2
SCENES=("raptor-light","turning-light")


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assess(scene, observation):
    """Do not convert tick/controller-set readout into frame attestation."""
    if scene not in SCENES: raise ValueError("unexpected scene")
    if not isinstance(observation,dict):
        return "INCONCLUSIVE_MISSING_READOUT"
    if observation.get("schema")!="fab.visual.omega11f.derivative.v1" or observation.get("scene")!=scene:
        return "FAIL_WRONG_HOOK"
    if observation.get("source_commit")!=D.PIN or observation.get("intervention")!="ADDITIVE_TEST_HOOK":
        return "FAIL_SOURCE_IDENTITY"
    if observation.get("runtime_frame_attested") is not False:
        return "FAIL_UNSUPPORTED_FRAME_ADMISSION"
    if observation.get("depth_order_attested") is not False:
        return "FAIL_UNSUPPORTED_DEPTH_ADMISSION"
    if observation.get("camera_grade")!=("SOURCE_STATIC" if scene=="raptor-light" else "NOT_AVAILABLE"):
        return "FAIL_CAMERA_GRADE"
    events=observation.get("events")
    if not isinstance(events,list) or len(events)<2:
        return "INCONCLUSIVE_TOO_FEW_UPDATES"
    last=None
    for event in events:
        if type(event.get("seq"))!=int or (last is not None and event["seq"]<=last):
            return "FAIL_NONMONOTONIC_TICK"
        last=event["seq"]
        if event.get("renderer_present_barrier")!="NOT_AVAILABLE":
            return "FAIL_UNSUPPORTED_PRESENT_BARRIER"
        if scene=="raptor-light":
            if event.get("frame_provenance")!="AFTER_TICK_DOM_UPDATE_BEFORE_NEXT_RAF":
                return "FAIL_WRONG_RAPTOR_HOOK"
            if not isinstance(event.get("springs"),dict) or not isinstance(event.get("gl_camera_static"),dict):
                return "FAIL_MISSING_RAPTOR_STATE"
            if type(event.get("app_clock")) not in (float,int):
                return "FAIL_MISSING_RAPTOR_CLOCK"
        else:
            if event.get("frame_provenance")!="AFTER_CONTROLLER_SET_BEFORE_NEXT_RAF":
                return "FAIL_WRONG_TURNING_HOOK"
            state=event.get("applied_controller_state")
            if not isinstance(state,dict) or any(k not in state for k in ("table","lift","time")):
                return "FAIL_MISSING_CONTROLLER_STATE"
    return "PASS_INSTRUMENTED_STATE_READOUT_ONLY"


async def inspect_source(browser,root,scene,side,process,out):
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    relative=D.SCENES[scene]["relative"]
    _,data=D.checked_file(root,relative,
       D.SCENES[scene]["sha"] if side=="original" else None)
    context=await browser.new_context(
      viewport={"width":1280 if scene=="raptor-light" else 390,"height":850},
      device_scale_factor=1, locale="en-US",timezone_id="UTC",
      reduced_motion="no-preference",color_scheme="light")
    page=await context.new_page()
    failures=[];blocked=[]
    page.on("pageerror",lambda e:failures.append(str(e)[:300]))
    async def guard(route):
        url=route.request.url
        if url.startswith(("file://","data:")):
            await route.continue_()
        else:
            blocked.append(url.split("?")[0][:200])
            await route.abort()
    await page.route("**/*",guard)
    try:
        await page.goto((root/relative).resolve().as_uri(),wait_until="load",timeout=60000)
        selector=D.SCENES[scene]["stage"]
        stage=page.locator(selector)
        if await stage.count()!=1:
            raise ValueError("real source-defined stage not unique")
        await stage.scroll_into_view_if_needed()
        await page.evaluate("async()=>{if(document.fonts)await document.fonts.ready}")
        if side=="derivative":
            try:
                await page.wait_for_function("()=>!!window.__fab11fDerivative && window.__fab11fDerivative.events.length>=2",timeout=20000)
            except PlaywrightTimeoutError:
                failures.append("instrumented derivative has fewer than two applied updates")
        else:
            await page.wait_for_timeout(350)
        witness=await page.evaluate("()=>window.__fab11fDerivative || null")
        stageinfo=await page.evaluate("""(selector)=>{
          const stage=document.querySelector(selector);
          const r=stage.getBoundingClientRect();
          return {selector,count:document.querySelectorAll(selector).length,
                  rect:[r.x,r.y,r.width,r.height],
                  aria_role:stage.getAttribute('role'),
                  aria_value_now:stage.getAttribute('aria-valuenow'),
                  reduced_motion:matchMedia('(prefers-reduced-motion:reduce)').matches,
                  svg_count:stage.querySelectorAll('svg').length,
                  canvas_count:stage.querySelectorAll('canvas').length};
        }""",selector)
        out.mkdir(parents=True,exist_ok=True)
        screenshot=out/f"{scene}-{side}-process{process}.png"
        await page.screenshot(path=str(screenshot),animations="disabled",
                              full_page=False,caret="hide")
        return {"scene":scene,"side":side,"process":process,
                "html_sha256":D.sha(data),"stage":stageinfo,
                "witness":witness if side=="derivative" else None,
                "original_page_had_derivative":witness is not None if side=="original" else None,
                "observation_classification":(
                   assess(scene,witness) if side=="derivative" else
                   "PASS_ORIGINAL_OBSERVER_ONLY" if witness is None else "FAIL_ORIGINAL_CONTAMINATION"),
                "errors":failures,"blocked_external":sorted(set(blocked)),
                "screenshot_sha256":sha(screenshot)}
    finally:
        await context.close()


async def run(args):
    from playwright.async_api import async_playwright
    original=args.original.resolve(strict=True)
    derivative=args.derivative.resolve(strict=True)
    manifest=json.loads(args.manifest.read_text())
    if manifest.get("source_pin")!=D.PIN or manifest.get("runtime_renderer_attestation")!="NOT_ADMITTED":
        raise ValueError("untrusted derivative manifest")
    for scene in SCENES:
        if scene not in manifest["patches"]:
            raise ValueError("missing derived patch provenance")
        item=manifest["patches"][scene]
        if D.checked_file(original,D.SCENES[scene]["relative"],item["original_html_sha256"])[1] == b"":
            raise ValueError("empty source")
        if D.checked_file(derivative,D.SCENES[scene]["relative"],item["derivative_html_sha256"])[1] == b"":
            raise ValueError("empty derivative")
    args.output.mkdir(parents=True,exist_ok=True)
    report={"schema":"fab.visual.omega11f.chromium.v1","source_pin":D.PIN,
            "derivative_manifest_sha256":sha(args.manifest),
            "patches":manifest["patches"],"original_source_modified":False,
            "processes_per_side":PROCESSES,"observations":[],
            "runtime_readout_gate":"NOT_RUN",
            "actual_renderer_frame_attestation":"NOT_ADMITTED",
            "actual_camera_projection_attestation":"NOT_ADMITTED",
            "actual_model_depth_order":"NOT_RUN",
            "historical_html_byte_parity":"FAIL",
            "historical_pixel_reproducibility":"FAIL",
            "release":"HOLD"}
    async with async_playwright() as playwright:
        for scene in SCENES:
            for side,root in (("original",original),("derivative",derivative)):
                for i in range(PROCESSES):
                    browser=await playwright.chromium.launch(headless=True,
                      args=["--disable-background-networking","--disable-dev-shm-usage"])
                    try:
                        report["browser_version"]=browser.version
                        report["observations"].append(
                          await inspect_source(browser,root,scene,side,i,args.output/"captures"))
                    finally:
                        await browser.close()
    failures=[]
    for x in report["observations"]:
        if x["errors"] or x["blocked_external"]:
            failures.append(x["scene"]+"/"+x["side"]+":runtime-or-network")
        if x["observation_classification"] not in (
            "PASS_INSTRUMENTED_STATE_READOUT_ONLY","PASS_ORIGINAL_OBSERVER_ONLY"):
            failures.append(x["scene"]+"/"+x["side"]+":missing-or-invalid-readout")
    if len(report["observations"])!=len(SCENES)*2*PROCESSES:
        failures.append("incomplete process coverage")
    report["runtime_readout_gate"]=("PASS_INSTRUMENTED_DERIVATIVE_ONLY"
                                 if not failures else "FAIL_OR_INCONCLUSIVE")
    report["failures"]=failures
    report["scope"]=("Disposable original-vs-test-derivative browser update observations; "
                     "not an independently attested presented renderer frame.")
    (args.output/"OMEGA11F_RUNTIME_RECEIPT.json").write_text(
      json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"observations":len(report["observations"]),
          "runtime_readout":report["runtime_readout_gate"],
          "real_frame":report["actual_renderer_frame_attestation"],
          "release":"HOLD"}))
    return 0 if not failures else 2


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original",required=True,type=Path)
    parser.add_argument("--derivative",required=True,type=Path)
    parser.add_argument("--manifest",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    return asyncio.run(run(parser.parse_args()))


if __name__=="__main__":
    sys.exit(main())
