/**
 * Original countryside pixel tile master. All pixels are directly authored
 * on the native 1px grid: irregular stepped crowns and individual highlight
 * clusters, no smoothing, SVG, filtering, 3D, third-party sprites or RNG.
 *
 * Only the world renderer came from Agent 2's current branch; their PNG
 * sources were absent when integrated, so this integration-owned replacement
 * is deliberately identified and kept editable/reproducible here.
 */
import sharp from 'sharp';
import {mkdirSync,writeFileSync} from 'node:fs';
const palette={
 sky:'#6DB6E5', far:'#6A9774', mid:'#4B8B56', near:'#2B7047',
 light:'#85AD65', trunk:'#705542', ink:'#263E39',
 grass:'#739D53', road:'#575E65', roadShadow:'#444C55',
 dust:'#E4D49B'
};
const specs={
 sky:[360,480],farTrees:[180,240],midTrees:[360,240],
 nearTrees:[360,250],verge:[180,160],road:[360,160]
};
const hex=(h)=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
const canv=(w,h)=>({w,h,data:new Uint8Array(w*h*4)});
function dot(im,x,y,c){
 if(x<0||x>=im.w||y<0||y>=im.h)return;
 let i=(y*im.w+x)*4;const rgb=hex(c);
 im.data[i]=rgb[0];im.data[i+1]=rgb[1];im.data[i+2]=rgb[2];im.data[i+3]=255;
}
function rect(im,x,y,w,h,c){
 x=Math.round(x);y=Math.round(y);w=Math.round(w);h=Math.round(h);
 for(let j=Math.max(0,y);j<Math.min(im.h,y+h);j++)
 for(let i=Math.max(0,x);i<Math.min(im.w,x+w);i++)dot(im,i,j,c);
}
function wrapRect(im,x,y,w,h,c){
 for(const dx of [-im.w,0,im.w])rect(im,x+dx,y,w,h,c);
}
function stepped(im,x,y,rows,c){
 // Each deliberate scan-band uses native crisp pixels, no circles or vectors.
 for(const [dy,xa,xb,height] of rows)wrapRect(im,x+xa,y+dy,xb-xa,height,c);
}
const canopy={
 oak:[[-109,-18,22,9],[-100,-32,30,11],[-89,-40,38,12],
      [-77,-45,43,15],[-62,-45,47,17],[-45,-40,42,10],
      [-35,-33,35,10],[-25,-18,28,10]],
 beech:[[-155,-9,14,12],[-143,-18,21,11],[-132,-23,27,16],
        [-116,-28,27,13],[-103,-30,31,20],[-83,-27,28,17],
        [-66,-23,24,18],[-48,-15,18,19],[-29,-10,11,13]],
 chestnut:[[-130,-30,7,11],[-119,-41,25,14],[-105,-46,38,14],
           [-91,-51,48,19],[-72,-49,49,16],[-56,-44,41,13],
           [-43,-34,38,12],[-31,-20,26,12]],
 poplar:[[-161,-8,8,10],[-151,-15,16,16],[-135,-20,20,24],
         [-111,-22,23,23],[-88,-23,22,21],[-67,-18,19,21],
         [-46,-15,15,19],[-27,-9,11,11]]
};
const detail={
 oak:[[-23,-86,20,9],[9,-103,18,7],[-40,-65,15,10],
      [19,-63,17,9],[-7,-43,21,8],[29,-48,9,6]],
 beech:[[-16,-136,12,8],[5,-119,15,13],[-25,-100,10,13],
        [1,-87,15,12],[-21,-64,12,10],[12,-52,9,10]],
 chestnut:[[-38,-93,17,10],[-9,-116,22,8],
           [19,-96,18,12],[-48,-67,19,9],[8,-54,25,8],
           [-25,-43,11,6]],
 poplar:[[-13,-138,12,11],[6,-123,8,15],[-22,-100,11,10],
         [7,-84,13,12],[-16,-62,12,12],[4,-44,10,8]]
};
const shade={
 oak:[[-31,-54,13,8],[16,-39,24,7]],
 beech:[[1,-52,15,10],[-11,-39,9,9]],
 chestnut:[[-25,-45,25,9],[20,-63,13,9]],
 poplar:[[-9,-33,14,8],[-14,-80,10,10]]
};
function tree(im,{x,ground,type,depth=1}){
 const main=depth===0?palette.far:depth===1?palette.mid:palette.near;
 const shadow=depth===0?palette.mid:palette.ink;
 const highlight=depth===0?palette.light:depth===1?palette.light:palette.mid;
 const narrow=type==='poplar'||type==='beech';
 const trunkW=depth===0?5:narrow?7:9;
 const trunkTop=type==='poplar'?ground-98:ground-71;
 wrapRect(im,x-Math.floor(trunkW/2),trunkTop,trunkW,ground-trunkTop,palette.trunk);
 wrapRect(im,x-Math.floor(trunkW/2),trunkTop,2,ground-trunkTop,shadow);
 // Faceted natural branch arms; partially obscured by hand-painted foliage.
 wrapRect(im,x-16,ground-63,16,5,palette.trunk);
 wrapRect(im,x+2,ground-54,13,5,palette.trunk);
 stepped(im,x,ground,canopy[type],shadow);
 stepped(im,x,ground-2,canopy[type].map(([dy,l,r,h])=>[dy+3,l+3,r-3,Math.max(1,h-5)]),main);
 for(const [dx,dy,w,h] of detail[type])wrapRect(im,x+dx,ground+dy,w,h,highlight);
 for(const [dx,dy,w,h] of shade[type])wrapRect(im,x+dx,ground+dy,w,h,main);
 // Tiny deliberate disconnected leaf pixels for hand-dithered contour.
 for(const [dx,dy] of [[-26,-96],[-11,-116],[23,-72],[35,-57],
                        [-29,-42],[10,-28]])
   wrapRect(im,x+dx,ground+dy,2,3,main);
}
const scenes={
 farTrees:[{x:21,ground:239,type:'beech',depth:0},
           {x:86,ground:236,type:'oak',depth:0},
           {x:161,ground:240,type:'poplar',depth:0}],
 midTrees:[{x:35,ground:240,type:'chestnut',depth:1},
           {x:127,ground:239,type:'poplar',depth:1},
           {x:228,ground:240,type:'oak',depth:1},
           {x:332,ground:240,type:'beech',depth:1}],
 nearTrees:[{x:52,ground:249,type:'oak',depth:2},
            {x:181,ground:250,type:'chestnut',depth:2},
            {x:318,ground:249,type:'beech',depth:2}]
};
async function make(name){
 const [w,h]=specs[name],im=canv(w,h);
 if(name==='sky')rect(im,0,0,w,h,palette.sky);
 if(scenes[name])for(const t of scenes[name])tree(im,t);
 if(name==='verge'){
   rect(im,0,0,w,h,palette.grass);
   // Hand-planted irregular roadside grass tufts and pixel-scale shade.
   for(const [x,y,k] of [[8,2,6],[28,3,4],[52,0,9],
                          [76,4,5],[99,1,9],[124,2,6],[148,0,8],[174,3,5]]) {
     wrapRect(im,x,y,k,3,palette.light);
     wrapRect(im,x+2,y+3,2,3,palette.mid);
   }
   for(const [x,y] of [[12,110],[34,132],[86,146],[121,108],[153,137]])
     wrapRect(im,x,y,4,2,palette.mid);
 }
 if(name==='road'){
   rect(im,0,0,w,96,palette.road);
   rect(im,0,0,w,3,palette.roadShadow);
   rect(im,0,8,w,2,palette.dust);
   rect(im,0,94,w,2,palette.roadShadow);
   // One simple marked road, pixel-authored 36px dash every 90px.
   for(let x=21;x<w;x+=90){
     rect(im,x,52,36,4,palette.dust);
     rect(im,x+3,56,30,1,palette.roadShadow);
   }
   for(const [x,y,width] of [[7,22,8],[39,70,5],[109,31,10],
     [172,76,7],[232,20,6],[305,68,11]])rect(im,x,y,width,1,palette.roadShadow);
 }
 const dest='public/countryside/world/'+name+'.png';
 await sharp(im.data,{raw:{width:w,height:h,channels:4}})
   .png({palette:true,compressionLevel:9,effort:10}).toFile(dest);
 return {name,width:w,height:h,file:dest};
}
mkdirSync('public/countryside/world',{recursive:true});
const result=[];
for(const layer of Object.keys(specs))result.push(await make(layer));
writeFileSync('public/countryside/world/manifest.json',
  JSON.stringify({origin:'original native pixel-authored integration rescue',version:1,
    loopTiles:true,files:result},null,2)+'\n');
console.log('COUNTRYSIDE_NATIVE_PIXEL_WORLD_BUILT '+JSON.stringify(result));
