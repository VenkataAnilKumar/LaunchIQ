// Browser E2E: failure UX. Start the API WITHOUT a model key first:
//   LLM_PROVIDER=anthropic ANTHROPIC_API_KEY= scripts/local_stack.sh up inline
// Run: node scripts/e2e/browser_failure.js (expects a clear error and a Retry button)
const { chromium } = require('playwright');
const ok = (c, m) => { if (!c) throw new Error('ASSERT: ' + m); console.log('ok  -', m); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:3000/launch/new?sample=2', { waitUntil: 'networkidle' });
  await p.waitForFunction(() => document.querySelector('#product-name')?.value.length > 0); await p.click('button:has-text("Create launch")');
  await p.waitForFunction(() => document.querySelector('[data-testid="launch-status"]')?.getAttribute('data-status') === 'failed', null, { timeout: 30000 });
  const t = await p.innerText('body');
  ok(/ANTHROPIC_API_KEY/.test(t), 'failure shows the real cause (missing API key)');
  ok(await p.isVisible('button:has-text("Retry market_intelligence")'), 'a Retry button is offered for the failed agent');
  await p.screenshot({ path: '.local/shots/w12-failed.png', fullPage: true });
  await p.click('button:has-text("Retry market_intelligence")');
  await p.waitForFunction(() => document.querySelector('[data-testid="launch-status"]')?.getAttribute('data-status') === 'failed', null, { timeout: 20000 });
  ok(await p.isVisible('button:has-text("Retry market_intelligence")'), 'retry runs again and fails cleanly (no crash)');
  console.log('page errors:', errs.length ? errs : 'none');
  await b.close();
})().catch(e => { console.error('FAILED:', e.message.slice(0, 400)); process.exit(1); });
