export type GapBar={time:number;open:number;high:number;low:number;close:number;closed?:boolean};
export type FairValueGap={time:number;lower:number;upper:number;side:'bullish'|'bearish'};
/** Wick-to-wick three-candle imbalance; confirmation and full-fill use closed bars only. */
export function fairValueGaps(bars:GapBar[],interval:number,sample=false):FairValueGap[]{
 const gaps:FairValueGap[]=[];
 for(let i=0;i<bars.length;i++){
  const c=bars[i];
  if(!(c.closed===true||(sample&&c.closed!==false)))continue;
  if(![c.open,c.high,c.low,c.close,c.time].every(Number.isFinite)||c.high<c.low)continue;
  for(let j=gaps.length-1;j>=0;j--)if(gaps[j].side==='bullish'?c.low<=gaps[j].lower:c.high>=gaps[j].upper)gaps.splice(j,1);
  if(i<2)continue;
  const a=bars[i-2],b=bars[i-1];
  if(![a,b].every(x=>(x.closed===true||(sample&&x.closed!==false))&&[x.open,x.high,x.low,x.close,x.time].every(Number.isFinite)&&x.high>=x.low)||b.time-a.time!==interval||c.time-b.time!==interval)continue;
  if(c.low>a.high)gaps.push({time:c.time,lower:a.high,upper:c.low,side:'bullish'});
  else if(c.high<a.low)gaps.push({time:c.time,lower:c.high,upper:a.low,side:'bearish'});
 }
 return gaps.slice(-30);
}
/** Native chart primitive follows zoom, pan, resizing and the price scale. */
export class FVGOverlay{
 private chart:any;private series:any;private update:(()=>void)|undefined;private gaps:FairValueGap[]=[];
 attached(p:any){this.chart=p.chart;this.series=p.series;this.update=p.requestUpdate;}
 detached(){this.update=undefined;this.chart=undefined;this.series=undefined;}
 setGaps(gaps:FairValueGap[]){this.gaps=gaps;this.update?.();}
 paneViews(){return [{zOrder:()=>'bottom',renderer:()=>({draw:(target:any)=>target.useBitmapCoordinateSpace((scope:any)=>{
  if(!this.chart||!this.series)return;
  const {context:ctx,horizontalPixelRatio:rx,verticalPixelRatio:ry,bitmapSize}=scope;
  for(const gap of this.gaps){const x=this.chart.timeScale().timeToCoordinate(gap.time),top=this.series.priceToCoordinate(gap.upper),bottom=this.series.priceToCoordinate(gap.lower);if(x===null||top===null||bottom===null)continue;
   const left=Math.max(0,x*rx),y=top*ry,h=Math.max(1,(bottom-top)*ry),w=bitmapSize.width-left;if(w<=0)continue;
   ctx.fillStyle=gap.side==='bullish'?'rgba(38,166,154,0.17)':'rgba(239,83,80,0.17)';ctx.fillRect(left,y,w,h);
   ctx.strokeStyle=gap.side==='bullish'?'rgba(70,205,168,0.65)':'rgba(242,125,139,0.65)';ctx.lineWidth=ry;ctx.setLineDash([4*rx,3*rx]);ctx.strokeRect(left,y,w,h);ctx.setLineDash([]);
   if(h>15*ry){ctx.font=`${10*ry}px sans-serif`;ctx.fillStyle=gap.side==='bullish'?'#70dfac':'#f28da0';ctx.fillText(`${gap.side==='bullish'?'Bull':'Bear'} FVG`,left+5*rx,y+12*ry);}
  }
 })})}];}
}
