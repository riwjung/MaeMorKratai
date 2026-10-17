const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..'),ctx={};vm.createContext(ctx);
for(const f of ['deck-data.js','title-workflow.js'])vm.runInContext(fs.readFileSync(path.join(root,'extension',f),'utf8'),ctx);
const deck=ctx.MMKT_DECK,spec=ctx.MMKT_TITLES.spec;
assert.equal(deck.length,78);assert.equal(new Set(deck.map(c=>c.id)).size,78);
for(const c of deck){
 assert(c.prompt.includes(spec));assert(c.prompt.includes(ctx.MMKT_TITLES.quality));assert.equal((c.prompt.match(/CARD TITLE:/g)||[]).length,1);
 assert(c.prompt.includes('CARD TITLE: '+c.name.toUpperCase()));assert(!c.prompt.includes('Do not add the card name'));assert(!c.prompt.includes('No words, letters'));
 assert(c.legacyPrompt.includes('Do not add the card name'));
 const edit=ctx.MMKT_TITLES.prompt(c,{mode:'edit',approved:true,sourceName:'TARGET_ORIGINAL_'+c.id});
 assert(edit.includes(spec)&&edit.includes('CARD TITLE: '+c.name.toUpperCase()));assert(!edit.includes('Create ONE complete'));
}
const report={passed:true,cards:78,checks:['all prompts share identical title specification','exact original English card names','no conflicting no-title instruction in title modes','preserved legacy no-title prompt','all edit prompts preserve artwork'],generation_requests:0};
fs.writeFileSync(path.join(__dirname,'artifacts/prompt-contract-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
