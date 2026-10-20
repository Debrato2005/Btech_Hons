/* Exact, context-preserving views of independently approved question evidence.
 * This author-written extractor is inactive until its code policy is separately
 * approved. Projections inherit question evidence; they are not new fact reviews.
 */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.RoboticsLearningResources=api;}(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='1.0.4';
const CHECKS=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication'];
const POLICY_CHECKS=['exactProjection','contextPreservation','sourceAndReviewBinding','failClosedMutationTests','runtimeTests'];
const clone=x=>JSON.parse(JSON.stringify(x));
function stableJSON(x){
 if(x===null||typeof x!=='object'){if(typeof x==='number'&&!Number.isFinite(x))throw Error('Nonfinite JSON');if(x===undefined)throw Error('Undefined JSON');return JSON.stringify(x);}
 if(Array.isArray(x))return '['+x.map(stableJSON).join(',')+']';
 return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+stableJSON(x[k])).join(',')+'}';
}
// SHA-256, over TextEncoder UTF-8 bytes. Cross-tested against Node crypto.
function sha256(text){return sha256Bytes(new TextEncoder().encode(text));}
function sha256Bytes(bytes){
 if(!(bytes instanceof Uint8Array))throw Error('SHA-256 bytes require Uint8Array');
 const length=bytes.length,total=Math.ceil((length+9)/64)*64,padded=new Uint8Array(total);padded.set(bytes);padded[length]=128;
 const dv=new DataView(padded.buffer);dv.setUint32(total-8,Math.floor(length/0x20000000));dv.setUint32(total-4,(length*8)>>>0);
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 const H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],W=new Uint32Array(64),rr=(v,n)=>(v>>>n)|(v<<(32-n));
 for(let off=0;off<total;off+=64){for(let i=0;i<16;i++)W[i]=dv.getUint32(off+i*4);for(let i=16;i<64;i++){const a=W[i-15],b=W[i-2];W[i]=(W[i-16]+(rr(a,7)^rr(a,18)^(a>>>3))+W[i-7]+(rr(b,17)^rr(b,19)^(b>>>10)))>>>0;}
 let [a,b,c,d,e,f,g,h]=H;for(let i=0;i<64;i++){const t1=(h+(rr(e,6)^rr(e,11)^rr(e,25))+((e&f)^(~e&g))+K[i]+W[i])>>>0,t2=((rr(a,2)^rr(a,13)^rr(a,22))+((a&b)^(a&c)^(b&c)))>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;}[a,b,c,d,e,f,g,h].forEach((v,i)=>H[i]=(H[i]+v)>>>0);}
 return H.map(v=>v.toString(16).padStart(8,'0')).join('');
}
function runtimeQuestionDigest(q){const copy={...q};delete copy.status;delete copy.reviewIds;return sha256(stableJSON(copy));}
const nonblank=x=>typeof x==='string'&&x.trim().length>0;
function uniqueIds(a){return Array.isArray(a)&&a.length>0&&a.every(nonblank)&&new Set(a).size===a.length;}
function sameSet(a,b){return uniqueIds(a)&&uniqueIds(b)&&a.length===b.length&&a.every(x=>b.includes(x));}
function literalAnswerValid(q,answer){
 const options=q.options;if(!Array.isArray(options)||options.length<2||options.some(o=>!o||!nonblank(o.id)))return false;
 const ids=options.map(o=>o.id);
 return uniqueIds(ids)&&uniqueIds(answer)&&answer.every(id=>ids.includes(id))&&
  (q.selectionMode==='single'?answer.length===1:q.selectionMode==='multi');
}
function independentReviewer(id,record){return nonblank(id)&&![record.authorId,...(record.revisionAuthors||[])].some(a=>nonblank(a)&&a.trim()===id.trim());}
function sourceRefAllowed(c,sources,slides){
 if(!c||typeof c!=='object')return false;
 const s=sources.get(c.sourceId),p=slides.get(c.slideId);
 return !!(s&&p&&s.retrievalStatus==='ready'&&/^[a-f0-9]{64}$/.test(c.sourceSha256||'')&&s.sha256===c.sourceSha256&&p.sourceSha256===c.sourceSha256&&p.sourceId===c.sourceId&&Number.isInteger(s.pageCount)&&s.pageCount>0&&Number.isInteger(c.physicalPage)&&c.physicalPage>0&&c.physicalPage<=s.pageCount&&p.physicalPage===c.physicalPage&&p.visualInspection?.status==='complete'&&['examinable','repeated','excluded'].includes(p.disposition));
}
function policyAllowed(bank){
 const x=bank.learningResourceIntegrity;if(!x||x.policyEligible!==true||x.policy?.version!==VERSION)return false;
 if(x.runtimePolicySha256!==sha256(stableJSON(x.policy)))return false;
 const current=(x.policyReviews||[]).filter(r=>r.resourceId===x.policy.id&&r.resourceVersion===x.policy.version&&r.resourceSha256===x.policySha256);
 return !current.some(r=>['flagged','rejected'].includes(r.decision))&&current.some(r=>r.decision==='verified'&&independentReviewer(r.reviewerId,x.policy)&&POLICY_CHECKS.every(k=>r.checks?.[k]===true));
}
function eligibleQuestions(bank){
 const diagnostics=[];if(!policyAllowed(bank))return {questions:[],diagnostics:[{id:'projection-policy',reason:'No current independent extractor-policy approval.'}]};
 const sources=new Map((bank.sources||[]).map(x=>[x.id,x])),slides=new Map((bank.slides||[]).map(x=>[x.id,x])),reviews=new Map();
 for(const r of bank.reviews||[]){if(!reviews.has(r.questionId))reviews.set(r.questionId,[]);reviews.get(r.questionId).push(r);}
 const questions=[];
 for(const q of bank.questions||[]){
  if(q.status!=='verified')continue;
  const bind=bank.learningResourceIntegrity.bindings?.[q.id],reasons=[];
  if(q.synthetic||q.origin==='synthetic')reasons.push('Synthetic question is not course evidence.');
  if(!bind||bind.questionVersion!==q.version||bind.runtimeSha256!==runtimeQuestionDigest(q)||!/^[a-f0-9]{64}$/.test(bind.questionSha256||''))reasons.push('Missing or stale content binding.');
  const cs=Array.isArray(q.citations)?q.citations:[];if(!cs.length)reasons.push('No citations.');
  if(!literalAnswerValid(q,q.correctOptionIds))reasons.push('Invalid literal answer key.');
  for(const c of cs){if(!sourceRefAllowed(c,sources,slides))reasons.push('Source/page/inspection mismatch.');if(c?.role==='conflict'&&!q.conflictResolution)reasons.push('Unqualified source conflict.');}
  if(cs.some(c=>!c||typeof c!=='object')){diagnostics.push({id:q.id,reasons});continue;}
  const rs=(reviews.get(q.id)||[]).filter(r=>r.questionVersion===q.version&&r.questionSha256===bind?.questionSha256&&cs.every(c=>r.sourceVersions?.[c.sourceId]===c.sourceSha256)&&Object.entries(r.sourceVersions||{}).every(([id,h])=>sources.get(id)?.sha256===h));
  if(rs.some(r=>['flagged','rejected'].includes(r.decision)))reasons.push('Current independent dispute.');
  const accepted=rs.filter(r=>r.decision==='verified'&&independentReviewer(r.reviewerId,q)&&CHECKS.every(k=>r.checks?.[k]===true)&&literalAnswerValid(q,r.independentAnswerOptionIds)&&sameSet(r.independentAnswerOptionIds,q.correctOptionIds)&&cs.every(c=>r.reviewedSlideIds?.includes(c.slideId)));
  if(!accepted.length)reasons.push('No current full independent approval.');
  if(reasons.length)diagnostics.push({id:q.id,reasons});else questions.push({question:q,binding:bind,reviewIds:accepted.map(r=>r.id)});
 }
 return {questions,diagnostics};
}
const VISUAL_CHECKS=['inventoryCompleteness','requiredInputFidelity','legibility','noAnswerLeak','sourceLinkage'];
const visualByteCache=new Map();
function visualEligibility(bank,embeddedAssets,questionIds){
 const ids=Array.isArray(questionIds)?[...new Set(questionIds)]:[],out={ready:{},diagnostics:[]},x=bank.questionVisuals;
 const fail=(id,message)=>out.diagnostics.push({questionId:id,reasons:[message]});
 if(!x||x.formatVersion!==1||!nonblank(x.manifest?.authorId)){ids.forEach(id=>fail(id,'Missing reviewed question-input inventory.'));return out;}
 const uniqueList=a=>Array.isArray(a)&&a.every(nonblank)&&new Set(a).size===a.length;
 const bound=(raw,hash,value)=>{try{return typeof raw==='string'&&/^[a-f0-9]{64}$/.test(hash||'')&&sha256(raw)===hash&&stableJSON(JSON.parse(raw))===stableJSON(value);}catch{return false;}};
 const exact=(a,b)=>stableJSON(a)===stableJSON(b),sourceKey=r=>[r.sourceId,r.sourceSha256,r.slideId,r.physicalPage].join('|');
 if(['records','reviews','assets'].some(k=>!Array.isArray(x[k])||x[k].some(v=>!v||typeof v!=='object')||!uniqueList(x[k].map(v=>v.id)))){ids.forEach(id=>fail(id,'Malformed or duplicate visual inventory identifiers.'));return out;}
 const eligible=new Map(eligibleQuestions({...bank,questions:(bank.questions||[]).filter(q=>ids.includes(q.id))}).questions.map(e=>[e.question.id,e]));
 const sources=new Map((bank.sources||[]).map(s=>[s.id,s])),slides=new Map((bank.slides||[]).map(s=>[s.id,s])),amap=new Map(x.assets.map(a=>[a.id,a]));
 const assetCounts=new Map();for(const a of x.assets)assetCounts.set(a.sha256,(assetCounts.get(a.sha256)||0)+1);
 for(const id of ids){try{
  const e=eligible.get(id),b=x.bindings?.[id],records=x.records.filter(r=>r.questionId===id),r=records[0];
  if(!e||!e.reviewIds.some(rid=>e.question.reviewIds?.includes(rid)))throw Error('Current attached independent question/policy approval is missing or revoked.');
  if(records.length!==1||!b||!bound(b.recordRawJSON,b.recordSha256,r))throw Error('Missing or stale independently reviewed visual-dependency binding.');
  const q=e.question;
  if(r.id!==b.recordId||r.version!==b.recordVersion||!Number.isInteger(r.version)||r.version<1||!nonblank(r.authorId)||!nonblank(r.reason)||r.questionVersion!==q.version||r.questionSha256!==e.binding.questionSha256||b.questionVersion!==q.version||b.questionSha256!==e.binding.questionSha256||r.dependencyStatus!==b.dependencyStatus||!exact(r.assetIds,b.assetIds)||!exact(r.requiredInputs,b.requiredInputs))throw Error('Visual inventory does not bind the current question content/version.');
  if(!uniqueList(r.assetIds)||!uniqueList(r.requiredInputs)||!['required','self_contained'].includes(r.dependencyStatus)||(r.dependencyStatus==='required'?(!r.assetIds.length||!r.requiredInputs.length):(r.assetIds.length||r.requiredInputs.length)))throw Error('Malformed required-input classification.');
  const refs=r.sourceRefs;
  if(!Array.isArray(refs)||!refs.length||refs.some(c=>!sourceRefAllowed(c,sources,slides)||x.manifest.sourceVersions?.[c.sourceId]!==c.sourceSha256||!q.citations.some(k=>k.sourceId===c.sourceId&&k.sourceSha256===c.sourceSha256))||new Set(refs.map(sourceKey)).size!==refs.length)throw Error('Question-input source/page/inspection binding is missing or stale.');
  const visualAssets=[];
  for(const aid of r.assetIds){
   const a=amap.get(aid),ab=x.assetBindings?.[aid],canonical=(bank.assets||[]).filter(v=>v.id===aid),embedded=embeddedAssets?.[aid];
   if(!a||!ab||ab.id!==aid||ab.assetSha256!==a.sha256||!bound(ab.rawJSON,ab.assetMetadataSha256,a)||assetCounts.get(a.sha256)!==1)throw Error('Missing, duplicate or stale visual asset metadata: '+aid);
   const projected={...a,kind:'diagram'};
   if(canonical.length!==1||!exact(canonical[0],projected)||!embedded||!exact(Object.fromEntries(Object.entries(embedded).filter(([k])=>k!=='data')),projected))throw Error('Embedded visual metadata differs from the approved crop: '+aid);
   const rect=a.cropRectangle;
   if(a.mimeType!=='image/png'||!/^[a-f0-9]{64}$/.test(a.sha256||'')||!sourceRefAllowed(a,sources,slides)||!refs.some(c=>sourceKey(c)===sourceKey(a))||!nonblank(a.alt)||!/^assets\/question-visuals\/[^:]+\.png$/.test(a.path||'')||a.path.split('/').includes('..')||!Number.isInteger(a.width)||a.width<1||!Number.isInteger(a.height)||a.height<1||!Array.isArray(rect)||rect.length!==4||!rect.every(Number.isFinite)||!(0<=rect[0]&&rect[0]<rect[2]&&0<=rect[1]&&rect[1]<rect[3])||!Number.isFinite(a.renderDpi)||a.renderDpi<=0)throw Error('Invalid visual crop/source metadata: '+aid);
   const encoded=embedded.data;
   if(typeof encoded!=='string'||!encoded.length||encoded.length%4!==0||!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(encoded))throw Error('Missing or malformed embedded visual pixels: '+aid);
   // Cache by immutable payload value AND expected hash, not by mutable asset ID.
   const previous=visualByteCache.get(aid);
   if(!previous||previous.encoded!==encoded||previous.sha!==a.sha256||previous.width!==a.width||previous.height!==a.height){
    const text=atob(encoded),bytes=Uint8Array.from(text,c=>c.charCodeAt(0));
    if(sha256Bytes(bytes)!==a.sha256)throw Error('Embedded visual pixels changed: '+aid);
    if(bytes.length<33||[137,80,78,71,13,10,26,10].some((v,i)=>bytes[i]!==v)||String.fromCharCode(...bytes.slice(12,16))!=='IHDR'||new DataView(bytes.buffer).getUint32(16)!==a.width||new DataView(bytes.buffer).getUint32(20)!==a.height)throw Error('Visual PNG dimensions/header differ from the approved metadata: '+aid);
    visualByteCache.set(aid,{encoded,sha:a.sha256,width:a.width,height:a.height});
   }
   visualAssets.push(a);
  }
  const current=x.reviews.filter(v=>v.visualId===r.id&&v.visualVersion===r.version&&v.visualSha256===b.recordSha256);
  if(current.some(v=>['flagged','rejected'].includes(v.decision)))throw Error('Current visual approval is disputed.');
  const accepted=current.filter(v=>{
   const rb=x.reviewBindings?.[v.id],linked=b.reviewBindings?.find(k=>k.id===v.id);
   return v.decision==='verified'&&independentReviewer(v.reviewerId,r)&&independentReviewer(v.reviewerId,x.manifest)&&VISUAL_CHECKS.every(k=>v.checks?.[k]===true)&&v.questionId===id&&v.questionVersion===q.version&&v.questionSha256===e.binding.questionSha256&&v.displayRole==='question_input'&&typeof v.reviewedAt==='string'&&Number.isFinite(Date.parse(v.reviewedAt))&&uniqueList(v.reviewedAssetIds)&&exact([...v.reviewedAssetIds].sort(),[...r.assetIds].sort())&&exact(v.assetHashes,Object.fromEntries(visualAssets.map(a=>[a.id,a.sha256])))&&exact(v.assetMetadataHashes,Object.fromEntries(visualAssets.map(a=>[a.id,x.assetBindings[a.id].assetMetadataSha256])))&&refs.every(c=>v.sourceVersions?.[c.sourceId]===c.sourceSha256)&&Object.entries(v.sourceVersions||{}).every(([sid,h])=>sources.get(sid)?.sha256===h)&&rb?.id===v.id&&linked?.reviewSha256===rb.reviewSha256&&bound(rb.rawJSON,rb.reviewSha256,v);
  });
  if(!accepted.length)throw Error('No current independent question-input visual approval; answer approval alone is insufficient.');
  const stamp={formatVersion:1,questionId:id,questionVersion:q.version,questionSha256:e.binding.questionSha256,recordId:r.id,recordVersion:r.version,recordSha256:b.recordSha256,dependencyStatus:r.dependencyStatus,reviewBindings:accepted.map(v=>({id:v.id,reviewSha256:x.reviewBindings[v.id].reviewSha256})).sort((a,b)=>a.id.localeCompare(b.id)),assetBindings:visualAssets.map(a=>({id:a.id,sha256:a.sha256,metadataSha256:x.assetBindings[a.id].assetMetadataSha256})).sort((a,b)=>a.id.localeCompare(b.id))};
  out.ready[id]={questionId:id,dependencyStatus:r.dependencyStatus,assets:visualAssets,requiredInputs:clone(r.requiredInputs),stamp};
 }catch(error){fail(id,error.message);}}
 return out;
}

