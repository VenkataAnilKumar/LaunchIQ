// Browser E2E: reject at the first review checkpoint. Run: node scripts/e2e/browser_reject.js
const { chromium } = require('playwright');
const assert = (c, m) => { if (!c) throw new Error('ASSERT: ' + m); console.log('ok  -', m); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); 
  p.on('dialog', d => d.accept());
  await p.goto('http://localhost:3000/launch/new', { waitUntil: 'networkidle' });
  await p.fill('input >> nth=0', 'RejectMe');
  await p.fill('textarea', 'A product we will reject at the first review checkpoint.');
  await p.fill('input[placeholder="B2B SaaS founders in North America"]', 'Testers');
  await p.click('button:has-text("Create launch")');
  await p.waitForSelector('[data-testid="hitl-panel"]', { timeout: 20000 });
  await p.click('button:has-text("Reject")');
  await p.waitForFunction(() => document.querySelector('[data-testid="launch-status"]')?.getAttribute('data-status') === 'rejected', null, { timeout: 15000 });
  assert(!(await p.$('[data-testid="hitl-panel"]')), 'review panel gone after reject');
  assert((await p.innerText('body')).includes('You rejected this launch'), 'rejected status explained');
  await p.goto('http://localhost:3000/dashboard', { waitUntil: 'networkidle' });
  assert((await p.innerText('body')).toLowerCase().includes('rejected'), 'dashboard shows rejected pill');
  console.log('page errors:', errs.length ? errs : 'none');
  await b.close();
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
