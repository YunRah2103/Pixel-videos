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

// Crossfade repeated segments to avoid sharp, clicky 4s boundaries.
// This does not claim to restore the missing full-length recording.
const segment=Math.min(3.86,shortDuration-0.02);
const overlap=Math.min(0.42,segment*0.16);
const advance=segment-overlap;
const loops=Math.ceil((SECONDS-segment)/advance)+1;
let filter='[1:a]asplit='+loops+Array.from({length:loops},(_,i)=>'[s'+i+']').join('')+';';
const labels=[];
for(let i=0;i<loops;i++){
 const dst='[b'+i+']',delay=Math.round(i*advance*1000);
 filter+='[s'+i+']atrim=0:'+segment.toFixed(3)+',asetpts=PTS-STARTPTS,'+
  'afade=t=in:st=0:d='+overlap.toFixed(3)+','+
  'afade=t=out:st='+(segment-overlap).toFixed(3)+':d='+overlap.toFixed(3)+','+
  'adelay='+delay+':all=1'+dst+';';
 labels.push(dst);
}
filter+=labels.join('')+'amix=inputs='+loops+':duration=longest:normalize=0,'+
 'atrim=0:12,afade=t=in:st=0:d=0.12,afade=t=out:st=11.1:d=0.9,'+
 'aresample=48000[score];[0:v]scale='+W+':'+H+':flags=neighbor,format=yuv420p[v]';
exec('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',NATIVE,'-i',SOURCE,
 '-filter_complex',filter,'-map','[v]','-map','[score]','-c:v','libx264',
 '-preset','medium','-crf','17','-pix_fmt','yuv420p','-r','30',
 '-c:a','aac','-b:a','160k','-ar','48000',
 '-t',String(SECONDS),'-movflags','+faststart',FINAL]);

const meta=probe(FINAL);
const v=meta.streams.find(s=>s.codec_type==='video');
const a=meta.streams.find(s=>s.codec_type==='audio');
if(!v||v.codec_name!=='h264'||v.width!==W||v.height!==H||
 v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==FRAMES||
 !a||a.codec_name!=='aac'||Math.abs(Number(meta.format.duration)-SECONDS)>0.15)
 throw Error('Delivery contract mismatch: '+JSON.stringify(meta));
exec('ffmpeg',['-v','error','-xerror','-i',FINAL,'-f','null','-']);

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
 excerptSeconds:shortDuration,crossfadeSeconds:overlap,
 caution:'Check owner audio rights before public music redistribution.',
 bytes:statSync(FINAL).size,contactSheet:CONTACT,checkpoints:frames
};
writeFileSync(QA+'/verification.json',JSON.stringify(result,null,2)+'\n');
console.log('V4_FINAL_VERIFIED '+JSON.stringify(result));
