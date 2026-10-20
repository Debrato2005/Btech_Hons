'use strict';
// Independent review harness. Synthetic gate probes stay in memory, not in course data.
const fs=require('fs'),R=require('../app/learning-resources.js'),T=require('../app/learning-tools.js');
const {fixture,approveTool}=require('../tests/fixtures/learning-resource-bank.js');
const packet=JSON.parse(fs.readFileSync('audits/blind-learning-resources-v1.json')),author=JSON.parse(fs.readFileSync('data/learning-tools-course.json')).learningTools,bank=JSON.parse(fs.readFileSync('data/bank.json'));
const out={runtime:'Node/default environment, no browser launch',comparison:[],traces:[],generated:[],failClosedProbes:[]};
bank.learningTools=author;T.registerBankNumericalFamilies(bank,{includeDrafts:true});
for(const r of packet.resources){
 if(r.examples){
  for(const e of r.examples){const v=T.generateVariant(r.id,{seed:e.seed,parameters:e.parameters});out.comparison.push({exampleId:e.exampleId,value:v.answer,precision:v.precision,units:v.units,steps:v.steps,formula:v.formula,variableDefinitions:v.variableDefinitions,options:v.options});}
  for(let i=0;i<1000;i++){const v=T.generateVariant(r.id,{seed:'contracts-independent-'+i});const restored=T.restoreVariant(v);if(JSON.stringify(v.options)!==JSON.stringify(restored.options))throw Error('Replay mismatch '+r.id);out.generated.push({kind:r.generatorKind,parameters:v.parameters,value:v.answer,precision:v.precision,options:v.options.map(o=>o.roundedValue)});}
 }else if(r.graph)out.traces.push({resourceId:r.id,trace:T.searchTrace(r.graph,r.config)});
 else out.traces.push({resourceId:r.id,trace:T.qLearningTrace(r.qLearningConfig)});
}
const clone=x=>JSON.parse(JSON.stringify(x));
function probe(name,change,expected){let b=fixture();change(b);let result;try{result=R.eligibleQuestions(b).questions.length;}catch(e){result='throws:'+e.message;}out.failClosedProbes.push({name,expected,actual:result,passed:result===expected});}
for(const [name,change] of [
 ['question mutation',b=>b.questions[0].stem+='changed'],['review removal',b=>b.reviews=[]],['revision author self-review',b=>b.questions[0].revisionAuthors=['reviewer']],['source hash changed',b=>b.sources[0].sha256='0'.repeat(64)],['page inspection missing',b=>b.slides[0].visualInspection.status='pending'],['current flagged review',b=>b.reviews.push({...b.reviews[0],decision:'flagged'})],['synthetic question',b=>b.questions[0].synthetic=true],['failed criterion',b=>b.reviews[0].checks.difficulty=false]
])probe(name,change,0);
probe('empty literal keys cannot project',b=>{b.questions[0].correctOptionIds=[];b.reviews[0].independentAnswerOptionIds=[];b.learningResourceIntegrity.bindings.Q.runtimeSha256=R.runtimeQuestionDigest(b.questions[0]);},0);
probe('nonexistent literal option cannot project',b=>{b.questions[0].correctOptionIds=['missing'];b.reviews[0].independentAnswerOptionIds=['missing'];b.learningResourceIntegrity.bindings.Q.runtimeSha256=R.runtimeQuestionDigest(b.questions[0]);},0);
probe('unknown page disposition cannot project',b=>b.slides[0].disposition='not-a-valid-disposition',0);
let b=fixture(),r={id:'synthetic-regression.removal',version:1,status:'verified',generatorKind:'q-learning-update',generatorVersion:'1.0.0'};approveTool(b,r);b.learningTools={numericalFamilies:[r]};T.registerBankNumericalFamilies(b);b.learningTools.numericalFamilies=[];T.registerBankNumericalFamilies(b);out.failClosedProbes.push({name:'Removed bank family evicts previously verified registration',expected:false,actual:T.listNumericalFamilies().some(f=>f.id===r.id),passed:!T.listNumericalFamilies().some(f=>f.id===r.id)});
let c=fixture();c.questions[0].supplementalProvenance={path:'synthetic-source-only',sha256:'f'.repeat(64),cell:8};c.questions[0].primaryImplementationEvidence={version:'synthetic'};c.learningResourceIntegrity.bindings.Q.runtimeSha256=R.runtimeQuestionDigest(c.questions[0]);const ctx=R.project(c).formulas[0].contexts[0];out.failClosedProbes.push({name:'Supplemental provenance retained in projected context',expected:true,actual:JSON.stringify(ctx).includes('synthetic-source-only'),passed:JSON.stringify(ctx).includes('synthetic-source-only')});
fs.writeFileSync('/tmp/resource-review/independent-node-results.json',JSON.stringify(out));
console.log(JSON.stringify({examples:out.comparison.length,traces:out.traces.length,generated:out.generated.length,probes:out.failClosedProbes},null,2));
