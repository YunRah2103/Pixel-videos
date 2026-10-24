import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname,relative,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import sharp from 'sharp';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const ASSET_ROOT=resolve(ROOT,'public','toolkit');
const CONFIG=resolve(ROOT,'studio','pixel-assets.json');
const spec=JSON.parse(await readFile(CONFIG,'utf8'));
const safe=(base,p)=>{
 if(typeof p!=='string'||p.includes('\0'))throw Error('Invalid path');
 const full=resolve(base,p);
 if(full!==base&&!full.startsWith(base+sep))throw Error('Path escapes root: '+p);
 return full;
};
const ensure=(condition,msg)=>{if(!condition)throw Error(msg);};
const report=[];
for(const sprite of spec.sprites){
 ensure(/^[a-z0-9-]+$/.test(sprite.id),'Unsafe id: '+sprite.id);
 const rows=sprite.rows, width=rows[0]?.length, height=rows.length;
 ensure(width>0&&height>0&&width<=512&&height<=512,'Bad sprite size '+sprite.id);
 ensure(rows.every(r=>r.length===width),'Uneven sprite rows: '+sprite.id);
 ensure(Object.keys(sprite.palette).every(k=>k.length===1),'Palette keys must be single characters');
 const pixels=Buffer.alloc(width*height*4);
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){
  const color=sprite.palette[rows[y][x]];
  ensure(color!==undefined,'Unknown palette code in '+sprite.id);
  const i=(y*width+x)*4;
  if(color===null)continue;
  ensure(/^#[0-9a-fA-F]{6}$/.test(color),'Bad hex for '+sprite.id);
  pixels[i]=parseInt(color.slice(1,3),16);
  pixels[i+1]=parseInt(color.slice(3,5),16);
  pixels[i+2]=parseInt(color.slice(5,7),16);
  pixels[i+3]=255;
 }
 const destination=safe(ASSET_ROOT,'sprites/'+sprite.id+'.png');
 await mkdir(dirname(destination),{recursive:true});
 await sharp(pixels,{raw:{width,height,channels:4}}).png({compressionLevel:9}).toFile(destination);
 report.push({id:sprite.id,kind:'hand-authored sprite',width,height,destination:relative(ROOT,destination)});
}
for(const item of spec.imports||[]){
 ensure(/^[a-z0-9-]+$/.test(item.id),'Unsafe import id');
 ensure(Number.isInteger(item.scale||1)&&(item.scale||1)>=1&&(item.scale||1)<=4,'scale 1..4 only');
 const src=safe(resolve(ROOT,'studio'),'imports/'+item.source);
 const dest=safe(ASSET_ROOT,'imports/'+item.id+'.png');
 const meta=await sharp(src).metadata();
 ensure(meta.format==='png'&&meta.width>0&&meta.height>0,'Imports must be PNG');
 await mkdir(dirname(dest),{recursive:true});
 await sharp(src).resize(meta.width*(item.scale||1),meta.height*(item.scale||1),{kernel:'nearest'}).png().toFile(dest);
 report.push({id:item.id,kind:'imported pixel art',width:meta.width,height:meta.height,destination:relative(ROOT,dest)});
}
await mkdir(resolve(ROOT,'out','toolkit'),{recursive:true});
await writeFile(resolve(ROOT,'out','toolkit','assets-report.json'),JSON.stringify({verified:true,entries:report},null,2)+'\n');
console.log('PIXEL_ASSETS_BUILT '+JSON.stringify(report));
