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
function leaves(c,x,y,rx,ry,dark,main,light,seed){
 const widths=[.36,.60,.78,.91,1,.97,.86,.68,.43];
 for(let j=0;j<widths.length;j++){
   const yy=y-ry+Math.round(j*ry*2/(widths.length-1)),half=Math.round(rx*widths[j]);
   block(c,x-half-2,yy-1,half*2+4,Math.max(3,Math.floor(ry/5)),dark);
   block(c,x-half,yy,half*2,Math.max(2,Math.floor(ry/6)),main);
 }
 for(let j=0;j<10;j++){
  const a=mod(j*13+seed*11,37)/37,b=mod(j*7+seed*5,29)/29;
  const px=x-rx+Math.round(a*rx*1.7),py=y-ry+Math.round(b*ry*1.65);
  block(c,px,py,3+(j%3)*2,2+(j%2),j%5===0?dark:light);
 }
 for(let j=0;j<6;j++){
  const px=x-rx+mod(j*19+seed*13,rx*2),py=y+mod(j*7+seed,Math.max(4,ry))-2;
  block(c,px,py,3+(j%2),2,dark);
 }
}
function tree(c,{x,y,kind,scale=1,depth=1,seed=1}){
 // Agent 4 compositional polish: grow layered native-pixel canopy sizes to
 // fill the formerly empty sky without shifting wheel or road contacts.
 // Native LDtk x/y, species and authored palette remain authoritative.
 // Largest near pines remain within 235px plane rather than being cut at top.
 scale *= depth===0?1.35:depth===1?1.50:1.48;
 const dark=depth===0?'farDark':depth===1?'midDark':'nearDark';
 const fill=depth===0?'far':depth===1?'mid':'near';
 const light=depth===0?'farLight':depth===1?'midLight':'nearLight';
 const stem=depth===0?'farDark':'bark';
 const h=Math.round((kind==='pine'?128:kind==='poplar'?132:kind==='birch'?108:96)*scale),
  width=Math.max(3,Math.round((kind==='pine'?5:7)*scale));
 block(c,x-width/2-1,y-h+22,width+2,h-20,dark);
 block(c,x-width/2,y-h+21,width,h-19,stem);
 if(depth>0){block(c,x+1,y-h+25,2,h-29,'barkLight');block(c,x-2,y-17,2,9,'barkDark')}
 if(kind==='pine'){
  for(let i=0;i<5;i++){
   const top=y-h+10+i*Math.round(h/6),rx=Math.round((12+i*5)*scale);
   leaves(c,x+(i%2?2:-2),top+9,rx,Math.round(13*scale),dark,fill,light,seed+i);
  }
 } else if(kind==='poplar'){
  for(let i=0;i<5;i++)leaves(c,x+(i%2?4:-4),y-h+16+i*Math.round(h/6),
   Math.round(14*scale),Math.round(24*scale),dark,fill,light,seed+i);
 } else {
  const crown=kind==='oak'?[[0,-.62,.58,.27],[-.44,-.49,.42,.26],[.43,-.46,.40,.26],[-.19,-.77,.36,.24],[.23,-.75,.39,.26]]:
   kind==='maple'?[[0,-.64,.58,.25],[-.46,-.55,.35,.24],[.45,-.51,.42,.24],[-.1,-.81,.34,.23],[.28,-.72,.34,.22]]:
   [[0,-.61,.57,.24],[-.43,-.48,.43,.23],[.45,-.44,.39,.22],[0,-.77,.43,.22]];
  for(let i=0;i<crown.length;i++){
   const [dx,dy,rX,rY]=crown[i];leaves(c,x+Math.round(dx*68*scale),y+Math.round(dy*h),
     Math.round(rX*60*scale),Math.round(rY*h*scale),dark,fill,light,seed+i);
  }
 }
 if(depth===2)for(let j=0;j<3;j++)block(c,x-32+j*24,y-5-(j%2)*2,6,3,'grassDark');
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
  cloud(c,26,98,65);cloud(c,244,154,82);cloud(c,-15,220,46);
  hill(c,23,404,'hill');hill(c,100,441,'farLight');
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
