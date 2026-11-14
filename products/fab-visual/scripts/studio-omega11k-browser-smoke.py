#!/usr/bin/env python3
"""Ω11K: real offline browser tests for reversible Studio editing and graph imports."""
from __future__ import annotations
import argparse, asyncio, hashlib, json
from pathlib import Path

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

async def run(args):
    from playwright.async_api import async_playwright
    output=args.output
    output.mkdir(parents=True,exist_ok=True)
    record={"schema":"fab.visual.omega11k.product-editor-browser.v1",
      "scope":"OFFLINE_VISUAL_EDITING_NOT_AUTHORITATIVE_MODEL",
      "release":"HOLD","source_authority_change":"NONE",
      "gpu_present":"NOT_ADMITTED","real_scientific_validation":"NOT_RUN",
      "browser_actions":[],"downloads":{},"errors":[],"blocked":[]}
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--disable-background-networking","--disable-dev-shm-usage"])
        record["chromium_version"]=browser.version
        context=await browser.new_context(viewport={"width":1400,"height":1100},
            device_scale_factor=1,accept_downloads=True,color_scheme="light",reduced_motion="reduce")
        page=await context.new_page()
        async def await_status(fragment):
            # Strict page CSP forbids unsafe-eval: use protocol DOM text polling.
            for _ in range(100):
                if fragment in await page.locator("#edit-status").inner_text():
                    return
                await asyncio.sleep(0.08)
            raise AssertionError("Editor status not reached: "+fragment)

        page.on("pageerror",lambda e:record["errors"].append(str(e)[:500]))
        async def intercept(route):
            url=route.request.url
            if url.startswith(("file://","data:","blob:")):await route.continue_()
            else:
                record["blocked"].append(url[:250])
                await route.abort()
        await page.route("**/*",intercept)
        try:
            await page.goto(args.html.resolve(strict=True).as_uri(),wait_until="load",timeout=50000)
            assert await page.locator("#edit-part option").count()==4
            assert await page.locator("#edit-x").input_value()=="40"
            assert await page.locator("button[data-view='compare']").is_enabled()
            assert await page.locator("#edit-undo").is_disabled()
            record["browser_actions"].append("EDITOR_SOURCE_CONTROLS_INIT")

            # The original graph export can be re-imported unchanged with its
            # strict original SceneIR/model/claim/source digest and exact edges.
            await page.locator("#graph-import-format").select_option("reactflow")
            await page.locator("#graph-import-file").set_input_files(str(args.reactflow))
            await await_status("Imported unmodified")
            assert await page.locator("button[data-view='compare']").is_enabled()
            record["browser_actions"].append("SOURCE_ANCHORED_XYFLOW_EXACT_IMPORT")

            # Visual-only geometry mutation must disable stale Anatomy.
            await page.locator("#edit-x").fill("92")
            await page.locator("#edit-w").fill("190")
            await page.locator("#edit-apply").click()
            assert await page.locator("#stage [data-part='intake'] rect").get_attribute("x")=="92"
            assert await page.locator("#stage [data-part='intake'] rect").get_attribute("width")=="190"
            assert await page.locator("button[data-view='isometric']").is_disabled()
            assert await page.locator("button[data-view='compare']").is_disabled()
            assert "VISUAL EDIT ONLY" in await page.locator("#edit-status").inner_text()
            record["browser_actions"].append("MOVE_RESIZE_REJECT_STALE_ANATOMY")

            await page.locator("#edit-undo").click()
            assert await page.locator("#stage [data-part='intake'] rect").get_attribute("x")=="40"
            assert await page.locator("button[data-view='compare']").is_enabled()
            await page.locator("#edit-redo").click()
            assert await page.locator("#stage [data-part='intake'] rect").get_attribute("x")=="92"
            record["browser_actions"].append("REVERSIBLE_UNDO_REDO")

            await page.locator("#edit-from").select_option("intake")
            await page.locator("#edit-to").select_option("human")
            await page.locator("#edit-flow").select_option("control")
            await page.locator("#edit-add-link").click()
            assert await page.locator("#stage path[data-flow='control']").count()==4
            record["browser_actions"].append("CREATE_TYPED_ILLUSTRATIVE_LINK")

            async def save_download(kind,filename):
                async with page.expect_download() as dp:
                    await page.locator("button[data-export='"+kind+"']").click()
                d=await dp.value
                dest=output/filename
                await d.save_as(dest)
                record["downloads"][kind]={"filename":d.suggested_filename,"bytes":dest.stat().st_size,"sha256":digest(dest)}
                return json.loads(dest.read_text()) if filename.endswith(".json") else dest.read_text()
            edited=await save_download("scene","edited-scene.json")
            assert edited["visualEdit"]["release"]=="HOLD"
            assert edited["parts"][0]["x"]==92
            assert edited["parts"][0]["w"]==190
            assert len(edited["links"])==4
            assert edited["claim"]["status"]=="EXPLANATORY"
            assert edited["model"]["authority"]=="local demonstration only"
            flow=await save_download("reactflow","edited-reactflow.json")
            assert flow["nodes"][0]["position"]["x"]==92
            assert flow["nodes"][0]["style"]["width"]==190
            assert len(flow["edges"])==4
            assert flow["release"]=="HOLD"
            cyt=await save_download("cytoscape","edited-cytoscape.json")
            assert cyt["elements"]["nodes"][0]["position"]["x"]==187
            assert len(cyt["elements"]["edges"])==4
            record["browser_actions"].append("DERIVED_SCENE_AND_GRAPH_DOWNLOADS")

            # Forged authorization stays REJECTED; the edited state must
            # preserve its values after rejected file import.
            bad=json.loads(args.reactflow.read_text())
            bad["nodes"][0]["data"]["status"]="RELEASED"
            tampered=output/"forged-status.json"
            tampered.write_text(json.dumps(bad))
            await page.locator("#graph-import-format").select_option("reactflow")
            await page.locator("#graph-import-file").set_input_files(str(tampered))
            await await_status("IMPORT REJECTED")
            assert await page.locator("#stage [data-part='intake'] rect").get_attribute("x")=="92"
            record["browser_actions"].append("FORGED_AUTHORIZATION_IMPORT_BLOCKED")

            # Real graph geometry modifications can become a new reversible
            # source-anchored presentation (not a new source model).
            changed=json.loads(args.reactflow.read_text())
            changed["nodes"][0]["position"]["x"]=76
            modified=output/"modified-xyflow.json"
            modified.write_text(json.dumps(changed))
            await page.locator("#graph-import-file").set_input_files(str(modified))
            await await_status("Imported reactflow derivative")
            assert await page.locator("#stage [data-part='intake'] rect").get_attribute("x")=="76"
            record["browser_actions"].append("DIFFERENTIAL_XYFLOW_IMPORT")

            cy=json.loads(args.cytoscape.read_text())
            cy["elements"]["nodes"][0]["position"]["x"]+=15
            changedcy=output/"modified-cytoscape.json"
            changedcy.write_text(json.dumps(cy))
            await page.locator("#graph-import-format").select_option("cytoscape")
            await page.locator("#graph-import-file").set_input_files(str(changedcy))
            await await_status("Imported cytoscape derivative")
            assert await page.locator("#stage [data-part='intake'] rect").get_attribute("x")=="55"
            record["browser_actions"].append("DIFFERENTIAL_CYTOSCAPE_IMPORT")

            shot=output/"studio-edited-source-anchored.png"
            await page.screenshot(path=str(shot),animations="disabled")
            record["edited_screenshot_sha256"]=digest(shot)
            assert not record["errors"],record["errors"]
            assert not record["blocked"],record["blocked"]
            record["result"]="PASS_OFFLINE_ROUNDTRIP_EDITOR"
        finally:
            await context.close()
            await browser.close()
    (output/"OMEGA11K_EDITOR_BROWSER_RECEIPT.json").write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":record.get("result"),"actions":len(record["browser_actions"]),
                      "downloads":len(record["downloads"]),"release":"HOLD"}))
    return 0

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--html",required=True,type=Path)
    ap.add_argument("--reactflow",required=True,type=Path)
    ap.add_argument("--cytoscape",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    raise SystemExit(asyncio.run(run(ap.parse_args())))
