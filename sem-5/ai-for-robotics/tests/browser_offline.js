#!/usr/bin/env node
/* Run the actual single-file artifact with file:// and networking disabled.
 * node tests/browser_offline.js [path/to/ai-for-robotics-mcq.html] [report.json]
 * This smoke/performance report does NOT certify answer correctness or full coverage.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const zlib = require('zlib');
const {pathToFileURL} = require('url');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const artifact = path.resolve(process.argv[2] || path.join(root, 'dist/ai-for-robotics-mcq.html'));
const output = path.resolve(process.argv[3] || path.join(root, 'audits/browser-report.json'));
const report = {
  schemaVersion: '1.0.0', suite: 'offline-file-url-smoke-performance',
  startedAt: new Date().toISOString(), artifact, fileUrl: pathToFileURL(artifact).href,
  scope: 'Actual bytes at the specified local path; not downloaded-release validation unless that path is the independently downloaded release.',
  networkDisabled: true, checks: [], errors: [], networkRequests: [], screenshots: [], performance: {},
  limitations: ['Structural/browser checks do not certify source coverage or answer correctness.',
    'Full behavior tests and human screenshot inspection are separate gates.']
};
function assert(value, message) {if (!value) throw new Error(message);}
async function check(name, fn) {
  const start = performance.now();
  try {const detail = await fn(); report.checks.push({name, status: 'passed', elapsedMs: performance.now()-start, detail});}
  catch (error) {report.checks.push({name, status: 'failed', elapsedMs: performance.now()-start, reason: error.message});}
}
function pending(name, reason) {report.checks.push({name, status: 'pending', reason});}
(async () => {
  if (!fs.existsSync(artifact)) throw new Error(`Artifact absent: ${artifact}. Offline release QA remains pending.`);
  const bytes = fs.readFileSync(artifact);
  report.artifactSha256 = crypto.createHash('sha256').update(bytes).digest('hex');
  report.fileBytes = bytes.length;
  report.gzipBytes = zlib.gzipSync(bytes).length;
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless: true, args: ['--no-sandbox']});
  report.browserVersion = browser.version(); report.nodeVersion = process.version;
  const context = await browser.newContext({offline: true, viewport: {width: 1440, height: 1000}, acceptDownloads: true, reducedMotion: 'reduce'});
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push({kind: 'pageerror', message: error.message}));
  page.on('console', message => {if (message.type() === 'error') errors.push({kind: 'console', message: message.text()});});
  page.on('request', request => {if (/^https?:/i.test(request.url())) report.networkRequests.push({url: request.url(), type: request.resourceType()});});
  const start = performance.now();
  await page.goto(report.fileUrl, {waitUntil: 'load', timeout: 120000});
  await page.waitForTimeout(250);
  report.performance.firstSettledLoadMs = performance.now()-start;
  report.performance.navigation = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0];
    return navigation ? {domInteractiveMs: navigation.domInteractive, domContentLoadedMs: navigation.domContentLoadedEventEnd, loadEventMs: navigation.loadEventEnd} : null;
  });
  const cdp = await context.newCDPSession(page);
  await cdp.send('Performance.enable');
  report.performance.chromiumMetrics = Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.filter(x => ['JSHeapUsedSize','JSHeapTotalSize','Nodes','Documents','LayoutCount','RecalcStyleCount','TaskDuration'].includes(x.name)).map(x => [x.name,x.value]));
  await check('file_protocol', async () => assert(await page.evaluate(() => location.protocol === 'file:'), 'Not a filesystem-opened artifact'));
  await check('offline_no_network_dependencies', async () => assert(report.networkRequests.length === 0, JSON.stringify(report.networkRequests)));
  await check('visible_content', async () => assert((await page.locator('body').innerText()).trim().length > 50, 'Blank/near-blank application'));
  await check('document_semantics', async () => {
    const values = await page.evaluate(() => ({lang:document.documentElement.lang,title:document.title,viewport:!!document.querySelector('meta[name="viewport"]')}));
    assert(values.lang && values.title && values.viewport, JSON.stringify(values)); return values;
  });
  const search = page.getByTestId('search');
  if (await search.count()) {
    await check('typing_does_not_trigger_shortcuts', async () => {
      await search.fill(''); await search.pressSequentially('1234');
      assert(await search.inputValue() === '1234', 'Numeric selection shortcut interferes with search typing'); await search.fill('');
    });
    await check('search_interaction_latency', async () => {
      const started = performance.now(); await search.fill('robot'); await page.waitForTimeout(30);
      const elapsedMs = performance.now()-started; report.performance.searchResponseMs = elapsedMs; await search.fill(''); return {elapsedMs};
    });
  } else pending('search_behavior', 'search test hook absent');
  const theme = page.getByTestId('theme');
  if (await theme.count()) {
    await check('theme_toggle_and_reload', async () => {
      const signature = () => page.evaluate(() => ({rootClass:document.documentElement.className,rootTheme:document.documentElement.dataset.theme,bodyClass:document.body.className,bodyTheme:document.body.dataset.theme,background:getComputedStyle(document.body).backgroundColor}));
      const before = await signature(); await theme.click(); const after = await signature();
      assert(JSON.stringify(before)!==JSON.stringify(after), 'Theme button did not change presentation');
      await page.reload({waitUntil:'load'}); const reloaded = await signature();
      assert(JSON.stringify(after)===JSON.stringify(reloaded), 'Theme did not persist reload'); return {before,after};
    });
  } else pending('theme_toggle_and_reload', 'theme test hook absent');
  for (const viewport of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]) {
    await page.setViewportSize(viewport); await page.waitForTimeout(70);
    await check(`viewport_${viewport.width}_no_document_overflow`, async () => {
      const dimensions = await page.evaluate(() => ({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));
      assert(dimensions.scroll<=dimensions.client+2, `Document overflows: ${JSON.stringify(dimensions)}`);return dimensions;
    });
    const screenshotPath = path.join(path.dirname(output),'screenshots',`offline-${viewport.width}.png`);
    fs.mkdirSync(path.dirname(screenshotPath),{recursive:true}); await page.screenshot({path:screenshotPath,fullPage:true});report.screenshots.push(screenshotPath);
  }
  await page.setViewportSize({width:1440,height:1000});
  await check('keyboard_focus_visible', async () => {
    await page.locator('body').click({position:{x:2,y:2}}); await page.keyboard.press('Tab');
    const focus = await page.evaluate(() => {const e=document.activeElement,s=getComputedStyle(e);return {tag:e.tagName,outlineStyle:s.outlineStyle,outlineWidth:s.outlineWidth,boxShadow:s.boxShadow};});
    assert(focus.tag!=='BODY', 'Tab did not focus a control');
    assert((focus.outlineStyle!=='none' && parseFloat(focus.outlineWidth)>0)||focus.boxShadow!=='none', `No visible keyboard focus: ${JSON.stringify(focus)}`);return focus;
  });
  await check('no_runtime_errors', async () => assert(errors.length===0, JSON.stringify(errors)));
  report.errors = errors;
  report.finishedAt = new Date().toISOString();
  report.status = report.checks.some(x=>x.status==='failed')?'failed':report.checks.some(x=>x.status==='pending')?'partial':'passed';
  await browser.close();
})().catch(error => {report.status='blocked';report.errors.push({kind:'runner',message:error.stack});process.exitCode=1;}).finally(()=>{
  fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({status:report.status,artifact,checks:report.checks.map(x=>({name:x.name,status:x.status,reason:x.reason})),report:output},null,2));
  if (report.status==='failed') process.exitCode=1;
});
