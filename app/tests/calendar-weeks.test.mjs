import {test} from 'node:test';
import assert from 'node:assert/strict';
import {calendarWeeks} from '../src/calendarWeeks.ts';
const days=n=>Array.from({length:n},(_,i)=>({date:`2026-10-${String(i+1).padStart(2,'0')}`,pnl:0,closed_count:0,open_count:1,trades:[]}));
test('partial Monday-Sunday rows include only current month and reconcile totals',()=>{
 const d=days(31);d[0].pnl=10.12;d[3].pnl=-3.12;d[4].pnl=2;d[30].pnl=-1;
 d[0].closed_count=2;d[3].closed_count=1;
 const r=calendarWeeks(d,3);
 assert.equal(r.length,5);assert.equal(r[0].days.length,4);assert.equal(r[0].pnl,7);assert.equal(r[0].trades,3);assert.equal(r[0].activeDays,2);
 assert.equal(r.reduce((s,w)=>s+w.pnl,0),8);assert.equal(r[1].pnl,2);assert.equal(r[4].pnl,-1);
});
test('six-row months and no-trade weeks preserve zero, excluding open position counts',()=>{
 const r=calendarWeeks(days(31),6);assert.equal(r.length,6);assert.equal(r[0].days.length,1);
 assert.ok(r.every(w=>w.pnl===0&&w.activeDays===0&&w.trades===0));
});
