import React from 'react';
import {Img,staticFile} from 'remotion';
/** Original 360x640 canvas, no independent animation. The motion agent owns offsets. */
export type CountrysideLayer='sky'|'farTrees'|'midTrees'|'nearTrees'|'verge'|'road';
export const COUNTRYSIDE_WORLD_TILES={
 sky:{width:360,height:480,y:0,scrolling:false},
 farTrees:{width:720,height:300,y:180,scrolling:true},
 midTrees:{width:840,height:265,y:215,scrolling:true},
 nearTrees:{width:960,height:235,y:245,scrolling:true},
 verge:{width:384,height:160,y:480,scrolling:true},
 road:{width:384,height:160,y:480,scrolling:true},
} as const;
export type CountrysideWorldProps={frame:number;layer:CountrysideLayer;offsetX?:number};
export function wrapWorldOffset(offsetX:number,width:number){
 if(!Number.isFinite(offsetX)||!Number.isInteger(width)||width<=0)throw Error('invalid offset or width');
 return ((Math.round(offsetX)%width)+width)%width;
}
/** Frame-seek safe, clipped PNG tiling at integer native pixel positions. */
export const CountrysideWorldLayer:React.FC<CountrysideWorldProps>=({frame,layer,offsetX=0})=>{
 if(!Number.isInteger(frame)||frame<0)throw Error('frame must be nonnegative integer');
 const t=COUNTRYSIDE_WORLD_TILES[layer];
 const src=staticFile('countryside/world/'+layer+'.png');
 const style:React.CSSProperties={position:'absolute',top:0,width:t.width,height:t.height,
   imageRendering:'pixelated',maxWidth:'none',pointerEvents:'none'};
 if(!t.scrolling)return <Img src={src} draggable={false} style={{...style,left:0,top:t.y}}/>;
 const shift=wrapWorldOffset(offsetX,t.width),x=shift-t.width;
 return <div style={{position:'absolute',top:t.y,left:0,width:360,height:t.height,
  overflow:'hidden',pointerEvents:'none'}}>
  {[0,1,2].map(i=><Img key={i} src={src} draggable={false}
    style={{...style,left:x+i*t.width}}/>)}
 </div>;
};
