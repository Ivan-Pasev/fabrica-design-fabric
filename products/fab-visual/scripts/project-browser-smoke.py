#!/usr/bin/env python3
"""Ω11M browser: real local forks, source/derived diff, accessible typed SVG links and ZIP."""
from __future__ import annotations
import argparse,asyncio,hashlib,io,json,zipfile
from pathlib import Path

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

async def browser(root,out):
    from playwright.async_api import async_playwright
    root=root.resolve(strict=True);out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((root/"gallery.manifest.json").read_text())
    cases={
      "energy":("battery","inverter","energy"),
      "laboratory":("pressure","optical","signal"),
      "agents":("planner","verifier","information")
    }
    evidence={
      "schema":"fab.visual.omega11m.browser-acceptance.v1",
      "source_manifest_sha256":sha(root/"gallery.manifest.json"),
      "source_original_git_173_check":"SEPARATELY_IN_CI",
      "source_authority":"PRESERVED", "signed_publisher":"NOT_PRESENT",
      "all_domains_synthetic":True,"real_gpu_present":"NOT_ADMITTED",
      "host_authorization":"NOT_RUN","release":"HOLD",
      "cases":[],"errors":[],"blocked_external_requests":[]
    }
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,args=["--disable-background-networking","--disable-dev-shm-usage"])
        evidence["chromium_version"]=b.version
        context=await b.new_context(viewport={"width":1500,"height":1080},
          accept_downloads=True,device_scale_factor=1,color_scheme="light",reduced_motion="reduce")
        page=await context.new_page()
        page.on("pageerror",lambda exc:evidence["errors"].append(str(exc)[:350]))
        async def route(request):
            url=request.request.url
            if url.startswith(("file://","data:","blob:")):await request.continue_()
            else:
                evidence["blocked_external_requests"].append(url[:200])
                await request.abort()
        await page.route("**/*",route)
        try:
            for entry in catalog["templates"]:
                key=entry["key"]
                path=root/entry["studio_path"]
                assert sha(path)==entry["html_sha256"]
                await page.goto(path.as_uri(),wait_until="load",timeout=50000)
                source=json.loads((root/entry["scene_path"]).read_text())
                assert await page.locator("#edit-canvas-connect").is_enabled()
                assert await page.locator("#edit-diff-toggle").is_enabled()
                assert await page.locator("#edit-project").is_enabled()
                assert await page.locator("#edit-revision option").count()==1
                assert await page.locator("#edit-undo").is_disabled()
                assert await page.locator("#stage g[data-part]").count()==entry["nodes"]
                await page.locator("#edit-diff-toggle").click()
                assert await page.locator("#edit-diff").is_visible()
                assert await page.locator("#edit-diff svg").count()==2
                assert "0 moved" in await page.locator("#edit-diff").inner_text()
                x0=float(await page.locator("#edit-x").input_value())
                await page.locator("#edit-x").fill(str(x0+21))
                await page.locator("#edit-apply").click()
                assert await page.locator("#edit-revision option").count()==2
                assert "1 moved" in await page.locator("#edit-diff").inner_text()
                assert await page.locator("button[data-view='isometric']").is_disabled()
                await page.locator("#edit-revision").select_option("0")
                assert "0 moved" in await page.locator("#edit-diff").inner_text()
                await page.locator("#edit-revision").select_option("1")
                assert "1 moved" in await page.locator("#edit-diff").inner_text()

                a,t,kind=cases[key]
                assert a in [s["id"] for s in source["parts"]]
                assert t in [s["id"] for s in source["parts"]]
                await page.locator("#edit-canvas-connect").click()
                assert await page.locator("#edit-canvas-connect").get_attribute("aria-pressed")=="true"
                # keyboard-source selection, then pointer target selection
                src_node=page.locator(f'#stage g[data-part="{a}"]')
                await src_node.focus()
                await src_node.press("Enter")
                await page.locator(f'#stage g[data-part="{t}"]').click()
                assert await page.locator("#edit-canvas-connect").get_attribute("aria-pressed")=="false"
                assert "Created illustrative" in await page.locator("#edit-status").inner_text()
                assert await page.locator("#stage path[data-edge]").count()==entry["links"]+1
                latest=entry["links"]
                path_edge=page.locator(f'#stage path[data-edge="{latest}"]')
                await path_edge.focus()
                await path_edge.press("Space")
                assert await page.locator("#edit-link-select").input_value()==str(latest)
                assert kind in await page.locator("#edit-canvas-status").inner_text()
                await page.locator("#edit-remove-link").click()
                assert await page.locator("#stage path[data-edge]").count()==entry["links"]
                await page.locator("#edit-undo").click()
                assert await page.locator("#stage path[data-edge]").count()==entry["links"]+1
                await page.locator("#edit-redo").click()
                assert await page.locator("#stage path[data-edge]").count()==entry["links"]
                assert "1 moved" in await page.locator("#edit-diff").inner_text()

                await page.locator("#edit-fork-slug").fill("study-01")
                async with page.expect_download() as pending:
                    await page.locator("#edit-fork").click()
                item=await pending.value
                forkfile=out/(key+"-fork.scene.json");await item.save_as(forkfile)
                fork=json.loads(forkfile.read_text())
                assert fork["id"]==source["id"]+"--fork-study-01"
                assert fork["model"]["revision"]==source["model"]["revision"]+"+visual-fork.study-01"
                assert fork["fork"]["sourceModelRevision"]==source["model"]["revision"]
                assert fork["fork"]["scope"]=="DERIVED_VISUAL_SCENE_NOT_MODEL_AUTHORITY"
                assert fork["fork"]["publisherSignature"]=="NOT_PRESENT"
                assert fork["model"]["authority"]==source["model"]["authority"]
                assert fork["audit"]["scientific_admission"]=="NOT_RUN"
                assert fork["claim"]==source["claim"]

                async with page.expect_download() as pending:
                    await page.locator("#edit-project").click()
                download=await pending.value
                projectfile=out/(key+"-visual-project.zip");await download.save_as(projectfile)
                with zipfile.ZipFile(projectfile,"r") as archive:
                    assert archive.testzip() is None
                    assert sorted(archive.namelist())==sorted([
                      "manifest.json","source/original.scene.json","derived/fork.scene.json",
                      "evidence/visual-diff.json","evidence/edit-history.json","readme.txt"])
                    manifest=json.loads(archive.read("manifest.json"))
                    assert manifest["originalSceneId"]==source["id"]
                    assert manifest["forkSceneId"]==fork["id"]
                    assert manifest["release"]=="HOLD"
                    assert manifest["sourceAuthorityPreserved"] is True
                    assert manifest["archives"]=="ZIP_STORE_CRC32_NOT_CRYPTOGRAPHIC_AUTHENTICATION"
                    original=json.loads(archive.read("source/original.scene.json"))
                    assert original==source
                    inside_fork=json.loads(archive.read("derived/fork.scene.json"))
                    assert inside_fork==fork
                    changes=json.loads(archive.read("evidence/visual-diff.json"))
                    assert changes["sourceAuthorityPreserved"] is True
                    assert len(changes["move"])==1
                    assert changes["release"]=="HOLD"
                    history=json.loads(archive.read("evidence/edit-history.json"))
                    assert history["schema"]=="fab.visual.local-edit-history.v1"
                    assert history["publisherSignature"]=="NOT_PRESENT"
                    assert len(history["snapshots"])>=4

                # Adversarial: no path traversal or host authority via local slug.
                await page.locator("#edit-fork-slug").fill("../evil")
                await page.locator("#edit-fork").click()
                assert "FORK REJECTED" in await page.locator("#edit-status").inner_text()
                await page.locator("#edit-project").click()
                assert "PROJECT REJECTED" in await page.locator("#edit-status").inner_text()

                pic=out/(key+"-visual-diff.png")
                await page.screenshot(path=str(pic),animations="disabled")
                evidence["cases"].append({
                  "key":key,"studio_source_sha256":entry["html_sha256"],
                  "source_scene_sha256":entry["scene_sha256"],
                  "fork_sha256":sha(forkfile),"project_zip_sha256":sha(projectfile),
                  "browser_diff_screenshot_sha256":sha(pic),
                  "visual_operations":["source_vs_revision_diff","keyboard_pointer_typed_link",
                    "focusable_svg_edge","undo_redo","visual_fork","portable_zip_integrity",
                    "forged_slug_denial"],
                  "source_unchanged":True,"source_authority_preserved":True,
                  "measured_physics":"NOT_PRESENT","release":"HOLD"
                })
            assert len(evidence["cases"])==3
            assert not evidence["errors"],evidence["errors"]
            assert not evidence["blocked_external_requests"],evidence["blocked_external_requests"]
            evidence["result"]="PASS_OFFLINE_THREE_DOMAIN_PROJECT_FORK_DIFF_CONNECTOR"
        finally:
            await context.close()
            await b.close()
    (out/"OMEGA11M_PRODUCT_BROWSER_RECEIPT.json").write_text(json.dumps(evidence,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":evidence.get("result"),"cases":len(evidence["cases"]),
        "browser":evidence.get("chromium_version"),"release":"HOLD"}))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--gallery",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    raise SystemExit(asyncio.run(browser(args.gallery,args.output)))
