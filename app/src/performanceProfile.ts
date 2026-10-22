import type {buildReport} from './journalReports';
type Report=ReturnType<typeof buildReport>;
export type PerformanceAxis={name:string;raw:number|null;score:number|null;format:'percent'|'ratio'|'money';rule:string};
const bound=(n:number)=>Math.max(0,Math.min(100,n));
/** Descriptive, versioned normalization. Not a probability or a trading signal. */
export function performanceProfile(report:Report){
 const trades=report.days.flatMap(d=>d.trades).filter(t=>t.status==='closed'&&t.closed_at!=null&&Number.isFinite(t.pnl));
 const wins=trades.filter(t=>t.pnl!>0),losses=trades.filter(t=>t.pnl!<0),winTotal=wins.reduce((s,t)=>s+t.pnl!,0),lossTotal=-losses.reduce((s,t)=>s+t.pnl!,0);
 const active=report.days.filter(d=>d.closed_count>0),meanAbsolute=trades.length?trades.reduce((s,t)=>s+Math.abs(t.pnl!),0)/trades.length:0;
 const payoff=wins.length&&losses.length?(winTotal/wins.length)/(lossTotal/losses.length):null;
 const recovery=report.closed_equity_drawdown>0?report.pnl/report.closed_equity_drawdown:null;
 const consistency=active.length?active.filter(d=>d.pnl>0).length/active.length:null;
 const axes:PerformanceAxis[]=[
 {name:'Win rate',raw:report.win_rate,score:report.win_rate===null?null:bound(report.win_rate*100),format:'percent',rule:'Win percentage × 100. Breakeven fills remain in the denominator.'},
 {name:'Profit factor',raw:report.profit_factor,score:report.profit_factor===null?null:bound(report.profit_factor/2*100),format:'ratio',rule:'Gross winning P/L / absolute gross losing P/L; a ratio of 2 maps to 100. Undefined without losses.'},
 {name:'Avg win / loss',raw:payoff,score:payoff===null?null:bound(payoff/2*100),format:'ratio',rule:'Average winning amount / average losing amount; a ratio of 2 maps to 100. Requires both outcomes.'},
 {name:'Recovery',raw:recovery,score:recovery===null?null:bound(recovery/3*100),format:'ratio',rule:'Net closed P/L / maximum closed-P/L drawdown; a ratio of 3 maps to 100. Negative recovery maps to zero. Undefined with no drawdown.'},
 {name:'Drawdown control',raw:trades.length?report.closed_equity_drawdown:null,score:meanAbsolute>0?bound(100/(1+report.closed_equity_drawdown/meanAbsolute)):null,format:'money',rule:'100 / (1 + maximum closed-P/L drawdown / mean absolute trade P/L). Lower drawdown relative to trade amounts scores higher; no account-equity assumption.'},
 {name:'Consistency',raw:consistency,score:consistency===null?null:bound(consistency*100),format:'percent',rule:'Profitable active days / all active days × 100. An active day has at least one closed fill.'}
 ];
 const complete=axes.every(a=>a.score!==null),enough=trades.length>=20&&active.length>=5,score=complete&&enough?Math.round(axes.reduce((s,a)=>s+a.score!,0)/axes.length*100)/100:null;
 const reason=!enough?'Headline score requires 20 closed trades across 5 active days.':!complete?'Some ratios are undefined. Both winning and losing trades, and observed drawdown, are needed.':'';
 return {version:'tradelens-performance-v1',axes,score,band:score===null?'Building history':score>=80?'High score':score>=60?'Upper-middle':score>=40?'Middle band':'Lower band',tradeCount:trades.length,activeDays:active.length,complete,enough,reason};
}
