'use strict';
// Synthetic in-memory gate fixture only. Never emitted into canonical course data.
const F=require('./learning-resource-bank.js'),R=require('../../app/learning-resources.js');
const clone=x=>JSON.parse(JSON.stringify(x));
function fixture(required=true){
 const bank=F.fixture(),q=bank.questions[0],h=bank.learningResourceIntegrity.bindings.Q.questionSha256;
 const data='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aOioAAAAASUVORK5CYII=',sha=R.sha256Bytes(Uint8Array.from(Buffer.from(data,'base64')));
 const a={id:'input',path:'assets/question-visuals/fixture.png',mimeType:'image/png',sha256:sha,width:1,height:1,sourceId:'S',sourceSha256:'a'.repeat(64),physicalPage:1,slideId:'S1',cropRectangle:[0,0,1,1],renderDpi:72,alt:'Synthetic one-pixel input for software gate tests'};
 const record={id:'V',version:1,authorId:'visual-author',questionId:'Q',questionVersion:1,questionSha256:h,dependencyStatus:required?'required':'self_contained',reason:'Synthetic gate fixture, not course evidence.',assetIds:required?['input']:[],requiredInputs:required?['Synthetic input']:[],sourceRefs:clone(q.citations)};
 const review={id:'VR',visualId:'V',visualVersion:1,visualSha256:R.sha256(R.stableJSON(record)),reviewerId:'independent-visual-reviewer',decision:'verified',questionId:'Q',questionVersion:1,questionSha256:h,sourceVersions:{S:'a'.repeat(64)},assetHashes:required?{input:sha}:{},assetMetadataHashes:required?{input:R.sha256(R.stableJSON(a))}:{},reviewedAssetIds:record.assetIds.slice(),displayRole:'question_input',checks:Object.fromEntries(R.VISUAL_CHECKS.map(k=>[k,true])),reviewedAt:'2026-10-20T00:00:00Z'};
 const rb={id:'VR',reviewSha256:R.sha256(R.stableJSON(review)),rawJSON:R.stableJSON(review)};
 bank.questionVisuals={formatVersion:1,manifest:{schemaVersion:'1.0.0',authorId:'visual-author',sourceVersions:{S:'a'.repeat(64)}},records:[record],assets:required?[a]:[],reviews:[review],reviewBindings:{VR:rb},assetBindings:required?{input:{id:'input',assetSha256:sha,assetMetadataSha256:R.sha256(R.stableJSON(a)),rawJSON:R.stableJSON(a)}}:{},bindings:{Q:{recordId:'V',recordVersion:1,recordSha256:review.visualSha256,recordRawJSON:R.stableJSON(record),questionVersion:1,questionSha256:h,dependencyStatus:record.dependencyStatus,assetIds:record.assetIds.slice(),requiredInputs:record.requiredInputs.slice(),reviewBindings:[{id:'VR',reviewSha256:rb.reviewSha256}]}},diagnostics:[]};
 bank.assets=required?[{...clone(a),kind:'diagram'}]:[];
 return {bank,assets:required?{input:{...clone(a),kind:'diagram',data}}:{}};
}
module.exports={fixture,clone};
