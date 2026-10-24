/**
 * Sunset Harbor V2 — all-original 360x640 vector pixel painting.
 * Individual visual elements are snapped to the native pixel grid.
 * No wall-clock timing, network assets, fonts or randomness at render time.
 */
const W=360,H=640;
const r=(x,y,w,h,c)=>`<rect x="${Math.round(x)}" y="${Math.round(y)}" width="${Math.max(1,Math.round(w))}" height="${Math.max(1,Math.round(h))}" fill="${c}"/>`;
const p=(pts,c)=>`<polygon points="${pts.map(([x,y])=>`${Math.round(x)},${Math.round(y)}`).join(' ')}" fill="${c}"/>`;
const t=(x,y,s,c,z=6)=>`<text x="${x}" y="${y}" fill="${c}" font-size="${z}" font-family="monospace" font-weight="bold">${s}</text>`;
const wave=(f,k,rate=.055)=>Math.sin(f*rate+k);
const rnd=n=>{let q=(n*1664525+1013904223)>>>0; q^=q>>>13;q=Math.imul(q,1274126177)>>>0;return (q>>>0)/4294967295};
const hex=(v)=>Math.round(Math.max(0,Math.min(255,v))).toString(16).padStart(2,'0');
const mix=(a,b,q)=>{const A=a.match(/[0-9a-f]{2}/gi).map(x=>parseInt(x,16)),B=b.match(/[0-9a-f]{2}/gi).map(x=>parseInt(x,16));return '#'+A.map((v,i)=>hex(v+(B[i]-v)*q)).join('')};
const skyStops=[[0,'#123e56'],[65,'#2c6679'],[118,'#657b97'],[170,'#aa8da9'],[233,'#da9cae'],[291,'#f0b4a1'],[355,'#f7c58e']];
function sky(f){let o='';for(let y=0;y<362;y+=3){let j=0;while(j<skyStops.length-2&&y>skyStops[j+1][0])j++;let a=skyStops[j],b=skyStops[j+1];let q=(y-a[0])/(b[0]-a[0]);o+=r(0,y,W,3,mix(a[1],b[1],q));}
// Tiny atmosphere highlights, staggered and deliberately sparse.
for(let i=0;i<170;i++){const x=Math.floor(rnd(i+190)*360),y=Math.floor(rnd(i+872)*293); if((i+Math.floor(f/24))%7!==0){o+=r(x,y,i%5===0?2:1,1,y>210?'#edb7ad':'#9babb5')}}return o}
function pixelDisc(cx,cy,rad,col,step=2){let o='';for(let yy=-rad;yy<=rad;yy+=step){let q=Math.sqrt(Math.max(0,rad*rad-yy*yy));o+=r(cx-q,cy+yy,2*q,step,col)}return o}
function cloud(x,y,s,frame,code){let o='';const ct=code%2===0;const body=ct?'#e4b1b9':'#c7a2b6',shade=ct?'#927b9e':'#7e779a',bright=ct?'#ffe2be':'#edc4bd';
o+=`<g transform="translate(${Math.round(x+frame*(code%2?.018:-.028))} ${Math.round(y)}) scale(${s})">`;
const k=[[0,17,120,14,shade],[17,8,98,21,body],[30,0,62,22,body],[50,-11,44,20,body],[82,3,47,22,body],[-9,24,146,8,shade],[26,31,118,6,'#a18aa8'],[4,14,18,8,shade],[47,1,37,5,bright],[84,6,32,4,bright],[31,29,78,3,'#f5bdaf'],[5,32,39,4,'#7c789c']];for(let i=0;i<k.length;i++){const z=k[i];o+=r(...z)}
for(let i=0;i<15;i++)o+=r(5+i*9,14+(i%3)*5,3,1,i%2?body:bright);
return o+'</g>'}
function mountains(){return p([[0,324],[23,314],[36,318],[50,305],[67,314],[87,292],[108,311],[136,287],[161,308],[184,291],[211,318],[237,299],[256,314],[278,305],[305,315],[329,301],[360,315],[360,367],[0,367]],'#8b8fa9')+p([[0,344],[27,327],[49,335],[65,326],[84,338],[108,313],[136,333],[156,315],[181,337],[199,322],[230,340],[250,325],[273,338],[292,324],[320,343],[338,331],[360,341],[360,379],[0,379]],'#5a8490')+p([[0,356],[24,348],[36,353],[51,345],[82,356],[108,338],[129,347],[149,344],[173,358],[215,343],[238,352],[263,343],[294,351],[327,337],[360,351],[360,380],[0,380]],'#477985')}
function water(frame){let o='';for(let y=354;y<529;y+=3){const q=(y-354)/175;o+=r(0,y,360,3,mix('#497e8b','#17485d',q));}
// long horizontal facets, sampled from deterministic salts
for(let i=0;i<620;i++){let depth=rnd(i+44),y=354+Math.floor(depth*174),x=(Math.floor(rnd(i+555)*430)+Math.round(frame*(0.13+depth*.42)*(i%2?1:-1))+430)%430-35;
const bright=(i%8===0)?'#77a9a1':(i%2?'#699b9c':'#346e7e');o+=r(x,y,2+Math.floor(depth*15)+i%9,(i%9===0?2:1),bright)}
// widening sunlit track; it flickers but does not wander randomly
for(let i=0;i<380;i++){const depth=rnd(i+221),y=360+depth*165,span=8+Math.pow(depth,1.48)*101;
const x=226+(rnd(i+919)-.5)*2*span+Math.sin(frame*.052+i*2.9)*(1+depth*4);
if(rnd(i+711)>.18){const a=rnd(i+450),col=a>.82?'#fff0bd':a>.50?'#fbd5a4':'#d99c90';o+=r(x,y,1+Math.floor(depth*17*rnd(i+77)),depth>.85?2:1,col)}}
// isolated large sparkling starbursts
for(let i=0;i<32;i++){let d=rnd(i+880),xx=225+(rnd(i+699)-.5)*(20+d*168),yy=372+d*149;
if(wave(frame,i,0.064)>.56){o+=r(xx-2,yy,5,1,'#ffe3aa')+r(xx,yy-2,1,5,'#ffe3aa')}}return o}
function tileRoof(x,y,w,seed){let o='';o+=p([[x-6,y+2],[x+8,y-14],[x+w-7,y-14],[x+w+7,y+2]],'#233f58');o+=p([[x-3,y],[x+10,y-11],[x+w-9,y-11],[x+w+4,y]],'#ad626c');o+=r(x-6,y+2,w+13,3,'#e7a28c');for(let i=0;i<w/7;i++){o+=r(x+Math.floor(i*7),y-6+(i%2),4,1,i%3?'#d98681':'#694d66')}if(seed%2===0)o+=r(x+w-15,y-23,7,14,'#536177')+r(x+w-17,y-25,11,3,'#d78b7f');return o}
function house(x,base,w,h,main,detail,seed){let o='',y=base-h;const shadow=mix(main,'#1d3a51',.25),light=seed%2?'#ffe3b0':'#ffd19d';
o+=r(x-2,y,w+4,h,'#213f58');o+=r(x,y,w,h,main)+r(x+w-9,y+2,9,h,shadow)+r(x+3,y+3,2,h-7,mix(main,'#f5d2a4',.28));
o+=tileRoof(x,y,w,seed);
for(let row=0;row<Math.floor((h-19)/21);row++)for(let col=0;col<Math.floor((w-10)/16);col++){let wx=x+9+col*16,wy=y+14+row*21,lit=(row*3+col+seed)%5!==0;
o+=r(wx-2,wy-3,12,14,detail)+r(wx,wy-1,8,10,lit?light:'#4b6c82')+r(wx+3,wy-1,1,10,'#8e8291')+r(wx,wy+4,8,1,lit?'#f8b68f':'#3e7180')+r(wx-3,wy+11,14,2,'#ddab93')+r(wx-4,wy+13,3,1,'#6b7684');}
// lively balconies and awnings, not uniform block towers
if(w>35){let by=base-31;o+=r(x+3,by,w-11,3,'#c48f8e');for(let i=0;i<w-12;i+=6)o+=r(x+5+i,by+3,2,8,'#314f63');o+=r(x+4,by+11,w-11,2,'#3a5968');}
if(seed%3===1){o+=r(x+8,base-22,w-18,6,'#ebc19d')+r(x+8,base-22,w-18,2,'#9d5767');for(let i=0;i<w-20;i+=7)o+=r(x+8+i,base-21,4,5,'#b65e6d');o+=r(x+10,base-15,w-23,14,'#40566a');}
// stonework at ground level
for(let k=0;k<w/9;k++)o+=r(x+Math.floor(k*9),base-4,6,1,'#b58a88');
// window glimmers / climbing creepers
if(seed%2===0)for(let k=0;k<9;k++)o+=r(x+w-6-(k%3)*3,base-12-k*6,2,3,k%2?'#5d8b78':'#7db08a');
return o}
function architecture(){let o='';// stacked onshore warm terraces; open golden centre
// backline skyline
const silhouettes=[[0,356,35,69,'#62848e','#42596d',0],[29,366,44,84,'#708a8d','#41576d',1],[71,368,35,60,'#9a8c8c','#5a6578',2],[101,380,49,115,'#ad887e','#596278',3],
[270,382,40,93,'#a77c88','#435d73',4],[307,392,51,124,'#77919a','#42647a',5],[348,395,50,92,'#8f8096','#566178',6]];
for(let i=0;i<silhouettes.length;i++)o+=house(...silhouettes[i]);
// signature bell tower at left, cupola and clock
let x=68,y=251;o+=r(x,y,22,48,'#dfafa0')+r(x+3,y+3,16,4,'#ffe0b7')+r(x+8,y+13,7,7,'#48697f')+p([[x-5,y+1],[x+11,y-15],[x+28,y+1]],'#4b526d')+r(x+9,y-21,4,12,'#e8be9f')+r(x+5,y+25,13,3,'#b47777');
// ground-level markets / nautical signs
for(let i=0;i<7;i++){let bx=6+i*13;o+=r(bx,378,11,3,i%2?'#e7aa90':'#fcceab')+r(bx+2,381,1,8,'#435569')}
o+=r(110,357,30,13,'#365565')+t(112,366,'CAFÉ','#fbd9ac',8);o+=r(311,353,27,12,'#345a6c')+t(314,362,'INN','#f4d3a9',7);
// Hanging lanterns and tiny chimney flecks
for(let j=0;j<8;j++){let xx=j<4?17+j*25:284+(j-4)*19,yy=j<4?376:385;o+=r(xx,yy,2,11,'#354a5b')+r(xx-2,yy+8,6,5,'#ffe1a4')+r(xx-4,yy+8,10,2,'#ce9d84')}
return o}
function docks(frame){let o='';
// terraced seawall, left fishing pier and distant right jetty
 o+=p([[0,380],[138,380],[138,403],[95,408],[0,415]],'#293f58')+r(0,384,136,5,'#b58d83');
for(let i=0;i<12;i++){let xx=i*13;o+=r(xx,392,9,3,'#64717b')+r(xx,399,8,2,'#40576a')}
for(let i=0;i<6;i++)o+=r(i*23+3,407,5,30,'#3a505c')+r(i*23+2,408,7,3,'#a98e7f');
o+=p([[295,394],[360,385],[360,417],[298,417]],'#334c61')+r(296,394,64,4,'#b69589');
for(let i=0;i<6;i++){let x=302+i*12;o+=r(x,395,3,28,'#30495a')+r(x,398,3,1,'#cbab8e')}
// low fishing skiff bobbing, reflected shadow and wake
let bx=144+Math.round(frame*.18),by=418+Math.round(wave(frame,1,.09)*2);
o+=r(bx-3,by+20,48,2,'#638e8d')+p([[bx,by+7],[bx+44,by+7],[bx+37,by+17],[bx+8,by+17]],'#253b50')+r(bx+6,by+6,29,3,'#c9897f')+r(bx+12,by-2,21,8,'#f2caa6')+r(bx+15,by,15,3,'#5e8192')+r(bx+22,by-23,2,24,'#485a6c')+p([[bx+24,by-20],[bx+24,by],[bx+37,by]],'#f8d9b4')+r(bx+10,by+17,25,2,'#629096');
// tiny background ferry crossing horizon
let far=322-frame*.21;o+=r(far,380,27,3,'#4c7080')+r(far+5,373,13,7,'#9b9fa3')+r(far+8,368,2,5,'#425a69')+r(far+12,387,18,1,'#d3b69f');
// rigging + mooring poles
for(let i=0;i<4;i++){let x=25+i*31;o+=r(x,382,2,32,'#263f54')+r(x-2,381,6,3,'#dba891')}
return o}
function birds(frame){let o='';for(let i=0;i<7;i++){let x=30+i*32+frame*(.035+i*.002),y=210+(i%3)*13+Math.sin(frame*.033+i)*2;let c=i%3===0?'#385e72':'#596a83';o+=r(x,y,4,1,c)+r(x-3,y-2,3,1,c)+r(x+4,y-2,3,1,c)}return o}
function promenade(frame){let o='';// foreground angled stone esplanade / paving
 o+=p([[0,517],[360,527],[360,640],[0,640]],'#344c5e');
 o+=p([[0,522],[360,529],[360,544],[0,539]],'#79898b');o+=r(0,539,360,4,'#c19d8b');o+=r(0,543,360,6,'#34485d');
 // intricately staggered flagstones
 for(let j=0;j<10;j++){let y=549+j*11;o+=r(0,y,360,1,j%2?'#4c6874':'#60727b');for(let i=0;i<10;i++){let x=i*41+(j%2)*20+Math.sin(j*i)*3;o+=r(x,y+2,1,9,'#243c50');if((i+j)%3===0)o+=r(x+7,y+4,4,1,'#81948f')}}
 // fading bronze railing behind spectators
 o+=r(0,507,360,4,'#d3ab91')+r(0,513,360,3,'#324b5e');
 for(let i=0;i<13;i++){let x=4+i*29;o+=r(x,493,3,34,'#3b5665')+r(x-2,490,7,5,'#a98c81')+r(x+1,502,1,15,'#c39b85')}
 o+=r(0,496,360,2,'#bd998c');
 // elegant iron bench with thin slats and warm timber
 o+=r(93,514,51,5,'#c58f73')+r(93,520,51,4,'#996c64')+r(98,507,43,3,'#b98979')+r(94,526,5,13,'#30495b')+r(138,526,5,13,'#30495b');
 for(let i=0;i<4;i++)o+=r(99+i*12,515,1,10,'#edbc98');
 // two nostalgic silhouettes leaning toward the bay; one seated
 const sway=Math.round(wave(frame,2,.036));
 o+=r(116+sway,489,9,10,'#e8b39a')+r(115+sway,486,11,5,'#38405a')+r(114+sway,500,13,16,'#405e74')+r(113+sway,514,15,5,'#2e4358')+r(114+sway,519,4,11,'#293c51')+r(126+sway,519,11,4,'#293c51');
 // standing figure with peach shawl and hat
 const bx=174+Math.round(wave(frame,4,.027));o+=r(bx+3,472,8,10,'#dfad98')+r(bx,471,15,4,'#394b64')+r(bx+2,469,10,4,'#6b5770')+p([[bx+2,483],[bx+12,483],[bx+16,511],[bx-3,511]],'#b98691')+r(bx+2,508,4,23,'#39465a')+r(bx+10,508,4,23,'#39465a')+r(bx-2,489,3,17,'#dfad98')+r(bx+14,489,3,15,'#e1b69d');
 // small observant cat near the bench
 o+=r(66,529,15,8,'#304253')+p([[68,529],[69,522],[75,528]],'#304253')+p([[76,528],[80,523],[80,532]],'#304253')+r(80,530,6,2,'#304253')+r(74,531,1,1,'#ffe8aa')+r(64,525,2,10,'#304253');
 return o}
