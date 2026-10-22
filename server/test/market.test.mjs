import test from 'node:test';
import assert from 'node:assert/strict';
import {markets,marketResponse,bridgeResponse} from '../src/market.mjs';
import {fixture} from './fixtures/market.mjs';
const now=Math.floor(Date.now()/1000);
test('both instruments and all timeframes retain candles, volume and stale labels',()=>{
 const ms=markets.parse([fixture('BTCUSDm'),fixture('XAUUSDm')]);
 for(const symbol of ['BTCUSDm','XAUUSDm'])for(const tf of ['M5','M15','H1','H4']){const response=marketResponse(ms,symbol,tf,now);assert.equal(response.connected,true);assert.equal(response.candles[0].tick_volume,20);assert.equal(response.symbol,symbol);assert.equal(marketResponse(ms,symbol,tf,now+40).state,'stale');}
 assert.equal(bridgeResponse(ms,'XAUUSDm',now).connected,true);assert.equal(bridgeResponse(ms,'XAUUSDm',now+40).connected,false);
 assert.deepEqual(marketResponse([],'XAUUSDm','M5',now).candles,[]);
 assert.equal(marketResponse([fixture('BTCUSDm')],'XAUUSDm','H4',now).state,'waiting');
});
test('market validation rejects duplicate instruments, invalid OHLC and mismatched quotes',()=>{
 const m=fixture('BTCUSDm');assert.equal(markets.safeParse([m,m]).success,false);
 assert.equal(markets.safeParse([{...m,quote:{...m.quote,symbol:'XAUUSDm'}}]).success,false);
 assert.equal(markets.safeParse([{...m,candles:{M5:[{...m.candles.M5[0],high:1}]}}]).success,false);
 assert.equal(markets.safeParse([{...m,demo:false}]).success,false);
});
