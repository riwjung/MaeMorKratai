// Domain checks load TypeScript in memory; no application sources are rewritten.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');
const ts = require('typescript');
const file = path.resolve(__dirname,'../lib/reading.ts');
const exportsForModule = {};
const compiled = ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{esModuleInterop:true,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
new Function('require','exports',compiled)(createRequire(file),exportsForModule);
const r = exportsForModule;
let passed = 0;
function test(name,fn){fn();passed++;console.log('PASS '+name);}
test('78 unique cards, 468 source meanings, five distinct installed images',()=>{
 assert.equal(r.cards.length,78);assert.equal(new Set(r.cards.map(c=>c.id)).size,78);
 assert.equal(r.cards.reduce((n,c)=>n+Object.keys(c.meanings).length,0),468);
 for(const c of r.cards){assert.ok(c.source_line&&c.source_message&&c.review_status);for(const context of r.contexts)assert.ok(c.meanings[context]);if(c.art)assert.ok(fs.existsSync(path.resolve(__dirname,'../public'+c.art)));}
 assert.equal(r.cards.filter(c=>c.art).length,5);
});
test('500 shuffles preserve identities, uniqueness and input catalog',()=>{
 const original=r.cards.map(c=>c.id);let changed=false;
 for(let i=0;i<500;i++){const deck=r.shuffleDeck();assert.equal(deck.length,78);assert.deepEqual([...deck].sort(),[...original].sort());changed ||= deck.join()!=original.join();}
 assert.ok(changed);assert.deepEqual(r.cards.map(c=>c.id),original);
});
test('unbiased index rejects the out-of-range tail',()=>{
 const descriptor=Object.getOwnPropertyDescriptor(globalThis,'crypto');let calls=0;
 Object.defineProperty(globalThis,'crypto',{configurable:true,value:{getRandomValues(a){a[0]=calls++===0?0xffffffff:77;return a;}}});
 try {assert.equal(r.randomBelow(78),77);assert.equal(calls,2);}finally{Object.defineProperty(globalThis,'crypto',descriptor);}
});
function selecting(){let s=r.sessionReducer(r.initialSession,{type:'QUESTION'});s=r.sessionReducer(s,{type:'START',deck:r.cards.map(c=>c.id)});s=r.sessionReducer(s,{type:'STOP'});s=r.sessionReducer(s,{type:'GATHERED'});return r.sessionReducer(s,{type:'SPREAD'});}
test('state guards prevent rapid duplicates, a fourth pick and premature reveal',()=>{
 let s=selecting();const first=s.deck[0];s=r.sessionReducer(s,{type:'PICK',id:first});assert.equal(r.sessionReducer(s,{type:'PICK',id:first}),s);assert.equal(r.sessionReducer(s,{type:'PICK',id:'invalid'}),s);assert.equal(r.sessionReducer(s,{type:'REVEAL'}),s);
 s=r.sessionReducer(s,{type:'PICK',id:s.deck[1]});s=r.sessionReducer(s,{type:'PICK',id:s.deck[2]});assert.equal(r.sessionReducer(s,{type:'PICK',id:s.deck[3]}),s);
 const order=s.deck; s=r.sessionReducer(s,{type:'REMOVE',id:first});assert.equal(s.deck,order);assert.deepEqual(s.selected,[order[1],order[2]]);s=r.sessionReducer(s,{type:'PICK',id:first});assert.deepEqual(s.selected,[order[1],order[2],first]);
 s=r.sessionReducer(s,{type:'REVEAL'});assert.equal(r.sessionReducer(s,{type:'REMOVE',id:first}),s);assert.equal(r.sessionReducer(s,{type:'UNLOCK'}),s);
 for(let i=0;i<3;i++)s=r.sessionReducer(s,{type:'NEXT_REVEAL'});assert.equal(s.phase,'locked');assert.equal(s.revealed,3);assert.equal(r.sessionReducer(s,{type:'NEXT_REVEAL'}),s);const ids=s.selected;s=r.sessionReducer(s,{type:'UNLOCK'});assert.equal(s.phase,'reading');assert.equal(s.selected,ids);
});
test('invalid start and stale animation events cannot replace a round',()=>{
 const s=selecting();assert.equal(r.sessionReducer(s,{type:'START',deck:r.shuffleDeck()}),s);assert.equal(r.sessionReducer(s,{type:'GATHERED'}),s);assert.equal(r.sessionReducer({...r.initialSession,phase:'question'},{type:'START',deck:Array(78).fill('the-fool')}).phase,'question');assert.deepEqual(r.sessionReducer(s,{type:'EDIT'}),{...r.initialSession,phase:'question'});
});
test('every love meaning stays source-exact in each position across six contexts',()=>{
 for(const situation of r.contexts)for(let i=0;i<78;i++){
 const ids=[r.cards[i].id,r.cards[(i+1)%78].id,r.cards[(i+2)%78].id];
 const result=r.createReading({category:'love',situation,question:'คำถามทดสอบ',spread:'past-present-future'},ids);
 assert.equal(result.status,'demo');result.entries.forEach((e,j)=>{const c=r.cards.find(c=>c.id===ids[j]);assert.equal(e.text,c.meanings[situation]);assert.equal(e.position,r.positions[j]);assert.equal(e.source.line,c.source_line);assert.ok(result.summary.includes(c.name));});
 }
});
test('context, position and second/third card influence summary; missing categories stay demo',()=>{
 const q={category:'love',situation:'คนโสด',question:'คำถาม',spread:'past-present-future'};const ids=r.cards.slice(0,3).map(c=>c.id);const first=r.createReading(q,ids);
 for(const next of [[ids[0],r.cards[4].id,ids[2]],[ids[0],ids[1],r.cards[5].id],[ids[1],ids[0],ids[2]]])assert.notEqual(r.createReading(q,next).summary,first.summary);
 assert.notEqual(r.createReading({...q,situation:'เลิกกัน'},ids).summary,first.summary);
 for(const category of ['work','money','life']){const result=r.createReading({...q,category,situation:r.situations[category][0]},ids);assert.ok(result.entries.every(e=>e.source===null&&e.text.includes('รอคำอ่าน')));assert.notEqual(result.summary,first.summary);}
 assert.throws(()=>r.createReading(q,[ids[0],ids[0],ids[1]]));assert.throws(()=>r.createReading({...q,situation:'invalid'},ids));
});
console.log(JSON.stringify({passed}));
