/** Countryside V2 original 1:1 pixel-authored world.
 * All shapes below are deliberately drawn native-pixel scan bands and stamps.
 * No SVG, vector curves, filtering, random noise, imported art or 3D.
 */
import sharp from 'sharp';
import {mkdirSync,writeFileSync} from 'node:fs';
const O='public/countryside/world';
const pal={sky:'#6DB6E5',skyTop:'#61A8DC',skyLow:'#7DBDE5',far:'#6A9774',farShade:'#4F7D69',farLight:'#88B087',mid:'#4B8B56',midShade:'#356D4D',midLight:'#85AD65',near:'#2B7047',nearShade:'#263E39',nearLight:'#5B9955',leaf:'#A0BC6E',bark:'#705542',barkLight:'#977354',grass:'#739D53',asphalt:'#575E65',roadShade:'#444C55',stripe:'#E4D49B'};
const spec={sky:[360,480,0],farTrees:[720,300,180],midTrees:[840,265,215],nearTrees:[960,235,245],verge:[384,160,480],road:[384,160,480]};
const rgb=Object.fromEntries(Object.entries(pal).map(([k,v])=>[k,[1,3,5].map(n=>parseInt(v.slice(n,n+2),16))]));
const canvas=(w,h)=>({w,h,p:new Uint8Array(w*h*4)});
function rect(a,x,y,w,h,c){x=Math.round(x);y=Math.round(y);w=Math.round(w);h=Math.round(h);if(w<1||h<1)return;const v=rgb[c];for(let yy=Math.max(0,y);yy<Math.min(a.h,y+h);yy++)for(let xx=x;xx<x+w;xx++){const i=(yy*a.w+((xx%a.w+a.w)%a.w))*4;a.p[i]=v[0];a.p[i+1]=v[1];a.p[i+2]=v[2];a.p[i+3]=255}}
const canopy={
 oak:[[-120,-15,11,8],[-112,-27,24,9],[-103,-37,36,11],[-92,-47,43,12],[-80,-53,49,14],[-66,-52,52,14],[-52,-49,48,12],[-40,-39,43,11],[-29,-27,29,10],[-19,-17,22,9]],
 maple:[[-135,-12,13,9],[-126,-29,22,9],[-117,-39,38,11],[-106,-52,44,13],[-93,-60,53,14],[-79,-57,58,14],[-65,-60,51,13],[-52,-53,48,12],[-40,-39,41,10],[-30,-29,30,10]],
 beech:[[-154,-8,12,10],[-144,-19,22,12],[-132,-29,28,13],[-119,-32,32,15],[-104,-35,36,16],[-88,-34,34,15],[-73,-32,34,15],[-58,-27,30,13],[-45,-24,24,12],[-33,-15,18,12]],
 poplar:[[-178,-4,8,14],[-164,-13,13,14],[-150,-19,18,15],[-135,-22,23,17],[-118,-24,25,17],[-101,-24,23,18],[-83,-26,25,19],[-64,-22,22,17],[-47,-18,18,18],[-29,-12,14,14]],
 pine:[[-193,-3,5,14],[-179,-12,10,11],[-168,-18,18,12],[-156,-10,13,9],[-147,-24,22,13],[-134,-15,16,9],[-125,-31,27,13],[-112,-18,19,9],[-103,-35,33,13],[-90,-19,20,9],[-81,-40,36,13],[-68,-24,25,10],[-58,-44,39,12],[-46,-27,27,9],[-37,-47,43,13],[-24,-27,28,10]]};
const cl={
 oak:[[-28,-106,16,6],[-6,-116,12,5],[14,-96,17,7],[-39,-82,16,8],[-10,-88,22,8],[30,-72,14,7],[-45,-63,16,6],[-24,-54,17,6],[11,-53,17,8],[-7,-33,16,6],[28,-39,11,6]],
 maple:[[-31,-121,19,6],[4,-132,12,5],[-48,-96,16,7],[-14,-105,20,7],[27,-98,16,7],[-41,-77,21,7],[-10,-83,23,8],[31,-75,17,7],[-50,-55,15,7],[-19,-48,16,6],[7,-60,18,8],[32,-49,12,6]],
 beech:[[-16,-143,12,7],[9,-126,12,8],[-27,-109,14,8],[1,-98,18,7],[-31,-82,14,7],[-10,-72,18,8],[13,-77,13,8],[-23,-53,13,7],[3,-51,14,8]],
 poplar:[[-9,-164,12,8],[-19,-140,11,9],[6,-130,12,8],[-13,-113,14,8],[8,-96,11,11],[-20,-88,11,8],[-15,-62,13,8],[5,-56,12,9],[-8,-42,13,7]],
 pine:[[-3,-174,8,5],[-10,-143,12,6],[8,-123,11,6],[-21,-100,14,6],[13,-78,13,6],[-28,-60,15,6],[10,-40,16,5],[-32,-29,16,5]]};
