/**
 * Exact twelve-second native Remotion/FFmpeg final renderer.
 * Never falls back to V4/V5, generic placeholders or toolkit smoke-test imagery.
 */
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,existsSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';
import sharp from 'sharp';

const FPS=30,FRAMES=360,W=1080,H=1920,SECONDS=12;
const DIR='out/countryside-final-qa';
const NATIVE='out/countryside-native-360x640.mp4';
const FINAL='out/countryside-drive-final-1080p.mp4';
mkdirSync(DIR,{recursive:true});
const exec=(bin,args)=>{
 const p=spawnSync(bin,args,{encoding:'utf8',maxBuffer:32*1024*1024});
 if(p.error||p.status!==0)throw Error(bin+' '+args.join(' ')+' FAILED:\n'+(p.stderr||p.stdout||p.error||p.status));
 return (p.stdout||'')+'\n'+(p.stderr||'');
};
const probe=(file)=>JSON.parse(exec('ffprobe',['-v','error','-count_frames',
 '-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt:format=duration,size',
 '-of','json',file]));
// Regenerate the original edited native-pixel world from reproducible source
// in every Actions render, never rely on untracked ephemeral image files.
exec('node',['studio/countryside/world/build-world-art.mjs']);
exec('node',['scripts/check-countryside-ready.mjs']);
const npx=process.platform==='win32'?'npx.cmd':'npx';
exec(npx,['remotion','render','src/index.ts','CountrysideDrive',NATIVE,
 '--codec','h264','--concurrency','2','--log','error']);
const np=probe(NATIVE);
const nv=np.streams.find(x=>x.codec_type==='video');
if(!nv||nv.width!==360||nv.height!==640||nv.r_frame_rate!=='30/1'||
 Number(nv.nb_read_frames)!==FRAMES)throw Error('Native frame check failed '+JSON.stringify(np));
exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',NATIVE,
 '-vf','scale=1080:1920:flags=neighbor,format=yuv420p',
 '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',
 '-r','30','-frames:v',String(FRAMES),'-an','-movflags','+faststart',FINAL]);
const meta=probe(FINAL),v=meta.streams.find(x=>x.codec_type==='video');
if(!v||v.codec_name!=='h264'||v.pix_fmt!=='yuv420p'||v.width!==W||
 v.height!==H||v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==FRAMES||
 Math.abs(Number(meta.format.duration)-SECONDS)>0.06)
 throw Error('FINAL MP4 CONTRACT FAIL: '+JSON.stringify(meta));
exec('ffmpeg',['-v','error','-xerror','-i',FINAL,'-f','null','-']);
const blacks=exec('ffmpeg',['-hide_banner','-i',FINAL,
 '-vf','blackdetect=d=0.065:pix_th=0.075:pic_th=0.99',
 '-an','-f','null','-']);
if(/black_start:/i.test(blacks))throw Error('BLACK GAP DETECTED: '+blacks.match(/black_start:.*$/m)?.[0]);
const checkpoints=[0,45,90,135,180,225,270,315,359],samples=[];
for(const f of checkpoints){
 const path=DIR+'/frame-'+String(f).padStart(3,'0')+'.png';
 exec('ffmpeg',['-v','error','-y','-i',FINAL,
 '-vf','select=eq(n\\,'+f+')','-fps_mode','vfr','-frames:v','1',path]);
 if(!existsSync(path)||statSync(path).size<1024)throw Error('Could not decode '+path);
 const content=readFileSync(path);
 // Use separate sharp pipelines. Reusing a resized Sharp instance here
 // would accidentally compare different dimensions and hide a grid defect.
 const shrunk=await sharp(content).resize(360,640,{kernel:'nearest'})
   .removeAlpha().raw().toBuffer({resolveWithObject:true});
 const reconstructed=await sharp(shrunk.data,{raw:{
   width:shrunk.info.width,height:shrunk.info.height,channels:shrunk.info.channels
 }}).resize(W,H,{kernel:'nearest'}).raw().toBuffer();
 const raw=await sharp(content).removeAlpha().raw().toBuffer({resolveWithObject:true});
 if(reconstructed.length!==raw.data.length)throw Error('Grid comparison buffers differ in size');
 // Codec chroma conversion softens a few edge pixels; report the deviation,
 // rather than silently declaring art crisp based only on a metadata test.
 let sum=0;const n=Math.min(reconstructed.length,raw.data.length);
 for(let i=0;i<n;i++)sum+=Math.abs(reconstructed[i]-raw.data[i]);
 samples.push({frame:f,path,sha256:createHash('sha256').update(content).digest('hex'),
  gridMeanAbsoluteError:Math.round(100*sum/n)/100});
}
if(new Set(samples.map(x=>x.sha256)).size!==samples.length)
 throw Error('DUPLICATE CHECKPOINT FRAMES: no convincing movement across the full duration');
const sheet=DIR+'/countryside-contact-sheet.png';
exec('ffmpeg',['-hide_banner','-loglevel','error','-y',
 '-framerate','1','-pattern_type','glob','-i',DIR+'/frame-*.png',
 '-vf','scale=180:320:flags=neighbor,tile=3x3:padding=6:margin=6',
 '-frames:v','1',sheet]);
if(!existsSync(sheet)||statSync(sheet).size<1024)throw Error('Missing decoded MP4 contact sheet');
const result={
 technicalVerified:true,artisticSignoff:false,
 final:FINAL,sourceComposition:'CountrysideDrive',native:'360x640',
 output:'1080x1920 exact 3x nearest-neighbour',fps:FPS,frames:FRAMES,
 decodedFrames:Number(v.nb_read_frames),codec:v.codec_name,pixelFormat:v.pix_fmt,
 duration:Number(meta.format.duration),bytes:statSync(FINAL).size,
 fullDecode:true,blackIntervals:0,sourceAudio:'none (silent original film)',
 captureCount:samples.length,allCapturesDistinct:true,checkpoints:samples,
 contactSheet:sheet,
 pendingManualReview:['visual playback at mobile scale','car shape/wheels/ground contact',
  'tree originality/variation','seamless parallax','palette and visible source-pixel grid',
  'approval of actual Agent 1–3 original assets and proof MP4s']
};
writeFileSync(DIR+'/verification.json',JSON.stringify(result,null,2)+'\n');
console.log('COUNTRYSIDE_TECHNICAL_QA_PASS '+JSON.stringify(result));
