/**
 * V4 Final: native Remotion moving scene + nearest-neighbour 3x upscale
 * and overlap-crossfaded V3 Day & Night user-supplied music.
 * Strong failures for broken renders, codec, frame count, black gaps and
 * duplicate stills. Produces contact sheet and decodes the whole file.
 */
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,existsSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';

const FPS=30, FRAMES=360, W=1080, H=1920, SECONDS=12;
const SRC='assets/v3-chill-part01.b64';
const QA='out/v4-final-qa';
const SOURCE='out/v4-final-day-night-source.opus';
const NATIVE='out/v4-final-native-360x640.mp4';
const FINAL='out/sunset-harbor-v4-FINAL-1080p.mp4';
mkdirSync(QA,{recursive:true});
const exec=(bin,args,quiet=false)=>{
 const p=spawnSync(bin,args,{encoding:'utf8',stdio:quiet?'pipe':'inherit',maxBuffer:32*1024*1024});
 if(p.error||p.status!==0)throw Error(bin+' failed: '+(p.stderr||p.stdout||p.error||p.status));
 return p.stdout||'';
};
const probe=file=>JSON.parse(exec('ffprobe',['-v','error','-count_frames',
 '-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,channels,sample_rate:format=duration,size',
 '-of','json',file],true));
if(!existsSync(SRC))throw Error('Original V3 user-supplied Day & Night excerpt missing — no substitute permitted');
writeFileSync(SOURCE,Buffer.from(readFileSync(SRC,'utf8').replace(/\s+/g,''),'base64'));
const shortDuration=Number(probe(SOURCE).format.duration);
if(!Number.isFinite(shortDuration)||shortDuration<2)throw Error('Score excerpt too short');
const npx=process.platform==='win32'?'npx.cmd':'npx';
exec(npx,['remotion','render','src/index.ts','SunsetHarborV4Final',NATIVE,
 '--codec','h264','--concurrency','2','--log','error']);

// Decode the exact owner-supplied four-second segment to independent PCM.
// FFmpeg's earlier asplit/adelay mix ended at the first excerpt! Build an
// explicit sample-accurate crossfade score, then encode the full 12s stream.
const SR=48000, PCM='out/v4-final-score-f32le.pcm';
const extracted=spawnSync('ffmpeg',['-v','error','-i',SOURCE,'-vn','-ac','1',
 '-ar',String(SR),'-f','f32le','-'],{encoding:null,maxBuffer:8*1024*1024});
if(extracted.status!==0||extracted.error)throw Error('Score decode failed: '+extracted.stderr?.toString());
const pcm=extracted.stdout;
if(!pcm||pcm.length<SR*2*4)throw Error('No real score PCM decoded');
const source=new Float32Array(pcm.length/4);
for(let i=0;i<source.length;i++)source[i]=pcm.readFloatLE(i*4);
const overlap=0.42;
const excerptSamples=Math.min(Math.floor((shortDuration-0.02)*SR),Math.floor(3.86*SR));
const crossSamples=Math.round(overlap*SR),step=excerptSamples-crossSamples;
const destSamples=Math.round(SECONDS*SR);
const output=new Float32Array(destSamples);
const count=Math.ceil((destSamples-excerptSamples)/step)+1;
for(let repeat=0;repeat<count;repeat++){
 const offset=repeat*step;
 for(let j=0;j<excerptSamples&&offset+j<destSamples;j++){
   let gain=1;
   if(j<crossSamples)gain=j/crossSamples;
   if(j>=excerptSamples-crossSamples)gain=Math.min(gain,(excerptSamples-1-j)/crossSamples);
   output[offset+j]+=source[j]*Math.max(0,gain);
 }
}
// A transparent short opening and 900ms ending fade. Small headroom prevents
// transients from clipping when original notes coincide in overlap sections.
for(let i=0;i<destSamples;i++){
 const inGain=Math.min(1,i/(0.12*SR));
 const outGain=Math.min(1,(destSamples-1-i)/(0.9*SR));
 output[i]*=0.87*Math.max(0,Math.min(inGain,outGain));
}
const scoreRms=[];
for(let sec=0;sec<SECONDS;sec++){
 let power=0;for(let j=sec*SR;j<(sec+1)*SR;j++)power+=output[j]*output[j];
 scoreRms.push(Math.sqrt(power/SR));
}
if(scoreRms.slice(0,11).some((r)=>r<0.002))throw Error('Silent music second in PCM master: '+scoreRms.join(', '));
const pcmBuffer=Buffer.allocUnsafe(destSamples*4);
for(let i=0;i<destSamples;i++)pcmBuffer.writeFloatLE(output[i],i*4);
writeFileSync(PCM,pcmBuffer);
// Encode from an explicit twelve-second PCM track — no input loop ambiguity.
exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',NATIVE,
 '-f','f32le','-ar',String(SR),'-ac','1','-i',PCM,'-map','0:v:0','-map','1:a:0',
 '-vf','scale='+W+':'+H+':flags=neighbor,format=yuv420p',
 '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',
 '-r','30','-c:a','aac','-b:a','160k','-ar',String(SR),'-t',String(SECONDS),
 '-movflags','+faststart',FINAL]);

