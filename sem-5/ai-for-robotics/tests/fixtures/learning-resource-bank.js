'use strict';
// Explicitly synthetic in-memory software fixtures. Never bundled as course data.
const R=require('../../app/learning-resources.js');
function fixture(){
 const h='a'.repeat(64),qh='b'.repeat(64),q={id:'Q',version:1,status:'verified',authorId:'author',reviewIds:['R'],week:1,lectureId:'L01',topic:'Demo',subtopic:'Bayes versus likelihood',stem:'Which distinction between prior and posterior is correct?',origin:'generated',selectionMode:'single',conceptIds:['C'],assumptions:['P(E)>0'],options:[{id:'o1',text:'Prior precedes the evidence.'},{id:'o2',text:'Prior always follows the evidence.'}],correctOptionIds:['o1'],citations:[{slideId:'S1',sourceId:'S',sourceSha256:h,physicalPage:1,role:'explicit',locator:'test only'}],solution:{justification:'The labels differ by conditioning.',formulas:[{expression:'P(H|E)=P(E|H)P(H)/P(E)',variables:{H:'hypothesis'},units:{P:'dimensionless'},assumptions:['P(E)>0']}],misconceptions:['Reversing prior and posterior.'],examTraps:['Ignoring evidence.'],optionExplanations:{o1:'Matches the definition.',o2:'Reverses the definition.'}}};
 const policy={id:'extractor',version:R.VERSION,authorId:'extractor-author'};const b={questions:[q],reviews:[{id:'R',questionId:'Q',questionVersion:1,questionSha256:qh,reviewerId:'reviewer',decision:'verified',sourceVersions:{S:h},reviewedSlideIds:['S1'],independentAnswerOptionIds:['o1'],checks:Object.fromEntries(R.CHECKS.map(k=>[k,true]))}],sources:[{id:'S',sha256:h,retrievalStatus:'ready',pageCount:3}],slides:[{id:'S1',sourceId:'S',sourceSha256:h,physicalPage:1,visualInspection:{status:'complete'},disposition:'examinable'}]};
 b.learningResourceIntegrity={policy,policySha256:'c'.repeat(64),runtimePolicySha256:R.sha256(R.stableJSON(policy)),policyEligible:true,policyReviews:[{resourceId:'extractor',resourceVersion:R.VERSION,resourceSha256:'c'.repeat(64),reviewerId:'other-reviewer',decision:'verified',checks:Object.fromEntries(R.POLICY_CHECKS.map(k=>[k,true]))}],bindings:{Q:{questionVersion:1,questionSha256:qh,runtimeSha256:R.runtimeQuestionDigest(q)}}};return b;
}

function approveTool(bank,record){
 record.authorId='test-tool-author';record.version=record.version||1;
 record.implementationFiles=record.implementationFiles||[{path:'test-only-engine.js',sha256:'a'.repeat(64)}];
 bank.learningResourceIntegrity.policy.codeHashes={'test-only-engine.js':'a'.repeat(64)};
 bank.learningResourceIntegrity.runtimePolicySha256=R.sha256(R.stableJSON(bank.learningResourceIntegrity.policy));
 record.sourceRefs=JSON.parse(JSON.stringify(bank.questions[0].citations));
 record.questionIds=['Q'];record.questionBindings=[{questionId:'Q',questionVersion:1,questionSha256:bank.learningResourceIntegrity.bindings.Q.questionSha256}];
 const x=bank.learningResourceIntegrity;x.toolBindings=x.toolBindings||{};x.toolReviews=x.toolReviews||[];
 x.toolBindings[record.id]={version:record.version,sha256:'d'.repeat(64),runtimeSha256:R.runtimeQuestionDigest(record)};
 x.toolReviews.push({id:'tool-review-'+record.id,toolId:record.id,toolVersion:record.version,toolSha256:'d'.repeat(64),reviewerId:'test-tool-reviewer',decision:'verified',checks:Object.fromEntries(R.TOOL_CHECKS.map(k=>[k,true])),sourceVersions:{S:'a'.repeat(64)},reviewedSlideIds:['S1']});
 return record;
}
module.exports={fixture,approveTool};
