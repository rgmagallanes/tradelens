export function rangeMonths(start:string,end:string){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(start)||!/^\d{4}-\d{2}-\d{2}$/.test(end)||start>end)return [];
 const a=new Date(start+'T00:00:00Z'),b=new Date(end+'T00:00:00Z');if(!Number.isFinite(+a)||!Number.isFinite(+b)||a.toISOString().slice(0,10)!==start||b.toISOString().slice(0,10)!==end)return [];
 a.setUTCDate(1);const months:string[]=[];while(a<=b&&months.length<=12){months.push(a.toISOString().slice(0,7));a.setUTCMonth(a.getUTCMonth()+1)}return months.length>12?[]:months;
}
export function weekStart(today:string){const date=new Date(today+'T00:00:00Z');date.setUTCDate(date.getUTCDate()-(date.getUTCDay()+6)%7);return date.toISOString().slice(0,10)}
export function monthEnd(month:string){return new Date(Date.UTC(Number(month.slice(0,4)),Number(month.slice(5,7)),0)).toISOString().slice(0,10)}
