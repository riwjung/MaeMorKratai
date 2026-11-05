import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const cases=JSON.parse(readFileSync(new URL('../lib/cases.json',import.meta.url)));
const catalog=JSON.parse(readFileSync(new URL('../lib/cards.json',import.meta.url)));
const ids=new Set(catalog.map(c=>c.id));
assert.equal(cases.length,60);assert.equal(new Set(cases.map(c=>c.id)).size,60);
// Saved readings refer to these original identities and wording.
assert.equal(createHash('sha256').update(JSON.stringify(cases.slice(0,30))).digest('hex'),'1ae87866272b05da82b4de95e69d1d426ba0a5e33a924453db9d323608159b99');
for(const [category,count] of Object.entries({love:30,work:10,money:10,health:10}))assert.equal(cases.filter(c=>c.category===category).length,count);
const dev=cases.filter(c=>c.split==='development'),hold=cases.filter(c=>c.split==='holdout');
assert.equal(dev.length,40);assert.equal(hold.length,20);
assert(!hold.some(c=>dev.some(d=>d.family===c.family)));
for(const c of cases){assert.equal(new Set(c.cards).size,4);assert(c.cards.every(id=>ids.has(id)));assert(c.question&&c.context&&c.horizon);assert.equal(c.source,'synthetic-scenario');assert(!('answer' in c))}
const metadata=['002_cases.sql','003_more_categories.sql'].flatMap(file=>[...readFileSync(new URL('../supabase/migrations/'+file,import.meta.url),'utf8').matchAll(/\('([^']+)','([^']+)','([^']+)'\)/g)].map(([,id,version,split])=>({id,version,split})));
assert.deepEqual(metadata,cases.map(({id,version,split})=>({id,version,split})));
console.log('PASS: 60 cases / 4 categories / 40 development / 20 holdout; original 30 unchanged; migrations match; valid cards and disjoint families');
