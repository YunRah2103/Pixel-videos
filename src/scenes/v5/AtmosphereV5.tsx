import React from 'react';

/**
 * Sunset Harbor V5 — original frame-driven atmosphere painting.
 * Scene space: 360 × 640; 30 fps. No CSS animation, noise textures,
 * nondeterministic randomness, filters, bloom, or foreign sprite assets.
 *
 * Integration order: sky, clouds, [distant landscape], air, water,
 * reflections, [architecture/harbour], lighting, [characters/foreground].
 * The sun is centred at (225,252), horizon is y=353, water ends at y=535.
 */
export type V5AtmospherePlaneName =
  'sky' | 'clouds' | 'water' | 'reflections' | 'lighting' | 'air';
export type V5AtmosphereProps = {
  frame: number;
  motion: any;
  plane: V5AtmospherePlaneName;
};

const WIDTH = 360, HEIGHT = 640;
const clamp = (v: number, lo = 0, hi = 1) => Math.max(lo, Math.min(hi,v));
const num = (value: unknown, fallback: number) =>
  typeof value === 'number' && Number.isFinite(value) ? value : fallback;
const mix = (a: number,b: number,t: number) => a+(b-a)*t;
const fract = (n: number) => n - Math.floor(n);
// Integer-only fixed seeds: never dependent on render order or current frame.
const seed = (n: number) => fract(Math.sin(n*91.137+37.211)*24531.781);
const colour = (a: string,b: string,t: number) => {
  const z = clamp(t);
  const h = (i:number) => Math.round(mix(parseInt(a.slice(i,i+2),16),parseInt(b.slice(i,i+2),16),z)).toString(16).padStart(2,'0');
  return '#' + h(1)+h(3)+h(5);
};
const rect=(x:number,y:number,w:number,h:number,fill:string,alpha=1)=>
  `<rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${Math.max(0.1,w).toFixed(2)}" height="${Math.max(0.1,h).toFixed(2)}" fill="${fill}" opacity="${clamp(alpha).toFixed(3)}"/>`;
const path=(d:string,fill:string,alpha=1)=>`<path d="${d}" fill="${fill}" opacity="${clamp(alpha).toFixed(3)}"/>`;
const stroke=(d:string,fill:string,w=1,alpha=1)=>
  `<path d="${d}" fill="none" stroke="${fill}" stroke-width="${w.toFixed(2)}" stroke-linecap="square" opacity="${clamp(alpha).toFixed(3)}"/>`;

const skyStops: [number,string][]=[
  [0,'#16374f'],[44,'#39516e'],[96,'#696b92'],
  [145,'#9682a5'],[192,'#c893b0'],[230,'#e6a6b1'],
  [277,'#f3b59e'],[322,'#f5c6a5'],[353,'#f5d5b1']
];
function paintSky(sunX:number,sunY:number,light:number){
 let o='';
 // Paired scanline pigments create a calm banded painted sky at native scale.
 for(let y=0;y<354;y+=2){
   let i=0;while(i<skyStops.length-2 && y>=skyStops[i+1][0])i++;
   const [ya,ca]=skyStops[i], [yb,cb]=skyStops[i+1];
   o+=rect(0,y,WIDTH,2,colour(ca,cb,(y-ya)/(yb-ya)));
 }
 // Deliberately broad translucent colour washes only in the neighbourhood
 // of the actual sun. Their irregular hand-shaped edges avoid flat overlays.
 o+=path(`M ${sunX-106} ${sunY+65} Q ${sunX-91} ${sunY+22} ${sunX-62} ${sunY-5}
 Q ${sunX-22} ${sunY-49} ${sunX+11} ${sunY-49}
 Q ${sunX+54} ${sunY-31} ${sunX+94} ${sunY+23}
 L ${sunX+115} ${sunY+72} Z`,'#f7b99f',.14*light);
 o+=path(`M ${sunX-54} ${sunY+42} Q ${sunX-48} ${sunY-19} ${sunX-19} ${sunY-31}
 Q ${sunX+6} ${sunY-41} ${sunX+34} ${sunY-20}
 Q ${sunX+57} ${sunY+12} ${sunX+77} ${sunY+43}Z`,'#ffe2b1',.24*light);
 // Fine nearby peach ribbons, with separate pink shadows.
 o+=stroke('M 10 231 Q 58 225 96 230 T 190 228', '#f3bab8',2,.38);
 o+=stroke('M 269 222 Q 302 219 354 215', '#ffd1b5',1.5,.38);
 o+=stroke('M 31 307 Q 80 304 140 310', '#e8acaf',1,.27);
 // Pixel-native disc; no radial blur or hard bloom halo.
 for(let ry=29;ry>=18;ry-=4){
   for(let yy=-ry;yy<ry;yy+=2){
      const radius=Math.sqrt(Math.max(0,ry*ry-(yy+1)*(yy+1)));
      o+=rect(sunX-radius,sunY+yy,radius*2,2,ry>26?'#ffd4a6':ry>22?'#ffe3b6':'#ffedc5',.65*light);
   }
 }
 for(let yy=-15;yy<=15;yy+=2){
   const radius=Math.sqrt(Math.max(0,16*16-yy*yy));
   o+=rect(sunX-radius,sunY+yy,2*radius,2,'#fff4d6',clamp(.82*light));
 }
 o+=stroke(`M ${sunX-10} ${sunY-5} h 21`,'#fff9e5',2,.72*light);
 return o;
}

