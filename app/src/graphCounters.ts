// Display-only digit wheel. Every full ten steps returns to the exact label.
export function counterFrame(exact:string,phase:number){
 const step=Math.floor(Math.max(0,phase)),fraction=Math.max(0,phase)-step;
 const roll=(offset:number)=>exact.replace(/[0-9]/g,d=>String((Number(d)+offset)%10));
 return {current:roll(step%10),next:roll((step+1)%10),offset:fraction*12};
}
export function settleCounter(phase:number,target:number,dt:number){const next=phase+(target-phase)*(1-Math.exp(-12*Math.max(0,dt)));return Math.abs(target-next)<.02?target:next}
