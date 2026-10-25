/** Native Remotion video proof + exact pixel scale and real frame verification. */
import {mkdirSync,readFileSync,statSync,writeFileSync,existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import sharp from 'sharp';
const dir='out/car-v2-proof',frames=120;
const native=dir+'/native-360x640.mp4';
const final=dir+'/coupe-v2-1080x1920.mp4';
mkdirSync(dir,{recursive:true});
function run(bin,args){
 const r=spawnSync(bin,args,{encoding:'utf8',maxBuffer:32*1024*1024});
 if(r.error||r.status!==0)throw Error(bin+' failed: '+(r.stderr||r.error||r.status));
 return r.stdout||'';
}
for(const f of ['public/countryside/car/coupe-v2-body.png','public/countryside/car/coupe-v2-wheels-8.png'])if(!existsSync(f))throw Error('Missing prepared car production sprite: '+f);
run(process.platform==='win32'?'npx.cmd':'npx',['remotion','render','src/countryside-v2-car-proof.tsx',
 'CountrysideCarV2Proof',native,'--codec','h264','--concurrency','2','--log','error']);
run('ffmpeg',['-v','error','-y','-i',native,'-vf','scale=1080:1920:flags=neighbor,format=yuv420p',
 '-r','30','-frames:v','120','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-an',final]);
const p=JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_entries',
 'stream=codec_name,codec_type,width,height,pix_fmt,r_frame_rate,nb_read_frames:format=duration,size','-of','json',final]));
const v=p.streams.find(s=>s.codec_type==='video');
if(!v||v.codec_name!=='h264'||v.width!==1080||v.height!==1920||v.pix_fmt!=='yuv420p'||
 v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==frames||Math.abs(Number(p.format.duration)-4)>.02)
 throw Error('MP4 contract fail '+JSON.stringify(p));
run('ffmpeg',['-v','error','-xerror','-i',final,'-f','null','-']);
const times=[0,15,30,45,60,75,90,105,119],sha=[],tiles=[];
for(let i=0;i<times.length;i++){
 const f=times[i],path=dir+'/frame-'+String(f).padStart(3,'0')+'.png';
 run('ffmpeg',['-v','error','-y','-i',final,'-vf','select=eq(n\\,'+f+')','-fps_mode','vfr','-frames:v','1',path]);
 if(!existsSync(path)||statSync(path).size<1024)throw Error('Missing decoded capture '+f);
 const bytes=readFileSync(path);
 sha.push(createHash('sha256').update(bytes).digest('hex'));
 const thumb=await sharp(bytes).resize(180,320,{kernel:'nearest'}).png().toBuffer();
 tiles.push({input:thumb,left:(i%3)*180,top:Math.floor(i/3)*320});
}
if(new Set(sha).size!==sha.length)throw Error('Motion did not advance on independent checkpoints');
const sheet=dir+'/contact-sheet.png';
await sharp({create:{width:540,height:960,channels:4,background:'#20303b'}}).composite(tiles).png().toFile(sheet);
const report={verified:true,scope:'isolated car-only PROOF, not final countryside film',
 native:'360x640',output:'1080x1920',frames:120,fps:30,duration:Number(p.format.duration),
 codec:v.codec_name,pixelFormat:v.pix_fmt,fullDecode:true,distinctCapturedFrames:sha.length,
 contactSheet:sheet,video:final,bytes:statSync(final).size};
writeFileSync(dir+'/verification.json',JSON.stringify(report,null,2)+'\n');
console.log('COUNTRYSIDE_CAR_V3_PIXELORAMA_REMOTION_PROOF_PASS '+JSON.stringify(report));
