const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  page.on('console', msg => {
    console.log(`[BROWSER CONSOLE - ${msg.type()}]: ${msg.text()}`);
  });

  page.on('pageerror', err => {
    console.error(`[BROWSER PAGE ERROR]:`, err.stack || err.toString());
  });

  page.on('requestfailed', request => {
    console.warn(`[BROWSER REQUEST FAILED]: ${request.url()} - ${request.failure().errorText}`);
  });

  console.log('Navigating to https://possessive-brother.surge.sh ...');
  try {
    await page.goto('https://possessive-brother.surge.sh', {
      waitUntil: 'networkidle0',
      timeout: 15000
    });
    console.log('Navigation complete.');

    // Wait a brief moment for any dynamic rendering
    await new Promise(resolve => setTimeout(resolve, 2000));

    const title = await page.title();
    console.log(`Page Title: "${title}"`);

    // Find and click the restore mode button
    const restoreButton = await page.evaluateHandle(() => {
      const elements = Array.from(document.querySelectorAll('div, span, p, a, [role="button"]'));
      return elements.find(b => b.textContent && b.textContent.includes('登録済みデータから復元'));
    });
    if (restoreButton) {
      await restoreButton.click();
      console.log('Clicked restore mode button.');
    } else {
      console.error('Could not find restore button.');
    }

    await new Promise(resolve => setTimeout(resolve, 1000));

    // Fill inputs and click submit button in browser context
    const actionResult = await page.evaluate(() => {
      const logs = [];
      const log = (msg) => logs.push(msg);

      // Find inputs
      const inputs = Array.from(document.querySelectorAll('input'));
      const visibleInputs = inputs.filter(i => i.offsetParent !== null);
      log(`Found ${inputs.length} inputs in DOM, ${visibleInputs.length} are visible.`);
      
      // Let's look for inputs with placeholders or types
      const nameInput = visibleInputs[0];
      const pinInput = visibleInputs[1];

      if (nameInput && pinInput) {
        nameInput.value = 'もと';
        pinInput.value = '1234';
        // Dispatch React events
        nameInput.dispatchEvent(new Event('input', { bubbles: true }));
        pinInput.dispatchEvent(new Event('input', { bubbles: true }));
        log('Filled visible name and pin input fields.');
      } else {
        log('Error: Could not find visible inputs.');
      }

      // Find submit button
      const buttons = Array.from(document.querySelectorAll('div, span, p, a, [role="button"]'));
      const submitBtn = buttons.find(el => el.textContent && el.textContent.includes('ログインしてデータを復元する'));
      if (submitBtn) {
        submitBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        log('Clicked the login submit button.');
      } else {
        log('Error: Could not find login submit button.');
      }
      return logs;
    });

    console.log('Simulation logs:', actionResult);

    // Wait for the fetch and response
    await new Promise(resolve => setTimeout(resolve, 5000));

    const textContent = await page.evaluate(() => document.body.innerText);
    console.log(`Page text content length: ${textContent.length}`);
    console.log(`Snippet of content:\n--- \n${textContent.slice(0, 300)}\n---`);

    const screenshotPath = '/Users/kumonmotohiro/.gemini/antigravity/brain/0d7370b0-cae8-4cc1-9141-b70a9a025232/web_screenshot.png';
    await page.screenshot({ path: screenshotPath });
    console.log(`Screenshot saved to: ${screenshotPath}`);

  } catch (e) {
    console.error('Navigation/Simulation error:', e.message);
  }

  await browser.close();
})();