const grove={
 farTrees:[['poplar',26,300],['beech',118,300],['oak',222,301],['pine',314,300],['maple',421,301],['poplar',526,300],['oak',650,301],['beech',706,300]],
 midTrees:[['maple',19,265],['beech',150,264],['oak',281,265],['pine',398,265],['oak',519,265],['poplar',632,264],['maple',740,265],['beech',828,265]],
 nearTrees:[['oak',-12,235],['poplar',139,235],['maple',279,234],['pine',432,235],['beech',580,235],['oak',728,235],['pine',865,235],['maple',968,235]]};
function tree(a,type,x,g,depth,variant){
 const outline=depth===0?'farShade':depth===1?'midShade':'nearShade',main=depth===0?'far':depth===1?'mid':'near',light=depth===0?'farLight':depth===1?'midLight':'nearLight';
 const tall=(depth===0?1.10:depth===1?1.27:1.43)*(type==='pine'?1.13:type==='poplar'?1.08:1);
 const stretch=n=>Math.round(n*tall);
 const bwidth=type==='pine'||type==='poplar'?5:8;const top=g-stretch(type==='pine'?118:type==='poplar'?128:82);
 rect(a,x-5,top,bwidth+2,g-top,outline);rect(a,x-3,top,bwidth,g-top,'bark');rect(a,x+1,top+15,2,g-top-18,'barkLight');
 for(const [dy,side,width] of [[-80,-1,20],[-61,1,25],[-44,-1,22]]){rect(a,x+(side<0?-width:0),g+stretch(dy),width,4,'bark');rect(a,x+(side<0?-width:width-5),g+stretch(dy)-7,5,11,'bark')}
 for(const [dy,l,r,h] of canopy[type])rect(a,x+l-3,g+stretch(dy),r-l+6,Math.ceil(h*tall)+2,outline);
 for(const [dy,l,r,h] of canopy[type])rect(a,x+l+2,g+stretch(dy)+2,r-l-4,Math.ceil(h*tall)-2,main);
 for(let n=0;n<cl[type].length;n++){const [dx,dy,w,h]=cl[type][n];rect(a,x+dx+variant,g+stretch(dy),w,h,n%6===0&&depth!==0?'leaf':light);rect(a,x+dx+variant+2,g+stretch(dy)+h,Math.min(w-2,8),2,main)}
 if(depth===2){rect(a,x-1,g-36,2,6,outline);rect(a,x+2,g-21,2,4,'barkLight')}
}
function paint(name){const [w,h]=spec[name],a=canvas(w,h);
 if(name==='sky'){rect(a,0,0,w,h,'skyLow');rect(a,0,0,w,72,'skyTop');rect(a,0,72,w,132,'sky')}
 if(grove[name])grove[name].forEach(([kind,x,g],i)=>tree(a,kind,x,g,name==='farTrees'?0:name==='midTrees'?1:2,(i%3)-1));
 if(name==='verge'){
  rect(a,0,0,w,h,'grass');rect(a,0,0,w,9,'mid');rect(a,0,9,w,3,'midLight');rect(a,0,100,w,2,'mid');
  for(const [x,y] of [[6,13],[27,21],[58,8],[87,27],[115,14],[155,18],[180,9],[214,21],[247,12],[270,20],[303,15],[334,24],[367,16]]){rect(a,x,y,10,2,'midLight');rect(a,x+5,y-5,2,6,'mid');rect(a,x-2,y+2,4,2,'mid')}
  for(const [x,y] of [[12,129],[41,146],[84,122],[121,151],[176,133],[219,151],[254,128],[311,145],[373,121]]){rect(a,x,y,12,2,'mid');rect(a,x+4,y-5,3,5,'mid');rect(a,x+9,y-3,2,3,'midLight')}
 }
 if(name==='road'){
  rect(a,0,0,w,96,'asphalt');rect(a,0,0,w,4,'roadShade');rect(a,0,4,w,2,'stripe');rect(a,0,7,w,2,'roadShade');rect(a,0,88,w,8,'roadShade');rect(a,0,96,w,64,'grass');rect(a,0,96,w,3,'midLight');
  for(let x=27;x<w;x+=96){rect(a,x,55,42,4,'stripe');rect(a,x+3,59,36,1,'roadShade')}
  for(const [x,y,n] of [[9,29,12],[77,73,7],[133,38,18],[195,79,10],[270,27,12],[345,70,10]])rect(a,x,y,n,1,'roadShade');
  for(const [x,y] of [[13,113],[75,139],[137,118],[196,149],[255,129],[328,150],[370,112]]){rect(a,x,y,8,2,'mid');rect(a,x+4,y-4,2,4,'mid')}
 }
 return a;
}
mkdirSync(O,{recursive:true});const manifest={version:2,grid:1,authored:'2026-10-24',palette:pal,original:true,tiles:{}};
for(const [name,[w,h,y]] of Object.entries(spec)){
 const a=paint(name),file=O+'/'+name+'.png';
 await sharp(a.p,{raw:{width:w,height:h,channels:4}}).png({palette:false,compressionLevel:9}).toFile(file);
 manifest.tiles[name]={width:w,height:h,y,file,scrolling:name!=='sky'};
}
writeFileSync(O+'/manifest.json',JSON.stringify(manifest,null,2)+'\n');
console.log('COUNTRYSIDE_V2_WORLD_BUILT '+JSON.stringify(manifest.tiles));
