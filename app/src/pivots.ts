import type {TechnicalBar} from './technicalIndicators';
export const pivotRows=['R3','R2','R1','P','S1','S2','S3'] as const;
export const pivotMethods=['Classic','Fibonacci','Camarilla','Woodie','DM'] as const;
type Levels=Record<typeof pivotRows[number],number|null>;
export function pivotLevels(previous:{open:number;high:number;low:number;close:number},currentOpen:number|null){
 const {open:o,high:h,low:l,close:c}=previous;
 if([o,h,l,c].some(x=>!Number.isFinite(x)||x<=0)||h<Math.max(o,c)||l>Math.min(o,c)||h<l)return null;
 const p=(h+l+c)/3,r=h-l,w=currentOpen!==null&&Number.isFinite(currentOpen)&&currentOpen>0?(h+l+2*currentOpen)/4:null;
 const x=c===o?h+l+2*c:c>o?2*h+l+c:2*l+h+c;
 const levels:Record<typeof pivotMethods[number],Levels>={
 Classic:{R3:p+2*r,R2:p+r,R1:2*p-l,P:p,S1:2*p-h,S2:p-r,S3:p-2*r},
 Fibonacci:{R3:p+r,R2:p+.618*r,R1:p+.382*r,P:p,S1:p-.382*r,S2:p-.618*r,S3:p-r},
 Camarilla:{R3:c+1.1*r/4,R2:c+1.1*r/6,R1:c+1.1*r/12,P:p,S1:c-1.1*r/12,S2:c-1.1*r/6,S3:c-1.1*r/4},
 Woodie:{R3:w===null?null:h+2*(w-l),R2:w===null?null:w+r,R1:w===null?null:2*w-l,P:w,S1:w===null?null:2*w-h,S2:w===null?null:w-r,S3:w===null?null:l-2*(h-w)},
 DM:{R3:null,R2:null,R1:x/2-l,P:x/4,S1:x/2-h,S2:null,S3:null}};
 return levels;
}
export function dailyPivots(input:TechnicalBar[],interval:number,source:'sample'|'exness'){
 const unavailable=(reason:string)=>({levels:null,previousDay:null as number|null,currentDay:null as number|null,reason});
 if(!input.length||interval<=0||86400%interval!==0)return unavailable('Waiting for a complete previous UTC day.');
 if(input.some((b,i)=>!Number.isInteger(b.time)||[b.open,b.high,b.low,b.close].some(x=>!Number.isFinite(x)||x<=0)||b.high<Math.max(b.open,b.close)||b.low>Math.min(b.open,b.close)||b.high<b.low||(i>0&&b.time<=input[i-1].time)))return unavailable('Invalid candle data; pivots unavailable.');
 const currentDay=Math.floor(input.at(-1)!.time/86400)*86400,previousDay=currentDay-86400;
 const b=input.filter(x=>x.time>=previousDay&&x.time<currentDay&&(x.closed===true||(source==='sample'&&x.closed!==false)));
 const complete=b.length===86400/interval&&b.every((x,i)=>x.time===previousDay+i*interval);
 if(!complete)return unavailable('Previous UTC day is incomplete in this feed; pivots unavailable.');
 const open=input.find(x=>x.time===currentDay)?.open??null;
 const levels=pivotLevels({open:b[0].open,high:Math.max(...b.map(x=>x.high)),low:Math.min(...b.map(x=>x.low)),close:b.at(-1)!.close},open);
 return{levels,previousDay,currentDay,reason:open===null?'Current UTC opening candle missing; Woodie unavailable.':''};
}

// Daily broker bars define complete trading sessions, including gold's weekend/session breaks.
export function dailySessionPivots(input:TechnicalBar[]){
 const unavailable=(reason:string)=>({levels:null,previousDay:null as number|null,currentDay:null as number|null,reason});
 if(input.length<2)return unavailable('Waiting for broker daily candles. Reload the updated quote indicator.');
 if(input.some((b,i)=>!Number.isInteger(b.time)||b.time%86400!==0||[b.open,b.high,b.low,b.close].some(x=>!Number.isFinite(x)||x<=0)||b.high<Math.max(b.open,b.close)||b.low>Math.min(b.open,b.close)||b.high<b.low||(i>0&&b.time<=input[i-1].time)))return unavailable('Invalid broker daily candles; pivots unavailable.');
 const current=input.at(-1)!,previous=input.at(-2)!;
 if(current.closed!==false||previous.closed!==true)return unavailable('Waiting for a confirmed previous daily session and current session open.');
 const levels=pivotLevels(previous,current.open);
 return {levels,previousDay:previous.time,currentDay:current.time,reason:'Calculated from the previous completed broker daily session. Session breaks and weekends are not filled. Woodie uses the current session open.'};
}
