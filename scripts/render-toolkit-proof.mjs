import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import sharp from 'sharp';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const out=resolve(ROOT,'out','toolkit');
await mkdir(resolve(out,'frames'),{recursive:true});
const w=360,h=640,N=90,FPS=30;
const lib={};
for(const id of ['cloud','boat','lantern','bush']){
 const file=resolve(ROOT,'public','toolkit','sprites',id+'.png');
 lib[id]={data:await readFile(file),meta:await sharp(file).metadata()};
}
const panel=async(width,height,hex)=>{
 const rgb=hex.match(/\w\w/g).map(s=>parseInt(s,16));
 return {input:await sharp({create:{width,height,channels:4,background:{r:rgb[0],g:rgb[1],b:rgb[2],alpha:1}}}).png().toBuffer(),left:0,top:0};
};
const composite=(id,x,y)=>({input:lib[id].data,left:Math.round(x),top:Math.round(y)});
for(let f=0;f<N;f++){
 const phase=f/FPS, drift=Math.round(phase*5);
 const layers=[
  await panel(w,260,'40375b'),
  {...await panel(w,116,'987394'),top:245},
  {...await panel(w,160,'315e70'),top:354},
  {...await panel(w,130,'253e56'),top:510},
  composite('cloud',40+drift,125),
  composite('cloud',206+Math.round(drift*.6),160),
  composite('boat',165+f*.48,403+Math.sin(phase*4)*2),
  composite('bush',80,548),composite('bush',254,555),
  composite('lantern',97,529),composite('lantern',291,537)
 ];
 const pathname=resolve(out,'frames','frame-'+String(f).padStart(3,'0')+'.png');
 await sharp({create:{width:w,height:h,channels:4,background:'#28384e'}}).composite(layers).png().toFile(pathname);
}
const run=(cmd,args)=>{
 const p=spawnSync(cmd,args,{cwd:ROOT,encoding:'utf8',maxBuffer:16*1024*1024});
 if(p.status!==0)throw Error(cmd+' failed: '+(p.stderr||p.error||'unknown'));
 return p.stdout;
};
const native=resolve(out,'toolkit-native.mp4');
const final=resolve(out,'pixel-toolkit-proof-1080p.mp4');
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate',String(FPS),'-i',resolve(out,'frames','frame-%03d.png'),'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',native]);
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',native,'-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',final]);
await sharp(resolve(out,'frames','frame-045.png')).resize(1080,1920,{kernel:'nearest'}).png().toFile(resolve(out,'proof-still.png'));
await writeFile(resolve(out,'proof-info.json'),JSON.stringify({kind:'moving art toolkit proof, not Sunset Harbor V5',frames:N,fps:FPS,final:'out/toolkit/pixel-toolkit-proof-1080p.mp4'},null,2)+'\n');
console.log('PIXEL_TOOLKIT_PROOF '+final);
