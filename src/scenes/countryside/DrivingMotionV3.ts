/**
 * Countryside V3: visibly faster road travel and cinematic, pixel-locked
 * tracking. The V2 controller remains unchanged for Agent 4 compatibility.
 * A single integer-valued distance controls ALL Pixi layers and wheel poses.
 */
import {springFromRoad,type CountrysideMotion} from './DrivingMotion.ts';

const FPS=30,FRAMES=360;
const nearest=(v:number)=>Math.round(v);
const easing=(t:number)=>{const u=Math.max(0,Math.min(1,t));return u*u*(3-2*u);};
export const roadStepForFrame=(f:number):number=>{
 if(!Number.isInteger(f)||f<0)throw Error('invalid motion frame');
 const n=f%FRAMES;
 if(n<45)return 3;
 if(n<120)return Math.min(7,3+Math.floor((n-45)/17)+1);
 if(n<252)return 7;
 if(n<305)return 6;
 return 5;
};
export const getCinematicRoadTravel=(frame:number):number=>{
 if(!Number.isInteger(frame)||frame<0)throw Error('invalid motion frame');
 let distance=0;
 for(let i=0;i<frame%FRAMES;i++)distance+=roadStepForFrame(i);
 return distance;
};
export type CinematicMotion=CountrysideMotion&{
 velocityPx:number;
 foregroundTravelPx:number;
 shot:'wide'|'wheel-closeup';
};
/**
 * Exact arithmetic and bounded tracking. The road is the only speed clock.
 * No extra wheel counter; zero jitter from DOM transitions or timers.
 */
export function getCinematicMotion(frame:number,wheelRadiusPx:number):CinematicMotion{
 if(!Number.isInteger(frame)||frame<0||!Number.isFinite(wheelRadiusPx)||wheelRadiusPx<=0)
  throw Error('invalid frame or measured wheel radius');
 const f=frame%FRAMES,travel=getCinematicRoadTravel(frame),velocityPx=roadStepForFrame(frame);
 const carX=nearest(f<125
  ?152+54*easing(f/125)
  :f<260?206-9*easing((f-125)/135)
   :197-19*easing((f-260)/100));
 const frontSpringPx=springFromRoad(travel,carX+55);
 const rearSpringPx=springFromRoad(travel,carX-53);
 const bobY=Math.max(-1,Math.min(1,frontSpringPx+rearSpringPx));
 const shadowOpacity=Math.round((0.30-0.028*bobY)*100)/100;
 return {
  frame,cycleFrame:f,carX,bobY,frontSpringPx,rearSpringPx,shadowOpacity,
  roadTravelPx:travel,
  velocityPx,
  foregroundTravelPx:nearest(travel*1.3),
  wheelRotationTurns:travel/(2*Math.PI*wheelRadiusPx),
  offsets:{
    farTrees:-nearest(travel*.14),
    midTrees:-nearest(travel*.37),
    nearTrees:-nearest(travel*.77),
    verge:-nearest(travel*.93),
    road:-travel,
  },
  shot:f>=205&&f<271?'wheel-closeup':'wide',
 };
}
