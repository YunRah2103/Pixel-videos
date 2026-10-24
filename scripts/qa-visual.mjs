import sharp from 'sharp';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const out=resolve(root,'out','studio-v3');
const frameRoot=resolve(out,'frames'), video=resolve(out,'countryside-toolkit-proof-1080p.mp4');
const args=process.argv.slice(2);const ri=args.indexOf('--reference');
const reference=ri>=0?resolve(root,args[ri+1]):null;
const run=(cmd,opts)=>{const p=spawnSync(cmd,opts,{encoding:'utf8',maxBuffer:16*1024*1024});
 if(p.status!==0||p.error)throw Error(cmd+' failed '+(p.stderr||p.error||p.status));return p.stdout};
const probe=JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt:format=duration','-of','json',video]));
const v=probe.streams.find(s=>s.codec_type==='video');
if(!v||v.width!==1080||v.height!==1920||v.codec_name!=='h264'||v.pix_fmt!=='yuv420p'||v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==90)throw Error('Unexpected video properties');
run('ffmpeg',['-v','error','-xerror','-i',video,'-f','null','-']);
const ids=[0,11,22,33,44,55,66,77,89],samples=[],allHashes=[];
let longestStill=1,still=1,blackFrames=0;
let prev='';
for(let f=0;f<90;f++){
 const bytes=await readFile(resolve(frameRoot,'frame-'+String(f).padStart(3,'0')+'.png'));
 const hash=createHash('sha256').update(bytes).digest('hex');allHashes.push(hash);
 if(hash===prev)still++;else still=1;
 longestStill=Math.max(longestStill,still);prev=hash;
 if(ids.includes(f)){
  const {data,info}=await sharp(bytes).resize(90,160,{kernel:'nearest'}).removeAlpha().raw().toBuffer({resolveWithObject:true});
  let dark=0,totalLum=0;
  const colors=new Set();
  for(let p=0;p<data.length;p+=info.channels){
   const r=data[p],g=data[p+1],b=data[p+2];
   const lum=(.2126*r+.7152*g+.0722*b);
   totalLum+=lum;
   if(lum<12)dark++;
   colors.add((r>>4)<<8|(g>>4)<<4|(b>>4));
  }
  const blackRatio=dark/(info.width*info.height);if(blackRatio>.9)blackFrames++;
  samples.push({frame:f,blackRatio:Number(blackRatio.toFixed(4)),
   meanLuma:Number((totalLum/(info.width*info.height)).toFixed(2)),
   quantizedColorBins:colors.size,sha256:hash});
 }
}
const uniqueFrames=new Set(allHashes).size;
if(blackFrames||uniqueFrames<45||longestStill>9)throw Error('Frozen or blank footage detected '+JSON.stringify({blackFrames,uniqueFrames,longestStill}));
const thumbs=[];
for(let j=0;j<ids.length;j++){
 const b=await readFile(resolve(frameRoot,'frame-'+String(ids[j]).padStart(3,'0')+'.png'));
 thumbs.push({input:await sharp(b).resize(180,320,{kernel:'nearest'}).png().toBuffer(),left:(j%3)*180,top:Math.floor(j/3)*320});
}
await mkdir(out,{recursive:true});
await sharp({create:{width:540,height:960,channels:4,background:'#202537'}}).composite(thumbs).png().toFile(resolve(out,'contact-sheet.png'));
let referenceComparison=null;
if(reference){
 const raw=await sharp(reference).resize(90,160,{fit:'fill',kernel:'nearest'}).removeAlpha().raw().toBuffer();
 const movie=await sharp(resolve(frameRoot,'frame-044.png')).resize(90,160,{kernel:'nearest'}).removeAlpha().raw().toBuffer();
 let difference=0;for(let i=0;i<raw.length;i++)difference+=Math.abs(movie[i]-raw[i]);
 referenceComparison={reference,meanAbsolutePixelDifference:Number((difference/raw.length).toFixed(2)),
  note:'Numerical difference only. This is not an artistic similarity or quality score.'};
}
const report={verified:true,frames:90,uniqueFrames,longestIdenticalFrameRun:longestStill,
 motionEvidence:true,blackFrames,codec:'h264',pixFmt:'yuv420p',width:1080,height:1920,
 samples,referenceComparison,
 limitations:['Hash-based motion checks do not judge artistry, anatomy, colour harmony or visual quality.',
 'No generic aesthetic score. Review contact sheet and play the final MP4 before approval.']};
await writeFile(resolve(out,'visual-qa.json'),JSON.stringify(report,null,2)+'\n');
console.log('PIXEL_VISUAL_QA_PASS '+JSON.stringify({uniqueFrames,longestStill,blackFrames,contactSheet:'out/studio-v3/contact-sheet.png'}));
