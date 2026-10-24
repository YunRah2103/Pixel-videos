/**
 * Sunset Harbor V3 — hand-authored pixel sprites / life layer.
 * All marks are authored SVG primitives on the native 360x640 grid.
 * Compatible with Agent 1's future HarborWorld: call harborLifeSvg(motion)
 * above its environment, or import the individual components below.
 */
const n = value => Math.round(value);
const rect=(x,y,w,h,c)=>`<rect x="${n(x)}" y="${n(y)}" width="${Math.max(1,n(w))}" height="${Math.max(1,n(h))}" fill="${c}"/>`;
const poly=(pts,c)=>`<polygon points="${pts.map(([x,y])=>`${n(x)},${n(y)}`).join(' ')}" fill="${c}"/>`;
const g=(x,y,content,extra='')=>`<g transform="translate(${n(x)},${n(y)})" ${extra}>${content}</g>`;
const sin=(a)=>Math.sin(a);
const ease=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
const d=(frame,period,phase=0)=>sin(frame*2*Math.PI/period+phase);

// Two carefully constructed mini-actors; character action is mostly silhouette,
// but limbs and head poses are individually articulated, not just sliding boxes.
export function harborCoupleSvg(m){
 const f=m.frame;
 const breathe=d(f,86)*0.55, turn=Math.round(m.glance*2);
 const hand=Math.round(m.handhold*6);
 const sway=Math.round(d(f,180)*0.7);
 const x=216,y=491;
 let a='';
 // Shadow on flagstones, never a floating torso.
 a+=rect(x-5,y+39,35,2,'#243d50')+rect(x+4,y+41,27,1,'#34475a');
 // Person one: sunset overcoat and loose scarf, left foot steps then settles.
 a+=g(x+sway,y,
   rect(3,27,5,13,'#27394c')+rect(12,27,4,13,'#263a4b')+
   poly([[0,11],[15,10],[19,30],[-3,30]],'#517184')+
   rect(-2,14,4,11,'#425e71')+rect(15,14,5,9,'#375364')+
   rect(2,0,11,12,'#d8a58d')+rect(1,-2,13,5,'#4b455a')+
   rect(2+turn,3,3,2,'#ebc09c')+rect(11,9,4,4,'#ad7680')+
   poly([[8,11],[15,12],[13,18],[5,16]],'#d9a08e')+
   rect(15,19,3+hand,3,'#e5b39a'));
 // Person two: aubergine shawl, hair sweep, knee/hand shift with small head turn.
 a+=g(x+21-sway,y+1+Math.round(breathe),
   rect(1,30,5,10,'#283b4f')+rect(11,30,4,10,'#293d50')+
   poly([[2,10],[14,10],[19,31],[-3,31]],'#9e788e')+
   poly([[12,13],[18,17],[20,28],[16,27]],'#bc8693')+
   rect(0,0,11,12,'#e4ac93')+rect(-1,-3,14,5,'#403c55')+
   rect(8,-6,7,7,'#463e56')+rect(3,4,2,1,'#6b5162')+
   rect(-4,17,4+Math.round(m.wave*5),3,'#e1ac92')+
   rect(-2-hand,21,3+hand,3,'#e6b69d'));
 // their hands meet at the end, a held moment not a random swing
 if(m.handhold>0.65) a+=rect(x+17,y+21,6,2,'#e9b99d');
 // Small scarf tail flutter, following the sea breeze.
 a+=poly([[x+13,y+13],[x+18,y+15],[x+17+Math.round(m.foliageSway),y+23],[x+14,y+19]],'#dfac95');
 return a;
}

