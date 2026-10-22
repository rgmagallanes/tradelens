// Perspective projection of a tilted Fibonacci sphere. Angle is in degrees.
export function globePoint(index:number,count:number,angle:number){
 const y=count<=1?0:1-2*(index+.5)/count,r=Math.sqrt(Math.max(0,1-y*y)),a=index*2.3999632297,turn=angle*Math.PI/180;
 const x=Math.cos(a)*r,z=Math.sin(a)*r;
 const rx=x*Math.cos(turn)+z*Math.sin(turn),rz=z*Math.cos(turn)-x*Math.sin(turn);
 const tilt=.22,ry=y*Math.cos(tilt)-rz*Math.sin(tilt),depth=y*Math.sin(tilt)+rz*Math.cos(tilt);
 const scale=650/(650-depth*190);
 return {x:420+rx*210*scale,y:260+ry*210*scale,scale,opacity:.42+.58*(depth+1)/2,depth};
}
