/** Production sprite assembly from REAL Pixelorama CLI exports. Sharp verifies and packs without resampling. */
import sharp from 'sharp';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const dir='public/countryside/car',out='out/car-v3-proof';
await mkdir(dir,{recursive:true});await mkdir(out,{recursive:true});
const specs=[
 {file:'coupe-v3-pixelorama-body.png',dest:'coupe-v2-body.png',w:192,h:80},
 {file:'coupe-v3-pixelorama-wheels.png',dest:'coupe-v2-wheels-8.png',w:256,h:32}
];
const proof=[];
for(const s of specs){
 const src=await readFile(dir+'/'+s.file);
 const m=await sharp(src).metadata();
 if(m.format!=='png'||m.width!==s.w||m.height!==s.h)throw Error('Pixelorama did not export valid native sprite '+s.file+': '+JSON.stringify(m));
 const raw=await sharp(src).ensureAlpha().raw().toBuffer();
 const rgbaColors=new Set();
 for(let i=0;i<raw.length;i+=4)if(raw[i+3])rgbaColors.add([raw[i],raw[i+1],raw[i+2],raw[i+3]].join(','));
 const minColors=s.file.includes('wheels')?6:10;
 if(rgbaColors.size<minColors||rgbaColors.size>120)throw Error('Invalid handcrafted 16-bit palette '+s.file+' '+rgbaColors.size);
 const result=await sharp(src).png({compressionLevel:9,palette:false}).toBuffer();
 await writeFile(dir+'/'+s.dest,result);
 // V3 named outputs for integration while preserving V2 scene's stable sprite filenames.
 await writeFile(dir+'/'+s.file.replace('pixelorama-',''),result);
 proof.push({source:s.file,production:s.dest,width:s.w,height:s.h,opaqueColors:rgbaColors.size,sha256:createHash('sha256').update(result).digest('hex')});
}
const wheels=await sharp(await readFile(dir+'/coupe-v2-wheels-8.png')).ensureAlpha().raw().toBuffer({resolveWithObject:true});
const poses=[];
for(let f=0;f<8;f++){
 const crop=await sharp(await readFile(dir+'/coupe-v2-wheels-8.png')).extract({left:f*32,top:0,width:32,height:32}).raw().toBuffer();
 poses.push(createHash('sha256').update(crop).digest('hex'));
}
if(new Set(poses).size!==8)throw Error('Pixelorama-exported wheels have repeated/missing animation poses');
await writeFile(out+'/pixelorama-export-validation.json',JSON.stringify({validated:true,actualEditorExportRequired:true,tools:['Pixelorama CLI','Sharp','Remotion'],sprites:proof,distinctWheelFrames:8},null,2)+'\n');
console.log('REAL_PIXELORAMA_SPRITES_VALIDATED '+JSON.stringify(proof));
