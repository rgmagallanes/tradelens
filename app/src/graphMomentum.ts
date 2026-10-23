export type Spin={yaw:number;pitch:number};
export function releaseSpin(yawDistance:number,pitchDistance:number):Spin{
 const length=Math.hypot(yawDistance,pitchDistance*180/Math.PI);if(length<2)return {yaw:0,pitch:0};
 return {yaw:Math.sign(yawDistance)*Math.min(72,Math.abs(yawDistance)*1.2),pitch:Math.sign(pitchDistance)*Math.min(1.1,Math.abs(pitchDistance)*1.4)};
}
export function advanceSpin(spin:Spin,dt:number){
 const decay=Math.exp(-1.4*Math.max(0,dt)),travel=(1-decay)/1.4;
 return {yaw:spin.yaw*decay,pitch:spin.pitch*decay,deltaYaw:spin.yaw*travel,deltaPitch:spin.pitch*travel};
}
