import type {Day,JournalData,Trade} from './journalTypes';

export const DEMO_MONTH='2026-09';
export const DEMO_DAY='2026-09-19';
export const DEMO_DATASETS=[
 {id:'mixed',label:'Demo · Mixed trading month'},
 {id:'drawdown',label:'Demo · Drawdown & recovery'},
] as const;
export type DemoDataset='none'|'mixed'|'drawdown';
const outcomes:Record<Exclude<DemoDataset,'none'>,Array<[number,number[]]>>={
 mixed:[[1,[8.4,12.6]],[2,[-7.5,4.2]],[3,[11.8]],[4,[-9.3,-5.4]],[7,[16.2,6.4]],[8,[0]],[9,[8.7]],[10,[-12.5]],[11,[18.6,9.4]],[14,[5.2,-6.8]],[15,[14.3]],[16,[-8.1]],[17,[12.4,7.6]],[18,[-10.2,3.8]],[19,[4.12,-6.4,12.36]],[21,[17.8]],[22,[-9.6]],[23,[6.4,10.2]],[24,[8.5]],[25,[-7.3,15.4]],[28,[11.6]],[29,[-6.2]],[30,[9.8,5.4]]],
 drawdown:[[1,[12.4]],[2,[-18.6,-9.8]],[3,[-14.2]],[4,[-7.4,-11.8]],[7,[5.6]],[8,[-16.4]],[9,[-8.2,4.6]],[10,[-12.8]],[11,[-7.6]],[14,[6.2,-9.4]],[15,[-14.6]],[16,[8.4]],[17,[5.2,-7.8]],[18,[11.4]],[19,[-8.6,4.2,7.8]],[21,[12.6]],[22,[-6.4]],[23,[14.2]],[24,[9.8,-5.6]],[25,[11.4]],[28,[7.2]],[29,[-4.8]],[30,[10.6,6.4]]],
};
const cents=(v:number)=>Math.round(v*100)/100;
const localDay=(n:number)=>new Date(n*1000+8*3600000).toISOString().slice(0,10);

/** Fictional, read-only examples. Never fetched from or written to an account. */
export function demoJournal(dataset:Exclude<DemoDataset,'none'>,month:string):JournalData{
 const trades:Trade[]=outcomes[dataset].flatMap(([d,values])=>values.map((pnl,i)=>{
  const opened=Date.parse(`${DEMO_MONTH}-${String(d).padStart(2,'0')}T${String(9+i*2).padStart(2,'0')}:05:00+08:00`)/1000;
  const side=(d+i)%2?'buy':'sell';const entry=82000+d*45+i*20;const lots=.02;
  return {id:`demo-${dataset}-${d}-${i}`,source:'demo',symbol:'BTCUSDm',side,lots,entry,exit:cents(entry+(side==='buy'?1:-1)*(pnl+.2)/lots),opened_at:opened,closed_at:opened+900,status:'closed',pnl,strategy:i%2?'Trend pullback · Fictional':'Breakout + retest · Fictional',note:pnl<0?'Example loss: review the entry and stop placement. This is fictional demo data.':'Example trade: document the setup and whether the plan was followed. This is fictional demo data.'};
 }));
 const [year,m]=month.split('-').map(Number);const count=new Date(Date.UTC(year,m,0)).getUTCDate();
 const initial=1000;let balance=cents(initial+trades.filter(t=>localDay(t.closed_at!)<month+'-01').reduce((s,t)=>s+t.pnl!,0));
 const days:Day[]=Array.from({length:count},(_,i)=>{
  const date=`${month}-${String(i+1).padStart(2,'0')}`;const closed=trades.filter(t=>localDay(t.closed_at!)===date);const pnl=cents(closed.reduce((s,t)=>s+t.pnl!,0));const start=balance;balance=cents(balance+pnl);
  return {date,start_balance:start,end_balance:balance,pnl,closed_count:closed.length,open_count:0,wins:closed.filter(t=>t.pnl!>0).length,losses:closed.filter(t=>t.pnl!<0).length,trades:closed,note:closed.length?(dataset==='drawdown'?'Example reflection: avoid chasing losses. Review each trade against the plan.':'Example reflection: keep position size consistent and record both good decisions and mistakes.'):''};
 });
 const closed=days.flatMap(d=>d.trades);const wins=closed.filter(t=>t.pnl!>0).length;
 return {source:'demo',month,initial_balance:initial,days,summary:{pnl:cents(closed.reduce((s,t)=>s+t.pnl!,0)),closed_count:closed.length,wins,losses:closed.filter(t=>t.pnl!<0).length,win_rate:closed.length?wins/closed.length:null,start_balance:days[0].start_balance,end_balance:balance},open_positions:[],undated_trades:[]};
}