function streetlamps(frame){let o='';for(let [x,y,s] of [[29,449,1],[278,462,.84]]){o+=`<g transform="translate(${x} ${y}) scale(${s})">`;
 o+=r(0,0,4,89,'#2a4356')+r(1,4,1,82,'#a07c78')+r(-6,-3,17,3,'#364f63')+r(-3,-8,11,5,'#48596c');
 // discrete stepped glow instead of raster blur
 for(let k=3;k>=0;k--)o+=r(-8-k*2,-9-k*2,22+k*4,12+k*3,['#fce2ad','#eec49c','#c99484','#9e7c80'][k]);
 o+=r(-5,-8,17,11,'#ffdfa9')+r(-2,-8,11,4,'#fff1bf')+r(-10,-12,27,2,'#34475c')+r(-3,91,11,3,'#273b4e');o+='</g>'}return o}
function foliage(frame){let o='';// corner masonry pots, cascading ivy and windswept leaves
for(let [px,py,s] of [[-7,570,1.5],[324,578,1.4],[13,630,1.1],[282,624,1.15]]){o+=`<g transform="translate(${px} ${py}) scale(${s})">`;
o+=p([[3,24],[34,24],[31,43],[7,43]],'#956d72')+r(0,22,36,5,'#c5917d')+r(4,27,28,3,'#e2ad89')+r(5,40,26,2,'#6c5f63');
for(let j=0;j<17;j++){let xx=4+j*2,yy=23-(j%6)*6;let sw=Math.round(Math.sin(frame*.04+j*3+px)*2);o+=r(xx,yy,1,24-yy+23,'#4d796e')+r(xx+sw-2,yy,6+(j%3),4,j%3?'#5c9581':'#92b18c');if(j%5===0)o+=r(xx+sw,yy-3,3,3,j%2?'#ffbb9c':'#f7d48f')}
o+='</g>'}
for(let i=0;i<35;i++){let x=(i*53)%360,y=604+(i%5)*6;let dx=Math.round(Math.sin(frame*.035+i)*2);o+=r(x,y,1,640-y,'#476f68')+r(x+dx,y-2,4,3,i%4?'#719783':'#c9ae8e');if(i%7===0)o+=r(x+dx+1,y-5,3,3,'#d79092')}
// right wall balcony flowering vines descending into scene
for(let k=0;k<28;k++){let x=350-(k%7)*4,y=333+Math.floor(k/7)*13;o+=r(x,y,4,4,k%3?'#42746c':'#7aa483');if(k%4===0)o+=r(x+1,y-2,2,2,'#e8a297')}
return o}
export function sunsetHarborSvg(frame){frame=Math.floor(Math.max(0,frame));let o=`<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">`;
o+=sky(frame);
// halo in stepped sunset bands and a deliberately faceted sun
for(let rr=48;rr>=24;rr-=8)o+=pixelDisc(227,273,rr,mix('#efb7ad','#f8c9ae',1-(rr-24)/24),3);
o+=pixelDisc(227,273,20,'#fff0bf',2)+pixelDisc(225,272,13,'#fff4cd',2);
o+=cloud(-41,111,1.3,frame,0)+cloud(166,154,.85,frame,1)+cloud(265,81,.8,frame,2)+cloud(-88,231,.95,frame,3);
o+=birds(frame)+mountains()+water(frame)+architecture()+docks(frame);
o+=promenade(frame)+streetlamps(frame)+foliage(frame);
// a soft frame-within-the-frame, not a dark vignette filter
return o+'</svg>'}