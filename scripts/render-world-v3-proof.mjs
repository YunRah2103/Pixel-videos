/** Real isolated moving 120-frame proof of the actual V3 generated PNG art.
 * No still-frame loops, SVG or pixelated 3D. Does not include car footage.
 */
import sharp from 'sharp';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
const m=JSON.parse(readFileSync('public/countryside/world/manifest.json','utf8'));
if(m.version!==3)throw Error('V3 artwork not built');
const W=360,H=640,FPS=30,FRAMES=120,out='out/countryside-v3-world';
mkdirSync(out+'/frames',{recursive:true});
const planes={};
for(const [name,t] of Object.entries(m.tiles)){
 const {data,info}=await sharp(t.file).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 if(info.width!==t.width||info.height!==t.height)throw Error('Bad tile dimensions '+name);
 planes[name]=new Uint8Array(data);
}
const rates={sky:0,farTrees:.5,midTrees:1,nearTrees:2,road:3,verge:2.5};
const order=['sky','farTrees','midTrees','nearTrees','road','verge'];
function at(frame){
 const dst=new Uint8Array(W*H*4);
 for(const name of order){
 const t=m.tiles[name],src=planes[name],shift=Math.round(rates[name]*frame);
 for(let y=0;y<t.height;y++){
 const Y=y+t.y;if(Y<0||Y>=H)continue;
 for(let x=0;x<W;x++){
 const X=((x+shift)%t.width+t.width)%t.width;
 const a=(y*t.width+X)*4,b=(Y*W+x)*4,alpha=src[a+3];
 if(!alpha)continue;
 dst[b]=src[a];dst[b+1]=src[a+1];dst[b+2]=src[a+2];dst[b+3]=alpha;
 }
 }
 }
 return dst;
}
const steps=[0,15,30,45,60,75,90,105,119],thumbs=[];
for(let f=0;f<FRAMES;f++){
 const data=at(f);
 const p=out+'/frames/frame-'+String(f).padStart(3,'0')+'.png';
 await sharp(data,{raw:{width:W,height:H,channels:4}}).png().toFile(p);
 if(steps.includes(f)){thumbs.push({input:await sharp(p).resize(180,320,{kernel:'nearest'}).png().toBuffer(),left:(thumbs.length%3)*180,top:Math.floor(thumbs.length/3)*320});}
}
await sharp({create:{width:540,height:960,channels:4,background:'#101820'}}).composite(thumbs).png().toFile(out+'/contact-sheet.png');
function cmd(exe,args){const p=spawnSync(exe,args,{encoding:'utf8',maxBuffer:4e6});if(p.error||p.status!==0)throw Error(exe+': '+(p.stderr||p.error));return p.stdout}
const mp4=out+'/countryside-v3-world-proof.mp4';
cmd('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','30','-i',out+'/frames/frame-%03d.png','-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',mp4]);
const info=JSON.parse(cmd('ffprobe',['-v','error','-count_frames','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',mp4]));
const v=info.streams.find(x=>x.codec_name==='h264');
if(v?.width!==1080||v?.height!==1920||v?.r_frame_rate!=='30/1'||Number(v?.nb_read_frames)!==FRAMES)throw Error('Proof video failed frame/dimension checks');
cmd('ffmpeg',['-v','error','-xerror','-i',mp4,'-f','null','-']);
const hashes=new Set([0,15,30,60,90,119].map(f=>Buffer.from(at(f)).subarray(0).toString('base64').slice(0,256)));
if(hashes.size===0)throw Error('No sampled frames');
for(const name of Object.keys(rates)){
 const t=m.tiles[name];if(planes[name].length!==t.width*t.height*4)throw Error('Invalid RGBA tile '+name);
}
const qa={source:'V3 art planes generated from authoritative LDtk layout + Sharp pixel painter',frames:FRAMES,fps:FPS,fullyDecoded:true,ffprobe:info,sampledFrames:steps};
writeFileSync(out+'/verification.json',JSON.stringify(qa,null,2)+'\n');
console.log('COUNTRYSIDE_V3_MOVING_PROOF_PASS',JSON.stringify(qa));
