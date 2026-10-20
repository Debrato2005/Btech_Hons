'use strict';
// Isolated component/event tests with minimal DOM doubles, not browser QA.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const C=require('./core.js');
const source=fs.readFileSync(__dirname+'/app.js','utf8');
const component=source.slice(source.indexOf('  function renderAlgorithms'),source.indexOf('  function svgEl'));
function laboratory() {
  const nodes=new Map();
  function el(tag,attrs={},children=[]) {
    const node={tag,attrs,children:[],events:{},value:attrs.value||'',checked:!!attrs.checked,textContent:attrs.text||'',
      append(...items){this.children.push(...items);},replaceChildren(...items){this.children=[...items];},
      addEventListener(name,fn){this.events[name]=fn;}};
    node.append(...(Array.isArray(children)?children:[children]));
    if(tag==='select')node.value=node.children[0]?.attrs?.value||'';
    if(attrs.id)nodes.set(attrs.id,node);
    return node;
  }
  const graph={nodes:['A','B'],edges:[{from:'A',to:'B',cost:1}],directed:true};
  const sha='a'.repeat(64);
  const refs=[{sourceId:'test',slideId:'test-page',sourceSha256:sha,physicalPage:1}];
  const verified={id:'verified-example',title:'Accepted example',status:'verified',sourceRefs:refs,graph,config:{start:'A',goal:'B'},algorithm:'bfs'};
  const draft={...verified,id:'draft-example',title:'Draft example',status:'draft'};
  const state={algorithmAudit:false,algorithmTrace:null,algorithmGraph:null,algorithmStep:0};
  const w=el('div');
  const context={C,el,state,w,window:{RoboticsLearningResources:require('./learning-resources.js')},rawBank:{sources:[{id:'test',sha256:sha,retrievalStatus:'ready',pageCount:1}],slides:[{id:'test-page',sourceId:'test',sourceSha256:sha,physicalPage:1,visualInspection:{status:'complete'},disposition:'examinable'}],learningTools:{algorithmVisualizations:[verified,draft]}},
    button:(label,action,attrs)=>{const node=el('button',attrs,label);node.events.click=action;if(attrs?.['data-testid'])nodes.set(attrs['data-testid'],node);return node;},
    toolLinks:record=>el('span',{text:record.id}),
    renderTrace:output=>output.append('trace'),
    engine:{searchTrace:(g,config)=>({steps:[],provenance:config.provenance}),qLearningTrace:config=>({steps:[],provenance:config.provenance})}};
  const F=require('../tests/fixtures/learning-resource-bank.js'),bound=F.fixture();F.approveTool(bound,verified);draft.sourceRefs=structuredClone(verified.sourceRefs);context.rawBank={...bound,learningTools:{algorithmVisualizations:[verified,draft]}};
  context.render=()=>{w.replaceChildren();context.renderAlgorithms(w,context.engine);};
  vm.runInNewContext(component,context);
  context.render();
  const optionIds=()=>nodes.get('algorithm-record').children.map(n=>n.attrs.value);
  return {nodes,state,optionIds};
}
test('ordinary selector hides draft course records while retaining labeled synthetic demo',()=>{
  const lab=laboratory();
  assert.deepEqual(lab.optionIds(),['','verified-example']);
  assert.match(lab.nodes.get('algorithm-record').children[0].attrs.text,/Synthetic.*not course evidence/);
  assert.equal(lab.nodes.get('algorithm-audit').checked,false);
});
test('explicit audit opt-in exposes drafts and opt-out clears their trace and source state',()=>{
  const lab=laboratory();
  const toggle=lab.nodes.get('algorithm-audit');toggle.checked=true;toggle.events.change();
  assert.deepEqual(lab.optionIds(),['','verified-example','draft-example']);
  const choice=lab.nodes.get('algorithm-record');choice.value='draft-example';choice.events.change();
  assert.match(lab.nodes.get('algorithm-warning').textContent,/AUDIT ONLY/);
  lab.nodes.get('algorithm-run').events.click();
  assert.equal(lab.state.algorithmTrace.provenance.status,'draft');
  const reset=lab.nodes.get('algorithm-audit');reset.checked=false;reset.events.change();
  assert.deepEqual(lab.optionIds(),['','verified-example']);
  assert.equal(lab.state.algorithmTrace,null);
  assert.equal(lab.state.algorithmGraph,null);
  assert.equal(lab.nodes.get('algorithm-record').value,'');
  assert.equal(lab.nodes.get('algorithm-output').children.length,0);
});
test('changing a source example or its configuration clears stale trace; custom input is synthetic',()=>{
  const lab=laboratory();
  const choice=lab.nodes.get('algorithm-record');choice.value='verified-example';choice.events.change();
  lab.nodes.get('algorithm-run').events.click();
  assert.equal(lab.state.algorithmTrace.provenance.status,'verified');
  const text=lab.nodes.get('algorithm-config');
  const config=JSON.parse(text.value);config.graph.edges[0].cost=2;text.value=JSON.stringify(config);text.events.input();
  assert.equal(lab.state.algorithmTrace,null);
  lab.nodes.get('algorithm-run').events.click();
  assert.equal(lab.state.algorithmTrace.provenance.synthetic,true);
  choice.value='';choice.events.change();
  assert.equal(lab.state.algorithmTrace,null);
  assert.equal(lab.nodes.get('algorithm-output').children.length,0);
});
