import type {Trade} from './journalTypes';
/** Current floating values grouped by entry day; never a historical daily return. */
export function calendarPositions(positions:Trade[]){
 const days=new Map<string,{count:number;pnl:number;known:boolean}>();
 for(const t of positions){if(t.status!=='open'||!Number.isFinite(t.opened_at))continue;const day=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Manila',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(t.opened_at*1000));const row=days.get(day)||{count:0,pnl:0,known:true};row.count++;if(t.floating_pnl!=null&&Number.isFinite(t.floating_pnl))row.pnl+=t.floating_pnl;else row.known=false;days.set(day,row)}return days;
}