function context(entry){
 // Retain every original field, including supplemental notebooks, experiments,
 // implementation versions and diagram provenance. Shared aliases refer to the
 // same detached clone, not a lossy list of currently known extension fields.
 const q=clone(entry.question);
 return {...q,questionId:q.id,questionVersion:q.version,questionSha256:entry.binding.questionSha256,originalReviewIds:q.reviewIds||[],reviewIds:clone(entry.reviewIds),correctOptions:q.options.filter(o=>q.correctOptionIds.includes(o.id)),justification:q.solution.justification,sourceRefs:q.citations,conflictResolution:q.conflictResolution||null,primaryEvidence:q.primaryEvidence||[]};
}
// A bounded study-order heuristic, not a claim about future exam likelihood.
// Every question retains its exact approved object; reuse provenance is separate.
function assignmentPriority(bank,{reuseOnly=false}={}){
 const reuseTargets=new Set((Array.isArray(bank.assignmentReuse?.links)?bank.assignmentReuse.links:[]).flatMap(l=>l?.reusedQuestionIds||[]));
 const eligible=eligibleQuestions(reuseOnly?{...bank,questions:(bank.questions||[]).filter(q=>reuseTargets.has(q.id))}:bank),byId=new Map(eligible.questions.map(e=>[e.question.id,e]));
 const sources=new Map((bank.sources||[]).map(s=>[s.id,s])),slides=new Map((bank.slides||[]).map(s=>[s.id,s]));
 const priority=new Map(),reuseLinks=[],diagnostics=[],mappingCounts=new Map(),itemCounts=new Map();
 const add=(id,reason,item,mappingId=null)=>{
  if(!priority.has(id))priority.set(id,{questionId:id,reasons:[],sourceItemIds:[],mappingIds:[]});
  const value=priority.get(id);if(!value.reasons.includes(reason))value.reasons.push(reason);
  if(item&&!value.sourceItemIds.includes(item))value.sourceItemIds.push(item);
  if(mappingId&&!value.mappingIds.includes(mappingId))value.mappingIds.push(mappingId);
 };
 for(const {question:q}of eligible.questions){
  if(!reuseOnly&&q.origin==='assignment_adapted'&&q.citations.some(c=>sources.get(c.sourceId)?.role==='assignment_solutions'))
   add(q.id,'Verified adaptation of a supplied assignment item',q.assignmentSourceItemId||null);
 }
 const boundObject=(binding,value,hashKey='reviewSha256',rawKey='rawJSON')=>{
  try{return typeof binding?.[rawKey]==='string'&&/^[a-f0-9]{64}$/.test(binding?.[hashKey]||'')&&sha256(binding[rawKey])===binding[hashKey]&&stableJSON(JSON.parse(binding[rawKey]))===stableJSON(value);}catch{return false;}
 };
 const candidates=bank.assignmentReuse?.formatVersion===1?bank.assignmentReuse.candidates:[];
 for(const pack of Array.isArray(candidates)?candidates:[]){try{for(const m of JSON.parse(pack.rawJSON).mappings||[]){mappingCounts.set(m.id,(mappingCounts.get(m.id)||0)+1);itemCounts.set(m.sourceItemId,(itemCounts.get(m.sourceItemId)||0)+1);}}catch{}}
 for(const pack of Array.isArray(candidates)?candidates:[]){
  let batch;
  try{
   if(typeof pack?.rawJSON!=='string'||!/^[a-f0-9]{64}$/.test(pack.sha256||'')||sha256(pack.rawJSON)!==pack.sha256)throw Error('Missing or changed exact mapping-file bytes.');
   batch=JSON.parse(pack.rawJSON);
   if(batch.proposedAdditionalUniqueQuestions!==0||!nonblank(batch.authorId)||!Array.isArray(batch.mappings)||!batch.mappings.length||new Set(batch.mappings.map(m=>m?.id)).size!==batch.mappings.length)throw Error('Malformed or duplicate mapping records.');
  }catch(error){diagnostics.push({id:pack?.batchPath||'assignment-reuse',reason:error.message});continue;}
  if(!Array.isArray(pack.reviews)||!uniqueIds(pack.reviews.map(r=>r?.id))){diagnostics.push({id:pack.batchPath,reason:'Missing or duplicate mapping review IDs.'});continue;}
  const reviews=pack.reviews.filter(r=>r&&r.reviewType==='independent_source_item_reuse_mapping'&&r.mappingPath===pack.batchPath&&r.mappingSha256===pack.sha256);
  if(reviews.some(r=>['flagged','rejected'].includes(r.decision))){diagnostics.push({id:pack.batchPath,reason:'Current mapping batch is disputed.'});continue;}
  for(const mapping of batch.mappings){
   try{
    if(mappingCounts.get(mapping.id)!==1||itemCounts.get(mapping.sourceItemId)!==1)throw Error('Duplicate mapping ID or source item.');
    const ids=mapping.reusedQuestionIds,targets=mapping.reusedQuestions,source=sources.get(mapping.sourceId);
    const link=(bank.assignmentReuse?.links||[]).find(l=>l.id===mapping.id&&l.mappingPath===pack.batchPath&&l.mappingFileSha256===pack.sha256);
    if(!link||link.coverageKind!=='reviewed_semantic_reuse'||link.additionalUniqueQuestions!==0||link.sourceItemId!==mapping.sourceItemId||link.assignmentConceptId!==mapping.assignmentConceptId||link.sourceId!==mapping.sourceId||link.sourceSha256!==mapping.sourceSha256||link.primaryReusedQuestionId!==mapping.primaryReusedQuestionId||link.duplicateQuestionId!==mapping.duplicateQuestionId||!sameSet(link.reusedQuestionIds,ids)||stableJSON(link.physicalPages)!==stableJSON(mapping.physicalPages)||!boundObject(link,mapping,'mappingSha256','mappingRawJSON'))throw Error('No matching assembled, independently gated reuse link.');
    if(!nonblank(mapping.id)||!nonblank(mapping.sourceItemId)||!uniqueIds(ids)||!Array.isArray(targets)||targets.length!==ids.length||new Set(targets.map(q=>q?.questionId)).size!==ids.length||!sameSet(targets.map(q=>q.questionId),ids)||!ids.includes(mapping.primaryReusedQuestionId)||ids.includes(mapping.duplicateQuestionId))throw Error('Malformed source-assignment target mapping.');
    if(source?.role!=='assignment_solutions'||source.sha256!==mapping.sourceSha256||!Array.isArray(mapping.physicalPages)||!mapping.physicalPages.length||new Set(mapping.physicalPages).size!==mapping.physicalPages.length)throw Error('Missing current assignment-source evidence.');
    const concept=(bank.concepts||[]).find(c=>c.id===mapping.assignmentConceptId),sourceSlideIds=[];
    for(const physicalPage of mapping.physicalPages){
     const slide=(bank.slides||[]).find(s=>s.sourceId===mapping.sourceId&&s.physicalPage===physicalPage);
     if(slide)sourceSlideIds.push(slide.id);
     if(!sourceRefAllowed({sourceId:mapping.sourceId,sourceSha256:mapping.sourceSha256,physicalPage,slideId:slide?.id},sources,slides))throw Error('Assignment-source page is stale, unresolved or uninspected.');
    }
    if(!concept||!concept.questionIds?.includes(mapping.duplicateQuestionId)||!sourceSlideIds.every(id=>concept.slideIds?.includes(id))||!sameSet(link.sourceSlideIds,sourceSlideIds))throw Error('Assignment concept/source link is missing or stale.');
    const originals=(pack.originalRecords||[]).filter(x=>x.path===mapping.originalRecordPath),original=originals.length===1?originals[0]:null;
    if(!original||original.sha256!==mapping.originalRecordSha256||typeof original.rawJSON!=='string'||sha256(original.rawJSON)!==original.sha256)throw Error('Original assignment record is missing or changed.');
    const originalValue=JSON.parse(original.rawJSON);
    if(originalValue.id!==mapping.sourceItemId||originalValue.sourceId!==mapping.sourceId||originalValue.sourceSha256!==mapping.sourceSha256||stableJSON(originalValue.physicalPages)!==stableJSON(mapping.physicalPages))throw Error('Original assignment-source identity mismatch.');
    const duplicate=(bank.questions||[]).find(q=>q.id===mapping.duplicateQuestionId),duplicateValue={...duplicate};delete duplicateValue.status;delete duplicateValue.reviewIds;
    if(!duplicate||!['flagged','rejected'].includes(duplicate.status)||duplicate.assignmentSourceItemId!==mapping.sourceItemId||!duplicate.conceptIds?.includes(mapping.assignmentConceptId)||!batch.duplicatesToExcludeFromVerifiedPool?.includes(duplicate.id)||link.duplicateBinding?.questionId!==duplicate.id||link.duplicateBinding?.questionVersion!==duplicate.version||link.duplicateBinding?.questionSha256!==mapping.duplicateQuestionSha256||!boundObject(link.duplicateBinding,duplicateValue,'questionSha256'))throw Error('Duplicate adaptation is missing, changed or not excluded.');
    for(const target of targets){
     const entry=byId.get(target.questionId),binding=bank.learningResourceIntegrity?.bindings?.[target.questionId];
     const linked=(link.questionBindings||[]).find(q=>q.questionId===target.questionId);
     if(!entry||entry.question.version!==target.questionVersion||binding?.questionSha256!==target.questionSha256||linked?.questionVersion!==target.questionVersion||linked?.questionSha256!==target.questionSha256||!uniqueIds(target.reviewIds)||!sameSet(target.sourceSlideIds,entry.question.citations.map(c=>c.slideId).filter((id,i,a)=>a.indexOf(id)===i))||!target.reviewIds.every(id=>entry.question.reviewIds?.includes(id)&&entry.reviewIds.includes(id)&&boundObject((linked.reviewBindings||[]).find(r=>r.id===id),(bank.reviews||[]).find(r=>r.id===id))))throw Error('Reused target lacks its current independent question/review binding.');
    }
    const matching=reviews.flatMap(r=>(Array.isArray(r.mappingReviews)?r.mappingReviews:[]).filter(m=>m?.mappingId===mapping.id&&m.sourceItemId===mapping.sourceItemId).map(m=>({review:r,mapping:m})));
    if(matching.some(x=>['flagged','rejected'].includes(x.mapping.decision)))throw Error('Current mapping has an unresolved dispute.');
    const accepted=matching.some(({review:r,mapping:m})=>(r.mappingReviews||[]).filter(x=>x.mappingId===mapping.id).length===1&&r.decision==='verified'&&independentReviewer(r.reviewerId,batch)&&boundObject((link.reviewBindings||[]).find(b=>b.id===r.id),r)&&boundObject(pack.reviewBindings?.[r.id],r)&&m.decision==='verified'&&m.originalRecordPreserved===true&&m.duplicateExclusionRequired===mapping.duplicateQuestionId&&m.additionalUniqueQuestions===0&&Array.isArray(m.sourcePages)&&m.sourcePages.length===mapping.physicalPages.length&&m.sourcePages.every(Number.isInteger)&&mapping.physicalPages.every(p=>m.sourcePages.includes(p))&&m.reusedQuestionHashes&&Object.keys(m.reusedQuestionHashes).length===ids.length&&targets.every(t=>m.reusedQuestionHashes[t.questionId]===t.questionSha256));
    if(!accepted)throw Error('No independent exact-file/source/target mapping approval.');
    reuseLinks.push(link);
    for(const id of ids)add(id,'Existing verified question linked by an independently approved assignment-source reuse mapping',mapping.sourceItemId,mapping.id);
   }catch(error){diagnostics.push({id:mapping?.id||pack.batchPath,reason:error.message});}
  }
 }
 return {priorities:[...priority.values()].sort((a,b)=>a.questionId.localeCompare(b.questionId,undefined,{numeric:true})),reuseLinks,diagnostics,eligibleQuestionIds:eligible.questions.map(e=>e.question.id),eligibleQuestionCount:eligible.questions.length};
}
function base(entry,kind,id){const q=entry.question;return {id,kind,provenanceKind:'exact-question-projection',status:'projected-from-verified',week:q.week,lectureId:q.lectureId,title:q.subtopic||q.topic||q.id,questionIds:[q.id],conceptIds:clone(q.conceptIds||[]),slideIds:[...new Set(q.citations.map(c=>c.slideId))],sourceRefs:clone(q.citations),contexts:[context(entry)],projectionVersion:VERSION};}
function project(bank){
 const eligible=eligibleQuestions(bank),formulas=[],confusionPairs=[],traps=[],formulaMap=new Map();
 for(const e of eligible.questions){const q=e.question,sol=q.solution;
  (sol.formulas||[]).forEach((f,i)=>{const key=stableJSON(f);let card=formulaMap.get(key);if(!card){card={...base(e,'formula','projection.formula.'+sha256(key)),expression:f.expression,variables:clone(f.variables||{}),units:clone(f.units||{}),assumptions:clone(f.assumptions||[]),exactFormula:clone(f),applications:[q.stem],commonMistakes:clone(sol.misconceptions||[]),formulaOrigins:[{questionId:q.id,index:i}]};formulaMap.set(key,card);formulas.push(card);}else{card.contexts.push(context(e));card.formulaOrigins.push({questionId:q.id,index:i});card.questionIds.push(q.id);card.conceptIds=[...new Set([...card.conceptIds,...q.conceptIds])];card.slideIds=[...new Set([...card.slideIds,...q.citations.map(c=>c.slideId)])];card.sourceRefs.push(...clone(q.citations));card.applications.push(q.stem);card.commonMistakes.push(...clone(sol.misconceptions||[]));}});
  const misconceptions=sol.misconceptions||[],explicitTraps=sol.examTraps||[];
  if(misconceptions.length||explicitTraps.length)traps.push({...base(e,'trap','projection.trap.'+q.id),explicitTraps:clone(explicitTraps),misconceptions:clone(misconceptions),explanation:sol.justification});
  if(/\b(?:versus|vs\.?|distinguish|distinction|difference|contrast|compare|comparison)\b/i.test(q.stem)){
   const correct=q.options.filter(o=>q.correctOptionIds.includes(o.id)),wrong=q.options.filter(o=>!q.correctOptionIds.includes(o.id));
   confusionPairs.push({...base(e,'confusion','projection.comparison.'+q.id),discriminator:q.stem,correctAlternatives:clone(correct),incorrectAlternatives:clone(wrong),optionExplanations:clone(sol.optionExplanations),description:'An exact discrimination exercise from an approved question. Incorrect alternatives below are misconceptions, not factual descriptions of a second concept.'});
  }
 }
 for(const f of formulas){f.weeks=[...new Set(f.contexts.map(c=>c.week))].sort((a,b)=>a-b);f.lectureIds=[...new Set(f.contexts.map(c=>c.lectureId))];f.questionIds=[...new Set(f.questionIds)];f.applications=[...new Set(f.applications)];f.commonMistakes=[...new Set(f.commonMistakes)];}
 return {formulas,confusionPairs,traps,diagnostics:eligible.diagnostics,eligibleQuestionCount:eligible.questions.length,projectionVersion:VERSION};
}
const TOOL_CHECKS=['sourceSupport','assumptions','answerOrTrace','calculations','runtimeTests','explanation','sourceLinkage'];
function toolRecordAllowed(record,bank){
 if(record?.status!=='verified'||record.synthetic||!policyAllowed(bank))return false;
 const x=bank.learningResourceIntegrity,b=x.toolBindings?.[record.id];
 const files=record.implementationFiles||[];
 if((record.generatorKind||record.config||record.qLearningConfig)&&(!Array.isArray(files)||!files.length))return false;
 if(!Array.isArray(files)||files.some(f=>!f||typeof f.path!=='string'||!/^[a-f0-9]{64}$/.test(f.sha256||'')||x.policy.codeHashes?.[f.path]!==f.sha256))return false;
 if(!b||b.version!==record.version||!/^[a-f0-9]{64}$/.test(b.sha256||'')||b.runtimeSha256!==runtimeQuestionDigest(record))return false;
 const refs=record.sourceRefs,links=record.questionBindings;if(!Array.isArray(refs)||!Array.isArray(links)||!refs.length||!links.length||links.some(l=>!l||typeof l!=='object')||!sameSet(record.questionIds,links.map(l=>l.questionId)))return false;
 const qmap=new Map((bank.questions||[]).map(q=>[q.id,q])),linked=links.map(l=>qmap.get(l.questionId));if(linked.some(q=>!q))return false;
 for(const l of links){const q=qmap.get(l.questionId),qb=x.bindings?.[l.questionId];if(q.version!==l.questionVersion||qb?.questionSha256!==l.questionSha256)return false;}
 if(eligibleQuestions({...bank,questions:linked}).questions.length!==linked.length)return false;
 const sources=new Map((bank.sources||[]).map(s=>[s.id,s])),slides=new Map((bank.slides||[]).map(s=>[s.id,s]));
 for(const c of refs){if(!sourceRefAllowed(c,sources,slides)||(c.role==='conflict'&&!record.conflictResolution))return false;}
 const rs=(x.toolReviews||[]).filter(r=>r.toolId===record.id&&r.toolVersion===record.version&&r.toolSha256===b.sha256);
 return !rs.some(r=>['flagged','rejected'].includes(r.decision))&&rs.some(r=>r.decision==='verified'&&independentReviewer(r.reviewerId,record)&&TOOL_CHECKS.every(k=>r.checks?.[k]===true)&&refs.every(c=>r.sourceVersions?.[c.sourceId]===c.sourceSha256&&r.reviewedSlideIds?.includes(c.slideId))&&Object.entries(r.sourceVersions||{}).every(([id,h])=>sources.get(id)?.sha256===h));
}
function filterPage(rows,{week='',lecture='',search='',page=0,pageSize=20}={}){
 if(!Number.isInteger(page)||page<0||!Number.isInteger(pageSize)||pageSize<1||pageSize>100)throw Error('Invalid page bounds');
 const needle=String(search).trim().toLocaleLowerCase(),filtered=rows.filter(r=>(!week||String(r.week)===String(week)||(r.weeks||[]).some(w=>String(w)===String(week)))&&(!lecture||r.lectureId===lecture||(r.lectureIds||[]).includes(lecture))&&(!needle||JSON.stringify(r).toLocaleLowerCase().includes(needle)));const pages=Math.max(1,Math.ceil(filtered.length/pageSize)),current=Math.min(page,pages-1);return {rows:filtered.slice(current*pageSize,(current+1)*pageSize),total:filtered.length,page:current,pages};
}
return Object.freeze({VERSION,CHECKS,POLICY_CHECKS,VISUAL_CHECKS,visualEligibility,literalAnswerValid,sourceRefAllowed,stableJSON,sha256,sha256Bytes,runtimeQuestionDigest,policyAllowed,eligibleQuestions,project,filterPage,TOOL_CHECKS,toolRecordAllowed,assignmentPriority});
}));
