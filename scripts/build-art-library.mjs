/**
 * Pixel Studio V4 -- authored pixel-cluster template library.
 * 16 designed silhouettes x 10 deterministic silhouette/palette variations:
 * 160 reusable native-resolution PNGs, not 160 individually hand-drawn masters.
 * No SVG, circles, antialiasing, texture scaling or blur.
 */
import sharp from 'sharp';
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const OUTPUT=resolve(ROOT,'public/studio-v4/library');
const templates=[
 ['oak','tree',48,72],['maple','tree',48,72],['birch','tree',42,72],
 ['pine','tree',36,75],['cypress','tree',30,76],['willow','tree',50,76],
 ['bush','flora',36,26],['flower','flora',18,28],['fern','flora',32,25],
 ['rocks','terrain',36,26],['cloud','sky',54,24],['hill','terrain',64,44],
 ['cottage','building',54,70],['lamp','building',18,64],
 ['hatchback','vehicle',70,36],['coupe','vehicle',78,32]
];
const palettes={
 oak:['#172f36','#285344','#387e53','#69a368','#a7be77','#69514a'],
 maple:['#372d3d','#9b413f','#cc6241','#eb994e','#ffd186','#55424e'],
 birch:['#263b46','#3c775e','#619f73','#a9ca91','#e6ddad','#d8d6c7'],
 pine:['#18313d','#245449','#397663','#669881','#a2b9a0','#685349'],
 cypress:['#172e38','#2a4c42','#467556','#668d69','#9eb18c','#67584f'],
 willow:['#223d42','#3f6551','#648562','#89a775','#bdc58b','#655044'],
 bush:['#1e3a41','#315d4c','#478063','#77a477','#b5c690','#533f43'],
 flower:['#304e46','#3c7956','#d16475','#f29e8a','#ffe2a1','#4d463c'],
 fern:['#203841','#2f6951','#4a8962','#79ac79','#afc68a','#544840'],
 rocks:['#333949','#525666','#7d8084','#a0a39e','#cdc6a9','#3a3948'],
 cloud:['#606a85','#8597af','#bfc2c5','#e5dcd0','#fff0d1','#7c738c'],
 hill:['#273b4c','#45566c','#62768a','#97a7a5','#c1c6af','#354d60'],
 cottage:['#3e384a','#6b5360','#b06d60','#d0a27c','#f1d6a5','#514953'],
 lamp:['#272f3f','#424a54','#ad704a','#e8ab5a','#ffe3a3','#252b35'],
 hatchback:['#2c3547','#73505c','#b45b55','#ec856c','#afc3c2','#1e2c3b'],
 coupe:['#243644','#425f6e','#4a92a0','#86c4bb','#f1d5a2','#1e2a36']
};
const hex=(s)=>[1,3,5].map(i=>parseInt(s.slice(i,i+2),16));
const seed=(a,b)=>{let x=(a*174623+111*b+362931)|0;return()=>{x=Math.imul(x^x>>>15,2246822507);x=Math.imul(x^x>>>13,3266489909);return ((x^x>>>16)>>>0)/4294967296;};};
const draw=(id,variant)=>{
 const [family,category,w,h]=templates[id],p=palettes[family],r=seed(id+1,variant+1);
 const pixels=new Uint8Array(w*h*4);
 const dot=(x,y,c)=>{x=Math.floor(x);y=Math.floor(y);if(x<0||y<0||x>=w||y>=h)return;const i=(y*w+x)*4;const a=hex(c);pixels[i]=a[0];pixels[i+1]=a[1];pixels[i+2]=a[2];pixels[i+3]=255;};
 const rect=(x,y,ww,hh,color)=>{for(let yy=Math.floor(y);yy<Math.floor(y+hh);yy++)for(let xx=Math.floor(x);xx<Math.floor(x+ww);xx++)dot(xx,yy,color);};
 const o=Math.round((r()-.5)*6),v=variant%5,mid=Math.floor(w/2)+o;
 const band=(cx,y,ww,hh,dark,base,shine)=>{
   rect(cx-ww/2,y,ww,hh,p[dark]);rect(cx-ww/2+2,y+2,ww-4,hh-3,p[base]);rect(cx-ww/2+4,y+2,Math.max(2,Math.floor(ww*.28)),3,p[shine]);
 };
 if(category==='tree'){
   const trunkW=(family==='birch'?5:family==='willow'?7:8);
   rect(mid-trunkW/2,Math.floor(h*.38),trunkW,Math.floor(h*.61),p[5]);
   rect(mid-trunkW/2+1,Math.floor(h*.4),2,Math.floor(h*.53),p[4]);
   if(family==='birch')for(let y=43;y<h-5;y+=10)rect(mid-trunkW/2+2,y,3,2,p[0]);
   if(['pine','cypress'].includes(family)){
     for(let k=0;k<5;k++){const yy=6+k*11;const ww=Math.max(10,Math.floor((family==='cypress'?18:25)+k*2.2+v));
       band(mid,yy,ww,12,0,2,3);}
     rect(mid-3,h-12,6,11,p[5]);
   }else if(family==='willow'){
     for(let k=0;k<6;k++)band(mid+(k%2?-8:8),9+k*8,Math.max(19,43-k*2),14,0,2,4);
     for(let k=0;k<8;k++)rect(Math.floor(mid-19+k*5),36+(k%3)*4,2,21+(k%4)*3,p[k%2?2:3]);
   }else{
     // Staggered outline and sun-facing pixel clusters; intentionally not a perfect circle.
     const crownY=9+(variant%3);
     const stacks=[[0,0,22],[ -10,7,28],[12,8,26],[-14,19,24],[8,20,34],[-6,29,32],[8,34,18]];
     for(const [dx,dy,ww] of stacks){const cx=mid+dx+(variant%3-1),yy=crownY+dy;
       band(cx,yy,ww+v,12,0,2,4);rect(cx-ww/2+4,yy+8,ww-8,3,p[1]);}
     for(let k=0;k<8;k++){const x=mid-17+Math.floor(r()*34),y=14+Math.floor(r()*29);rect(x,y,3+(k%3),2,p[k%3?3:4]);}
   }
 }else if(family==='bush'||family==='fern'){
   const count=family==='fern'?7:5;
   for(let i=0;i<count;i++){const cx=4+Math.floor(i*(w-9)/(count-1)),height=10+Math.floor(r()*12);
     band(cx,h-height-3,Math.max(7,13-(i%3)),height,0,2,(i%2?3:4));}
   rect(2,h-5,w-4,4,p[1]);
 }else if(family==='flower'){
   rect(mid,h-17,2,17,p[1]);rect(mid-5,h-9,5,3,p[2]);rect(mid+1,h-12,6,3,p[1]);
   for(const [x,y] of [[-3,-3],[2,-3],[-5,1],[4,1],[-2,5]])rect(mid+x,8+y+o,6,6,p[2+(variant%3)]);
   rect(mid,10+o,3,3,p[4]);
 }else if(family==='rocks'){
   rect(1,h-9,w-2,6,p[0]);rect(4,h-17,20,11,p[1]);rect(8,h-20,14,4,p[3]);
   rect(20,h-15,14,11,p[2]);rect(23,h-15,7,3,p[4]);rect(2,h-7,30,3,p[0]);
 }else if(family==='cloud'){
   rect(2,12,w-5,9,p[0]);rect(4,9,w-9,12,p[2]);
   rect(11,5,17+v,6,p[3]);rect(27,3,13,11,p[3]);rect(8,15,40,4,p[4]);
 }else if(family==='hill'){
   for(let y=7;y<h;y++){const wAt=Math.floor(64*(y-7)/(h-7));rect(32-wAt/2,y,wAt,1,p[1]);}
   for(let y=12;y<25;y++)rect(28-(y-12),y,2*(y-12)+7,1,p[2]);
   rect(27,12,8,3,p[4]);
 }else if(family==='cottage'){
   rect(5,22,44,46,p[0]);rect(8,25,38,40,p[3]);
   for(let y=5;y<22;y++)rect(mid-(y-4)*1.4,y,(y-4)*2.8,2,p[1]);
   rect(18,18,16,4,p[2]);rect(17,42,14,23,p[5]);
   rect(20,45,8,13,p[1]);rect(11,29,9,11,p[0]);rect(12,30,7,9,p[4]);
   rect(36,29,9,11,p[0]);rect(37,30,7,9,p[4]);
   for(let y=51;y<62;y+=5)rect(10,y,5,2,p[2]);
 }else if(family==='lamp'){
   rect(mid-1,12,3,47,p[0]);rect(mid-5,57,12,4,p[0]);
   rect(mid-5,9,12,5,p[1]);rect(mid-4,7,10,6,p[4]);
   rect(mid-3,8,8,4,p[3]);rect(mid-6,6,13,2,p[0]);rect(mid-8,4,17,2,p[0]);
 }else if(category==='vehicle'){
   const y=20; rect(6,y,w-12,11,p[0]);rect(8,y+1,w-16,8,p[2]);
   rect(16,13,Math.floor(w*.44),10,p[0]);rect(19,14,Math.floor(w*.37),7,p[4]);
   rect(37,14,2,7,p[0]);rect(11,y+3,6,2,p[3]);rect(w-13,y+2,5,2,p[4]);
   const whe=[19,w-20];for(const cx of whe){
      rect(cx-7,27,14,4,p[0]);rect(cx-5,26,10,10,p[0]);
      rect(cx-3,29,6,4,p[4]);rect(cx-1,29,2,4,p[5]);}
   for(let x=11;x<w-11;x+=6)rect(x,25,2,1,p[3]);
 }
 return {family,category,id:family+'-'+String(variant).padStart(2,'0'),w,h,pixels};
};
await mkdir(OUTPUT,{recursive:true});
const manifest={version:4,nativePixel:true,grid:'one integer pixel per source sample; nearest neighbour only',
 sources:'16 coded authored cluster templates; ten deterministic visual variants each; NOT 160 separately hand-drawn masters',
 templates:templates.map(x=>({id:x[0],category:x[1]})),sprites:[]};
for(let i=0;i<templates.length;i++)for(let v=0;v<10;v++){
 const a=draw(i,v),dest=resolve(OUTPUT,a.id+'.png');
 await sharp(a.pixels,{raw:{width:a.w,height:a.h,channels:4}}).png().toFile(dest);
 manifest.sprites.push({id:a.id,template:a.family,category:a.category,width:a.w,height:a.h,
   path:'studio-v4/library/'+a.id+'.png',variant:v,method:'pixel-cluster authored template + seeded parametric variation'});
}
await writeFile(resolve(OUTPUT,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log('PIXEL_V4_LIBRARY_BUILT '+JSON.stringify({templates:manifest.templates.length,variants:manifest.sprites.length,dir:OUTPUT}));
