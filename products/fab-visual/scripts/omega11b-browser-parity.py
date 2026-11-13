#!/usr/bin/env python3
"""Ω11B: source-locked, non-mutating Chromium observations of Anatomy HTML drift.

Reports observed pixel/DOM equivalence at finitely sampled browser conditions;
never infers universal 3D geometry, all camera states, or product release.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import sys

PIN = "1482e8469b0a9e0d8cc18ea2740a01423d29ae80"
PAGES = {
    "raptor-dark": ("examples/raptor-engine/raptor-engine.html",
                    "cb2b7df8f24bf86fe870aa25598e348626af263332c553b90bd574dd029a257b"),
    "raptor-light": ("examples/raptor-engine/raptor-engine-light.html",
                     "48f64b954b93567f1a5ca87fa823c34ae9e81842fa5b95512deba6b22b37a537"),
    "turning-light": ("examples/turning-dial/turning-stress-light.html",
                      "e175e82f1bba087bb6031e375fb5da386f4f779e89e91a7864f7fc298b8b14e3"),
}
WIDTHS = (390, 768, 1280)
STATES = ("initial", "hover_center")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_file(root, relative, expected=None):
    root = Path(root)
    for node in (root, *[root.joinpath(*Path(relative).parts[:i])
                           for i in range(1, len(Path(relative).parts) + 1)]):
        if node.is_symlink():
            raise ValueError(f"symlinked source path: {node}")
    target = root / relative
    if not target.is_file():
        raise ValueError(f"missing generated source: {target}")
    actual = sha(target)
    if expected and actual != expected:
        raise ValueError(f"pinned original hash mismatch: {relative}")
    return actual


def classify_pixels(baseline_same_state, candidate_same_state, baseline_stable,
                    candidate_stable, baseline_dom, candidate_dom, runtime_errors):
    """A finite-state observation classifier, NOT a generic renderer oracle."""
    if runtime_errors:
        return "INCONCLUSIVE_RUNTIME"
    if not baseline_stable or not candidate_stable:
        return "INCONCLUSIVE_DYNAMIC_STATE"
    if baseline_dom != candidate_dom:
        return "OBSERVED_DOM_DELTA"
    if baseline_same_state and candidate_same_state:
        return "OBSERVED_IDENTICAL_PIXELS"
    return "OBSERVED_PIXEL_DELTA"


def image_stats(a, b, output_path):
    from PIL import Image, ImageChops
    with Image.open(a) as i, Image.open(b) as j:
        left, right = i.convert("RGBA"), j.convert("RGBA")
        if left.size != right.size:
            return {"equal": False, "same_dimensions": False,
                    "sizes": [list(left.size), list(right.size)]}
        difference = ImageChops.difference(left, right)
        boxes = [channel.getbbox() for channel in difference.split()]
        boxes = [b for b in boxes if b]
        box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
               max(b[2] for b in boxes), max(b[3] for b in boxes)) if boxes else None
        if box is None:
            return {"equal": True, "same_dimensions": True, "changed_pixels": 0,
                    "changed_fraction": 0.0, "bbox": None}
        # Count differing RGBA tuples. Bounded by the viewport, no external numpy.
        count = sum(any(v for v in pixel) for pixel in difference.getdata())
        difference.save(output_path)
        return {"equal": False, "same_dimensions": True, "changed_pixels": count,
                "changed_fraction": count / (left.width * left.height),
                "bbox": list(box)}


async def inspect_page(browser, root, relative, width, state, out_prefix):
    """Fresh incognito context; no HTTP(S) resource admission."""
    from playwright.async_api import Error as PWError
    context = await browser.new_context(viewport={"width": width, "height": 850},
                                        device_scale_factor=1, locale="en-US",
                                        timezone_id="UTC", color_scheme="light",
                                        reduced_motion="reduce")
    page = await context.new_page()
    page_errors, blocked = [], []
    page.on("pageerror", lambda err: page_errors.append(str(err)[:500]))

    async def guard(route):
        url = route.request.url
        if url.startswith("file://") or url.startswith("data:"):
            await route.continue_()
        else:
            blocked.append(url.split("?")[0][:200])
            await route.abort()

    await page.route("**/*", guard)
    try:
        await page.goto((Path(root) / relative).resolve().as_uri(),
                        wait_until="load", timeout=60000)
        await page.evaluate("async () => { if(document.fonts) await document.fonts.ready; }")
        await page.wait_for_timeout(450)
        if state == "hover_center":
            bounds = await page.evaluate("""() => {
                const target=document.querySelector('.iso-plate svg')
                    || document.querySelector('svg') || document.body;
                if(!target) return null;
                target.scrollIntoView({block:'center',inline:'nearest'});
                const r=target.getBoundingClientRect();
                return {x:Math.min(innerWidth-2,Math.max(2,r.left+r.width/2)),
                        y:Math.min(innerHeight-2,Math.max(2,r.top+r.height/2))};
            }""")
            if bounds:
                await page.mouse.move(bounds["x"], bounds["y"])
                await page.wait_for_timeout(250)
        census = await page.evaluate("""() => ({
            svg:document.querySelectorAll('svg').length,
            svgPaths:document.querySelectorAll('svg path').length,
            canvas:document.querySelectorAll('canvas').length,
            renderedBody:!!document.body && document.body.getBoundingClientRect().height>1,
            noOverflow:document.documentElement.scrollWidth<=innerWidth+2,
            buttons:document.querySelectorAll('button').length,
            isoPlates:document.querySelectorAll('.iso-plate').length
        })""")
        out_prefix.parent.mkdir(parents=True, exist_ok=True)
        first = out_prefix.with_name(out_prefix.name + "-capture.png")
        repeat = out_prefix.with_name(out_prefix.name + "-repeat.png")
        await page.screenshot(path=str(first), animations="disabled", full_page=False,
                              timeout=60000, caret="hide")
        await page.wait_for_timeout(350)
        await page.screenshot(path=str(repeat), animations="disabled", full_page=False,
                              timeout=60000, caret="hide")
        return {"census": census, "page_errors": page_errors,
                "blocked_requests": sorted(set(blocked)),
                "capture": str(first), "repeat": str(repeat),
                "sha256": {"capture": sha(first), "repeat": sha(repeat)}}
    finally:
        await context.close()


async def run(args):
    from playwright.async_api import async_playwright
    base, rebuilt, output = Path(args.baseline), Path(args.rebuilt), Path(args.output)
    # Provenance preflight must finish before any original HTML is executed.
    hashes = {}
    for name, (relative, expected) in PAGES.items():
        hashes[name] = {"pinned": check_file(base, relative, expected),
                        "rebuilt": check_file(rebuilt, relative)}
    output.mkdir(parents=True, exist_ok=True)
    report = {"schema":"fab.visual.omega11b.browser.v1",
              "source_pin": PIN, "source_hashes": hashes,
              "config":{"widths": WIDTHS, "height": 850, "states": STATES,
                        "dpr":1, "locale":"en-US", "timezone":"UTC",
                        "reduced_motion":"reduce","external_requests":"BLOCKED",
                        "browser":"CHROMIUM_ONLY", "camera_orbit":"NOT_RUN"},
              "observations":[], "runtime_failures":[],
              "visible_equivalence":"NOT_ADMITTED",
              "discrete_occlusion_equivalence":"NOT_RUN",
              "true_3d_geometry":"NOT_RUN",
              "strict_generated_byte_parity":("PASS" if all(x["pinned"] == x["rebuilt"] for x in hashes.values()) else "FAIL"),
              "release":"HOLD"}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True,
                    args=["--disable-background-networking","--disable-dev-shm-usage"])
        report["browser_version"] = browser.version
        report["playwright_version"] = importlib.metadata.version("playwright")
        try:
            for name, (relative, _) in PAGES.items():
                for width in WIDTHS:
                    for state in STATES:
                        tag = f"{name}-{width}-{state}"
                        original = candidate = None
                        try:
                            original = await inspect_page(browser, base, relative, width, state,
                                                          output / (tag + "-original"))
                            candidate = await inspect_page(browser, rebuilt, relative, width, state,
                                                           output / (tag + "-rebuilt"))
                            diff_path = output / (tag + "-DIFF.png")
                            pix = image_stats(original["capture"], candidate["capture"], diff_path)
                            control_a = image_stats(original["capture"], original["repeat"],
                                                    output / (tag + "-ORIGINAL-VARIATION.png"))
                            control_b = image_stats(candidate["capture"], candidate["repeat"],
                                                    output / (tag + "-REBUILT-VARIATION.png"))
                            err = original["page_errors"] + candidate["page_errors"] + \
                                  original["blocked_requests"] + candidate["blocked_requests"]
                            classification = classify_pixels(pix["equal"], pix["equal"],
                                control_a["equal"], control_b["equal"],
                                original["census"], candidate["census"], err)
                            report["observations"].append({"case":tag, "classification":classification,
                                "pixels":pix, "original_stable":control_a["equal"],
                                "rebuilt_stable":control_b["equal"],
                                "original_census":original["census"], "rebuilt_census":candidate["census"],
                                "original_page_errors":original["page_errors"],
                                "rebuilt_page_errors":candidate["page_errors"],
                                "original_blocked_requests":original["blocked_requests"],
                                "rebuilt_blocked_requests":candidate["blocked_requests"],
                                "captures":{"original":original["sha256"],"rebuilt":candidate["sha256"]}})
                        except Exception as exc:
                            report["runtime_failures"].append({"case":tag,"error":str(exc)[:1000]})
        finally:
            await browser.close()
    counts = {}
    for observation in report["observations"]:
        key = observation["classification"]
        counts[key] = counts.get(key, 0) + 1
    report["classification_counts"] = counts
    report["expected_cases"] = len(PAGES)*len(WIDTHS)*len(STATES)
    report["completed_cases"] = len(report["observations"])
    report["observation_coverage"] = (
        "EXECUTED" if not report["runtime_failures"] and
        report["completed_cases"] == report["expected_cases"] else "INCOMPLETE")
    report["claims"] = ("Finite Chromium viewport + initial/hover observations only. "
        "Pixel equality cannot establish 3D occlusion, all camera angles, "
        "dynamic behavior, physical geometry, WCAG or output byte parity.")
    (output / "OMEGA11B_BROWSER_RECEIPT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"coverage": report["observation_coverage"],
        "counts": counts, "strict_bytes": report["strict_generated_byte_parity"],
        "release": "HOLD", "browser": report["browser_version"]}))
    return 0 if report["observation_coverage"] == "EXECUTED" else 2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--rebuilt", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        return asyncio.run(run(args))
    except Exception as error:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output / "OMEGA11B_FAILURE.txt").write_text(str(error)+"\n",encoding="utf8")
        raise

if __name__ == "__main__":
    sys.exit(main())
