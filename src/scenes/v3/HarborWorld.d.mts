export interface HarborMotion {
 cameraX?:number;cameraY?:number;cameraZoom?:number;
 cloudDrift?:number;waterMotion?:number;foliage?:number;
 lightIntensity?:number;
}
export declare const HARBOR_WIDTH:360,HARBOR_HEIGHT:640;
export declare function renderHarborWorld(frame:number,motion?:HarborMotion):string;
