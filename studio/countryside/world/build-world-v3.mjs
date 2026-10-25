/** Pixel Videos V3 countryside world — original native-pixel artwork.
 * Six reusable scenery planes for the existing driving compositor.
 * Sharp writes real native-resolution RGBA PNGs. Never interpolate pixels.
 */
import sharp from 'sharp';
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
const OUT='public/countryside/world';
const size={sky:[360,480,0],farTrees:[720,300,180],midTrees:[840,265,215],nearTrees:[960,235,245],road:[384,160,480],verge:[384,160,480]};
const P={skyHigh:'#4E99D6',sky:'#67AFE1',skyLow:'#8FC9E7',cloud:'#E9F3E7',cloudShadow:'#BCDDE0',
 farDark:'#547A78',far:'#789C82',farLight:'#A3B99A',hill:'#82A88D',
 midDark:'#385E50',mid:'#4E8757',midLight:'#85B16B',
 nearDark:'#24483D',near:'#367750',nearLight:'#69A65B',spark:'#B5CC79',
 barkDark:'#493D39',bark:'#735643',barkLight:'#AC7A51',
 grassDark:'#426E43',grass:'#79A657',grassLight:'#B2C87B',
 roadDark:'#3C4A4E',road:'#566269',roadLight:'#687477',line:'#E6D79D',soil:'#8F7955'};
