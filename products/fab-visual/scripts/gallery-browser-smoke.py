#!/usr/bin/env python3
"""Ω11L — actual offline Gallery category/filter -> Studio/edit/download browser path."""
from __future__ import annotations
import argparse, asyncio, hashlib, json
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
async def run(root,out):
    from playwright.async_api import async_playwright
    root=root.resolve(strict=True)
    out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((root/"gallery.manifest.json").read_text())
    assert manifest["schema"]=="fab.visual.gallery-manifest.v1"
    assert manifest["release"]=="HOLD" and len(manifest["templates"])==3
    receipt={"schema":"fab.visual.omega11l.gallery-browser.v1",
       "source_index_sha256":sha(root/"index.html"),
       "source_manifest_sha256":sha(root/"gallery.manifest.json"),
       "scope":"OFFLINE_FIRST_PARTY_SYNTHETIC_TEMPLATES_ONLY",
       "source_templates":[],
       "real_measurements":"NOT_PRESENT","scientific_validation":"NOT_RUN",
       "source_code_execution_authority":"NONE","release":"HOLD",
       "browser_error":[],"external_requests_blocked":[]}
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--disable-background-networking","--disable-dev-shm-usage"])
        receipt["browser"]=browser.version
        context=await browser.new_context(viewport={"width":1460,"height":990},
            device_scale_factor=1,accept_downloads=True,locale="en-US",reduced_motion="reduce",
            color_scheme="light")
        page=await context.new_page()
        page.on("pageerror",lambda exc:receipt["browser_error"].append(str(exc)[:300]))
        async def only_local(route):
            u=route.request.url
            if u.startswith(("file://","data:","blob:")):await route.continue_()
            else:
                receipt["external_requests_blocked"].append(u[:180])
                await route.abort()
        await page.route("**/*",only_local)
        try:
            await page.goto((root/"index.html").as_uri(),wait_until="load",timeout=45000)
            assert await page.locator("[data-gallery-card]").count()==3
            assert "3 of 3 local templates" in await page.locator("#gallery-count").inner_text()
            assert await page.locator("a[data-open-studio]").count()==3
            assert await page.locator(".template-card .thumb svg").count()==3
            await page.screenshot(path=str(out/"gallery-overview.png"),full_page=True,animations="disabled")
            receipt["gallery_overview_sha256"]=sha(out/"gallery-overview.png")
            await page.locator("#template-search").fill("solar")
            assert await page.locator("[data-gallery-card]:visible").count()==1
            assert "1 of 3" in await page.locator("#gallery-count").inner_text()
            await page.locator("#template-search").fill("does-not-exist")
            assert await page.locator("[data-gallery-card]:visible").count()==0
            assert await page.locator("#gallery-empty").is_visible()
            await page.locator("#template-search").fill("")
            await page.locator("#template-category").select_option("Research apparatus")
            assert await page.locator("[data-gallery-card]:visible").count()==1
            assert await page.locator("[data-gallery-card]:visible").get_attribute("data-category")=="Research apparatus"
            await page.locator("#template-category").select_option("all")
            assert await page.locator("[data-gallery-card]:visible").count()==3
            for x in manifest["templates"]:
                key=x["key"]
                pth=(root/x["studio_path"])
                assert sha(pth)==x["html_sha256"]
                assert sha(root/x["scene_path"])==x["scene_sha256"]
                assert sha(root/x["preview_path"])==x["svg_sha256"]
                if key=="agents":assert x["physical_or_scientific_validation"]=="NOT_RUN"
                # Actually follow the gallery's local navigation link.
                await page.locator(f'a[data-open-studio="{key}"]').click()
                await page.wait_for_load_state("load")
                assert page.url==pth.as_uri()
                assert await page.locator("#edit-part option").count()==x["nodes"]
                assert await page.locator("#stage g[data-part]").count()==x["nodes"]
                assert "Release HOLD" in await page.locator("header").inner_text()
                assert await page.locator("#edit-undo").is_disabled()
                first=await page.locator("#edit-part").input_value()
                before=float(await page.locator("#edit-x").input_value())
                await page.locator("#edit-x").fill(str(before+14))
                await page.locator("#edit-apply").click()
                assert float(await page.locator(f'#stage g[data-part="{first}"] rect').get_attribute("x"))==before+14
                assert await page.locator("button[data-view='isometric']").is_disabled()
                assert await page.locator("button[data-view='compare']").is_disabled()
                assert "VISUAL EDIT ONLY" in await page.locator("#edit-status").inner_text()
                async with page.expect_download() as pending:
                    await page.locator('button[data-export="scene"]').click()
                item=await pending.value
                target=out/(key+"-edited-scene.json")
                await item.save_as(target)
                loaded=json.loads(target.read_text())
                assert loaded["id"]==x["id"]
                assert loaded["claim"]["status"]=="EXPLANATORY"
                assert loaded["visualEdit"]["release"]=="HOLD"
                assert loaded["model"]["synthetic"] is True
                assert loaded["parts"][0]["x"]==before+14
                assert all(o["evidence"]=="NOT_RUN" for o in loaded["observables"])
                await page.locator("#edit-undo").click()
                assert float(await page.locator(f'#stage g[data-part="{first}"] rect').get_attribute("x"))==before
                await page.locator("#edit-redo").click()
                assert float(await page.locator(f'#stage g[data-part="{first}"] rect').get_attribute("x"))==before+14
                capture=out/(key+"-studio-edited.png")
                await page.screenshot(path=str(capture),animations="disabled")
                receipt["source_templates"].append({"key":key,"source_html_sha256":x["html_sha256"],
                  "scene_sha256":x["scene_sha256"],"edited_scene_sha256":sha(target),
                  "edited_screenshot_sha256":sha(capture),
                  "source_claim":"EXPLANATORY","edit_provenance":"DERIVED_VISUAL_ONLY",
                  "browser_actions":"NAVIGATE_EDIT_DOWNLOAD_UNDO_REDO",
                  "source_authority_unchanged":True,"release":"HOLD"})
                await page.goto((root/"index.html").as_uri(),wait_until="load")
            assert len(receipt["source_templates"])==3
            assert receipt["browser_error"]==[],receipt["browser_error"]
            assert receipt["external_requests_blocked"]==[],receipt["external_requests_blocked"]
            receipt["result"]="PASS_THREE_LOCAL_DOMAIN_STUDIOS_AND_GALLERY"
        finally:
            await context.close()
            await browser.close()
    (out/"OMEGA11L_GALLERY_BROWSER_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":receipt.get("result"),"templates":len(receipt["source_templates"]),
        "release":"HOLD","external_requests":len(receipt["external_requests_blocked"])}))
    return 0
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--gallery",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    raise SystemExit(asyncio.run(run(args.gallery,args.output)))
