/**
 * Agent 3's isolated genuine-asset motion comparison proof.
 * Uses exact existing integrated authored tree and car PNGs. Not a final film.
 * The body moves ONLY 1 native px; wheel centres remain at fixed Y, independently.
 * No animation beyond the shared frame-derived pixel coordinate controller.
 */
import React from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame} from 'remotion';
import {COUNTRYSIDE_WHEEL_CONTACT_Y,getCountrysideMotion,wheelPoseIndex,AUTHOR_WHEEL_RADIUS_PX} from './DrivingMotion';
import {CountrysideWorldLayer} from './WorldLayers';

export const CountrysideMotionProof:React.FC=()=>{
 const frame=useCurrentFrame();
 const m=getCountrysideMotion(frame,AUTHOR_WHEEL_RADIUS_PX);
 const layers=['sky','farTrees','midTrees','nearTrees','verge','road'] as const;
 const carLeft=m.carX-78,carTop=COUNTRYSIDE_WHEEL_CONTACT_Y-59;
 const pose=wheelPoseIndex(m.wheelRotationTurns,8);
 const px:React.CSSProperties={imageRendering:'pixelated',pointerEvents:'none',maxWidth:'none'};
 return <AbsoluteFill style={{background:'#6DB6E5',overflow:'hidden',imageRendering:'pixelated'}}>
   {layers.map(layer=><CountrysideWorldLayer key={layer} frame={frame} layer={layer}
      offsetX={layer==='sky'?0:m.offsets[layer]}/>)}
   <Img src={staticFile('countryside/motion/contact-shadow.png')} draggable={false}
      style={{...px,position:'absolute',left:carLeft+7,top:COUNTRYSIDE_WHEEL_CONTACT_Y-3,
        width:142,height:7,opacity:m.shadowOpacity/.27}}/>
   <div style={{position:'absolute',left:carLeft,top:carTop,width:156,height:63,
      pointerEvents:'none',imageRendering:'pixelated'}}>
      {[35,120].map(cx=><div key={cx} style={{position:'absolute',left:cx-12,top:35,
       width:24,height:24,overflow:'hidden',imageRendering:'pixelated'}}>
       <Img src={staticFile('countryside/car/coupe-wheels-8.png')} draggable={false}
         style={{...px,position:'absolute',left:-pose*24,top:0,width:192,height:24}}/>
      </div>)}
      <Img src={staticFile('countryside/car/coupe-body.png')} draggable={false}
        style={{...px,position:'absolute',left:0,top:m.bobY,width:156,height:63}}/>
   </div>
 </AbsoluteFill>;
};
