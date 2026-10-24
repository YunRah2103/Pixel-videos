import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {
  COUNTRYSIDE_LAYER_SPEC,
  getCountrysideMotion,
  wheelPoseIndex,
  wrapTileOffset,
  type CountrysideMovingLayer,
} from './DrivingMotion';

/**
 * Technical motion proof ONLY; deliberately blocky debug stand-ins, NOT art.
 * Agent 4 replaces these with the real authored PNG car and world layers.
 * Native canvas 360x640. Every moving element has integer left/top.
 */
const palette = {
  sky: '#6DB6E5',
  far: '#6A9774',
  mid: '#4B8B56',
  near: '#2B7047',
  trunk: '#705542',
  grass: '#739D53',
  road: '#575E65',
  shade: '#444C55',
  lane: '#E4D49B',
  car: '#D84E3F',
  window: '#9ACBDD',
  wheel: '#26323B',
} as const;

const rect = (left: number, top: number, width: number, height: number, backgroundColor: string): React.CSSProperties => ({
  position: 'absolute', left: Math.round(left), top: Math.round(top),
  width: Math.round(width), height: Math.round(height), backgroundColor,
  imageRendering: 'pixelated',
});

const TechnicalTree: React.FC<{x:number;y:number;scale:number;kind:0|1|2;color:string}> = ({x,y,scale,kind,color}) => {
  const stemX = Math.round(20 * scale);
  const top = kind === 0 ? 6 : kind === 1 ? 13 : 0;
  return <div style={{position:'absolute',left:x,top:y,width:Math.ceil(54*scale),height:Math.ceil(100*scale)}}>
    <div style={rect(stemX, 35*scale, 8*scale, 65*scale, palette.trunk)}/>
    <div style={rect((kind === 1?5:0)*scale, top*scale, (kind === 2?46:49)*scale, 36*scale,color)}/>
    <div style={rect(7*scale,(top-7)*scale,35*scale,11*scale,color)}/>
    <div style={rect(11*scale,(top-15)*scale,26*scale,8*scale,color)}/>
  </div>;
};

const ScrollingTrees: React.FC<{layer:'farTrees'|'midTrees'|'nearTrees';offsetX:number}> = ({layer,offsetX}) => {
  const spec = COUNTRYSIDE_LAYER_SPEC[layer], tileWidth = spec.periodPx;
  const x0 = wrapTileOffset(offsetX,tileWidth);
  const settings = layer === 'farTrees'
    ? {y:356,s:.70,color:palette.far}
    : layer === 'midTrees'
    ? {y:338,s:1.03,color:palette.mid}
    : {y:324,s:1.38,color:palette.near};
  return <AbsoluteFill style={{overflow:'hidden'}}>
    {Array.from({length:4},(_,tile) => <React.Fragment key={tile}>
      <TechnicalTree x={x0+tile*tileWidth+8} y={settings.y} scale={settings.s} kind={0} color={settings.color}/>
      <TechnicalTree x={x0+tile*tileWidth+Math.round(tileWidth*.52)} y={settings.y+11} scale={settings.s*.83} kind={tile % 2 ? 1 : 2} color={settings.color}/>
    </React.Fragment>)}
  </AbsoluteFill>;
};

const ScrollingRoad: React.FC<{offsetX:number}> = ({offsetX}) => {
  const roadPhase = wrapTileOffset(offsetX,COUNTRYSIDE_LAYER_SPEC.road.periodPx);
  return <AbsoluteFill>
    <div style={rect(0,480,360,95,palette.road)}/>
    <div style={rect(0,573,360,67,palette.grass)}/>
    {Array.from({length:16},(_,i)=> <div key={i} style={rect(roadPhase+i*36,526,18,3,palette.lane)}/>)}
    <div style={rect(0,569,360,4,palette.shade)}/>
  </AbsoluteFill>;
};

const ScrollingVerge: React.FC<{offsetX:number}> = ({offsetX}) => {
  const pos = wrapTileOffset(offsetX,COUNTRYSIDE_LAYER_SPEC.verge.periodPx);
  return <AbsoluteFill>
    <div style={rect(0,458,360,22,palette.grass)}/>
    {Array.from({length:8},(_,i)=> <div key={i} style={rect(pos+i*45,467+(i%2)*4,10,3,palette.mid)}/>)}
  </AbsoluteFill>;
};

const MotionCar: React.FC<{x:number;bobY:number;turns:number}> = ({x,bobY,turns}) => {
  // Two road-touching tyres: hub pattern changes pose but outer silhouette does not.
  const pose = wheelPoseIndex(turns,8), angle = (2*Math.PI*pose)/8;
  const dotX = Math.round(Math.cos(angle)*5), dotY = Math.round(Math.sin(angle)*5);
  const left = x-76;
  return <AbsoluteFill>
    <div style={rect(left+11,456+bobY,131,26,palette.car)}/>
    <div style={rect(left+38,438+bobY,68,21,palette.car)}/>
    <div style={rect(left+48,443+bobY,47,11,palette.window)}/>
    <div style={rect(left+2,465+bobY,14,10,palette.car)}/>
    <div style={rect(left+137,462+bobY,13,10,palette.car)}/>
    {[left+28,left+120].map((centerX,i)=><React.Fragment key={i}>
      <div style={rect(centerX-10,475,20,20,palette.wheel)}/>
      <div style={rect(centerX-6,479,12,12,palette.shade)}/>
      <div style={rect(centerX-2,483,4,4,palette.lane)}/>
      <div style={rect(centerX+dotX-2,485+dotY-2,4,4,palette.window)}/>
    </React.Fragment>)}
  </AbsoluteFill>;
};

export const CountrysideMotionProof: React.FC = () => {
  const frame = useCurrentFrame();
  const m = getCountrysideMotion(frame);
  return <AbsoluteFill style={{backgroundColor:palette.sky,overflow:'hidden',imageRendering:'pixelated',fontFamily:'monospace'}}>
    <ScrollingTrees layer="farTrees" offsetX={m.offsets.farTrees}/>
    <ScrollingTrees layer="midTrees" offsetX={m.offsets.midTrees}/>
    <ScrollingTrees layer="nearTrees" offsetX={m.offsets.nearTrees}/>
    <ScrollingVerge offsetX={m.offsets.verge}/>
    <ScrollingRoad offsetX={m.offsets.road}/>
    <MotionCar x={m.carX} bobY={m.bobY} turns={m.wheelRotationTurns}/>
    <div style={{position:'absolute',top:18,left:16,color:'#263E39',fontSize:13,fontWeight:900,whiteSpace:'pre'}}>
      MOTION PROOF - NOT FINAL ART
    </div>
    <div style={{position:'absolute',top:42,left:16,color:'#263E39',fontSize:11,whiteSpace:'pre'}}>
      {String(frame).padStart(3,'0')}f  road {m.roadTravelPx}px  wheel {m.wheelRotationTurns.toFixed(2)}t
    </div>
    <div style={{position:'absolute',top:60,left:16,color:'#263E39',fontSize:11}}>
      pixel snapped / no camera / 12s loop
    </div>
  </AbsoluteFill>;
};
