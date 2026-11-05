// @ts-ignore Explicit extension supports Node's native TypeScript test runner.
import {demoJournal,DEMO_MONTH} from './journalDemo.ts';
import type {Trade} from './journalTypes';
export {DEMO_MONTH};
export function dashboardDemo(kind:'mixed'|'drawdown'){
 const data=demoJournal(kind,DEMO_MONTH);
 for(const day of data.days){for(const [i,t] of day.trades.entries()){
  t.pnl=Math.round(t.pnl!*25*100)/100;t.symbol=(Number(day.date.slice(-2))+i)%2?'BTCUSDm':'XAUUSDm';
  t.entry=t.symbol==='BTCUSDm'?82000+Number(day.date.slice(-2))*45:3900+Number(day.date.slice(-2))*3;t.lots=.1;
  const multiplier=t.symbol==='XAUUSDm'?100:1;t.exit=t.entry+(t.side==='buy'?1:-1)*t.pnl/(t.lots*multiplier);
  t.protection=undefined;t.stop=undefined;t.target=undefined;
 }day.pnl=Math.round(day.trades.reduce((s,t)=>s+t.pnl!,0)*100)/100;}
 let balance=10000;for(const day of data.days){day.start_balance=balance;balance=Math.round((balance+day.pnl)*100)/100;day.end_balance=balance;}
 data.initial_balance=10000;data.summary={...data.summary,pnl:Math.round((balance-10000)*100)/100,start_balance:10000,end_balance:balance};
 return data;
}
export const DEMO_POSITIONS:Trade[]=[
 {id:'fictional-btc-open',source:'demo',symbol:'BTCUSDm',side:'buy',lots:.1,entry:82450,opened_at:Date.parse('2026-09-30T08:00:00Z')/1000,status:'open',floating_pnl:74.5,strategy:'Fictional breakout',note:'Fictional dashboard preview'},
 {id:'fictional-gold-open',source:'demo',symbol:'XAUUSDm',side:'sell',lots:.1,entry:3995,opened_at:Date.parse('2026-09-30T09:00:00Z')/1000,status:'open',floating_pnl:-32,strategy:'Fictional pullback',note:'Fictional dashboard preview'},
];
