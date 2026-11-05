import type {Trade} from './journalTypes';
export type BreakdownBy='symbol'|'side'|'time';
const clock=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Manila',hour:'2-digit',hourCycle:'h23'});
export function performanceBreakdown(trades:Trade[],by:BreakdownBy){
 const groups=new Map<string,{label:string;count:number;wins:number;losses:number;flat:number;cents:number}>();
 for(const t of trades){if(t.status!=='closed'||!Number.isFinite(t.pnl))continue;
 const hour=Number.isFinite(t.opened_at)?Number(clock.format(new Date(t.opened_at*1000))):NaN;
 const label=by==='symbol'?t.symbol||'Unknown':by==='side'?(t.side==='buy'?'Buy':t.side==='sell'?'Sell':'Unknown'):!Number.isFinite(hour)?'Unknown entry time':hour<6?'00:00–05:59':hour<12?'06:00–11:59':hour<18?'12:00–17:59':'18:00–23:59';
 const row=groups.get(label)||{label,count:0,wins:0,losses:0,flat:0,cents:0};row.count++;row.cents+=Math.round(t.pnl!*100);if(t.pnl!>0)row.wins++;else if(t.pnl!<0)row.losses++;else row.flat++;groups.set(label,row);
 }return [...groups.values()].sort((a,b)=>by==='time'?a.label.localeCompare(b.label):b.cents-a.cents||a.label.localeCompare(b.label));
}
