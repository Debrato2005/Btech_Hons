#!/usr/bin/env node
'use strict';
// Compare full artifacts in separate fresh, offline Chromium processes.
const fs=require('node:fs'), path=require('node:path'), crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
async function run(artifact,output){
  const report={artifact:path.resolve(artifact),environment:{platform:process.platform,node:process.version},networkDisabled:true,samples:[],actions:[],errors:[]};
  report.bytes=fs.statSync(artifact).size;
  const hash=crypto.createHash('sha256');for await(const chunk of fs.createReadStream(artifact))hash.update(chunk);report.sha256=hash.digest('hex');
  const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
  report.environment.chromium=browser.version();report.environment.executable=process.env.CHROMIUM_PATH||'Playwright headless shell';
  const system=await browser.newBrowserCDPSession();
  let sampling=false;
  async function sample(stage){
    if(sampling)return;sampling=true;
    try{const {processInfo}=await system.send('SystemInfo.getProcessInfo');let rss=0,rendererRss=0;
      for(const p of processInfo){try{const k=Number(fs.readFileSync(`/proc/${p.id}/status`,'utf8').match(/^VmRSS:\s+(\d+)/m)?.[1]||0)*1024;rss+=k;if(p.type==='renderer')rendererRss+=k;}catch{}}
      report.samples.push({stage,ms:Math.round(performance.now()-start),rss,rendererRss});
    }finally{sampling=false;}
  }
  const context=await browser.newContext({offline:true,acceptDownloads:true,viewport:{width:1440,height:1000},reducedMotion:'reduce'}),page=await context.newPage();
  page.on('pageerror',e=>report.errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))report.errors.push('Network request: '+r.url());});
  const start=performance.now();const timer=setInterval(()=>sample('startup').catch(()=>{}),100);
  try{
    await page.goto(pathToFileURL(report.artifact).href,{waitUntil:'load',timeout:180000});
    await page.waitForFunction(()=>!!window.RoboticsStudyApp,null,{timeout:180000});
    report.usableMs=Math.round(performance.now()-start);clearInterval(timer);await sample('usable');
    const cdp=await context.newCDPSession(page);await cdp.send('Performance.enable');
    async function snapshot(stage){await sample(stage);const m=Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(m=>[m.name,m.value]));report[stage]={...report.samples.at(-1),heapUsed:m.JSHeapUsedSize,heapTotal:m.JSHeapTotalSize,nodes:m.Nodes};}
    await page.waitForTimeout(2000);await snapshot('steady');
    report.bank=await page.evaluate(()=>({version:RoboticsStudyApp.rawBank.bankVersion,total:RoboticsStudyApp.rawBank.questions.length,verified:RoboticsStudyApp.bank.questions.filter(q=>q.status==='verified').length}));
    for(const query of ['robot','Bayes','W12','']){const t=performance.now();await page.getByTestId('search').fill(query);await page.waitForFunction(q=>RoboticsStudyApp.getState().filters.search===q,query);report.actions.push({action:'search',query,ms:Math.round(performance.now()-t)});}
    const t=performance.now();for(let i=0;i<100;i++)await page.getByTestId('next').click();report.actions.push({action:'100 question navigations',ms:Math.round(performance.now()-t)});await snapshot('afterNavigation');
    await page.getByTestId('option-o1').count();
    await page.locator('.option').first().click();
    if(await page.getByTestId('submit-answer').isEnabled())await page.getByTestId('submit-answer').click();
    for(let i=0;i<30;i++){
      const t=performance.now();await page.getByTestId('source-open').first().click();await page.locator('#source-dialog').waitFor({state:'visible'});await page.getByRole('button',{name:'Close source preview',exact:true}).click();report.actions.push({action:'source open/close',ms:Math.round(performance.now()-t)});
      if(i%10===9)await snapshot('previewCycle'+(i+1));
    }
    await page.waitForTimeout(2000);await snapshot('afterPreviews');
    const figureIds=await page.evaluate(()=>{const b=RoboticsStudyApp.rawBank;return Object.entries(b.practiceInputs||b.questionVisuals?.bindings||{}).filter(([id,v])=>v.assetIds?.length).slice(0,20).map(([id])=>id);});
    for(const id of [...figureIds,...figureIds.slice(0,3)]){await page.getByTestId('search').fill(id);await page.waitForFunction(id=>RoboticsStudyApp.getState().filters.search===id,id);const images=page.getByTestId('question-visual');await images.first().waitFor();await images.evaluateAll(xs=>Promise.all(xs.map(i=>i.decode())));}
    await snapshot('afterFigureRevisits');
    report.cacheSize=await page.evaluate(()=>RoboticsStudyApp.assetCacheSize?.()??null);
    await cdp.send('HeapProfiler.collectGarbage');await snapshot('afterGC');
    fs.mkdirSync(path.dirname(output),{recursive:true});await page.screenshot({path:output.replace(/\.json$/,'.png'),fullPage:true});
  }catch(e){report.errors.push(e.stack);}finally{clearInterval(timer);report.peakStartupRss=Math.max(...report.samples.filter(s=>s.stage==='startup'||s.stage==='usable').map(s=>s.rss));report.peakRss=Math.max(...report.samples.map(s=>s.rss));report.peakRendererRss=Math.max(...report.samples.map(s=>s.rendererRss));await browser.close();fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');}
  console.log(JSON.stringify({output,bytes:report.bytes,usableMs:report.usableMs,peakRss:report.peakRss,steady:report.steady,errors:report.errors},null,2));
}
run(process.argv[2],process.argv[3]).catch(e=>{console.error(e);process.exitCode=1;});
