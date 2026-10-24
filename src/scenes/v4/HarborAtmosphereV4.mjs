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
 {x:-85,y:99,s:1.06,k:0,v:0.13},
 {x:159,y:55,s:.89,k:1,v:-0.092},
 {x:105,y:153,s:.75,k:2,v:0.085},
 {x:-104,y:211,s:.55,k:3,v:-0.065},
 {x:265,y:175,s:.65,k:4,v:0.056},
 {x:15,y:12,s:.55,k:5,v:0.106},
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
 const k=c.k;
 const shapes=[
  [[-36,61],[-36,48],[-26,48],[-26,33],[-12,33],[-12,17],[6,17],[6,2],[28,2],[28,-12],[47,-12],[47,-27],[69,-27],[69,-35],[84,-35],[84,-27],[105,-27],[105,-15],[128,-15],[128,-2],[146,-2],[146,12],[163,12],[163,25],[188,25],[188,35],[218,35],[218,49],[238,49],[238,69],[-36,69]],
  [[-22,56],[-22,42],[-9,42],[-9,28],[6,28],[6,11],[19,11],[19,-3],[35,-3],[35,-20],[56,-20],[56,-29],[76,-29],[76,-18],[91,-18],[91,-7],[112,-7],[112,-24],[132,-24],[132,-39],[151,-39],[151,-30],[167,-30],[167,-16],[182,-16],[182,0],[198,0],[198,14],[220,14],[220,30],[238,30],[238,56]],
  [[-36,53],[-36,39],[-15,39],[-15,27],[6,27],[6,14],[31,14],[31,2],[50,2],[50,-11],[67,-11],[67,-18],[86,-18],[86,-8],[105,-8],[105,5],[127,5],[127,14],[147,14],[147,2],[165,2],[165,-9],[184,-9],[184,2],[199,2],[199,18],[220,18],[220,36],[241,36],[241,56]],
  [[-26,48],[-26,34],[-12,34],[-12,22],[10,22],[10,7],[24,7],[24,-7],[46,-7],[46,-20],[65,-20],[65,-15],[91,-15],[91,-3],[116,-3],[116,8],[143,8],[143,18],[162,18],[162,31],[189,31],[189,48]],
  [[-32,52],[-32,39],[-15,39],[-15,26],[2,26],[2,13],[29,13],[29,0],[46,0],[46,-14],[63,-14],[63,-24],[83,-24],[83,-12],[108,-12],[108,-2],[129,-2],[129,9],[155,9],[155,0],[171,0],[171,14],[193,14],[193,28],[221,28],[221,53]],
  [[-23,54],[-23,36],[-8,36],[-8,24],[13,24],[13,9],[38,9],[38,-4],[59,-4],[59,-17],[79,-17],[79,-28],[95,-28],[95,-14],[116,-14],[116,-4],[139,-4],[139,11],[164,11],[164,24],[183,24],[183,40],[205,40],[205,57]]
 ];
 const outline=shapes[k];
 const cool=['#7586a1','#7486a2','#7b849e','#8885a7','#7e8da8','#7d8ba9'][k];
 const mid=['#ae94b2','#afa3bd','#c4a2bb','#ae9fba','#aa9dbc','#9fa3c0'][k];
 const warm=['#e9b1bc','#efbcb9','#ffccbb','#e7b4c2','#f4b5b9','#dec2c9'][k];
 const gold=['#ffe2b2','#fff0c9','#ffe2b7','#f7d5b6','#ffe8c1','#ffe6c6'][k];
 const id='v4_cloud_clip_'+k;
 const points=outline.map(([x,y])=>x+','+y).join(' ');
 let a='<defs><clipPath id="'+id+'"><polygon points="'+points+'"/></clipPath></defs>';
 // The entire body is masked to a unique hand-authored silhouette.
 a+=pp(outline,cool);
 a+='<g clip-path="url(#'+id+')">';
 a+=pp([[-45,7],[22,-20],[82,-43],[159,-25],[261,3],[261,38],[-45,49]],mid);
 a+=pp([[-47,24],[-13,10],[29,-14],[77,-25],[133,-17],[184,3],[263,22],[263,49],[-47,45]],warm,.94);
 a+=pp([[-39,51],[23,43],[64,51],[113,42],[151,53],[207,42],[252,53],[254,76],[-39,76]],cool,.77);
 a+=pp([[-40,44],[18,33],[63,40],[101,32],[157,39],[194,32],[257,43],[258,51],[214,51],[160,47],[122,50],[76,46],[19,49],[-40,54]],'#8b89a6',.92);
 // Golden crown and cascading stepped rim, oriented towards the sinking sun.
 a+=pp([[8,16],[8,1],[25,1],[25,-13],[48,-13],[48,-28],[68,-28],[68,-34],[82,-34],[82,-25],[101,-25],[101,-12],[119,-12],[119,-7],[92,-7],[92,-13],[68,-13],[68,-7],[49,-7],[49,0],[29,0],[29,10],[12,10],[12,20]],gold,.92);
 a+=pp([[106,2],[116,-12],[132,-12],[132,-24],[150,-24],[150,-32],[162,-32],[162,-18],[176,-18],[176,-4],[191,-4],[191,9],[220,9],[220,15],[187,15],[187,8],[167,8],[167,3],[143,3],[143,9],[122,9],[122,15]],gold,.57);
 // Painterly lavender cavity shadows are placed on structural seams.
 a+=pp([[-24,32],[-8,24],[12,24],[12,31],[32,31],[32,36],[57,36],[57,44],[6,44],[6,40],[-24,40]],'#7b819f',.82);
 a+=pp([[67,28],[86,19],[104,19],[104,27],[125,27],[125,32],[145,32],[145,37],[173,37],[173,44],[96,44],[96,37],[67,37]],'#9e8da9',.89);
 a+=pp([[130,15],[152,10],[171,10],[171,19],[191,19],[191,27],[222,27],[222,36],[185,36],[185,30],[156,30],[156,25],[130,25]],'#c59cb5',.83);
 a+=pp([[10,19],[29,13],[51,13],[51,18],[73,18],[73,24],[100,24],[100,28],[52,28],[52,23],[10,23]],'#ffe9cb',.62);
 // Tiny clustered brushstrokes inside the cloud, not independent sparkles.
 for(let j=0;j<95;j++){
  const x=-11+hash(k*171+j*7.3)*229,y=-27+hash(j*3.17+k*103)*99;
  const n=hash(j*2.71+k*127),coolPocket=y>23;
  const col=coolPocket?(n>.57?'#7284a1':'#b293b0'):(n>.63?gold:n>.31?warm:mid);
  a+=rr(x,y,2+Math.round(n*7),n>.86?2:1,col,coolPocket?.18+.20*n:.17+.20*n);
 }
 for(let j=0;j<14;j++){
  const x=7+j*15+(k%2)*5,y=25+(j%4)*4;
  a+=rr(x,y,6+(j%3)*7,1,j%3===0?'#f9d9bc':'#d69fb7',.31);
 }
 a+='</g>';
 // Selected crisp sunlit edges read as layered, hand-inked cut-outs.
 a+=rr(21,10,28,2,gold,.47+energy*.07);
 a+=rr(92,18,33,1,gold,.31+energy*.06);
 return '<g transform="translate('+Math.round(c.x+offset*c.v)+' '+c.y+') scale('+c.s+')">'+a+'</g>';
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
 for(let j=0;j<146;j++){
  const z=(j+.5)/146, y=start+4+z*(end-start-7);
  const amp=1+z*3.7,wide=4+z*32;
  for(let i=0;i<7;i++){
   const bx=frac(hash(j*17+i*31)*.4+i/5+.08)*410-25;
   const x=bx+Math.sin(phase*.3+j*.43+i*1.7)*amp;
   const yy=y+Math.sin(phase*.53+j*.36+i*2.4)*(.30+z*1.7);
   const shade=(i+j)%7===0?'#9ebbac':(i+j)%3===0?'#64a4a5':(i+j)%3===1?'#2a7283':'#387f89';
   out+=rr(x,yy,wide*(.26+.73*hash(j*7+i)),z>.77&&i%3===0?2:1,shade,.53+.32*(1-z));
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
 for(let i=0;i<425;i++){
  const z=(i+.5)/425,y=top+7+z*(depth-9);
  const span=5+Math.pow(z,1.35)*98;
  const centre=sunX+Math.sin(phase*.22+z*8)*1.4;
  const stripes=1+(i%4===0?1:0);
  for(let s=0;s<stripes;s++){
   const seed=i*17+s*31,dist=(hash(seed+38)*2-1),edge=Math.abs(dist);
   const x=centre+dist*span+Math.sin(phase*.42+z*11+s*2+i*.8)*(1+z*2);
   const len=(2+z*17)*(1-edge*.59)*(0.58+hash(seed+5)*.65);
   const bright=edge<.35?'#fff0bf':edge<.68?'#ffdaa8':'#dba695';
   const opacity=(.32+.53*(1-edge))*(.85+Math.sin(phase*.3+i*.37)*.06)*light;
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
