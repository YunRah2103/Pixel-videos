import {spawnSync} from 'node:child_process';
import {mkdirSync,existsSync,readFileSync,writeFileSync} from 'node:fs';

const W=1080,H=1920,FPS=30,FRAMES=360,DURATION=12;
const final='out/sunset-harbor-v3-FINAL-1080p.mp4';
mkdirSync('out/qa',{recursive:true});
const run=(exe,args,opts={})=>{
  const p=spawnSync(exe,args,{encoding:'utf8',stdio:opts.quiet?'pipe':'inherit'});
  if(p.status!==0)throw Error(`${exe} ${args.join(' ')} failed: ${p.stderr||p.stdout||p.error||p.status}`);
  return p.stdout||'';
};
const npx=process.platform==='win32'?'npx.cmd':'npx';
const embedded='assets/v3-chill-part01.b64';
if(!existsSync(embedded))throw Error('V3 requested Day & Night soundtrack missing. Do not silently substitute V2 jazz.');
const audio='out/v3-day-night-chill.opus';
writeFileSync(audio,Buffer.from(readFileSync(embedded,'utf8').replace(/\s+/g,''),'base64'));
run(npx,['remotion','render','src/index.ts','SunsetHarborV3Final','out/v3-final-360x640.mp4','--codec','h264']);
run('ffmpeg',['-hide_banner','-loglevel','error','-y',
  '-i','out/v3-final-360x640.mp4','-stream_loop','3','-i',audio,'-map','0:v:0','-map','1:a:0',
  '-vf',`scale=${W}:${H}:flags=neighbor,format=yuv420p`,
  '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',
  '-r',String(FPS),'-c:a','aac','-b:a','160k',
  '-af','afade=t=in:st=0:d=0.12,afade=t=out:st=10.9:d=1.1',
  '-t',String(DURATION),'-movflags','+faststart',final]);
const report=JSON.parse(run('ffprobe',['-v','error','-count_frames',
  '-show_entries','stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,sample_rate,channels:format=duration,size',
  '-of','json',final],{quiet:true}));
const v=report.streams.find(s=>s.codec_type==='video');
const a=report.streams.find(s=>s.codec_type==='audio');
if(!v||v.codec_name!=='h264'||v.width!==W||v.height!==H||v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==FRAMES||
 !a||a.codec_name!=='aac'||Math.abs(Number(report.format.duration)-DURATION)>0.12)
 throw Error('V3 QA mismatch: '+JSON.stringify(report));
run('ffmpeg',['-v','error','-i',final,'-f','null','-']);
for(const [name,frame] of [['opening',20],['middle',180],['ending',330]]){
 run('ffmpeg',['-hide_banner','-loglevel','error','-y',
   '-i',final,'-vf',`select=eq(n\\,${frame})`,'-vsync','0','-frames:v','1',`out/qa/v3-${name}.png`]);
}
const proof={verified:true,audioEdit:'user-supplied Day & Night excerpt looped gracefully for 12 seconds',file:final,audio:'user-supplied Day and Night chill clip',frames:FRAMES,fps:FPS,
 resolution:`${W}x${H}`,duration:report.format.duration,audioCodec:a.codec_name,
 audioChannels:a.channels,videoCodec:v.codec_name,sizeBytes:report.format.size,
 screenshots:['out/qa/v3-final-opening.png','out/qa/v3-final-middle.png','out/qa/v3-final-ending.png']};
writeFileSync('out/qa/v3-final-verification.json',JSON.stringify(proof,null,2));
console.log(JSON.stringify(proof,null,2));
