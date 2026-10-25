/**
 * Countryside V3: native-pixel plans consumed by a REAL PixiJS v8 scene graph.
 * All transforms are functions of the Remotion frame. No ticker, CSS or RNG clock.
 */
import type {CountrysideMotion} from './DrivingMotion';

export const PIXI_WORLD_LAYERS = [
  {name:'sky',path:'sky.png',width:360,height:480,y:0},
  {name:'farTrees',path:'farTrees.png',width:720,height:300,y:180},
  {name:'midTrees',path:'midTrees.png',width:840,height:265,y:215},
  {name:'nearTrees',path:'nearTrees.png',width:960,height:235,y:245},
  {name:'road',path:'road.png',width:384,height:160,y:480},
  {name:'verge',path:'verge.png',width:384,height:160,y:480},
] as const;
export type PixiWorldLayer = typeof PIXI_WORLD_LAYERS[number]['name'];
type WorldOffsets = Record<Exclude<PixiWorldLayer,'sky'>,number>;
const mod=(n:number,m:number)=>((n%m)+m)%m;
const check=(x:number)=>{if(!Number.isInteger(x))throw Error('Pixi native pixel coordinate required');return x;};
export type PixiWorldPlan = {
  layers:ReadonlyArray<{name:PixiWorldLayer;tileX:number; y:number}>;
  lightPixels:ReadonlyArray<{x:number;y:number;alpha:number;color:number}>;
  contactShadow:{x:number;y:number;width:number;alpha:number};
  frame:number;
};
/** Leaves/light flecks move coherently with foreground foliage, not the camera. */
export function planPixiWorld(frame:number,motion:CountrysideMotion):PixiWorldPlan{
  if(!Number.isInteger(frame)||frame<0||frame!==motion.frame)throw Error('Stale world/motion frame');
  const offsets=motion.offsets as WorldOffsets;
  const layers=PIXI_WORLD_LAYERS.map(layer=>({
    name:layer.name,
    tileX:layer.name==='sky'?0:check(offsets[layer.name]),
    y:layer.y,
  }));
  // A tiny fixed set of quantised sunlit leaf clusters, carried by the world.
  // No diffuse bloom, anti-aliasing, translucent full-screen overlays or noise.
  const leafBases=[{x:32,y:359},{x:145,y:401},{x:278,y:339},
    {x:391,y:417},{x:526,y:371},{x:671,y:389},{x:817,y:348}];
  const lightPixels=leafBases.map((p,i)=>({
    x:check(mod(p.x+offsets.nearTrees,960)-0),
    y:check(p.y+((Math.floor(frame/14+i*3)%3)===0?-1:0)),
    alpha:[0.16,0.22,0.12][Math.floor(frame/11+i)%3],
    color:i%3===0?0xC1CF81:0x9FBD68,
  })).filter(p=>p.x>=0&&p.x<360);
  return {
    frame,layers,lightPixels,
    contactShadow:{x:check(motion.carX-73),y:494,width:146,alpha:motion.shadowOpacity},
  };
}
