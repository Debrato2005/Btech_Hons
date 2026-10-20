'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {gunzipSync,gzipSync}=require('node:zlib');
test('bank loader restores every Unicode field from lossless gzip',async()=>{
  const P=require('../app/payloads.js'),bank={questions:[{id:'q1',answer:['o2'],text:'Σ θ → 中文'}]};
  const node={type:'application/gzip',textContent:gzipSync(JSON.stringify(bank)).toString('base64'),remove(){this.removed=true;}};
  assert.deepEqual(await P.readBank(node),bank);assert.equal(node.removed,true);
});
test('lazy assets decode exactly, release URLs, and remain available for revisits',()=>{
  const P=require('../app/payloads.js'),bytes=Buffer.from('source pixels '.repeat(20000)),encoded=bytes.toString('base64');let reads=0;
  const node={get textContent(){reads++;return encoded;}},created=[],revoked=[];
  const urls={createObjectURL(b){created.push(b);return 'blob:'+created.length;},revokeObjectURL(u){revoked.push(u);}};
  const store=P.assetStore({a:{payloadId:'a-bytes',mimeType:'image/png'}},()=>node,urls);
  assert.equal(reads,0);assert.equal(store.url('a'),'blob:1');assert.equal(store.url('a'),'blob:1');assert.equal(reads,1);
  store.release('a');assert.deepEqual(revoked,['blob:1']);assert.equal(store.url('a'),'blob:2');assert.equal(reads,2);
  return created[1].arrayBuffer().then(b=>assert.deepEqual(Buffer.from(b),bytes));
});
test('unused asset URLs stay bounded while visible images remain usable',()=>{
  const P=require('../app/payloads.js'),revoked=[],assets=Object.fromEntries(Array.from({length:20},(_,i)=>[i,{data:'YQ=='}]));let n=0;
  const store=P.assetStore(assets,()=>null,{createObjectURL(){return 'blob:'+ ++n;},revokeObjectURL(u){revoked.push(u);}});
  for(let i=0;i<20;i++){store.url(i);store.prune(new Set(['blob:1']),4);}
  assert.equal(revoked.includes('blob:1'),false);assert.ok(store.size<=5);store.clear();assert.equal(store.size,0);
});
test('source preview cache reuses one PDF and releases it when the source changes',()=>{
  const P=require('../app/payloads.js'),revoked=[];let count=0;
  const store=P.assetStore({a:{kind:'source_pdf',data:'YQ=='},b:{kind:'source_pdf',data:'Yg=='}},()=>null,{createObjectURL(){return 'blob:'+ ++count;},revokeObjectURL(u){revoked.push(u);}});
  const first=store.sourceURL('a');
  for(let i=0;i<30;i++)assert.equal(store.sourceURL('a'),first);
  assert.equal(count,1);assert.equal(store.sourceURL('b'),'blob:2');assert.deepEqual(revoked,['blob:1']);assert.equal(store.size,1);
});
