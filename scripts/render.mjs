import {spawnSync} from 'node:child_process';
import {mkdirSync, existsSync, readFileSync, writeFileSync} from 'node:fs';
mkdirSync('out',{recursive:true});
const exec=(cmd,args)=>{const p=spawnSync(cmd,args,{stdio:'inherit'});if(p.status!==0)process.exit(p.status??1)};
const npx=process.platform==='win32'?'npx.cmd':'npx';
const target='out/sunset-harbor-1080p.mp4';
exec(npx,['remotion','render','src/index.ts','SunsetHarbor','out/sunset-harbor-lowres.mp4','--codec','h264']);
const embed=existsSync('assets/sunset-jazz-excerpt.m4a.b64');
if(embed&&!existsSync('assets/sunset-jazz-excerpt.m4a')) {
  writeFileSync('out/sunset-jazz-excerpt.m4a',Buffer.from(readFileSync('assets/sunset-jazz-excerpt.m4a.b64','utf8').replace(/\s/g,''),'base64'));
}
const music=existsSync('assets/sunset-jazz-excerpt.m4a')?'assets/sunset-jazz-excerpt.m4a':embed?'out/sunset-jazz-excerpt.m4a':null;
const args=['-hide_banner','-loglevel','error','-y','-i','out/sunset-harbor-lowres.mp4'];
if(music)args.push('-i',music);
args.push('-map','0:v:0');
if(music)args.push('-map','1:a:0');
args.push('-vf','scale=1080:1920:flags=neighbor,format=yuv420p','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-r','30');
if(music)args.push('-filter:a','afade=t=in:st=0:d=0.24,afade=t=out:st=10.65:d=1.35','-c:a','aac','-b:a','128k','-shortest');
args.push('-movflags','+faststart',target);
exec('ffmpeg',args);
const probe=spawnSync('ffprobe',['-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',target],{encoding:'utf8'});
if(probe.status!==0)throw Error('FFprobe failed');
const data=JSON.parse(probe.stdout),v=data.streams[0];
if(v.codec_name!=='h264'||v.width!==1080||v.height!==1920||v.r_frame_rate!=='30/1'||Number(v.nb_read_frames)!==360||Math.abs(Number(data.format.duration)-12)>.12)throw Error('Final file failed technical verification '+JSON.stringify(data));
console.log(JSON.stringify({verified:true,path:target,video:v,duration:data.format.duration,audio:!!music},null,2));