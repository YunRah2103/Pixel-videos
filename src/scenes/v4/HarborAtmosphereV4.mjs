/**
 * Sunset Harbor V4 atmospheric paint — Agent 2.
 * Standalone deterministic SVG fragments, native 360x640 pixel coordinate space.
 * No unseeded randomness, CSS animations, external image assets or filters.
 * Integrators should layer: clouds (behind landscape), water, waterHighlights
 * (behind boats/piers), illumination (over architecture), nearAir (over distance).
 */
export const HARBOR_V4_FX_GEOMETRY=Object.freeze({width:360,height:640,sunX:227,sunY:273,waterTop:353,waterBottom:535});
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const finite=(v,otherwise)=>Number.isFinite(Number(v))?Number(v):otherwise;
const frac=(x)=>x-Math.floor(x);
const hash=(n)=>frac(Math.sin(n*127.1+78.233)*43758.5453123);
const rr=(x,y,w,h,c,opacity)=>'<rect x="'+Math.round(x)+'" y="'+Math.round(y)+'" width="'+Math.max(1,Math.round(w))+'" height="'+Math.max(1,Math.round(h))+'" fill="'+c+'"'+(opacity===undefined?'':' opacity="'+clamp(opacity,0,1).toFixed(3)+'"')+'/>';
const pp=(points,c,opacity)=>'<polygon points="'+points.map(q=>Math.round(q[0])+','+Math.round(q[1])).join(' ')+'" fill="'+c+'"'+(opacity===undefined?'':' opacity="'+clamp(opacity,0,1).toFixed(3)+'"')+'/>';
const h=(a,b,t)=>a+(b-a)*t;
const rgb=(a,b,t)=>'#'+a.slice(1).match(/../g).map((x,i)=>Math.round(h(parseInt(x,16),parseInt(b.slice(1+2*i,3+2*i),16),t)).toString(16).padStart(2,'0')).join('');
const palette=[{y:0,c:'#133b59'},{y:48,c:'#275c7c'},{y:102,c:'#5b769a'},{y:151,c:'#9889ae'},{y:198,c:'#ce9eb1'},{y:240,c:'#f0b1aa'}];
const clouds=[
 {x:-74,y:63,s:1.25,k:0,v:0.11},
 {x:140,y:61,s:1.00,k:1,v:-0.10},
 {x:250,y:124,s:0.83,k:2,v:0.08},
 {x:-55,y:186,s:0.72,k:3,v:-0.055},
 {x:206,y:206,s:0.56,k:4,v:0.05},
 {x:43,y:13,s:0.68,k:5,v:0.13},
];
const silhouettes=[
 [[-12,42],[-10,29],[0,29],[0,17],[13,17],[13,4],[28,4],[28,-8],[42,-8],[42,-17],[66,-17],[66,-10],[80,-10],[80,1],[96,1],[96,10],[118,10],[118,20],[143,20],[143,34],[154,34],[154,46]],
 [[-18,47],[-18,33],[-5,33],[-5,19],[7,19],[7,10],[22,10],[22,-2],[39,-2],[39,-17],[60,-17],[60,-9],[78,-9],[78,-1],[102,-1],[102,10],[128,10],[128,22],[145,22],[145,43]],
 [[-20,37],[-17,28],[-9,28],[-9,16],[3,16],[3,7],[19,7],[19,-7],[32,-7],[32,-16],[49,-16],[49,-11],[65,-11],[65,-3],[85,-3],[85,8],[108,8],[108,19],[139,19],[139,28],[150,28],[150,44]],
 [[-18,43],[-18,27],[-8,27],[-8,16],[13,16],[13,6],[26,6],[26,-5],[47,-5],[47,-12],[62,-12],[62,-3],[82,-3],[82,10],[96,10],[96,16],[129,16],[129,26],[149,26],[149,43]],
 [[-16,37],[-10,23],[0,23],[0,10],[22,10],[22,2],[39,2],[39,-8],[63,-8],[63,0],[82,0],[82,10],[106,10],[106,20],[137,20],[137,31],[156,31],[156,42]],
 [[-16,39],[-12,25],[1,25],[1,14],[12,14],[12,3],[37,3],[37,-13],[52,-13],[52,-5],[72,-5],[72,7],[88,7],[88,14],[113,14],[113,22],[141,22],[141,36]]
];
function sculptCloud(c,offset,energy){
 const sh=silhouettes[c.k],k=c.k,light=k%3===0?['#596c90','#a193b1','#e7acb4','#ffe5b7']:k%3===1?['#607694','#a59cb6','#efb7b6','#ffe9bb']:['#597b97','#b19ebb','#f1b8b6','#ffe4c5'];
 const drift=offset*c.v;
 let t='';
 // Individual staggered sculpted silhouettes, rather than overlapped rectangular pills.
 t+=pp(sh.concat([[153,52],[-18,52]]),light[0]);
 t+=pp(sh.map(([x,y])=>[x-1,y-3]).concat([[150,41],[-13,41]]),light[1]);
 t+=pp([[5,28],[11,13],[30,13],[30,2],[44,2],[44,-8],[57,-8],[57,-1],[71,-1],[71,10],[93,10],[93,17],[112,17],[112,23],[133,23],[133,34],[5,34]],light[2]);
 t+=pp([[19,17],[31,12],[31,0],[44,0],[44,-9],[56,-9],[56,-1],[69,-1],[69,8],[82,8],[82,13],[96,13],[96,17],[57,17],[57,14],[19,14]],light[3]);
 t+=pp([[9,34],[35,35],[35,39],[62,39],[62,43],[88,43],[88,46],[134,46],[134,50],[8,50]],'#6c7895');
 t+=pp([[78,21],[85,13],[100,13],[100,20],[119,20],[119,27],[136,27],[136,36],[124,36],[124,32],[96,32],[96,27],[78,27]],'#cf9eb0');
 // Art-directed shadow joints, crown rim lighting and body facets.
 const facets=[
  [[2,27],[17,27],[17,21],[28,21],[28,25],[36,25],[36,31],[2,31]],
  [[34,9],[50,9],[50,13],[67,13],[67,17],[40,17]],
  [[67,27],[83,27],[83,21],[104,21],[104,26],[123,26],[123,31],[67,31]],
  [[48,36],[67,36],[67,39],[93,39],[93,42],[50,42]],
  [[19,42],[36,42],[36,45],[52,45],[52,47],[19,47]]
 ];
 facets.forEach((poly,i)=>{t+=pp(poly,[light[0],light[3],light[1],light[2],'#79839e'][i],i===1?.9:1)});
 for(let j=0;j<26;j++){
  const x=-3+j*5.5+hash(k*47+j)*3, y=31+hash(j+k*21)*9;
  t+=rr(x,y,1+(j%3),j%5===0?2:1,j%7===0?'#f4c4ba':j%3===0?'#69799a':'#a28fac',0.8);
 }
 // Subtle coherent breathing changes only illumination, not cloud shape.
 t+=rr(24,7,25,2,'#fff1c6',0.20+energy*.12);
 return '<g transform="translate('+Math.round(c.x+drift)+' '+c.y+') scale('+c.s+')">'+t+'</g>';
}
function skyAndClouds(frame,m,geo){
 const drift=finite(m.cloudDrift,frame/30),light=clamp(finite(m.lightIntensity,.93),0.6,1.3);
 let out='';
 for(let y=0;y<238;y+=2){
  let i=0;while(i<palette.length-2&&y>palette[i+1].y)i++;
  const a=palette[i],b=palette[i+1];out+=rr(0,y,360,2,rgb(a.c,b.c,clamp((y-a.y)/(b.y-a.y),0,1)));
 }
 // Atmospheric receding bands below cloud undersides; jagged, crisp boundaries.
 out+=pp([[0,183],[30,180],[57,185],[95,179],[142,183],[175,178],[226,181],[270,174],[316,182],[360,176],[360,185],[0,192]],'#e3acb8',.16);
 out+=pp([[0,222],[49,220],[94,225],[135,219],[167,221],[219,218],[251,219],[300,213],[360,219],[360,224],[0,228]],'#ffe0bc',.23);
 clouds.forEach((c,i)=>{out+=sculptCloud(c,drift*(1+i*.03),light)});
 // Scattered distant stratus strokes are individually grouped; no framewise noise.
 for(let i=0;i<17;i++){
  const x=hash(i*11+5)*380-12,y=157+hash(i*6+3)*70;
  out+=rr(x+drift*(i%2?-.07:.07),y,12+(i%6)*7,1+(i%8===0?1:0),i%3===0?'#ffd4be':'#b4a3b9',.56);
 }
 return out;
}
function ocean(frame,m,g){
 const start=g.waterTop,end=g.waterBottom;
 const phase=finite(m.waterPhase,frame*.087);
 let out='';
 for(let y=start;y<end;y+=2){
  const z=(y-start)/(end-start);
  out+=rr(0,y,360,2,rgb('#5c9ba0','#103c57',Math.pow(z,.84)));
 }
 // Large coherent, phase-locked wave families. Individual streaks advect without jitter.
 for(let j=0;j<72;j++){
  const z=(j+.5)/72, y=start+4+z*(end-start-7);
  const amp=1+z*3.7,wide=4+z*32;
  for(let i=0;i<5;i++){
   const bx=frac(hash(j*17+i*31)*.4+i/5+.08)*410-25;
   const x=bx+Math.sin(phase*.3+j*.43+i*1.7)*amp;
   const yy=y+Math.sin(phase*.53+j*.36+i*2.4)*(.30+z*1.7);
   const shade=(i+j)%7===0?'#9ebbac':(i+j)%3===0?'#64a4a5':(i+j)%3===1?'#2a7283':'#387f89';
   out+=rr(x,yy,wide*(.26+.73*hash(j*7+i)),z>.77&&i%3===0?2:1,shade,.43+.34*(1-z));
   if(z>.40&&i%4===0)out+=rr(x+5,yy+2,wide*.29,1,'#143f59',.7);
  }
 }
 // Broad rolling dark troughs produce perspective and rhythm under highlights.
 for(let j=0;j<22;j++){
  const z=(j+.7)/22,y=start+z*(end-start-4);
  const x=(j*83)%420-25+Math.sin(phase*.22+j)*4*z;
  out+=rr(x,y,26+z*52,1+Number(z>.83),'#113e56',.18+.17*z);
 }
 return out;
}
function waterLighting(frame,m,g){
 const top=g.waterTop,depth=g.waterBottom-top,phase=finite(m.waterPhase,frame*.087);
 const sunX=g.sunX,light=clamp(finite(m.lightIntensity,.93),.55,1.35);
 let out='';
 // The core stays under the sun, broadening towards the viewer.
 for(let i=0;i<250;i++){
  const z=(i+.5)/250,y=top+7+z*(depth-9);
  const span=3+Math.pow(z,1.37)*89;
  const centre=sunX+Math.sin(phase*.22+z*8)*1.4;
  const stripes=1+(i%4===0?1:0);
  for(let s=0;s<stripes;s++){
   const seed=i*17+s*31,dist=(hash(seed+38)*2-1),edge=Math.abs(dist);
   const x=centre+dist*span+Math.sin(phase*.42+z*11+s*2+i*.8)*(1+z*2);
   const len=(2+z*17)*(1-edge*.59)*(0.58+hash(seed+5)*.65);
   const bright=edge<.35?'#fff0bf':edge<.68?'#ffdaa8':'#dba695';
   const opacity=(.24+.56*(1-edge))*(.80+Math.sin(phase*.3+i*.37)*.08)*light;
   out+=rr(x,y,len,z>.78&&i%9===0?2:1,bright,clamp(opacity,.15,.94));
  }
 }
 // A few longer wave crests across the ribbon, aligned with the wave phase.
 for(let j=0;j<31;j++){
  const z=.07+j/34,y=top+z*depth;
  const w=4+z*66,x=sunX-w*.55+Math.sin(phase*.28+j*.83)*(2+z*4);
  out+=rr(x,y,w,1,j%4===0?'#fff2c2':'#f8ca9e',(.24+.19*Math.sin(j+phase*.43))*light);
 }
 // Coherent reflections from lit shopfronts and quay lamps, offset from solar path.
 for(const [cx,col,seed] of [[33,'#ffcf99',17],[86,'#f6b29e',29],[307,'#ffd6a3',43],[342,'#f5b7ac',61]]){
  for(let j=0;j<43;j++){
   const z=(j+.4)/43, y=381+z*(Math.min(516,g.waterBottom)-381);
   const x=cx+(hash(j*11+seed)-.5)*(4+z*29)+Math.sin(phase*.5+j*.71)*(1+z*2);
   out+=rr(x,y,2+z*(4+hash(j+seed)*14),j%17===0?2:1,col,(.22+(1-z)*.35)*light);
  }
 }
 // Boat disturbance wakes: optional motion boatX or fixed V3 tracking fallback.
 const boat=finite(m.boatX,276-frame*.105),by=finite(m.boatY,406)+finite(m.boatBob,0);
 for(let j=0;j<15;j++){
  const spread=j*5.2,xx=boat-15-spread,yy=by+16+j*.9+Math.sin(phase*.25+j)*1.2;
  out+=rr(xx,yy,2+j*.5,1,j%3===0?'#efc6a7':'#83afaa',(.29-j*.012)*light);
 }
 return out;
}
function lampAndWindowLight(frame,m,g){
 const light=clamp(finite(m.lightIntensity,.93),.5,1.4),sway=.96+.035*Math.sin(frame*.018);
 let out='';
 // Very small stepped halos; keep crisp pixels and dark silhouettes intact.
 for(const [x,y,power] of [[29,444,1],[278,457,.9],[35,452,.75],[319,451,.6]]){
  const a=power*light*sway;
  out+=rr(x-11,y-11,26,19,'#f8bd90',.055*a);
  out+=rr(x-7,y-8,18,12,'#ffd2a2',.09*a);
  out+=rr(x-4,y-6,12,8,'#ffe0b0',.10*a);
  out+=rr(x,y-4,3,3,'#fff3cf',.83*a);
 }
 // Window illumination is concentrated on explicitly placed V3 facade details.
 for(const [x,y,seed] of [[18,318,1],[36,340,2],[52,324,3],[77,342,4],[91,324,5],[116,320,6],[130,345,7],[289,324,8],[320,314,9],[337,345,10]]){
  const a=(.20+.05*Math.sin(frame*.013+seed*2.3))*light;
  out+=rr(x-2,y-1,10,11,'#ffbc8e',.055*a);
  out+=rr(x,y,6,7,seed%3===0?'#fff0bf':'#ffe2b0',a);
  out+=rr(x+1,y+1,2,3,'#fff2ca',a*.48);
 }
 // Sunward edges of harbour waterline, very restrained warm fringe.
 out+=rr(157,g.waterTop-3,103,1,'#ffddb8',.15*light);
 out+=rr(185,g.waterTop-5,54,1,'#fff0c6',.17*light);
 return out;
}
function airDetails(frame,m,g){
 const t=frame/30,drift=finite(m.cloudDrift,t);
 let out='';
 // Layered distant moisture, confined to the ridge and horizon, never fullscreen fog.
 out+=pp([[0,335],[43,332],[89,335],[133,332],[178,336],[219,332],[263,335],[317,331],[360,334],[360,352],[0,352]],'#ffd4b5',.080);
 out+=pp([[0,346],[54,345],[92,349],[157,344],[228,348],[282,342],[360,346],[360,353],[0,353]],'#91b2ad',.11);
 for(let j=0;j<11;j++){
  const x=hash(j*39+8)*385-20+drift*(j%2?.11:-.07),y=324+j%4*5;
  out+=rr(x,y,13+j%4*8,1,j%3===0?'#ffdabb':'#aab4b5',.11);
 }
 // Tiny far-distance gull silhouettes follow continuous trajectories.
 for(let i=0;i<4;i++){
  const x=(28+i*44+t*(1.8+i*.18))%418-28;
  const y=179+(i%3)*18+Math.sin(t*.64+i)*1.2;
  const rise=Math.sin(t*2.5+i*1.6)>0? -1:1;
  out+=rr(x-4,y+rise,4,1,'#516d83',.80)+rr(x,y,3,1,'#526981',.8)+rr(x+3,y-rise,4,1,'#516d83',.80);
 }
 return out;
}
/**
 * @param {number} frame Frame index; arbitrary seek order supported.
 * @param {object} motion V3/V4 motion with optional cloudDrift, waterPhase,
 *    lightIntensity, sunX, sunY, waterTop, waterBottom, boatX, boatBob.
 * @returns {{clouds:string,water:string,waterHighlights:string,illumination:string,nearAir:string}}
 */
export function renderHarborFxLayers(frame,motion={}){
 const f=Math.max(0,Math.floor(finite(frame,0)));
 const m=motion&&typeof motion==='object'?motion:{};
 const g={
  sunX:finite(m.sunX,227),sunY:finite(m.sunY,273),
  waterTop:clamp(finite(m.waterTop,353),320,450),
  waterBottom:clamp(finite(m.waterBottom,535),470,570)
 };
 return {
  clouds:skyAndClouds(f,m,g),
  water:ocean(f,m,g),
  waterHighlights:waterLighting(f,m,g),
  illumination:lampAndWindowLight(f,m,g),
  nearAir:airDetails(f,m,g),
 };
}
