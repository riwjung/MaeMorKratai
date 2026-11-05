// Import only matching v3 art; preserve source files and all existing meanings.
import {readFile,readdir,mkdir,writeFile,stat} from 'node:fs/promises';
import {resolve,extname,basename} from 'node:path';
import {homedir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import sharp from 'sharp';
const root=fileURLToPath(new URL('..',import.meta.url));
const source=resolve(process.argv[2]||resolve(homedir(),'Downloads/MaeMorKratai/cards-restyled/v3'));
const cards=JSON.parse(await readFile(resolve(root,'lib/reading-cards.json'),'utf8'));
if(cards.length!==78||new Set(cards.map(c=>c.id)).size!==78)throw Error('Expected unique 78-card catalog');
const known=new Set(cards.map(c=>c.id)),found=new Map(),ignored=[];
for(const name of (await readdir(source)).sort()){
 const ext=extname(name).toLowerCase();if(!['.jpg','.jpeg','.png','.webp'].includes(ext))continue;
 const id=basename(name,extname(name));if(!known.has(id)){ignored.push(name);continue;}
 const s=await stat(resolve(source,name));if(!s.isFile())continue;
 found.set(id,[...(found.get(id)||[]),{name,mtime:s.mtimeMs}]);
}
const out=resolve(root,'public/cards/v3');await mkdir(out,{recursive:true});
const manifest={version:'v3',capturedAt:new Date().toISOString(),selection:'Newest modification time; filename breaks ties',cards:[],duplicates:[],ignored};
for(const card of cards){
 const candidates=(found.get(card.id)||[]).sort((a,b)=>b.mtime-a.mtime||a.name.localeCompare(b.name));
 card.art=null;
 if(!candidates.length)continue;
 const chosen=candidates[0],bytes=await readFile(resolve(source,chosen.name));
 const metadata=await sharp(bytes).metadata();
 if(!metadata.width||!metadata.height||metadata.height<=metadata.width)throw Error('Expected portrait card: '+chosen.name);
 const web=await sharp(bytes).rotate().resize({width:600,withoutEnlargement:true}).webp({quality:85}).toBuffer();
 const rendered=await sharp(web).metadata();
 const hash=createHash('sha256').update(web).digest('hex');
 const filename=card.id+'-'+hash.slice(0,12)+'.webp';
 await writeFile(resolve(out,filename),web);
 card.art='/cards/v3/'+filename;
 manifest.cards.push({id:card.id,sourceFile:chosen.name,sourceSha256:createHash('sha256').update(bytes).digest('hex'),art:card.art,sha256:hash,bytes:web.length,width:metadata.width,height:metadata.height,renderedWidth:rendered.width,renderedHeight:rendered.height});
 if(candidates.length>1)manifest.duplicates.push({id:card.id,chosen:chosen.name,alternatives:candidates.slice(1).map(c=>c.name)});
}
await writeFile(resolve(root,'lib/reading-cards.json'),JSON.stringify(cards,null,2)+'\n');
await writeFile(resolve(root,'public/cards/deck.js'),'window.__mmktDeck='+JSON.stringify(cards.map(({id,name,art})=>({id,name,art})))+';\n');
await writeFile(resolve(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({total:cards.length,withArt:manifest.cards.length,nameOnly:cards.length-manifest.cards.length,duplicates:manifest.duplicates,ignored}));
