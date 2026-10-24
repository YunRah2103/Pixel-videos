/**
 * Countryside Drive V2 — authored native-pixel landscape master.
 * Crisp stepped original sprite artwork with seamless repeating tile periods.
 * No vectors, pixelation filters, smooth gradients or third-party assets.
 */
import sharp from 'sharp';
import {mkdirSync,writeFileSync} from 'node:fs';
const P={sky:'#6DB6E5',far:'#6A9774',farShade:'#568369',farLight:'#87AF80',
 mid:'#4B8B56',midShade:'#34764C',midLight:'#85AD65',
 near:'#2B7047',nearShade:'#244F3F',nearLight:'#559659',
 bark:'#705542',barkDark:'#4D433B',outline:'#263E39',
 verge:'#739D53',vergeShade:'#527F49',vergeLight:'#98B96D',
 asphalt:'#575E65',asphaltDark:'#444C55',asphaltLight:'#687078',line:'#E4D49B'};
const dims={sky:[360,480],farTrees:[180,240],midTrees:[360,280],nearTrees:[360,340],verge:[180,160],road:[360,160]};
const RGB=Object.fromEntries(Object.entries(P).map(([k,v])=>[k,[1,3,5].map(i=>parseInt(v.slice(i,i+2),16))]));
const bitmap=(w,h)=>({w,h,data:Buffer.alloc(w*h*4)});
function rect(b,x,y,w,h,c){const rgb=RGB[c];x=Math.round(x);y=Math.round(y);w=Math.round(w);h=Math.round(h);
 for(let j=Math.max(0,y);j<Math.min(b.h,y+h);j++)for(let i=Math.max(0,x);i<Math.min(b.w,x+w);i++){
  const k=(j*b.w+i)*4;b.data[k]=rgb[0];b.data[k+1]=rgb[1];b.data[k+2]=rgb[2];b.data[k+3]=255;
 }}
function band(b,x,y,w,h,c){for(const dx of [-b.w,0,b.w])rect(b,x+dx,y,w,h,c);}
const crown=[[-19,-5,10],[-16,-12,23],[-13,-17,34],[-9,-21,42],[-4,-24,48],
 [2,-26,51],[8,-25,50],[14,-21,44],[20,-18,38],[26,-13,28],[32,-7,17]];
