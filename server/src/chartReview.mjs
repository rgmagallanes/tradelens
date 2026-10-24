import {readFile} from 'node:fs/promises';
import {z} from 'zod';
import {sources,date,day} from './domain.mjs';
import {hash} from './security.mjs';
export const intervals={M5:300,M15:900,H1:3600};
export const chartRequest=z.object({source:sources,day:date,symbol:z.string().regex(/^[A-Za-z0-9._-]{1,30}$/),timeframe:z.enum(['M5','M15','H1']),trade_id:z.string().min(1).max(120).optional()});
export async function ensureChartTables(pool){const sql=await readFile(new URL('./schema.sql',import.meta.url),'utf8');for(const statement of sql.split(';').map(s=>s.trim()).filter(s=>s.startsWith('CREATE TABLE IF NOT EXISTS tl_chart_')))await pool.query(statement);}
export function archiveRows(body,now=Date.now()/1000){
 if(!body.demo)return [];
 const batches=[...(body.review_history||[]),...(body.markets||[]).flatMap(m=>Object.entries(m.candles).filter(([tf])=>tf in intervals).map(([timeframe,bars])=>({symbol:m.symbol,timeframe,bars,timestamp:m.timestamp})))];
 const rows=new Map();
 for(const batch of batches){const step=intervals[batch.timeframe];for(const b of batch.bars){if(!b.closed||b.time%step||b.time+step>now)continue;const candle={time:b.time,open:b.open,high:b.high,low:b.low,close:b.close};const key=batch.symbol+':'+batch.timeframe+':'+b.time,old=rows.get(key);if(!old||old.timestamp<=batch.timestamp)rows.set(key,{symbol:batch.symbol,timeframe:batch.timeframe,time:b.time,timestamp:batch.timestamp,payload:JSON.stringify(candle)});}}
 return [...rows.values()];
}
export async function archiveUpload(c,userId,body){const rows=archiveRows(body);for(let i=0;i<rows.length;i+=300){const chunk=rows.slice(i,i+300);await c.execute('INSERT INTO tl_chart_candles(user_id,symbol,timeframe,bar_time,export_timestamp,payload) VALUES '+chunk.map(()=>'(?,?,?,?,?,?)').join(',')+' ON DUPLICATE KEY UPDATE payload=IF(export_timestamp<=VALUES(export_timestamp),VALUES(payload),payload),export_timestamp=GREATEST(export_timestamp,VALUES(export_timestamp))',chunk.flatMap(r=>[userId,r.symbol,r.timeframe,r.time,r.timestamp,r.payload]));}}
export function reviewKey(q){return hash(JSON.stringify([q.source,q.day,q.symbol,q.timeframe,q.trade_id||null]));}
export function reconstructReview(q,candles,trades,now=Date.now()/1000){
 const step=intervals[q.timeframe],start=Date.parse(q.day+'T00:00:00+08:00')/1000,end=start+86400;
 const unique=new Map();for(const b of candles)if(b.time>=start&&b.time<end&&b.time%step===0&&b.time+step<=now)unique.set(b.time,{time:b.time,open:b.open,high:b.high,low:b.low,close:b.close});
 const bars=[...unique.values()].sort((a,b)=>a.time-b.time),completed=Math.max(0,Math.floor((Math.min(end,Math.floor(now/step)*step)-start)/step));
 const selected=trades.filter(t=>t.symbol===q.symbol&&(q.trade_id?t.id===q.trade_id:day(t.status==='closed'?t.closed_at:t.opened_at)===q.day));
 return {source:q.source,day:q.day,symbol:q.symbol,timeframe:q.timeframe,saved:false,capture_kind:'historical_reconstruction',timezone:'Asia/Manila',time_basis:'Uploaded MT5 UTC+0 demo candles; displayed in Asia/Manila',state:bars.length>=2?'available':'unavailable',bars,trades:selected,captured_at:now,coverage:{bars:bars.length,expected_full_day:86400/step,missing_completed_bars:Math.max(0,completed-bars.length),in_progress:now<end},provenance:['User-scoped uploaded MT5 UTC+0 demo candle archive.','Only completed candles are shown; absent bars remain gaps.','Markers use journal execution times and price levels; candles are context, not proof of execution.'],message:bars.length>=2?'Historical reconstruction from uploaded MT5 demo candles; not an entry-time screenshot or proof of execution.':'No usable uploaded candle history for this day yet. Keep MT5 and the updated uploader running. Older days require a local candle archive backfill.'};
}
export async function loadReview(pool,userId,input,save=false){
 const q=chartRequest.parse(input),key=reviewKey(q);
 const [saved]=await pool.execute('SELECT payload FROM tl_chart_reviews WHERE user_id=? AND review_key=?',[userId,key]);if(saved.length)return {...JSON.parse(saved[0].payload),saved:true};
 const [snapshots]=await pool.execute('SELECT payload FROM tl_snapshots WHERE user_id=?',[userId]);const snapshot=snapshots[0]?JSON.parse(snapshots[0].payload):null;
 const [records]=await pool.execute('SELECT payload FROM tl_trades WHERE user_id=? AND source=?',[userId,q.source]);const trades=records.map(r=>JSON.parse(r.payload));
 if(q.trade_id&&!trades.some(t=>t.id===q.trade_id&&t.symbol===q.symbol))throw Object.assign(Error('Trade not found in this journal source and symbol.'),{status:404});
 let result;
 if(q.source==='sample'||!snapshot?.demo||!['BTCUSDm','XAUUSDm'].includes(q.symbol))result={...reconstructReview(q,[],trades),message:q.source==='sample'?'Sample trades have no recorded broker chart.':snapshot?.demo===false?'Live-account chart history is not supported yet. Demo candles are not substituted for live trades.':'No uploaded BTCUSDm/XAUUSDm demo candle feed is available for this workspace.'};
 else {
 const start=Date.parse(q.day+'T00:00:00+08:00')/1000;
 const [rows]=await pool.execute('SELECT payload FROM tl_chart_candles WHERE user_id=? AND symbol=? AND timeframe=? AND bar_time>=? AND bar_time<? ORDER BY bar_time',[userId,q.symbol,q.timeframe,start,start+86400]);
 const fallback=(snapshot.markets||[]).find(m=>m.symbol===q.symbol)?.candles[q.timeframe]||[];
 result=reconstructReview(q,[...fallback.filter(b=>b.closed),...rows.map(r=>JSON.parse(r.payload))],trades);
 if(q.source==='manual')result.provenance.push('Manual trade records may originate from a different account or feed.');
 }
 if(!save)return result;
 if(result.state!=='available')throw Object.assign(Error(result.message),{status:422});
 result.snapshot_sha256=hash(JSON.stringify(result));
 await pool.execute('INSERT IGNORE INTO tl_chart_reviews(user_id,review_key,payload) VALUES(?,?,?)',[userId,key,JSON.stringify(result)]);
 const [stored]=await pool.execute('SELECT payload FROM tl_chart_reviews WHERE user_id=? AND review_key=?',[userId,key]);return {...JSON.parse(stored[0].payload),saved:true};
}
