#!/usr/bin/env python3
"""Ω11F: additive, isolated TEST-ONLY Anatomy HTML derivative for runtime readback.

The immutable 173-file source checkout is NEVER written. These injectors assert
source-specific pinned HTML SHA hashes and unique runtime anchors. The resulting
HTML is not byte/source-parity evidence, and no runtime sample attests the full
renderer frame, camera projection, physical geometry or actual 3D occlusion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

PIN="1482e8469b0a9e0d8cc18ea2740a01423d29ae80"
SCENES={
 "raptor-light":{
  "relative":"examples/raptor-engine/raptor-engine-light.html",
  "sha":"48f64b954b93567f1a5ca87fa823c34ae9e81842fa5b95512deba6b22b37a537",
  "stage":".rp-stage",
  "model":"D",
  "original_hook":"  if (!burn.on) say(idleText());\n  frame = visible",
  "marker":"  if (!burn.on) say(idleText());\n  __fab11fCaptureRaptor(now);\n  frame = visible"
 },
 "turning-light":{
  "relative":"examples/turning-dial/turning-stress-light.html",
  "sha":"e175e82f1bba087bb6031e375fb5da386f4f779e89e91a7864f7fc298b8b14e3",
  "stage":".ts-stage",
  "model":"DATA",
  "original_hook":"    controller.set({ table: angle, lift: 1, time });\n    slow =",
  "marker":"    controller.set({ table: angle, lift: 1, time });\n    __fab11fCaptureTurning(now);\n    slow ="
 }
}
BOOT_ANCHOR="function tick(now) {"
RAPTOR_BOOT="""/* Ω11F ISOLATED TEST DERIVATIVE — NOT THE UNMODIFIED ORIGINAL */
window.__fab11fDerivative = {schema:'fab.visual.omega11f.derivative.v1',
  scene:'raptor-light', source_commit:'1482e8469b0a9e0d8cc18ea2740a01423d29ae80',
  intervention:'ADDITIVE_TEST_HOOK', camera_grade:'SOURCE_STATIC',
  runtime_frame_attested:false, depth_order_attested:false, events:[]};
let __fab11fSeq=0;
function __fab11fCaptureRaptor(now) {
  const w=window.__fab11fDerivative;
  w.events.push({
    seq:++__fab11fSeq, raf_now_ms:now,
    app_clock:clock, tour_clock:tourClock, touring, visible, reduced_motion:still.matches,
    selected_part:selected, apart, aria_value_now:stage.getAttribute('aria-valuenow'),
    burn:{on:burn.on,phase:burn.phase,t:burn.t,armed:burn.armed},
    springs:Object.fromEntries(IDS.map(id=>[id,{x:piece[id].x,target:piece[id].target}])),
    gl_camera_static:D.camera,
    frame_provenance:'AFTER_TICK_DOM_UPDATE_BEFORE_NEXT_RAF',
    renderer_present_barrier:'NOT_AVAILABLE'
  });
  if(w.events.length>64) w.events.shift();
}
"""
TURNING_BOOT="""/* Ω11F ISOLATED TEST DERIVATIVE — NOT THE UNMODIFIED ORIGINAL */
window.__fab11fDerivative = {schema:'fab.visual.omega11f.derivative.v1',
  scene:'turning-light', source_commit:'1482e8469b0a9e0d8cc18ea2740a01423d29ae80',
  intervention:'ADDITIVE_TEST_HOOK', camera_grade:'NOT_AVAILABLE',
  runtime_frame_attested:false, depth_order_attested:false, events:[]};
