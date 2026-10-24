import React from 'react';
import {Img, staticFile} from 'remotion';

/** Countryside Drive V2 hero asset: true native-resolution hand-authored pixel sprite. */
export const CAR_NATIVE_WIDTH=192;
export const CAR_NATIVE_HEIGHT=80;
export const WHEEL_DIAMETER_PX=32;
export const WHEEL_RADIUS_PX=15.5;
export const WHEEL_POSE_COUNT=8;
export const CAR_WHEEL_CENTERS_X:readonly [number,number]=[43,151];
export const DEFAULT_ROAD_TRAVEL_PX_PER_FRAME=3;
export type CarLayerProps={
 frame:number;x?:number;wheelContactY?:number;wheelRotationTurns?:number;bobY?:number;
};

export function carRollAtFrame(frame:number,pxPerFrame=DEFAULT_ROAD_TRAVEL_PX_PER_FRAME){
 if(!Number.isInteger(frame)||frame<0)throw Error('Bad frame');
 return frame*pxPerFrame/(2*Math.PI*WHEEL_RADIUS_PX);
}
export function wheelPoseFromTurns(turns:number){
 if(!Number.isFinite(turns))throw Error('Bad wheel rotation');
 return Math.min(7,Math.floor((((turns%1)+1)%1)*WHEEL_POSE_COUNT+1e-8));
}

/**
 * Centre x defaults to 180px in the native 360px scene.
 * Wheel sprites are independently grounded; bobY affects body only.
 * Wheel top at local Y=46, bottom at Y=78 = wheelContactY.
 * CarLayer consumes wheelRotationTurns from the ONE motion controller.
 */
export const CarLayer:React.FC<CarLayerProps>=({
 frame,x=180,wheelContactY=495,wheelRotationTurns,bobY=0
})=>{
 const pose=wheelPoseFromTurns(wheelRotationTurns??carRollAtFrame(frame));
 const bodyBob=Math.max(-1,Math.min(1,Math.round(bobY)));
 return <div aria-label="Original hand-drawn sport coupe, pixel-art edition 2" style={{
  position:'absolute',left:Math.round(x)-96,top:Math.round(wheelContactY)-78,
  width:192,height:80,imageRendering:'pixelated',pointerEvents:'none'
 }}>
  {/* Three stepped pixel contact-shadow bands, behind both wheels, zero blur. */}
  <div style={{position:'absolute',left:20,top:77,width:155,height:2,background:'#24323b'}}/>
  <div style={{position:'absolute',left:37,top:79,width:123,height:1,background:'#2e403f'}}/>
  {CAR_WHEEL_CENTERS_X.map(cx=><div key={cx} style={{
   position:'absolute',left:cx-16,top:46,width:32,height:32,
   overflow:'hidden',imageRendering:'pixelated'
  }}><Img src={staticFile('countryside/car/coupe-v2-wheels-8.png')} style={{
   position:'absolute',left:-pose*32,top:0,width:256,height:32,
   maxWidth:'none',imageRendering:'pixelated'
  }}/></div>)}
  <Img src={staticFile('countryside/car/coupe-v2-body.png')} style={{
   position:'absolute',left:0,top:bodyBob,width:192,height:80,
   imageRendering:'pixelated'
  }}/>
 </div>;
};