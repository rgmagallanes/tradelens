import {test} from 'node:test';
import assert from 'node:assert/strict';
import {calendarPositions} from '../src/calendarPositions.ts';
const trade=(id,time,pnl,status='open')=>({id,opened_at:Date.parse(time)/1000,floating_pnl:pnl,status});
test('floating totals group by Manila entry day and remain separate from closed trades',()=>{
 const map=calendarPositions([trade('a','2026-10-19T15:59:00Z',10),trade('b','2026-10-19T16:00:00Z',20),trade('c','2026-10-20T02:00:00Z',-5),trade('closed','2026-10-20T02:00:00Z',999,'closed')]);
 assert.deepEqual(map.get('2026-10-19'),{count:1,pnl:10,known:true});
 assert.deepEqual(map.get('2026-10-20'),{count:2,pnl:15,known:true});
});
test('missing floating values do not masquerade as zero',()=>{
 const map=calendarPositions([trade('missing','2026-10-20T02:00:00Z',undefined),trade('known','2026-10-20T02:00:00Z',-7)]);
 assert.deepEqual(map.get('2026-10-20'),{count:2,pnl:-7,known:false});
 assert.equal(calendarPositions([]).size,0);
});
