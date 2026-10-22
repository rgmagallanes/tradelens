import type {Day} from './journalTypes';
/** Monday–Sunday calendar rows; boundary rows contain visible-month days only. */
export function calendarWeeks(days:Day[],offset:number){
 const rows=Array.from({length:Math.ceil((offset+days.length)/7)},(_,i)=>({number:i+1,days:[] as Day[],pnl:0,trades:0,activeDays:0}));
 days.forEach((day,i)=>rows[Math.floor((offset+i)/7)].days.push(day));
 for(const row of rows){row.pnl=row.days.reduce((n,d)=>n+Math.round(d.pnl*100),0)/100;row.trades=row.days.reduce((n,d)=>n+d.closed_count,0);row.activeDays=row.days.filter(d=>d.closed_count>0).length;}
 return rows;
}
