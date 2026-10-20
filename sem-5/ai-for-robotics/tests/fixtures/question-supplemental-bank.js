'use strict';
// Synthetic in-memory text-input fixture, not a course approval.
const F=require('./question-visual-bank.js'),R=require('../../app/learning-resources.js');
function rebind(f){const x=f.bank.questionVisuals,r=x.records[0],s=x.supplementalInputs[0],review=x.reviews[0];
 x.supplementalBindings={[s.id]:{id:s.id,inputSha256:R.sha256(R.stableJSON(s)),rawJSON:R.stableJSON(s)}};
 review.visualSha256=R.sha256(R.stableJSON(r));review.reviewedSupplementalInputIds=r.supplementalInputIds.slice();review.supplementalInputHashes={[s.id]:x.supplementalBindings[s.id].inputSha256};review.supplementalSourceHashes={[s.sourceArtifact]:s.sourceSha256,[s.notebookArtifact]:s.notebookSha256};
 const rb={id:review.id,rawJSON:R.stableJSON(review),reviewSha256:R.sha256(R.stableJSON(review))};x.reviewBindings={[review.id]:rb};x.bindings.Q={...x.bindings.Q,recordSha256:review.visualSha256,recordRawJSON:R.stableJSON(r),assetIds:[],supplementalInputIds:r.supplementalInputIds.slice(),reviewBindings:[{id:review.id,reviewSha256:rb.reviewSha256}]};return f;
}
function fixture(output=false){const f=F.fixture(),x=f.bank.questionVisuals,name='sources/supplemental/fixture.ipynb',notebook={cells:[{cell_type:'code',metadata:{id:'colab-cell'},source:['x = 2\n','print(x)\n'],outputs:[{output_type:'stream',text:['2\n']}]}]},rawText=JSON.stringify(notebook),sha=R.sha256(rawText),text=output?'2\n':'x = 2\nprint(x)\n';
 const s={id:'text-input',authorId:'supplemental-author',kind:output?'verbatim_saved_output':'verbatim_source_code',language:output?'text':'python',sourceArtifact:name,sourceSha256:sha,lineStart:null,lineEnd:null,notebookArtifact:name,notebookSha256:sha,cellIndexZeroBased:0,cellId:'colab-cell',cellLineStart:1,cellLineEnd:output?1:2,sourceUrl:null,upstreamCommit:null,upstreamGitBlobSha:null,upstreamPinStatus:'local_only',notebookRepresentation:'verbatim',text,textSha256:R.sha256(text),transformation:'Exact synthetic text fixture; never executed.'};
 if(output){s.notebookOutputIndex=0;s.notebookOutputField='text';x.records[0].savedOutputUse='explicit_output_reading';x.reviews[0].savedOutputUse='explicit_output_reading';x.reviews[0].checks.savedOutputIsQuestionStimulus=true;}
 x.records[0].assetIds=[];x.records[0].supplementalInputIds=[s.id];x.assets=[];x.assetBindings={};x.reviews[0].assetHashes={};x.reviews[0].assetMetadataHashes={};x.reviews[0].reviewedAssetIds=[];x.supplementalInputs=[s];x.supplementalArtifacts={[name]:{sha256:sha,rawText}};f.assets={};f.bank.assets=[];return rebind(f);
}
module.exports={fixture,rebind};
