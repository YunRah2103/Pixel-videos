import sharp from 'sharp';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {carPose} from '../src/toolkit/rigs.mjs';
import {lightPixelScene,contactShadow} from '../src/toolkit/pixelLighting.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'), out=resolve(root,'out','studio-v3');
const scene=JSON.parse(await readFile(resolve(root,'public/toolkit/environments/countryside/scene.json'),'utf8'));
const frames=resolve(out,'frames');await mkdir(frames,{recursive:true});
const layers=await Promise.all(scene.layers.map(async l=>({...l,
 path:resolve(root,'public',l.image)})));
const car=await sharp(resolve(root,'public/toolkit/sprites',scene.hero.sprite+'.png'))
 .resize({width:((await sharp(resolve(root,'public/toolkit/sprites',scene.hero.sprite+'.png')).metadata()).width)*scene.hero.scale,kernel:'nearest'})
 .png().toBuffer();
const shadow=await contactShadow({width:84,height:9,opacity:.29});
const FPS=30,N=90,WIDTH=scene.width,HEIGHT=scene.height;
const run=(cmd,args)=>{const proc=spawnSync(cmd,args,{encoding:'utf8',maxBuffer:16*1024*1024});
 if(proc.error||proc.status!==0)throw Error(cmd+' failed '+(proc.stderr||proc.error||proc.status));
 return proc.stdout;
};
for(let frame=0;frame<N;frame++){
 const cameraDistance=frame/(N-1)*(scene.camera?.motion||20);
 const comps=[];
 for(const layer of layers){
  const x=Math.min(scene.stageWidth-WIDTH,Math.max(0,Math.round(cameraDistance*(1+layer.depth*3))));
  comps.push({input:await sharp(layer.path).extract({left:x,top:0,width:WIDTH,height:HEIGHT}).png().toBuffer(),left:0,top:0});
 }
 const pose=carPose(frame,{speed:1.7,roadRoughness:1});
 const heroX=Math.round(scene.hero.x+Math.sin(frame*.024)*4);
 const heroY=scene.hero.y+pose.bodyY;
 comps.push({input:shadow,left:heroX+3,top:heroY+27});
 comps.push({input:car,left:heroX,top:heroY});
 const base=await sharp({create:{width:WIDTH,height:HEIGHT,channels:4,background:'#243a48'}})
   .composite(comps).png().toBuffer();
 const image=await lightPixelScene(base,{
  ambient:.93,
  lights:[{x:277-frame*.05,y:235,radius:210,intensity:.27,color:[254,195,118]}],
  fog:{top:315,bottom:450,color:[202,199,164],alpha:.045}});
 await writeFile(resolve(frames,'frame-'+String(frame).padStart(3,'0')+'.png'),image);
}
const native=resolve(out,'countryside-native.mp4'),final=resolve(out,'countryside-toolkit-proof-1080p.mp4');
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate',String(FPS),'-i',resolve(frames,'frame-%03d.png'),'-c:v','libx264','-crf','17','-preset','veryfast','-pix_fmt','yuv420p',native]);
run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',native,'-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',final]);
console.log('PIXEL_COUNTRYSIDE_PROOF '+JSON.stringify({file:final,frames:N,characters:[scene.hero.sprite]}));