const meta=probe(FINAL);
const v=meta.streams.find(s=>s.codec_type==='video');
const a=meta.streams.find(s=>s.codec_type==='audio');
if(!v||v.codec_name!=='h264'||v.width!==W||v.height!==H||
 v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==FRAMES||
 !a||a.codec_name!=='aac'||Math.abs(Number(meta.format.duration)-SECONDS)>0.15)
 throw Error('Delivery contract mismatch: '+JSON.stringify(meta));
exec('ffmpeg',['-v','error','-xerror','-i',FINAL,'-f','null','-']);
// Verify decoded AAC audio is present in EVERY second, not just at the start.
const audioCheck=spawnSync('ffmpeg',['-v','error','-i',FINAL,'-vn','-ac','1',
 '-ar','8000','-f','f32le','-'],{encoding:null,maxBuffer:2*1024*1024});
if(audioCheck.status!==0||audioCheck.error)throw Error('AAC decode failure');
const outputAudioRms=[];
for(let sec=0;sec<SECONDS;sec++){
 const start=sec*8000*4,end=Math.min(audioCheck.stdout.length,(sec+1)*8000*4);
 if(end-start<7500*4)throw Error('Truncated AAC second '+sec);
 let sum=0;
 for(let k=start;k<end;k+=4){const x=audioCheck.stdout.readFloatLE(k);sum+=x*x;}
 outputAudioRms.push(Math.sqrt(sum/((end-start)/4)));
}
if(outputAudioRms.slice(0,11).some(x=>x<0.001))
 throw Error('Decoded AAC has missing music segments: '+JSON.stringify(outputAudioRms));


// Nine scene-space checkpoints, from opening through final music fade.
const checkpoints=[0,45,90,135,180,225,270,315,359];
const frames=[];
for(const idx of checkpoints){
 const name='frame-'+String(idx).padStart(3,'0')+'.png',path=QA+'/'+name;
 exec('ffmpeg',['-v','error','-y','-i',FINAL,
 '-vf','select=eq(n\\,'+idx+')','-vsync','0','-frames:v','1',path]);
 if(!existsSync(path)||statSync(path).size<1024)throw Error('QA image missing: '+path);
 frames.push({frame:idx,path,sha256:createHash('sha256').update(readFileSync(path)).digest('hex')});
}
if(new Set(frames.map(f=>f.sha256)).size!==frames.length)
 throw Error('Identical keyframes: possible still-frame video');

// FFmpeg contact sheet is generated from actual decoded MP4 captures.
const CONTACT=QA+'/sunset-harbor-v4-contact-sheet.png';
exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','1',
 '-pattern_type','glob','-i',QA+'/frame-*.png','-vf',
 'scale=180:320:flags=neighbor,tile=3x3:padding=8:margin=8',
 '-frames:v','1',CONTACT]);
if(!existsSync(CONTACT)||statSync(CONTACT).size<1024)throw Error('QA contact sheet missing');
const blacks=exec('ffmpeg',['-i',FINAL,'-vf','blackdetect=d=0.07:pix_th=0.075:pic_th=0.99',
 '-an','-f','null','-'],true);
if(/black_start:/i.test(blacks))throw Error('Black frame interval detected: '+blacks.match(/black_start:.*$/m)?.[0]);

const result={
 verified:true,render:'Remotion 4 native artwork, 3x nearest-neighbour 1080p master',
 file:FINAL,frames:FRAMES,decodedFrames:Number(v.nb_read_frames),fps:FPS,
 width:v.width,height:v.height,videoCodec:v.codec_name,audioCodec:a.codec_name,
 audioChannels:a.channels,duration:Number(meta.format.duration),fullFFmpegDecode:true,
 audioProvenance:'V3 user-supplied Day & Night excerpt (original recording not fully available)',
 excerptSeconds:shortDuration,crossfadeSeconds:overlap,audioRmsPerSecond:outputAudioRms,
 caution:'Check owner audio rights before public music redistribution.',
 bytes:statSync(FINAL).size,contactSheet:CONTACT,checkpoints:frames
};
writeFileSync(QA+'/verification.json',JSON.stringify(result,null,2)+'\n');
console.log('V4_FINAL_VERIFIED '+JSON.stringify(result));
