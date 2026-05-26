import { chromium } from 'playwright';
import path from 'path';

const SAVE_DIR = '/Users/kumonmotohiro/.gemini/antigravity/brain/547e00a6-9804-43cc-891a-144801f3b28c';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  console.log('Step 1: Navigating to registration URL...');
  await page.goto('http://localhost:8501/?user_id=demo_new_user_888', { waitUntil: 'networkidle', timeout: 30000 });
  await sleep(3000);

  const shot1 = path.join(SAVE_DIR, 'registration_flow_01_initial_load.png');
  await page.screenshot({ path: shot1, fullPage: true });
  console.log('Saved:', shot1);

  // Check for dialog/modal
  await sleep(2000);
  const shot2 = path.join(SAVE_DIR, 'registration_flow_02_after_load.png');
  await page.screenshot({ path: shot2, fullPage: true });
  console.log('Saved:', shot2);

  // Get page text content for analysis
  const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 2000));
  console.log('PAGE TEXT:', bodyText);

  // Check for any dialog/overlay
  const dialogVisible = await page.evaluate(() => {
    const dialogs = document.querySelectorAll('[data-testid="modal"], [role="dialog"], .stDialog, [data-baseweb="dialog"]');
    return { count: dialogs.length, text: Array.from(dialogs).map(d => d.innerText.substring(0, 300)).join(' | ') };
  });
  console.log('DIALOGS:', JSON.stringify(dialogVisible));

  // Try to interact if there's a profile dialog shown
  await sleep(1000);
  const shot3 = path.join(SAVE_DIR, 'registration_flow_03_dialog_state.png');
  await page.screenshot({ path: shot3, fullPage: true });
  console.log('Saved:', shot3);

  // Get all input fields
  const inputs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
      type: el.type,
      placeholder: el.placeholder,
      name: el.name,
      label: el.closest('label')?.innerText || el.getAttribute('aria-label') || ''
    }));
  });
  console.log('INPUTS:', JSON.stringify(inputs, null, 2));

  // Get all buttons
  const buttons = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(t => t.length > 0);
  });
  console.log('BUTTONS:', JSON.stringify(buttons));

  await browser.close();
  console.log('DONE');
})();
