'use strict';
// Algorithm/numerical software tests use synthetic fixtures unless explicitly
// identified as a course trace regression. They never establish source review.
const test = require('node:test');
const assert = require('node:assert/strict');
const tools = require('../app/learning-tools.js');

const graph = {
  directed: false,
  nodes: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
  edges: [['A','B',5],['A','C',2],['B','D',6],['B','E',3],['C','F',4],['D','E',2],['D','G',6],['E','F',1],['F','G',3]]
    .map(([from,to,cost]) => ({ from,to,cost }))
};
const heuristic = { A:7, B:6, C:5, D:4, E:3, F:2, G:0 };

test('RNG repeats seeds, distinguishes types, and bounds integer/shuffle values', () => {
  const a = tools.createRng('seed'), b = tools.createRng('seed');
  assert.deepEqual(Array.from({length:100}, () => a.next()), Array.from({length:100}, () => b.next()));
  assert.notEqual(tools.createRng('4').next(), tools.createRng(4).next());
  assert.deepEqual(tools.createRng('shuffle').shuffle([1,2,3,4]).sort(), [1,2,3,4]);
  assert.throws(() => tools.createRng(''), /seed/i);
  assert.throws(() => tools.createRng(Number.NaN), /seed/i);
});

test('rounding is declared half away from zero with no negative zero', () => {
  assert.equal(tools.roundNumber(1.005,2), 1.01);
  assert.equal(tools.roundNumber(-1.005,2), -1.01);
  assert.equal(tools.formatNumber(-0.00001,3), '0.000');
  assert.throws(() => tools.roundNumber(Infinity), /finite/);
  assert.throws(() => tools.roundNumber(1,11), /precision/);
  assert.throws(() => tools.roundNumber(1e15,4), /large/);
});

test('options reject duplicates, rounded equivalence, unit mismatch, ambiguous answers', () => {
  const options = [1,2,3,4].map((value,i) => ({id:'o'+i,value}));
  assert.equal(tools.validateNumericOptions(options,2,0).filter(o=>o.correct).length,1);
  assert.throws(() => tools.validateNumericOptions([...options.slice(0,3),{id:'o3',value:3.00001}],2,3), {code:'EQUIVALENT_OPTIONS'});
  assert.throws(() => tools.validateNumericOptions(options,5,0), {code:'AMBIGUOUS_ANSWER'});
  assert.throws(() => tools.validateNumericOptions(options.map(o=>({...o,text:'same'})),2,0), {code:'DUPLICATE_OPTION'});
  assert.throws(() => tools.validateNumericOptions(options.map(o=>({...o,units:'m'})),2,0,'s'), /units/);
});

test('synthetic numerical families cannot be mistaken for source-supported course bank', () => {
  assert.deepEqual(tools.listNumericalFamilies(), []);
  assert.equal(tools.listNumericalFamilies({includeSynthetic:true}).length,2);
  for (const family of tools.listNumericalFamilies({includeSynthetic:true})) {
    const variant=tools.generateVariant(family.id,{seed:'known-seed'});
    assert.equal(variant.provenance.synthetic,true);
    assert.equal(variant.provenance.courseSupported,false);
    assert.equal(variant.provenance.status,'draft');
    assert.equal(variant.correctOptionIds.length,1);
    assert.equal(variant.options.length,4);
    assert.ok(variant.steps.length>=3);
    assert.ok(variant.options.every(o=>o.justification));
  }
});

test('1000 seeds per numerical family produce distinct valid options and reproduce', () => {
  for (const family of tools.listNumericalFamilies({includeSynthetic:true})) {
    for(let seed=0;seed<1000;seed++) {
      const variant=tools.generateVariant(family.id,{seed:'property-'+seed});
      assert.equal(new Set(variant.options.map(o=>o.roundedValue)).size,4);
      assert.deepEqual(tools.generateVariant(family.id,{seed:'property-'+seed}),variant);
      const restored=tools.restoreVariant(JSON.parse(JSON.stringify(variant)));
      assert.deepEqual(restored,variant);
      const correct=variant.options.find(o=>o.id===variant.correctOptionIds[0]);
      assert.equal(correct.roundedValue,variant.roundedAnswer);
    }
  }
});

