/**
 * Sunset Harbor V4 — original hand-composed 360x640 pixel scenery.
 * Agent 1 owns only the WORLD. No water, clouds, people or narrative FX live here.
 * Six raw SVG fragment planes, deliberately independent for Agents 2 and 3.
 * All positions/clusters are pixel snapped and entirely frame deterministic.
 */
export const HARBOR_V4_WIDTH = 360;
export const HARBOR_V4_HEIGHT = 640;
const snap=n=>Math.round(n);
const R=(x,y,w,h,c)=>w>0&&h>0?'<rect x="'+snap(x)+'" y="'+snap(y)+'" width="'+Math.max(1,snap(w))+'" height="'+Math.max(1,snap(h))+'" fill="'+c+'"/>':'';
const P=(a,c)=>'<polygon points="'+a.map(q=>snap(q[0])+','+snap(q[1])).join(' ')+'" fill="'+c+'"/>';
const L=(x,y,w,h,c)=>R(x,y,w,h,c);
const G=(x,y,s,body)=>'<g transform="translate('+snap(x)+' '+snap(y)+') scale('+s+')">'+body+'</g>';
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const numb=(v,def=0)=>Number.isFinite(v)?v:def;
const hash=n=>{let t=Math.imul((n|0)^0x9e3779b9,0x85ebca6b);t^=t>>>13;t=Math.imul(t,0xc2b2ae35);return((t^t>>>16)>>>0)/4294967296};
const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
const col=(a,b,t)=>{let x=rgb(a),y=rgb(b);return '#'+x.map((v,i)=>snap(v+(y[i]-v)*clamp(t)).toString(16).padStart(2,'0')).join('')};
const blade=(x,y,c)=>P([[x,y],[x+1,y-7],[x+3,y-11],[x+4,y-3],[x+7,y-8],[x+7,y],[x+5,y+3],[x+1,y+3]],c);

