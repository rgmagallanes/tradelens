import {useLayoutEffect} from 'react';

// Rank newly mounted panels by their rendered rows, including responsive layouts.
export function usePanelOrder(){
 useLayoutEffect(()=>{
  const main=document.querySelector('.app main');if(!main)return;
  const seen=new WeakSet<Element>();
  const selector='.td-panel,.td-metric,.workspace .panel,.trading-journal .j-card,.trading-journal .j-sourcebar,.trading-journal .j-report,.farm-dashboard';
  const rank=()=>{
   const panels=Array.from(main.querySelectorAll<HTMLElement>(selector)).filter(el=>!el.parentElement?.closest(selector));
   const fresh=panels.filter(el=>!seen.has(el));if(!fresh.length)return;
   const positions= fresh.map(el=>{const rect=el.getBoundingClientRect();const transform=getComputedStyle(el).transform;const dy=transform==='none'?0:new DOMMatrixReadOnly(transform).m42;return {el,top:rect.top-dy,left:rect.left}}).sort((a,b)=>a.top-b.top||a.left-b.left);
   const rows:typeof positions[]=[];
   for(const item of positions){const row=rows.at(-1);if(row&&Math.abs(row[0].top-item.top)<24)row.push(item);else rows.push([item])}
   let index=0;for(const row of rows){row.sort((a,b)=>a.left-b.left);for(const {el} of row){el.style.setProperty('--panel-delay',`${Math.min(index++,8)*120}ms`);seen.add(el)}}
  };
  rank();const observer=new MutationObserver(records=>{if(records.some(r=>Array.from(r.addedNodes).some(n=>n.nodeType===1)))rank()});
  observer.observe(main,{childList:true,subtree:true});return()=>observer.disconnect();
 },[]);
}