test('Bayes numerical independent arithmetic and invalid-domain rejection', () => {
  const variant=tools.generateVariant('synthetic.bayes-two-hypotheses',{
    seed:'fixed',parameters:{prior:0.2,likelihoodTrue:0.8,likelihoodFalse:0.3}
  });
  assert.ok(Math.abs(variant.answer-0.4)<1e-12);
  assert.throws(()=>tools.generateVariant('synthetic.bayes-two-hypotheses',{
    seed:'fixed',parameters:{prior:1.2,likelihoodTrue:0.8,likelihoodFalse:0.3}
  }),/prior/);
  assert.throws(()=>tools.generateVariant('synthetic.bayes-two-hypotheses',{
    seed:'fixed',parameters:{prior:0.5,likelihoodTrue:0.8,likelihoodFalse:0.8}
  }),{code:'EQUIVALENT_OPTIONS'});
});

test('Q numerical nonterminal and terminal calculations use correct targets', () => {
  const params={oldQ:2,reward:3,maxNextQ:4,alpha:0.5,gamma:0.9,terminal:false};
  assert.equal(tools.generateVariant('synthetic.q-learning-update',{seed:'q',parameters:params}).roundedAnswer,4.3);
  const terminal=tools.generateVariant('synthetic.q-learning-update',{seed:'q',parameters:{...params,terminal:true}});
  assert.equal(terminal.roundedAnswer,2.5);
  assert.throws(()=>tools.generateVariant('synthetic.q-learning-update',{seed:'q',parameters:{...params,alpha:2}}),/alpha/);
});

test('restoration rejects unavailable versions, identity changes, invalid option order', () => {
  const variant=tools.generateVariant('synthetic.q-learning-update',{seed:'restore'});
  assert.throws(()=>tools.restoreVariant({...variant,engineVersion:'2'}),{code:'VERSION_MISMATCH'});
  assert.throws(()=>tools.restoreVariant({...variant,generatorVersion:'2'}),{code:'VERSION_MISMATCH'});
  assert.throws(()=>tools.restoreVariant({...variant,id:'fake'}),{code:'CORRUPT_VARIANT'});
  assert.throws(()=>tools.restoreVariant({...variant,optionOrder:['x','x','x','x']}),{code:'CORRUPT_VARIANT'});
});

test('family registration requires provenance and cannot replace a running version', () => {
  const definition={id:'test.invalid',version:'1',sample(){},validate(){},solve(){}};
  assert.throws(()=>tools.registerNumericalFamily(definition),/source references/);
  assert.throws(()=>tools.registerNumericalFamily({...definition,id:'synthetic.q-learning-update',synthetic:true}),/already registered/);
});

test('course BFS regression matches physical lecture pages 1108–1111', () => {
  const trace=tools.searchTrace(graph,{algorithm:'bfs',start:'A',goal:'G'});
  assert.deepEqual(trace.path,['A','B','D','G']);
  assert.equal(trace.cost,17); assert.equal(trace.hops,3); assert.equal(trace.expansions,6);
  assert.deepEqual(trace.steps.filter(s=>s.event==='expand').map(s=>s.current.node),['A','B','C','D','E','F']);
  assert.equal(trace.steps.at(-1).event,'goal');
});

test('course UCS regression matches p1116 tie D before G and six expansions', () => {
  const trace=tools.searchTrace(graph,{algorithm:'ucs',start:'A',goal:'G',tieBreak:'lexicographic'});
  assert.deepEqual(trace.path,['A','C','F','G']);
  assert.equal(trace.cost,9); assert.equal(trace.expansions,6);
  assert.deepEqual(trace.steps.filter(s=>s.event==='expand').map(s=>s.current.node),['A','C','B','F','E','D']);
  const atE=trace.steps.find(s=>s.current&&s.current.node==='E');
  assert.deepEqual(atE.frontier.map(e=>[e.node,e.g]),[['D',9],['G',9]]);
});

test('course A* regression matches pages1121–1123, including expansion count', () => {
  const trace=tools.searchTrace(graph,{algorithm:'astar',start:'A',goal:'G',heuristic,tieBreak:'lexicographic'});
  assert.deepEqual(trace.path,['A','C','F','G']); assert.equal(trace.cost,9); assert.equal(trace.expansions,3);
  assert.deepEqual(trace.steps.filter(s=>s.event==='expand').map(s=>s.current.node),['A','C','F']);
});

