/**
 * Native-pixel cinematic grammar: shots, camera/parallax and meaningful changes.
 * No implicit randomness or time-dependent motion.
 */
export const SHOTS=Object.freeze([
 {id:'instant-hook',start:0,end:55,frame:'low-reveal',speed:1.65,heroX:49,heroY:219,close:1,focus:'car enters from left'},
 {id:'scenery-passes',start:55,end:128,frame:'tracking',speed:2.15,heroX:53,heroY:220,close:1,focus:'distinct foreground trees reveal speed'},
 {id:'detail-beat',start:128,end:180,frame:'close-side',speed:1.2,heroX:38,heroY:225,close:1.25,focus:'wheel bounce/side view close-up'},
 {id:'big-reveal',start:180,end:268,frame:'wide-movement',speed:2.65,heroX:62,heroY:217,close:.91,focus:'different biome opens at crest'},
 {id:'payoff',start:268,end:360,frame:'sunset-run',speed:1.8,heroX:56,heroY:221,close:1.04,focus:'memorable last composition'}
]);
export const snap=(x)=>Math.round(x);
export function shotAt(frame){
 if(!Number.isInteger(frame)||frame<0||frame>=360)throw Error('frame must be 0..359');
 return SHOTS.find(x=>frame>=x.start&&frame<x.end);
}
export function timeline(frame){
 const shot=shotAt(frame);
 const beats=SHOTS.slice(0,SHOTS.indexOf(shot));
 let distance=0;
 for(const b of beats)distance+=(b.end-b.start)*b.speed;
 distance+=(frame-shot.start)*shot.speed;
 const phase=(frame-shot.start)/(shot.end-shot.start);
 const cameraX=snap(distance),heroX=snap(shot.heroX+(Math.sin((frame-shot.start)*.07)*1.5));
 const roadPx=snap(distance),wheelTurns=distance/(2*Math.PI*8);
 return {frame,shotId:shot.id,shotName:shot.frame,focus:shot.focus,
  localProgress:phase,stageCamera:cameraX,roadPx,wheelTurns,
  heroX,heroY:shot.heroY+snap(Math.sin(frame*.22)),zoom:shot.close,
  offsets:{sky:snap(distance*.02),mountains:snap(distance*.13),far:snap(distance*.27),
   middle:snap(distance*.52),road:snap(distance),foreground:snap(distance*1.3)}};
}
export function shotChangeReport(total=360){
 const ids=[];for(let f=0;f<total;f++)if(f===0||shotAt(f).id!==shotAt(f-1).id)ids.push({frame:f,shot:shotAt(f).id});
 return ids;
}
