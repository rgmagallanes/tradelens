import type {Trade} from './journalTypes';
export type ReviewBar={time:number;open:number;high:number;low:number;close:number};
export type ReviewData={source:string;day:string;symbol:string;timeframe:string;saved:boolean;state:string;bars:ReviewBar[];trades:Trade[];message:string;captured_at?:number;provenance?:string[];snapshot_sha256?:string;coverage?:{bars:number;expected_full_day:number;missing_completed_bars:number;in_progress:boolean}};
export function demoDayChart(day:string,symbol:string,tf:string,trades:Trade[]):ReviewData{
 const step={M5:300,M15:900,H1:3600}[tf]||300;const start=Date.parse(day+'T00:00:00+08:00')/1000;const base=82000+Number(day.slice(-2))*45;
 const anchors=[{time:start,price:base-100},...trades.filter(t=>t.symbol===symbol).flatMap(t=>[{time:t.opened_at,price:t.entry},...(t.closed_at&&t.exit!=null?[{time:t.closed_at,price:t.exit}]:[])]),{time:start+86400,price:base+120}].sort((a,b)=>a.time-b.time);
 function price(time:number){let i=1;while(i<anchors.length-1&&anchors[i].time<time)i++;const a=anchors[i-1],b=anchors[i];const f=(time-a.time)/Math.max(1,b.time-a.time);return a.price+(b.price-a.price)*f+Math.sin(f*Math.PI)*Math.sin(time/900)*35}
 const bars:ReviewBar[]=Array.from({length:86400/step},(_,i)=>{const time=start+i*step;const open=price(time),close=price(time+step);return {time,open,close,high:Math.max(open,close)+18,low:Math.min(open,close)-18}});
 return {source:'demo',day,symbol,timeframe:tf,saved:false,state:'available',bars,trades:trades.filter(t=>t.symbol===symbol),message:'Fictional chart and trade markers for demonstration only. These are not market prices or backtest results.',coverage:{bars:bars.length,expected_full_day:bars.length,missing_completed_bars:0,in_progress:false}};
}
