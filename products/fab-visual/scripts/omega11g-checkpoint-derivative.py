#!/usr/bin/env python3
"""Ω11G source-pinned DISPOSABLE checkpoint variants, never original-source edits.

Original Anatomy stays pristine. Two derivatives use identical stop-on-N
application-hook scheduling; MINIMAL does not collect a detailed state snapshot
and OBSERVING does. No version proves identical elapsed time or presented frame.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("omega11f_derivative",HERE/"omega11f-derivative.py")
D=importlib.util.module_from_spec(sp);sp.loader.exec_module(D)
PIN=D.PIN
MODES=("MINIMAL_CHECKPOINT","OBSERVING_CHECKPOINT")
TARGET=3
BOOT_ANCHOR="function tick(now) {"

def sha(v:bytes):
    return hashlib.sha256(v).hexdigest()

RAPTOR_BODY="""{
   app_clock:clock, tour_clock:tourClock, selected_part:selected, apart,
   burn:{on:burn.on, phase:burn.phase, t:burn.t, armed:burn.armed},
   springs:Object.fromEntries(IDS.map(id=>[id,{x:piece[id].x,target:piece[id].target}])),
   gl_camera_static:D.camera,
   aria_value_now:stage.getAttribute('aria-valuenow')
 }"""
TURNING_BODY="""{
   applied_controller_state:{table:angle,lift:1,time},
   touring,visible,throttle_slow:slow,skip,reduced_motion:still.matches,
   camera_state:'NOT_AVAILABLE'
 }"""


def anchor_one(text,needle,replacement):
    count=text.count(needle)
    if count!=1:raise ValueError(f"runtime anchor ambiguous or missing: {needle[:55]!r}: {count}")
    return text.replace(needle,replacement,1)


def patch(scene,raw,mode):
    if scene not in D.SCENES:raise ValueError("unknown scene")
    if mode not in MODES:raise ValueError("unknown checkpoint mode")
    spec=D.SCENES[scene]
    if sha(raw)!=spec["sha"]:raise ValueError("immutable original source hash mismatch")
    text=raw.decode("utf8")
    if "__fab11gControl" in text or "__fab11fDerivative" in text:
        raise ValueError("original must have no prior test hooks")
    fields=RAPTOR_BODY if scene=="raptor-light" else TURNING_BODY
    grade=("AFTER_RAPTOR_TICK_DOM_UPDATE_BEFORE_PRESENT" if scene=="raptor-light"
           else "AFTER_TURNING_CONTROLLER_SET_BEFORE_PRESENT")
    boot="""/* Ω11G TEST-ONLY DISPOSABLE DERIVATIVE, NOT THE ORIGINAL */
window.__fab11gControl = {
  schema:'fab.visual.omega11g.control.v1', scene:'__SCENE__',
  mode:'__MODE__', target:3, serial:0, done:false, events:[],
  applied_state_grade:'__GRADE__',
  actual_renderer_frame:'NOT_ADMITTED', actual_mesh_depth:'NOT_RUN'
};
function __fab11gApplied(now) {
  const c=window.__fab11gControl;
  if(c.done) return;
  const t0=performance.now();
  c.serial++;
  if(c.mode==='OBSERVING_CHECKPOINT') c.events.push({
    serial:c.serial, applied_timestamp_ms:now,
    applied_state:__FIELDS__,
    renderer_present_barrier:'NOT_AVAILABLE'
  });
  c.readout_cost_ms=(performance.now()-t0);
  if(c.serial>=c.target) c.done=true;
}
""".replace("__SCENE__",scene).replace("__MODE__",mode).replace("__GRADE__",grade).replace("__FIELDS__",fields)
    text=anchor_one(text,BOOT_ANCHOR,boot+BOOT_ANCHOR)
    text=anchor_one(text,spec["original_hook"],
                    spec["original_hook"].replace("\n  frame =", "\n  __fab11gApplied(now);\n  frame =")
                    if scene=="raptor-light"
                    else spec["original_hook"].replace("\n    slow =","\n    __fab11gApplied(now);\n    slow ="))
    if scene=="raptor-light":
        old="frame = visible && (moving || burning || touring) ? requestAnimationFrame(tick) : 0;"
        new="frame = !window.__fab11gControl.done && visible && (moving || burning || touring) ? requestAnimationFrame(tick) : 0;"
        text=anchor_one(text,old,new)
        text=anchor_one(text,"if (!frame && visible) {",
                        "if (!frame && visible && !window.__fab11gControl.done) {")
    else:
        old="frame = visible && touring ? requestAnimationFrame(tick) : 0;"
        new="frame = !window.__fab11gControl.done && visible && touring ? requestAnimationFrame(tick) : 0;"
        text=anchor_one(text,old,new)
        text=anchor_one(text,
             "if (visible && touring && !frame) frame = requestAnimationFrame(tick);",
             "if (visible && touring && !frame && !window.__fab11gControl.done) frame = requestAnimationFrame(tick);")
    if text.count("__fab11gApplied(now)")!=2:
        raise ValueError("missing function declaration or call")
    result=text.encode()
    return result,{
      "scene":scene,"mode":mode,
      "original_html_sha256":sha(raw),"derivative_html_sha256":sha(result),
      "source_commit":PIN,"injection_count":1,"checkpoint_target":TARGET,
      "original_file":spec["relative"],"boot_sha256":sha(boot.encode()),
      "renderer_presented_frame":"NOT_ADMITTED",
      "real_mesh_depth":"NOT_RUN","release":"HOLD"
    }


def create(original:Path,minimal:Path,observing:Path,receipt_path:Path):
    original=original.resolve(strict=True)
    minimal=minimal.resolve(strict=True)
    observing=observing.resolve(strict=True)
    if len({str(p) for p in (original,minimal,observing)})!=3:
        raise ValueError("original/minimal/observing roots not distinct")
    if any(a in b.parents for a in (original,minimal,observing)
           for b in (original,minimal,observing) if a!=b):
        raise ValueError("nested source and derivative roots forbidden")
    prepared=[]
    for scene,meta in D.SCENES.items():
        _,raw=D.checked_file(original,meta["relative"],meta["sha"])
        for mode,dest in (("MINIMAL_CHECKPOINT",minimal),
                          ("OBSERVING_CHECKPOINT",observing)):
            _,same=D.checked_file(dest,meta["relative"],meta["sha"])
            if raw!=same:raise ValueError("copied derivative no longer equals original")
            patched,manifest=patch(scene,raw,mode)
            prepared.append((scene,mode,dest/meta["relative"],patched,manifest))
    receipt={
       "schema":"fab.visual.omega11g.checkpoint-derivatives.v1",
       "source_commit":PIN,"original_untouched":True,
       "checkpoint_target":TARGET,"variants":{},
       "frame_attestation":"NOT_ADMITTED","real_depth":"NOT_RUN","release":"HOLD"
    }
    for scene,mode,p,raw,manifest in prepared:
        p.write_bytes(raw)
        receipt["variants"][scene+"|"+mode]=manifest
    for scene,meta in D.SCENES.items():
        D.checked_file(original,meta["relative"],meta["sha"])
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    receipt_path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    return receipt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original",type=Path,required=True)
    parser.add_argument("--minimal",type=Path,required=True)
    parser.add_argument("--observing",type=Path,required=True)
    parser.add_argument("--receipt",type=Path,required=True)
    args=parser.parse_args()
    result=create(args.original,args.minimal,args.observing,args.receipt)
    print(json.dumps({"variants":sorted(result["variants"]),
          "target":TARGET,"frame":result["frame_attestation"],"release":"HOLD"}))


if __name__=="__main__":main()
