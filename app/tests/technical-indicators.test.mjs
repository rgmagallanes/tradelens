import {test} from 'node:test';
import assert from 'node:assert/strict';
import {analyseTechnicals,emaSeries,rsi,stochastic,macdHistogram,ratingLabel,cci,adx,awesome,williams,ultimate,stochRsi,vwma,hull,ichimoku} from '../src/technicalIndicators.ts';
const bars=(n=250,direction=1)=>Array.from({length:n},(_,i)=>{const close=1000+direction*i;return {time:1800000000+i*300,open:close,high:close+2,low:close-2,close,tick_volume:10,closed:true}});
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-9,`${a} != ${b}`);

test('SMA-seeded EMA and Wilder RSI use known arithmetic',()=>{
 assert.deepEqual(emaSeries([10,20,30,40],3),[null,null,20,30]);
 near(rsi([10,11,13,12,14],3),100-100/7);
 assert.equal(rsi([5,5,5,5],3),50);assert.equal(rsi([5,4,3,2],3),0);assert.equal(rsi([1,2],14),null);
 near(macdHistogram(Array.from({length:100},(_,i)=>i+1)),0);
});
test('flat prices produce genuinely neutral groups without divide-by-zero',()=>{
 const b=bars().map(b=>({...b,open:100,high:100,low:100,close:100}));
 assert.equal(stochastic(b),50);const m=analyseTechnicals(b,300,'exness');
 assert.equal(m.summary.label,'Neutral');assert.equal(m.summary.neutral,26);assert.equal(m.summary.score,0);
});
test('rising/falling histories derive distinct ratings with equal group weighting',()=>{
 const up=analyseTechnicals(bars(250,1),300,'exness');
 assert.equal(up.movingRating.buy,13);assert.equal(up.oscillatorRating.total,11);assert.equal(up.movingRating.total,15);
 near(up.summary.score,(up.oscillatorRating.score+up.movingRating.score)/2);assert.equal(up.summary.label,'Buy');
 const down=analyseTechnicals(bars(250,-1),300,'exness');assert.equal(down.movingRating.sell,13);assert.equal(down.summary.label,'Sell');
});
test('forming candles and unconfirmed live bars cannot change closed-bar ratings',()=>{
 const b=bars();const before=analyseTechnicals(b,300,'exness');
 const forming={time:b.at(-1).time+300,open:100000,high:100001,low:99999,close:100000,closed:false};
 assert.deepEqual(analyseTechnicals([...b,forming],300,'exness'),before);
 assert.equal(before.lastClosedAt,b.at(-1).time+300);
 const unspecified=b.map(({closed,...b})=>b);
 assert.equal(analyseTechnicals(unspecified,300,'exness').summary.label,'Unavailable');
 assert.equal(analyseTechnicals(unspecified,300,'sample').barCount,250);
});
test('gaps reset warmup and invalid data never generates a rating',()=>{
 const b=bars();b.at(-1).time+=300;const g=analyseTechnicals(b,300,'exness');
 assert.equal(g.barCount,1);assert.equal(g.summary.score,null);assert.equal(g.movingRating.label,'Unavailable');
 const invalid=bars();invalid[0].high=1;assert.equal(analyseTechnicals(invalid,300,'exness').invalid,true);
 assert.equal(analyseTechnicals([],300,'exness').summary.label,'Unavailable');
});
test('rating thresholds distinguish unavailable from neutral',()=>{
 assert.equal(ratingLabel(null),'Unavailable');assert.equal(ratingLabel(-.5),'Strong sell');assert.equal(ratingLabel(.5),'Strong buy');
 assert.equal(ratingLabel(-.1),'Neutral');assert.equal(ratingLabel(.1),'Neutral');assert.equal(ratingLabel(-.2),'Sell');
});


test('expanded indicators have independently known values on linear prices',()=>{
 const b=bars(250,1),v=b.map(x=>x.close),last=v.at(-1);
 near(cci(b),126.66666666666667);near(adx(b).value,100);
 near(awesome(b),14.5);near(williams(b),-100*2/17);
 near(ultimate(b),50);near(stochRsi(b).k,50);near(stochRsi(b).d,50);
 near(vwma(b),last-9.5);near(hull(v),last);
 near(ichimoku(b).base,last-12.5);
 const m=analyseTechnicals(b,300,'exness');assert.equal(m.oscillators.length,11);assert.equal(m.movingAverages.length,15);
 assert.equal(m.summary.available,26);assert.ok(Number.isFinite(m.summary.score));
});
test('tick-volume weighting is genuine and missing history never receives invented values',()=>{
 const b=bars(250);b.at(-1).tick_volume=190;
 const w=b.slice(-20),expected=w.reduce((s,x)=>s+x.close*x.tick_volume,0)/w.reduce((s,x)=>s+x.tick_volume,0);near(vwma(b),expected);
 for(const volume of [undefined,-1,NaN]){const missing=b.map(x=>({...x,tick_volume:volume}));assert.equal(vwma(missing),null);assert.equal(analyseTechnicals(missing,300,'exness').summary.score,null)}
 assert.equal(vwma(b.map(x=>({...x,tick_volume:0}))),null);
 const short=analyseTechnicals(b.slice(-199),300,'exness');assert.equal(short.summary.score,null);assert.match(short.reason,/200/);
 for(const fn of [cci,adx,awesome,williams,ultimate,stochRsi,vwma,ichimoku])assert.equal(fn([]),null);
 assert.equal(hull([]),null);
});


test('Gold bar-based indicators retain history across session gaps; BTC remains strict',()=>{
 const b=bars(250);for(let i=100;i<b.length;i++)b[i].time+=7200;
 const btc=analyseTechnicals(b,300,'exness');assert.equal(btc.barCount,150);assert.equal(btc.summary.score,null);
 const gold=analyseTechnicals(b,300,'exness','XAUUSDm');assert.equal(gold.barCount,250);assert.equal(gold.summary.available,26);assert.ok(Number.isFinite(gold.summary.score));assert.match(gold.reason,/coverage is not verified/);
 assert.deepEqual(gold.summary,analyseTechnicals(bars(250),300,'exness','XAUUSDm').summary);
 const forming={...b.at(-1),time:b.at(-1).time+300,closed:false,high:99999,close:99999};
 assert.deepEqual(analyseTechnicals([...b,forming],300,'exness','XAUUSDm'),gold);
 const invalid=b.map(x=>({...x}));invalid[0].high=1;assert.equal(analyseTechnicals(invalid,300,'exness','XAUUSDm').summary.score,null);
});
