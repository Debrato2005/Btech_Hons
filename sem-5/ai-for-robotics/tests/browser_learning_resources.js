#!/usr/bin/env node
/* Browser component checks with explicitly synthetic in-memory approvals.
 * Does not activate a course policy or certify subject-matter correctness.
 */
'use strict';
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const {fixture,approveTool}=require('./fixtures/learning-resource-bank.js');
const R=require('../app/learning-resources.js'),root=path.resolve(__dirname,'..');
const output=process.argv[2]||path.join(root,'audits/learning-resource-browser-author-checks.json');
const report={scope:'Author browser component checks; synthetic fixtures only, no independent course approval.',checks:[],errors:[],screenshots:[]};
function assert(ok,msg){if(!ok)throw Error(msg);}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const ctx=await browser.newContext({offline:true,viewport:{width:1200,height:900}}),page=await ctx.newPage();page.on('pageerror',e=>report.errors.push(e.message));
 await page.setContent('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Synthetic resource component test</title></head><body><main id="resources"></main></body></html>');
 await page.addStyleTag({content:fs.readFileSync(path.join(root,'app/styles.css'),'utf8')});
 for(const file of ['learning-resources.js','learning-resource-ui.js'])await page.addScriptTag({content:fs.readFileSync(path.join(root,'app',file),'utf8')});
 const b=fixture();for(let i=1;i<45;i++){const q=structuredClone(b.questions[0]);q.id='Q'+i;q.stem+=' Example '+i;q.week=i%11+1;q.lectureId='L'+String(i%53+1).padStart(2,'0');q.solution.formulas[0].expression+=' + '+i;b.questions.push(q);b.reviews.push({...b.reviews[0],id:'R'+i,questionId:q.id});b.learningResourceIntegrity.bindings[q.id]={...b.learningResourceIntegrity.bindings.Q,runtimeSha256:R.runtimeQuestionDigest(q)};}
 b.questions[0].solution.formulas[0].expression='<img src=x onerror="window.INJECTED=true">';b.learningResourceIntegrity.bindings.Q.runtimeSha256=R.runtimeQuestionDigest(b.questions[0]);
 await page.evaluate(b=>{window.TESTBANK=b;window.seen=[];window.paint=kind=>{const el=document.getElementById('resources');el.replaceChildren();RoboticsLearningResourceUI.render(kind,el,TESTBANK,{onQuestion:id=>seen.push(id),onSource:c=>seen.push(c.slideId)});};paint('formulas');},b);
 assert(await page.locator('article.tool-record').count()===20,'Page size is not bounded to 20');report.checks.push('bounded initial formula pagination');
 assert(await page.locator('article img').count()===0&&!await page.evaluate(()=>window.INJECTED),'Formula content was interpreted as HTML');report.checks.push('exact formula text is not interpreted as HTML');
 await page.getByRole('button',{name:'Next resource page',exact:true}).click();assert(await page.locator('article.tool-record').count()===20,'Second page size');await page.getByRole('button',{name:'Next resource page',exact:true}).click();assert(await page.locator('article.tool-record').count()===5,'Final page size');report.checks.push('next/previous resource page controls');
 await page.getByLabel('Learning tool week',{exact:true}).selectOption('1');assert(await page.locator('article.tool-record').count()===5,'Week filter');await page.getByLabel('Learning tool week',{exact:true}).selectOption('');await page.getByLabel('Search learning resources').fill('Example 44');await page.waitForTimeout(230);assert(await page.locator('article.tool-record').count()===1,'Search exact context');report.checks.push('week and full-context search filtering');
 await page.locator('summary').first().click();await page.waitForTimeout(30);await page.getByRole('button',{name:/Q44 · open approved question/}).click();await page.getByRole('button',{name:'Source S · PDF page 1',exact:true}).click();assert(JSON.stringify(await page.evaluate(()=>seen))===JSON.stringify(['Q44','S1']),'Source/question callbacks');report.checks.push('lazy context and exact source/question links');
 await page.evaluate(()=>paint('confusion'));assert((await page.locator('body').innerText()).includes('Tempting alternatives · incorrect'),'Incorrect alternative not labeled');report.checks.push('comparison labels never describe wrong options as facts');
 for(const width of [1200,390]){await page.setViewportSize({width,height:900});const dims=await page.evaluate(()=>({w:document.documentElement.clientWidth,s:document.documentElement.scrollWidth}));assert(dims.s<=dims.w+2,'Horizontal overflow at '+width);const screenshot=path.join(root,'audits/screenshots/learning-resources-author-'+width+'.png');fs.mkdirSync(path.dirname(screenshot),{recursive:true});await page.screenshot({path:screenshot,fullPage:false});report.screenshots.push(screenshot);}
 report.checks.push('desktop and mobile component layout');
 await page.evaluate(()=>{TESTBANK.learningResourceIntegrity.policyEligible=false;paint('formulas');});assert(await page.locator('article.tool-record').count()===0,'Inactive policy exposed content');report.checks.push('policy deactivation hides projected cards');
 assert(report.errors.length===0,'Browser errors');report.checks.push('no JavaScript runtime errors');await browser.close();report.status='passed';
})().catch(e=>{report.status=report.checks.length===0&&/Operation not permitted/.test(e.message)?'blocked':'failed';report.errors.push(e.stack);process.exitCode=1;}).finally(()=>{fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));});
