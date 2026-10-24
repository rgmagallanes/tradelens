import type {JournalData} from './journalTypes';
// Performance reports track closed records; live position/quote updates must not reload them.
export function closedReportRevision(data:JournalData|undefined){
 if(!data)return '';
 return JSON.stringify([data.source,data.month,data.initial_balance,data.days.map(day=>[day.date,day.start_balance,day.end_balance,day.pnl,day.closed_count,day.wins,day.losses,day.trades.filter(t=>t.status==='closed').slice().sort((a,b)=>a.id.localeCompare(b.id))])]);
}
