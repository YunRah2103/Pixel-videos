/** Sprite sheets: indexed frames, pivots and deterministic frame choice. */
export function frameRectangle(sheet,frame,{fps=30,hold=1,loop=true}={}){
 if(!Number.isInteger(frame)||frame<0||sheet.frames<1||!sheet.frameWidth||!sheet.frameHeight)throw Error('invalid sprite animation');
 const n=loop?Math.floor(frame/hold)%sheet.frames:Math.min(sheet.frames-1,Math.floor(frame/hold));
 return {left:n*sheet.frameWidth,top:0,width:sheet.frameWidth,height:sheet.frameHeight,
  pivot:sheet.pivot??{x:0,y:0}};
}
export function screenAnchor(rect,screenX,screenY,scale=1){
 if(!Number.isInteger(scale)||scale<1||scale>8)throw Error('sprites must use integral native scale');
 return {left:Math.round(screenX-rect.pivot.x*scale),top:Math.round(screenY-rect.pivot.y*scale)};
}