test('DFS convention expands first ordered neighbor first and terminates on cycles', () => {
  const trace=tools.searchTrace(graph,{algorithm:'dfs',start:'A',goal:'G'});
  assert.equal(trace.status,'found');
  assert.deepEqual(trace.steps.slice(1,3).map(s=>s.current.node),['A','B']);
  assert.ok(trace.expansions<graph.nodes.length);
  assert.match(trace.conventions.repeatedStates,/insertion/);
});

test('input neighbor ordering is distinct from lexical ordering', () => {
  const g={directed:true,nodes:['S','A','B','G'],edges:[{from:'S',to:'B'},{from:'S',to:'A'},{from:'A',to:'G'},{from:'B',to:'G'}]};
  assert.deepEqual(tools.searchTrace(g,{algorithm:'bfs',start:'S',goal:'G',neighborOrder:'input'}).path,['S','B','G']);
  assert.deepEqual(tools.searchTrace(g,{algorithm:'bfs',start:'S',goal:'G',neighborOrder:'lexicographic'}).path,['S','A','G']);
});

test('start equals goal, exhausted, and bounded traces are explicit', () => {
  const same=tools.searchTrace(graph,{start:'A',goal:'A'});
  assert.deepEqual(same.path,['A']); assert.equal(same.cost,0); assert.equal(same.expansions,0);
  const disconnected={directed:false,nodes:['A','Z'],edges:[]};
  assert.equal(tools.searchTrace(disconnected,{start:'A',goal:'Z'}).status,'exhausted');
  assert.equal(tools.searchTrace(graph,{start:'A',goal:'G',maxSteps:1}).status,'truncated');
});

test('graph validation rejects unknown nodes, missing direction, negative costs, duplicate edges', () => {
  assert.throws(()=>tools.searchTrace({...graph,directed:undefined},{start:'A',goal:'G'}),/direction/);
  assert.throws(()=>tools.searchTrace(graph,{start:'missing',goal:'G'}),/Start/);
  assert.throws(()=>tools.validateGraph({...graph,edges:[{from:'A',to:'B',cost:-1}]}),/nonnegative/);
  assert.throws(()=>tools.validateGraph({...graph,edges:[{from:'A',to:'B'},{from:'B',to:'A'}]}),/duplicate/);
  assert.throws(()=>tools.searchTrace(graph,{algorithm:'astar',start:'A',goal:'G',heuristic:{A:0}}),/Heuristic/);
  assert.throws(()=>tools.searchTrace(graph,{algorithm:'astar',start:'A',goal:'G',heuristic:{...heuristic,Z:3}}),/unknown node/);
});

test('A* reopens a closed state for admissible but inconsistent heuristic', () => {
  const g={directed:true,nodes:['S','A','B','G'],edges:[
    {from:'S',to:'A',cost:3},{from:'S',to:'B',cost:1},{from:'B',to:'A',cost:1},{from:'A',to:'G',cost:3}
  ]};
  const trace=tools.searchTrace(g,{algorithm:'astar',start:'S',goal:'G',heuristic:{S:5,A:0,B:4,G:0}});
  assert.equal(trace.cost,5);
  assert.deepEqual(trace.path,['S','B','A','G']);
  assert.ok(trace.steps.some(s=>s.actions.some(a=>a.type==='reopen'&&a.to==='A')));
});

test('UCS and zero-heuristic A* agree with an independent Floyd–Warshall oracle on 100 graphs', () => {
  const rng=tools.createRng('independent-graphs');
  for(let sample=0;sample<100;sample++) {
    const nodes=['A','B','C','D','E','F'], edges=[];
    const distances=nodes.map((_,i)=>nodes.map((__,j)=>i===j?0:Infinity));
    for(let i=0;i<nodes.length;i++)for(let j=0;j<nodes.length;j++) {
      if(i!==j&&rng.next()<0.35) {const cost=rng.int(0,20);edges.push({from:nodes[i],to:nodes[j],cost});distances[i][j]=cost;}
    }
    for(let k=0;k<nodes.length;k++)for(let i=0;i<nodes.length;i++)for(let j=0;j<nodes.length;j++)distances[i][j]=Math.min(distances[i][j],distances[i][k]+distances[k][j]);
    const g={nodes,edges,directed:true};
    for(const algorithm of ['ucs','astar']) {
      const trace=tools.searchTrace(g,{algorithm,start:'A',goal:'F',heuristic:Object.fromEntries(nodes.map(n=>[n,0]))});
      assert.equal(trace.cost,distances[0][5]===Infinity?null:distances[0][5]);
    }
  }
});

