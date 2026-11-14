#!/usr/bin/env python3
"""Ω11N: real Chromium offline ZIP import, SHA admission and reversible local replay."""
from __future__ import annotations
import argparse,asyncio,hashlib,json
from pathlib import Path
from playwright.async_api import async_playwright

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

async def wait_text(page,selector,fragment):
    for _ in range(125):
        txt=await page.locator(selector).inner_text()
        if fragment in txt:return txt
        await asyncio.sleep(.08)
    raise AssertionError(f"Timed out waiting for {fragment} in {selector}: "+(await page.locator(selector).inner_text()))

async def main(gallery,output):
    gallery=gallery.resolve(strict=True);output.mkdir(parents=True,exist_ok=True)
    index=json.loads((gallery/"gallery.manifest.json").read_text())
    witness={"schema":"fab.visual.omega11n.project-import-browser.v1",
             "release":"HOLD","publisherSignature":"NOT_PRESENT",
             "scientificValidation":"NOT_RUN","gpuPresent":"NOT_ADMITTED",
             "sourceLock":"SEPARATE_173_GIT_OBJECT_CI_GATE",
             "cases":[],"errors":[],"blockedExternal":[]}
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--disable-background-networking","--disable-dev-shm-usage"])
        witness["chromium"]=browser.version
        context=await browser.new_context(viewport={"width":1500,"height":1080},
            color_scheme="light",reduced_motion="reduce",device_scale_factor=1,accept_downloads=True)
        page=await context.new_page()
        page.on("pageerror",lambda e:witness["errors"].append(str(e)[:400]))
        async def local_only(route):
            url=route.request.url
            if url.startswith(("file://","data:","blob:")):await route.continue_()
            else:
                witness["blockedExternal"].append(url[:250]);await route.abort()
        await page.route("**/*",local_only)
        archives={}
        try:
            # Create a genuine Ω11M project from each user-facing source Studio.
            for entry in index["templates"]:
                key=entry["key"]
                await page.goto((gallery/entry["studio_path"]).as_uri(),wait_until="load",timeout=45000)
                x0=float(await page.locator("#edit-x").input_value())
                await page.locator("#edit-x").fill(str(x0+25))
                await page.locator("#edit-apply").click()
                await page.locator("#edit-fork-slug").fill("replay-a")
                async with page.expect_download() as pending:
                    await page.locator("#edit-project").click()
                download=await pending.value
                archive=output/(key+"-source-project.zip")
                await download.save_as(archive)
                archives[key]=(archive,x0)
                assert archive.stat().st_size>200
            for entry in index["templates"]:
                key=entry["key"]
                path,x0=archives[key]
                await page.goto((gallery/entry["studio_path"]).as_uri(),wait_until="load",timeout=45000)
                assert await page.locator("#edit-replay-cards button").count()==1
                assert float(await page.locator("#edit-x").input_value())==x0
                assert await page.locator("#edit-replay-apply").is_disabled()
                assert await page.locator("#edit-project-import-file").is_visible()
                await page.locator("#edit-project-import-file").set_input_files(str(path))
                accepted=await wait_text(page,"#edit-project-import-status","SOURCE-BOUND LOCAL PROJECT ACCEPTED")
                assert "SHA-256 checked" in accepted
                assert "NOT PRESENT" in accepted and "RELEASE HOLD" in accepted
                assert await page.locator("#edit-replay-cards button").count()==2
                assert float(await page.locator("#edit-x").input_value())==x0+25
                assert await page.locator("button[data-view='isometric']").is_disabled()
                await page.locator("#edit-replay-cards button").first.click()
                assert await page.locator("#edit-diff").is_visible()
                assert "0 moved" in await page.locator("#edit-diff").inner_text()
                assert float(await page.locator("#edit-x").input_value())==x0+25
                await page.locator("#edit-replay-apply").click()
                assert float(await page.locator("#edit-x").input_value())==x0
                assert await page.locator("#edit-undo").is_disabled()
                await page.locator("#edit-replay-next").click()
                assert "1 moved" in await page.locator("#edit-diff").inner_text()
                await page.locator("#edit-replay-apply").click()
                assert float(await page.locator("#edit-x").input_value())==x0+25
                await page.locator("#edit-undo").click()
                assert float(await page.locator("#edit-x").input_value())==x0
                await page.locator("#edit-redo").click()
                assert float(await page.locator("#edit-x").input_value())==x0+25
                # Wrong model's project must not change the working scene.
                foreign=next(v[0] for k,v in archives.items() if k!=key)
                await page.locator("#edit-project-import-file").set_input_files(str(foreign))
                await wait_text(page,"#edit-project-import-status","PROJECT REJECTED")
                assert float(await page.locator("#edit-x").input_value())==x0+25
                # Valid source archive with one flipped byte fails CRC.
                corrupt=output/(key+"-tampered.zip")
                bits=bytearray(path.read_bytes())
                i=bits.find(b'FAB.VISUAL')
                assert i>0
                bits[i]^=1
                corrupt.write_bytes(bits)
                await page.locator("#edit-project-import-file").set_input_files(str(corrupt))
                await wait_text(page,"#edit-project-import-status","PROJECT REJECTED")
                assert float(await page.locator("#edit-x").input_value())==x0+25
                # Editor must remain functional after two rejected inputs.
                async with page.expect_download() as pending:
                    await page.locator('button[data-export="scene"]').click()
                download=await pending.value
                out=output/(key+"-replayed.scene.json")
                await download.save_as(out)
                parsed=json.loads(out.read_text())
                assert parsed["claim"]["status"]=="EXPLANATORY"
                assert parsed["parts"][0]["x"]==x0+25
                assert parsed["model"]["synthetic"] is True
                assert parsed["model"]["authority"]==json.loads((gallery/entry["scene_path"]).read_text())["model"]["authority"]
                shot=output/(key+"-import-replay.png")
                await page.screenshot(path=str(shot),animations="disabled")
                witness["cases"].append({"domain":key,"source_zip_sha256":digest(path),
                    "replayed_scene_sha256":digest(out),
                    "browser_screenshot_sha256":digest(shot),
                    "steps":["ZIP_EXPORT","SHA_CRC_SOURCE_ID_ADMISSION","TIMELINE_CARDS",
                             "SOURCE_PREVIEW_NONMUTATING","APPLY_REVISION","UNDO_REDO",
                             "REJECT_FOREIGN_SOURCE","REJECT_TAMPERED_CRC",
                             "RETAIN_PRIOR_EDITOR_STATE"],"release":"HOLD"})
            assert len(witness["cases"])==3
            assert not witness["blockedExternal"],witness["blockedExternal"]
            assert not witness["errors"],witness["errors"]
            witness["result"]="PASS_THREE_DOMAIN_SOURCE_BOUND_ZIP_IMPORT_REPLAY"
        finally:
            await context.close();await browser.close()
    (output/"OMEGA11N_PROJECT_IMPORT_BROWSER_RECEIPT.json").write_text(
        json.dumps(witness,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"result":witness.get("result"),"cases":len(witness["cases"]),
                      "release":witness["release"],"errors":witness["errors"]}))
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--gallery",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    asyncio.run(main(a.gallery,a.output))