const color=Object.fromEntries(Object.entries(P).map(([k,v])=>[k,[1,3,5].map(i=>parseInt(v.slice(i,i+2),16))]));
function canvas(w,h){return {w,h,p:new Uint8Array(w*h*4)}}
function put(c,x,y,k){if(y<0||y>=c.h)return;const xx=((x%c.w)+c.w)%c.w,i=(y*c.w+xx)*4,v=color[k];c.p[i]=v[0];c.p[i+1]=v[1];c.p[i+2]=v[2];c.p[i+3]=255}
function block(c,x,y,w,h,k){for(let yy=Math.round(y);yy<Math.round(y+h);yy++)for(let xx=Math.round(x);xx<Math.round(x+w);xx++)put(c,xx,yy,k)}
const mod=(n,m)=>((n%m)+m)%m;
function cloud(c,x,y,len){
 const cells=[[0,10,8,5],[7,5,15,10],[16,0,13,15],[27,4,14,13],[39,8,12,8],[8,13,40,6]];
 for(const [dx,dy,w,h] of cells)block(c,x+Math.round(dx*len/54),y+dy+2,Math.max(3,Math.round(w*len/54)),h,'cloudShadow');
 for(const [dx,dy,w,h] of cells)block(c,x+Math.round(dx*len/54),y+dy,Math.max(3,Math.round(w*len/54)),Math.max(2,h-3),'cloud');
 for(let j=0;j<4;j++)block(c,x+6+j*11*len/54,y+19+j%2,Math.max(5,Math.round(7*len/54)),1,'skyLow');
}
function hill(c,phase,base,shade){
 for(let x=0;x<c.w;x+=4){const slope=Math.round(Math.sin((x+phase)*.012)*9+Math.sin((x+phase)*.031)*3);
 block(c,x,base+slope,4,c.h-base-slope,shade)}
}
/** Individual organic sprite silhouettes: hand-tuned stepped contours, not rectangular canopies. */
function blob(c,cx,cy,rx,ry,dark,main,light,seed){
 const step=3;
 for(let y=-ry;y<=ry;y+=step){
  const unit=Math.abs(y)/ry;
  if(unit>=.99)continue;
  const w=Math.max(2,Math.round(rx*Math.sqrt(1-unit*unit)));
  const irregular=(mod(seed*37+Math.floor(y/step)*11,9)-4);
  const left=Math.round(cx-w+irregular+Math.sin((y+seed*7)*.21)*3);
  const right=Math.round(cx+w+irregular/2);
  block(c,left-2,cy+y,right-left+4,3,dark);
  block(c,left+2,cy+y,right-left-3,3,main);
  if(mod(y+seed,5)===0){
   block(c,left+5,cy+y,Math.max(3,Math.floor(w*.28)),2,light);
   block(c,right-Math.round(w*.46),cy+y,Math.max(2,Math.floor(w*.25)),1,light);
  }
 }
 // Directional three-tone leaf clusters make every crown feel hand-shaded.
 for(let i=0;i<11;i++){
  const px=cx-rx+mod(i*31+seed*17,Math.max(4,rx*2-12));
  const py=cy-ry+mod(i*13+seed*7,Math.max(4,ry*2-8));
  const nx=(px-cx)/rx,ny=(py-cy)/ry;
  if(nx*nx+ny*ny>.72)continue;
  block(c,px,py,5+mod(i+seed,7),3+mod(i,3),i%4===0?dark:light);
  block(c,px+3,py+3,3+mod(seed,3),1,main);
 }
 // Intentional irregular leaf cluster boundaries and carefully placed glints.
 for(let i=0;i<26;i++){
  const xx=mod(seed*17+i*37,rx*2)-rx, yy=mod(seed*11+i*19,ry*2)-ry;
  if((xx*xx)/(rx*rx)+(yy*yy)/(ry*ry)>.83)continue;
  const lightKey=i%7===0?dark:i%4===0?light:main;
  block(c,cx+xx,cy+yy,2+mod(i,4),2+mod(i+seed,2),lightKey);
 }
}
function needleTier(c,x,yy,rx,ry,shade,main,light,seed){
 for(let dy=0;dy<ry;dy+=3){
  const wide=Math.max(1,Math.round(rx*(dy/ry)));
  const rag=mod(seed*11+dy*7,7)-3;
  block(c,x-wide-rag,yy+dy,wide*2+rag+2,3,shade);
  block(c,x-wide+2-rag,yy+dy,Math.max(3,wide*2-3),2,main);
  if(dy%9===0)block(c,x-wide+5,yy+dy,Math.max(3,wide*.45),1,light);
 }
}
function tree(c,{x,y,kind,scale=1,depth=1,seed=1}){
 const dark=depth===0?'farDark':depth===1?'midDark':'nearDark';
 const fill=depth===0?'far':depth===1?'mid':'near';
 const light=depth===0?'farLight':depth===1?'midLight':'nearLight';
 const h=Math.round((depth===2?kind==='pine'?198:kind==='poplar'?194:173:depth===1?153:146)*scale);
 const stemW=Math.max(3,Math.round((kind==='poplar'||kind==='pine'?5:8)*scale));
 const top=y-h;
 // Bark first, foliage later, so branch junctions are naturally hidden.
 block(c,x-stemW/2-1,top+24,stemW+2,h-22,dark);
 block(c,x-stemW/2,top+25,stemW,h-22,depth===0?'farDark':'bark');
 if(depth!==0){
  block(c,x+1,top+31,2,h-36,'barkLight');
  for(const [dx,dy,w] of [[-1,.48,28],[1,.61,23],[-1,.74,18]]){
   const yy=Math.round(top+h*dy);
   block(c,x+(dx<0?-w:0),yy,w,3,'barkDark');
   block(c,x+(dx<0?-w:x+w-4),yy-6,4,8,'bark');
  }
 }
 const cx=Math.round(x+(seed%3-1)*3);
 if(kind==='pine'){
  for(let i=0;i<5;i++){
   const py=top+Math.round(8+i*h*.137),rx=Math.round((15+i*6)*scale),ry=Math.round(29*scale);
   needleTier(c,cx+(i%2),py,rx,ry,dark,fill,light,seed+i);
  }
  block(c,x-1,top-3,2,19,light);
 } else if(kind==='poplar'){
  for(let i=0;i<5;i++){
   const ty=top+Math.round((.19+i*.12)*h);
   blob(c,cx+(i%2?4:-3),ty,Math.round((18+(i%3)*3)*scale),Math.round(31*scale),dark,fill,light,seed+i);
  }
 }else {
  const crowned=kind==='oak'?[[-.42,.43,.39,.25],[.26,.36,.44,.27],[0,.24,.43,.25],[-.13,.58,.47,.24],[.4,.57,.32,.19]]:
   kind==='maple'?[[-.32,.38,.4,.24],[.29,.37,.4,.23],[0,.2,.39,.25],[-.08,.61,.48,.22]]:
   kind==='birch'?[[-.19,.31,.32,.22],[.26,.35,.32,.23],[0,.5,.39,.24],[-.35,.59,.25,.15]]:
   [[-.37,.41,.38,.2],[.31,.45,.4,.22],[0,.31,.45,.2],[.03,.62,.46,.19]];
  const crownWidth=Math.round((kind==='oak'?100:kind==='maple'?88:kind==='birch'?70:94)*scale);
  for(let i=0;i<crowned.length;i++){
   const [dx,dy,wx,hy]=crowned[i];
   const rx=Math.max(12,Math.round(crownWidth*wx)),ry=Math.round(h*hy);
   blob(c,cx+Math.round(dx*crownWidth),top+Math.round(dy*h),rx,ry,dark,fill,light,seed*3+i*7);
  }
  if(kind==='birch'&&depth>0){
   block(c,x-2,y-54,4,45,'cloud');
   for(let k=0;k<5;k++)block(c,x-2+(k%2)*2,y-50+k*8,3,2,'nearDark');
  }
 }
 // Native-pixel tufts and root cast shadow rather than a boxy shared platform.
 if(depth===2){
  block(c,x-19,y-3,35,3,'nearDark');
  for(let j=0;j<6;j++){
   const tx=x-28+j*11,hh=4+mod(j*seed,7);
   block(c,tx,y-hh,2,hh,'grassDark');
   block(c,tx-2,y-hh+3,5,2,j%3===0?'spark':'nearLight');
  }
 }
}

const groves={
 farTrees:[['poplar',12,300,.72],['pine',98,300,.73],['oak',184,300,.77],['birch',273,300,.76],['maple',364,300,.78],['poplar',455,300,.71],['beech',556,300,.82],['pine',654,300,.78]],
 midTrees:[['oak',6,265,1.01],['birch',110,265,.96],['pine',202,265,1.03],['maple',307,265,1.00],['poplar',414,265,.94],['beech',516,265,.99],['pine',613,265,1.02],['oak',711,265,1.03],['birch',819,265,.94]],
 nearTrees:[['pine',-32,235,1.13],['oak',90,235,1.08],['maple',215,235,1.16],['birch',341,235,1.06],['pine',454,235,1.17],['beech',576,235,1.09],['oak',699,235,1.14],['poplar',819,235,1.11],['maple',947,235,1.08]]};
