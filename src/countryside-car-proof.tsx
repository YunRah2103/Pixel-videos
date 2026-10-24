import React from 'react';
import {Composition,registerRoot,useCurrentFrame} from 'remotion';
import {CarLayer} from './scenes/countryside/CarLayer';
const CarProof:React.FC=()=>{
 const frame=useCurrentFrame();
 return <div style={{position:'absolute',width:360,height:640,background:'#6DB6E5',imageRendering:'pixelated'}}>
  <div style={{position:'absolute',left:0,top:495,width:360,height:1,background:'#263E39',opacity:.55}}/>
  <CarLayer frame={frame}/>
 </div>;
};
registerRoot(()=><Composition id="CountrysideCarProof" component={CarProof}
 durationInFrames={120} fps={30} width={360} height={640}/>);