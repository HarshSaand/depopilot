from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1150},device_scale_factor=1.5)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8051');page.wait_for_function("document.getElementById('recipe').textContent==='AL120-0542'")
 page.screenshot(path=str(root/'artifacts/depopilot-recommendation.png'),full_page=True)
 page.get_by_role('button',name='Reveal recorded result').click();page.wait_for_function("document.getElementById('result').textContent.includes('0.660')")
 page.screenshot(path=str(root/'artifacts/depopilot-result.png'),full_page=True)
 with page.expect_download() as d:page.get_by_role('button',name='Recipe JSON').click()
 assert d.value.suggested_filename=='AL120-0542.json'
 page.get_by_role('button',name='Recommend next experiment').click();page.wait_for_function("document.getElementById('recipe').textContent!=='AL120-0542'")
 page.get_by_role('button',name='Reveal recorded result').click();page.wait_for_function("document.getElementById('result').textContent.includes('1.025')")
 page.screenshot(path=str(root/'artifacts/depopilot-completed.png'),full_page=True)
 page.set_input_files('#file',str(root/'artifacts/initial_observations.csv'));page.wait_for_function("document.getElementById('recipe').textContent==='AL120-0542'")
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(root/'artifacts/depopilot-mobile.png'),full_page=True)
 assert not errors,errors
 browser.close();print('Browser checks passed: initial recommendation, real reveal, download, update, CSV import and mobile layout.')
