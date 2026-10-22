import {test} from 'node:test';
import assert from 'node:assert/strict';
import {fairValueGaps} from '../src/fairValueGaps.ts';
const bar=(time,low,high,closed=true)=>({time,low,high,open:low,close:high,closed});
test('bullish gap survives partial fill and is removed by full fill',()=>{
 const bars=[bar(0,9,10),bar(300,10,14),bar(600,12,15)];
 assert.deepEqual(fairValueGaps(bars,300),[{time:600,lower:10,upper:12,side:'bullish'}]);
 assert.equal(fairValueGaps([...bars,bar(900,11,13)],300).length,1);
 assert.equal(fairValueGaps([...bars,bar(900,10,13)],300).length,0);
});
test('bearish gap and full mitigation are symmetric',()=>{
 const bars=[bar(0,12,15),bar(300,9,13),bar(600,8,10)];
 assert.equal(fairValueGaps(bars,300)[0].side,'bearish');
 assert.equal(fairValueGaps([...bars,bar(900,9,12)],300).length,0);
});
test('forming bars cannot create or mitigate gaps; missing intervals cannot create gaps',()=>{
 const bars=[bar(0,9,10),bar(300,10,14),bar(600,12,15)];
 assert.equal(fairValueGaps([...bars.slice(0,2),{...bars[2],closed:false}],300).length,0);
 assert.equal(fairValueGaps([...bars,bar(900,8,13,false)],300).length,1);
 assert.equal(fairValueGaps([bars[0],bars[1],{...bars[2],time:900}],300).length,0);
});
