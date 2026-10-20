/* Exact, context-preserving views of independently approved question evidence.
 * This author-written extractor is inactive until its code policy is separately
 * approved. Projections inherit question evidence; they are not new fact reviews.
 */
(function(root,factory){'use strict';const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.RoboticsLearningResources=api;}(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='1.0.1';
const CHECKS=['sourceSupport','assumptions','answerSet','distractors','calculations','figureFidelity','explanation','difficulty','duplication'];
const POLICY_CHECKS=['exactProjection','contextPreservation','sourceAndReviewBinding','failClosedMutationTests','runtimeTests'];
const clone=x=>JSON.parse(JSON.stringify(x));
function stableJSON(x){
 if(x===null||typeof x!=='object'){if(typeof x==='number'&&!Number.isFinite(x))throw Error('Nonfinite JSON');if(x===undefined)throw Error('Undefined JSON');return JSON.stringify(x);}
 if(Array.isArray(x))return '['+x.map(stableJSON).join(',')+']';
 return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+stableJSON(x[k])).join(',')+'}';
}
// SHA-256, over TextEncoder UTF-8 bytes. Cross-tested against Node crypto.
function sha256(text){
 const bytes=new TextEncoder().encode(text),length=bytes.length,total=Math.ceil((length+9)/64)*64,padded=new Uint8Array(total);padded.set(bytes);padded[length]=128;
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
function context(entry){
 // Retain every original field, including supplemental notebooks, experiments,
 // implementation versions and diagram provenance. Shared aliases refer to the
 // same detached clone, not a lossy list of currently known extension fields.
 const q=clone(entry.question);
 return {...q,questionId:q.id,questionVersion:q.version,questionSha256:entry.binding.questionSha256,reviewIds:clone(entry.reviewIds),correctOptions:q.options.filter(o=>q.correctOptionIds.includes(o.id)),justification:q.solution.justification,sourceRefs:q.citations,conflictResolution:q.conflictResolution||null,primaryEvidence:q.primaryEvidence||[]};
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
return Object.freeze({VERSION,CHECKS,POLICY_CHECKS,literalAnswerValid,sourceRefAllowed,stableJSON,sha256,runtimeQuestionDigest,policyAllowed,eligibleQuestions,project,filterPage,TOOL_CHECKS,toolRecordAllowed});
}));
