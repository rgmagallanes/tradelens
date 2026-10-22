import type {JournalData,Trade} from './journalTypes';
export type GraphNode={id:string;kind:'core'|'strategy'|'symbol'|'trade'|'note';label:string;detail:string;trade?:Trade;day?:string;x:number;y:number};
export function buildJournalGraph(data:JournalData){
 const nodes:GraphNode[]=[{id:'core',kind:'core',label:'Journal',detail:'Connections from recorded fields only.',x:420,y:260}],edges:{from:string;to:string}[]=[];
 const seen=new Set<string>();const trades=data.days.flatMap(d=>d.trades.map(t=>({t,day:d.date}))).filter(({t})=>{if(seen.has(t.id))return false;seen.add(t.id);return true}).sort((a,b)=>b.t.opened_at-a.t.opened_at);
 const selected=trades.slice(0,120);
 function group(kind:'strategy'|'symbol',label:string){const id=kind+':'+label;if(!nodes.some(n=>n.id===id)){nodes.push({id,kind,label,detail:kind==='strategy'?'Recorded strategy label.':'Recorded instrument.',x:0,y:0});edges.push({from:'core',to:id})}return id}
 for(const {t,day} of selected){const id='trade:'+t.id;nodes.push({id,kind:'trade',label:t.side.toUpperCase()+' '+t.symbol,detail:t.note||'No trade note recorded.',trade:t,day,x:0,y:0});edges.push({from:group('symbol',t.symbol),to:id},{from:group('strategy',t.strategy.trim()||'Unclassified'),to:id});if(t.note.trim()){const note='note:'+t.id;nodes.push({id:note,kind:'note',label:'Trade note',detail:t.note,day,x:0,y:0});edges.push({from:id,to:note})}}
 for(const d of data.days){if(d.note?.trim()){const id='reflection:'+d.date;nodes.push({id,kind:'note',label:'Daily reflection · '+d.date,detail:d.note,day:d.date,x:0,y:0});edges.push({from:'core',to:id});for(const n of nodes.filter(n=>n.kind==='trade'&&n.day===d.date))edges.push({from:id,to:n.id})}}
 // Golden-angle rings give every recorded node a stable, reproducible position.
 for(const kind of ['strategy','symbol','trade','note']){const ring=nodes.filter(n=>n.kind===kind);ring.forEach((n,i)=>{const a=i*2.399963+({'strategy':0,'symbol':1,'trade':2,'note':3}[kind]||0);const radius=kind==='trade'?140+(i%5)*17:kind==='note'?215:95;n.x=420+Math.cos(a)*radius*1.35;n.y=260+Math.sin(a)*radius*.87})}
 return {nodes,edges,total:trades.length,shown:selected.length};
}
