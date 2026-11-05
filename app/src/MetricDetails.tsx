import {useState} from 'react';
import type {Trade} from './journalTypes';
export default function MetricDetails({metric,trades,onClose}:{metric:string;trades:Trade[];onClose:()=>void}){
 const [filter,setFilter]=useState('all');
 const money=(c:number)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(c/100);
 const ordered=[...trades].sort((a,b)=>a.closed_at!-b.closed_at!||a.id.localeCompare(b.id));
 let total=0,peak=0,max=0,peakIndex=-1,from=-1,to=-1,profit=0,loss=0;
 ordered.forEach((t,i)=>{const cents=Math.round(t.pnl!*100);total+=cents;if(cents>0)profit+=cents;else loss-=cents;if(total>peak){peak=total;peakIndex=i}if(peak-total>max){max=peak-total;from=peakIndex;to=i}});
 const rows=metric==='Closed P/L drawdown'?ordered.slice(from+1,to+1):trades.filter(t=>filter==='all'||(filter==='wins'?t.pnl!>0:filter==='losses'?t.pnl!<0:t.pnl===0));
 const wins=trades.filter(t=>t.pnl!>0).length;
 return <section className="td-panel td-metric-details" id="dashboard-metric-details" aria-label={metric+' breakdown'}><div className="td-panel-head"><h3>{metric} · Breakdown</h3><button onClick={onClose}>Close details</button></div>
 <p>{metric==='Closed net P/L'?`${money(profit)} winning fills − ${money(loss)} losing fills = ${money(total)} net.`:metric==='Win rate'?`${wins} winning fills ÷ ${trades.length} closed fills${trades.length?` = ${(wins/trades.length*100).toFixed(1)}%`:': no trades yet'}. Break-even fills remain in the denominator.`:metric==='Profit factor'?`${money(profit)} gross winning net results ÷ ${money(loss)} absolute losing net results${loss?` = ${(profit/loss).toFixed(2)}`:': unavailable without losing fills'}.`:`Largest closed-ledger decline: ${money(max)}. The table shows fills after the peak through the trough${from<0?' (starting from the period baseline)':''}.`}</p>
 {metric!=='Closed P/L drawdown'&&<label>Show fills <select value={filter} onChange={e=>setFilter(e.target.value)}><option value="all">All results</option><option value="wins">Winners</option><option value="losses">Losers</option><option value="flat">Break-even</option></select></label>}
 <div className="td-table-scroll"><table><thead><tr><th>Closed · Manila</th><th>Instrument</th><th>Side</th><th>Net P/L</th></tr></thead><tbody>{rows.map(t=><tr key={t.id}><td>{new Date(t.closed_at!*1000).toLocaleString('en-GB',{timeZone:'Asia/Manila'})}</td><td>{t.symbol}</td><td>{t.side.toUpperCase()}</td><td className={t.pnl!>0?'positive':t.pnl!<0?'negative':''}>{money(Math.round(t.pnl!*100))}</td></tr>)}</tbody></table>{!rows.length&&<p>No matching closed fills.</p>}</div><small>Selected source and period · Partial closes count separately · Floating P/L and cash movements excluded.</small></section>
}
