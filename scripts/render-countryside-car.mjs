/** Isolated native Remotion animation and FFmpeg 3x-nearest proof. */
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
import sharp from 'sharp';
const out=resolve('out/countryside-car');
await mkdir(resolve(out,'frames'),{recursive:true});
function run(cmd,args){
 const r=spawnSync(cmd,args,{encoding:'utf8',maxBuffer:64*1024*1024});
 if(r.status!==0)throw Error(cmd+' failed: '+(r.stderr||r.stdout||r.error));
 return r.stdout;
}
run('node',['studio/countryside/car/build-car-art.mjs']);
const native=resolve(out,'coupe-proof-native.mp4');
const full=resolve(out,'coupe-proof-1080p.mp4');
run('npx',['remotion','render','src/countryside-car-proof.tsx','CountrysideCarProof',native,'--codec=h264','--crf=17','--concurrency=2']);
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',native,
 '-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-preset','veryfast','-crf','17',
 '-pix_fmt','yuv420p','-movflags','+faststart',full]);
const indices=[0,14,28,42,56,70,84,98,112];
for(let i=0;i<indices.length;i++){
 run('ffmpeg',['-v','error','-y','-i',native,'-vf','select=eq(n\\,'+indices[i]+')',
 '-vsync','0','-frames:v','1',resolve(out,'frames','sample-'+i+'.png')]);
}
const layers=indices.map((frame,i)=>({input:resolve(out,'frames','sample-'+i+'.png'),
 left:(i%3)*360,top:Math.floor(i/3)*640}));
await sharp({create:{width:1080,height:1920,channels:4,background:'#6DB6E5'}})
 .composite(layers).png().toFile(resolve(out,'coupe-contact-sheet.png'));
const info=JSON.parse(run('ffprobe',['-v','error','-select_streams','v:0',
 '-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt',
 '-show_entries','format=duration','-of','json',full]));
const v=info.streams[0];
if(v.codec_name!=='h264'||v.width!==1080||v.height!==1920||
 v.r_frame_rate!=='30/1'||v.pix_fmt!=='yuv420p'||Number(v.nb_frames)!==120)
 throw Error('Invalid movie metadata '+JSON.stringify(info));
run('ffmpeg',['-v','error','-xerror','-i',full,'-f','null','-']);
const {data}=await sharp('public/countryside/car/coupe-wheels-8.png').ensureAlpha().raw().toBuffer({resolveWithObject:true});
const poses=new Set();
for(let pose=0;pose<8;pose++){
 const parts=[];
 for(let y=0;y<24;y++)for(let x=0;x<24;x++){
  const p=4*(y*192+pose*24+x);parts.push(...data.subarray(p,p+4));
 }
 poses.add(Buffer.from(parts).toString('base64'));
}
if(poses.size!==8)throw Error('Wheel poses are not visually distinct');
const result={verified:true,kind:'isolated AGENT 1 moving proof (not final film)',ffprobe:info,
 fullDecode:true,authoredWheelPoses:poses.size,contactFrames:indices,mp4:'out/countryside-car/coupe-proof-1080p.mp4'};
await writeFile(resolve(out,'verification.json'),JSON.stringify(result,null,2)+'\n');
console.log('COUNTRYSIDE_CAR_PROOF_VERIFIED '+JSON.stringify(result));