let __fab11fSeq=0;
function __fab11fCaptureTurning(now) {
  const w=window.__fab11fDerivative;
  w.events.push({
    seq:++__fab11fSeq, raf_now_ms:now,
    applied_controller_state:{table:angle,lift:1,time},
    touring,visible,throttle_slow:slow,skip,reduced_motion:still.matches,
    frame_provenance:'AFTER_CONTROLLER_SET_BEFORE_NEXT_RAF',
    renderer_present_barrier:'NOT_AVAILABLE'
  });
  if(w.events.length>64) w.events.shift();
}
"""


def sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()


def checked_file(root:Path,relative:str,expected:str|None=None)->tuple[Path,bytes]:
    root=root.resolve(strict=True)
    if not root.is_dir(): raise ValueError("root must be a directory")
    p=root/relative
    nodes=[root]
    for part in Path(relative).parts:
        nodes.append(nodes[-1]/part)
    if any(x.is_symlink() for x in nodes):
        raise ValueError("symlink in original/derivative path")
    if not p.is_file() or not p.resolve().is_relative_to(root):
        raise ValueError("missing, escaping or nonfile source")
    raw=p.read_bytes()
    if expected and sha(raw)!=expected:
        raise ValueError("stale immutable original HTML hash rejected")
    return p,raw


def inject(name:str,raw:bytes)->tuple[bytes,dict]:
    if name not in SCENES:raise ValueError("unknown exact source scene")
    item=SCENES[name]
    if sha(raw)!=item["sha"]:
        raise ValueError("source HTML SHA mismatch before any patch")
    s=raw.decode("utf8")
    if s.count(BOOT_ANCHOR)!=1 or s.count(item["original_hook"])!=1:
        raise ValueError("runtime anchor missing, duplicate or ambiguous")
    if "__fab11fDerivative" in s:
        raise ValueError("instrumentation already present in original")
    boot=RAPTOR_BOOT if name=="raptor-light" else TURNING_BOOT
    result=s.replace(BOOT_ANCHOR,boot+BOOT_ANCHOR,1)
    result=result.replace(item["original_hook"],item["marker"],1)
    if result.count("__fab11fDerivative")==0 or result==s:
        raise ValueError("failed to apply exact additive patch")
    patch={
      "scene":name,"relative":item["relative"],
      "original_html_sha256":sha(raw),"derivative_html_sha256":sha(result.encode()),
      "source_commit":PIN,"source_grade":"IMMUTABLE_ORIGINAL_PLUS_SEPARATE_DERIVATIVE",
      "hook_anchor_sha256":sha(item["original_hook"].encode()),
      "boot_snippet_sha256":sha(boot.encode()),
      "injection_points":["BEFORE_FUNCTION_TICK",
           "AFTER_RAPTOR_TICK_DOM_UPDATE" if name=="raptor-light"
           else "AFTER_TURNING_CONTROLLER_SET"],
      "original_blameless":True,"derivative_is_original":False,
      "modified_source_geometry":False,
      "runtime_frame_attestation":"NOT_ADMITTED",
      "real_renderer_depth":"NOT_RUN",
      "generated_byte_parity":"FAIL","release":"HOLD"
    }
    return result.encode(),patch


def apply(original:Path,derivative:Path,output:Path)->dict:
    original=original.resolve(strict=True)
    derivative=derivative.resolve(strict=True)
    if original==derivative or (original in derivative.parents) or (derivative in original.parents):
        raise ValueError("derivative and source checkouts must be separate")
    receipt={"schema":"fab.visual.omega11f.derivative-manifest.v1",
             "source_pin":PIN,"source_original_untouched":True,
             "patches":{},"runtime_renderer_attestation":"NOT_ADMITTED",
             "actual_3d_geometry":"NOT_RUN","release":"HOLD"}
    prepared=[]
    for scene,item in SCENES.items():
        p,source=checked_file(original,item["relative"],item["sha"])
        dest,copy=checked_file(derivative,item["relative"],item["sha"])
        data,patch=inject(scene,source)
        if copy!=source:raise ValueError("derivative copy must be identical before patch")
        prepared.append((scene,dest,data,patch))
    for scene,p,data,patch in prepared:
        p.write_bytes(data)
        receipt["patches"][scene]=patch
    for scene,item in SCENES.items():
        _,raw=checked_file(original,item["relative"],item["sha"])
        _,der=checked_file(derivative,item["relative"])
        if sha(raw)!=receipt["patches"][scene]["original_html_sha256"]:
            raise ValueError("pinned original modified during patch")
        if sha(der)!=receipt["patches"][scene]["derivative_html_sha256"]:
            raise ValueError("derived HTML changed unexpectedly")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original",required=True,type=Path)
    parser.add_argument("--derivative",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    result=apply(args.original,args.derivative,args.output)
    print(json.dumps({"patched":list(result["patches"]),
          "original_untouched":result["source_original_untouched"],
          "frame_attestation":result["runtime_renderer_attestation"],
          "release":"HOLD"}))


if __name__=="__main__":
    sys.exit(main())
