/**
 * Original editable 16-bit countryside coupe sprite master.
 * Each authored run "12j" means 12 pixels of palette colour j.
 * Palette-only pixel clusters, no vector graphics, imported art or filters.
 * Wheel strip is eight individually raster-quantised hub poses.
 */
import sharp from 'sharp';
import {mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
const out=resolve(process.cwd(),'public/countryside/car');
const palette={"a":"#26323B","b":"#263E39","c":"#444C55","d":null,"e":"#575E65","f":"#6DB6E5","g":"#823B38","h":"#9ACBDD","i":"#BCC5B9","j":"#D84E3F","k":"#E4D49B","l":"#F17853","m":"#F5BD7E"};
const bodyRows=[
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "57d40b59d",
 "52d51b53d",
 "47d5b48l7b49d",
 "47d60b49d",
 "43d67b46d",
 "43d67b46d",
 "40d8b18h8b30h8b44d",
 "40d8b3h13f2h8b3h25f2h8b44d",
 "38d6b23h6b35h6b42d",
 "38d6b23h6b2h28f5h6b42d",
 "35d9b2h17f4h6b2h31f2h8b40d",
 "35db5g27hg3bg38h4gb40d",
 "33d2b6g2h18f7hg3bg38h5g2b38d",
 "33d2b6g27hg3bg10h20i8h5g2b38d",
 "30d9g29hg3bg41h7g2b33d",
 "30d9g29hg3bg41h7g2b33d",
 "20d10b14g21b4g3b2g38b13g7b24d",
 "13d9b8j39g3b53g6j7b18d",
 "13d9b8j39g3b53g6j7b18d",
 "9d3b8j10l4g35l3b44l4g19l3j2b12d",
 "9d3b3j15l4g35l3b44l4g22l2b12d",
 "7d2b4j17l4g35l3b44l4g25l3jb7d",
 "7d2b4j17l4g35l3b44l4g7l2m16l3jb7d",
 "5d2b4j6l7m6l4g35l3b44l4g27l3jb5d",
 "5d2b23j4g15j5m15j2g49j25m5jb5d",
 "4d3b62j2g50j27l2j3b3d",
 "4d2b63j2g81jb3d",
 "4d2b63j2g81jb3d",
 "3d5g19j5l3jb3j5l25j2g7j6i28j5l3jb3j5l23j3bd",
 "3dg5m21j11b28j2g6j9b29j11b21j5k3bd",
 "3dg5m19j7bd7b26j2g42j7bd7b21j4m2bd",
 "3d3b21j4b9d4b25j2g41j4b9d4b23j3bd",
 "3d3b7j3g10j3b13d3b24j2g40j3b13d3b9jb2jb2jb6j3bd",
 "3d3b7j3g9j3b15d3b23j2g39j3b15d3b8jb2jb2jb6j3bd",
 "3d3b7j2g9l3b17d3b22j2g8j30l3b17d3b7jb2jb2jb6j3bd",
 "5d3b5j3g7j3b19d3b21j2g9j28g3b19d3b19j3bd",
 "5d3b5j3g7j2b21d2b21j2g37j2b21d2b19j3bd",
 "5d3b14g3b21d3b58g3b21d3b12g5bg3bd",
 "5d3b14g2b23d2b58g2b23d2b13g5i3bd",
 "8d14g2b23d2b35g18b5g2b23d2b18gb3d",
 "8d2b12j2b23d2b22j3b11j18g4j2b23d2b17j2b3d",
 "8d4b10i2b23d2b58g2b23d2b2g14i3b3d",
 "8d5bj7g2b25d2b56g2b25d2b11g3j4b3d",
 "12d2b8g2b23d2b58g2b23d2b12g5b5d",
 "12d12b23d62b23d19b5d",
 "12d12b23d62b23d19b5d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d",
 "156d"
];
const hex=(s)=>s===null?null:[1,3,5].map(i=>parseInt(s.slice(i,i+2),16));
const colors=Object.fromEntries(Object.entries(palette).map(([code,value])=>[code,hex(value)]));
function art(width,height){
 const data=Buffer.alloc(width*height*4);
 function pixel(x,y,key){
  if(x<0||y<0||x>=width||y>=height)throw new Error('Pixel out of bounds');
  const p=(y*width+x)*4,v=colors[key];
  if(!v)return;
  data[p]=v[0];data[p+1]=v[1];data[p+2]=v[2];data[p+3]=255;
 }
 async function save(name){await sharp(data,{raw:{width,height,channels:4}}).png({compressionLevel:9,palette:true,effort:10}).toFile(resolve(out,name));}
 return {pixel,save};
}
const body=art(156,63);
if(bodyRows.length!==63)throw Error('Wrong body height');
for(let y=0;y<63;y++){
 let x=0;const encoded=bodyRows[y],parts=[...encoded.matchAll(/(\d*)([a-m])/g)];
 if(parts.map(x=>x[0]).join('')!==encoded)throw Error('Bad pixel row '+y);
 for(const part of parts){const n=part[1]?Number(part[1]):1;for(let i=0;i<n;i++)body.pixel(x++,y,part[2]);}
 if(x!==156)throw Error('Bad row width at '+y+': '+x);
}
const wheel=art(192,24);
for(let frame=0;frame<8;frame++){
 const ox=frame*24,cx=11.5,cy=11.5,alpha=frame*Math.PI/4;
 for(let y=0;y<24;y++)for(let x=0;x<24;x++){
  const d=Math.hypot(x-cx,y-cy);
  if(d<=11.7)wheel.pixel(ox+x,y,d>=10.4?'b':d>=8?'a':d>=6.6?'e':d>=5.2?'i':'c');
  if(d>=8.4&&d<9.3&&x<=4&&y>=7&&y<=16)wheel.pixel(ox+x,y,'c');
 }
 for(let spoke=0;spoke<3;spoke++){
  const angle=alpha+spoke*Math.PI*2/3;
  for(let r=2;r<=6;r++){
   const x=Math.round(cx+Math.sin(angle)*r),y=Math.round(cy-Math.cos(angle)*r);
   wheel.pixel(ox+x,y,'i');
   if(r>=4)wheel.pixel(ox+x+1,y,'k');
  }
 }
 const valveX=Math.round(cx+7*Math.cos(alpha+.28)),valveY=Math.round(cy+7*Math.sin(alpha+.28));
 wheel.pixel(ox+valveX,valveY,'m');
 for(const [x,y,k] of [[11,11,'k'],[12,11,'k'],[11,12,'i'],[12,12,'b']])wheel.pixel(ox+x,y,k);
}
await mkdir(out,{recursive:true});
await Promise.all([body.save('coupe-body.png'),wheel.save('coupe-wheels-8.png')]);
console.log('COUNTRYSIDE_CAR_ASSETS_BUILT 156x63 body + eight 24x24 wheel poses');
