/** Frame-exact 2D rig helpers for sprite artists and Remotion films.
 * Pure functions: no wall clock, no noise, no nonseeded randomness.
 */
const finiteFrame=(frame)=>{if(!Number.isInteger(frame)||frame<0)throw Error('frame must be a nonnegative integer');};
const wave=(f,p)=>Math.sin((f%p)*2*Math.PI/p);
export function walkPose(frame,{cycle=16,stride=3}={}){
 finiteFrame(frame);
 if(cycle<2||stride<0)throw Error('invalid walk parameters');
 const phase=frame*2*Math.PI/cycle;
 return {leftFootX:Math.round(Math.sin(phase)*stride),rightFootX:Math.round(Math.sin(phase+Math.PI)*stride),
  leftFootY:-Math.max(0,Math.round(Math.cos(phase)*stride/2)),rightFootY:-Math.max(0,Math.round(Math.cos(phase+Math.PI)*stride/2)),
  hipY:Math.round(Math.cos(phase*2)),headTilt:Math.sin(phase)*0.04,
  leftArm:Math.sin(phase+Math.PI)*.3,rightArm:Math.sin(phase)*.3};
}
export function carPose(frame,{speed=1,roadRoughness=1}={}){
 finiteFrame(frame);
 if(!Number.isFinite(speed)||speed<0||!Number.isFinite(roadRoughness)||roadRoughness<0)throw Error('bad car settings');
 return {bodyY:Math.round(wave(frame,21)*roadRoughness),bodyPitch:wave(frame,34)*.012*roadRoughness,
  wheelAngle:(frame*speed*.18)%(2*Math.PI),suspensionFront:Math.sin(frame*.29)*roadRoughness,
  suspensionRear:Math.sin(frame*.29-1)*roadRoughness};
}
export function boatPose(frame,{swell=2}={}){
 finiteFrame(frame);
 return {x:Math.round(frame*.25),y:Math.round(wave(frame,80)*swell),roll:wave(frame,87)*.05,
  sailBend:wave(frame,56)*.075,wakeStrength:.5+.4*(.5+.5*wave(frame,47))};
}
export function animalPose(frame,{cycle=20}={}){
 finiteFrame(frame);
 const t=frame%cycle;
 return {frontPawY:Math.max(0,Math.round(wave(frame,cycle)*2)),rearPawY:Math.max(0,Math.round(-wave(frame,cycle)*2)),
  tailAngle:wave(frame,36)*.26,eyeClosed:t===0||t===1};
}
export function clothPose(frame,{phase=0,wind=1}={}){
 finiteFrame(frame);
 return {x:Math.round(wave(frame+phase,65)*2*wind),y:Math.round(wave(frame+phase,48)*wind),
  angle:wave(frame+phase,67)*.06*wind};
}
export function frameSlot(frame,{count,hold=4,start=0}){
 finiteFrame(frame);
 if(!Number.isInteger(count)||count<1||!Number.isInteger(hold)||hold<1)throw Error('bad sprite sheet config');
 return (Math.floor(frame/hold)+start%count+count)%count;
}
export function rigPose(rig,frame,settings={}){
 const actions={walk:walkPose,car:carPose,boat:boatPose,animal:animalPose,cloth:clothPose};
 if(!Object.hasOwn(actions,rig))throw Error('Unknown animation rig '+rig);
 return actions[rig](frame,settings);
}
