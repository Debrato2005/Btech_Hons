'use strict';
const fs=require('fs'),assert=require('assert/strict'),vm=require('vm'),R=require('../app/learning-resources.js');
const {fixture}=require('../tests/fixtures/learning-resource-bank.js');
// This fake DOM is an inert structural test. It is NOT a browser, layout engine, or permission-denial workaround.
class Node {constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.listeners={};this.textContent='';}append(...xs){this.children.push(...xs);}setAttribute(k,v){this.attributes[k]=v;}addEventListener(k,v){this.listeners[k]=v;}replaceChildren(...xs){this.children=xs;}}
const sandbox={RoboticsLearningResources:R,document:{createElement:t=>new Node(t)},setTimeout,clearTimeout};sandbox.globalThis=sandbox;
vm.runInNewContext(fs.readFileSync('app/learning-resource-ui.js','utf8'),sandbox);
const b=fixture();b.questions[0].stem='Which difference applies to <img src=x onerror=alert(1)>?';b.learningResourceIntegrity.bindings.Q.runtimeSha256=R.runtimeQuestionDigest(b.questions[0]);
let tests=0;const flat=n=>[n,...n.children.filter(x=>x&&typeof x==='object').flatMap(flat)];
for(const kind of ['formulas','confusion','traps']){
 const root=new Node('root');assert.equal(sandbox.RoboticsLearningResourceUI.render(kind,root,b,{onQuestion(){},onSource(){}}),true);tests++;
 for(const d of flat(root).filter(x=>x.tag==='details')){d.open=true;d.listeners.toggle();}
 const nodes=flat(root);assert.equal(nodes.some(n=>n.tag==='img'||n.tag==='script'),false);assert.equal(nodes.some(n=>String(n.textContent).includes('<img src=x')),true);tests+=2;
}
const stale=fixture();stale.learningResourceIntegrity.policyEligible=false;const root=new Node('root');assert.equal(sandbox.RoboticsLearningResourceUI.render('formulas',root,stale,{}),false);assert.equal(flat(root).some(n=>n.tag==='article'),false);tests+=2;
const actual=JSON.parse(fs.readFileSync('data/bank.json'));actual.learningResourceIntegrity.policyEligible=true;const x=actual.learningResourceIntegrity;
x.policyReviews=[{id:'SYNTHETIC-IN-MEMORY-CENSUS-NOT-APPROVAL',resourceId:x.policy.id,resourceVersion:x.policy.version,resourceSha256:x.policySha256,reviewerId:'synthetic-census',decision:'verified',checks:Object.fromEntries(R.POLICY_CHECKS.map(k=>[k,true]))}];
const projected=R.project(actual);let formulas=0,traps=0,comparisons=0;
const byId=new Map(actual.questions.map(q=>[q.id,q]));
for(const c of projected.formulas)for(const origin of c.formulaOrigins){assert.deepEqual(c.exactFormula,byId.get(origin.questionId).solution.formulas[origin.index]);formulas++;}
for(const c of projected.traps){assert.deepEqual(c.explicitTraps,byId.get(c.questionIds[0]).solution.examTraps||[]);assert.deepEqual(c.misconceptions,byId.get(c.questionIds[0]).solution.misconceptions||[]);traps++;}
for(const c of projected.confusionPairs){const q=byId.get(c.questionIds[0]);assert.deepEqual(c.correctAlternatives,q.options.filter(o=>q.correctOptionIds.includes(o.id)));assert.deepEqual(c.incorrectAlternatives,q.options.filter(o=>!q.correctOptionIds.includes(o.id)));comparisons++;}
const omissions=[];for(const group of [projected.formulas,projected.confusionPairs,projected.traps])for(const card of group)for(const c of card.contexts){const q=byId.get(c.questionId);for(const k of ['supplementalProvenance','externalEvidence','primaryImplementationEvidence','experimentProvenance','diagramSourceSlideIds'])if(q[k]&&!Object.hasOwn(c,k))omissions.push({questionId:q.id,field:k,cardId:card.id});}
const out={at:new Date().toISOString(),runtime:'Inert Node structural DOM, not actual browser QA',structuralAssertionsPassed:tests,exactFormulaOriginsMatched:formulas,exactTrapRecordsMatched:traps,exactComparisonRecordsMatched:comparisons,projectedQuestionCount:projected.eligibleQuestionCount,diagnostics:projected.diagnostics.length,contextOmissions:omissions};
fs.writeFileSync('audits/learning-resources-v1-contracts-projection-checks.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({...out,contextOmissions:omissions.length}));