// SKY deliberately cloud-free: Agent 2 is the cloud/water/atmosphere owner.
function sky(frame,m){
 const stops=[[0,'#153d5e'],[44,'#2c5877'],[95,'#5e7894'],[150,'#a08ba8'],[213,'#daa1ae'],[261,'#f6b29f'],[310,'#ffcfaa'],[354,'#ffdeb0']];
 let o='';
 for(let y=0;y<354;y+=2){
  let j=0;while(j<stops.length-2&&y>stops[j+1][0])j++;
  let a=stops[j],b=stops[j+1];o+=R(0,y,360,2,col(a[1],b[1],(y-a[0])/(b[0]-a[0])));
 }
 // Broad pixel-stepped crepuscular glow, not a blurry overlay.
 for(let j=6;j>=0;j--){
  const w=45+j*12,cy=245,xx=225;
  o+=P([[xx-w,cy+12+j*6],[xx-w+20,cy-9-j*3],[xx+w-20,cy-9-j*3],[xx+w,cy+12+j*6]],['#ffd4aa','#f9c4a9','#f6bea8','#f3baa9','#f0b5a7','#edb1aa','#e6abad'][j]);
 }
 // Faceted gold sun and fine tiered rim; silhouettes remain deliberately open.
 for(let radius=29;radius>17;radius-=4){
  let pts=[];
  for(let y=-radius;y<=radius;y+=2){const w=Math.sqrt(radius*radius-y*y);o+=R(225-w,252+y,2*w,2,radius>25?'#ffd9ad':radius>21?'#ffe1b6':'#ffe9bc');}
 }
 for(let y=-16;y<=16;y+=2){let w=Math.sqrt(256-y*y);o+=R(225-w,252+y,2*w,2,'#fff1c7');}
 o+=R(205,250,38,2,'#fff6d4')+R(210,245,29,1,'#fff4d3');
 // Luminous horizon ribbons leave ample room for independently drawn clouds.
 o+=P([[0,232],[57,230],[101,232],[152,230],[206,234],[253,228],[318,230],[360,225],[360,229],[308,234],[263,233],[219,237],[157,234],[104,237],[56,234],[0,235]],'#e9b0af');
 o+=R(152,315,128,1,'#ffe2bc')+R(168,318,86,1,'#ffd7aa');
 return o;
}
function mountain(pts,base,face,light,seed){
 let o=P([...pts,[360,base],[0,base]],face);
 for(let i=1;i<pts.length-1;i++){
  const q=pts[i],prev=pts[i-1];
  if(q[1]<prev[1]-7){
   o+=P([[q[0],q[1]],[q[0]+6,q[1]+8],[q[0]+4,q[1]+19],[q[0]+12,q[1]+25]],light);
   o+=R(q[0]-2,q[1]+7,3,11,light);
  }
 }
 for(let i=0;i<16;i++){
  let x=hash(i+seed)*350,y=base-24+hash(i+seed+81)*16;
  o+=R(x,y,3+hash(i+seed+5)*11,1,i%3?'#7794a4':light);
 }
 return o;
}
function distant(frame,m){
 let out='';
 // Four distinct ridge contours, scaled in perspective to a sheltered natural bay.
 out+=mountain([[0,315],[17,300],[34,303],[55,282],[65,285],[80,263],[94,271],[119,245],[133,253],[156,239],[171,258],[188,251],[203,265],[225,269],[241,261],[263,281],[281,271],[299,288],[319,274],[337,290],[360,276]],359,'#8795ad','#c0aabb',100);
 out+=mountain([[0,338],[16,321],[35,329],[60,303],[78,311],[101,291],[121,307],[135,301],[151,317],[176,303],[191,317],[211,310],[230,326],[247,312],[265,324],[286,305],[306,314],[329,300],[345,315],[360,308]],373,'#648b9c','#a2b7b2',310);
 out+=P([[0,350],[17,342],[28,349],[44,336],[61,345],[81,333],[98,344],[120,329],[141,340],[153,346],[174,343],[192,353],[208,348],[226,350],[239,344],[258,350],[277,333],[293,337],[310,330],[334,337],[360,331],[360,383],[0,383]],'#3f7684');
 out+=P([[0,362],[20,348],[30,355],[50,347],[66,355],[81,342],[96,352],[111,348],[125,359],[148,352],[166,363],[192,355],[215,360],[230,359],[254,354],[276,351],[299,345],[320,349],[339,342],[360,347],[360,383],[0,383]],'#3e6a78');
 // Naturally clustered deep evergreens, gentle contour rather than repetitive teeth.
 for(let i=0;i<52;i++){
  let x=i*7.4-7+hash(i+60)*3,y=359+Math.sin(i*.53)*4,w=4+hash(i+88)*5,h=5+hash(i+144)*9;
  let edge=(x<143||x>257);
  if(edge)out+=P([[x-w/2,y],[x,y-h],[x+w/2,y],[x+w/3,y],[x+w/1.7,y+3],[x-w/2,y+3]],i%3===0?'#315a70':'#3d6577');
 }
 // Distant terrace hamlet, nearly dissolved into mountain haze.
 for(let i=0;i<18;i++){
  let x=i<10?113+i*5.4:253+(i-10)*6.4,y=350+hash(i+172)*5;
  out+=R(x,y-8,4+hash(i+11)*3,9,'#7093a0')+
   P([[x-2,y-8],[x+3,y-13],[x+8,y-8]],'#6d788f')+R(x+2,y-5,2,3,'#d5b8b1');
 }
 // Close shore banks frame the open centre — not placed on top of the sun.
 out+=P([[0,360],[29,355],[58,350],[86,359],[112,356],[131,364],[144,373],[147,387],[0,390]],'#365e70');
 out+=P([[262,372],[282,358],[305,358],[319,345],[338,349],[360,341],[360,395],[258,388]],'#365e70');
 return '<g transform="translate('+snap(-numb(m.cameraX)*.18)+' '+snap(-numb(m.cameraY)*.16)+')">'+out+'</g>';
}
function roof(spec){
 const {w,style,roof:c}=spec;let o='';
 if(style==='tower'){
  o+=P([[-5,0],[w/2,-20],[w+5,0]],'#293f5c')+P([[-1,-2],[w/2,-17],[w+1,-2]],c);
  o+=R(w/2-3,-26,6,9,'#d2ac9d')+R(w/2-5,-27,10,2,'#fff0c6');
 } else if(style==='hip'){
  o+=P([[-7,0],[3,-12],[w-7,-15],[w+8,1]],'#324860');
  o+=P([[-4,-2],[7,-11],[w-7,-13],[w+5,-1]],c);
  o+=R(-5,1,w+12,3,'#f1c19e');
 } else if(style==='shed'){
  o+=P([[-7,-4],[w+4,-13],[w+9,2],[-7,4]],'#344459');
  o+=P([[-4,-2],[w+4,-10],[w+5,0]],c);
  o+=R(-7,2,w+16,3,'#d8a08c');
 } else {
  o+=P([[-8,3],[w/2,-19],[w+9,3]],'#304058');
  o+=P([[-4,1],[w/2,-16],[w+4,1]],c);
  o+=P([[w/2,-16],[w+4,1],[w/2+3,1]],'#775e78');
  o+=R(-7,2,w+14,3,'#f7c7a0');
 }
 for(let i=0;i<w;i+=7){
  let y=style==='gable'? -3-Math.round((w/2-Math.abs(i-w/2))*.29) : style==='shed'? -4-Math.round(i/w*8) : -5-(i%3===0?1:0);
  if(style!=='tower')o+=R(i,y,4,1,i%3===0?'#ffc5a0':'#866077');
 }
 if(spec.chimney){
  o+=R(w-13,-25,7,18,'#596377')+R(w-15,-27,11,3,'#e6ae9a')+R(w-11,-23,3,9,'#ac7f84');
 }
 return o;
}
function window(x,y,w,h,seed,palette){
 let o='';
 const lit=seed%5!==1;
 o+=R(x-2,y-2,w+4,h+5,palette.trim);
 o+=R(x,y,w,h,lit?'#ffe5b3':'#416c7c');
 o+=R(x+1,y+1,w-2,2,lit?'#fff1d0':'#668fa1');
 o+=R(x+w/2,y,1,h,lit?'#c89c8b':'#213f57');
 o+=R(x,y+h/2,w,1,lit?'#d6a48f':'#426579');
 o+=R(x-3,y+h+2,w+6,2,'#dfaa92');
 if(seed%3===0)o+=R(x-4,y-2,2,h+4,'#496479')+R(x+w+2,y-2,2,h+4,'#496479');
 if(lit)o+=R(x+2,y+h-3,2,2,'#fff3c6');
 return o;
}
function balcony(x,y,w){
 let o=R(x-3,y,w+6,4,'#e4b69d')+R(x-5,y+4,w+10,3,'#47566a');
 o+=R(x-5,y+6,w+10,2,'#9d7f81');
 for(let i=0;i<w+10;i+=5)o+=R(x-3+i,y-6,2,13,i%2===0?'#354a61':'#5f6270');
 o+=R(x-5,y-7,w+10,2,'#d2a59b');
 return o;
}
function flowers(x,y,s,seed){
 let o=R(x,y+4,18*s,4*s,'#8f6476')+R(x+2*s,y+3,14*s,2*s,'#e1a28f');
 for(let i=0;i<6;i++){
  let px=x+i*s*3,py=y-s*(2+(i%3)*2);
  o+=R(px,py,2*s,5*s,i%2?'#4d8c7e':'#66a084');
  o+=R(px-1*s,py-1*s,4*s,2*s,i%3?'#ee9e9b':'#ffdab0');
 }
 return o;
}
function building(spec){
 const {x,top,w,h,wall,side,trim,roof:roofColour,style,seed}=spec;
 let o='',body='';
 // Sculpted masonry, beveled silhouette, shaded side and subtly irregular stucco.
 body+=P([[0,3],[2,1],[w-3,1],[w,4],[w,h],[0,h]],'#284459');
 body+=P([[1,5],[w-8,4],[w-9,h-2],[1,h-2]],wall);
 body+=P([[w-9,4],[w-1,4],[w-1,h],[w-9,h-2]],side);
 body+=R(2,10,2,h-14,trim)+R(5,h-7,w-9,2,'#b2878b');
 body+=R(0,7,w,2,'#ebc0a2')+R(1,h-5,w-1,3,'#42586b');
 // Purposeful plaster blocks and timber pegs, not procedural random noise.
 for(let i=0;i<17;i++){
  let px=4+hash(seed*5+i)*Math.max(1,w-15),py=12+hash(seed*8+i+50)*Math.max(2,h-23);
  if(i%3!==1)body+=R(px,py,2+i%3,1,i%2?trim:'#d3aaa0');
 }
 const rows=h>98?3:h>74?2:1;
 const cols=w>=42?2:1;
 for(let row=0;row<rows;row++)for(let c=0;c<cols;c++){
  let wx=cols===1?Math.round(w/2-4):8+c*(w-20);
  let wy=15+row*24+(style==='tower'?6:0);
  if(wy+15>h-10)continue;
  body+=window(wx,wy,8,10,seed+row*2+c,{trim:'#624f65'});
 }
 if(style==='tower'){
  body+=R(w/2-7,7,14,2,'#d8ab9f');
  body+=P([[w/2-5,11],[w/2,5],[w/2+5,11],[w/2+5,22],[w/2-5,22]],'#384b61');
  body+=R(w/2-2,13,4,7,'#ffe6ac')+R(w/2-8,27,16,3,'#ffccae');
 } else if(h>=87&&w>30){
  body+=balcony(6,h-36,w-15);
  body+=flowers(8,h-40,1,seed);
 }
 // Doors made of arched recesses, with asymmetric steps and shadows.
 const dx=style==='tower'?Math.round(w/2-5):seed%2?7:w-20;
 body+=P([[dx-2,h-4],[dx-2,h-20],[dx+1,h-24],[dx+10,h-24],[dx+13,h-20],[dx+13,h-4]],'#31475b');
 body+=R(dx,h-20,10,16,seed%2?'#6a586d':'#755a68');
 body+=R(dx+2,h-17,2,9,'#9c7a78')+R(dx+7,h-12,1,2,'#ffe5b2');
 body+=R(dx-3,h-5,17,2,'#f1c6a7');
 // Street-facing unique shopfronts / curved awnings.
 if(seed%3===0&&w>33){
  body+=R(3,h-29,w-6,5,'#f7cfaa');
  for(let i=0;i<w-8;i+=6)body+=R(4+i,h-26,4,7,i%2?'#df8f8c':'#fff0c3');
  body+=R(5,h-18,w-10,13,'#365a69')+R(8,h-16,w-17,6,'#b58b8e');
  body+=R(6,h-4,w-12,2,'#e7b094');
 }
 if(seed%4===1){
  body+=R(w-7,h-54,2,49,'#477b72');
  for(let i=0;i<8;i++)body+=R(w-12-(i%3)*3,h-17-i*5,8,3,i%2?'#5c937d':'#8eae89');
  body+=R(w-9,h-33,3,2,'#edaf99');
 }
 // A further tier of handmade 1px cornices and stone arch shadows.
 body+=R(1,12,w-4,1,'#cda69c')+R(2,h-9,w-5,1,'#efc49e');
 if(seed%2===0){body+=R(1,h-35,4,22,'#6b7788')+R(w-7,h-35,3,22,'#c79e98');}
 // Put roof last so ridgelines and tiles cover the top of the masonry.
 o+=G(x,top,1,body+roof({w,roof:roofColour,style,chimney:seed%3===1}));
 return o;
}
function architecture(frame,m){
 let o='';
 // Warm back alley tiers and roofs, hand-drawn behind the main houses.
 o+=P([[0,357],[7,335],[26,331],[46,344],[61,331],[76,341],[104,337],[135,355],[149,375],[0,391]],'#536979');
 o+=P([[267,374],[279,349],[297,342],[323,333],[350,329],[360,339],[360,406],[265,398]],'#4b6577');
 // Individually spaced houses with distinct elevations, edge directions, roof profiles.
 const structures=[
  {x:-18,top:322,w:42,h:72,wall:'#aa9a9c',side:'#637887',trim:'#e1b4a4',roof:'#956a7f',style:'hip',seed:1},
  {x:14,top:298,w:46,h:100,wall:'#d5aa9d',side:'#8c8290',trim:'#f7d7b8',roof:'#b57079',style:'gable',seed:3},
  {x:60,top:264,w:29,h:136,wall:'#d7b5a5',side:'#7c8292',trim:'#f8d6b7',roof:'#62647e',style:'tower',seed:9},
  {x:84,top:289,w:43,h:110,wall:'#d69b91',side:'#8b7684',trim:'#ffd1ab',roof:'#93637b',style:'hip',seed:4},
  {x:123,top:327,w:30,h:70,wall:'#a7a2a0',side:'#66838c',trim:'#edb6a5',roof:'#6c6d83',style:'shed',seed:6},
  {x:267,top:328,w:32,h:72,wall:'#b5a19c',side:'#718991',trim:'#f0c6ae',roof:'#a56e79',style:'shed',seed:7},
  {x:292,top:303,w:40,h:100,wall:'#ddb0a0',side:'#847786',trim:'#ffdcad',roof:'#ac7182',style:'gable',seed:5},
  {x:326,top:273,w:39,h:133,wall:'#b0a1af',side:'#61798d',trim:'#edc5b8',roof:'#64738c',style:'hip',seed:8}
 ];
 for(const b of structures)o+=building(b);
 o+=portArchitecturalDetails(frame);
 // Signature right-facing harbour café terrace, layered curved awning and balcony.
 o+=P([[98,382],[150,382],[146,394],[95,394]],'#344d61');
 o+=R(99,368,50,3,'#e9b9a1');
 for(let i=0;i<8;i++)o+=R(99+i*6,371,4,8,i%2?'#e79f92':'#fbd5b1');
 o+=R(103,379,40,13,'#355364')+R(108,381,29,5,'#eeb8a0');
 o+=R(101,390,45,2,'#d1a08e');
 // Right ochre harbour inn sign, designed in 1px marks rather than font glyphs.
 o+=R(311,367,20,13,'#394d60')+R(314,370,14,7,'#d5a58e')+R(316,371,1,5,'#fff0c1')+R(320,371,1,5,'#fff0c1')+R(324,371,1,5,'#fff0c1');
 // Ornamental roof accents and finials.
 o+=R(71,233,2,17,'#e5c8a8')+R(68,236,8,3,'#ffdea9')+R(71,230,2,3,'#34485f');
 o+=P([[308,290],[314,284],[320,290]],'#f2c6ad')+R(313,280,2,7,'#546378');
 // Golden illuminated archways at waterfront, strengthening reflected-light source positions.
 for(let x of [3,39,92,315,349]){
  o+=P([[x,392],[x,381],[x+3,377],[x+11,377],[x+14,382],[x+14,395]],'#304b5d');
  o+=R(x+4,382,8,11,'#f1c298')+R(x+6,384,3,7,'#ffe3ad');
 }
 return '<g transform="translate('+snap(-numb(m.cameraX)*.4)+' '+snap(-numb(m.cameraY)*.28)+')">'+o+'</g>';
}
function seaSteps(x,y,w){
 let o='';
 o+=R(x,y,w,5,'#e1ae97')+R(x,y+5,w,7,'#586d77')+R(x,y+12,w,12,'#3e596b');
 for(let i=0;i<Math.ceil(w/14);i++){
  o+=R(x+2+i*14,y+8,10,1,'#8b8f88')+R(x+8+i*14,y+16,8,2,'#647981');
 }
 return o;
}
function boat(x,y,frame,s=1){
 let bob=Math.sin(frame*.082+x)*1.4,drift=Math.sin(frame*.016+x)*2.2;
 let o='';
 o+=P([[0,8],[43,7],[36,17],[7,17]],'#283f55')+
  P([[2,8],[41,7],[35,13],[9,14]],'#975e6c')+
  R(7,5,29,3,'#f6c59d')+R(15,0,16,7,'#e5af93')+R(18,2,10,3,'#4c7481');
 o+=R(24,-29,2,29,'#3a5165');
 o+=P([[25,-26],[25,3],[39,3]],'#f9d5b1')+P([[22,-21],[20,1],[7,1]],'#d8a9a4');
 o+=R(9,16,27,2,'#638d90')+R(13,19,19,1,'#9eb4ac');
 return G(x+drift,y+bob,s,o);
}
function harbour(frame,m){
 let o='';
 // Hand-set stone seawalls create proper depth and perspective.
 o+=P([[0,394],[146,390],[156,407],[118,423],[0,417]],'#304959');
 o+=P([[0,393],[144,391],[146,396],[0,400]],'#efbc9e');
 o+=seaSteps(0,398,130);
 o+=P([[278,394],[360,382],[360,428],[304,418]],'#2c4c5c');
 o+=P([[280,394],[360,382],[360,390],[283,400]],'#f2bc9f');
 o+=seaSteps(306,393,54);
 // Wooden moorings, measured plank directions and deep pier supports.
 o+=P([[0,432],[86,428],[122,451],[33,464]],'#31485a');
 o+=P([[0,427],[86,423],[122,446],[33,459]],'#a27e7c');
 for(let i=0;i<11;i++){
  let x=i*11-5,y=427+i*.25;
  o+=R(x,y,8,2,i%2?'#d19d86':'#b4887f');
 }
 for(let i=0;i<6;i++){
  let x=8+i*18,y=446+i*.5;
  o+=R(x,y,5,34,'#31475b')+R(x+1,y+3,1,12,'#806b6c');
 }
 o+=P([[326,412],[360,406],[360,425],[330,436],[309,424]],'#b08b80');
 for(let x of [318,339,356])o+=R(x,424,4,28,'#30485b')+R(x+1,425,1,7,'#ba9385');
 // Coiled mooring lines and brass rings.
 for(let [x,y] of [[18,417],[63,418],[103,418],[326,404],[350,396]]){
  o+=R(x,y-10,4,16,'#29495b')+R(x-1,y-12,6,3,'#ffe0a8');
  o+=R(x+5,y-3,8,1,'#d9b39a')+R(x+10,y-2,2,3,'#d9b39a');
 }
 // Hanging nets / lobster cages / barrels, readable at native resolution.
 for(let [x,y] of [[19,443],[49,452],[78,449]]){
  o+=R(x,y,12,8,'#7e6b6d')+R(x+2,y+1,8,5,'#c28f7e');
  for(let k=0;k<4;k++)o+=R(x+k*3,y,1,8,'#394f60');
 }
 o+=R(118,408,7,13,'#b07d74')+R(119,409,5,2,'#e3ac8d');
 o+=R(129,407,9,15,'#9d7776')+R(129,409,9,2,'#e7b6a0');
 // Leave the open central passage clear for Agent 3's moving sailboat; the\n // earlier moored skiff overlapped the hero vessel near the ending.
 // Separate stationary shore skiff and delicate rigging near the far right.
 o+=boat(300,452,frame,.58);
 o+=R(133,407,2,31,'#495b67')+R(137,409,2,29,'#495b67');
 o+=P([[132,407],[135,415],[137,408]],'#ebc4ac');
 return '<g transform="translate('+snap(-numb(m.cameraX)*.7)+' '+snap(-numb(m.cameraY)*.48)+')">'+o+'</g>';
}
function paving(){
 let o='';
 // Bevelled quay stone: staggered courses recede toward the sea.
 o+=P([[0,515],[360,529],[360,640],[0,640]],'#374b5d');
 o+=P([[0,515],[360,529],[360,540],[0,528]],'#c6a79b');
 o+=P([[0,527],[360,540],[360,545],[0,532]],'#7c8790');
 o+=P([[0,535],[360,547],[360,640],[0,640]],'#4a6070');
 for(let j=0;j<10;j++){
  let y=548+j*(8+j*.67);
  o+=R(0,y,360,1,j%2?'#839095':'#788b8f');
  const step=29+j*2;
  for(let i=-1;i<14;i++){
   let x=i*step+(j%2)*step*.5;
   o+=R(x,y+1,1,8+j*.69,'#304a5c');
   if((i+j)%3===0)o+=R(x+8,y+4,7,1,'#9b9896');
   if((i+j)%5===0)o+=R(x+15,y+7,3,1,'#6c9291');
  }
 }
 // Golden edge of cobbles catches sunset.
 o+=R(0,548,360,2,'#b89b94');
 return o;
}
function promenade(frame,m){
 let o=paving();
 // Pier balustrade doubles as a framing device, spaced and warm on its lit edge.
 o+=P([[0,501],[360,514],[360,518],[0,506]],'#bda18f');
 o+=P([[0,511],[360,524],[360,528],[0,515]],'#2c495d');
 for(let i=0;i<16;i++){
  let x=i*25-3,y=497+x*.039;
  o+=R(x,y,3,27,'#354f60')+R(x+1,y+4,1,17,'#ac9086');
  o+=R(x-2,y-4,8,4,'#e1ba9b')+R(x-1,y-6,6,2,'#495d6c');
 }
 // Wood-slat bench deliberately facing ocean, sized for Agent 3 characters.
 o+=R(89,544,77,5,'#b8877a')+R(92,537,72,4,'#dcaa8f');
 o+=R(93,551,71,5,'#946c70');
 for(let i=0;i<9;i++)o+=R(95+i*8,539,2,16,'#efc49d');
 o+=R(94,555,6,20,'#31495c')+R(158,555,6,20,'#31495c');
 o+=R(92,573,75,3,'#2d4256');
 // Café sidewalk furniture: two tiny cups, cupola parasol and laid table.
 o+=R(281,563,35,3,'#d3a18b')+R(298,566,3,25,'#344c5d');
 o+=R(280,590,37,3,'#31485a')+R(287,558,5,5,'#f6d8ad')+R(305,558,5,5,'#ffe2b9');
 o+=R(292,553,2,6,'#5f747d')+R(277,563,1,10,'#495a69');
 o+=R(285,575,2,23,'#3e5566')+R(307,575,2,23,'#3e5566');
 o+=P([[260,561],[292,541],[326,559]],'#a36e7d')+
   P([[266,558],[292,545],[317,558]],'#e8a596');
 o+=R(291,559,3,8,'#725f6e');
 // Right-side shallow stone staircase with visibly varied tread widths.
 for(let i=0;i<5;i++)o+=R(334-i*4,536+i*6,36+i*4,3,'#a99b97');
 return '<g transform="translate('+snap(-numb(m.cameraX)*.93)+' '+snap(-numb(m.cameraY)*.82)+')">'+o+'</g>';
}
function lantern(x,y,size){
 let o='';
 o+=R(-2,0,4,99,'#263f55')+R(-1,6,1,78,'#a18c83');
 o+=P([[-8,-5],[0,-16],[9,-5]],'#2c4359');
 o+=R(-7,-5,15,3,'#b38b81')+R(-6,-2,13,15,'#385166');
 o+=R(-4,0,9,10,'#ffe6ae')+R(-3,1,7,4,'#fff3ce');
 o+=R(-7,11,16,3,'#b48d80')+R(-4,14,10,2,'#344a5d');
 o+=R(-8,94,16,4,'#31475b')+R(-3,97,7,1,'#d4b09b');
 return G(x,y,size,o);
}
function leafCluster(x,y,s,seed,frame){
 let sway=Math.sin(frame*.035+seed)*2.0;
 let o='';
 o+=R(-1,0,3,25,'#3b6667')+R(0,-15,2,15,'#587873');
 for(let j=0;j<13;j++){
  let theta=j*2.399,dist=3+Math.sqrt(j)*3;
  let lx=Math.cos(theta)*dist+sway*(.1+j/20),ly=-11+Math.sin(theta)*dist*.55;
  o+=R(lx-3,ly,6+(j%3),3+(j%2),['#356e6b','#508b79','#75a088','#a1b392'][j%4]);
  if(j%4===0)o+=R(lx,ly-2,3,2,j%2?'#ffd3a7':'#ef9aa6');
 }
 return G(x,y,s,o);
}
function foreground(frame,m){
 let o='';
 // Painted wrought iron lamppost silhouettes live in front of moving characters.
 o+=lantern(27,448,1.02);
 o+=lantern(337,476,.78);
 // Climbing foliage on the border, drawn from local clusters (not screen-wide noise).
 for(let i=0;i<4;i++)o+=leafCluster(-8+i*8,590+i*11,1.18,i+2,frame);
 for(let i=0;i<6;i++)o+=leafCluster(355-i*6,588+i*8,1.08,i+20,frame);
 // Detailed planted urns at two depths; foreground corners stay non-symmetrical.
 for(let [x,y,s,seed] of [[-11,568,1.5,2],[328,571,1.45,5],[18,621,.88,8],[286,634,.8,10]]){
  let q=P([[1,16],[35,16],[31,44],[8,44]],'#8a6973');
  q+=R(0,14,37,5,'#d39a83')+R(4,21,30,2,'#e1af91')+R(7,40,25,3,'#5a6671');
  for(let k=0;k<12;k++){
   const xx=5+(k%6)*5,yy=13-8-(k%4)*6;
   q+=R(xx,yy,2,18-yy,'#3f7c6d')+R(xx-3,yy,7,4,k%3===0?'#89ad8b':'#578f7a');
   if(k%3===0)q+=R(xx-1,yy-3,4,3,k%2?'#f5c49b':'#ee91aa');
  }
  o+=G(x,y,s,q);
 }
 // Small flower beds along the pavement create an ornate but readable border.
 for(let i=0;i<15;i++){
  const x=i*26-4,y=625+(i%3)*4;
  if(x>100&&x<247)continue;
  const sway=Math.round(Math.sin(frame*.04+i*2)*1.5);
  o+=blade(x,y,'#43836f')+R(x+sway,y-11,4,4,i%3===0?'#f7d39e':'#d38ca3');
  o+=R(x+5+sway,y-8,3,3,'#eeaea8');
 }
 // Left upper hanging wisteria framing against the sky.
 o+=P([[0,0],[31,0],[35,9],[17,22],[4,29],[0,31]],'#2b586b');
 for(let i=0;i<11;i++){
  let x=1+i*3,y=7+i%3*6;
  o+=R(x,y,3,13+(i%4)*3,'#356d70');
  o+=R(x,y+11,4,5,i%2?'#866f98':'#bd92b0');
  if(i%3===0)o+=R(x+1,y+18,3,4,'#e1adbd');
 }
 // Anchor and ropes at the edge of the foreground without occluding harbour.
 o+=R(247,620,4,12,'#7b8387')+R(241,622,16,3,'#b4a3a0')+
   P([[243,634],[240,626],[245,632],[252,632],[256,626],[254,636],[249,640],[246,640]],'#334b5d');
 return '<g transform="translate('+snap(-numb(m.cameraX)*1.17)+' '+snap(-numb(m.cameraY)*1.02)+')">'+o+'</g>';
}

