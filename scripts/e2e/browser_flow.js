// Browser E2E against the keyless local stack (make local + next dev). Needs playwright + chromium.
// Run: node scripts/e2e/browser_flow.js   (screenshots go to .local/shots/)
const { chromium } = require('playwright');
const fs = require('fs');
const shot = (p, n) => p.screenshot({ path: `.local/shots/${n}.png`, fullPage: true });
const body = async p => (await p.innerText('body')).replace(/\s+/g, ' ');
const assert = (c, m) => { if (!c) throw new Error('ASSERT: ' + m); console.log('ok  -', m); };
const BASE = 'http://localhost:3000';

(async () => {
  fs.mkdirSync('.local/shots', { recursive: true });
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 200)); });
  p.on('pageerror', e => errs.push('pageerror: ' + e.message.slice(0, 200)));
  p.on('response', r => { if (r.status() >= 400) errs.push(`http ${r.status()} ${r.url().slice(0, 100)}`); });

  // landing
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  const landing = await body(p);
  assert(landing.includes('One brief. Four agents. Two checkpoints'), 'landing page copy updated');
  assert(!landing.includes('03:47') && !landing.includes('< 10 min'), 'landing page has no unverifiable claims');
  await shot(p, 'w01-landing');

  // validation on empty submit
  await p.goto(BASE + '/launch/new', { waitUntil: 'networkidle' });
  await p.click('button:has-text("Create launch")');
  assert((await body(p)).includes('Enter a product name.'), 'empty form shows validation errors');
  await shot(p, 'w02-new-validation');

  // sample brief prefill via link and chip
  await p.goto(BASE + '/launch/new?sample=0', { waitUntil: 'networkidle' });
  await p.waitForFunction(() => document.querySelector('#product-name')?.value === 'Zephyr');
  assert(true, 'sample=0 prefills the form');
  await shot(p, 'w03-new-sample');
  await p.click('button:has-text("Create launch")');
  await p.waitForURL(/\/launch\/[0-9a-f-]+\/tracker/, { timeout: 15000 });

  // review 1: formatted, not raw JSON
  await p.waitForSelector('[data-testid="hitl-panel"]', { timeout: 20000 });
  let txt = await body(p);
  assert(txt.includes('Review the market research'), 'first review is titled for humans');
  assert(txt.includes('Acme Launch') && !txt.includes('"market_size"'), 'review shows formatted content, not raw JSON');
  await p.waitForFunction(() => /Live updates: connected/.test(document.body.innerText), null, { timeout: 10000 });
  assert(true, 'live stream connected');
  await shot(p, 'w04-review-1');

  // read other tab while paused
  await p.click('nav[aria-label="Launch sections"] a:has-text("Market")');
  await p.waitForFunction(() => document.body.innerText.includes('Acme Launch'), null, { timeout: 10000 });
  await p.click('nav[aria-label="Launch sections"] a:has-text("Progress")');
  await p.waitForSelector('[data-testid="hitl-panel"]');
  await p.fill('#review-comment', 'Looks right');
  await p.click('button:has-text("Approve")');

  // review 2 with generated edit form
  await p.waitForFunction(() => document.body.innerText.includes('Review the launch strategy'), null, { timeout: 20000 });
  assert(true, 'second review is the strategy');
  await shot(p, 'w05-review-2');
  await p.click('button:has-text("Edit")');
  await p.waitForSelector('[data-testid="edit-form"]', { timeout: 10000 });
  await shot(p, 'w06-edit-form');
  const field = p.getByLabel(/positioning statement/i).first();
  await field.fill('HUMAN-EDITED POSITIONING');
  await p.click('button:has-text("Submit edits")');
  await p.waitForFunction(() => document.querySelector('[data-testid="launch-status"]')?.getAttribute('data-status') === 'completed', null, { timeout: 30000 });
  assert(true, 'launch completed after the edit');
  await shot(p, 'w07-completed');

  const tabs = [['Personas', 'Priya'], ['Strategy', 'HUMAN-EDITED POSITIONING'], ['Content', 'Zephyr'], ['Document', 'HUMAN-EDITED POSITIONING']];
  for (const [tab, needle] of tabs) {
    await p.click(`nav[aria-label="Launch sections"] a:has-text("${tab}")`);
    await p.waitForFunction(n => document.body.innerText.includes(n), needle, { timeout: 10000 });
    assert(true, `${tab} tab shows "${needle}"`);
    await shot(p, `w08-${tab.toLowerCase()}`);
  }
  const [dl] = await Promise.all([p.waitForEvent('download'), p.click('button:has-text("Download .md")')]);
  const md = fs.readFileSync(await dl.path(), 'utf8');
  assert(md.includes('# Launch Brief: Zephyr') && md.includes('HUMAN-EDITED POSITIONING'), `document downloads (${dl.suggestedFilename()}) with the edit`);

  await p.click('nav[aria-label="Launch sections"] a:has-text("Analytics")');
  await p.waitForSelector('#metrics-json');
  await p.click('button:has-text("Analyze results")');
  await p.waitForSelector('[data-testid="analytics-result"]', { timeout: 15000 });
  assert((await body(p)).includes('Next action'), 'analytics recommendations rendered');
  await shot(p, 'w09-analytics');

  // dashboard: stats, search, filter
  await p.goto(BASE + '/dashboard', { waitUntil: 'networkidle' });
  assert((await body(p)).includes('Zephyr'), 'dashboard lists the launch');
  await p.fill('#launch-search', 'zzz-nothing');
  assert((await body(p)).includes('No launches match your search.'), 'search filters launches');
  await p.fill('#launch-search', 'zeph');
  assert((await body(p)).includes('Zephyr'), 'search finds the launch');
  await shot(p, 'w10-dashboard');

  // mobile: no horizontal overflow
  const m = await b.newContext({ viewport: { width: 390, height: 800 } });
  const mp = await m.newPage();
  for (const [name, path] of [['landing', '/'], ['dashboard', '/dashboard'], ['new', '/launch/new']]) {
    await mp.goto(BASE + path, { waitUntil: 'networkidle' });
    const overflow = await mp.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    assert(overflow <= 1, `mobile ${name}: no horizontal scroll (overflow ${overflow}px)`);
    await mp.screenshot({ path: `.local/shots/w11-mobile-${name}.png`, fullPage: true });
  }

  console.log('BROWSER ERRORS:', errs.length ? errs : 'none');
  await b.close();
  if (errs.length) process.exit(1);
})().catch(e => { console.error('FLOW FAILED:', e.message.slice(0, 600)); process.exit(1); });
