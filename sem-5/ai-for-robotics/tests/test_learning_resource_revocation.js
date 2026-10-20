'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const R=require('../app/learning-resources.js'),E=require('../app/learning-tools.js');
const {fixture,approveTool}=require('./fixtures/learning-resource-bank.js');
const clone=x=>JSON.parse(JSON.stringify(x));
let serial=0;
function course(){const b=fixture(),r={id:'revocation.family.'+(++serial),version:1,status:'verified',generatorKind:'q-learning-update',generatorVersion:'1.0.0'};approveTool(b,r);b.learningTools={numericalFamilies:[r]};assert.deepEqual(E.registerBankNumericalFamilies(b).registered,[r.id]);return {b,r,v:E.generateVariant(r.id,{seed:'revocation-fixed'})};}
const refresh=b=>b.learningResourceIntegrity.bindings.Q.runtimeSha256=R.runtimeQuestionDigest(b.questions[0]);
test('literal key, reviewer answer and stable option IDs must be nonempty, unique and valid',()=>{
 const cases=[(q,r)=>{q.correctOptionIds=[];r.independentAnswerOptionIds=[];},(q,r)=>{q.correctOptionIds=['missing'];r.independentAnswerOptionIds=['missing'];},(q,r)=>r.independentAnswerOptionIds=['o1','o1'],(q,r)=>q.correctOptionIds=['o1','o1'],(q,r)=>r.independentAnswerOptionIds=[],(q,r)=>q.options[1].id='o1',(q,r)=>q.options[0].id=' ',(q,r)=>q.selectionMode='unknown',(q,r)=>{q.correctOptionIds=['o1','o2'];r.independentAnswerOptionIds=['o1','o2'];}];
 for(const change of cases){const b=fixture();change(b.questions[0],b.reviews[0]);refresh(b);assert.equal(R.eligibleQuestions(b).questions.length,0);}
 const b=fixture();b.questions[0].selectionMode='multi';b.questions[0].correctOptionIds=['o1','o2'];b.reviews[0].independentAnswerOptionIds=['o2','o1'];refresh(b);assert.equal(R.eligibleQuestions(b).questions.length,1);
});
test('blank and author-equivalent reviewer identities cannot activate any gate',()=>{
 for(const who of ['', '   ',null,17,' author ']){const b=fixture();b.reviews[0].reviewerId=who;assert.equal(R.eligibleQuestions(b).questions.length,0);}
 const b=fixture();b.learningResourceIntegrity.policyReviews[0].reviewerId=' ';assert.equal(R.policyAllowed(b),false);
 const {b:x,r}=course();x.learningResourceIntegrity.toolReviews[0].reviewerId=' ';assert.equal(R.toolRecordAllowed(r,x),false);
});
test('question citations and tool sourceRefs share one-based bounded-page and disposition checks',()=>{
 for(const bad of [0,-1,1.5,true,null,'1',4]){const b=fixture(),q=b.questions[0];q.citations[0].physicalPage=bad;b.slides[0].physicalPage=bad;refresh(b);assert.equal(R.eligibleQuestions(b).questions.length,0);}
 for(const field of ['unknown','unreviewed','unresolved','']){const b=fixture();b.slides[0].disposition=field;assert.equal(R.eligibleQuestions(b).questions.length,0);}
 for(const count of [0,null,'3',true,2.5]){const b=fixture();b.sources[0].pageCount=count;assert.equal(R.eligibleQuestions(b).questions.length,0);}
 const {b,r}=course();r.sourceRefs[0].physicalPage=0;b.learningResourceIntegrity.toolBindings[r.id].runtimeSha256=R.runtimeQuestionDigest(r);assert.equal(R.toolRecordAllowed(r,b),false);
});
test('bound generator implementation must agree with approved policy code',()=>{const {b,r}=course();r.implementationFiles[0].sha256='f'.repeat(64);b.learningResourceIntegrity.toolBindings[r.id].runtimeSha256=R.runtimeQuestionDigest(r);assert.equal(R.toolRecordAllowed(r,b),false);});
test('record removal and bank switch revoke listings, generation and saved restoration',()=>{
 const {b,r,v}=course();b.learningTools.numericalFamilies=[];assert.ok(!E.listNumericalFamilies().some(f=>f.id===r.id));assert.throws(()=>E.generateVariant(r.id,{seed:1}),{code:'STALE_RESOURCE'});assert.throws(()=>E.restoreVariant(v),{code:'STALE_RESOURCE'});
 E.registerBankNumericalFamilies(b);assert.throws(()=>E.generateVariant(r.id,{seed:1}),/Unknown/);
 const next=course();E.registerBankNumericalFamilies({learningTools:{numericalFamilies:[]}});assert.ok(!E.listNumericalFamilies().some(f=>f.id===next.r.id));assert.throws(()=>E.restoreVariant(next.v),{code:'VERSION_MISMATCH'});
 assert.ok(E.listNumericalFamilies({includeSynthetic:true}).some(f=>f.provenance.synthetic));
});
test('in-place source, question, policy, family or review changes revoke without re-registration',()=>{
 const changes=[b=>b.reviews=[],b=>b.sources[0].sha256='f'.repeat(64),b=>b.questions[0].stem+=' changed',b=>b.learningResourceIntegrity.policyReviews=[],b=>b.learningResourceIntegrity.policyEligible=false,b=>b.learningTools.numericalFamilies[0].title='changed',b=>b.learningResourceIntegrity.toolReviews=[]];
 for(const change of changes){const {b,r,v}=course();change(b);assert.ok(!E.listNumericalFamilies().some(f=>f.id===r.id));assert.throws(()=>E.generateVariant(r.id,{seed:1}),{code:'STALE_RESOURCE'});assert.throws(()=>E.restoreVariant(v),{code:'STALE_RESOURCE'});}
});
test('new approval cannot silently re-bless a cached old resource binding',()=>{
 const {b,r,v}=course();r.version=2;approveTool(b,r);E.registerBankNumericalFamilies(b);assert.throws(()=>E.restoreVariant(v),{code:'STALE_RESOURCE'});assert.equal(E.generateVariant(r.id,{seed:1}).provenance.resourceBinding.toolVersion,2);assert.notEqual(E.generateVariant(r.id,{seed:v.seed,parameters:v.parameters}).id,v.id);
});
test('all supplemental, experiment, diagram and original solution context is detached and exact',()=>{
 const b=fixture(),q=b.questions[0];Object.assign(q,{supplementalProvenance:{url:'https://example.invalid/notebook',sha256:'a'.repeat(64),cell:8},externalEvidence:[{qualification:'scope'}],primaryImplementationEvidence:{library:'pinned'},experimentProvenance:{executed:false,reason:'blocked'},diagramSourceSlideIds:['S1'],futureContextField:{assumption:'must survive'},conflictResolution:{basis:'qualified source conflict'}});q.citations[0].role='conflict';q.solution.steps=['full working'];refresh(b);
 for(const group of Object.values(R.project(b)).filter(Array.isArray).filter(a=>a[0]?.contexts))for(const card of group){const c=card.contexts[0];for(const k of ['supplementalProvenance','externalEvidence','primaryImplementationEvidence','experimentProvenance','diagramSourceSlideIds','futureContextField','solution','conflictResolution'])assert.deepEqual(c[k],q[k]);c.supplementalProvenance.cell=999;assert.equal(q.supplementalProvenance.cell,8);}
});
// Inert structural DOM only: this is not a browser, layout test or network workaround.
class N{constructor(tag,attrs={},children=[]){this.tag=tag;this.attrs=attrs;this.children=children;this.textContent=attrs.text||'';}append(...xs){this.children.push(...xs);}replaceChildren(...xs){this.children=xs;}setAttribute(k,v){this.attrs[k]=v;}addEventListener(k,v){(this.listeners||(this.listeners={}))[k]=v;}}
const flat=n=>[n,...n.children.filter(x=>x&&typeof x==='object').flatMap(flat)];
function renderer(variant){let saves=0,exports=0;const box=new N('root'),s={state:{variant},progress:{},C:{clone,uid:()=>String(Date.now())},save:()=>saves++,download:()=>exports++,toast:()=>{},el:(tag,a={},c=[])=>new N(tag,a,c),button:(text,handler,a={})=>Object.assign(new N('button',{...a,text}),{handler}),listBlock:(label,value)=>new N('list',{text:label+' '+JSON.stringify(value)}),textBlock:(label,value)=>new N('text',{text:label+' '+value}),toolLinks:()=>new N('links')};const text=fs.readFileSync(require.resolve('../app/app.js'),'utf8'),start=text.indexOf('  function renderVariant('),end=text.indexOf('  function exportQuestions(',start);vm.runInNewContext(text.slice(start,end)+';this.renderVariant=renderVariant;',s);return {s,box,render:()=>s.renderVariant(box,E),counts:()=>({saves,exports})};}
test('cached renderer refuses revoked variants before display/persistence and rechecks interactions',()=>{
 const {b,v}=course(),r=renderer(v);r.render();assert.equal(r.counts().saves,1);const buttons=flat(r.box).filter(n=>n.tag==='button'),answer=buttons.find(n=>n.attrs.class==='option'),exportButton=buttons.find(n=>n.attrs.text==='Save reproducible variant JSON');assert.ok(answer&&exportButton);
 b.learningResourceIntegrity.toolReviews=[];answer.handler();exportButton.handler();assert.deepEqual(r.counts(),{saves:1,exports:0});assert.equal(r.s.progress.variants[v.id].answers.length,0);assert.match(r.box.children[0].textContent,/historical/);
 const initial=renderer(v);initial.render();assert.deepEqual(initial.counts(),{saves:0,exports:0});assert.equal(flat(initial.box).some(n=>n.tag==='button'),false);
});
test('projection UI renders exact notebook and conflict context as inert text',()=>{
 const b=fixture(),q=b.questions[0];q.supplementalProvenance={url:'https://example.invalid/exact-notebook',sha256:'e'.repeat(64),cell:8};q.experimentProvenance={executed:false};q.diagramSourceSlideIds=['S1'];q.conflictResolution={basis:'<script>not markup</script>'};refresh(b);
 const sandbox={RoboticsLearningResources:R,document:{createElement:t=>new N(t)},setTimeout,clearTimeout};sandbox.globalThis=sandbox;vm.runInNewContext(fs.readFileSync(require.resolve('../app/learning-resource-ui.js'),'utf8'),sandbox);const box=new N('root');sandbox.RoboticsLearningResourceUI.render('formulas',box,b,{onQuestion(){},onSource(){}});
 for(let pass=0;pass<3;pass++)for(const d of flat(box).filter(n=>n.tag==='details')){d.open=true;d.listeners.toggle();}
 const content=flat(box).map(n=>n.textContent).join('\n');assert.match(content,/exact-notebook/);assert.match(content,/"cell": 8/);assert.match(content,/executed/);assert.match(content,/not markup/);assert.equal(flat(box).some(n=>n.tag==='script'),false);
});
test('cached verified algorithm trace is rejected after current record removal',()=>{
 const b=fixture(),r={id:'trace-test',version:1,status:'verified',config:{start:'A'}};approveTool(b,r);b.learningTools={algorithmVisualizations:[r]};const trace={provenance:{synthetic:false,status:'verified',resourceBinding:{toolId:r.id,toolRuntimeSha256:R.runtimeQuestionDigest(r),policyRuntimeSha256:b.learningResourceIntegrity.runtimePolicySha256,toolSha256:b.learningResourceIntegrity.toolBindings[r.id].sha256}},steps:[]};
 b.learningTools.algorithmVisualizations=[];const text=fs.readFileSync(require.resolve('../app/app.js'),'utf8'),start=text.indexOf('  function renderTrace('),end=text.indexOf('  function renderNumerical(',start),sandbox={state:{algorithmTrace:trace},rawBank:b,window:{RoboticsLearningResources:R},el:(tag,a={})=>new N(tag,a)};vm.runInNewContext(text.slice(start,end)+';this.renderTrace=renderTrace;',sandbox);const box=new N('root');sandbox.renderTrace(box);assert.match(box.children[0].textContent,/historical trace/);
});
