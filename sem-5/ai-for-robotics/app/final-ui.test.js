'use strict';
// Deterministic, inert DOM doubles. These tests do not execute a browser.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const C=require('./core.js'),source=fs.readFileSync(__dirname+'/app.js','utf8');
function extract(start,end){return source.slice(source.indexOf('  function '+start),source.indexOf('  function '+end));}
function dom(){
  const nodes=new Map();
  function el(tag,attrs={},children=[]){const n={tag,attrs,children:[],events:{},value:attrs.value||'',textContent:attrs.text||'',disabled:!!attrs.disabled,append(...items){this.children.push(...items);},replaceChildren(...items){this.children=[...items];},addEventListener(name,fn){this.events[name]=fn;},click(){this.events.click?.();}};n.append(...(Array.isArray(children)?children:[children]));if(tag==='select')n.value=n.children[0]?.attrs.value||'';if(attrs.id)nodes.set(attrs.id,n);return n;}
  const button=(label,action,attrs={})=>{const n=el('button',attrs,[label]);n.events.click=action;return n;};
  const all=(node,predicate)=>[...(predicate(node)?[node]:[]),...(node.children||[]).flatMap(c=>typeof c==='object'&&c?all(c,predicate):[])];
  return {el,button,nodes,all};
}
test('course explorer exposes nested subtopic scopes and locks navigation during an exam',()=>{
  const D=dom(),tree=D.el('div'),filters=new Map(['week','lecture','topic','subtopic'].map(k=>['filter-'+k,{value:''}]));
  let locked=false,view=null,toasts=[];
  const state={filters:{}},context={...D,C,state,bank:{pages:[{week:1,lectureId:'L01',lectureTitle:'Lecture one'}],questions:[{id:'one',week:'1',lecture:'L01',topic:'Search',subtopic:'Frontier',status:'verified'},{id:'two',week:1,lecture:'L01',topic:'Search',subtopic:'Visited set',status:'verified'}]},$:id=>id==='course-tree'?tree:filters.get(id),pretty:String,activeExam:()=>locked,toast:m=>toasts.push(m),clearFilters:()=>{state.filters={};},setView:v=>{view=v;}};
  vm.runInNewContext(extract('renderCourseTree','clearFilters'),context);context.renderCourseTree();
  assert.equal(D.all(tree,n=>n.attrs?.['data-subtopic']).length,0,'Subtopics must not inflate initial DOM');const topic=D.all(tree,n=>n.attrs?.['data-course-topic'])[0];topic.open=true;topic.events.toggle();topic.events.toggle();const links=D.all(tree,n=>n.attrs?.['data-subtopic']);assert.deepEqual(links.map(n=>n.attrs['data-subtopic']),['Frontier','Visited set']);
  links[1].click();assert.equal(view,'practice');for(const [key,value]of Object.entries({week:'1',lecture:'L01',topic:'Search',subtopic:'Visited set'})){assert.equal(state.filters[key],value);assert.equal(filters.get('filter-'+key).value,value);}
  locked=true;links[0].click();assert.equal(state.filters.subtopic,'Visited set');assert.match(toasts[0],/locked during the exam/);
});
test('coverage filters source then week then lecture, reset dependent scopes, and keep physical page labels',()=>{
  const D=dom(),w=D.el('div'),state={coverageSource:'',coverageWeek:'',coverageLecture:'',coveragePage:4};
  const pages=[{id:'p1',sourceId:'s',physicalPage:1,week:1,lectureId:'L01'},{id:'p2',sourceId:'s',physicalPage:2,week:1,lectureId:'L02'},{id:'p3',sourceId:'s',physicalPage:3,week:2,lectureId:'L03'},{id:'a1',sourceId:'a',physicalPage:1,week:1,lectureId:'A01'}].map(p=>({...p,visualInspection:{status:'complete'},conceptIds:[],disposition:'examinable'}));
  const sources=[{id:'s',filename:'lectures.pdf',pageCount:3,retrievalStatus:'ready'},{id:'a',filename:'assignments.pdf',pageCount:1,retrievalStatus:'ready'}];let selected=null;
  const context={...D,C,state,bank:{pages,sources,concepts:[]},rawBank:{},sourceById:new Map(sources.map(s=>[s.id,s])),stat:(v,l)=>D.el('div',{text:v+' '+l}),empty:(a,b)=>D.el('div',{text:a+b}),pretty:String,pageCoverage:()=> 'partial',showCoveragePage:p=>{selected=p;}};
  context.render=()=>{w.replaceChildren();context.renderCoverage(w);};vm.runInNewContext(extract('renderCoverage','showCoveragePage'),context);context.render();
  const control=label=>D.all(w,n=>n.attrs?.['aria-label']===label)[0];const heat=()=>D.all(control('Source-page coverage heatmap'),n=>n.tag==='button');
  assert.equal(state.coveragePage,0);assert.deepEqual(heat().map(n=>n.children[0]),['1','2','3']);
  control('Coverage week').value='1';control('Coverage week').events.change();assert.deepEqual(heat().map(n=>n.children[0]),['1','2']);
  assert.deepEqual(control('Coverage lecture').children.map(n=>n.attrs.value),['','L01','L02']);
  control('Coverage lecture').value='L02';control('Coverage lecture').events.change();assert.deepEqual(heat().map(n=>n.children[0]),['2']);heat()[0].click();assert.equal(selected.id,'p2');
  control('Coverage week').value='2';control('Coverage week').events.change();assert.equal(state.coverageLecture,'');assert.deepEqual(heat().map(n=>n.children[0]),['3']);
  control('Coverage source file').value='a';control('Coverage source file').events.change();assert.equal(state.coverageWeek,'');assert.equal(state.coverageLecture,'');assert.deepEqual(heat().map(n=>n.children[0]),['1']);
});
test('active exam exposes backup/import actions without rendering solutions or the general export menu',()=>{
  const D=dom(),w=D.el('div');let exports=0,imports=0,questionRenders=0;
  const exam={question_order:['q'],questions:[{id:'q'}],selections:{q:['o']},rules:{partial:false},index:0};
  const context={...D,activeExam:()=>exam,exportBackup:()=>exports++,$:id=>({click(){assert.equal(id,'backup-file');imports++;}}),confirm:()=>false,completeExam:()=>{},renderQuestion:q=>{questionRenders++;return D.el('article',{'data-question-id':q.id});},navigator:()=>D.el('nav'),renderPalette:()=>D.el('aside'),updateClock:()=>{}};
  vm.runInNewContext(extract('renderExam','completeExam'),context);context.renderExam(w);
  const hook=id=>D.all(w,n=>n.attrs?.['data-testid']===id)[0];hook('exam-backup-export').click();hook('exam-backup-import').click();assert.equal(exports,1);assert.equal(imports,1);assert.equal(questionRenders,1);assert.ok(hook('exam-submit'));assert.equal(D.all(w,n=>n.attrs?.['data-testid']==='export-format').length,0);assert.equal(D.all(w,n=>n.attrs?.class==='solution').length,0);
});
