#!/usr/bin/env node
/**
 * Isolated Agent 3 native-Remotion motion proof and hard FFmpeg QA.
 * This is deliberately NOT the Agent 4 final Countryside Drive renderer.
 */
import {spawnSync} from 'node:child_process';
import {mkdir, readFile, writeFile, stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';

const ROOT = resolve(import.meta.dirname,'..');
const OUT = resolve(ROOT,'out','countryside-motion');
const CAPTURES = resolve(OUT,'captures');
await mkdir(CAPTURES,{recursive:true});

function run(bin,args,limit=128*1024*1024){
  const proc=spawnSync(bin,args,{cwd:ROOT,encoding:'utf8',maxBuffer:limit});
  if(proc.error || proc.status !== 0){
    throw new Error(`${bin} ${args.join(' ')} failed: ${proc.error || proc.stderr || proc.stdout}`);
  }
  return proc.stdout;
}

const native=resolve(OUT,'motion-proof-native.mp4');
const final=resolve(OUT,'countryside-motion-proof-1080p.mp4');
const remotion=resolve(ROOT,'node_modules','.bin','remotion');
run(remotion,[
  'render','src/scenes/countryside/motion-proof.entry.ts',
  'CountrysideMotionProof',native,'--codec=h264','--crf=18'
]);
run('ffmpeg',['-hide_banner','-loglevel','error','-y',
  '-i',native,'-vf','scale=1080:1920:flags=neighbor',
  '-c:v','libx264','-preset','veryfast','-crf','18',
  '-pix_fmt','yuv420p','-movflags','+faststart',final]);
const probe=JSON.parse(run('ffprobe',['-v','error','-count_frames',
  '-select_streams','v:0','-show_entries',
  'stream=codec_name,width,height,pix_fmt,avg_frame_rate,nb_read_frames,duration:format=duration,size',
  '-of','json',final]));
const stream=probe.streams?.[0];
const duration=Number(probe.format?.duration ?? stream?.duration);
if(!stream || stream.codec_name !== 'h264' || stream.width !== 1080 || stream.height !== 1920 ||
   stream.pix_fmt !== 'yuv420p' || stream.avg_frame_rate !== '30/1' ||
   Number(stream.nb_read_frames) !== 360 || Math.abs(duration-12) > .03){
  throw new Error('Motion proof failed stream metadata verification: '+JSON.stringify(probe));
}
run('ffmpeg',['-v','error','-xerror','-i',final,'-f','null','-']);
const picks=[0,40,80,120,160,200,240,280,320];
const sha=[];
for(let i=0;i<picks.length;i++){
  const target=resolve(CAPTURES,'capture-'+String(i).padStart(3,'0')+'.png');
  run('ffmpeg',['-hide_banner','-loglevel','error','-y','-i',final,
    '-vf',`select=eq(n\\,${picks[i]}),scale=360:640:flags=neighbor`,
    '-frames:v','1',target]);
  const bytes=await readFile(target);
  sha.push(createHash('sha256').update(bytes).digest('hex'));
}
if(new Set(sha).size!==picks.length)throw new Error('Motion proof did not show 9 distinct frames');
const contact=resolve(OUT,'motion-contact-sheet.png');
run('ffmpeg',['-hide_banner','-loglevel','error','-y',
  '-framerate','1','-i',resolve(CAPTURES,'capture-%03d.png'),
  '-vf','tile=3x3','-frames:v','1',contact]);
const blackScan=spawnSync('ffmpeg',['-hide_banner','-loglevel','info','-i',final,
 '-vf','blackdetect=d=0.05:pix_th=0.08','-an','-f','null','-'],
 {cwd:ROOT,encoding:'utf8',maxBuffer:128*1024*1024});
if(blackScan.status!==0 || blackScan.error)throw new Error('FFmpeg black-gap scan failed: '+(blackScan.stderr || blackScan.error));
if((blackScan.stderr || '').includes('black_start'))throw new Error('Motion proof contains black gaps');
const report={
  type:'AGENT 3 MOTION PROOF — NOT FINAL COUNTRYSIDE FILM',
  renderEntry:'src/scenes/countryside/motion-proof.entry.ts',
  output:'out/countryside-motion/countryside-motion-proof-1080p.mp4',
  checks:{
    nativeRemotion:true,
    ffprobe:probe,
    ffmpegFullDecode:true,
    nineDistinctCaptures:true,
    blackGaps:false,
    nearestNeighborInteger3x:true,
  },
  contactSheet:'out/countryside-motion/motion-contact-sheet.png',
  frameSamples:picks.map((frame,i)=>({frame,sha256:sha[i]})),
  finalBytes:(await stat(final)).size,
};
await writeFile(resolve(OUT,'motion-verification.json'),JSON.stringify(report,null,2)+'\n');
console.log('VERIFIED MOTION PROOF '+final);
console.log('CAPTURE CONTACT SHEET '+contact);
