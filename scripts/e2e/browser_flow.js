// Browser E2E against the keyless local stack (make local + next dev). Needs playwright + chromium.
// Run: node scripts/e2e/browser_flow.js   (screenshots go to .local/shots/)
const { chromium } = require('playwright');
const shot = (p, n) => p.screenshot({ path: `.local/shots/${n}.png`, fullPage: true });
const body = async p => (await p.innerText('body')).replace(/\s+/g, ' ');
const assert = (c, m) => { if (!c) throw new Error('ASSERT: ' + m); console.log('ok  -', m); };
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 1000 }, acceptDownloads: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 200)); });
  p.on('pageerror', e => errs.push('pageerror: ' + e.message.slice(0, 200)));
  p.on('response', r => { if (r.status() >= 400) errs.push(`http ${r.status()} ${r.url().slice(0, 100)}`); });

  await p.goto('http://localhost:3000/launch/new', { waitUntil: 'networkidle' });
  await p.fill('input >> nth=0', 'Zephyr');
  await p.fill('textarea', 'An AI assistant that plans product launches for small B2B teams.');
  await p.fill('input[placeholder="B2B SaaS founders in North America"]', 'B2B SaaS startups');
  await p.fill('input[placeholder="Add competitor"]', 'Acme Launch');
  await p.click('button:has-text("Add")');
  await p.click('button:has-text("Create launch")');
  await p.waitForURL(/\/launch\/[0-9a-f-]+\/tracker/, { timeout: 15000 });
  const base = p.url().replace('/tracker', '');

  await p.waitForSelector('[data-testid="hitl-panel"]', { timeout: 20000 });
  assert((await body(p)).includes('Zephyr'), 'tracker shows product name');
  assert((await body(p)).includes('brief_review'), 'first review is brief_review');
  await p.waitForFunction(() => document.body.innerText.includes('connected') && !document.body.innerText.includes('reconnecting'), null, { timeout: 10000 });
  assert(true, 'live stream connected (auth header works)');
  await shot(p, '3-review-1');

  // read the brief while the pipeline is paused (no blocking overlay)
  await p.click('a:has-text("Brief")');
  await p.waitForURL(/\/brief/);
  await p.waitForFunction(() => document.body.innerText.includes('Acme Launch'), null, { timeout: 10000 });
  assert(true, 'brief page renders market data during review');
  await shot(p, '4-brief');
  await p.click('a:has-text("Tracker")'); await p.waitForURL(/\/tracker/);
  await p.waitForSelector('[data-testid="hitl-panel"]');
  await p.click('button:has-text("Approve")');

  await p.waitForFunction(() => document.body.innerText.includes('strategy_review'), null, { timeout: 20000 });
  assert(true, 'second review is strategy_review');
  await shot(p, '5-review-2');

  // edit: change positioning statement
  await p.click('button:has-text("Edit")');
  const ta = p.locator('#hitl-edit-json');
  const obj = JSON.parse(await ta.inputValue());
  obj.positioning_statement = 'HUMAN-EDITED POSITIONING';
  await ta.fill(JSON.stringify(obj, null, 2));
  await p.click('button:has-text("Submit edits")');

  await p.waitForFunction(() => document.querySelector('[data-testid="launch-status"]')?.getAttribute('data-status') === 'completed', null, { timeout: 30000 });
  assert(true, 'launch completed');
  await shot(p, '6-completed');

  for (const [tab, needle] of [['Personas', 'Priya'], ['Strategy', 'HUMAN-EDITED POSITIONING'], ['Content', 'Zephyr']]) {
    await p.click(`a:has-text("${tab}")`);
    await p.waitForFunction(n => document.body.innerText.includes(n), needle, { timeout: 10000 });
    assert(true, `${tab} page shows "${needle}"`);
    await shot(p, `7-${tab.toLowerCase()}`);
  }
  await p.click('a:has-text("Tracker")'); await p.waitForURL(/\/tracker/);
  const [dl] = await Promise.all([p.waitForEvent('download'), p.click('button:has-text("Download launch brief")')]);
  const path = await dl.path();
  const md = require('fs').readFileSync(path, 'utf8');
  assert(md.includes('# Launch Brief: Zephyr') && md.includes('HUMAN-EDITED POSITIONING'), `export downloaded (${dl.suggestedFilename()}) and contains the edit`);

  await p.click('a:has-text("Analytics")');
  await p.waitForSelector('#metrics-json');
  await p.click('button:has-text("Analyze results")');
  await p.waitForSelector('[data-testid="analytics-result"]', { timeout: 15000 });
  assert((await body(p)).includes('Next action'), 'analytics recommendations rendered from supplied metrics');
  await shot(p, '9-analytics');
  await p.fill('#metrics-json', '{not json');
  await p.click('button:has-text("Analyze results")');
  assert((await body(p)).includes('valid JSON'), 'invalid metrics JSON is rejected client-side');

  await p.goto('http://localhost:3000/dashboard', { waitUntil: 'networkidle' });
  assert((await body(p)).includes('Zephyr'), 'dashboard lists the launch');
  await shot(p, '8-dashboard');
  console.log('BROWSER ERRORS:', errs.length ? errs : 'none');
  await b.close();
})().catch(e => { console.error('FLOW FAILED:', e.message.slice(0, 500)); process.exit(1); });
