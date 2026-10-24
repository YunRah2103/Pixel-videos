import {readFile,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import sharp from 'sharp';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const root=resolve(ROOT,'out','toolkit');
const report=JSON.parse(await readFile(resolve(root,'assets-report.json'),'utf8'));
if(!report.verified||report.entries.length<4)throw Error('Asset generator not verified');
for(const e of report.entries){
 const meta=await sharp(resolve(ROOT,e.destination)).metadata();
 if(meta.width!==e.width||meta.height!==e.height||meta.format!=='png')throw Error('Bad asset '+e.id);
}
const mp4=resolve(root,'pixel-toolkit-proof-1080p.mp4');
const call=(name,args)=>{
 const p=spawnSync(name,args,{cwd:ROOT,encoding:'utf8',maxBuffer:16*1024*1024});
 if(p.status!==0)throw Error(name+' failed: '+(p.stderr||p.error||'unknown'));
 return p.stdout;
};
const probe=JSON.parse(call('ffprobe',['-v','error','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,nb_read_frames,r_frame_rate:format=duration','-of','json',mp4]));
const v=probe.streams.find(x=>x.codec_type==='video');
if(!v||v.codec_name!=='h264'||v.width!==1080||v.height!==1920||v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==90)throw Error('Video proof invalid '+JSON.stringify(probe));
call('ffmpeg',['-v','error','-xerror','-i',mp4,'-f','null','-']);
const frames=[0,15,30,45,60,75,89], hashes=[];
for(const f of frames){
 const b=await readFile(resolve(root,'frames','frame-'+String(f).padStart(3,'0')+'.png'));
 hashes.push(createHash('sha256').update(b).digest('hex'));
}
if(new Set(hashes).size!==frames.length)throw Error('Proof frames are identical');
const result={verified:true,nativeFrames:90,decodedFrames:Number(v.nb_read_frames),fps:30,width:1080,height:1920,artSprites:report.entries.length,frameDiversity:true,fullDecode:true,duration:Number(probe.format.duration)};
await writeFile(resolve(root,'verification.json'),JSON.stringify(result,null,2)+'\n');
console.log('PIXEL_TOOLKIT_QA_PASS '+JSON.stringify(result));
