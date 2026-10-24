import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {renderHarborBaseLayers} from './HarborWorldV4.mjs';
import {getHarborMotion} from '../v3/HarborMotion.mjs';
import {harborCoupleSvg,harborCatSvg} from '../v3/HarborLife.mjs';

/**
 * Isolated V4 WORLD moving proof. Temporary water and cloud placeholders
 * are intentionally NOT part of HarborWorldV4.mjs or Agent 2's scope.
 * V3 character sprites serve as proof-only placeholders for Agent 3.
 * Music added in the dedicated render script, matching the V3 final.
 */
const ri=(x:number,y:number,w:number,h:number,c:string)=>'<rect x="'+Math.round(x)+'" y="'+Math.round(y)+'" width="'+Math.max(1,Math.round(w))+'" height="'+Math.max(1,Math.round(h))+'" fill="'+c+'"/>';
const pp=(a:number[][],c:string)=>'<polygon points="'+a.map(z=>Math.round(z[0])+','+Math.round(z[1])).join(' ')+'" fill="'+c+'"/>';
const h=(n:number)=>{let t=Math.imul(n^0x6343fc11,0x9e3779b1);t^=t>>>15;return((t>>>0)%104729)/104729;};

const cloud=(x:number,y:number,s:number,t:number,seed:number)=>{
 const dx=x+Math.sin(t/170+seed)*3+(seed%2? t*.008 : -t*.014);
 let o='';
 const base=seed%2?'#dba9bf':'#dbb5c1',dark=seed%2?'#9387aa':'#9c91ad';
 o+=pp([[-14,18],[-7,9],[4,9],[4,-2],[19,-2],[19,-13],[38,-13],[38,-7],[55,-7],[55,2],[77,2],[77,11],[96,11],[96,18]],dark);
 o+=pp([[-12,14],[3,9],[7,0],[21,0],[24,-10],[37,-10],[39,-2],[53,-2],[57,7],[78,7],[84,15],[95,17]],base);
 o+=ri(16,-3,22,2,'#ffdcc8')+ri(44,4,24,2,'#ffe1c8')+ri(6,17,67,2,'#b48ea7');
 return '<g transform="translate('+Math.round(dx)+' '+Math.round(y)+') scale('+s+')">'+o+'</g>';
};
const cloudProof=(f:number)=>{
 let c='';
 c+=cloud(-36,96,1.46,f,1)+cloud(180,128,1.18,f,2)+cloud(266,56,1.07,f,3);
 c+=cloud(-83,212,.92,f,4)+cloud(273,203,.78,f,5);
 // Tiny moving gull flock, low enough to distinguish movement in key frames.
 for(let i=0;i<6;i++){
  const x=40+i*21+f*(.022+i*.008),y=208+i%3*9+Math.sin(f*.06+i)*2;
  const wing=Math.sin(f*.17+i)>0?2:-1;
  c+=ri(x,y,3,1,'#54718c')+ri(x-3,y-wing,3,1,'#54718c')+ri(x+3,y-wing,3,1,'#54718c');
 }
 return c;
};
const waterProof=(f:number)=>{
 let o='',phase=f*.067;
 for(let y=353;y<537;y+=2){
  const d=(y-353)/184;
  o+=ri(0,y,360,2,d<.20?'#528a93':d<.42?'#407d8a':d<.65?'#306b7c':d<.8?'#28596e':'#204a5e');
 }
 // Perspective-scaled, slowly shearing wave planes with independent movements.
 for(let i=0;i<680;i++){
  const d=h(i*11+83),x=h(i*7+502)*395-20+Math.sin(phase+i*.8)*(1+d*5);
  const y=355+d*181,w=2+d*d*23+h(i+42)*6;
  o+=ri(x,y,w,i%13===0?2:1,i%8===0?'#9ec3b5':i%3===0?'#6aa49e':i%3===1?'#3b8190':'#508b94');
 }
 // Widening golden track aligned to sun at x=225.
 for(let i=0;i<450;i++){
  let d=h(i*9+505),y=357+d*178,x=225+(h(i*27+318)-.5)*(18+Math.pow(d,1.6)*204);
  const shimmer=Math.sin(phase+i*1.2)*(2+d*5);
  o+=ri(x+shimmer,y,2+d*16*h(i+4),i%17===0?2:1,i%6===0?'#fff0c5':i%3===0?'#fbd0a1':'#dba49f');
 }
 for(let i=0;i<48;i++){
  const x=(i*37)%360,y=401+h(i+214)*125,d=(y-353)/184;
  if(i%4===0)o+=ri(x+Math.sin(phase+i)*2,y,5+d*8,1,'#b8baaf');
 }
 return o;
};

export const HarborWorldProof:React.FC=()=>{
 const frame=useCurrentFrame();
 const motion=getHarborMotion(frame);
 const layers=renderHarborBaseLayers(frame,{
  cameraX:motion.cameraX,cameraY:motion.cameraY,
  foliageSway:motion.foliageSway,cloudDrift:motion.cloudDrift,
 });
 const image='<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">'+
  layers.sky+cloudProof(frame)+layers.distant+waterProof(frame)+
  layers.architecture+layers.harbourStructures+layers.promenade+
  harborCoupleSvg(motion)+harborCatSvg(motion)+layers.foreground+'</svg>';
 const scale=1.004+frame/359*.025;
 const tx=-1.4+frame/359*2.4,ty=-.35-frame/359*1.1;
 return <AbsoluteFill style={{width:360,height:640,background:'#153d5e',overflow:'hidden'}}>
  <div style={{width:360,height:640,imageRendering:'pixelated',
     transform:'translate('+tx.toFixed(3)+'px,'+ty.toFixed(3)+'px) scale('+scale.toFixed(5)+')',
     transformOrigin:'55% 48%'}}
   dangerouslySetInnerHTML={{__html:image}} />
 </AbsoluteFill>;
};