function clump(b,x,y,s,ink,fill,light,flip=0){
 for(const [yy,xx,ww] of crown){const X=flip?-xx-ww:xx;band(b,x+X*s,y+yy*s,ww*s,5*s,ink);}
 for(const [yy,xx,ww] of crown.slice(1,-1)){const X=flip?-xx-ww:xx;band(b,x+(X+3)*s,y+(yy+2)*s,Math.max(3,ww-6)*s,3*s,fill);}
 for(const [dx,dy,w,h] of [[-11,-11,10,4],[8,-16,14,4],[-15,1,9,4],[19,5,8,3]])
   band(b,x+(flip?-dx-w:dx)*s,y+dy*s,w*s,h*s,light);
 for(const [dx,dy,w] of [[-8,18,13],[13,22,8]])band(b,x+dx*s,y+dy*s,w*s,3*s,fill);
}
function tree(b,{x,ground,kind,layer=1,accent=0}){
 const C=layer===0?['farShade','far','farLight']:
  layer===1?['midShade','mid','midLight']:['nearShade','near','nearLight'];
 const lean=accent%2?3:-2;
 const pineTip=ground-(layer===2?353:290);
 const trunkTop=kind==='pine'?pineTip:kind==='poplar'?ground-150:kind==='birch'?ground-107:ground-91;
 const width=layer===0?5:kind==='pine'||kind==='poplar'?7:9;
 band(b,x-Math.floor(width/2),trunkTop,width,ground-trunkTop,'bark');
 band(b,x-Math.floor(width/2),trunkTop,2,ground-trunkTop,'barkDark');
 if(kind==='pine'){
  // Joined tiered boughs, not detached generic geometric triangles.
  const levels=Math.floor((ground-21-pineTip)/12);
  for(let k=0;k<=levels;k++){
   const yy=pineTip+k*12;
   const reach=Math.min(55,Math.max(3,3+Math.round(k*2.25)));
   const sway=k%4===0?-3:k%4===2?2:0;
   band(b,x-reach+sway,yy,reach*2+3,15,C[0]);
   band(b,x-reach+3+sway,yy+2,reach*2-3,10,C[1]);
   if(k%2===0)band(b,x-reach+4+sway,yy+4,Math.max(4,Math.round(reach*.66)),3,C[2]);
   if(k%3===0)band(b,x+reach-7+sway,yy+8,7,4,C[2]);
   if(k%4===1)band(b,x-reach-5+sway,yy+10,9,3,C[0]);
  }
  band(b,x-4,ground-26,9,26,'bark');
  band(b,x-4,ground-24,2,24,'barkDark');
  return;
 }
 band(b,x+1,ground-74,22,5,'barkDark');band(b,x-17,ground-66,18,5,'barkDark');
 if(kind==='poplar'){
  for(let j=0;j<6;j++){
   const yy=ground-194+j*23;const xx=x+(j%2?4:-4);
   clump(b,xx,yy,1,C[0],C[1],C[2],j%2);
  }
  return;
 }
 const clumps=kind==='oak'?
  [[-38,-119,1,0],[-1,-143,1,1],[34,-126,1,0],[-57,-85,1,1],[-15,-98,1,0],[25,-90,1,1],[56,-84,1,0],[-18,-59,1,1],[24,-56,1,0]]:
  kind==='chestnut'?
  [[-43,-113,1,0],[-8,-157,1,0],[29,-133,1,1],[-60,-86,1,1],[-15,-102,1,0],[35,-97,1,1],[52,-69,1,0],[1,-58,1,0]]:
  [[-30,-105,1,0],[4,-131,1,1],[35,-107,1,1],[-49,-74,1,0],[-4,-91,1,1],[39,-75,1,0],[-6,-56,1,1]];
 for(const [xx,yy,ss,fl] of clumps)clump(b,x+xx+lean,ground+yy,ss,C[0],C[1],C[2],fl);
 band(b,x-2,ground-23,4,19,'barkDark');
 if(kind==='birch'){band(b,x-2,ground-46,4,6,'line');band(b,x+1,ground-24,3,4,'line');}
}
const layouts={
 farTrees:[{x:5,ground:239,kind:'oak',layer:0},{x:91,ground:235,kind:'poplar',layer:0},{x:161,ground:238,kind:'birch',layer:0}],
 midTrees:[{x:22,ground:280,kind:'birch'},{x:119,ground:279,kind:'chestnut',accent:1},
  {x:211,ground:280,kind:'pine'},{x:314,ground:279,kind:'oak',accent:1}],
 nearTrees:[{x:15,ground:340,kind:'pine',layer:2},{x:108,ground:339,kind:'oak',layer:2,accent:1},
  {x:232,ground:340,kind:'birch',layer:2},{x:340,ground:339,kind:'pine',layer:2,accent:1}]
};
function landscape(name,b){
 if(name==='sky'){rect(b,0,0,b.w,b.h,'sky');return;}
 if(layouts[name]){
  const shrub=name==='farTrees'?['farShade','far']:
    name==='midTrees'?['midShade','mid']:['nearShade','near'];
  for(let x=0;x<b.w;x+=17){band(b,x-1,b.h-27+(x%5),22,29,shrub[0]);
   band(b,x+3,b.h-24+(x%3),12,25,shrub[1]);}
  for(const t of layouts[name])tree(b,t);
  return;
 }
 if(name==='verge'){
  rect(b,0,0,b.w,b.h,'verge');rect(b,0,0,b.w,8,'vergeShade');
  rect(b,0,16,b.w,8,'vergeLight');
  for(const [x,y] of [[3,5],[21,12],[49,1],[72,16],[95,7],[128,4],[152,13],[173,5]]){
   band(b,x,y,9,3,'vergeLight');band(b,x+2,y-4,3,5,'midShade');band(b,x+7,y-2,2,3,'vergeShade');}
  for(const [x,y] of [[11,121],[33,109],[74,133],[105,149],[147,116],[169,137]]){
   band(b,x,y,14,3,'vergeShade');band(b,x+4,y-5,2,5,'midShade');}
  return;
 }
 if(name==='road'){
  rect(b,0,0,b.w,96,'asphalt');rect(b,0,0,b.w,3,'asphaltDark');
  rect(b,0,7,b.w,3,'line');rect(b,0,11,b.w,2,'asphaltLight');
  rect(b,0,93,b.w,3,'asphaltDark');
  for(let x=17;x<360;x+=90){band(b,x,51,37,4,'line');band(b,x+5,55,24,1,'asphaltDark');}
  for(const [x,y,w] of [[3,25,7],[29,71,11],[76,38,5],[118,81,8],[162,21,6],
    [201,64,10],[252,34,8],[288,77,6],[331,25,13]])band(b,x,y,w,1,'asphaltDark');
 }
}
mkdirSync('public/countryside/world',{recursive:true});const files=[];
for(const [name,[w,h]] of Object.entries(dims)){
 const b=bitmap(w,h);landscape(name,b);const file='public/countryside/world/'+name+'.png';
 await sharp(b.data,{raw:{width:w,height:h,channels:4}}).png({palette:true,compressionLevel:9,effort:8}).toFile(file);
 files.push({name,width:w,height:h,file});
}
writeFileSync('public/countryside/world/manifest.json',JSON.stringify({version:2,origin:'original hand-composed native sprite pixels',loopWidths:{farTrees:180,midTrees:360,nearTrees:360,verge:180,road:360},files},null,2)+'\n');
console.log('COUNTRYSIDE_V2_PIXEL_WORLD '+JSON.stringify(files));
