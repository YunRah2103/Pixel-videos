import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {V5WorldPlane} from './WorldV5';
import {V5AtmospherePlane} from './AtmosphereV5';
import {V5StoryPlane} from './StoryV5';
import {getV5Motion} from './MotionV5.mjs';

/**
 * SUNSET HARBOR V5 FINAL — true three-agent native-picture integration.
 * All 17 planes are their own authored V5 source, 360×640.
 * The director owns exactly ONE external depth/camera transform per plane.
 * No V4 art/story and no stand-in layered stills.
 */
const W = 360, H = 640;
type Kind = 'world'|'atmosphere'|'story';
type Plane = {
  id:string;kind:Kind;plane:string;depth:number;
};
/** Occlusion order is intentional: water behind docks; actors on paving. */
const STACK:Plane[] = [
  {id:'sky',kind:'atmosphere',plane:'sky',depth:.13},
  {id:'clouds',kind:'atmosphere',plane:'clouds',depth:.16},
  {id:'birds',kind:'story',plane:'birds',depth:.28},
  {id:'far',kind:'world',plane:'far',depth:.28},
  {id:'air',kind:'atmosphere',plane:'air',depth:.29},
  {id:'water',kind:'atmosphere',plane:'water',depth:.69},
  {id:'reflections',kind:'atmosphere',plane:'reflections',depth:.69},
  {id:'waterInteraction',kind:'story',plane:'waterInteraction',depth:.61},
  {id:'architecture',kind:'world',plane:'architecture',depth:.51},
  {id:'harbor',kind:'world',plane:'harbor',depth:.63},
  {id:'lighting',kind:'atmosphere',plane:'lighting',depth:.55},
  {id:'boat',kind:'story',plane:'boat',depth:.61},
  {id:'promenade',kind:'world',plane:'promenade',depth:.96},
  {id:'characters',kind:'story',plane:'characters',depth:1.02},
  {id:'cat',kind:'story',plane:'cat',depth:1.02},
  {id:'foreground',kind:'world',plane:'foreground',depth:1.19},
  {id:'foregroundLife',kind:'story',plane:'foregroundLife',depth:1.19},
];

const renderPlane = (p:Plane,frame:number,motion:any) => {
  const dx=motion.cameraX*p.depth,dy=motion.cameraY*p.depth;
  const zoom=1+(motion.cameraZoom-1)*p.depth;
  const style:React.CSSProperties={
    position:'absolute',left:0,top:0,width:W,height:H,
    transform:`translate(${dx.toFixed(3)}px,${dy.toFixed(3)}px) scale(${zoom.toFixed(5)})`,
    transformOrigin:'50% 46%',pointerEvents:'none',imageRendering:'pixelated'
  };
  return <div key={p.id} data-v5-final-plane={p.id} style={style}>
    {p.kind==='atmosphere'
      ? <V5AtmospherePlane frame={frame} motion={motion} plane={p.plane as any}/>
      : p.kind==='story'
      ? <V5StoryPlane frame={frame} motion={motion} plane={p.plane as any}/>
      : <V5WorldPlane frame={frame} motion={{...motion,disableWorldParallax:true}} plane={p.plane as any}/>}
  </div>;
};

export const SunsetHarborV5Final:React.FC=()=>{
  const frame=useCurrentFrame();
  const motion=getV5Motion(frame);
  return <AbsoluteFill style={{
    width:W,height:H,overflow:'hidden',backgroundColor:'#183a53',imageRendering:'pixelated'
  }}>
    {STACK.map(p=>renderPlane(p,frame,motion))}
  </AbsoluteFill>;
};
