import test from 'node:test';
import assert from 'node:assert/strict';
import {buildJournalGraph,connectionSummary} from '../src/journalConnections.ts';
const trade=(id,extra={})=>({id,source:'mt5',symbol:'BTCUSDm',side:'buy',lots:.1,entry:100,opened_at:1000,closed_at:1100,status:'closed',pnl:1,strategy:'Retest',note:'Waited for close.',...extra});
const journal=trades=>({days:[{date:'2026-10-23',trades}]});
test('graph uses actual recorded connections, deduplicates rows and preserves trade identity',()=>{
 const data=journal([trade('one'),trade('one'),trade('two',{symbol:'XAUUSDm',strategy:'',note:'',pnl:-1})]);const g=buildJournalGraph(data);
 assert.equal(g.total,2);assert.equal(g.nodes.filter(n=>n.kind==='trade').length,2);assert.equal(g.nodes.filter(n=>n.kind==='note').length,1);
 assert.ok(g.edges.some(e=>e.from==='strategy:Unclassified'&&e.to==='trade:two'));
 assert.ok(g.edges.some(e=>e.from==='symbol:XAUUSDm'&&e.to==='trade:two'));
 assert.ok(!g.nodes.some(n=>n.kind==='mistake'||n.kind==='lesson'));
 assert.equal(g.nodes.find(n=>n.id==='trade:one').day,'2026-10-23');
 assert.deepEqual(g,buildJournalGraph(data));assert.ok(g.nodes.every(n=>Number.isFinite(n.x)&&Number.isFinite(n.y)));
});
test('empty journal and bounded latest-trade view never manufacture entries',()=>{
 assert.equal(buildJournalGraph(journal([])).nodes.length,1);
 const g=buildJournalGraph(journal(Array.from({length:130},(_,i)=>trade(String(i),{opened_at:i}))));assert.equal(g.total,130);assert.equal(g.shown,120);assert.ok(!g.nodes.some(n=>n.id==='trade:0'));assert.ok(g.nodes.some(n=>n.id==='trade:129'));
 const ids=new Set(g.nodes.map(n=>n.id));assert.ok(g.edges.every(e=>ids.has(e.from)&&ids.has(e.to)));
});

test('daily reflections remain recorded context, including days with no trades',()=>{const g=buildJournalGraph({days:[{date:'2026-10-22',note:'Review discipline',trades:[]},{date:'2026-10-23',note:'Wait for confirmation',trades:[trade('one')]}]});assert.equal(g.nodes.filter(n=>n.id.startsWith('reflection:')).length,2);assert.ok(g.edges.some(e=>e.from==='reflection:2026-10-23'&&e.to==='trade:one'));assert.equal(g.nodes.find(n=>n.id==='reflection:2026-10-22').detail,'Review discipline')});

test('manual tags connect trades and summaries exclude open and unknown P/L',()=>{const data=journal([trade('win',{pnl:12}),trade('loss',{pnl:-5}),trade('open',{status:'open',pnl:999}),trade('unknown',{pnl:undefined})]);const tags={win:{mistakes:[],lessons:['followed plan']},loss:{mistakes:['entered early'],lessons:[]}};const g=buildJournalGraph(data,tags);assert.ok(g.edges.some(e=>e.from==='mistake:entered early'&&e.to==='trade:loss'));const lesson=g.nodes.find(n=>n.id==='lesson:followed plan');assert.equal(connectionSummary(data,lesson,tags).pnl,12);const stats=connectionSummary(data,g.nodes[0],tags);assert.equal(stats.pnl,7);assert.equal(stats.winRate,.5);assert.equal(stats.open,1);assert.equal(stats.missing,1);assert.equal(stats.trades,4)});

test('every trade gets TP/SL satellites without inventing missing records',()=>{const t=trade('protected',{protection:{stop:{value:0,basis:'open-snapshot',observed_at:1000},target:{value:150,basis:'open-snapshot',observed_at:1000}}});const g=buildJournalGraph(journal([t,trade('legacy')]));const tp=g.nodes.find(n=>n.id==='tp:protected'),sl=g.nodes.find(n=>n.id==='sl:protected');assert.equal(tp.record.value,150);assert.equal(sl.record.value,0);assert.match(sl.label,/Not set/);assert.equal(g.nodes.find(n=>n.id==='sl:legacy').record.basis,'unknown');assert.ok(g.edges.some(e=>e.from==='trade:protected'&&e.to==='tp:protected'));assert.equal(tp.tradeId,'protected')});

test('non-MT5 journals do not claim automatic broker protective records',()=>{const g=buildJournalGraph({...journal([trade('manual',{source:'manual',stop:90,target:120})]),source:'manual'});assert.equal(g.nodes.filter(n=>n.kind==='tp'||n.kind==='sl').length,0)});
