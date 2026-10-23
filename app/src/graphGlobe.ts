// Perspective projection of a tilted Fibonacci sphere. Angle is in degrees.
export function globePoint(index:number,count:number,angle:number,tilt=.22){
 const y=count<=1?0:1-2*(index+.5)/count,r=Math.sqrt(Math.max(0,1-y*y)),a=index*2.3999632297,turn=angle*Math.PI/180;
 const x=Math.cos(a)*r,z=Math.sin(a)*r;
 const rx=x*Math.cos(turn)+z*Math.sin(turn),rz=z*Math.cos(turn)-x*Math.sin(turn);
 const ry=y*Math.cos(tilt)-rz*Math.sin(tilt),depth=y*Math.sin(tilt)+rz*Math.cos(tilt);
 const scale=650/(650-depth*190);
 return {x:420+rx*210*scale,y:260+ry*210*scale,scale,opacity:.42+.58*(depth+1)/2,depth};
}

export function closedTradeColor(status:string,pnl:number|undefined){
 if(status!=='closed'||pnl==null||!Number.isFinite(pnl))return '#e4af86';
 return pnl>0?'#5cdda6':pnl<0?'#f17c91':'#b9afc7';
}

// Square-root radius scaling keeps large P/L outliers from dominating the view.
export function tradeRadius(status:string,pnl:number|undefined,monthMax:number){
 if(status!=='closed'||pnl==null||!Number.isFinite(pnl))return 5;
 if(pnl===0||!Number.isFinite(monthMax)||monthMax<=0)return 4;
 return 4+10*Math.sqrt(Math.min(1,Math.abs(pnl)/monthMax));
}