test('snapshots do not mutate graph, options, or other snapshots', () => {
  const before=JSON.stringify(graph),trace=tools.searchTrace(graph,{start:'A',goal:'G'});
  assert.equal(JSON.stringify(graph),before);
  trace.steps[0].frontier[0].path.push('FAKE');
  assert.deepEqual(trace.steps[1].current.path,['A']);
});

test('Q-learning uses sequential pre-update table, terminal guard, and explicit legal actions', () => {
  const initialQ={S:{a:2},T:{a:4,b:7},END:{a:100}};
  const trace=tools.qLearningTrace({alpha:0.5,gamma:0.9,initialQ,transitions:[
    {state:'S',action:'a',reward:3,nextState:'T',terminal:false,nextActions:['a','b']},
    {state:'T',action:'b',reward:5,nextState:'END',terminal:true,nextActions:['a']},
    {state:'S',action:'a',reward:0,nextState:'T',terminal:false,nextActions:['a','b']}
  ]});
  assert.equal(trace.steps[1].maxNextQ,7); assert.equal(trace.steps[1].newQ,5.65);
  assert.equal(trace.steps[2].target,5); assert.equal(trace.steps[2].newQ,6);
  assert.equal(trace.steps[3].maxNextQ,6); assert.equal(trace.steps[3].newQ,5.525);
  assert.deepEqual(initialQ,{S:{a:2},T:{a:4,b:7},END:{a:100}});
});

test('Q-learning self-transition bootstrap uses the old rather than updated value', () => {
  const trace=tools.qLearningTrace({alpha:0.5,gamma:0.5,initialQ:{S:{a:4}},transitions:[
    {state:'S',action:'a',reward:2,nextState:'S',terminal:false,nextActions:['a']}
  ]});
  assert.equal(trace.steps[1].target,4); assert.equal(trace.finalQ.S.a,4);
});

test('Q-learning validation rejects missing terminal/action domains and nonfinite rewards', () => {
  const config={alpha:0.5,gamma:0.9,transitions:[{state:'S',action:'a',reward:1,nextState:'T',terminal:false}]};
  assert.throws(()=>tools.qLearningTrace(config),/legal next action/);
  assert.throws(()=>tools.qLearningTrace({...config,alpha:2}),/alpha/);
  assert.throws(()=>tools.qLearningTrace({...config,transitions:[{...config.transitions[0],terminal:undefined}]}),/terminal/);
  assert.throws(()=>tools.qLearningTrace({...config,transitions:[{...config.transitions[0],terminal:true,reward:NaN}]}),/Reward/);
});

test('stepper supports boundaries, seek, reset, and safe returned copies', () => {
  const stepper=tools.createStepper(tools.searchTrace(graph,{start:'A',goal:'G'}));
  assert.equal(stepper.index,0); stepper.previous(); assert.equal(stepper.index,0);
  stepper.next(); assert.equal(stepper.index,1);
  stepper.seek(stepper.length-1);stepper.next();assert.equal(stepper.index,stepper.length-1);
  assert.equal(stepper.reset().event,'initial'); assert.throws(()=>stepper.seek(-1),/index/);
});

