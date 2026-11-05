import type {Day} from './journalTypes';
// Keep one real baseline day before the first close; never project future results.
export function chartDays(days:Day[],today:string){
 const elapsed=days.filter(d=>d.date<=today).sort((a,b)=>a.date.localeCompare(b.date));
 const first=elapsed.findIndex(d=>d.closed_count>0);
 return first<0?elapsed:elapsed.slice(Math.max(0,first-1));
}
export function niceAxis(values:number[]){
 const lo=Math.min(0,...values),hi=Math.max(0,...values),range=hi-lo||1;
 const raw=range/4,power=10**Math.floor(Math.log10(raw)),fraction=raw/power;
 const step=(fraction<=1?1:fraction<=2?2:fraction<=2.5?2.5:fraction<=5?5:10)*power;
 const min=Math.floor(lo/step)*step,max=Math.ceil(hi/step)*step||step;
 const ticks=Array.from({length:Math.round((max-min)/step)+1},(_,i)=>Number((min+i*step).toPrecision(12)));
 return {min,max,ticks};
}
