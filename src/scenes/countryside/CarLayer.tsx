import React from 'react';
import {Img, staticFile} from 'remotion';
export const CAR_NATIVE_WIDTH=156;
export const CAR_NATIVE_HEIGHT=63;
export const WHEEL_DIAMETER_PX=24;
export const WHEEL_RADIUS_PX=11.5;
export const WHEEL_POSE_COUNT=8;
export const CAR_WHEEL_CENTERS_X:readonly [number,number]=[35,120];
export const DEFAULT_ROAD_TRAVEL_PX_PER_FRAME=2.8;
export type CarLayerProps={
 frame:number;x?:number;wheelContactY?:number;wheelRotationTurns?:number;bobY?:number;
};
export function carRollAtFrame(frame:number, pxPerFrame=DEFAULT_ROAD_TRAVEL_PX_PER_FRAME){
 if(!Number.isInteger(frame)||frame<0)throw Error('Bad frame');
 return frame*pxPerFrame/(2*Math.PI*WHEEL_RADIUS_PX);
}
export function wheelPoseFromTurns(turns:number){
 if(!Number.isFinite(turns))throw Error('Bad wheel rotation');
 return Math.min(7,Math.floor((((turns%1)+1)%1)*8+1e-8));
}
/** Original native pixels only; no scenery, camera or CSS rotation. */
export const CarLayer:React.FC<CarLayerProps>=({
 frame,x=180,wheelContactY=495,wheelRotationTurns,bobY
})=>{
 const pose=wheelPoseFromTurns(wheelRotationTurns??carRollAtFrame(frame));
 const bounce=Math.round(bobY??0.6*Math.sin(frame*.17));
 return <div aria-label="Original red pixel-art coupe" style={{
  position:'absolute',left:Math.round(x)-78,top:Math.round(wheelContactY)+bounce-59,
  width:156,height:63,imageRendering:'pixelated',pointerEvents:'none'
 }}>
  {CAR_WHEEL_CENTERS_X.map(cx=><div key={cx} style={{
   position:'absolute',left:cx-12,top:35,width:24,height:24,
   overflow:'hidden',imageRendering:'pixelated'
  }}><Img src={staticFile('countryside/car/coupe-wheels-8.png')} style={{
   position:'absolute',left:-pose*24,top:0,width:192,height:24,
   maxWidth:'none',imageRendering:'pixelated'
  }}/></div>)}
  <Img src={staticFile('countryside/car/coupe-body.png')} style={{
   position:'absolute',left:0,top:0,width:156,height:63,imageRendering:'pixelated'
  }}/>
 </div>;
};