function syntheticLearningBank() {
  return {sources:[{id:'test-source',pageCount:3}],questions:[{id:'q'}],learningTools:{formulaSheet:[
    {id:'f',status:'verified',week:1,expression:'x+y',citations:[{sourceId:'test-source',physicalPage:2,locator:'test equation'}],questionIds:['q']}
  ],confusionPairs:[],traps:[]}};
}
test('formula/confusion/trap views require hash-bound approval, not a verified label', () => {
  const bank=syntheticLearningBank(),views=tools.buildLearningViews(bank);
  assert.equal(views.formulas.length,0);assert.equal(views.diagnostics.length,1);
  assert.equal(tools.buildLearningViews(bank,{includeDrafts:true}).formulas[0].sourceRefs[0].physicalPage,2);
  bank.learningTools.formulaSheet[0].status='draft';assert.equal(tools.buildLearningViews(bank).formulas.length,0);
  assert.equal(tools.buildLearningViews(bank,{includeDrafts:true}).formulas.length,1);
  bank.learningTools.formulaSheet[0].synthetic=true;assert.equal(tools.buildLearningViews(bank,{includeDrafts:true}).formulas.length,0);
});

test('broken/out-of-range source references are not offered as course learning views', () => {
  const bank=syntheticLearningBank();bank.learningTools.formulaSheet[0].citations[0].physicalPage=4;
  assert.equal(tools.buildLearningViews(bank,{includeDrafts:true}).formulas.length,0);
  assert.match(tools.buildLearningViews(bank).diagnostics[0].errors.join(' '),/page count/);
});

test('mastery discounts repeated memorization and numerical variants from the same family', () => {
  const questions=[{id:'q1',status:'verified',conceptIds:['c'],cognitiveSkill:'recall'},
    {id:'q2',status:'verified',conceptIds:['c'],familyId:'family',cognitiveSkill:'numerical'},
    {id:'q3',status:'verified',conceptIds:['c'],familyId:'family',cognitiveSkill:'numerical'},
    {id:'draft',status:'draft',conceptIds:['c']}];
  const attempts=Array.from({length:100},(_,i)=>({questionId:'q1',correct:true,timestamp:i}));
  attempts.push({questionId:'q2',correct:true},{questionId:'q3',correct:false},{questionId:'draft',correct:true});
  const mastery=tools.masteryByConcept(questions,attempts);
  assert.equal(mastery.length,2);
  assert.equal(mastery[0].uniqueEvidenceCount,1);assert.equal(mastery[0].label,'limited evidence');
  assert.equal(mastery[0].estimatedAccuracy,2/3);
  assert.equal(mastery[1].uniqueEvidenceCount,1);assert.equal(mastery[1].correctCount,0);
});

test('mistake revision follows prerequisite links without cycles and excludes drafts', () => {
  const bank={concepts:[{id:'c',prerequisiteConceptIds:['p']},{id:'p',prerequisiteConceptIds:['c']}],questions:[
    {id:'wrong',status:'verified',conceptIds:['c']},{id:'prep',status:'verified',conceptIds:['p']},
    {id:'fresh',status:'verified',conceptIds:['c']},{id:'draft',status:'draft',conceptIds:['p']}
  ]};
  const revision=tools.mistakeRevision(bank,[{questionId:'wrong',correct:false}],{bookmarks:['prep']});
  assert.deepEqual(revision.map(x=>x.questionId),['wrong','prep','fresh']);
  assert.ok(revision.find(x=>x.questionId==='prep').reasons.some(x=>x.includes('Prerequisite')));
});

test('bank numerical registration is allowlisted, source-linked, versioned and draft-gated', () => {
  const bank=syntheticLearningBank();
  bank.learningTools.numericalFamilies=[{id:'test.source-linked-q',title:'Test mapping only',status:'draft',
    generatorKind:'q-learning-update',generatorVersion:'1.0.0',sourceRefs:[{sourceId:'test-source',physicalPage:2,locator:'test equation'}]}];
  assert.deepEqual(tools.registerBankNumericalFamilies(bank).registered,[]);
  assert.deepEqual(tools.registerBankNumericalFamilies(bank,{includeDrafts:true}).registered,['test.source-linked-q']);
  const variant=tools.generateVariant('test.source-linked-q',{seed:'source-linked'});
  assert.equal(variant.provenance.synthetic,false);assert.equal(variant.provenance.status,'draft');
  assert.equal(variant.provenance.sourceRefs[0].physicalPage,2);
  bank.learningTools.numericalFamilies[0].generatorVersion='9';
  assert.deepEqual(tools.registerBankNumericalFamilies(bank,{includeDrafts:true}).registered,[]);
});
