export type ElasticPoint={x:number;y:number;vx:number;vy:number};
export type ElasticState={points:Map<string,ElasticPoint>;adjacency:Map<string,string[]>;parents:Map<string,string>;depth:Map<string,number>;satellites:Map<string,string>;held:string|null;active:boolean;releasedFor:number};
export function createElastic(ids:string[],edges:{from:string;to:string}[],satellites:Map<string,string>=new Map()):ElasticState{
 const adjacency=new Map(ids.map(id=>[id,[] as string[]]));for(const e of edges){adjacency.get(e.from)?.push(e.to);adjacency.get(e.to)?.push(e.from)}
 return {points:new Map(ids.map(id=>[id,{x:0,y:0,vx:0,vy:0}])),adjacency,satellites,parents:new Map(),depth:new Map(),held:null,active:false,releasedFor:0};
}
export function grabElastic(s:ElasticState,id:string){
 if(!s.points.has(id))return;s.held=id;s.active=true;s.releasedFor=0;s.parents.clear();s.depth=new Map([[id,0]]);const queue=[id];
 for(let i=0;i<queue.length;i++){const parent=queue[i];for(const next of s.adjacency.get(parent)||[])if(!s.depth.has(next)){s.depth.set(next,s.depth.get(parent)!+1);s.parents.set(next,parent);queue.push(next)}}
}
export function moveElastic(s:ElasticState,x:number,y:number){if(!s.held)return;const p=s.points.get(s.held)!;p.x=Math.max(-300,Math.min(300,x));p.y=Math.max(-240,Math.min(240,y));p.vx=p.vy=0}
export function resetElastic(s:ElasticState){for(const p of s.points.values())p.x=p.y=p.vx=p.vy=0;s.held=null;s.active=false;s.releasedFor=0}
export function releaseElastic(s:ElasticState,reduced=false){s.held=null;s.releasedFor=0;if(reduced)resetElastic(s)}
export function stepElastic(s:ElasticState,dt:number){
 if(!s.active)return false;dt=Math.max(0,Math.min(dt,.05));if(!s.held)s.releasedFor+=dt;
 const steps=Math.max(1,Math.ceil(dt/(1/120))),h=dt/steps;
 for(let step=0;step<steps;step++){
  // Snapshot each step so influence travels outward, rather than through iteration order.
  const prior=new Map([...s.points].map(([id,p])=>[id,{x:p.x,y:p.y}]));
  for(const [id,p] of s.points){if(id===s.held)continue;const parent=prior.get(s.parents.get(id)||''),held=prior.get(s.held||''),depth=s.depth.get(id)||5;
   const owner=prior.get(s.satellites.get(id)||'');
   const target=owner?{x:owner.x,y:owner.y}:s.held?(parent?{x:parent.x*.7,y:parent.y*.7}:{x:(held?.x||0)*.035,y:(held?.y||0)*.035}):{x:0,y:0};
   const frequency=owner?24:s.held?13/(1+Math.min(depth,6)*.22):11,stiffness=frequency*frequency,damping=frequency*1.95;
   p.vx+=(stiffness*(target.x-p.x)-damping*p.vx)*h;p.vy+=(stiffness*(target.y-p.y)-damping*p.vy)*h;p.x+=p.vx*h;p.y+=p.vy*h;
  }
 }
 if(!s.held&&(s.releasedFor>3||[...s.points.values()].every(p=>Math.hypot(p.x,p.y)<.08&&Math.hypot(p.vx,p.vy)<.15)))resetElastic(s);
 return s.active;
}

// Move spring rest positions with the new globe orientation, preserving visible
// positions as lag offsets. Release settles toward this new orientation, not the old one.
export function rebaseElastic(s:ElasticState,before:Map<string,{x:number;y:number}>,after:Map<string,{x:number;y:number}>,immediate=false){
 for(const [id,p] of s.points){const a=before.get(id),b=after.get(id);if(immediate){p.x=p.y=p.vx=p.vy=0}else if(id===s.held){p.vx=p.vy=0}else if(a&&b){p.x+=a.x-b.x;p.y+=a.y-b.y}}
}
