import {test} from 'node:test';
import assert from 'node:assert/strict';
import {pivotLevels,dailyPivots} from '../src/pivots.ts';
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);
test('known OHLC yields correct five-method levels including Woodie current open',()=>{
 const m=pivotLevels({open:100,high:120,low:90,close:105},110);
 assert.deepEqual(m.Classic,{R3:165,R2:135,R1:120,P:105,S1:90,S2:75,S3:45});
 near(m.Fibonacci.R1,116.46);near(m.Fibonacci.S2,86.46);near(m.Camarilla.R3,113.25);near(m.Camarilla.S1,102.25);
 assert.deepEqual(m.Woodie,{R3:155,R2:137.5,R1:125,P:107.5,S1:95,S2:77.5,S3:65});
 assert.deepEqual(m.DM,{R3:null,R2:null,R1:127.5,P:108.75,S1:97.5,S2:null,S3:null});
 assert.equal(pivotLevels({open:100,high:120,low:90,close:100},110).DM.P,102.5);
 assert.equal(pivotLevels({open:110,high:120,low:90,close:100},110).DM.P,100);
 assert.equal(pivotLevels({open:100,high:120,low:90,close:105},null).Woodie.P,null);
 assert.equal(pivotLevels({open:100,high:1,low:90,close:105},110),null);
});
const day=1800057600; // UTC midnight
const bars=()=>Array.from({length:25},(_,i)=>({time:day+i*3600,open:100,high:120,low:90,close:105,closed:i<24}));
test('daily coverage is exact and forming current high/close cannot affect pivots',()=>{
 const b=bars();assert.equal(day%86400,0);const m=dailyPivots(b,3600,'exness');assert.ok(m.levels);assert.equal(m.previousDay,day);
 b.at(-1).high=9999;b.at(-1).close=9998;assert.deepEqual(dailyPivots(b,3600,'exness'),m);
 b.at(-1).open=110;assert.notEqual(dailyPivots(b,3600,'exness').levels.Woodie.P,m.levels.Woodie.P);
});
test('incomplete, unconfirmed, unordered and missing-current-open cases stay explicit',()=>{
 const b=bars();assert.equal(dailyPivots(b.slice(1),3600,'exness').levels,null);
 const forming=bars();forming[0].closed=false;assert.equal(dailyPivots(forming,3600,'exness').levels,null);
 const missingOpen=[...b.slice(0,24),{...b.at(-1),time:day+25*3600}];const m=dailyPivots(missingOpen,3600,'exness');assert.equal(m.levels.Woodie.P,null);assert.equal(m.levels.Classic.P,105);
 assert.equal(dailyPivots([...b].reverse(),3600,'exness').levels,null);
 assert.equal(dailyPivots([],3600,'exness').levels,null);
});
