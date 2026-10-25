/**
 * TRUE PixiJS v8 production renderer: hand-authored trees and coupe,
 * but now with visibly cinematic animated depth / acceleration.
 * Every animation draws from Remotion's frame, never wall-clock time.
 */
import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {cancelRender,continueRender,delayRender,staticFile} from 'remotion';
import type {Application,Graphics,TilingSprite} from 'pixi.js';
import type {CinematicMotion} from './DrivingMotionV3';
import {PIXI_WORLD_LAYERS,planPixiWorld,type PixiWorldLayer,type PixiWorldPlan} from './PixiWorldPlan';

type PixiStage={
 app:Application;
 tiles:Map<PixiWorldLayer,TilingSprite>;
 shade:Graphics;roadDetails:Graphics;shrubs:Graphics;
 shadow:Graphics;glints:Graphics;leaves:Graphics;dust:Graphics;
};
function drawFrame(stage:PixiStage,plan:PixiWorldPlan):void{
 for(const layer of plan.layers){
  const tile=stage.tiles.get(layer.name);
  if(!tile)throw Error('Missing required PixiJS art plane: '+layer.name);
  tile.tilePosition.x=layer.tileX;
  tile.tilePosition.y=0;
 }
 // Moving hard-edged canopy shadow across the roadway. Native pixel rectangles.
 stage.shade.clear();
 for(const band of plan.shadeBands){
  stage.shade.rect(band.x,490,band.width,7)
   .fill({color:0x273B40,alpha:band.alpha*.65});
  stage.shade.rect(band.x+3,497,band.width+8,23)
   .fill({color:0x24373A,alpha:band.alpha});
  stage.shade.rect(band.x+9,520,band.width+14,17)
   .fill({color:0x24373A,alpha:band.alpha*.85});
  stage.shade.rect(band.x+14,537,band.width+8,29)
   .fill({color:0x24373A,alpha:band.alpha*.72});
 }
 stage.roadDetails.clear();
 for(const s of plan.roadSpecks){
  stage.roadDetails.rect(s.x,s.y,s.width,1).fill({color:s.color,alpha:.35});
 }
 // An original passing foreground verge plane: chunky 16-bit leaf geometry.
 // Its travel is 130% of road distance, creating unmistakable near depth.
 stage.shrubs.clear();
 const palettes=[
  [0x244E38,0x387647,0x81AA62],
  [0x27513D,0x3D7C51,0x8DAF62],
  [0x2D563C,0x467A43,0x9CB66E],
  [0x214A37,0x3F7849,0x77A560],
 ];
 for(const s of plan.shrubs){
  const [dark,base,bright]=palettes[s.tint];
  const w=s.size,h=9+Math.floor(s.size*.7),y=s.y;
  stage.shrubs.rect(s.x+Math.floor(w*.44),y-h+8,3,h+9).fill(dark)
   .rect(s.x+3,y-h+8,w-6,h-5).fill(dark)
   .rect(s.x+7,y-h+4,w-15,h-3).fill(base)
   .rect(s.x+Math.floor(w*.26),y-h,w-Math.floor(w*.45),6).fill(base)
   .rect(s.x+6,y-h+10,Math.max(3,w-12),4).fill(base)
   .rect(s.x+8,y-h+4,Math.max(3,Math.floor(w*.28)),2).fill(bright)
   .rect(s.x+w-10,y-h+13,5,2).fill(bright)
   .rect(s.x+2,y-2,w,3).fill(dark);
 }
 stage.shadow.clear()
  .rect(plan.contactShadow.x,plan.contactShadow.y,plan.contactShadow.width,2)
  .fill({color:0x182B30,alpha:plan.contactShadow.alpha})
  .rect(plan.contactShadow.x+19,plan.contactShadow.y+2,105,1)
  .fill({color:0x2C4944,alpha:plan.contactShadow.alpha*.58});
 stage.glints.clear();
 for(const light of plan.lightPixels){
  stage.glints.rect(light.x,light.y,3,2)
   .fill({color:light.color,alpha:light.alpha});
 }
 stage.leaves.clear();
 for(const leaf of plan.leafMotes){
  stage.leaves.rect(leaf.x,leaf.y,leaf.size,2)
   .fill({color:leaf.color,alpha:.78});
  stage.leaves.rect(leaf.x+1,leaf.y+2,1,1)
   .fill({color:0x537847,alpha:.58});
 }
 stage.dust.clear();
 for(const puff of plan.dust){
  stage.dust.rect(puff.x,puff.y,puff.size,2)
   .fill({color:0xB4A783,alpha:puff.opacity});
 }
 // The Pixi canvas is the actual world in the encoded Remotion movie.
 stage.app.renderer.render({container:stage.app.stage});
}
export const PixiCountrysideWorld:React.FC<{frame:number;motion:CinematicMotion}>=({
 frame,motion,
})=>{
 const host=useRef<HTMLDivElement>(null);
 const sceneRef=useRef<PixiStage|null>(null);
 const plan=planPixiWorld(frame,motion);
 const latestPlan=useRef(plan);
 const [renderHandle]=useState(()=>delayRender('Initialize real PixiJS six-layer countryside',{timeoutInMilliseconds:60000}));
 useLayoutEffect(()=>{
  latestPlan.current=plan;
  if(sceneRef.current)drawFrame(sceneRef.current,plan);
 },[frame,motion]);
 useEffect(()=>{
  let disposed=false;
  let stage:PixiStage|null=null;
  (async()=>{
   const pixi=await import('pixi.js');
   const app=new pixi.Application();
   await app.init({
    width:360,height:640,preference:'webgl',antialias:false,
    resolution:1,autoDensity:false,backgroundAlpha:0,
    autoStart:false,preserveDrawingBuffer:true,
   });
   if(disposed){app.destroy(true);return;}
   app.ticker.stop();
   app.canvas.style.width='360px';
   app.canvas.style.height='640px';
   app.canvas.style.display='block';
   app.canvas.style.imageRendering='pixelated';
   if(!host.current)throw Error('Missing actual PixiJS canvas host');
   host.current.appendChild(app.canvas);
   const tiles=new Map<PixiWorldLayer,TilingSprite>();
   for(const layer of PIXI_WORLD_LAYERS){
    const texture=await pixi.Assets.load(staticFile('countryside/world/'+layer.path));
    if(disposed){app.destroy(true);return;}
    texture.source.scaleMode='nearest';
    const tile=new pixi.TilingSprite({texture,width:360,height:layer.height});
    tile.x=0;tile.y=layer.y;tile.roundPixels=true;
    tiles.set(layer.name,tile);
    app.stage.addChild(tile);
   }
   const shade=new pixi.Graphics(),roadDetails=new pixi.Graphics(),
    shrubs=new pixi.Graphics(),shadow=new pixi.Graphics(),
    glints=new pixi.Graphics(),leaves=new pixi.Graphics(),dust=new pixi.Graphics();
   for(const graphic of [shade,roadDetails,shrubs,shadow,glints,leaves,dust]){
    app.stage.addChild(graphic);
   }
   stage={app,tiles,shade,roadDetails,shrubs,shadow,glints,leaves,dust};
   if(disposed){app.destroy(true);return;}
   sceneRef.current=stage;
   drawFrame(stage,latestPlan.current);
   continueRender(renderHandle);
  })().catch(e=>{if(!disposed)cancelRender(e instanceof Error?e:new Error(String(e)));});
  return ()=>{
   disposed=true;sceneRef.current=null;
   if(stage)stage.app.destroy(true);
  };
 },[renderHandle]);
 return <div ref={host} data-pixi-world="real-animated-depth-shade-and-road-motion"
  style={{position:'absolute',left:0,top:0,width:360,height:640,
   overflow:'hidden',imageRendering:'pixelated',pointerEvents:'none'}}/>;
};
