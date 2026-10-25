import {mkdir,writeFile} from 'node:fs/promises';
import {resolve,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import sharp from 'sharp';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..'),file=process.argv[2];
if(!file)throw Error('Usage: node scripts/audit-pixel-art.mjs path/to/artwork.png [pixel-scale]');
const scale=Number(process.argv[3]||3);
if(!Number.isInteger(scale)||scale<1||scale>16)throw Error('Pixel scale must be integer 1-16');
const name=resolve(ROOT,file);if(!name.startsWith(ROOT+'/'))throw Error('Input must be inside repository');
const img=sharp(name),meta=await img.metadata();
if(meta.format!=='png'||meta.width*meta.height>3000000)throw Error('PNG under 3 million pixels required');
const {data,info}=await img.ensureAlpha().raw().toBuffer({resolveWithObject:true});
const at=(x,y)=>{const i=(y*info.width+x)*4;return data[i]+','+data[i+1]+','+data[i+2]+','+data[i+3]};
let misses=0,samples=0;const colors=new Set();
for(let y=0;y<info.height;y++)for(let x=0;x<info.width;x++)colors.add(at(x,y));
for(let y=0;y<info.height;y+=scale)for(let x=0;x<info.width;x+=scale){
 const base=at(x,y);
 for(let v=y;v<Math.min(y+scale,info.height);v++)for(let u=x;u<Math.min(x+scale,info.width);u++){
  samples++;if(at(u,v)!==base)misses++;
 }
}
const report={file:relative(ROOT,name),width:info.width,height:info.height,
colors:colors.size,assumed_pixel_scale:scale,grid_mismatch_fraction:Number((misses/samples).toFixed(5)),
metric_not_artistic_quality:true,
warning:'Off-grid fraction only meaningful for artwork already enlarged using this exact integer pixel scale; beautiful pixel art requires human review.'};
const out=resolve(ROOT,'out/artist-v4');await mkdir(out,{recursive:true});
await writeFile(resolve(out,'pixel-grid-audit.json'),JSON.stringify(report,null,2)+'\n');
console.log('PIXEL_GRID_AUDIT '+JSON.stringify(report));
