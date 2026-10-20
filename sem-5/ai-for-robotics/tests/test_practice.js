'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const old=require('../app/core.js'),C=require('../app/practice-core.js');
const raw={id:'persistent-q',version:3,status:'verified',stem:'Pick x²',selectionMode:'multi',options:[{id:'one',text:'x²'},{id:'two',text:'x*x'},{id:'three',text:'x'}],correctOptionIds:['one','two'],solution:{justification:'Square',optionExplanations:{one:'yes',two:'yes',three:'no'}},citations:[{sourceId:'lectures',physicalPage:1}],conceptIds:[]};
test('practice fingerprint and answer IDs stay compatible with the original app',()=>{
  const q=C.normalizeQuestion(raw);assert.deepEqual(q,old.normalizeQuestion(raw));
  for(const order of [C.baseOptionOrder(q),['three','two','one']]){
    assert.equal(C.score(q,order.filter(id=>q.correct_option_ids.includes(id))).correct,true);
    assert.equal(C.score(q,['one']).correct,false);
  }
});
test('existing saved answers, bookmark and unrelated history survive a practice resume',()=>{
  const q=C.normalizeQuestion(raw),p=old.freshProgress('same');p.questions[q.id]={bookmark:true,review:true,events:[{id:'past',correct:true}],current:{fingerprint:q.fingerprint,selected:['one','two'],submitted:true,order:['three','two','one']}};p.attempts=[{id:'historic'}];
  const resumed=C.resumeProgress(JSON.stringify(p),'same');assert.deepEqual(resumed,p);
  const current=C.practiceSelection(resumed,q);assert.deepEqual(current,p.questions[q.id].current);assert.equal(resumed.questions[q.id].bookmark,true);assert.deepEqual(resumed.attempts,[{id:'historic'}]);
});
test('changed question versions clear only current selections and retain bookmarks and history',()=>{
  const q=C.normalizeQuestion(raw),p=C.freshProgress('same');p.questions[q.id]={bookmark:true,events:[{id:'past'}],current:{fingerprint:'stale',selected:['three'],submitted:true,order:['three','one','two']}};
  const current=C.practiceSelection(p,q);assert.deepEqual(current.selected,[]);assert.equal(current.submitted,false);assert.equal(p.questions[q.id].bookmark,true);assert.equal(p.questions[q.id].events.length,1);
});
test('new practice records stay compact and bounded without deleting legacy history',()=>{
  const q=C.normalizeQuestion({...raw,stem:'Large question '.repeat(5000)}),p=C.freshProgress('same');
  p.questions[q.id]={bookmark:true,review:true,events:[{id:'legacy',correct:false,question_snapshot:{stem:'preserve this old answer'}}]};
  for(let i=0;i<100;i++)C.record(p,q,q.correct_option_ids,C.baseOptionOrder(q));
  const state=p.questions[q.id];assert.equal(state.events[0].id,'legacy');assert.equal(state.events[0].question_snapshot.stem,'preserve this old answer');
  assert.equal(state.events.length,2);assert.equal(state.events.at(-1).correct,true);assert.equal(state.bookmark,true);assert.equal(state.review,true);
  assert.ok(JSON.stringify(state).length<1500,'New saves must not duplicate the question or source payloads');
});
