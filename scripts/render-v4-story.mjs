/**
 * Sunset Harbor V4 — Agent 3 full native Remotion + FFmpeg proof.
 * Does not modify the shared Root, V3 files, or other V4 agents' modules.
 * Temporary entry file is removed even when render fails.
 * Usage: node scripts/render-v4-story.mjs
 */
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,existsSync,unlinkSync} from 'node:fs';
import {createHash} from 'node:crypto';
const FPS=30,FRAMES=360,W=1080,H=1920;
const OUT='out/sunset-harbor-v4-STORY-1080p.mp4';
const ENTRY='src/__v4_story_entry.tsx';
const SOURCE='assets/v3-chill-part01.b64';
const SHORT='out/v4-story-day-night-source.opus';
const NATIVE='out/v4-story-native-360x640.mp4';
mkdirSync('out/v4-story-qa',{recursive:true});
function call(binary,args,quiet=false) {
 const p=spawnSync(binary,args,{encoding:'utf8',stdio:quiet?'pipe':'inherit',maxBuffer:16*1024*1024});
 if(p.error||p.status!==0)throw Error(binary+' failed ('+p.status+'): '+(p.stderr||p.stdout||p.error));
 return p.stdout||'';
}
function probe(file) {
 return JSON.parse(call('ffprobe',['-v','error','-count_frames','-show_entries',
   'format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,channels,sample_rate',
   '-of','json',file],true));
}
if(!existsSync(SOURCE))throw Error('User-supplied V3 Day & Night score not present. NEVER substitute jazz.');
writeFileSync(SHORT,Buffer.from(readFileSync(SOURCE,'utf8').replace(/\s+/g,''),'base64'));
const duration=Number(probe(SHORT).format.duration);
if(!Number.isFinite(duration)||duration<2)throw Error('Day & Night source fragment too short to overlap safely.');
const segment=Math.min(3.86,duration-0.02);
const overlap=Math.min(.42,segment*.16);
const advance=segment-overlap;
const count=Math.ceil((12-segment)/advance)+1;
const entry="import React from 'react';\n"+
 "import {registerRoot,Composition} from 'remotion';\n"+
 "import {HarborStoryProof} from './scenes/v4/HarborStoryProof';\n"+
 "const Root=()=> <Composition id=\"HarborStoryProof\" component={HarborStoryProof} durationInFrames={360} fps={30} width={360} height={640}/>;\n"+
 "registerRoot(Root);\n";
writeFileSync(ENTRY,entry,'utf8');
try {
 const npx=process.platform==='win32'?'npx.cmd':'npx';
 call(npx,['remotion','render',ENTRY,'HarborStoryProof',NATIVE,'--codec','h264','--log','error']);
 const splitLabels=Array.from({length:count},(_,i)=>'[s'+i+']').join('');
 let filter='[1:a]asplit='+count+splitLabels+';';
 const mixed=[];
 for(let i=0;i<count;i++) {
   const label='[b'+i+']';
   const delay=Math.round(i*advance*1000);
   filter+='[s'+i+']atrim=0:'+segment.toFixed(3)+',asetpts=PTS-STARTPTS,'+
    'afade=t=in:st=0:d='+overlap.toFixed(3)+','+
    'afade=t=out:st='+(segment-overlap).toFixed(3)+':d='+overlap.toFixed(3)+','+
    'adelay='+delay+':all=1'+label+';';
   mixed.push(label);
 }
 filter+=mixed.join('')+'amix=inputs='+count+':duration=longest:normalize=0,'+
  'atrim=0:12,afade=t=in:st=0:d=0.12,afade=t=out:st=11.35:d=0.65,'+
  'aresample=48000[score];'+
  '[0:v]scale='+W+':'+H+':flags=neighbor,format=yuv420p[v]';
 call('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',NATIVE,'-i',SHORT,
   '-filter_complex',filter,'-map','[v]','-map','[score]',
   '-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p',
   '-r',String(FPS),'-c:a','aac','-b:a','160k','-ar','48000',
   '-t','12','-movflags','+faststart',OUT]);
 const qa=probe(OUT);
 const v=qa.streams.find(s=>s.codec_type==='video'),a=qa.streams.find(s=>s.codec_type==='audio');
 if(!v||v.codec_name!=='h264'||v.width!==W||v.height!==H||
   v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==FRAMES||
   !a||a.codec_name!=='aac'||Math.abs(Number(qa.format.duration)-12)>0.15)
   throw Error('FFprobe delivery contract mismatch: '+JSON.stringify(qa));
 // Full video+audio decode (not just container/stream metadata).
 call('ffmpeg',['-v','error','-xerror','-i',OUT,'-f','null','-']);
 const pictures=[];
 for(const [name,index] of [['opening',18],['story',126],['meeting',224],['ending',340]]) {
   const path='out/v4-story-qa/'+name+'.png';
   call('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',OUT,
     '-vf','select=eq(n\\,'+index+')','-vsync','0','-frames:v','1',path]);
   const bytes=readFileSync(path);
   pictures.push({name,frame:index,path,sha256:createHash('sha256').update(bytes).digest('hex')});
 }
 if(new Set(pictures.map(p=>p.sha256)).size!==pictures.length)
   throw Error('Video proof was not dynamically different at all sampled story beats');
 const report={
   verified:true,renderer:'Remotion 4, native 360x640, 3x nearest-neighbour FFmpeg finish',
   file:OUT,duration:qa.format.duration,frames:FRAMES,fps:FPS,
   resolution:W+'x'+H,videoCodec:v.codec_name,audioCodec:a.codec_name,
   audioChannels:a.channels,
   audioProvenance:'user-supplied Day & Night segment already in V3 branch',
   sourceExcerptSeconds:duration,joinedWithSeconds:overlap,
   musicNote:'V3 stores only a compact excerpt, blended overlaps avoid hard 4-second cuts; full owner recording is needed for unlooped 12-second musical development',
   fullDecodePassed:true,sizeBytes:qa.format.size,
   captures:pictures
 };
 writeFileSync('out/v4-story-qa/verification.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
} finally {
 if(existsSync(ENTRY))unlinkSync(ENTRY);
}
