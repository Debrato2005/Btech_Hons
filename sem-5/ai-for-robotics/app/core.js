/* Pure, dependency-free study logic. Also loadable through CommonJS for tests. */
(function (root) {
  'use strict';
  const SCHEMA = 1;
  const clone = value => JSON.parse(JSON.stringify(value));
  const array = value => Array.isArray(value) ? value : [];
  const unique = values => [...new Set(values)];
  const text = value => typeof value === 'string' ? value : value == null ? '' : String(value);
  const uid = () => globalThis.crypto && globalThis.crypto.randomUUID ? globalThis.crypto.randomUUID() : `event-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  function hash(value) { let h=2166136261; for (const c of text(value)) { h ^= c.charCodeAt(0); h = Math.imul(h,16777619); } return h >>> 0; }
  function random(seed) { let a=hash(seed); return () => { a += 0x6D2B79F5; let t=a; t=Math.imul(t ^ t>>>15,t|1); t ^= t+Math.imul(t ^ t>>>7,t|61); return ((t ^ t>>>14)>>>0)/4294967296; }; }
  function shuffle(values, seed) { const out=values.slice(), rng=random(seed); for(let i=out.length-1;i>0;i--){const j=Math.floor(rng()*(i+1)); [out[i],out[j]]=[out[j],out[i]];} return out; }
  // Presentation order is independent of the answer key and of cyclic author array order.
  function baseOptionOrder(q) { return shuffle(q.options.map(o=>o.id).slice().sort(), `presentation-v1:${q.id}`); }
  function normalizeQuestion(raw) {
    const explanation = raw.explanation || raw.solution || {};
    const citations = array(raw.source_refs || raw.citations || raw.sources);
    const options=array(raw.options).map((o,i)=>({ ...o, id:text(o.id || o.option_id || `option-${i+1}`), text:text(o.text || o.content || o.label) }));
    const correct=array(raw.correctOptionIds || raw.correct_option_ids || raw.answer_option_ids || raw.answer?.option_ids || raw.answer?.correct_option_ids);
    const status=raw.status || raw.audit_status || raw.review?.status || 'draft';
    return { ...raw, id:text(raw.id || raw.question_id), prompt:text(raw.prompt || raw.stem || raw.question), type:raw.type || raw.question_type || (correct.length>1?'multi_select':'single_select'), options, correct_option_ids:correct, status,
      difficulty:raw.difficulty || 'unclassified', week:raw.week ?? raw.week_id ?? citations[0]?.week_id ?? '', lecture:raw.lectureId ?? raw.lecture ?? raw.lecture_id ?? citations[0]?.lecture_id ?? '', topic:raw.topic || raw.topic_id || '', subtopic:raw.subtopic || raw.subtopic_id || '',
      concept_ids:array(raw.conceptIds || raw.concept_ids), mastery_dimension:raw.cognitiveSkill || raw.mastery_dimension || raw.skill || raw.cognitive_skill || 'conceptual', explanation, source_refs:citations,
      option_explanations:explanation.optionExplanations || raw.option_explanations || explanation.option_rationales || explanation.distractor_rationales || explanation.distractors || {},
      prerequisites:array(explanation.prerequisiteConceptIds || raw.prerequisite_concept_ids || explanation.prerequisites), tags:array(raw.tags), high_yield:!!(raw.highYield||raw.high_yield||array(raw.tags).includes('high_yield')), fingerprint:hash(JSON.stringify([raw.id,raw.version,raw.stem,options,correct,explanation,citations,raw.variant])).toString(16)
    };
  }
  function normalizeBank(raw) { const concepts=new Map(array(raw.concepts).map(c=>[c.id,c]));const questions=array(raw.questions).map(normalizeQuestion).map(q=>({...q,concept_text:q.concept_ids.map(id=>concepts.has(id)?[concepts.get(id).title,concepts.get(id).description].join(' '):id).join(' ')}));return { ...raw, metadata:raw.metadata || raw.meta || {bank_version:raw.bankVersion, title:raw.title, complete:raw.complete}, questions, sources:array(raw.sources), pages:array(raw.pages || raw.slides), concepts:array(raw.concepts), learning_tools:raw.learningTools || raw.learning_tools || {} }; }
  function searchable(q) { return JSON.stringify([q.id,q.prompt,q.options,q.explanation,q.topic,q.subtopic,q.concept_ids,q.concept_text,q.tags]).toLocaleLowerCase(); }
  function isMulti(q) { return q.selectionMode==='multi' || q.correct_option_ids.length>1 || /multi|multiple|select_all/i.test(q.type); }
  function score(q, selected, rules={correct:1,incorrect:0,partial:false}) {
    const valid=new Set(q.options.map(o=>o.id)); const chosen=unique(array(selected));
    if(chosen.some(id=>!valid.has(id))) throw new Error(`Invalid selected option in ${q.id}`);
    const answers=new Set(q.correct_option_ids); const exact=chosen.length===answers.size && chosen.every(id=>answers.has(id));
    let points=chosen.length===0?0:exact?rules.correct:-rules.incorrect;
    if(rules.partial && isMulti(q) && chosen.length && !exact) { const hits=chosen.filter(id=>answers.has(id)).length; const wrong=chosen.length-hits; const incorrectCount=q.options.length-answers.size; points=Math.max(-rules.incorrect,rules.correct*(hits/answers.size-(incorrectCount?wrong/incorrectCount:0))); }
    return {correct:exact, answered:chosen.length>0, points:Number(points.toFixed(6)), maximum:rules.correct, selected_option_ids:chosen};
  }
  function freshProgress(version) { return {schema_version:SCHEMA,bank_version:version || 'unknown',updated_at:new Date().toISOString(),settings:{theme:'system',immediate:false,shuffle_options:true},questions:{},variants:{},attempts:[],active_exam:null}; }
  function questionState(progress,id) { return Object.hasOwn(progress.questions,id) ? progress.questions[id] : {bookmark:false,review:false,events:[]}; }
  function record(progress,q,selected,optionOrder,mode='practice',rules={correct:1,incorrect:0,partial:false}) { const result=score(q,selected,rules); const s=questionState(progress,q.id); s.events=array(s.events); s.events.push({...result,id:uid(),question_id:q.id,timestamp:new Date().toISOString(),mode,question_version:q.version,question_fingerprint:q.fingerprint,correct_option_ids:q.correct_option_ids.slice(),source_refs:clone(q.source_refs),question_snapshot:{id:q.id,version:q.version,stem:q.prompt,options:clone(q.options),correctOptionIds:q.correct_option_ids.slice()},rules:clone(rules),option_order:optionOrder.slice(),variant:q.variant || null}); progress.questions[q.id]=s; progress.updated_at=new Date().toISOString(); return result; }
  function mastery(progress,questions) {
    const groups={};
    for(const q of questions.filter(q=>q.status==='verified')) {
      const dimension=q.mastery_dimension || 'conceptual';
      if(!groups[dimension]) groups[dimension]={dimension,evidence:new Map(),unique_concepts:new Set(),seen_concepts:new Set()};
      const g=groups[dimension],key=q.variant?.familyId || q.familyId || q.id;
      q.concept_ids.forEach(c=>g.unique_concepts.add(c));
      const events=array(questionState(progress,q.id).events).filter(e=>!e.question_fingerprint||e.question_fingerprint===q.fingerprint),last=events.at(-1);
      if(!g.evidence.has(key))g.evidence.set(key,null);
      if(last){const previous=g.evidence.get(key);if(!previous||text(last.timestamp)>=text(previous.timestamp))g.evidence.set(key,last);q.concept_ids.forEach(c=>g.seen_concepts.add(c));}
    }
    return Object.values(groups).map(g=>{const attempted=[...g.evidence.values()].filter(Boolean),correct=attempted.filter(e=>e.correct).length;return {dimension:g.dimension,total:g.evidence.size,attempted:attempted.length,correct,unique_concepts:g.unique_concepts.size,seen_concepts:g.seen_concepts.size,accuracy:attempted.length?correct/attempted.length:null};});
  }
  function revisionScore(q,progress) { const s=questionState(progress,q.id), events=array(s.events).filter(e=>!e.question_fingerprint||e.question_fingerprint===q.fingerprint), last=events.at(-1); return (last&&!last.correct?12:0)+(s.review?8:0)+(s.bookmark?5:0)+(q.high_yield?3:0)+(!last?1:0)+Math.min(events.filter(e=>!e.correct).length,5); }
  function rankRevisionQuestions(questions,progress,sourceAssignmentIds=[],followUpIds=[]) {
    const assignmentIds=new Set(sourceAssignmentIds),followUps=new Set(followUpIds),priority=q=>revisionScore(q,progress)+(assignmentIds.has(q.id)?2:0)+(followUps.has(q.id)?2:0);
    return questions.filter(q=>q.status==='verified'&&priority(q)>1).sort((a,b)=>priority(b)-priority(a)||Number(a.week||0)-Number(b.week||0)||String(a.lecture||'').localeCompare(String(b.lecture||''),undefined,{numeric:true})||a.id.localeCompare(b.id,undefined,{numeric:true}));
  }
  // Recommendations use only outcomes tied to the current exact presentation fingerprint.
  // Historical or imported unbound outcomes remain in backups but cannot seed this graph.
  function currentStudyProgress(progress,questions) {
    const out={...progress,questions:{}};
    for(const q of questions){const previous=questionState(progress,q.id),events=array(previous.events).map((event,index)=>({event,index})).filter(x=>x.event?.question_fingerprint===q.fingerprint&&typeof x.event.correct==='boolean').sort((a,b)=>(Date.parse(a.event.timestamp)||0)-(Date.parse(b.event.timestamp)||0)||a.index-b.index).map(x=>x.event);out.questions[q.id]={...previous,events};}
    return out;
  }
  // Input questions must already pass the independent runtime gate. Concept links
  // remain study-order heuristics, not new semantic/source approvals.
  function studyFollowUps(rawBank,progress,engine,{focusQuestionId=null,limit=null}={}) {
    if(typeof engine?.mistakeRevision!=='function')return {recommendations:[],total:0};
    const questions=array(rawBank.questions).filter(q=>q.status==='verified'&&!q.synthetic&&q.origin!=='synthetic'),byId=new Map(questions.map(q=>[q.id,q]));
    const concepts=array(rawBank.concepts).filter(c=>c.status==='verified'&&array(c.questionIds).some(id=>array(byId.get(id)?.conceptIds).includes(c.id))),byConcept=new Map(concepts.map(c=>[c.id,c]));
    const graph={questions:questions.map(q=>({...q,conceptIds:array(q.conceptIds).filter(id=>array(byConcept.get(id)?.questionIds).includes(q.id))})),concepts:concepts.map(c=>({...c,prerequisiteConceptIds:array(c.prerequisiteConceptIds||c.prerequisiteIds).filter(id=>byConcept.has(id))}))};
    const normalized=normalizeBank({questions}).questions,current=currentStudyProgress(progress,normalized),focus=focusQuestionId?graph.questions.find(q=>q.id===focusQuestionId):null;
    if(focusQuestionId&&!focus)return {recommendations:[],total:0};
    const attempts=normalized.flatMap(q=>{const last=current.questions[q.id].events.at(-1);return last?[{questionId:q.id,correct:last.correct}]:[];}),missed=new Set(attempts.filter(a=>!a.correct).map(a=>a.questionId));
    // A focus query is ephemeral context for the existing graph traversal only.
    // It never records an attempt, and all output labels remove any missed/untested claim.
    const rows=engine.mistakeRevision(graph,focus?[{questionId:focus.id,correct:false}]:attempts,focus?{}:{bookmarks:questions.filter(q=>current.questions[q.id].bookmark).map(q=>q.id),reviewFlags:questions.filter(q=>current.questions[q.id].review).map(q=>q.id)}),found=new Map();
    const add=(id,reasons,priority)=>{if(id===focusQuestionId||!byId.has(id)||!reasons.length)return;const old=found.get(id)||{questionId:id,reasons:[],priority:0,conceptIds:graph.questions.find(q=>q.id===id).conceptIds};old.reasons=unique([...old.reasons,...reasons]);old.priority=Math.max(old.priority,priority);found.set(id,old);};
    for(const row of rows){const reasons=focus?row.reasons.flatMap(reason=>reason==='Prerequisite of a recently missed concept'?['Recorded prerequisite concept for this question']:reason==='Unattempted practice for a recently missed concept'?['Shares a recorded concept with this question']:[]):row.reasons;add(row.questionId,reasons,row.priority);}
    const seeds=focus?[focus]:graph.questions.filter(q=>missed.has(q.id)),directPrerequisites=new Set(seeds.flatMap(q=>array((q.solution||q.explanation)?.prerequisiteConceptIds)).filter(id=>byConcept.has(id)));
    for(const q of graph.questions)if(q.conceptIds.some(id=>directPrerequisites.has(id)))add(q.id,[focus?'Recorded question-level prerequisite':'Recorded prerequisite of a recently missed question'],2);
    if(focus)for(const id of array(focus.relatedQuestionIds))add(id,['Authored related-question link'],3);
    const ordered=[...found.values()].sort((a,b)=>b.priority-a.priority||a.questionId.localeCompare(b.questionId,undefined,{numeric:true})),maximum=limit===null?ordered.length:Number.isInteger(limit)&&limit>=0?limit:focus?8:ordered.length;
    return {recommendations:ordered.slice(0,maximum),total:ordered.length};
  }
  function selectQuestions(questions,filters,progress) { const query=text(filters.search).toLocaleLowerCase().trim();return questions.filter(q=> {if(filters.status && filters.status!=='all' && q.status!==filters.status)return false;for(const key of ['week','lecture','topic','subtopic','difficulty','type']) if(filters[key] && text(q[key])!==text(filters[key]))return false;if(query && !searchable(q).includes(query))return false;const s=questionState(progress,q.id),last=array(s.events).filter(e=>!e.question_fingerprint||e.question_fingerprint===q.fingerprint).at(-1);if(filters.learning==='bookmarked'&&!s.bookmark)return false;if(filters.learning==='review'&&!s.review)return false;if(filters.learning==='unanswered'&&last)return false;if(filters.learning==='incorrect'&&(!last||last.correct))return false;if(filters.learning==='correct'&&(!last||!last.correct))return false;return true;}); }
  function createExam(pool,config,now=Date.now()) {
    if(!Number.isInteger(config.count)||config.count<1)throw new Error('Choose a positive whole question count.');
    if(!Number.isFinite(config.minutes)||config.minutes<=0||config.minutes>1440)throw new Error('Duration must be between 1 and 1440 minutes.');
    if(!Number.isFinite(config.rules.correct)||config.rules.correct<=0||!Number.isFinite(config.rules.incorrect)||config.rules.incorrect<0)throw new Error('Scoring must use positive marks and a nonnegative penalty.');
    const seed=config.seed || uid(); let chosen=[];pool=pool.filter(q=>q.status==='verified');
    if(config.mix && Object.values(config.mix).some(n=>n>0)) { if(Object.values(config.mix).reduce((a,b)=>a+b,0)!==config.count)throw new Error('Difficulty counts must add up to the question count.'); for(const [difficulty,count]of Object.entries(config.mix)){if(!Number.isInteger(count)||count<0)throw new Error('Difficulty counts must be nonnegative whole numbers.');const available=pool.filter(q=>q.difficulty===difficulty);if(available.length<count)throw new Error(`Only ${available.length} verified ${difficulty} questions match your scope; ${count} requested.`);chosen.push(...shuffle(available,`${seed}:${difficulty}`).slice(0,count));} } else {if(pool.length<config.count)throw new Error(`Only ${pool.length} verified questions match your scope.`);chosen=shuffle(pool,seed).slice(0,config.count);}
    chosen=shuffle(chosen,`${seed}:questions`);
    return {id:uid(),schema_version:SCHEMA,seed,started_at:now,ends_at:now+config.minutes*60000,status:'active',index:0,rules:clone(config.rules),question_order:chosen.map(q=>q.id),questions:clone(chosen),option_orders:Object.fromEntries(chosen.map(q=>[q.id,shuffle(q.options.map(o=>o.id),`${seed}:${q.id}`)])),selections:{},review_flags:{},config:clone(config)};
  }
  function finishExam(exam,now=Date.now(),reason='submitted') { const ended=clone(exam);ended.status='completed';ended.completed_at=now;ended.completion_reason=reason;ended.results=ended.question_order.map(id=>{const q=ended.questions.find(q=>q.id===id);return {question_id:id,...score(q,ended.selections[id]||[],ended.rules),option_order:ended.option_orders[id],variant:q.variant || null};});ended.total=Number(ended.results.reduce((s,r)=>s+r.points,0).toFixed(6));ended.maximum=ended.results.reduce((s,r)=>s+r.maximum,0);return ended; }
  function safeObject(value) { return value && typeof value==='object'&&!Array.isArray(value); }
  function validateProgress(data) {
    if(!safeObject(data)||data.schema_version!==SCHEMA||!safeObject(data.questions)||!safeObject(data.settings)||!Array.isArray(data.attempts))throw new Error('This is not a supported version-1 progress backup.');
    if(Object.keys(data.questions).length>200000||data.attempts.length>10000)throw new Error('Backup exceeds safe import limits.');
    for(const [id,s]of Object.entries(data.questions)){if(['__proto__','constructor','prototype'].includes(id)||!safeObject(s)||!Array.isArray(s.events))throw new Error('Malformed question progress.');for(const e of s.events){if(!safeObject(e)||typeof e.id!=='string'||!Array.isArray(e.selected_option_ids)||e.selected_option_ids.some(v=>typeof v!=='string')||!Array.isArray(e.option_order)||e.option_order.some(v=>typeof v!=='string')||typeof e.correct!=='boolean'||!Number.isFinite(e.points)||!Number.isFinite(e.maximum))throw new Error(`Malformed answer history for ${id}.`);}}
    const validateExam=(e,expectedStatus)=>{if(!safeObject(e)||typeof e.id!=='string'||e.status!==expectedStatus||!safeObject(e.review_flags)||!Array.isArray(e.question_order)||!Array.isArray(e.questions)||!safeObject(e.selections)||!safeObject(e.option_orders)||!safeObject(e.rules)||!Number.isFinite(e.ends_at)||!Number.isFinite(e.started_at)||e.ends_at<=e.started_at||!Number.isFinite(e.rules.correct)||e.rules.correct<=0||!Number.isFinite(e.rules.incorrect)||e.rules.incorrect<0||!Number.isInteger(e.index)||e.index<0||e.index>=e.question_order.length)throw new Error('Malformed exam state.');if(e.question_order.length!==new Set(e.question_order).size||e.question_order.length!==e.questions.length)throw new Error('Invalid exam question ordering.');for(const id of e.question_order){if(['__proto__','constructor','prototype'].includes(id))throw new Error('Unsafe exam identifier.');const q=e.questions.find(q=>q.id===id);if(!q||typeof q.prompt!=='string'||!safeObject(q.explanation)||!safeObject(q.option_explanations)||!Array.isArray(q.source_refs)||!Array.isArray(q.concept_ids)||!Array.isArray(q.options)||!Array.isArray(q.correct_option_ids)||q.correct_option_ids.length===0||q.correct_option_ids.some(id=>!q.options.some(o=>o.id===id))||!Array.isArray(e.option_orders[id])||e.option_orders[id].length!==q.options.length||new Set(e.option_orders[id]).size!==q.options.length||e.option_orders[id].some(o=>!q.options.some(x=>x.id===o)))throw new Error('Invalid exam option ordering.');score(q,e.selections[id]||[],e.rules);}if(expectedStatus==='completed'){if(!Number.isFinite(e.completed_at)||!Array.isArray(e.results)||e.results.length!==e.question_order.length)throw new Error('Malformed completed exam.');const recalculated=finishExam(e,e.completed_at,e.completion_reason);if(recalculated.total!==e.total||recalculated.maximum!==e.maximum||JSON.stringify(recalculated.results)!==JSON.stringify(e.results))throw new Error('Completed exam scores do not match its saved answers.');}};
    if(data.variants!==undefined){if(!safeObject(data.variants))throw new Error('Malformed saved variants.');for(const [id,v]of Object.entries(data.variants)){if(['__proto__','constructor','prototype'].includes(id)||!safeObject(v)||!safeObject(v.variant)||v.variant.id!==id||!Array.isArray(v.answers)||v.answers.some(a=>typeof a.id!=='string'||typeof a.selectedOptionId!=='string'||typeof a.correct!=='boolean'))throw new Error('Malformed numerical variant history.');}}data.attempts.forEach(e=>validateExam(e,'completed'));if(data.active_exam)validateExam(data.active_exam,'active');return true;
  }
  function mergeProgress(current,incoming,version,{useIncomingExam=false}={}) {
    validateProgress(incoming);const out=clone(current);let addedEvents=0;
    for(const [id,entry]of Object.entries(incoming.questions)){const old=questionState(out,id); const eventMap=new Map(array(old.events).map(e=>[e.id,e])); for(const e of entry.events)if(!eventMap.has(e.id)){eventMap.set(e.id,e);addedEvents++;}out.questions[id]={...old,bookmark:!!(old.bookmark||entry.bookmark),review:!!(old.review||entry.review),events:[...eventMap.values()].sort((a,b)=>text(a.timestamp).localeCompare(text(b.timestamp)))};}
    out.variants=out.variants||{};for(const [id,v]of Object.entries(incoming.variants||{})){if(!Object.hasOwn(out.variants,id))out.variants[id]=clone(v);else{const answers=new Map(out.variants[id].answers.map(a=>[a.id,a]));v.answers.forEach(a=>{if(!answers.has(a.id))answers.set(a.id,a);});out.variants[id].answers=[...answers.values()];}}const attempts=new Map(array(out.attempts).map(a=>[a.id,a]));incoming.attempts.forEach(a=>{if(!attempts.has(a.id))attempts.set(a.id,a);});out.attempts=[...attempts.values()];
    if(incoming.active_exam && (!out.active_exam||useIncomingExam) && !attempts.has(incoming.active_exam.id))out.active_exam=clone(incoming.active_exam);
    if(out.active_exam&&attempts.has(out.active_exam.id))out.active_exam=null;
    out.bank_version=version;out.updated_at=new Date().toISOString();return {progress:out,addedEvents,bankChanged:incoming.bank_version!==version};
  }
  function selectAlgorithmRecords(records, {includeUnverified=false, bank={}}={}) {
    const sources = new Map(array(bank.sources).map(source => [source.id, source]));
    const slides = new Map(array(bank.slides).map(slide => [slide.id, slide]));
    return array(records).filter(record => record && !record.synthetic && !record.provenance?.synthetic
      && Array.isArray(record.sourceRefs) && record.sourceRefs.length > 0
      && (includeUnverified || (root.RoboticsLearningResources ||
        (typeof module === 'object' && module.exports ? require('./learning-resources.js') : null))?.toolRecordAllowed(record, bank))
      && record.sourceRefs.every(ref => {
        if (!ref || typeof ref.sourceSha256 !== 'string' || !/^[a-f0-9]{64}$/.test(ref.sourceSha256)) return false;
        const source = sources.get(ref.sourceId), slide = slides.get(ref.slideId);
        return source?.retrievalStatus === 'ready' && source.sha256 === ref.sourceSha256
          && slide?.sourceId === ref.sourceId && slide.sourceSha256 === ref.sourceSha256
          && Number.isInteger(ref.physicalPage) && ref.physicalPage > 0 && ref.physicalPage <= source.pageCount
          && slide.physicalPage === ref.physicalPage && slide.visualInspection?.status === 'complete'
          && ['examinable','repeated','excluded'].includes(slide.disposition)
          && (ref.role !== 'conflict' || !!record.conflictResolution);
      }));
  }
  function shortcutAllowed(event) { if(event.altKey||event.ctrlKey||event.metaKey||event.target?.closest?.('input,textarea,select,[contenteditable=true]'))return false;if((event.key==='Enter'||event.key===' ')&&event.target?.closest?.('button,a,summary,[role=button]'))return false;return true; }
  function csv(rows) { return rows.map(row=>row.map(cell=>{let s=cell==null?'':typeof cell==='object'?JSON.stringify(cell):String(cell);if(/^[=+@\-\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}).join(',')).join('\r\n'); }
  const api={SCHEMA,clone,array,unique,uid,hash,random,shuffle,baseOptionOrder,normalizeQuestion,normalizeBank,searchable,isMulti,score,freshProgress,questionState,record,mastery,revisionScore,rankRevisionQuestions,currentStudyProgress,studyFollowUps,selectQuestions,createExam,finishExam,validateProgress,mergeProgress,selectAlgorithmRecords,shortcutAllowed,csv};
  if(typeof module==='object'&&module.exports)module.exports=api;root.RoboticsStudyCore=api;
})(typeof window==='object'?window:globalThis);
