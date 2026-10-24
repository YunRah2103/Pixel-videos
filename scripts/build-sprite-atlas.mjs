import sharp from 'sharp';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const manifest=JSON.parse(await readFile(resolve(root,'out/toolkit/assets-report.json'),'utf8'));
const configs=JSON.parse(await readFile(resolve(root,'studio/atlas.config.json'),'utf8'));
const limit=configs.width||512, gap=configs.padding??2;
if(!Number.isInteger(limit)||limit<32||limit>8192||!Number.isInteger(gap)||gap<1||gap>16)throw Error('Invalid atlas constraints');
const frames=[];
for(const a of manifest.entries){
 const src=resolve(root,a.destination);
 const meta=await sharp(src).metadata();
 const cuts=configs.frames?.[a.id]||{columns:1,rows:1};
 if(meta.format!=='png'||meta.width%cuts.columns||meta.height%cuts.rows)throw Error('Frames do not divide source '+a.id);
 const w=meta.width/cuts.columns,h=meta.height/cuts.rows;
 for(let j=0;j<cuts.rows;j++)for(let i=0;i<cuts.columns;i++){
  const input=await sharp(src).extract({left:i*w,top:j*h,width:w,height:h}).png().toBuffer();
  frames.push({id:(cuts.columns*cuts.rows===1)?a.id:a.id+'-'+String(j*cuts.columns+i).padStart(2,'0'),source:a.id,input,w,h});
 }
}
frames.sort((a,b)=>b.h-a.h||b.w-a.w||a.id.localeCompare(b.id));
let x=gap,y=gap,row=0,height=0;
for(const f of frames){
 if(f.w+2*gap>limit)throw Error('Sprite too wide for atlas '+f.id);
 if(x+f.w+gap>limit){x=gap;y+=row+gap;row=0;}
 f.x=x;f.y=y;x+=f.w+gap;row=Math.max(row,f.h);
 height=Math.max(height,f.y+f.h+gap);
}
if(height>8192)throw Error('Atlas too tall');
const layers=frames.map(f=>({input:f.input,left:f.x,top:f.y}));
const image=await sharp({create:{width:limit,height,channels:4,background:'#00000000'}})
 .composite(layers).png({palette:false}).toBuffer();
const output=resolve(root,'public/toolkit/atlas');
await mkdir(output,{recursive:true});
await writeFile(resolve(output,'atlas.png'),image);
const metadata={
 version:1,scale:1,padding:gap,width:limit,height,
 frames:Object.fromEntries(frames.map(f=>[f.id,{x:f.x,y:f.y,w:f.w,h:f.h,source:f.source,
  uv:[f.x/limit,f.y/height,(f.x+f.w)/limit,(f.y+f.h)/height]}]))
};
await writeFile(resolve(output,'atlas.json'),JSON.stringify(metadata,null,2)+'\n');
console.log('PIXEL_ATLAS_OK '+JSON.stringify({sprites:frames.length,width:limit,height,path:'public/toolkit/atlas/atlas.png'}));
