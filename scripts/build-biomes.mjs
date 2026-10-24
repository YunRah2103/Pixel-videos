/**
 * 5 reproducible biome parallax stages.
 * Output: independent transparent 960x320 PNG layers + integration manifests.
 * Stage output is pixel-authored/template-generated, not SVG rasterized.
 * Agents may replace any layer with hand-drawn PNG at matching native dimensions.
 */
import sharp from 'sharp';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const OUTPUT=resolve(ROOT,'public/studio-v4/biomes');
const LIB=resolve(ROOT,'public/studio-v4/library');
const manifest=JSON.parse(await readFile(resolve(LIB,'manifest.json'),'utf8'));
const W=960,H=320;
const themes={
 forest:{sky:['#447b9e','#79b9c4','#a8c6bc'],hill:['#4c766b','#64896f'],
 foliage:['oak','birch','pine','bush','fern'],ground:'#76936c',road:'#424b59',mark:'#e4d6a3',weather:'leaves',mood:'day'},
 autumn:{sky:['#665c78','#b58580','#e3b99a'],hill:['#866875','#a38470'],
 foliage:['maple','birch','oak','bush'],ground:'#a58b62',road:'#4b4355',mark:'#f0cb98',weather:'leaves',mood:'golden'},
 coast:{sky:['#4d83a1','#94b9b9','#ddc7a2'],hill:['#548d90','#83aca3'],
 foliage:['cypress','bush','fern'],ground:'#86a18b',road:'#49535d',mark:'#eacfa0',weather:'clear',mood:'day'},
 mountains:{sky:['#3e6a89','#7393a0','#c1bdb1'],hill:['#52657a','#849196'],
 foliage:['pine','cypress','rocks','fern'],ground:'#677f75',road:'#444d5b',mark:'#e8cca5',weather:'snow',mood:'day'},
 nightcity:{sky:['#19283c','#29445c','#547383'],hill:['#2d475e','#455666'],
 foliage:['cottage','lamp','cypress','bush'],ground:'#405a5a',road:'#343b4a',mark:'#b2a68b',weather:'rain',mood:'night'}
};
const rng=(seed)=>{let x=seed>>>0;return()=>{x=Math.imul(x^x>>>13,0x85ebca6b);x=Math.imul(x^x>>>16,0xc2b2ae35);return ((x^x>>>16)>>>0)/4294967296;};};
const panel=async(width,height,color)=>sharp({create:{width,height,channels:4,background:color}}).png().toBuffer();
const sources=new Map();
const get=async(id)=>{if(!sources.has(id))sources.set(id,await readFile(resolve(LIB,id+'.png')));return sources.get(id);};
const layers=['sky','mountains','far','middle','road','foreground'];
const results=[];
for(const [biome,theme] of Object.entries(themes)){
 const dir=resolve(OUTPUT,biome);await mkdir(dir,{recursive:true});
 const rand=rng([...biome].reduce((s,c)=>s*33+c.charCodeAt(0),517));
 const maps={};
 const blits={};
 for(const id of layers)blits[id]=[];
 // Fully covered three-band sky: no fullscreen empty void above the scene.
 for(const [j,color] of theme.sky.entries())blits.sky.push({input:await panel(W,j===0?39:j===1?49:44,color),left:0,top:[0,39,88][j]});
 // Dithered native pixel cloud field and an occasional distinctive larger cloud.
 for(let x=17;x<960;x+=75+Math.floor(rand()*65)){
   const id='cloud-'+String(Math.floor(rand()*10)).padStart(2,'0');
   blits.sky.push({input:await get(id),left:x,top:15+Math.floor(rand()*65)});
 }
 // Stylized 1px-stepped mountain silhouette, water band at the coast.
 for(let x=0;x<W;x++){
  const peak=108+Math.round(Math.sin(x*.029)*13+Math.sin(x*.067)*7);
  const yy=biome==='coast'?139:peak;
  blits.mountains.push({input:await panel(1,174-yy,theme.hill[x%7===0?1:0]),left:x,top:yy});
 }
 if(biome==='coast'){
  blits.mountains.push({input:await panel(W,22,'#4f91a1'),left:0,top:159});
  for(let x=4;x<W;x+=19)blits.mountains.push({input:await panel(7,1,'#b2c7b3'),left:x,top:167+(x%5)});
 }
 // Distant forms are smaller; deliberate space between silhouettes avoids mechanical rows.
 for(let x=0;x<W-70;x+=28+Math.floor(rand()*10)){
  const family=theme.foliage[Math.floor(rand()*Math.min(3,theme.foliage.length))],v=Math.floor(rand()*10);
  const id=family+'-'+String(v).padStart(2,'0'),m=manifest.sprites.find(s=>s.id===id);
  const xx=x+Math.floor(rand()*6),yy=199-Math.round(m.height*.72)+(Math.floor(rand()*12)-6);
  let item=await get(id);
  if(m.width>36){item=await sharp(item).resize({width:Math.floor(m.width*.75),kernel:'nearest'}).png().toBuffer();}
  const dim=await sharp(item).metadata();
  blits.far.push({input:item,left:xx,top:Math.min(204,Math.max(110,yy))});
 }
 for(let x=0;x<W-88;x+=56+Math.floor(rand()*25)){
  const family=theme.foliage[Math.floor(rand()*theme.foliage.length)],v=Math.floor(rand()*10);
  const id=family+'-'+String(v).padStart(2,'0'),m=manifest.sprites.find(s=>s.id===id);
  const xx=x+Math.floor(rand()*7),yy=235-m.height+Math.floor(rand()*9);
  if(yy<0||xx+m.width>W||yy+m.height>253)continue;
  blits.middle.push({input:await get(id),left:xx,top:yy});
 }
 // Road and verge are exact flat-colour native pixels with edge clusters.
 blits.road.push({input:await panel(W,23,theme.ground),left:0,top:230});
 blits.road.push({input:await panel(W,52,theme.road),left:0,top:253});
 blits.road.push({input:await panel(W,15,theme.ground),left:0,top:305});
 blits.road.push({input:await panel(W,2,'#aeb1a1'),left:0,top:254});
 blits.road.push({input:await panel(W,1,'#253740'),left:0,top:304});
 for(let x=9;x<W;x+=34)blits.road.push({input:await panel(15,2,theme.mark),left:x,top:284});
 for(let x=6;x<W-25;x+=18+Math.floor(rand()*15)){
  const id=(rand()>.46?'fern':'flower')+'-'+String(Math.floor(rand()*10)).padStart(2,'0');
  const m=manifest.sprites.find(s=>s.id===id);
  if(x+m.width>W)continue;
  // Foreground silhouettes break the straight horizontal line.
  blits.foreground.push({input:await get(id),left:x,top:320-m.height+Math.floor(rand()*3)});
 }
 for(const layer of layers){
  // Prevent source rectangles extending beyond pixel stage.
  const composited=blits[layer].filter(c=>c.left>=0&&c.top>=0);
  const buf=await sharp({create:{width:W,height:H,channels:4,background:'#00000000'}})
   .composite(composited).png({palette:false}).toBuffer();
  await writeFile(resolve(dir,layer+'.png'),buf);
  maps[layer]={file:'studio-v4/biomes/'+biome+'/'+layer+'.png',
   depth:{sky:.03,mountains:.12,far:.29,middle:.54,road:1,foreground:1.2}[layer],
   objects:composited.length};
 }
 const data={name:biome,nativeWidth:180,nativeHeight:320,stageWidth:W,
  pixelUpscale:6,weather:theme.weather,mood:theme.mood,
  layers:Object.fromEntries(layers.map(x=>[x,maps[x]]))};
 await writeFile(resolve(dir,'scene.json'),JSON.stringify(data,null,2)+'\n');
 results.push({name:biome,layers:layers.length,weather:theme.weather,mood:theme.mood});
}
await writeFile(resolve(OUTPUT,'manifest.json'),JSON.stringify({version:4,biomes:results,fullNativePixel:true},null,2)+'\n');
console.log('PIXEL_V4_BIOMES_BUILT '+JSON.stringify(results));