// The LDtk project is the authoritative tree-layout source; edit its entity placements.
const layout=JSON.parse(readFileSync('studio/countryside/world/countryside-v3.ldtk','utf8'));
for(const layerName of Object.keys(groves)){
 const layer=layout.levels[0].layerInstances.find(l=>l.__identifier===layerName);
 if(!layer||!Array.isArray(layer.entityInstances)||layer.entityInstances.length<5)
  throw Error('Missing authored LDtk entities for '+layerName);
 groves[layerName]=layer.entityInstances.map(e=>{
  const field=n=>e.fieldInstances.find(x=>x.__identifier===n)?.__value;
  const kind=field('kind'),scale=Number(field('scale'));
  if(!['oak','maple','birch','pine','poplar','beech'].includes(kind)||!Number.isFinite(scale))throw Error('Malformed LDtk tree');
  return [kind,e.px[0],e.px[1],scale];
 });
}
function paint(id){const [w,h]=size[id],c=canvas(w,h);
 if(id==='sky'){
  block(c,0,0,w,110,'skyHigh');block(c,0,110,w,155,'sky');block(c,0,265,w,h-265,'skyLow');
  for(let yy=100;yy<118;yy+=5)block(c,0,yy,w,1,'sky');
  cloud(c,12,55,58);cloud(c,230,113,96);cloud(c,-10,186,78);
  cloud(c,140,247,73);
  block(c,0,302,w,2,'skyLow');
  hill(c,23,379,'hill');hill(c,100,435,'farLight');
 } else if(groves[id]){
  const depth=id==='farTrees'?0:id==='midTrees'?1:2;
  for(const [i,t] of groves[id].entries())tree(c,{x:t[1],y:t[2],kind:t[0],scale:t[3],depth,seed:i*3+1});
  const base=depth===0?'farDark':depth===1?'midDark':'nearDark',gr=depth===0?'far':depth===1?'mid':'near';
  block(c,0,h-12,w,12,base);block(c,0,h-7,w,7,gr);
  for(let x=0;x<w;x+=11){const yy=h-12-mod(x*7,10);block(c,x,yy,3+mod(x,4),3,gr);
  if(depth===2){block(c,x+2,h-17-mod(x,6),2,9,'nearLight');block(c,x+4,h-16,1,4,'spark')}}
 }else if(id==='road'){
  block(c,0,0,w,98,'road');block(c,0,0,w,4,'roadDark');block(c,0,4,w,2,'line');
  block(c,0,9,w,2,'roadLight');block(c,0,84,w,3,'roadLight');block(c,0,94,w,4,'roadDark');
  for(let x=13;x<w;x+=96){block(c,x,54,39,4,'line');block(c,x+3,58,32,1,'roadDark')}
  for(let x=0;x<w;x+=13){let y=16+mod(x*11,69);block(c,x+2,y,2+mod(x,5),1,mod(x,3)?'roadDark':'roadLight')}
  for(let x=0;x<w;x+=64){block(c,x+4,22,5,1,'roadLight');block(c,x+23,77,4,1,'roadDark')}
  block(c,0,98,w,62,'grass');block(c,0,98,w,4,'soil');block(c,0,102,w,2,'grassLight');
  for(let x=0;x<w;x+=13){const y=107+mod(x*7,52);block(c,x,y,5,2,'grassDark');block(c,x+2,y-4,2,5,'grassLight')}
 }else if(id==='verge'){
  for(let x=0;x<w;x+=11){const k=mod(x*7,9);block(c,x,0-k,2,7+k,'grassDark');block(c,x+3,3,2,3,'grassLight')}
  for(let x=7;x<w;x+=51){const k=mod(x,7);block(c,x,8+k,2,6,'grassDark');
   block(c,x-2,9+k,6,2,'grassLight');block(c,x,7+k,2,2,'spark')}
  for(let x=2;x<w;x+=23){let y=111+mod(x*5,38);block(c,x,y,2,7,'grassDark');
   block(c,x-2,y+3,5,2,'grassLight')}
 }
 return c;
}
mkdirSync(OUT,{recursive:true});const manifest={version:3,source:'original native-pixel authored Pixel Videos V3',nativeCanvas:[360,640],palette:P,tiles:{}};
for(const [id,[w,h,y]] of Object.entries(size)){
 const c=paint(id),file=OUT+'/'+id+'.png';
 await sharp(c.p,{raw:{width:w,height:h,channels:4}}).png({compressionLevel:9}).toFile(file);
 manifest.tiles[id]={width:w,height:h,y,file,scrolling:id!=='sky'};
}
writeFileSync(OUT+'/manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log('COUNTRYSIDE_V3_WORLD_BUILT',JSON.stringify(manifest.tiles));
