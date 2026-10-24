import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,existsSync,mkdirSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';

const FRAMES=360,FPS=30,W=1080,H=1920,DURATION=12;
const dir='out/v4-world';
const native=dir+'/sunset-harbor-v4-world-native-360p.mp4';
const movie=dir+'/sunset-harbor-v4-world-1080p.mp4';
mkdirSync(dir+'/qa',{recursive:true});
function run(cmd,args,quiet=false){
 const p=spawnSync(cmd,args,{stdio:quiet?'pipe':'inherit',encoding:quiet?'utf8':undefined});
 if(p.error||p.status!==0)throw Error(cmd+' failed: '+(p.stderr||p.stdout||p.error?.message||p.status));
 return p.stdout||'';
}
const npx=process.platform==='win32'?'npx.cmd':'npx';
const entry='src/scenes/v4/HarborWorldProofIndex.ts';
const score='assets/v3-chill-part01.b64';
if(!existsSync(score))throw Error('V3 user-supplied Day & Night score is missing. Do not substitute a different track.');
const decoded=Buffer.from(readFileSync(score,'utf8').replace(/\s+/g,''),'base64');
if(decoded.length<2048)throw Error('Unexpectedly short V3 score');
const audio=dir+'/v3-user-score.opus';
writeFileSync(audio,decoded);

run(npx,['remotion','render',entry,'HarborWorldV4Proof',native,'--codec','h264','--log','error']);
run('ffmpeg',['-hide_banner','-loglevel','error','-y',
 '-i',native,'-stream_loop','-1','-i',audio,
 '-map','0:v:0','-map','1:a:0',
 '-vf','scale='+W+':'+H+':flags=neighbor,format=yuv420p',
 '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',String(FPS),
 '-c:a','aac','-b:a','160k',
 '-af','afade=t=in:st=0:d=0.12,afade=t=out:st=10.9:d=1.1',
 '-t',String(DURATION),'-movflags','+faststart',movie]);
const report=JSON.parse(run('ffprobe',['-v','error','-count_frames',
 '-show_entries','stream=index,codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,channels:format=duration,size',
 '-of','json',movie],true));
const video=report.streams.find(x=>x.codec_type==='video');
const soundtrack=report.streams.find(x=>x.codec_type==='audio');
if(!video||video.codec_name!=='h264'||video.width!==W||video.height!==H||
 video.r_frame_rate!=='30/1'||Number(video.nb_read_frames)!==FRAMES||
 !soundtrack||soundtrack.codec_name!=='aac'||Math.abs(Number(report.format.duration)-DURATION)>.13)
 throw Error('V4 world proof failed metadata verification: '+JSON.stringify(report));
// Decode EVERY moving frame and audio packet, not only ffprobe metadata.
run('ffmpeg',['-v','error','-xerror','-i',movie,'-f','null','-']);
const stills=[];
for(const [label,index] of [['opening',0],['middle',180],['ending',330]]){
 const name=dir+'/qa/world-'+label+'-'+String(index).padStart(3,'0')+'.png';
 run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',movie,
  '-vf','select=eq(n\\,'+index+')','-vsync','0','-frames:v','1',name]);
 if(!existsSync(name)||statSync(name).size<2000)throw Error('Missing or invalid screenshot: '+name);
 stills.push({frame:index,path:name,bytes:statSync(name).size,sha256:createHash('sha256').update(readFileSync(name)).digest('hex')});
}
if(new Set(stills.map(x=>x.sha256)).size!==stills.length)
 throw Error('Motion verification failed: first/mid/final captures are identical');
const output={
 verified:true,issue:5,branch:'agent/sunset-harbor-v4-world',
 video:movie,dimensions:W+'x'+H,fps:FPS,frames:FRAMES,
 durationSeconds:Number(report.format.duration),codec:video.codec_name,
 audioCodec:soundtrack.codec_name,audioSource:'V3 original user-supplied Day & Night',
 allFramesDecoded:true,firstMiddleLastDiffer:true,stills,
 sizeBytes:statSync(movie).size
};
writeFileSync(dir+'/qa/world-v4-verification.json',JSON.stringify(output,null,2));
console.log(JSON.stringify(output,null,2));
