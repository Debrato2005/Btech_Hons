(function(root){
  'use strict';
  function bytes(encoded){
    const parts=[];
    for(let i=0;i<encoded.length;i+=65536){
      const text=atob(encoded.slice(i,i+65536)),part=new Uint8Array(text.length);
      for(let j=0;j<text.length;j++)part[j]=text.charCodeAt(j);
      parts.push(part);
    }
    return parts;
  }
  async function readBank(node){
    let bank;
    if(node.type==='application/gzip'){
      if(typeof DecompressionStream!=='function')throw Error('This browser needs offline gzip support. Open this file in a current Chrome, Edge, Firefox, or Safari.');
      const stream=new Blob(bytes(node.textContent)).stream().pipeThrough(new DecompressionStream('gzip'));
      bank=await new Response(stream).json();
    }else bank=JSON.parse(node.textContent);
    node.remove();return bank;
  }
  function assetStore(assets,find,urls=URL){
    const cache=new Map();let sourceId=null;
    function release(id){const old=cache.get(id);if(old){urls.revokeObjectURL(old);cache.delete(id);}}
    return {
      url(id){
        const a=assets[id];if(!a)return null;
        if(cache.has(id)){const url=cache.get(id);cache.delete(id);cache.set(id,url);return url;}
        const encoded=a.payloadId?find(a.payloadId)?.textContent:a.data||a.base64;
        if(!encoded)throw Error('Embedded asset is missing: '+id);
        const url=urls.createObjectURL(new Blob(bytes(encoded),{type:a.mimeType||a.mime||'application/octet-stream'}));
        cache.set(id,url);return url;
      },release,
      sourceURL(id){if(sourceId!==null&&sourceId!==id)release(sourceId);sourceId=id;return this.url(id);},
      prune(pinned=new Set(),limit=8){let spare=Array.from(cache.values()).filter(u=>!pinned.has(u)).length;for(const [id,url]of cache)if(spare>limit&&!pinned.has(url)){release(id);spare--;}}
      ,clear(){for(const id of cache.keys())release(id);sourceId=null;},get size(){return cache.size;}
    };
  }
  const api={bytes,readBank,assetStore};if(typeof module==='object'&&module.exports)module.exports=api;else root.RoboticsPayloads=api;
})(typeof window==='object'?window:globalThis);
