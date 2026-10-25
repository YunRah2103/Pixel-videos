/**
 * A production PixiJS v8 canvas, not a dependency smoke test.
 *
 * Pixi draws the ACTUAL six authored countryside PNG textures on six real
 * TilingSprites, moves their tilePosition on Remotion's frame, and draws tiny
 * native-pixel leaf glints / an axle-aware road contact shadow with Graphics.
 * The hand-authored animated hero car remains a separate foreground React
 * layer so Agents 1/2 can safely replace either art asset.
 */
import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {cancelRender,continueRender,delayRender,staticFile} from 'remotion';
import type {Application,Graphics,TilingSprite} from 'pixi.js';
import type {CountrysideMotion} from './DrivingMotion';
import {PIXI_WORLD_LAYERS,planPixiWorld,type PixiWorldLayer,type PixiWorldPlan} from './PixiWorldPlan';

type PixiStage = {
  app:Application;
  tiles:Map<PixiWorldLayer,TilingSprite>;
  shadows:Graphics;
  glints:Graphics;
};
function drawFrame(stage:PixiStage,plan:PixiWorldPlan):void{
  for(const layer of plan.layers){
    const tile=stage.tiles.get(layer.name);
    if(!tile)throw Error('Missing required PixiJS art plane: '+layer.name);
    // PixiJS is the actual parallax animator; every shift snaps to a native px.
    tile.tilePosition.x=layer.tileX;
    tile.tilePosition.y=0;
  }
  stage.shadows.clear()
    .rect(plan.contactShadow.x,plan.contactShadow.y,plan.contactShadow.width,2)
    .fill({color:0x182B30,alpha:plan.contactShadow.alpha})
    .rect(plan.contactShadow.x+19,plan.contactShadow.y+2,105,1)
    .fill({color:0x2C4944,alpha:plan.contactShadow.alpha*.58});
  stage.glints.clear();
  for(const light of plan.lightPixels){
    stage.glints.rect(light.x,light.y,2,1)
      .fill({color:light.color,alpha:light.alpha});
  }
  // Explicit one-frame render: never run Pixi's wall-clock ticker in Remotion.
  stage.app.renderer.render({container:stage.app.stage});
}
export const PixiCountrysideWorld:React.FC<{frame:number;motion:CountrysideMotion}> = ({
  frame,motion,
})=>{
  const host=useRef<HTMLDivElement>(null);
  const sceneRef=useRef<PixiStage|null>(null);
  const plan=planPixiWorld(frame,motion);
  const latestPlan=useRef(plan);
  const [renderHandle]=useState(()=>delayRender('Initialize actual PixiJS countryside scene and PNG textures', {timeoutInMilliseconds:60000}));

  // Runs before Chrome's screenshot on random-access frame seeks.
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
      if(!host.current)throw Error('Missing PixiJS canvas host');
      host.current.appendChild(app.canvas);
      const tiles=new Map<PixiWorldLayer,TilingSprite>();
      for(const layer of PIXI_WORLD_LAYERS){
        // These files are Agent 1's ORIGINAL handcrafted V2 native PNGs.
        const texture=await pixi.Assets.load(staticFile('countryside/world/'+layer.path));
        if(disposed){app.destroy(true);return;}
        texture.source.scaleMode='nearest';
        const sprite=new pixi.TilingSprite({
          texture,width:360,height:layer.height,
        });
        sprite.x=0;
        sprite.y=layer.y;
        sprite.roundPixels=true;
        tiles.set(layer.name,sprite);
        app.stage.addChild(sprite);
      }
      const shadows=new pixi.Graphics(),glints=new pixi.Graphics();
      app.stage.addChild(shadows);
      app.stage.addChild(glints);
      stage={app,tiles,shadows,glints};
      if(disposed){app.destroy(true);return;}
      sceneRef.current=stage;
      drawFrame(stage,latestPlan.current);
      // Failure to initialize/render Pixi means Remotion MUST fail, not fall
      // back to DOM static scenery or secretly produce a placeholder proof.
      continueRender(renderHandle);
    })().catch(e=>{if(!disposed)cancelRender(e instanceof Error?e:new Error(String(e)));});
    return ()=>{
      disposed=true;
      sceneRef.current=null;
      if(stage)stage.app.destroy(true);
    };
  },[renderHandle]);

  return <div ref={host} data-pixi-world="six-original-tiling-sprites"
    style={{position:'absolute',left:0,top:0,width:360,height:640,
      overflow:'hidden',imageRendering:'pixelated',pointerEvents:'none'}}/>;
};
