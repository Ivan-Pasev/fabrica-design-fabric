#!/usr/bin/env python3
"""Ω6 browser regression: controlled generated HTML only, loaded via set_content.
Prereqs: Python Playwright, locally installed Chromium. No external navigation.
This is keyboard/DOM/screenshot evidence, NOT screen-reader or WCAG certification.
"""
import asyncio, json, hashlib, pathlib, sys, datetime
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT/'evidence'/'omega6-browser'
OUT.mkdir(parents=True,exist_ok=True)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
async def main():
    reports=[]; problems=[]; screenshots=[]
    async with async_playwright() as p:
        executable='/usr/bin/chromium' if pathlib.Path('/usr/bin/chromium').exists() else p.chromium.executable_path
        browser=await p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        browser_version=browser.version
        async def scenario(name,html,viewport,reduced_motion=None):
            ctx=await browser.new_context(viewport=viewport,reduced_motion=reduced_motion or 'no-preference')
            page=await ctx.new_page()
            exceptions=[]; page.on('pageerror',lambda e:exceptions.append(str(e)))
            await page.set_content(html,wait_until='load',timeout=16000)
            return ctx,page,exceptions
        def check(n,good,notes=''):
            reports.append({'name':n,'status':'PASS' if good else 'FAIL','notes':notes})
            if not good:problems.append(n+': '+notes)
        timeline_path=ROOT/'dist'/'anatomy-timeline.html'
        html=timeline_path.read_text()
        ctx,page,errors=await scenario('policy',html,{'width':1365,'height':900})
        check('policy_initial_state', 'Frame 1 of 5' in await page.locator('#phase').inner_text())
        check('policy_initial_release_false','released=false' in await page.locator('#phase').inner_text())
        check('policy_svg_has_accessible_name', await page.locator('#stage svg[role="img"] > title#fab-ttl').count()==1)
        check('policy_previous_disabled_initial',await page.locator('#prev').is_disabled())
        for n in range(1,5):
            await page.get_by_role('button',name='Next').click()
            check(f'policy_forward_frame_{n+1}',f'Frame {n+1} of 5' in await page.locator('#phase').inner_text())
        check('policy_final_authorized_release', 'authorized=true' in await page.locator('#phase').inner_text() and 'released=true' in await page.locator('#phase').inner_text())
        check('policy_next_disabled_final',await page.locator('#next').is_disabled())
        frames=await page.evaluate("JSON.parse(document.getElementById('frames').textContent)")
        finalparts=await page.locator('#stage [data-part="release"]').get_attribute('data-status')
        check('policy_final_status_matches_trace',finalparts=='RELEASED' and frames[-1]['observables'][-1]['value'] is True)
        screen=OUT/'policy-final-desktop.png';await page.screenshot(path=str(screen),full_page=True);screenshots.append(str(screen))
        await page.locator('#seek').focus();await page.keyboard.press('Home')
        check('policy_keyboard_home','Frame 1 of 5' in await page.locator('#phase').inner_text())
        await page.keyboard.press('End')
        check('policy_keyboard_end','Frame 5 of 5' in await page.locator('#phase').inner_text())
        await page.get_by_role('button',name='Previous').focus();await page.keyboard.press('Enter')
        check('policy_keyboard_previous','Frame 4 of 5' in await page.locator('#phase').inner_text())
        check('policy_no_js_exceptions',not errors,';'.join(errors[:4]))
        await ctx.close()

        ctx,page,errors=await scenario('policy-mobile',html,{'width':390,'height':844},'reduce')
        check('policy_reduced_motion_declared',await page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"))
        check('policy_mobile_no_horizontal_overflow',await page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'))
        await page.get_by_role('button',name='Next').click()
        check('policy_mobile_click','Frame 2 of 5' in await page.locator('#phase').inner_text())
        screen=OUT/'policy-mobile-reduced-motion.png';await page.screenshot(path=str(screen),full_page=True);screenshots.append(str(screen))
        check('policy_mobile_no_js_exceptions',not errors,';'.join(errors[:4]));await ctx.close()

        path=ROOT/'dist'/'semantic-descent.html';doc=path.read_text()
        ctx,page,errors=await scenario('semantic',doc,{'width':1280,'height':900})
        check('semantic_initial_overview','System overview' in await page.locator('#level').inner_text())
        check('semantic_refinement_pass_text','numerical refinement=PASS' in await page.locator('#level').inner_text())
        check('semantic_parent_part',await page.locator('#scene [data-part="rack"]').count()==1)
        await page.get_by_role('button',name='Inspect components').click()
        check('semantic_child_view',await page.locator('#scene [data-part="moduleA"]').count()==1 and await page.locator('#scene [data-part="moduleB"]').count()==1)
        check('semantic_parent_hidden_after_descent',await page.locator('#scene [data-part="rack"]').count()==0)
        await page.locator('details summary').click()
        check('semantic_evidence_sum', '"derived": 24' in await page.locator('#evidence').inner_text())
        shot=OUT/'semantic-component-descent.png';await page.screenshot(path=str(shot),full_page=True);screenshots.append(str(shot))
        await page.get_by_role('button',name='Overview').focus();await page.keyboard.press('Enter')
        check('semantic_keyboard_return',await page.locator('#scene [data-part="rack"]').count()==1)
        check('semantic_no_js_exceptions',not errors,';'.join(errors[:4]))
        await ctx.close();await browser.close()
    report={'schema':'fab.browser_qa.v0.1','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser':browser_version,'browser_engine':'Chromium via Playwright Python; HTML loaded with set_content (no file/http navigation)','inputs':{str(x.relative_to(ROOT)):sha(x) for x in [timeline_path,ROOT/'dist'/'semantic-descent.html']},'screenshots':{str(pathlib.Path(s).relative_to(ROOT)):sha(pathlib.Path(s)) for s in screenshots},'checks':reports,'passes':sum(r['status']=='PASS' for r in reports),'fails':len(problems),'screen_reader_test':'NOT_RUN','wcag_full_audit':'NOT_RUN','cross_browser':'NOT_RUN','production':'HOLD','failures':problems}
    (OUT/'BROWSER_QA_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passes':report['passes'],'fails':report['fails'],'browser':report['browser'],'screenshots':list(report['screenshots']),'failures':problems},indent=2))
    return 1 if problems else 0
if __name__=='__main__':sys.exit(asyncio.run(main()))
