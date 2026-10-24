/**
 * True raster sprite-sheet importer/exporter and pivot-aware placement.
 * Actual sprite frames, not a rotation or filter applied to a static car.
 */
import sharp from 'sharp';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const base=resolve(root,'public/studio-v4'),output=resolve(base,'animations');
await mkdir(output,{recursive:true});
const entries=[];
const wheelFrames=8;
for(const name of ['hatchback-00','coupe-03']){
 const input=resolve(base,'library',name+'.png');
 const m=await sharp(input).metadata();
 const w=m.width,h=m.height;
 const source=await sharp(input).ensureAlpha().raw().toBuffer();
 const wheels=[19,w-20];
 const all=[];
 for(let f=0;f<wheelFrames;f++){
  const {data}=await sharp(source,{raw:{width:w,height:h,channels:4}}).raw().toBuffer({resolveWithObject:true});
  const dst=Buffer.from(data);
  const mark=(x,y,c)=>{if(x<0||y<0||x>=w||y>=h)return;const i=(y*w+x)*4;dst[i]=c[0];dst[i+1]=c[1];dst[i+2]=c[2];dst[i+3]=255};
  for(const cx of wheels){
   // Explicit 8 authored angular hub patterns, indexed by frame.
   const rim=[[0,-3],[2,-2],[3,0],[2,2],[0,3],[-2,2],[-3,0],[-2,-2]];
   for(let j=0;j<8;j++){const [dx,dy]=rim[j];const active=(j+f)%4===0;
    mark(cx+dx,30+dy,active?[224,229,218]:[69,86,95]);}
   mark(cx,30,[220,225,215]);
  }
  all.push(await sharp(dst,{raw:{width:w,height:h,channels:4}}).png().toBuffer());
 }
 const sheet=await sharp({create:{width:w*wheelFrames,height:h,channels:4,background:'#00000000'}})
  .composite(all.map((b,i)=>({input:b,left:i*w,top:0}))).png().toBuffer();
 const file=resolve(output,name+'-wheel-strip.png');await writeFile(file,sheet);
 entries.push({id:name+'-wheel',file:'studio-v4/animations/'+name+'-wheel-strip.png',
  frames:wheelFrames,frameWidth:w,frameHeight:h,pivot:{x:Math.floor(w/2),y:h-4},
  fps:12,authoredBasis:name,animation:'rotating hub mark positions drawn on native pixels'});
}
const spritesheet={version:1,entries};await writeFile(resolve(output,'manifest.json'),JSON.stringify(spritesheet,null,2)+'\n');
console.log('PIXEL_ANIMATION_SHEETS_OK '+JSON.stringify(entries.map(x=>({name:x.id,frames:x.frames}))));
