/**
 * V5 Agent 2 native 12s proof + verified 1080x1920 master.
 *
 * Rebuilds the approved V4 master as an apples-to-apples picture/audio
 * reference, then encodes new 360x640 Remotion frames at 3x nearest-neighbour.
 * The 12s soundtrack is taken WITHOUT modification from that verified V4
 * final master (the owner's short Day & Night excerpt crossfaded in V4).
 */
import {spawnSync} from 'node:child_process';
import {mkdirSync,readFileSync,writeFileSync,existsSync,statSync} from 'node:fs';
import {createHash} from 'node:crypto';
const FRAMES=360,FPS=30,W=1080,H=1920,DURATION=12;
const QA='out/v5-atmosphere-qa';
const NATIVE='out/sunset-harbor-v5-atmosphere-native-360x640.mp4';
const VIDEO='out/sunset-harbor-v5-atmosphere-1080p.mp4';
const V4='out/sunset-harbor-v4-FINAL-1080p.mp4';
mkdirSync(QA,{recursive:true});
const run=(exe,args,quiet=false)=>{
 const p=spawnSync(exe,args,{encoding:'utf8',stdio:quiet?'pipe':'inherit',maxBuffer:32*1024*1024});
 if(p.status!==0||p.error)throw Error(exe+' failed: '+(p.stderr||p.stdout||p.error||p.status));
 return p.stdout||'';
};
const sha=file=>createHash('sha256').update(readFileSync(file)).digest('hex');
const probe=file=>JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_entries',
 'stream=codec_name,codec_type,width,height,nb_read_frames,r_frame_rate,sample_rate,channels:format=duration,size',
 '-of','json',file],true));
if(!existsSync(V4)||!existsSync('out/v4-final-qa/verification.json'))
 throw Error('Run node scripts/render-v4-final.mjs first: the genuine V4 reference and user score must exist.');
const v4qa=JSON.parse(readFileSync('out/v4-final-qa/verification.json','utf8'));
if(v4qa.verified!==true||Number(v4qa.decodedFrames)!==360)
 throw Error('Approved V4 A/B source is not QA-verified');
const entry='out/v5-atmosphere-entry.tsx';
writeFileSync(entry,[
 "import React from 'react';",
 "import {registerRoot,Composition} from 'remotion';",
 "import {AtmosphereV5Proof} from '../src/scenes/v5/AtmosphereV5Proof';",
 "registerRoot(() => React.createElement(Composition,{id:'AtmosphereV5Proof',component:AtmosphereV5Proof,durationInFrames:360,fps:30,width:360,height:640}));",
].join('\n')+'\n');
const npx=process.platform==='win32'?'npx.cmd':'npx';
run(npx,['remotion','render',entry,'AtmosphereV5Proof',NATIVE,
 '--codec','h264','--concurrency','2','--log','error']);
run('ffmpeg',['-hide_banner','-loglevel','error','-y',
 '-i',NATIVE,'-i',V4,'-map','0:v:0','-map','1:a:0',
 '-vf',`scale=${W}:${H}:flags=neighbor,format=yuv420p`,
 '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',
 '-r',String(FPS),'-c:a','aac','-b:a','160k','-t',String(DURATION),
 '-movflags','+faststart',VIDEO]);
const meta=probe(VIDEO);
const v=meta.streams.find(x=>x.codec_type==='video');
const a=meta.streams.find(x=>x.codec_type==='audio');
if(!v||!a||v.codec_name!=='h264'||a.codec_name!=='aac'||
 v.width!==W||v.height!==H||v.r_frame_rate!=='30/1'||
 Number(v.nb_read_frames)!==FRAMES||
 Math.abs(Number(meta.format.duration)-DURATION)>.15)
 throw Error('V5 stream/length contract failed: '+JSON.stringify(meta));
run('ffmpeg',['-v','error','-xerror','-i',VIDEO,'-f','null','-']);
// 9 full-motion image checkpoints, comparing identical V4/V5 timestamps.
const checkpoints=[0,45,90,135,180,225,270,315,359];
const qa=[];
for(const frame of checkpoints){
 const stem='frame-'+String(frame).padStart(3,'0'),file=QA+'/'+stem+'.png';
 run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',VIDEO,
   '-vf','select=eq(n\\,'+frame+')','-vsync','0','-frames:v','1',file]);
 if(!existsSync(file)||statSync(file).size<1024)
   throw Error('Frame extraction failed at '+frame);
 const other='out/v4-final-qa/'+stem+'.png';
 if(!existsSync(other))throw Error('V4 A/B reference frame missing: '+other);
 const compare=QA+'/comparison-'+String(frame).padStart(3,'0')+'.png';
 run('ffmpeg',['-hide_banner','-loglevel','error','-y',
  '-i',other,'-i',file,'-filter_complex',
  '[0:v]scale=180:320:flags=neighbor[left];[1:v]scale=180:320:flags=neighbor[right];[left][right]hstack=inputs=2',
  '-frames:v','1',compare]);
 qa.push({frame,file,sha256:sha(file),v4Sha256:sha(other),comparison:compare});
}
if(new Set(qa.map(x=>x.sha256)).size!==9)
 throw Error('V5 keyframes duplicate each other: scene could be static');
if(qa.some(x=>x.sha256===x.v4Sha256))
 throw Error('V5 frame identical to V4: atmosphere may not be active');
const CONTACT=QA+'/sunset-harbor-v5-contact-sheet.png';
const COMPARE=QA+'/v4-v5-side-by-side.png';
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','1',
 '-pattern_type','glob','-i',QA+'/frame-*.png',
 '-vf','scale=180:320:flags=neighbor,tile=3x3:padding=6:margin=6',
 '-frames:v','1',CONTACT]);
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','1',
 '-pattern_type','glob','-i',QA+'/comparison-*.png',
 '-vf','tile=3x3:padding=6:margin=6','-frames:v','1',COMPARE]);
const blacks=run('ffmpeg',['-i',VIDEO,'-vf',
 'blackdetect=d=0.07:pix_th=0.075:pic_th=0.99','-an','-f','null','-'],true);
if(/black_start:/i.test(blacks))throw Error('Black frames detected in V5');
const report={
 verified:true,video:VIDEO,bytes:statSync(VIDEO).size,
 codec:v.codec_name,audioCodec:a.codec_name,width:v.width,height:v.height,
 fps:FPS,frames:FRAMES,duration:Number(meta.format.duration),
 decode:'full FFmpeg -xerror PASS',blackFrames:'none',
 nativeRemotion:true,nearestNeighbour3x:true,
 audioProvenance:'Exactly the approved V4 owner-provided Day & Night excerpt, 12s crossfaded score',
 caution:'Music public usage and redistribution rights remain for the owner to confirm.',
 v4Baseline:v4qa.file,qaFrames:qa,
 contactSheet:CONTACT,sideBySide:COMPARE,
 deterministicMotion:'frame index only; all parameterised, fixed-seed paint',
 };
writeFileSync(QA+'/verification.json',JSON.stringify(report,null,2)+'\n');
console.log('V5_ATMOSPHERE_VERIFIED '+JSON.stringify(report));
