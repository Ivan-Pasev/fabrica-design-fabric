#!/usr/bin/env python3
"""Ω11J: offline user-facing FAB.VISUAL Studio browser workflow, NOT GPU attestation."""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

async def run(path,out):
    from playwright.async_api import async_playwright
    path=path.resolve(strict=True)
    out.mkdir(parents=True,exist_ok=True)
    log={"schema":"fab.visual.omega11j.offline-studio-smoke.v1",
         "source_html_sha256":sha(path),"scope":"USER_FUNCTIONALITY_TEST_ONLY",
         "canvas_gpu_present":"NOT_ADMITTED","scientific_certification":"NOT_RUN",
         "release":"HOLD","downloads":{},"screenshots":{}}
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--disable-background-networking","--disable-dev-shm-usage"])
        log["chromium_version"]=browser.version
        context=await browser.new_context(viewport={"width":1400,"height":980},
                        device_scale_factor=1,accept_downloads=True,
                        color_scheme="light",reduced_motion="reduce")
        page=await context.new_page()
        errs=[];blocked=[]
        page.on("pageerror",lambda exc:errs.append(str(exc)[:300]))
        async def deny_remote(route):
            url=route.request.url
            if url.startswith(("file://","data:","blob:")):await route.continue_()
            else:
                blocked.append(url[:200]);await route.abort()
        await page.route("**/*",deny_remote)
        try:
            await page.goto(path.as_uri(),wait_until="load",timeout=50000)
            assert await page.locator("#part-list button").count()==4
            assert await page.locator("#stage g[data-part]").count()==4
            assert await page.locator("button[data-view='2d']").get_attribute("aria-pressed")=="true"
            assert await page.locator("button[data-view='isometric']").is_enabled()
            assert "release hold" in (await page.locator("#scene-state").inner_text()).lower()
            shot=out/"studio-reference-2d.png"
            await page.screenshot(path=str(shot),animations="disabled")
            log["screenshots"]["reference_2d_sha256"]=sha(shot)
            await page.locator("#component-search").fill("release")
            assert await page.locator("#part-list li:visible").count()==1
            assert "1 of 4" in await page.locator("#search-count").inner_text()
            await page.locator("#part-list li:visible button").click()
            assert "status=BLOCKED" in await page.locator("#part-info").inner_text()
            await page.locator("#component-search").fill("")
            await page.locator("button[data-view='isometric']").click()
            assert await page.locator("button[data-view='isometric']").get_attribute("aria-pressed")=="true"
            assert await page.locator("#stage g[data-part]").count()==4
            assert "Pinned Anatomy" in await page.locator("#scene-state").inner_text() or "Anatomy" in await page.locator("#scene-state").inner_text()
            shot=out/"studio-pinned-anatomy.png"
            await page.screenshot(path=str(shot),animations="disabled")
            log["screenshots"]["pinned_anatomy_sha256"]=sha(shot)
            await page.locator("button[data-view='compare']").click()
            assert await page.locator("#stage .compare-grid figure").count()==2
            assert await page.locator("#stage g[data-part]").count()==8
            shot=out/"studio-comparison.png"
            await page.screenshot(path=str(shot),animations="disabled")
            log["screenshots"]["compare_sha256"]=sha(shot)
            for kind,ext in (("scene","json"),("reactflow","json"),("cytoscape","json"),
                             ("mermaid","mmd"),("dot","dot"),("svg","svg")):
                async with page.expect_download() as pending:
                    await page.locator("button[data-export='"+kind+"']").click()
                download=await pending.value
                assert download.suggested_filename.endswith("."+ext)
                dest=out/("download-"+kind+"."+ext)
                await download.save_as(dest)
                txt=dest.read_text(encoding="utf-8")
                assert len(txt)>10
                if kind in ("scene","reactflow","cytoscape"):
                    d=json.loads(txt)
                    assert d.get("release","HOLD")=="HOLD"
                    assert d.get("scene_id",d.get("id")) in ("codexstation-policy-machine",None)
                    if kind=="reactflow":assert len(d["nodes"])==4 and len(d["edges"])==3
                    if kind=="cytoscape":assert len(d["elements"]["nodes"])==4
                elif kind=="mermaid":assert txt.startswith("flowchart LR\n")
                elif kind=="dot":assert txt.startswith("digraph FabVisual {")
                elif kind=="svg":assert txt.lstrip().startswith("<svg")
                log["downloads"][kind]={"sha256":sha(dest),"bytes":dest.stat().st_size}
            assert "HOLD" in await page.locator("footer").inner_text()
            assert errs==[],errs
            assert blocked==[],blocked
            log["case_count"]=15
            log["result"]="PASS_OFFLINE_STUDIO_END_TO_END"
            log["errors"]=[]
            log["blocked_external_requests"]=[]
        finally:
            await context.close();await browser.close()
    (out/"OMEGA11J_STUDIO_BROWSER_RECEIPT.json").write_text(json.dumps(log,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":log.get("result"),"downloads":list(log["downloads"]),
                      "screenshots":list(log["screenshots"]),"release":"HOLD"}))
    return 0

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--html",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(asyncio.run(run(args.html,args.output)))

if __name__=="__main__":main()