/**
 * Six independently composed silhouette studies (hand-traced Bézier profiles).
 * Antialiased SVG curves are rasterized at only 360px, then nearest-upscaled;
 * edges are naturally pixel-shaped, not giant polygonal staircases.
 */
const cloudDrawings = [
 {base:'M -15 47 C -10 36 4 31 16 33 C 17 18 29 8 45 11 C 50 -3 66 -12 82 -8 C 93 -30 118 -32 131 -14 C 147 -22 164 -12 169 0 C 188 -2 202 12 203 27 C 226 27 237 38 240 52 L 236 62 Q 153 68 86 59 Q 31 70 -15 57 Z',
  mid:'M -7 44 Q 21 21 42 26 Q 49 0 76 5 Q 91 -18 114 -9 Q 134 -7 143 10 Q 169 -2 177 21 Q 206 22 225 48 L 190 55 Q 147 39 111 48 Q 61 43 20 56 Z',
  rim:'M 18 32 Q 30 20 45 21 Q 49 3 69 0 Q 81 -4 91 -1 Q 103 -23 122 -19 Q 137 -18 143 -5 Q 157 -12 167 3',
  cavity:'M 3 44 Q 29 38 48 44 Q 74 30 92 43 Q 122 34 144 46 Q 173 37 212 53 L 195 62 Q 158 55 135 58 Q 102 51 72 59 Q 31 55 3 54 Z'},
 {base:'M -16 55 Q -13 33 1 31 Q 7 14 26 16 Q 32 -1 50 3 Q 68 -25 91 -16 Q 111 -35 132 -19 Q 150 -20 163 -5 Q 178 -8 190 12 Q 207 9 214 28 Q 235 35 236 58 Q 133 67 62 63 Z',
  mid:'M -4 49 Q 13 27 32 29 Q 44 1 64 12 Q 79 -13 100 -3 Q 124 -26 145 -4 Q 167 1 173 15 Q 206 17 224 47 Q 179 41 145 54 Q 103 40 66 52 Q 25 48 -4 56 Z',
  rim:'M 13 32 Q 20 17 37 19 Q 44 3 59 5 Q 73 -17 95 -13 Q 107 -30 129 -21 Q 138 -15 148 -12',
  cavity:'M 2 45 Q 19 39 41 46 Q 61 36 82 46 Q 113 39 132 49 Q 166 38 183 51 Q 214 44 225 60 L 44 63 Z'},
 {base:'M -14 55 Q -14 40 4 35 Q 14 17 34 24 Q 40 2 59 5 Q 68 -13 89 -6 Q 96 -24 115 -19 Q 129 -26 143 -9 Q 171 -18 181 6 Q 204 3 209 21 Q 233 22 241 49 L 232 64 L 17 64 Z',
  mid:'M -2 45 Q 25 27 45 35 Q 57 7 82 12 Q 95 -12 118 -4 Q 141 -15 155 9 Q 185 5 195 26 Q 225 28 236 47 Q 191 41 169 52 Q 138 39 105 53 Q 55 45 10 57 Z',
  rim:'M 24 26 Q 37 16 51 23 Q 60 -1 78 3 Q 91 -15 111 -11 Q 131 -20 146 -6 Q 161 -12 174 5',
  cavity:'M -2 46 Q 25 48 45 42 Q 66 39 83 48 Q 110 35 129 46 Q 154 40 169 49 Q 203 43 230 53 L 221 65 L -5 62 Z'},
 {base:'M -13 55 Q -3 39 10 43 Q 15 22 38 26 Q 49 8 62 16 Q 74 -5 93 0 Q 100 -18 119 -12 Q 132 -19 150 -5 Q 171 -8 181 8 Q 201 8 208 30 Q 232 28 242 53 L 226 65 L -13 65 Z',
  mid:'M 2 50 Q 19 31 45 34 Q 61 11 80 23 Q 96 -1 115 7 Q 138 -7 157 16 Q 179 11 196 34 Q 220 38 231 55 Q 190 49 163 55 Q 128 45 103 56 Q 43 50 2 61 Z',
  rim:'M 22 36 Q 39 22 56 26 Q 64 9 85 12 Q 92 -8 115 -3 Q 136 -13 150 5',
  cavity:'M -3 47 Q 38 50 57 43 Q 84 39 106 49 Q 130 41 155 48 Q 190 45 218 55 L 204 64 L 5 65 Z'},
];
type CloudSpec={x:number;y:number;scale:number;kind:number;speed:number;depth:number};
const clouds:CloudSpec[]=[
 {x:-65,y:93,scale:.66,kind:0,speed:.83,depth:1},
 {x:134,y:66,scale:.68,kind:1,speed:-.53,depth:.8},
 {x:282,y:38,scale:.43,kind:2,speed:.64,depth:.6},
 {x:-101,y:181,scale:.62,kind:2,speed:.53,depth:.75},
 {x:77,y:174,scale:.43,kind:3,speed:-.39,depth:.66},
 {x:270,y:182,scale:.42,kind:1,speed:.32,depth:.7},
 {x:13,y:15,scale:.28,kind:3,speed:-.69,depth:.35},
];
function paintClouds(f:number,m:any){
 const drift=num(m.cloudDrift,f*.046);
 const ambient=clamp(num(m.lightIntensity,.96),.65,1.35);
 let o='';
 clouds.forEach((c,i)=>{
  const s=cloudDrawings[c.kind],dx=c.x+drift*c.speed,dy=c.y+Math.sin(f*.008+i)*.65*c.depth;
  const id='v5-cloud-mask-'+i;
  const cool=['#65738f','#716f91','#77738f','#787894'][c.kind];
  const pink=['#e8b5bf','#e8aabd','#eeb7c1','#edb6c1'][c.kind];
  const salmon=['#f6c9b7','#f1bdba','#f8c7b3','#ecc0ba'][c.kind];
  o+=`<g transform="translate(${dx.toFixed(3)} ${dy.toFixed(3)}) scale(${c.scale})">`;
  o+=`<defs><clipPath id="${id}"><path d="${s.base}"/></clipPath></defs>`;
  o+=path(s.base,cool,.94);
  o+=`<g clip-path="url(#${id})">`;
  o+=path(s.mid,pink,.98);
  o+=path('M -19 56 Q 17 46 40 51 Q 70 40 95 53 Q 126 45 154 56 Q 204 43 251 57 L 251 77 L -18 77 Z','#776f95',.68);
  o+=path(s.cavity,'#8e7e9d',.88);
  o+=stroke(s.rim,'#f8d5c3',1.8,.57*ambient);
  o+=stroke(s.rim,'#ffe9d0',3,.12);
  o+=stroke('M 8 40 Q 35 34 64 39 T 124 37','#ffdcc5',2,.46);
  o+=stroke('M 120 25 Q 151 16 183 31 T 224 41','#f6c5b9',3,.53);
  // Hand-laid broken illumination and lavender shadow clusters.
  o+=path('M 31 27 Q 48 20 65 24 L 92 20 Q 77 29 55 32 L 23 34 Z',salmon,.67);
  o+=path('M 109 4 Q 126 -3 145 9 L 161 18 Q 145 10 131 16 L 106 12 Z','#ffdbbf',.51);
  o+=path('M 26 49 Q 53 42 70 49 L 94 52 Q 62 55 26 53 Z','#625f88',.46);
  o+=stroke('M 71 43 Q 99 39 127 46 T 173 47','#bc94ad',2,.56);
  o+='</g>';
  o+=stroke('M 13 63 Q 44 65 74 62','#d5a4b7',1,.43);
  o+='</g>';
 });
 // Three delicate fixed stratus arrangements; motion is slow at depth.
 o+=stroke(`M ${-11+drift*.21} 224 Q ${35+drift*.21} 221 ${93+drift*.21} 225`,'#f7c4c0',1.7,.53);
 o+=stroke(`M ${253-drift*.18} 208 Q ${313-drift*.18} 205 ${375-drift*.18} 211`,'#ffd0ba',1.6,.45);
 o+=stroke(`M ${26-drift*.12} 146 Q ${67-drift*.12} 144 ${112-drift*.12} 148`,'#d9b2c0',1,.31);
 return o;
}
function paintWater(f:number,m:any,top:number,bottom:number){
 const phase=num(m.waterPhase,f*.073);
 let o='';
 const depth=bottom-top;
 // Deep, quiet teal strokes and a warm horizon; decreasing saturation nearby.
 const seaStops:[number,string][]=[
   [0,'#7ba7a3'],[.18,'#548e94'],[.45,'#367985'],
   [.74,'#245b70'],[1,'#173e58']
 ];
 for(let y=top;y<bottom;y+=2){
  const z=(y-top)/depth;
  let i=0;while(i<seaStops.length-2 && z>=seaStops[i+1][0])i++;
  o+=rect(0,y,360,Math.min(2,bottom-y),colour(seaStops[i][1],seaStops[i+1][1],(z-seaStops[i][0])/(seaStops[i+1][0]-seaStops[i][0])));
 }
 // Horizontal wave families each occupy a carefully spaced depth lane.
 // Smooth shared phase: no uncorrelated per-frame speckles or teleportation.
 const rows=21;
 for(let row=0;row<rows;row++){
  const z=(row+.5)/rows;
  const y=top+3+z*(depth-7);
  const count=Math.round(5+z*3);
  for(let k=0;k<count;k++){
    const key=row*31+k*107;
    const distribution=(k+.18+.65*seed(key+5))/count;
    const baseX=distribution*385-16;
    const x=baseX+Math.sin(phase*.42+row*.39+k*.78)*(1.3+z*4.0);
    const crestY=y+Math.sin(phase*.58+row*.31+k)*(0.38+z*1.14);
    const width=(7+z*27)*(.58+.66*seed(key+19));
    const amp=.5+z*.65;
    const col=(k+row)%7===0?'#a4c1ad':(k+row)%3===0?'#6fa99f':(k+row)%3===1?'#3e8790':'#467d89';
    o+=stroke(`M ${x.toFixed(2)} ${crestY.toFixed(2)}
      q ${(width*.28).toFixed(2)} ${(-amp).toFixed(2)} ${(width*.51).toFixed(2)} 0
      t ${(width*.49).toFixed(2)} ${(amp*.12).toFixed(2)}`,col,z>.8?1.5:1,.38+.38*(1-z));
    if(z>.52&&(k+row)%4===0){
      o+=stroke(`M ${(x+width*.24).toFixed(2)} ${(crestY+2).toFixed(2)} h ${(width*.62).toFixed(2)}`,'#143f57',1,.47);
    }
  }
 }
 // Only a dozen large low-frequency troughs; no blanket glitter.
 for(let row=0;row<12;row++){
   const z=(row+.65)/12, y=top+z*(depth-7);
   const x=22+seed(row*43+61)*320+Math.sin(phase*.19+row*1.5)*2*z;
   o+=stroke(`M ${x.toFixed(2)} ${y.toFixed(2)} q ${(15+z*21).toFixed(2)} 1 ${(28+z*49).toFixed(2)} -1`,'#113a54',1.25,.22+.22*z);
 }
 return o;
}
function paintReflections(f:number,m:any,top:number,bottom:number,sunX:number){
 const phase=num(m.waterPhase,f*.073),light=clamp(num(m.lightIntensity,.96),.6,1.32);
 const depth=bottom-top;
 let o='';
 // Wide, quiet golden path is locked to sun, broadened by perspective.
 // Deliberate crest groupings and breaks read as water, not pixel confetti.
 for(let row=0;row<25;row++){
  const z=(row+.32)/25, y=top+5+z*(depth-9);
  const span=7+Math.pow(z,1.35)*72;
  const count=3+Math.round(z*4.2);
  for(let j=0;j<count;j++){
    const key=173+row*67+j*37;
    const normalized=count===1?0:(j/(count-1)*2-1);
    const edge=normalized*.82+(seed(key)-.5)*.24;
    const slip=Math.sin(phase*.40+row*.66)*(.65+2.8*z);
    const x=sunX+edge*span+slip;
    const yy=y+Math.sin(phase*.52+row*.37+j*.58)*(.2+z*.73);
    const w=(5+z*28)*(.68+.52*seed(key+9))*(1-.30*Math.abs(edge));
    const warm=Math.abs(edge)>.58?'#eeb17f':(j+row)%5===0?'#fff5cd':(j+row)%2===0?'#ffe7aa':'#fbd093';
    const alpha=(.52+.30*(1-Math.abs(edge))+.08*z)*light*(.95+.05*Math.sin(phase*.48+row*.2));
    o+=stroke(`M ${(x-w*.5).toFixed(2)} ${yy.toFixed(2)}
       q ${(w*.27).toFixed(2)} -.55 ${(w*.52).toFixed(2)} 0
       t ${(w*.48).toFixed(2)} .14`,warm,z>.84&&row%4===0?2:1,alpha);
  }
 }
 // Sparse long crescents reinforce direction instead of micro-sparkle.
 for(let j=0;j<13;j++){
   const z=(j+.3)/14,y=top+7+z*(depth-8);
   const w=5+z*40, x=sunX-w*.55+Math.sin(phase*.33+j*.72)*z*4;
   o+=stroke(`M ${x.toFixed(2)} ${y.toFixed(2)} q ${(w*.5).toFixed(2)} -1 ${w.toFixed(2)} 0`,
     j%4===0?'#fff3ca':'#f5c28c',1.45,.34+.21*light);
 }
 // Waterfront lights reflect only in localized, correctly positioned ribbons.
 const lamps:[[number,number,string,number],[number,number,string,number],[number,number,string,number]]=[
   [30,399,'#f6cda2',13],[99,399,'#f7b5a0',19],[328,394,'#ffd4a6',27]
 ];
 for(const [lampX,startingY,shade,k] of lamps){
   for(let i=0;i<13;i++){
     const z=(i+.4)/13,y=startingY+z*Math.min(101,bottom-startingY-6);
     const x=lampX+(seed(i*9+k)-.5)*(2+z*13)+Math.sin(phase*.43+i*.84)*z;
     const w=2+z*8*seed(k+i*2);
     o+=stroke(`M ${x.toFixed(2)} ${y.toFixed(2)} h ${w.toFixed(2)}`,shade,1,(.33-.17*z)*light);
   }
 }
 return o;
}
function paintLighting(f:number,m:any){
 const light=clamp(num(m.lightIntensity,.96),.55,1.3);
 const breathe=.97+.03*Math.sin(f*.018); // coherent dusk shift, never flicker
 let o='';
 // Only small, optically local gradients: the existing V4 facade stays legible.
 for(const [x,y,power] of [[29,444,.9],[278,457,.78],[319,450,.68],[105,402,.55]]){
   o+=rect(x-7,y-6,15,12,'#ffd5ab',.043*light*power*breathe);
   o+=rect(x-4,y-3,9,6,'#ffd9ae',.075*light*power*breathe);
   o+=rect(x-1,y-1,3,2,'#ffebbe',.27*light*power*breathe);
 }
 // Thin bounced light along masonry edges, not invented bright windows.
 o+=stroke('M 3 394 L 122 392','#ffd8ad',1,.16*light);
 o+=stroke('M 293 391 L 358 382','#ffdbb4',1,.20*light);
 o+=rect(31,383,5,8,'#ffdea8',.18*light);
 o+=rect(98,382,5,8,'#ffdda9',.18*light);
 o+=rect(318,381,5,9,'#ffe2b0',.18*light);
 return o;
}
function paintAir(f:number,m:any,top:number){
 const drift=num(m.cloudDrift,f*.046);
 let o='';
 // Mist is limited to the mountains' last 25 pixels; never a fullscreen tint.
 o+=path(`M 0 ${top-21} Q 43 ${top-25} 85 ${top-20} T 169 ${top-22}
 Q 232 ${top-26} 296 ${top-22} L 360 ${top-24} L 360 ${top-8} L 0 ${top-7} Z`,'#f5c3b0',.085);
 o+=path(`M 0 ${top-11} Q 62 ${top-17} 114 ${top-11} T 240 ${top-13}
 Q 303 ${top-15} 360 ${top-9} L 360 ${top+3} L 0 ${top+3} Z`,'#9cbcaf',.10);
 for(let i=0;i<7;i++){
   const x=(i*53+22+drift*(i%2?.12:-.14));
   o+=rect(x,top-12+(i%3)*3,15+i%3*8,1,i%3===0?'#ffe0ba':'#c1b5b9',.15);
 }
 return o;
}

