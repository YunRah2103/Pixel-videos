/**
 * Agent 3 / V5: genuine frame-rendered proof, owner-supplied soundtrack,
 * nine decoded keyframes, three close-up animation crops, V4 comparison.
 * Run: npm install && node scripts/render-v5-story.mjs
 * Creates an isolated temporary Remotion registration, NEVER edits Root.tsx.
 */
import {spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,readFileSync,writeFileSync,unlinkSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';
const FPS=30,COUNT=360,DURATION=12,SR=48000,QA='out/v5-story-qa';
const ENTRY='src/__v5_story_entry.tsx';
const NATIVE='out/v5-story-native-360x640.mp4';
const OUTPUT='out/sunset-harbor-v5-AGENT3-1080p.mp4';
const PCM='out/v5-story-score-f32le.pcm';
const AUDIO='out/v5-story-original-day-night.opus';
mkdirSync(QA,{recursive:true});
function cmd(bin,args,quiet=false){
 const p=spawnSync(bin,args,{encoding:'utf8',stdio:quiet?'pipe':'inherit',maxBuffer:48*1024*1024});
 if(p.error||p.status!==0)throw new Error(bin+' failed '+(p.stderr||p.stdout||p.error||p.status));
 return p.stdout||'';
}
const probe=file=>JSON.parse(cmd('ffprobe',['-v','error','-count_frames',
 '-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,channels,sample_rate',
 '-of','json',file],true));
const npx=process.platform==='win32'?'npx.cmd':'npx';
function frameGrab(idx,output,filter=''){
 const filters='select=eq(n\\,'+idx+')'+(filter?','+filter:'');
 cmd('ffmpeg',['-v','error','-y','-i',OUTPUT,'-vf',filters,
  '-vsync','0','-frames:v','1',output]);
 if(!existsSync(output)||statSync(output).size<500)throw Error('Still missing '+output);
}
const source='assets/v3-chill-part01.b64';
if(!existsSync(source))throw Error('Missing ORIGINAL owner-provided V3 Day & Night excerpt');
writeFileSync(AUDIO,Buffer.from(readFileSync(source,'utf8').replace(/\s+/g,''),'base64'));
const duration=Number(probe(AUDIO).format.duration);
if(!Number.isFinite(duration)||duration<2)throw Error('Soundtrack excerpt missing/invalid');
writeFileSync(ENTRY,`import React from 'react';
import {registerRoot,Composition} from 'remotion';
import {SunsetHarborV5StoryProof} from './scenes/v5/StoryV5Proof';
const Root=()=> <Composition id="SunsetHarborV5StoryProof" component={SunsetHarborV5StoryProof} durationInFrames={360} fps={30} width={360} height={640}/>;
registerRoot(Root);
`);
try{
 cmd(npx,['remotion','render',ENTRY,'SunsetHarborV5StoryProof',NATIVE,
  '--codec','h264','--concurrency','2','--log','error']);
 // Decode original excerpt to mono Float32 once, repeat using 420ms equal
 // crossfades. The V4 master used this process; no replacement music or SFX.
 const parsed=spawnSync('ffmpeg',['-v','error','-i',AUDIO,'-vn',
  '-ac','1','-ar',String(SR),'-f','f32le','-'],
  {encoding:null,maxBuffer:8*1024*1024});
 if(parsed.status!==0||parsed.error)throw Error('Original audio decode failed');
 const src=parsed.stdout;
 const len=src.length/4;
 if(len<SR*2)throw Error('Decoded music too short');
 const overlap=Math.round(.42*SR),excerpt=Math.min(len-960,Math.floor(3.86*SR));
 const advance=excerpt-overlap;
 const out=new Float32Array(DURATION*SR);
 const clips=Math.ceil((out.length-excerpt)/advance)+1;
 for(let k=0;k<clips;k++){
  const offset=k*advance;
  for(let j=0;j<excerpt&&offset+j<out.length;j++){
   const fadeIn=Math.min(1,j/overlap);
   const fadeOut=Math.min(1,(excerpt-1-j)/overlap);
   out[offset+j]+=src.readFloatLE(j*4)*Math.max(0,Math.min(fadeIn,fadeOut));
  }
 }
 const scoreCheck=[];
 for(let s=0;s<DURATION;s++){
  let sum=0;
  for(let i=s*SR;i<(s+1)*SR;i++){
   const tail=Math.min(1,(out.length-1-i)/(.85*SR));
   const head=Math.min(1,i/(.12*SR));
   out[i]*=.88*Math.max(0,Math.min(tail,head));
   sum+=out[i]**2;
  }
  scoreCheck.push(Math.sqrt(sum/SR));
 }
 if(scoreCheck.slice(0,11).some(v=>v<.0015))throw Error('Missing score section '+scoreCheck);
 const buffer=Buffer.allocUnsafe(out.length*4);
 for(let i=0;i<out.length;i++)buffer.writeFloatLE(out[i],i*4);
 writeFileSync(PCM,buffer);
 cmd('ffmpeg',['-v','error','-y','-i',NATIVE,
  '-f','f32le','-ar',String(SR),'-ac','1','-i',PCM,
  '-map','0:v:0','-map','1:a:0','-vf','scale=1080:1920:flags=neighbor,format=yuv420p',
  '-c:v','libx264','-preset','medium','-crf','17',
  '-pix_fmt','yuv420p','-r',String(FPS),'-c:a','aac','-b:a','160k',
  '-ar',String(SR),'-t',String(DURATION),'-movflags','+faststart',OUTPUT]);
 const meta=probe(OUTPUT),v=meta.streams.find(s=>s.codec_type==='video');
 const a=meta.streams.find(s=>s.codec_type==='audio');
 if(!v||v.codec_name!=='h264'||v.width!==1080||v.height!==1920||
  v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==COUNT||
  !a||a.codec_name!=='aac'||Math.abs(Number(meta.format.duration)-12)>.15)
  throw Error('MP4 delivery contract failed: '+JSON.stringify(meta));
 cmd('ffmpeg',['-v','error','-xerror','-i',OUTPUT,'-f','null','-']);
 // Verify each of 12 decoded AAC seconds, not merely existence of an audio track.
 const audio=spawnSync('ffmpeg',['-v','error','-i',OUTPUT,'-vn','-ac','1','-ar','8000','-f','f32le','-'],
  {encoding:null,maxBuffer:2*1024*1024});
 if(audio.status!==0||audio.error)throw Error('Audio stream cannot decode');
 const audible=[];
 for(let s=0;s<12;s++){
  const start=s*8000*4,end=Math.min(audio.stdout.length,(s+1)*8000*4);
  if(end-start<7500*4)throw Error('Audio truncated in second '+s);
  let sum=0;
  for(let j=start;j<end;j+=4)sum+=audio.stdout.readFloatLE(j)**2;
  audible.push(Math.sqrt(sum/((end-start)/4)));
 }
 if(audible.slice(0,11).some(x=>x<.0009))
  throw Error('Decoded AAC contains silent sections '+JSON.stringify(audible));
 const checkpoints=[0,45,90,135,180,225,270,315,359];
 const captures=[];
 for(const f of checkpoints){
  const file=QA+'/frame-'+String(f).padStart(3,'0')+'.png';
  frameGrab(f,file);
  captures.push({frame:f,file,sha256:createHash('sha256').update(readFileSync(file)).digest('hex')});
 }
 if(new Set(captures.map(x=>x.sha256)).size!==9)
  throw Error('Duplicate keyframes: static/padded story was rendered');
 cmd('ffmpeg',['-v','error','-y','-framerate','1','-pattern_type','glob',
  '-i',QA+'/frame-*.png','-vf','scale=180:320:flags=neighbor,tile=3x3:padding=8:margin=8',
  '-frames:v','1',QA+'/contact-sheet.png']);
 // Truly frame-derived enlarged close crops (rather than CSS mockups).
 for(const [id,f,rect] of [
  ['arrival',150,'crop=330:315:510:1320,scale=660:630:flags=neighbor'],
  ['handhold',235,'crop=330:315:510:1320,scale=660:630:flags=neighbor'],
  ['yacht',180,'crop=420:360:500:960,scale=630:540:flags=neighbor']]){
  frameGrab(f,QA+'/crop-'+id+'.png',rect);
 }
 // Actual V4 frame at the SAME timestamp, compared at native pixel resolution.
 const V4=QA+'/v4-reference-frame-225.png';
 cmd(npx,['remotion','still','src/index.ts','SunsetHarborV4Final',V4,
  '--frame=225','--log','error']);
 cmd('ffmpeg',['-v','error','-y','-i',V4,'-i',QA+'/frame-225.png',
  '-filter_complex',
  '[0:v]scale=360:640:flags=neighbor[a];[1:v]scale=360:640:flags=neighbor[b];[a][b]hstack=inputs=2[v]',
  '-map','[v]','-frames:v','1',QA+'/v4-v5-comparison.png']);
 const black=cmd('ffmpeg',['-i',OUTPUT,'-vf',
  'blackdetect=d=0.07:pix_th=0.075:pic_th=0.99','-an','-f','null','-'],true);
 if(/black_start:/i.test(black))throw Error('Black frame gap detected');
 const report={verified:true,file:OUTPUT,duration:Number(meta.format.duration),
  fps:30,decodedFrames:Number(v.nb_read_frames),width:v.width,height:v.height,
  codec:v.codec_name,audioCodec:a.codec_name,fullDecode:true,
  soundtrack:'unchanged owner-supplied V3 Day & Night four-second excerpt with V4-style crossfades',
  sourceExcerptSeconds:duration,aacRmsBySecond:audible,
  frameCaptures:captures,contactSheet:QA+'/contact-sheet.png',
  crops:['arrival','handhold','yacht'].map(x=>QA+'/crop-'+x+'.png'),
  comparison:QA+'/v4-v5-comparison.png',
  caution:'Track rights and supply full original 12s source if available; no substituted music.',
  sizeBytes:statSync(OUTPUT).size};
 writeFileSync(QA+'/verification.json',JSON.stringify(report,null,2)+'\n');
 console.log('V5_STORY_VERIFIED '+JSON.stringify(report));
}finally{
 if(existsSync(ENTRY))unlinkSync(ENTRY);
}
