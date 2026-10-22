import {test} from 'node:test';
import assert from 'node:assert/strict';
import {performanceProfile} from '../src/performanceProfile.ts';
function report(scale=1){let id=0;const days=Array.from({length:5},(_,i)=>({date:`2026-10-${10+i}`,closed_count:4,pnl:20*scale,trades:[20,-10,20,-10].map(pnl=>({id:String(++id),status:'closed',closed_at:100+id,pnl:pnl*scale}))}));return{days,win_rate:.5,profit_factor:2,pnl:100*scale,closed_equity_drawdown:10*scale}}
test('known six-axis arithmetic and equal weighting produce a disclosed 85 score',()=>{
 const p=performanceProfile(report());assert.equal(p.tradeCount,20);assert.equal(p.activeDays,5);
 assert.deepEqual(p.axes.map(a=>Math.round(a.score)),[50,100,100,100,60,100]);assert.equal(p.score,85);assert.equal(p.axes[2].raw,2);assert.equal(p.axes[3].raw,10);assert.equal(p.band,'High score');
});
test('normalization is invariant to currency scale and excludes open positions',()=>{
 const first=performanceProfile(report());const scaled=performanceProfile(report(1000));assert.equal(first.score,scaled.score);
 const r=report();r.days[0].trades.push({id:'open',status:'open',pnl:100000,closed_at:null});assert.deepEqual(performanceProfile(r),first);
});
test('small samples and undefined ratios never receive a fabricated headline score',()=>{
 const short=report();short.days[0].trades.pop();assert.equal(performanceProfile(short).score,null);assert.match(performanceProfile(short).reason,/20 closed/);
 const empty=performanceProfile({days:[],win_rate:null,profit_factor:null,pnl:0,closed_equity_drawdown:0});assert.equal(empty.score,null);assert.equal(empty.complete,false);assert.ok(empty.axes.every(a=>a.raw===null));
 const winners=report();for(const d of winners.days){for(const t of d.trades)t.pnl=20;d.pnl=80}Object.assign(winners,{win_rate:1,profit_factor:null,pnl:400,closed_equity_drawdown:0});const p=performanceProfile(winners);assert.equal(p.score,null);assert.equal(p.axes[1].score,null);assert.equal(p.axes[3].score,null);assert.match(p.reason,/undefined/);
});
test('negative recovery maps to zero and axes stay bounded',()=>{
 const r=report();r.pnl=-100;const p=performanceProfile(r);assert.equal(p.axes[3].raw,-10);assert.equal(p.axes[3].score,0);assert.ok(p.axes.every(a=>a.score===null||a.score>=0&&a.score<=100));
});
