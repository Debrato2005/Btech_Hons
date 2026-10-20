'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const E=require('../app/learning-tools.js'),N=require('../app/course-numerical.js');
const oracles={
 'rotated-vector-x':p=>{const t=p.angleDeg*Math.PI/180;return [Math.cos(t),-Math.sin(t)].reduce((s,v,i)=>s+v*[p.vx,p.vy][i],0);},
 'net-force-component':p=>[p.ax,p.ay,0].map(x=>p.m*x)[0],
 'series-stiffness':p=>1/(1/p.k1+1/p.k2),
 'coupled-inertia-torque':p=>[[p.a,p.b],[p.b,p.d]].map(row=>row.reduce((s,v,i)=>s+v*[p.x,p.y][i],0))[0],
 'epsilon-greedy-probability':p=>{const masses=Array(p.actions).fill(p.epsilon/p.actions);masses[0]+=1-p.epsilon;return masses[0];},
 'pinhole-image-x':p=>((p.fMM/1000)/p.Z)*p.X*1000,
 'convolution-output-size':p=>{let n=0;for(let start=0;start+p.K<=p.I+2*p.P;start+=p.S)n++;return n;},
 'octile-grid-distance':p=>{const d=Array.from({length:p.dx+1},()=>Array(p.dy+1).fill(Infinity));d[0][0]=0;for(let x=0;x<=p.dx;x++)for(let y=0;y<=p.dy;y++){if(x)d[x][y]=Math.min(d[x][y],d[x-1][y]+p.cell);if(y)d[x][y]=Math.min(d[x][y],d[x][y-1]+p.cell);if(x&&y)d[x][y]=Math.min(d[x][y],d[x-1][y-1]+Math.hypot(p.cell,p.cell));}return d[p.dx][p.dy];},
 'lidar-roundtrip-range':p=>p.timeNS*.15,
 'uniform-sample-count':p=>{let n=0;while(n*1000<p.durationMS*p.rate)n++;return n;},
 'adc-uniform-bin-width':p=>p.reference/Array.from({length:p.bits}).reduce(x=>2*x,1)
};
const report={scope:'Author implementation checks only; not independent approval or hardware execution.',families:{}};
for(const kind of N.kinds){const def=N.getImplementation(kind),id='synthetic.test.'+kind;E.registerNumericalFamily({...def,id,synthetic:true,status:'draft'});test(kind+': 1000 varied seeds, oracle, distinct rounded options and replay',()=>{const seen=new Set();let retries=0;for(let i=0;i<1000;i++){const seed='source-linked-'+kind+'-'+i,v=E.generateVariant(id,{seed}),p=v.parameters;seen.add(JSON.stringify(p));retries+=v.generationAttempt-1;assert.ok(Math.abs(v.answer-oracles[kind](p))<1e-10*Math.max(1,Math.abs(v.answer)),JSON.stringify(v));assert.equal(new Set(v.options.map(o=>o.roundedValue)).size,4);assert.equal(v.correctOptionIds.length,1);assert.ok(v.steps.length>=2);assert.ok(v.options.every(o=>o.justification));assert.deepEqual(v,E.generateVariant(id,{seed}));assert.deepEqual(E.restoreVariant(JSON.parse(JSON.stringify(v))).parameters,p);}report.families[kind]={cases:1000,uniqueParameterSets:seen.size,resampledCollisions:retries};assert.ok(seen.size>30);});test(kind+': nonfinite, type and missing parameter inputs rejected',()=>{const p=def.sample(E.createRng('invalid'));for(const k of Object.keys(p))for(const bad of [NaN,Infinity,-Infinity,null,true,'1',undefined])assert.throws(()=>def.validate({...p,[k]:bad}));});}
test('declared domain boundary rejections',()=>{assert.throws(()=>N.getImplementation('series-stiffness').validate({k1:0,k2:100}));assert.throws(()=>N.getImplementation('coupled-inertia-torque').validate({a:2,b:5,d:2,x:1,y:2}));assert.throws(()=>N.getImplementation('pinhole-image-x').validate({fMM:10,X:.2,Z:0}));assert.throws(()=>N.getImplementation('epsilon-greedy-probability').validate({epsilon:0,actions:4}));assert.throws(()=>N.getImplementation('octile-grid-distance').validate({dx:2,dy:2,cell:1}));assert.throws(()=>N.getImplementation('adc-uniform-bin-width').validate({bits:8.5,reference:5}));});
test('fixed parameters with equivalent displayed distractors are rejected',()=>{assert.throws(()=>E.generateVariant('synthetic.test.net-force-component',{seed:1,parameters:{m:2,ax:3,ay:3}}),/equivalent/);});
if(process.env.ROBOTICS_NUMERICAL_REPORT)process.on('exit',()=>require('node:fs').writeFileSync(process.env.ROBOTICS_NUMERICAL_REPORT,JSON.stringify(report,null,2)+'\n'));
