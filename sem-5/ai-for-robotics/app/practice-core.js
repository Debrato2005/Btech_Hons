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
  function searchable(q) { return JSON.stringify([q.id,q.prompt,q.options,q.explanation,q.topic,q.subtopic,q.concept_ids,q.concept_text,q.tags]).toLocaleLowerCase(); }
  function isMulti(q) { return q.selectionMode==='multi' || q.correct_option_ids.length>1 || /multi|multiple|select_all/i.test(q.type); }
  function score(q,selected){
    const chosen=unique(array(selected)),valid=new Set(q.options.map(o=>o.id));
    if(chosen.some(id=>!valid.has(id)))throw Error('Invalid selected option in '+q.id);
    const correct=chosen.length===q.correct_option_ids.length&&chosen.every(id=>q.correct_option_ids.includes(id));
    return {correct,answered:chosen.length>0,points:correct?1:0,maximum:1,selected_option_ids:chosen};
  }
  function freshProgress(version){return {schema_version:1,bank_version:version,updated_at:new Date().toISOString(),settings:{theme:'system',immediate:false,shuffle_options:true},questions:{},practice_resume:null};}
  function questionState(progress,id) { return Object.hasOwn(progress.questions,id) ? progress.questions[id] : {bookmark:false,review:false,events:[]}; }
  function record(progress,q,selected,optionOrder) { const rules={correct:1,incorrect:0,partial:false},result=score(q,selected); const s=questionState(progress,q.id); s.events=array(s.events); s.events.push({...result,id:uid(),question_id:q.id,timestamp:new Date().toISOString(),mode:'practice',question_version:q.version,question_fingerprint:q.fingerprint,correct_option_ids:q.correct_option_ids.slice(),source_refs:clone(q.source_refs),question_snapshot:{id:q.id,version:q.version,stem:q.prompt,options:clone(q.options),correctOptionIds:q.correct_option_ids.slice()},rules:clone(rules),option_order:optionOrder.slice(),variant:q.variant || null}); progress.questions[q.id]=s; progress.updated_at=new Date().toISOString(); return result; }
  function shortcutAllowed(event) { if(event.altKey||event.ctrlKey||event.metaKey||event.target?.closest?.('input,textarea,select,[contenteditable=true]'))return false;if((event.key==='Enter'||event.key===' ')&&event.target?.closest?.('button,a,summary,[role=button]'))return false;return true; }
  function resumeProgress(saved,version){
    if(!saved)return freshProgress(version);
    const p=JSON.parse(saved);
    if(!p||p.schema_version!==1||!p.questions||typeof p.questions!=='object'||Array.isArray(p.questions)||!p.settings||typeof p.settings!=='object')throw Error('Saved practice data has an unsupported format.');
    for(const q of Object.values(p.questions))if(!q||typeof q!=='object'||!Array.isArray(q.events))throw Error('Saved answer history is invalid.');
    return p;
  }
  function practiceSelection(progress,q){
    if(!Object.hasOwn(progress.questions,q.id))progress.questions[q.id]={bookmark:false,review:false,events:[]};
    const s=progress.questions[q.id],current=s.current;
    if(!current||current.fingerprint!==q.fingerprint||!Array.isArray(current.order)||current.order.length!==q.options.length||new Set(current.order).size!==q.options.length||current.order.some(id=>!q.options.some(o=>o.id===id))||!Array.isArray(current.selected)||current.selected.some(id=>!current.order.includes(id)))s.current={selected:[],submitted:false,fingerprint:q.fingerprint,order:progress.settings.shuffle_options===false?q.options.map(o=>o.id):baseOptionOrder(q)};
    return s.current;
  }
  const api={clone,array,unique,uid,hash,shuffle,baseOptionOrder,normalizeQuestion,searchable,isMulti,score,freshProgress,questionState,record,shortcutAllowed,resumeProgress,practiceSelection};
  if(typeof module==='object'&&module.exports)module.exports=api;else root.RoboticsPracticeCore=api;
})(typeof window==='object'?window:globalThis);
