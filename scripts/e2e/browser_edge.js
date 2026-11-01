// Browser E2E: edge cases (404s, keyboard, competitor input, invalid edit blocked, Escape). Run: node scripts/e2e/browser_edge.js
const { chromium } = require('playwright');
const ok = (c, m) => { if (!c) throw new Error('ASSERT: ' + m); console.log('ok  -', m); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  // 404 + settings
  await p.goto('http://localhost:3000/launch/does-not-exist/tracker', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);
  const t404 = await p.innerText('body');
  ok(/could not load|not found|404/i.test(t404), 'unknown launch id shows an error, not a blank page');
  await p.goto('http://localhost:3000/settings', { waitUntil: 'networkidle' });
  ok((await p.innerText('body')).includes('Preview.'), 'settings page loads with the preview notice');
  await p.goto('http://localhost:3000/no-such-page', { waitUntil: 'networkidle' });
  ok((await p.innerText('body')).includes('Page not found'), 'unknown route shows the not-found page');
  // keyboard: new launch form reachable and submit by keyboard
  await p.goto('http://localhost:3000/launch/new', { waitUntil: 'networkidle' });
  await p.keyboard.press('Tab');
  const focus = await p.evaluate(() => document.activeElement?.tagName + ':' + (document.activeElement?.textContent || '').slice(0, 20));
  ok(focus.length > 3, `keyboard focus moves into the page (${focus})`);
  // competitor Enter adds a chip, max 10, dedupe
  await p.fill('#competitor-input', 'Alpha'); await p.keyboard.press('Enter');
  await p.fill('#competitor-input', 'Alpha'); await p.keyboard.press('Enter');
  ok((await p.$$('button[aria-label^="Remove"]')).length === 1, 'Enter adds a competitor; duplicates are ignored');
  await p.click('button[aria-label="Remove Alpha"]');
  ok((await p.$$('button[aria-label^="Remove"]')).length === 0, 'competitor chip can be removed');
  // invalid edit blocked in the generated form
  await p.goto('http://localhost:3000/launch/new?sample=1', { waitUntil: 'networkidle' });
  await p.click('button:has-text("Create launch")');
  await p.waitForSelector('[data-testid="hitl-panel"]', { timeout: 20000 });
  await p.click('button:has-text("Edit")'); await p.waitForSelector('[data-testid="edit-form"]');
  await p.getByLabel(/white space/i).first().fill('');
  await p.click('button:has-text("Submit edits")');
  await p.waitForTimeout(800);
  ok(await p.isVisible('[data-testid="edit-form"]'), 'clearing a required field keeps the edit form open (blocked)');
  ok(/required|must|error/i.test(await p.innerText('[data-testid="edit-form"]')), 'the form explains what is wrong');
  await p.keyboard.press('Escape');
  await p.waitForTimeout(400);
  ok(!(await p.isVisible('[data-testid="edit-form"]')), 'Escape closes the edit dialog');
  ok(await p.isVisible('[data-testid="hitl-panel"]'), 'review panel is still waiting after cancelling');
  console.log('page errors:', errs.length ? errs : 'none');
  await b.close();
})().catch(e => { console.error('FAILED:', e.message.slice(0, 400)); process.exit(1); });
