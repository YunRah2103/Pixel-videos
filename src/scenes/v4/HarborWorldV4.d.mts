export interface HarborV4Motion {
 cameraX?:number;cameraY?:number;cameraZoom?:number;foliageSway?:number;
 waterPhase?:number;cloudDrift?:number;lightIntensity?:number;
}
export declare const HARBOR_V4_WIDTH:360,HARBOR_V4_HEIGHT:640;
export interface HarborV4Layers{
 sky:string;distant:string;architecture:string;
 harbourStructures:string;promenade:string;foreground:string;
}
export declare function renderHarborBaseLayers(frame:number,motion?:HarborV4Motion):HarborV4Layers;