/**
 * Returns raw fragments WITHOUT per-layer SVG wrappers. Composition order:
 * sky -> (Agent 2 clouds) -> distant -> (Agent 2 water) ->
 * architecture -> harbourStructures -> (Agent 3 life) ->
 * promenade -> foreground.
 *
 * motion: optional cameraX / cameraY / foliageSway, future compatible keys.
 * Agent 2 may replace atmospheric layers without modifying architecture.
 */

/**
 * Individually painted identity details placed over the house geometry,
 * never generated as uniform repeated blocks.
 */
function portArchitecturalDetails(frame){
 let o='';
 // Bell tower octagonal copper lantern room, luminous clock and carved pillars.
 o+=P([[60,266],[64,259],[69,255],[80,255],[87,262],[89,268]],'#3c4d63');
 o+=P([[65,261],[71,257],[79,257],[84,263]],'#d8a69f');
 o+=R(63,267,24,4,'#ffe0ab')+R(64,272,3,11,'#b48086')+R(84,272,3,11,'#9e7784');
 o+=P([[70,279],[78,279],[82,283],[82,291],[78,295],[70,295],[66,291],[66,283]],'#46566c');
 o+=P([[71,282],[77,282],[79,284],[79,291],[77,293],[71,293],[69,291],[69,284]],'#ffe0af');
 o+=R(74,283,1,6,'#46556b')+R(74,288,4,1,'#46556b');
 o+=R(64,297,23,2,'#ffe3b6');
 // Roof dormers, stone cornices, tiny chimney caps and asymmetrical shutters.
 for(const [x,y,c] of [[29,291,'#8b657e'],[98,279,'#b36e7c'],[312,294,'#8e6883'],[339,263,'#66718d']]){
  o+=P([[x-5,y+5],[x+5,y-5],[x+15,y+5]],'#334761');
  o+=P([[x-2,y+3],[x+5,y-3],[x+12,y+3]],c);
  o+=R(x+2,y+5,7,7,'#415a6d')+R(x+3,y+6,5,4,'#ffe1ae');
  o+=R(x-4,y+13,20,2,'#e8b39b');
 }
 // Decorated timber balcony steps, flower cascade and warm café lantern strings.
 for(const [x,y,w] of [[10,352,48],[92,342,34],[304,351,30]]){
  o+=R(x,y,w,2,'#f2c29f')+R(x,y+5,w,2,'#42576b');
  for(let i=0;i<w;i+=5)o+=R(x+i,y-7,2,13,'#4b5669');
  for(let i=0;i<w;i+=9){
   o+=R(x+i,y-10,3,5,'#5a947d')+
      R(x+i-1,y-12,5,3,i%2?'#e9a4aa':'#f8d9a5');
  }
 }
 // Hanging laundry deliberately on the left alley, coloured textiles catching warm light.
 o+=R(0,336,55,1,'#c9a49d');
 for(const [x,c,len] of [[5,'#f8c9a4',12],[19,'#8ea7a5',11],[32,'#de9ca6',17],[47,'#b0b3ac',10]]){
  o+=R(x,335,1,4,'#e4bea5')+R(x,339,9,len,c)+R(x+2,341,5,2,'#ffe0bc');
 }
 // Carved arch-and-window shadows on the quay wall, each with its own trim.
 for(let i=0;i<5;i++){
  const x=i<3?6+i*28:307+(i-3)*27,y=394;
  o+=P([[x,y+1],[x,y-9],[x+3,y-13],[x+11,y-13],[x+14,y-9],[x+14,y+2]],'#344b5e');
  o+=P([[x+2,y+1],[x+2,y-8],[x+5,y-11],[x+9,y-11],[x+12,y-8],[x+12,y+1]],'#dfab96');
  o+=R(x+5,y-5,5,7,'#fff0bb')+R(x-2,y+3,17,2,'#e4baa0');
 }
 // Cafe sign and wooden striped fabric canopy cast a stepped shadow.
 o+=R(97,363,50,5,'#344c61');
 for(let i=0;i<8;i++)o+=R(98+i*6,368,4,9,i%2?'#e27f84':'#ffe2ae');
 o+=R(104,360,29,5,'#ffdbac')+R(108,361,3,3,'#5a6574')+
    R(116,361,3,3,'#5a6574')+R(124,361,3,3,'#5a6574');
 o+=R(142,356,2,12,'#445b67')+R(141,358,11,8,'#41596b')+
    R(143,360,8,3,'#f9c39d');
 // Delicate bridge stair to lower fishing dock with 3D steps and railing.
 for(let i=0;i<7;i++){
  let x=130+i*3,y=400+i*7;
  o+=R(x,y,26-i*2,4,'#ad8980')+R(x,y-2,24-i*2,2,'#e3b299');
 }
 o+=R(129,401,2,49,'#40586b')+R(153,431,2,21,'#40586b');
 // Hand-set ivy that blooms on the right wall; layered, not random speckles.
 for(let i=0;i<26;i++){
  let y=301+i*3.1,x=352-Math.sin(i*.63)*7-(i%5)*2;
  o+=R(x,y,4+(i%3),3,i%3?'#4c8a77':'#88aa89');
  if(i%7===0)o+=R(x+1,y-3,3,3,'#f3b6a1');
 }
 // Tiny coastal shutters add depth to the formerly plain end façades.
 for(let [x,y] of [[346,313],[346,339],[277,348],[31,323]]){
  o+=R(x,y,3,12,'#476274')+R(x+4,y,7,10,'#f8dfa9')+
      R(x+12,y,3,12,'#536478')+R(x+2,y+12,15,2,'#e5b49b');
 }
 return o;
}

export function renderHarborBaseLayers(frame, motion={}){
 const f=Math.max(0,Math.floor(numb(frame)));
 return {
  sky:sky(f,motion),
  distant:distant(f,motion),
  architecture:architecture(f,motion),
  harbourStructures:harbour(f,motion),
  promenade:promenade(f,motion),
  foreground:foreground(f,motion),
 };
}
