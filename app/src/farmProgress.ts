export const FARM_FACILITIES=[{name:'Greenhouse',threshold:1000},{name:'Chicken coop',threshold:2500},{name:'Grain silo',threshold:5000},{name:'Tractor garage',threshold:10000}];
type FarmDay={date:string;pnl:number;closed_count:number};
export function farmWeek(days:FarmDay[],date:string){
 const monday=new Date(date+'T00:00:00Z');monday.setUTCDate(monday.getUTCDate()-(monday.getUTCDay()+6)%7);
 const start=monday.toISOString().slice(0,10);monday.setUTCDate(monday.getUTCDate()+6);const end=monday.toISOString().slice(0,10);
 const rows=days.filter(d=>d.date>=start&&d.date<=date);const cents=rows.reduce((n,d)=>n+Math.round(d.pnl*100),0);
 const sorted=[...days].filter(d=>d.date<=date).sort((a,b)=>a.date.localeCompare(b.date));let week='',sum=0,peak=0,earned=0;
 for(const d of sorted){const t=new Date(d.date+'T00:00:00Z');t.setUTCDate(t.getUTCDate()-(t.getUTCDay()+6)%7);const key=t.toISOString().slice(0,10);if(key!==week){earned+=peak;week=key;sum=peak=0}sum+=Math.round(d.pnl*100);peak=Math.max(peak,sum)}earned+=peak;
 return {beds:2+Math.min(8,Math.floor(earned/50000)),earned:earned/100,start,end,pnl:cents/100,trades:rows.reduce((n,d)=>n+d.closed_count,0),partial:!days.some(d=>d.date===start),progress:1-Math.exp(-earned/500000)};
}