/** Optional Agent-3 motion keys: cloudDrift, waterPhase, lightIntensity,
 * sunX, sunY, waterTop, waterBottom, waveStrength. Missing keys use local
 * frame-derived deterministic defaults. Never relies on a shared animation
 * state object or a changing camera.
 */
export function renderV5AtmosphereFragment(frame:number,motion:any,plane:V5AtmospherePlaneName):string {
 const f=Math.max(0,Math.floor(num(frame,0)));
 const m=motion&&typeof motion==='object'?motion:{};
 const sunX=num(m.sunX,225),sunY=num(m.sunY,252);
 const waterTop=clamp(num(m.waterTop,353),330,390);
 const waterBottom=clamp(num(m.waterBottom,535),490,555);
 switch(plane){
  case 'sky':return paintSky(sunX,sunY,clamp(num(m.lightIntensity,.96),.6,1.3));
  case 'clouds':return paintClouds(f,m);
  case 'water':return paintWater(f,m,waterTop,waterBottom);
  case 'reflections':return paintReflections(f,m,waterTop,waterBottom,sunX);
  case 'lighting':return paintLighting(f,m);
  case 'air':return paintAir(f,m,waterTop);
 }
}
/**
 * A full-size transparent SVG plane, designed to be depth-composited
 * by Agent 4. No shared Root or other agents' source is modified.
 */
export const V5AtmospherePlane:React.FC<V5AtmosphereProps>=({frame,motion,plane})=>{
 const svg=renderV5AtmosphereFragment(frame,motion,plane);
 return <svg xmlns="http://www.w3.org/2000/svg"
   width={WIDTH} height={HEIGHT} viewBox="0 0 360 640"
   shapeRendering="crispEdges" preserveAspectRatio="xMidYMid meet"
   style={{width:WIDTH,height:HEIGHT,position:'absolute',left:0,top:0,
     overflow:'hidden',imageRendering:'pixelated',pointerEvents:'none'}}
   dangerouslySetInnerHTML={{__html:svg}} />;
};
