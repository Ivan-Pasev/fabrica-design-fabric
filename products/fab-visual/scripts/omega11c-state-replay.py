#!/usr/bin/env python3
"""Ω11C2 — fresh Chromium-process state/replay witness, source-conserving.

Does NOT set or mutate Anatomy cameras. A DOM observation and source JSON
fingerprint cannot substitute for a source-backed frame/camera state proof.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import sys

PIN="1482e8469b0a9e0d8cc18ea2740a01423d29ae80"
TARGETS=(
 ("raptor-light","examples/raptor-engine/raptor-engine-light.html",
  "48f64b954b93567f1a5ca87fa823c34ae9e81842fa5b95512deba6b22b37a537",1280,"D"),
 ("turning-light","examples/turning-dial/turning-stress-light.html",
  "e175e82f1bba087bb6031e375fb5da386f4f779e89e91a7864f7fc298b8b14e3",390,"DATA"),
)
REPEATS=3
PROCESSES=2


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_fingerprint(root: Path,relative: str,symbol: str,expected=None) -> dict:
    root=root.resolve(strict=True)
    target=root/relative
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
        raise ValueError("missing, symlinked or escaping source path")
    raw=target.read_bytes()
    hexdigest=digest(raw)
    if expected and hexdigest!=expected:
        raise ValueError("original source hash rejected")
    data=raw.decode("utf8")
    marker="const "+symbol+" = "
    if data.count(marker)!=1:
        raise ValueError("source-backed model constant missing or ambiguous")
    model,end=json.JSONDecoder().raw_decode(data[data.index(marker)+len(marker):])
    if type(model) is not dict:
        raise ValueError("invalid embedded model type")
    canonical=json.dumps(model,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
    detail={"html_sha256":hexdigest,"embedded_model_sha256":digest(canonical),
            "model_constant":symbol,"model_keys":sorted(model.keys())[:30]}
    if symbol=="D":
        detail["camera"]={k:model.get("camera",{}).get(k)
                          for k in ("k","cam") if isinstance(model.get("camera"),dict)}
    else:
        detail["hand_packed_sha256"]=digest(
            str(model.get("framed",{}).get("hand","")).encode())
    return detail


def comparable_state(a,b):
    """Only declarative DOM/camera observation; may not be a unique frame ID."""
    return (a.get("observation")==b.get("observation")
            and a.get("live_camera")==b.get("live_camera")
            and a.get("pointer")==b.get("pointer"))


def replay_classification(sides: dict) -> str:
    if any(len(sides.get(s,[]))!=PROCESSES for s in ("pinned","rebuilt")):
        return "INCOMPLETE"
    for side in ("pinned","rebuilt"):
        runs=sides[side]
        if any(x.get("errors") or x.get("blocked") or len(x.get("frames",[]))!=REPEATS
               for x in runs):
            return "INCONCLUSIVE_RUNTIME"
        if not all(comparable_state(runs[0],x) for x in runs[1:]):
            return "FAIL_CROSS_PROCESS_STATE_OBSERVATION"
        if any(len(set(x["frames"]))!=1 for x in runs):
            return "FAIL_WITHIN_PROCESS_PIXELS"
        if runs[0]["frames"][0]!=runs[1]["frames"][0]:
            return "FAIL_CROSS_PROCESS_PIXELS"
    if sides["pinned"][0]["frames"][0]!=sides["rebuilt"][0]["frames"][0]:
        return "OBSERVED_BASELINE_CANDIDATE_PIXEL_DELTA"
    return "PASS_FINITE_REPLAY_ONLY"


async def capture(playwright,root,relative,output,stem,width,source):
    browser=await playwright.chromium.launch(headless=True,
        args=["--disable-background-networking","--disable-dev-shm-usage"])
    context=await browser.new_context(viewport={"width":width,"height":850},
        device_scale_factor=1,locale="en-US",timezone_id="UTC",
        reduced_motion="reduce",color_scheme="light")
    page=await context.new_page()
    errors=[];blocked=[]
    page.on("pageerror",lambda ex:errors.append(str(ex)[:250]))
    async def guard(route):
        url=route.request.url
        if url.startswith(("file://","data:")):
            await route.continue_()
        else:
            blocked.append(url.split("?")[0][:180])
            await route.abort()
    await page.route("**/*",guard)
    try:
        await page.goto((root/relative).resolve().as_uri(),wait_until="load",timeout=60000)
        await page.evaluate("async()=>{if(document.fonts)await document.fonts.ready}")
        await page.wait_for_timeout(450)
        pointer=await page.evaluate("""() => {
          const target=document.querySelector('.iso-plate svg')
                   ||document.querySelector('svg')||document.body;
          target.scrollIntoView({block:'center',inline:'nearest'});
          const r=target.getBoundingClientRect();
          return {x:Math.min(innerWidth-2,Math.max(2,r.left+r.width/2)),
                  y:Math.min(innerHeight-2,Math.max(2,r.top+r.height/2))};
        }""")
        await page.mouse.move(pointer["x"],pointer["y"])
        await page.wait_for_timeout(250)
        observation=await page.evaluate("""(p) => {
          const el=document.elementFromPoint(p.x,p.y);
          const plate=document.querySelector('.iso-plate')||document.body;
          const svg=document.querySelector('.iso-plate svg')||document.querySelector('svg');
          const r=svg?.getBoundingClientRect();
          return {
            hover_hit:el?{tag:el.tagName,cls:String(el.getAttribute('class')||'').slice(0,120)}:null,
            readout:(document.querySelector('[data-readout]')?.textContent||'').slice(0,240),
            live:(document.querySelector('[data-live]')?.textContent||'').slice(0,240),
            visible_svg:document.querySelectorAll('svg').length,
            svg_paths:document.querySelectorAll('svg path').length,
            svg_rect:r?[r.x,r.y,r.width,r.height].map(v=>Math.round(v*1000)/1000):null,
            viewbox:svg?.getAttribute('viewBox')||null,
            plate_class:String(plate.className),
            overflow:document.documentElement.scrollWidth>innerWidth+2,
            reduced_motion:matchMedia('(prefers-reduced-motion:reduce)').matches
          };
        }""",pointer)
        # A lexical camera object may exist; lacking it is a transparent NOT_AVAILABLE.
        live_camera=await page.evaluate("""() => {
          try {
            if(typeof D!=='undefined' && D && D.camera)
              return {source:'D.camera',camera:D.camera,
                      frame:'NOT_EXPOSED'};
            if(typeof DATA!=='undefined' && DATA && DATA.camera)
              return {source:'DATA.camera',camera:DATA.camera,
                      frame:'NOT_EXPOSED'};
          } catch(e){}
          return {source:'UNAVAILABLE',frame:'NOT_EXPOSED'};
        }""")
        output.mkdir(parents=True,exist_ok=True)
        frames=[]
        for i in range(REPEATS):
            dest=output/f"{stem}-frame-{i}.png"
            await page.screenshot(path=str(dest),animations="disabled",caret="hide",
                                  timeout=60000,full_page=False)
            frames.append(digest(dest.read_bytes()))
            await page.wait_for_timeout(320)
        return {"frames":frames,"observation":observation,"pointer":pointer,
                "live_camera":live_camera,"html_source":source,
                "errors":errors,"blocked":sorted(set(blocked)),
                "browser":browser.version}
    finally:
        await context.close()
        await browser.close()


async def run(args):
    from playwright.async_api import async_playwright
    base,rebuilt,out=map(Path,(args.baseline,args.rebuilt,args.output))
    preflight={}
    for label,relative,expected,width,symbol in TARGETS:
        preflight[label]={"pinned":source_fingerprint(base,relative,symbol,expected),
                          "rebuilt":source_fingerprint(rebuilt,relative,symbol),
                          "width":width}
    out.mkdir(parents=True,exist_ok=True)
    report={"schema":"fab.visual.omega11c.state-replay.v1",
      "source_pin":PIN,"preflight":preflight,"processes_per_side":PROCESSES,
      "capture_frames_per_process":REPEATS,"case_results":[],
      "release":"HOLD","true_camera_frame_state":"NOT_ADMITTED",
      "depth_order_oracle":"NOT_RUN","physical_geometry":"NOT_RUN",
      "cross_platform_cause":"NOT_RUN","upstream_mutated":False}
    async with async_playwright() as playwright:
        for label,relative,expected,width,symbol in TARGETS:
            evidence={"pinned":[],"rebuilt":[]}
            for side,root in (("pinned",base),("rebuilt",rebuilt)):
                for attempt in range(PROCESSES):
                    evidence[side].append(await capture(playwright,root,relative,
                        out/"frames",f"{label}-{side}-process{attempt}",width,
                        preflight[label][side]))
            classification=replay_classification(evidence)
            source_camera=all(r["live_camera"]["source"]!="UNAVAILABLE"
                for side in evidence for r in evidence[side])
            report["case_results"].append({"case":label,"width":width,
                "state":"hover_center","classification":classification,
                "camera_model_exposed":source_camera,
                "authoritative_camera_frame_readback":"NOT_AVAILABLE",
                "attempts":evidence})
    report["process_replay_execution"]=(
        "PASS" if len(report["case_results"])==len(TARGETS) else "INCOMPLETE")
    report["claim_boundary"]="Source-locked DOM/hover observations and fresh-process PNG replay. "
    report["claim_boundary"]+="No authoritative camera/frame event readback, "
    report["claim_boundary"]+="so cannot infer depth/occlusion, full visual or physical equivalence."
    (out/"OMEGA11C_REPLAY_RECEIPT.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"execution":report["process_replay_execution"],
      "cases":{r["case"]:r["classification"] for r in report["case_results"]},
      "state_verified":"NOT_ADMITTED","release":"HOLD"}))
    return 0 if report["process_replay_execution"]=="PASS" else 2


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--baseline",required=True,type=Path)
    parser.add_argument("--rebuilt",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    return asyncio.run(run(args))


if __name__=="__main__":
    sys.exit(main())
