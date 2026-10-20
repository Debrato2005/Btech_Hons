'use strict';
// Read-only application path inspection with inert DOM doubles. This is NOT a browser test.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'app/app.js'),'utf8'),style=fs.readFileSync(path.join(root,'app/styles.css'),'utf8');
const C=require(path.join(root,'app/core.js')),raw=JSON.parse(fs.readFileSync(path.join(root,'data/bank.json'),'utf8')),bank=C.normalizeBank(raw);
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
function extract(start,end){const a=source.indexOf('  function '+start),b=source.indexOf('  function '+end,a+1);if(a<0||b<0)throw Error('Function boundary not found');return source.slice(a,b);}
function dom(){
 function el(tag,attrs={},children=[]){const n={tag,attrs,children:[],textContent:attrs.text||'',append(...items){this.children.push(...items);},replaceChildren(...items){this.children=[...items];},setAttribute(k,v){this.attrs[k]=v;}};n.append(...(Array.isArray(children)?children:[children]));return n;}
 const button=(label,action,attrs={})=>el('button',attrs,[label]);
 const all=(n,fn)=>[...(fn(n)?[n]:[]),...(n.children||[]).flatMap(c=>c&&typeof c==='object'?all(c,fn):[])];
 return{el,button,all};
}
const representativeIds=['W01-L01-P0016-Q06','W01-L01-P0021-Q04'];
const observations=[];
for(const id of representativeIds){
 const q=bank.questions.find(q=>q.id===id),D=dom();let sourceButtonCalls=0;
 const exam={questions:[q],question_order:[id],option_orders:{[id]:q.options.map(o=>o.id)},selections:{},review_flags:{},index:0};
 const context={...D,C,state:{examReview:null,view:'exam',assignmentPriority:new Map()},assets:{},activeExam:()=>exam,getQS:()=>({bookmark:false,review:false,events:[]}),questionInteraction:()=>({selected:[],order:exam.option_orders[id],submitted:false}),pretty:String,sourceButtons:()=>{sourceButtonCalls++;return[];},progress:{settings:{}}};
 vm.runInNewContext(extract('renderQuestion','selectOption'),context);const rendered=context.renderQuestion(q);
 const target=D.el('section');const pcontext={...D,C,state:{examReview:null},exportQuestions:()=>[q],exportOrder:()=>exam.option_orders[id],$:()=>target,version:raw.bankVersion,pretty:String,assets:{},citationText:c=>'Source '+c.sourceId+' p. '+c.physicalPage,window:{print(){}},setTimeout(){}};
 vm.runInNewContext(extract('printStudy','download'),pcontext);pcontext.printStudy('paper');
 observations.push({questionId:id,stem:q.prompt,status:q.status,type:q.type,assetIds:q.assetIds||[],sourceRefs:q.source_refs.map(c=>({slideId:c.slideId,physicalPage:c.physicalPage})),renderedExamImageOrObjectCount:D.all(rendered,n=>['img','object','svg','iframe'].includes(n.tag)).length,renderedExamSourceButtonCalls:sourceButtonCalls,renderedPaperImageOrObjectCount:D.all(target,n=>['img','object','svg','iframe'].includes(n.tag)).length});
}
const D=dom(),samples=bank.questions.slice(0,3),states=Object.fromEntries(samples.map((q,i)=>[q.id,{bookmark:false,review:false,events:i===2?[]:[{correct:i===0}]}]));
const context={...D,C,state:{index:0,examReview:null},activeExam:()=>null,getQS:id=>states[id],save(){},render(){}};
vm.runInNewContext(extract('renderPalette','renderSolution'),context);const palette=context.renderPalette(samples);
const paletteButtons=D.all(palette,n=>n.tag==='button'&&n.attrs?.['aria-label']?.startsWith('Question')).map(n=>({visibleLabel:n.children.join(''),classes:n.attrs.class,accessibleLabel:n.attrs['aria-label']}));
const receipt=JSON.parse(fs.readFileSync(path.join(root,'audits/validated-milestone-20261020T031351Z.json'),'utf8'));
const evidence={recordedAt:new Date().toISOString(),scope:'Read-only source execution with inert DOM doubles; no browser launched and no visual acceptance claimed',inputHashes:{'app/app.js':hash(source),'app/styles.css':hash(style),'data/bank.json':hash(fs.readFileSync(path.join(root,'data/bank.json')))},validatedReceipt:{bankVersion:receipt.bankVersion,bankSha256:receipt.bankSha256,artifact:receipt.artifact},bankAssetSummary:{totalQuestions:raw.questions.length,questionsWithAssetIds:raw.questions.filter(q=>(q.assetIds||[]).length).length,assets:(raw.assets||[]).map(a=>({id:a.id,kind:a.kind,mimeType:a.mimeType}))},diagramExamples:observations,paletteButtons,cssPalettePseudoElements:(style.match(/\.palette[^{}]*:{1,2}(?:before|after)[^{}]*\{[^}]+\}/g)||[])};
console.log(JSON.stringify(evidence,null,2));
