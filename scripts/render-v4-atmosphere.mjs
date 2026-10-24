import {spawnSync} from 'node:child_process';
import {mkdirSync,existsSync,readFileSync,writeFileSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';

const FRAMES=360,FPS=30,W=1080,H=1920,DURATION=12;
const native='out/sunset-harbor-v4-atmosphere-native.mp4';
const dest='out/sunset-harbor-v4-atmosphere-1080p.mp4';
mkdirSync('out/qa-v4-atmosphere',{recursive:true});
const entry='out/harbor-v4-atmosphere-entry.tsx';
writeFileSync(entry,[
 "import React from 'react';",
 "import {registerRoot,Composition} from 'remotion';",
 "import {HarborAtmosphereProof} from '../src/scenes/v4/HarborAtmosphereProof';",
 "registerRoot(() => React.createElement(Composition,{id:'HarborAtmosphereProof',component:HarborAtmosphereProof,durationInFrames:360,fps:30,width:360,height:640}));",
].join('\n')+'\n');
const run=(exe,args,quiet=false)=>{
 const p=spawnSync(exe,args,{stdio:quiet?'pipe':'inherit',encoding:'utf8',maxBuffer:1024*1024*6});
 if(p.status!==0)throw Error(exe+' '+args.join(' ')+' failed: '+(p.stderr||p.stdout||p.error||p.status));
 return p.stdout||'';
};
const npx=process.platform==='win32'?'npx.cmd':'npx';
const audioB64='assets/v3-chill-part01.b64';
if(!existsSync(audioB64))throw Error('The V3 user-supplied Day & Night soundtrack is missing. Do not substitute other music.');
const soundtrack='out/v4-atmosphere-day-night.opus';
writeFileSync(soundtrack,Buffer.from(readFileSync(audioB64,'utf8').replace(/\s/g,''),'base64'));
// Actual native Remotion rendering — NOT a static slideshow or generated GIF.
run(npx,['remotion','render',entry,'HarborAtmosphereProof',native,'--codec=h264','--concurrency=2']);
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',native,
 '-stream_loop','3','-i',soundtrack,'-map','0:v:0','-map','1:a:0',
 '-vf','scale='+W+':'+H+':flags=neighbor,format=yuv420p',
 '-c:v','libx264','-preset','medium','-crf','17','-r',String(FPS),'-pix_fmt','yuv420p',
 '-c:a','aac','-b:a','160k',
 '-af','afade=t=in:st=0:d=0.12,afade=t=out:st=10.9:d=1.1',
 '-t',String(DURATION),'-movflags','+faststart',dest]);
const metadata=JSON.parse(run('ffprobe',['-v','error','-count_frames',
 '-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,sample_rate,channels:format=duration,size',
 '-of','json',dest],true));
const v=metadata.streams.find(s=>s.codec_type==='video');
const a=metadata.streams.find(s=>s.codec_type==='audio');
if(!v||v.codec_name!=='h264'||v.width!==W||v.height!==H||v.r_frame_rate!=='30/1'||
 Number(v.nb_read_frames)!==FRAMES||!a||a.codec_name!=='aac'||
 Math.abs(Number(metadata.format.duration)-DURATION)>.13)throw Error('Proof failed stream checks: '+JSON.stringify(metadata));
run('ffmpeg',['-v','error','-i',dest,'-f','null','-']);
// Three art-direction checkpoints along the uninterrupted 360-frame movie.
for(const [key,frame] of [['opening',0],['middle',180],['ending',359]]){
 const path='out/qa-v4-atmosphere/'+key+'.png';
 run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',dest,
  '-vf','select=eq(n\\,'+frame+')','-vsync','0','-frames:v','1',path]);
 if(!existsSync(path)||statSync(path).size<1024)throw Error('Missing QA frame: '+path);
}
const hashes=Object.fromEntries(['opening','middle','ending'].map(key=>{
 const data=readFileSync('out/qa-v4-atmosphere/'+key+'.png');
 return [key,createHash('sha256').update(data).digest('hex')];
}));
if(new Set(Object.values(hashes)).size!==3)throw Error('The first, middle, ending stills are identical: motion was not rendered.');
const result={verified:true,video:dest,frames:FRAMES,fps:FPS,width:W,height:H,duration:metadata.format.duration,
 videoCodec:v.codec_name,audioCodec:a.codec_name,audioSource:'Existing V3 user-supplied Day & Night excerpt (looped)',
 decodedEntireVideo:true,qaFrames:hashes,bytes:statSync(dest).size,
 caution:'User-supplied music rights must be checked before redistribution.'};
writeFileSync('out/qa-v4-atmosphere/verification.json',JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));
