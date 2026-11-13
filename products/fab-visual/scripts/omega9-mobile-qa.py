#!/usr/bin/env python3
"""Ω9 scoped Chromium/Playwright verification of model-backed semantic inspection.
No external navigation. Generated synthetic HTML. Not WCAG/screen-reader certification.
"""
import asyncio, json, hashlib, pathlib, sys
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/'evidence'/'omega9-mobile'
OUT.mkdir(parents=True,exist_ok=True)
records=[];screenshots=[]
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def check(name,truth,detail=None):
    records.append({'name':name,'status':'PASS' if truth else 'FAIL','detail':detail})
    if not truth:raise AssertionError(f'{name}: {detail}')

async def scenario(browser,file,kind,viewport,reduce=False):
    width=viewport['width']; ctx=await browser.new_context(viewport=viewport,reduced_motion='reduce' if reduce else 'no-preference')
    page=await ctx.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.set_content(file.read_text(),wait_until='load',timeout=25000)
    prefix=f'{kind}_{width}'
    stage=page.locator('#stage' if kind=='policy' else '#scene')
    check(prefix+'_initial_svg',await stage.locator('svg[role=img]').count()==1)
    check(prefix+'_no_document_overflow',await page.evaluate('document.documentElement.scrollWidth <= innerWidth+2'))
    check(prefix+'_initial_zoom100',await page.locator('#zoom-level').inner_text()=='100%')
    check(prefix+'_parts_are_keyboard_labeled',await page.locator('#part-list button').count()==(4 if kind=='policy' else 1))
    sizes=await page.locator('#zoom-in').evaluate('(e)=>[e.getBoundingClientRect().width,e.getBoundingClientRect().height]')
    check(prefix+'_zoom_touch_height',sizes[1]>=44, sizes)
    font=await page.locator('#part-info').evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')
    check(prefix+'_inspector_text_16px',font>=16, font)
    await page.get_by_role('button',name='Zoom in diagram').focus()
    await page.keyboard.press('Enter')
    check(prefix+'_keyboard_150',await page.locator('#zoom-level').inner_text()=='150%')
    await page.get_by_role('button',name='Zoom in diagram').click()
    await page.get_by_role('button',name='Zoom in diagram').click()
    check(prefix+'_max_zoom300',await page.locator('#zoom-level').inner_text()=='300%')
    dims=await page.evaluate('''(stageId)=>{
      let el=document.getElementById(stageId),svg=el.querySelector('svg');
      return {svg:svg.getBoundingClientRect().width,viewport:el.clientWidth,scrollWidth:el.scrollWidth,bodyWidth:document.documentElement.scrollWidth,windowWidth:innerWidth};
    }''','stage' if kind=='policy' else 'scene')
    check(prefix+'_svg_magnified',dims['svg']>=dims['viewport']*2.75,dims)
    check(prefix+'_zoom_remains_contained',dims['bodyWidth']<=dims['windowWidth']+2,dims)
    if width==390: check(prefix+'_has_local_pan',dims['scrollWidth']>dims['viewport'],dims)
    part='Release' if kind=='policy' else 'Battery rack'
    await page.locator('#part-list button').filter(has_text=part).click()
    text=await page.locator('#part-info').inner_text()
    check(prefix+'_part_status_readable',part in text and 'status=' in text,text)
    check(prefix+'_part_pressed',await page.locator('#part-list button[aria-pressed=true]').count()==1)
    selected=await stage.locator('.part[data-selected=true]').count()
    check(prefix+'_diagram_part_highlight',selected==1,selected)
    zoomshot=OUT/f'omega9-{kind}-{width}-zoom300.png'
    await page.screenshot(path=str(zoomshot),full_page=False)
    screenshots.append(str(zoomshot))
    if kind=='policy':
      await page.get_by_role('button',name='Next',exact=True).click()
      check(prefix+'_frame_changes', 'Frame 2 of 5' in await page.locator('#phase').inner_text())
      check(prefix+'_selection_survives_state', 'Release' in await page.locator('#part-info').inner_text())
      await page.locator('#seek').focus(); await page.keyboard.press('End')
      check(prefix+'_final_model_release', 'released=true' in await page.locator('#phase').inner_text())
      check(prefix+'_inspector_live_released', 'status=RELEASED' in await page.locator('#part-info').inner_text())
    else:
      await page.get_by_role('button',name='Inspect components').click()
      check(prefix+'_component_descent',await page.locator('#part-list button').count()==2)
      check(prefix+'_semantic_two_children',await page.locator('#part-list').inner_text()=='Module A\nModule B')
      await page.locator('#part-list button').filter(has_text='Module A').focus()
      await page.keyboard.press('Enter')
      check(prefix+'_keyboard_focus_child','Module A' in await page.locator('#part-info').inner_text())
      await page.get_by_role('button',name='Overview').click()
      check(prefix+'_overview_clears_absent_child',await page.locator('#part-info').inner_text()=='Select a component to read its current label and status.')
    await page.get_by_role('button',name='Reset zoom').click()
    check(prefix+'_zoom_reset',await page.locator('#zoom-level').inner_text()=='100%')
    if reduce:check(prefix+'_media_reduce',await page.evaluate("matchMedia('(prefers-reduced-motion:reduce)').matches"))
    check(prefix+'_no_js_exceptions',not errors,errors)
    shot=OUT/f'omega9-{kind}-{width}.png'
    await page.screenshot(path=str(shot),full_page=False)
    screenshots.append(str(shot))
    await ctx.close()

async def main():
    outputs=[('policy',ROOT/'dist'/'omega9-policy.html'),('semantic',ROOT/'dist'/'omega9-semantic.html')]
    async with async_playwright() as p:
        executable='/usr/bin/chromium' if pathlib.Path('/usr/bin/chromium').exists() else p.chromium.executable_path
        browser=await p.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox','--disable-dev-shm-usage'])
        version=browser.version
        try:
            for kind,path in outputs:
                for width in (390,768,1280):
                    await scenario(browser,path,kind,{'width':width,'height':850},reduce=width==390)
        finally:await browser.close()
    receipt={'schema':'fab.omega9.mobile.v0.1','source_scope':'Generated synthetic HTML only','browser':version,'inputs':{p.name:sha(p) for _,p in outputs},'screenshots':{pathlib.Path(p).name:sha(p) for p in screenshots},'checks':records,'passed':sum(x['status']=='PASS' for x in records),'failed':sum(x['status']=='FAIL' for x in records),'limits':['Not a WCAG audit','Not physical metrology','Not real screen-reader testing','Not cross-browser','No live CodexStation installation'],'release':'HOLD'}
    (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'browser':version,'passed':receipt['passed'],'failed':receipt['failed'],'screenshots':len(screenshots)}))
    return 1 if receipt['failed'] else 0
if __name__=='__main__':
    try:sys.exit(asyncio.run(main()))
    except Exception as ex:
        (OUT/'FAILURE.txt').write_text(str(ex)+'\n')
        raise
