export type Spin={yaw:number;pitch:number};
export function releaseSpin(yawDistance:number,pitchDistance:number,velocity:Spin={yaw:0,pitch:0}):Spin{
 const length=Math.hypot(yawDistance,pitchDistance*180/Math.PI);if(length<2)return {yaw:0,pitch:0};
 return {yaw:Math.max(-72,Math.min(72,yawDistance*1.2+velocity.yaw*.28)),pitch:Math.max(-1.1,Math.min(1.1,pitchDistance*1.4+velocity.pitch*.28))};
}
export function advanceSpin(spin:Spin,dt:number){
 const decay=Math.exp(-1.4*Math.max(0,dt)),travel=(1-decay)/1.4;
 return {yaw:spin.yaw*decay,pitch:spin.pitch*decay,deltaYaw:spin.yaw*travel,deltaPitch:spin.pitch*travel};
}

// Exponentially forget the last pointer movement while the pointer rests.
export function freshSpin(velocity:Spin,elapsed:number):Spin{
 const weight=Math.exp(-Math.max(0,elapsed)/.09);
 return {yaw:velocity.yaw*weight,pitch:velocity.pitch*weight};
}