export function harborCatSvg(m){
 const x=m.catX,y=535,step=m.catStep;
 const walking=1-ease((m.frame-282)/38);
 const leg=step%2?2:-1;
 let body=rect(1,2,14,7,'#28394b')+rect(5,0,9,4,'#364455');
 body+=poly([[12,1],[13,-5],[16,0]],'#263a4a')+
       poly([[18,0],[19,-5],[21,1]],'#28394a')+
       rect(12,-1,9,8,'#303e51')+
       rect(19,2,1,1,'#f6dba0')+
       rect(3,8,3,4+walking*leg,'#26374a')+
       rect(11,8,3,4-walking*leg,'#26374a');
 // Curved, articulated tail rises as the cat stops.
 body+=rect(-2,0,3,9,'#263a49')+
       rect(-5,-3-Math.round(m.catSit*3),3,6,'#263a49');
 if(m.catSit>0.1){
   const crouch=Math.round(m.catSit*3);
   body+=rect(2,8-crouch,14,5,'#28394b');
 }
 return g(x,y+Math.round(d(m.frame,29)*0.65*walking),body);
}
export function harborBoatSvg(m){
 const f=m.frame,x=m.boatX,y=406+m.boatBob;
 let a=rect(x-12,y+14,61,2,'#608d8e');
 a+=poly([[x,y+1],[x+46,y+1],[x+39,y+11],[x+9,y+11]],'#293f56');
 a+=rect(x+8,y,31,3,'#bf827c')+rect(x+16,y-6,20,6,'#eac0a0');
 a+=rect(x+21,y-25,2,20,'#334e61');
 a+=poly([[x+23,y-23],[x+23,y-5],[x+39,y-5]],'#e9d4ae');
 a+=rect(x+12,y+12,27,2,'#759797');
 for(let k=0;k<4;k++)a+=rect(x-13-k*12,y+9+(k%2)*3,6+Math.floor(k/2)*3,1,k%2?'#9aafaa':'#d5ad91');
 return a;
}
export function harborBirdsSvg(m){
 let out='';
 for(let i=0;i<5;i++){
   const x=33+i*21+m.frame*(0.09+i*0.012)-m.cameraX*m.parallax.sky;
   const y=205+(i%3)*13+d(m.frame,128,i)*2;
   const up=((m.gullWing+i)%4)<2;
   const c=i%2?'#54738a':'#3b687e';
   out+=rect(x,y,3,1,c)+rect(x-4,y+(up?-2:1),4,1,c)+
       rect(x+3,y+(up?-2:1),4,1,c);
 }
 return out;
}
export function harborBreezeSvg(m){
 const f=m.frame;
 let out='';
 // Light catches several individual flowers and paper streamers in the near field.
 for(let i=0;i<13;i++){
   const x=8+i*28,y=621+(i%3)*5;
   const s=Math.round(d(f,102,i*0.83)*2+m.foliageSway*0.5);
   out+=rect(x,y-10,1,10,'#48776c')+
       rect(x-2+s,y-13,5,4,i%4?'#7aa58b':'#e2a397');
   if(i%3===0)out+=rect(x+s,y-16,2,2,'#edba9f');
 }
 // Far lanterns slowly breathe in the scene, no featureless blur overlay.
 for(const [x,y] of [[31,444],[278,456]]){
   if(m.lightIntensity>0.87)out+=rect(x-3,y-6,8,1,'#ffe1b0');
   out+=rect(x,y-3,3,2,m.lightIntensity>0.90?'#fff1bd':'#efd1a1');
 }
 return out;
}
export function harborWaterAccentsSvg(m){
 let out='';
 const f=m.frame;
 for(let i=0;i<93;i++){
   const z=((i*29+11)%149)/149;
   const y=374+z*141;
   const bx=227+(i%2?1:-1)*z*46;
   const x=bx+Math.sin(m.waterPhase*0.55+i*3.8)*(2+z*7);
   if((i+Math.floor(f/11))%5!==0)
     out+=rect(x,y,2+Math.round(z*14),1,i%4===0?'#fff0bd':'#e7b99d');
 }
 return out;
}
/** SVG overlay can sit over old V2 art or Agent 1's HarborWorld. */
export function harborLifeSvg(m){
 const layers=[
  `<g opacity="0.75">${harborBirdsSvg(m)}</g>`,
  `<g opacity="0.76">${harborWaterAccentsSvg(m)}</g>`,
  // The boat moves in the mid-ground; open space near the right dock.
  `<g opacity="0.93">${harborBoatSvg(m)}</g>`,
  `<g>${harborCoupleSvg(m)}${harborCatSvg(m)}</g>`,
  `<g>${harborBreezeSvg(m)}</g>`,
 ];
 return `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">${layers.join('')}</svg>`;
}
