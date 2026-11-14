#!/usr/bin/env python3
"""Ω11I immutable Anatomy source-call coverage and fail-closed frame proof gate.

Evidence is exactly the two independently source-pinned original files. The
scan is a bounded text/call-site audit, not comprehensive static JS semantics.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

PIN="1482e8469b0a9e0d8cc18ea2740a01423d29ae80"
SOURCES={
  "raptor":("examples/raptor-engine/live.js",
            "c3c6a53d1f57f8e3743fb78dc391c251e19f6660"),
  "turning":("examples/turning-dial/stress.mjs",
             "0dadd6e5584785e6678ec0a80f7a42be18b50c06"),
}
SCHEDULE={
  "requestAnimationFrame":"SYNTHETIC_CLOCK_REPLACED",
  "cancelAnimationFrame":"SYNTHETIC_CLOCK_REPLACED",
  "IntersectionObserver":"SYNTHETIC_VISIBILITY_REPLACED",
  "performance.now":"SYNTHETIC_PERF_CLOCK_REPLACED",
  "setTimeout":"UNCONTROLLED_NATIVE_TIMER",
  "clearTimeout":"UNCONTROLLED_NATIVE_TIMER_CANCEL",
  "Date.now":"UNCONTROLLED_NATIVE_OR_GENERATOR_DATE",
  "document.hidden":"UNASSESSED_VISIBILITY",
  "visibilityState":"UNASSESSED_VISIBILITY",
  "getContext":"RENDERER_CONTEXT_NOT_PRESENT_WITNESS",
  "drawArrays":"DRAW_SUBMISSION_NOT_PRESENT_WITNESS",
  "drawElements":"DRAW_SUBMISSION_NOT_PRESENT_WITNESS",
  "readPixels":"GPU_READBACK_API_NOT_PRESENT_WITNESS",
  "D.camera":"SOURCE_STATIC_GL_CAMERA_NOT_COMPOSITE_CAMERA",
  "controller.set":"CONTROLLER_APPLICATION_NOT_PRESENT_WITNESS"
}
PATTERNS={
  "requestAnimationFrame":r"\brequestAnimationFrame\s*\(",
  "cancelAnimationFrame":r"\bcancelAnimationFrame\s*\(",
  "IntersectionObserver":r"\bIntersectionObserver\s*\(",
  "performance.now":r"\bperformance\.now\s*\(",
  "setTimeout":r"\bsetTimeout\s*\(",
  "clearTimeout":r"\bclearTimeout\s*\(",
  "Date.now":r"\bDate\.now\s*\(",
  "document.hidden":r"\bdocument\.hidden\b",
  "visibilityState":r"\bvisibilityState\b",
  "getContext":r"\.getContext\s*\(",
  "drawArrays":r"\.drawArrays\s*\(",
  "drawElements":r"\.drawElements\s*\(",
  "readPixels":r"\.readPixels\s*\(",
  "D.camera":r"\bD\.camera\b",
  "controller.set":r"\bcontroller\.set\s*\("
}

def git_blob_hash(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def line_number(text,pos):
    return text.count("\n",0,pos)+1

def analyze_source(name,raw):
    if name not in SOURCES:
        raise ValueError("unknown exact Anatomy original file")
    relative,expected=SOURCES[name]
    if git_blob_hash(raw)!=expected:
        raise ValueError("upstream original source Git-blob identity mismatch")
    text=raw.decode("utf-8")
    occurrences={}
    for token,pat in PATTERNS.items():
        found=list(re.finditer(pat,text))
        occurrences[token]={
          "count":len(found),
          "coverage_class":SCHEDULE[token],
          "line_numbers":[line_number(text,m.start()) for m in found],
          "source_snippets":[text[max(0,m.start()-42):min(len(text),m.end()+56)].replace("\n"," ") for m in found[:8]],
        }
    if name=="raptor":
        if occurrences["requestAnimationFrame"]["count"]<2 or occurrences["IntersectionObserver"]["count"]<1 or occurrences["setTimeout"]["count"]<1 or occurrences["D.camera"]["count"]<1:
            raise ValueError("source call graph changed outside audited minimal model")
        if "G.layer(" not in text or "stage.style.transform" not in text:
            raise ValueError("renderer geometry/gl source anchor missing")
        context="GL_SHADER_LAYERS_PLUS_DOM_SVG_AND_STAGE_CSS"
    else:
        if occurrences["requestAnimationFrame"]["count"]<2 or occurrences["performance.now"]["count"]<2 or occurrences["controller.set"]["count"]!=1 or occurrences["IntersectionObserver"]["count"]<1 or occurrences["Date.now"]["count"]<1:
            raise ValueError("turning source call graph changed outside audited minimal model")
        if "const LIVE =" not in text or "T.build(" not in text:
            raise ValueError("HTML generator source anchor missing")
        context="GENERATED_LIVE_STRING_AND_RUNTIME_CONTROLLER"
    return {
      "scene":name,"original_path":relative,"original_git_blob":expected,
      "source_pin":PIN,"context":context,
      "bounded_static_callsite_audit":True,
      "source_apis":occurrences,
      "actual_gpu_compositor_present_event":"NOT_IDENTIFIED",
      "renderer_frame_state_binding":"NOT_ADMITTED",
      "real_part_mesh_transform_camera_depth":"NOT_RUN",
      "normal_browser_clock_semantics":"NOT_ATTESTED_BY_TEST_HARNESS",
      "claim":"SOURCE_BOUNDED_COVERAGE_ONLY"
    }

def frame_gate(witness):
    if not isinstance(witness,dict):
        return "FAIL_MISSING_WITNESS"
    if witness.get("original_source_pin")!=PIN:
        return "FAIL_SOURCE_PROVENANCE"
    if witness.get("scene") not in SOURCES:
        return "FAIL_SCENE"
    if witness.get("observation_grade") in ("SYNTHETIC_CLOCK","DOM_UPDATED","RAF_CB","CONTROLLER_SET","SCREENSHOT_SHA","GPU_DRAW_SUBMITTED"):
        return "NOT_ADMITTED_STATE_OR_CAPTURE_IS_NOT_PRESENT"
    if witness.get("observation_grade")=="GPU_PRESENTED":
        # No matching original source frame token / authoritative GPU barrier
        # exists in this finite audit. Even a schema-valid assertion must HOLD.
        return "NOT_ADMITTED_NO_SOURCE_ATTESTED_GPU_PRESENT_TOKEN"
    return "NOT_ADMITTED_NO_INDEPENDENT_PRESENT_PROOF"

def run(root,output):
    root=Path(root).resolve(strict=True)
    report={"schema":"fab.visual.omega11i.source-render-boundary.v1",
      "source_pin":PIN,"sources":{},
      "source_checkout_read_only":True,
      "static_callsite_audit_not_comprehensive":True,
      "actual_native_render_present":"NOT_ADMITTED",
      "unmodified_browser_equivalence":"NOT_ADMITTED",
      "physical_geometry":"NOT_RUN",
      "release":"HOLD"}
    for key,(path,expected) in SOURCES.items():
        candidate=(root/path)
        if candidate.is_symlink() or not candidate.is_file() or candidate.resolve()!=candidate.absolute():
            raise ValueError("untrusted or redirected upstream source path")
        report["sources"][key]=analyze_source(key,candidate.read_bytes())
    report["uncovered_timer_count"]=sum(x["source_apis"]["setTimeout"]["count"] for x in report["sources"].values())
    report["generator_date_count"]=sum(x["source_apis"]["Date.now"]["count"] for x in report["sources"].values())
    report["pass"]="PASS_SOURCE_CALLSITE_INVENTORY_ONLY"
    output=Path(output)
    if output.exists():raise ValueError("never overwrite audited result")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=run(a.original,a.output)
    print(json.dumps({"source_pin":PIN,"callsite_result":result["pass"],
          "uncovered_native_timers":result["uncovered_timer_count"],
          "generator_date_calls":result["generator_date_count"],
          "frame_present":result["actual_native_render_present"],"release":"HOLD"}))

if __name__=="__main__":main()
