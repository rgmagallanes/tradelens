// Keep punctuation and leading places stationary; roll decimals or the final integer group.
export function counterParts(exact:string){
 const decimal=exact.lastIndexOf('.');
 const digits=exact.match(/[0-9]+$/)?.[0]||'';
 const length=decimal>=0?digits.length:Math.min(3,digits.length);
 return {prefix:exact.slice(0,exact.length-length),suffix:exact.slice(exact.length-length)};
}
// Display-only digit wheel. Every full ten steps returns to the exact label.
export function counterFrame(exact:string,phase:number){
 const step=Math.floor(Math.max(0,phase)),fraction=Math.max(0,phase)-step;
 const {prefix,suffix}=counterParts(exact);
 const roll=(offset:number)=>suffix.replace(/[0-9]/g,d=>String((Number(d)+offset)%10));
 return {prefix,current:prefix+roll(step%10),next:prefix+roll((step+1)%10),suffix:roll(step%10),nextSuffix:roll((step+1)%10),offset:fraction*12};
}
export function settleCounter(phase:number,target:number,dt:number){const next=phase+(target-phase)*(1-Math.exp(-12*Math.max(0,dt)));return Math.abs(target-next)<.02?target:next}
