import type {Day,JournalData} from './journalTypes';
export type ReportPeriod='weekly'|'monthly'|'quarterly';
const iso=(d:Date)=>d.toISOString().slice(0,10);
export function reportRange(anchor:string,period:ReportPeriod){
 const d=new Date(anchor+'T00:00:00Z');let first:Date,last:Date;
 if(period==='weekly'){first=new Date(d);first.setUTCDate(d.getUTCDate()-(d.getUTCDay()+6)%7);last=new Date(first);last.setUTCDate(first.getUTCDate()+6)}
 else{const m=period==='quarterly'?Math.floor(d.getUTCMonth()/3)*3:d.getUTCMonth();first=new Date(Date.UTC(d.getUTCFullYear(),m,1));last=new Date(Date.UTC(d.getUTCFullYear(),m+(period==='quarterly'?3:1),0))}
 const months:string[]=[];let m=new Date(Date.UTC(first.getUTCFullYear(),first.getUTCMonth(),1));while(m<=last){months.push(iso(m).slice(0,7));m=new Date(Date.UTC(m.getUTCFullYear(),m.getUTCMonth()+1,1))}
 return {start:iso(first),end:iso(last),months};
}
const round=(n:number)=>Math.round(n*100)/100;
export function buildReport(snapshots:JournalData[],start:string,end:string){
 const days=snapshots.flatMap(s=>s.days).filter(d=>start<=d.date&&d.date<=end).sort((a,b)=>a.date.localeCompare(b.date));
 const trades=days.flatMap(d=>d.trades).filter(t=>t.status==='closed'&&t.closed_at!=null).sort((a,b)=>a.closed_at!-b.closed_at!||a.id.localeCompare(b.id));
 const wins=trades.filter(t=>t.pnl!>0),losses=trades.filter(t=>t.pnl!<0),positive=wins.reduce((s,t)=>s+t.pnl!,0),negative=-losses.reduce((s,t)=>s+t.pnl!,0);const initial=days[0]?.start_balance??0;
 let equity=initial,peak=initial,drawdown=0;for(const t of trades){equity=round(equity+t.pnl!);peak=Math.max(peak,equity);drawdown=Math.max(drawdown,peak-equity)}
 const active=days.filter(d=>d.closed_count);const pnl=round(trades.reduce((s,t)=>s+t.pnl!,0));
 return {start,end,timezone:'Asia/Manila',source:snapshots[0]?.source,days,trade_count:trades.length,wins:wins.length,losses:losses.length,breakeven:trades.length-wins.length-losses.length,pnl,start_balance:initial,end_balance:round(initial+pnl),win_rate:trades.length?wins.length/trades.length:null,return_pct:initial>0?pnl/initial*100:null,profit_factor:negative>0?positive/negative:null,average_trade:trades.length?pnl/trades.length:null,closed_equity_drawdown:round(drawdown),trading_days:active.length,best_day:active.length?active.reduce((a,b)=>a.pnl>=b.pnl?a:b):null,worst_day:active.length?active.reduce((a,b)=>a.pnl<=b.pnl?a:b):null};
}
export function reportGroups(days:Day[],period:ReportPeriod){
 const groups=new Map<string,{label:string;pnl:number;trades:number;wins:number}>();
 for(const d of days){const key=period==='weekly'?d.date:period==='quarterly'?d.date.slice(0,7):reportRange(d.date,'weekly').start;const prev=groups.get(key)||{label:key,pnl:0,trades:0,wins:0};prev.pnl=round(prev.pnl+d.pnl);prev.trades+=d.closed_count;prev.wins+=d.wins;groups.set(key,prev)}
 return Array.from(groups.values());
}
