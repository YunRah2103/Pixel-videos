/** V2 car-only real Remotion proof; intentionally not the final countryside film. */
import React from 'react';
import {Composition,AbsoluteFill,useCurrentFrame,registerRoot} from 'remotion';
import {CarLayer,WHEEL_RADIUS_PX} from './scenes/countryside/CarLayer';
const CarV2Proof:React.FC=()=>{
 const frame=useCurrentFrame();
 const travel=frame*3;
 const offset=(x:number,width:number)=>((x-travel)%width+width)%width;
 return <AbsoluteFill style={{background:'#83bcca',overflow:'hidden',imageRendering:'pixelated'}}>
  <div style={{position:'absolute',top:445,left:0,width:360,height:43,background:'#719b70'}}/>
  <div style={{position:'absolute',top:474,left:0,width:360,height:14,background:'#627c49'}}/>
  {Array.from({length:8},(_,i)=>{
   const x=offset(i*85-frame,680)-80;
   return <React.Fragment key={i}>
    <div style={{position:'absolute',left:x,top:457,width:5,height:30,background:'#526a52'}}/>
    <div style={{position:'absolute',left:x-8,top:437,width:19,height:21,background:'#557b59'}}/>
    <div style={{position:'absolute',left:x-5,top:428,width:13,height:14,background:'#6f9968'}}/>
   </React.Fragment>;
  })}
  <div style={{position:'absolute',top:488,left:0,width:360,height:152,background:'#3e4b51'}}/>
  <div style={{position:'absolute',top:495,left:0,width:360,height:2,background:'#64747b'}}/>
  {Array.from({length:7},(_,i)=><div key={i} style={{
   position:'absolute',left:offset(i*90,630)-90,top:551,width:41,height:2,background:'#cec59f'
  }}/>)}
  <CarLayer frame={frame} wheelContactY={495} x={180} bobY={Math.round(.75*Math.sin(frame*Math.PI/15))}
   wheelRotationTurns={travel/(2*Math.PI*WHEEL_RADIUS_PX)}/>
 </AbsoluteFill>;
};
const Root:React.FC=()=> <Composition id="CountrysideCarV2Proof" component={CarV2Proof}
 width={360} height={640} durationInFrames={120} fps={30}/>;
registerRoot(Root);
