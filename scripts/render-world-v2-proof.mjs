/** 4s real moving pixel-parallax world proof, not the final film.
 * Uses the exact PNG layers produced by the original source builder.
 */
import sharp from 'sharp';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
const manifest=JSON.parse(readFileSync('public/countryside/world/manifest.json'));
const W=360,H=640,N=120,FPS=30,out='out/countryside-v2-world';
mkdirSync(out+'/frames',{recursive:true});
const planes={};
for(const [id,t] of Object.entries(manifest.tiles))
 planes[id]=new Uint8Array(await sharp(t.file).ensureAlpha().raw().toBuffer());
const speed={sky:0,farTrees:.42,midTrees:.93,nearTrees:1.76,verge:2.42,road:2.86};
function render(frame){
 const dst=new Uint8Array(W*H*4);
 for(const [id,t] of Object.entries(manifest.tiles)){
  const src=planes[id],offset=Math.round(frame*speed[id]);
  for(let y=0;y<t.height;y++){
   const yy=t.y+y;if(yy<0||yy>=H)continue;
   for(let x=0;x<W;x++){
    const sx=((x+offset)%t.width+t.width)%t.width,si=(y*t.width+sx)*4,di=(yy*W+x)*4;
    if(src[si+3]===0)continue;
    dst[di]=src[si];dst[di+1]=src[si+1];dst[di+2]=src[si+2];dst[di+3]=255;
   }
  }
 }
 return dst;
}
const ids=[0,15,30,45,60,75,90,105,119];
for(let frame=0;frame<N;frame++)
 await sharp(render(frame),{raw:{width:W,height:H,channels:4}}).png()
 .toFile(out+'/frames/frame-'+String(frame).padStart(3,'0')+'.png');
const thumb=[];
for(let i=0;i<ids.length;i++){
 const p=out+'/frames/frame-'+String(ids[i]).padStart(3,'0')+'.png';
 thumb.push({input:await sharp(p).resize(180,320,{kernel:'nearest'}).png().toBuffer(),
 left:i%3*180,top:Math.floor(i/3)*320});
}
await sharp({create:{width:540,height:960,channels:4,background:'#121820'}})
 .composite(thumb).png().toFile(out+'/contact-sheet.png');
function run(c,a){
 const p=spawnSync(c,a,{encoding:'utf8',maxBuffer:2e6});
 if(p.error||p.status!==0)throw Error(c+' failed: '+(p.stderr||p.error));
 return p.stdout;
}
const mp4=out+'/countryside-v2-world-proof.mp4';
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate',String(FPS),'-i',
 out+'/frames/frame-%03d.png','-vf','scale=1080:1920:flags=neighbor','-c:v','libx264',
 '-crf','17','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart',mp4]);
const info=JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_entries',
 'stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',mp4]));
const v=info.streams.find(x=>x.codec_name==='h264');
if(v?.width!==1080||v?.height!==1920||v?.r_frame_rate!=='30/1'||Number(v?.nb_read_frames)!==N)
 throw Error('MP4 properties do not match proof contract');
run('ffmpeg',['-v','error','-xerror','-i',mp4,'-f','null','-']);
for(const [id,t] of Object.entries(manifest.tiles)){
 const pixels=planes[id];
 if(pixels.length!==t.width*t.height*4)throw Error('bad '+id+' buffer');
 if(id!=='sky')for(let y=0;y<t.height;y++){
  if(pixels[y*t.width*4+3]!==pixels[(y*t.width+t.width-1)*4+3])
    throw Error(id+' uncovered seam row '+y);
 }
}
writeFileSync(out+'/verification.json',JSON.stringify({scene:'Countryside V2 world only',
 frames:N,fullyDecoded:true,ffprobe:info,sampledFrames:ids},null,2));
console.log('COUNTRYSIDE_V2_WORLD_PROOF_PASS '+JSON.stringify(info));
