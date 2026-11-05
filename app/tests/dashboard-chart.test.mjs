import test from 'node:test';
import assert from 'node:assert/strict';
import {chartDays,niceAxis} from '../src/dashboardChart.ts';
test('chart excludes future dates and keeps a baseline before first activity',()=>{const days=Array.from({length:31},(_,i)=>({date:`2026-10-${String(i+1).padStart(2,'0')}`,closed_count:i===20?1:0,pnl:i===20?-6076.92:0}));const shown=chartDays(days,'2026-10-25');assert.equal(shown[0].date,'2026-10-20');assert.equal(shown.at(-1).date,'2026-10-25');assert.equal(shown.reduce((s,d)=>s+d.pnl,0),-6076.92)});
test('rounded axis covers losses, gains, tiny results and flat series',()=>{for(const values of [[-6076.92,9478.94],[0],[.001,.003],[-5], [100]]){const a=niceAxis(values);assert.ok(a.min<=Math.min(0,...values));assert.ok(a.max>=Math.max(0,...values));assert.ok(a.max>a.min);assert.ok(a.ticks.includes(0));assert.ok(a.ticks.length<=9)}assert.deepEqual(niceAxis([-6076.92,9478.94]).ticks,[-10000,-5000,0,5000,10000])});
