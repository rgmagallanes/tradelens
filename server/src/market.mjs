import {z} from 'zod';
const positive=z.number().finite().positive().max(1e9);
const stamp=z.number().int().positive().max(4102444800);
// Allow broker forming bars, but reject candles dated beyond the current clock.

const bar=z.object({time:stamp.refine(t=>t<=Date.now()/1000+60),open:positive,high:positive,low:positive,close:positive,tick_volume:z.number().finite().nonnegative().optional(),real_volume:z.number().finite().nonnegative().optional(),closed:z.boolean()}).refine(b=>b.high>=Math.max(b.open,b.close,b.low)&&b.low<=Math.min(b.open,b.close));
const bars=z.array(bar).max(1000).refine(b=>b.every((v,i)=>!i||v.time>b[i-1].time));
const quote=z.object({version:z.literal(1),symbol:z.enum(['BTCUSDm','XAUUSDm']),timestamp:stamp,bid:positive,ask:positive,demo:z.literal(true),terminal_connected:z.boolean(),quote_age_seconds:z.number().finite().nonnegative(),tick_time_msc:z.number().finite().nonnegative().optional()}).refine(q=>q.ask>=q.bid);
export const markets=z.array(z.object({symbol:z.enum(['BTCUSDm','XAUUSDm']),timestamp:stamp,demo:z.literal(true),terminal_connected:z.boolean(),clock:z.literal('broker-server'),server_utc_offset_seconds:z.literal(0),candles:z.object({M1:bars.optional(),M5:bars.optional(),M15:bars.optional(),H1:bars.optional(),H4:bars.optional()}),quote:quote.optional()}).refine(m=>!m.quote||m.quote.symbol===m.symbol)).max(2).refine(ms=>new Set(ms.map(m=>m.symbol)).size===ms.length).superRefine((ms,c)=>{for(const m of ms)if(m.timestamp>Date.now()/1000+60||m.quote?.timestamp>Date.now()/1000+60)c.addIssue({code:'custom',message:'Future market timestamp'});});
export function marketResponse(ms,symbol,tf,now=Date.now()/1000){
 const m=ms?.find(m=>m.symbol===symbol),b=m?.candles[tf]||[],q=m?.quote;
 const age=m?now-m.timestamp:null,qa=q?now-q.timestamp:null;
 const recent=q&&b.length&&q.tick_time_msc/1000-b.at(-1).time>=0&&q.tick_time_msc/1000-b.at(-1).time<({M5:300,M15:900,H1:3600,H4:14400}[tf]*2);
 const fresh=Boolean(m?.terminal_connected&&age>=0&&age<30&&q?.terminal_connected&&qa>=0&&qa<30&&q.quote_age_seconds<30&&recent);
 return {source:'exness',symbol,clock:'broker-server',connected:fresh&&b.length>1,state:!b.length?'waiting':fresh?'fresh':'stale',candles:b,price:b.at(-1)?.close,age_seconds:age,research_m1_count:m?.candles.M1?.length||0,message:!b.length?'Waiting for this instrument’s candles. Run the updated Mac uploader with its quote indicator attached.':fresh?'Uploaded MT5 demo candles · Broker server time · Last candle forming':'Last uploaded candles · Feed stale or disconnected. Keep MT5 and the uploader running.'};
}
export function bridgeResponse(ms,symbol,now=Date.now()/1000){
 const q=ms?.find(m=>m.symbol===symbol)?.quote,age=q?now-q.timestamp:null;
 const fresh=Boolean(q?.terminal_connected&&age>=0&&age<30&&q.quote_age_seconds<30);
 return {source:'exness-mt5',connected:fresh,state:!q?'waiting':fresh?'fresh':'stale',snapshot:q,age_seconds:age,spread:q?q.ask-q.bid:undefined,message:fresh?'Uploaded demo quote received.':'Waiting for a fresh uploaded demo quote.'};
}
