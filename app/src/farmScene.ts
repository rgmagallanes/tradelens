import {FARM_FACILITIES} from './farmProgress';
import * as T from 'three';
/** Decorative diorama; progress follows review checkpoints, never account equity. */
export function createFarm(el:HTMLElement){
 const renderer=new T.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.setClearColor(0x0b1b27,0);el.appendChild(renderer.domElement);
 const scene=new T.Scene(),camera=new T.OrthographicCamera(-15,15,10,-10,.1,100);camera.position.set(19,19,25);camera.lookAt(1,0,0);
 scene.add(new T.HemisphereLight(0xc5e3ee,0x5a5937,2.3));const sun=new T.DirectionalLight(0xffd59a,3.4);sun.position.set(-8,18,8);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-15,right:15,top:15,bottom:-15});sun.shadow.normalBias=.035;scene.add(sun);
 const materials=new Map<number,T.MeshStandardMaterial>();const mat=(c:number)=>{if(!materials.has(c))materials.set(c,new T.MeshStandardMaterial({color:c,roughness:.85}));return materials.get(c)!};
 const mesh=(g:T.BufferGeometry,c:number,x:number,y:number,z:number,parent:T.Object3D=scene)=>{const m=new T.Mesh(g,mat(c));m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m};
 const box=(x:number,y:number,z:number,w:number,h:number,d:number,c:number,p:T.Object3D=scene)=>mesh(new T.BoxGeometry(w,h,d),c,x,y,z,p);
 const ball=(x:number,y:number,z:number,r:number,c:number,p:T.Object3D=scene)=>mesh(new T.IcosahedronGeometry(r,1),c,x,y,z,p);
 const pole=(x:number,y:number,z:number,r:number,h:number,c:number,p:T.Object3D=scene)=>mesh(new T.CylinderGeometry(r,r,h,7),c,x,y,z,p);
 const beam=(a:T.Vector3,b:T.Vector3,width:number,c:number,p:T.Object3D=scene)=>{const m=box(0,0,0,width,a.distanceTo(b),width,c,p);m.position.copy(a).add(b).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),b.clone().sub(a).normalize());return m};
 const timber=0xa3703d,grass=0x778c45,cream=0xe8d6ac,roof=0x344551;
 // Raised island, grass, stone edging and winding gravel lanes.
 box(0,-.65,0,23,1.2,16,0x605844);box(0,-.03,0,23,.25,16,grass);
 for(let i=0;i<50;i++){const side=i%4,t=(i/4%13)/12;const x=side<2?-11.3+t*22.6:(side===2?-11.4:11.4),z=side<2?(side===0?-7.9:7.9):-7.8+t*15.6;const rock=ball(x,-.2,z,.42+(i%3)*.12,0x8c8d78);rock.scale.y=.8;}
 box(0,.12,3,21,.09,1.4,0xbba17a);box(1,.13,0,1.4,.1,13,0xbba17a);box(-5,.14,-1,7,.08,1.1,0xbba17a);
 for(let i=0;i<80;i++){const x=-10.5+(i*1.73%21),z=2.5+(i*.73%1);ball(x,.19,z,.035,0xdfcba3);}
 // Farmhouse: finished wing, slate gable roof, windows and doorway.
 box(-3,1.6,-2,4.2,3.1,3.5,cream);box(-3,.25,-2,4.6,.4,3.9,0x9b9988);
 const roofPanel=(x:number,z:number,w:number,d:number,y:number,c:number)=>{for(const side of [-1,1]){const m=box(x,y,z+side*d/4,w,.17,d*.65,c);m.rotation.x=side*Math.PI/5;}};
 roofPanel(-3,-2,4.7,4.4,3.55,roof);box(-4,4,-2,.6,1.7,.7,0xb7865b);box(-4,4.9,-2,.8,.2,.9,0xe5d0a6);
 for(const x of [-4.2,-2]){box(x,1.8,-.23,.7,.9,.09,0x6b502e);box(x,1.8,-.16,.53,.7,.04,0x8db4b8);box(x,1.8,-.12,.05,.7,.04,cream);box(x,1.8,-.12,.6,.05,.04,cream);}box(-3.1,.9,-.15,.7,1.6,.18,0x765035);box(-3.1,.19,.4,1.4,.2,.6,0xa4a290);
 // Extension is explicitly a construction site, with beams and scaffold.
 const construction=new T.Group();scene.add(construction);box(.05,.35,-2,2.2,.5,3.5,0xb9b39d,construction);
 for(const x of [-.9,1])for(const z of [-3.6,-.4]){box(x,1.8,z,.14,3.2,.14,timber,construction);}
 for(const z of [-3.6,-.4]){box(.05,3.4,z,2.2,.17,.17,timber,construction);beam(new T.Vector3(-1,3.4,z),new T.Vector3(.05,4.5,z),.13,timber,construction);beam(new T.Vector3(.05,4.5,z),new T.Vector3(1.1,3.4,z),.13,timber,construction);}
 box(.05,4.5,-2,.15,.15,3.5,timber,construction);for(let z=-3.5;z<-.3;z+=.55){beam(new T.Vector3(-1,3.4,z),new T.Vector3(.05,4.5,z),.09,timber,construction);beam(new T.Vector3(.05,4.5,z),new T.Vector3(1.1,3.4,z),.09,timber,construction);}
 for(const x of [1.5,2.2])for(const z of [-3.9,.1])box(x,1.7,z,.08,3.5,.08,0xb99561);
 for(const h of [1.1,2.3])box(1.85,h,-1.9,.9,.09,4.4,0xc89c61);
 for(let i=0;i<5;i++)box(2.9,.25+i*.12,-.5,1.5,.1,.21,timber);
 for(let i=0;i<5;i++)box(-1.2,.16+i*.15,1.8,1.7,.12,.55,0xc29a60);
 const roofPieces:T.Mesh[]=[];for(let i=0;i<6;i++){for(const side of [-1,1]){const piece=box(.05+side*.55,4,-3.5+i*.55,1.45,.1,.52,roof,construction);piece.rotation.z=-side*Math.PI/4;roofPieces.push(piece);}}
 // Barn, white trim, double doors and shed.
 box(6,1.4,-3.3,3.4,2.8,3.5,0x9e4236);roofPanel(6,-3.3,3.9,4.1,3.15,roof);
 box(6,1,-1.51,1.75,1.9,.1,0x74332b);for(const x of [5.1,6.9])box(x,1,-1.4,.1,2,.12,cream);box(6,2,-1.4,1.9,.1,.12,cream);box(6,1,-1.4,.08,1.9,.12,cream);
 for(const s of [-1,1])beam(new T.Vector3(6,1.85,-1.35),new T.Vector3(6+s*.8,.15,-1.35),.07,cream);
 for(let i=0;i<4;i++)box(8.2,.32+(i%2)*.6,-1.8-Math.floor(i/2)*.7,.6,.6,.6,0xb48d48);
 // Crop beds and vegetables, alternating leaves, tomatoes, carrots.
 const cropGroups:T.Group[]=[];
 // Ten distinct raised plots fill the available garden from left to right.
 for(let index=0;index<10;index++){const g=new T.Group();g.position.set(2.2+(index%5)*1.4,0,4.8+Math.floor(index/5)*1.35);scene.add(g);cropGroups.push(g);
 box(0,.18,0,1.15,.28,1.05,0x54472e,g);
 for(const side of [-1,1]){box(side*.6,.25,0,.09,.28,1.18,timber,g);box(0,.25,side*.56,1.28,.28,.09,timber,g);}
 for(let plant=0;plant<6;plant++){const x=-.36+(plant%3)*.36,z=-.25+Math.floor(plant/3)*.5;pole(x,.48,z,.025,.4,0x5d7430,g);for(const side of [-1,1]){const leaf=ball(x+side*.09,.48,z,.12,index%2?0x679443:0x3c773e,g);leaf.scale.y=.5;}ball(x,.65,z,.085,index%2?0xd7a03b:0xc7462b,g);}}
 // Pond and jetty, still water.
 const pond=mesh(new T.CylinderGeometry(2.2,2.2,.08,40),0x4b939b,-7,.15,4.7);pond.scale.z=.72;
 for(let i=0;i<14;i++){const a=i/14*Math.PI*2;ball(-7+Math.cos(a)*2.2,.25,4.7+Math.sin(a)*1.6,.3,0x9da38b);}
 for(let i=0;i<6;i++)box(-5.2,.35,4.1+i*.25,1.25,.1,.19,timber);for(const z of [4,5.5])pole(-5.7,.35,z,.07,.9,timber);
 // Fence rails and pasture.
 for(let x=-10;x<=10;x+=2){for(const z of [-6.8,7.1]){box(x,.65,z,.12,1.2,.12,timber);if(x<10)for(const h of [.45,.9])box(x+1,h,z,2,.09,.09,0xc29b61);}}
 for(let z=-6;z<3;z+=2){box(10,.65,z,.12,1.2,.12,timber);for(const h of [.45,.9])box(10,h,z+1,.09,.09,2,0xc29b61);}
 // Orchard trees with visible fruit and slow wind sway.
 const trees:T.Group[]=[];
 for(const [i,x,z] of [[0,-8,-4],[1,-9,-1],[2,-6,-5],[3,8,-6],[4,10,4],[5,-10,6]]){const g=new T.Group();g.position.set(x,0,z);scene.add(g);trees.push(g);pole(0,1.1,0,.18,2.2,timber,g);for(let j=0;j<5;j++)ball(Math.sin(j*2)*.55,2.4+(j%2)*.5,Math.cos(j*2)*.5,.85,j%2?0x739348:0x4e793a,g);for(let j=0;j<6;j++)ball(Math.sin(j*2)*.9,2.3+(j%3)*.3,Math.cos(j*2)*.85,.13,0xb9472e,g);void i;}
 // Tractor and trailer.
 const tractor=new T.Group();tractor.position.set(6.6,.25,1.9);scene.add(tractor);box(0,.65,0,1.8,.55,.85,0xc2603d,tractor);box(-.45,1.3,0,.9,.12,1.2,0xba5537,tractor);for(const z of [-.45,.45])for(const x of [-.8,.65]){const wheel=mesh(new T.CylinderGeometry(x<0?.49:.31,x<0?.49:.31,.24,12),0x273233,x,.35,z,tractor);wheel.rotation.x=Math.PI/2;const hub=mesh(new T.CylinderGeometry(.15,.15,.26,10),0xd8b276,x,.35,z,tractor);hub.rotation.x=Math.PI/2;}box(-.6,.8,0,.3,.5,.5,0x514133,tractor);pole(.65,1.1,.15,.05,.8,0x3e4946,tractor);box(-2,.5,0,1.3,.4,1.1,0x9d824b,tractor);
 // Workers: articulated limbs; individual routes and jobs.
 const workers:{root:T.Group;legs:T.Group[];arms:T.Group[];task:string;phase:number}[]=[];
 function worker(x:number,z:number,task:string,phase:number){const root=new T.Group();root.position.set(x,.2,z);scene.add(root);box(0,.7,0,.38,.48,.26,0x4777a0,root);ball(0,1.12,0,.19,0xd8ad80,root);pole(0,1.3,0,.24,.08,0xe6b94f,root);ball(0,1.31,0,.19,0xe7bd58,root);const legs:T.Group[]=[],arms:T.Group[]=[];for(const s of [-1,1]){const leg=new T.Group();leg.position.set(s*.1,.5,0);root.add(leg);box(0,-.2,0,.14,.4,.15,0x364d61,leg);box(0,-.43,.04,.17,.1,.27,0x614d39,leg);legs.push(leg);const arm=new T.Group();arm.position.set(s*.25,.9,0);root.add(arm);box(0,-.17,0,.12,.32,.13,0x4777a0,arm);ball(0,-.37,0,.075,0xd8ad80,arm);arms.push(arm);}if(task==='carry')box(0,.85,.42,1.2,.12,.2,timber,root);if(task==='hammer'){box(.25,.55,.16,.06,.4,.06,timber,arms[1]);box(.25,.75,.16,.26,.1,.1,0x89918c,arms[1]);}if(task==='water'){box(.35,.5,.35,.3,.28,.28,0x82aab0,root);}if(task==='barrow'){box(0,.45,.65,.7,.25,.7,0x7a9857,root);pole(0,.3,1,.16,.15,0x323d35,root).rotation.x=Math.PI/2;for(const s of [-1,1])box(s*.3,.55,.22,.05,.05,.7,timber,root);}
 workers.push({root,legs,arms,task,phase});return root;}
 worker(-3,2.8,'carry',0);worker(1.85,-1,'hammer',1).position.y=2.35;worker(2.8,5.2,'water',2);worker(-.1,3,'barrow',3);worker(8,-.8,'carry',4);
 const fireCrew=[worker(4.5,0,'fire',0),worker(7.6,.4,'fire',2)];
 fireCrew.forEach(g=>{g.rotation.y=Math.PI;pole(.3,.55,.25,.14,.3,0x879da0,g);});
 const fire=new T.Group();scene.add(fire);
 const flames:T.Mesh[]=[];for(let i=0;i<12;i++){const c=i%2?0xffc94c:0xff6b1a;const f=mesh(new T.ConeGeometry(.27+(i%3)*.08,1.2+(i%4)*.35,6),c,4.9+(i%4)*.7,3.5+Math.floor(i/4)*.3,-1.8-Math.floor(i/4)*.6,fire);f.material.emissive.setHex(c);f.material.emissiveIntensity=.8;flames.push(f);}
 const fireSmoke=Array.from({length:7},(_,i)=>ball(5.8+Math.sin(i)*.4,4+i*.38,-3,.28+i*.045,0x777b77,fire));
 const water=Array.from({length:18},(_,i)=>{const t=i/17;return ball(4.5+t*1.2,1+Math.sin(t*Math.PI)*1.8,-t*2.2,.055,0xa9d9df,fire)});
 // Animated animals, not financial indicators.
 const animals:{g:T.Group;kind:string;phase:number;legs:T.Mesh[];home:T.Vector3}[]=[];
 function animal(x:number,z:number,kind:string,phase:number){const g=new T.Group();g.position.set(x,.25,z);scene.add(g);const cow=kind==='cow',duck=kind==='duck',c=cow?0xe9dfc4:duck?0xf1e4c5:0xe6d5b2;const body=ball(0,cow?.65:.25,0,cow?.6:.22,c,g);body.scale.set(cow?1.4:1.2,cow?.85:.9,.8);ball(cow?.65:.22,cow?.9:.42,0,cow?.27:.14,c,g);const beak=box(cow?.89:.36,cow?.85:.42,0,cow?.2:.12,.08,.12,cow?0xb7a18e:0xdca23e,g);void beak;if(!cow&&!duck)ball(.22,.55,0,.07,0xbe4332,g);const legs:T.Mesh[]=[];if(!duck)for(const a of [-1,1])for(const b of [-1,1])legs.push(box(a*(cow?.45:.1),cow?.22:.08,b*(cow?.25:.1),cow?.1:.03,cow?.45:.16,cow?.1:.03,0x7d684c,g));if(cow){ball(-.2,.9,.18,.22,0x514c41,g);ball(.3,.8,-.28,.25,0x514c41,g);}animals.push({g,kind,phase,legs,home:g.position.clone()});}
 animal(8,5,'chicken',0);animal(8.8,4.7,'chicken',2);animal(9.3,5.5,'chicken',4);animal(-7,4.7,'duck',0);animal(-7.7,4.3,'duck',2);animal(-8,.9,'cow',1);
 // Smoke puffs drift above chimney.
 const smoke=Array.from({length:4},(_,i)=>ball(-4,5+i*.35,-2,.16+i*.07,0xb8b8a4));smoke.forEach(s=>{s.castShadow=false});
 // Widen the grounds and spacing. Preserve the proportions of living figures.
 for(const object of scene.children){if(object instanceof T.Light)continue;object.position.x*=1.22;if(object instanceof T.Mesh)object.scale.x*=1.22;else if(object===construction)object.scale.x*=1.22;}
 // Barn structural pieces get a wider facade around their new center.
 for(const object of scene.children){if(object instanceof T.Mesh&&object.position.z>=-5.4&&object.position.z<=-1.3&&object.position.x>5.5&&object.position.x<9.5){object.position.x=7.32+(object.position.x-7.32)*1.18;object.scale.x*=1.18;}}
 // Small, slow cloud groups frame the rear of the scene without covering the barn.
 const clouds=Array.from({length:2},(_,i)=>{const g=new T.Group();g.position.set(-8+i*13,7+i,-7);scene.add(g);for(let j=0;j<3;j++){const puff=ball(j*.65,Math.sin(j)*.2,0,.65,0xd7ded6,g);puff.scale.set(1.4,.45,.65);puff.castShadow=false;}return g});
 animals.forEach(a=>a.home.x*=1.22);
 const routines=workers.map(w=>({home:w.root.position.clone(),goal:w.root.position.clone(),until:0,mode:'rest' as 'rest'|'walk'|'work'}));
 const choose=(items:number[])=>items[Math.floor(Math.random()*items.length)];
 // Expansion plots sit beyond the original northern boundary.
 const estates=FARM_FACILITIES.map((facility,i)=>{const root=new T.Group();root.position.set(-10+i*6.6,0,-10.7);scene.add(root);
 box(0,-.65,0,6.6,1.2,5.5,0x605844,root);box(0,-.03,0,6.6,.25,5.5,grass,root);box(0,.13,1.9,6.6,.08,.8,0xbba17a,root);box(0,.14,2.35,.9,.09,1,0xbba17a,root);
 for(const x of [-3,0,3]){box(x,.55,-2.5,.12,1,.12,timber,root);if(x<3)box(x+1.5,.75,-2.5,3,.09,.09,timber,root);}
 const building=new T.Group();root.add(building);
 if(i===0){box(0,1.1,0,3.8,2.1,2.4,0x8bb8af,building);for(const x of [-2,-1,0,1,2]){box(x,1.15,1.25,.09,2.3,.09,cream,building);box(x,1.15,-1.25,.09,2.3,.09,cream,building);}for(const side of [-1,1]){const pane=box(0,2.5,side*.65,4.2,.12,1.65,0xb4d4c5,building);pane.rotation.x=side*Math.PI/5;}box(0,1,1.3,.75,1.8,.1,0x466b58,building);}
 if(i===1){box(0,.5,0,2.5,.9,2,0x705139,building);box(0,1.4,0,2.7,1.3,2.1,0xba8550,building);box(0,2.15,0,3.1,.2,2.5,roof,building);box(0,1.2,1.1,.6,.65,.1,0x342b25,building);const ramp=box(0,.6,1.8,.7,.1,1.6,timber,building);ramp.rotation.x=.5;for(const x of [-1,1])ball(x,.3,1.8,.2,cream,building);}
 if(i===2){pole(0,2,0,1.3,4,0xa8b4ae,building);mesh(new T.ConeGeometry(1.5,1.1,16),roof,0,4.5,0,building);for(const y of [1,2,3]){const ring=mesh(new T.TorusGeometry(1.31,.045,5,24),0x54686d,0,y,0,building);ring.rotation.x=Math.PI/2;}box(0,.6,1.3,.6,1.2,.1,0x526368,building);}
 if(i===3){box(0,1.4,0,4.5,2.8,2.8,0xb6a47e,building);box(0,2.9,0,4.9,.2,3.2,roof,building);box(0,1.25,1.45,3.4,2.4,.1,0x344551,building);for(const x of [-1.6,0,1.6])box(x,1.3,1.53,.08,2.5,.08,cream,building);}
 root.visible=false;return {root,building,threshold:facility.threshold,amount:0};});
 const target=new T.Vector3(1,0,0),focusTarget=target.clone();let focusZoom=1,focusing=false;
 let frame=0,time=0,last=0,visible=true,dead=false;
 const render=(now:number)=>{if(dead)return;const dt=last?Math.min(.05,(now-last)/1000):0;last=now;const paused=el.dataset.paused==='true',loss=el.dataset.loss==='true';fire.visible=loss;if(!paused&&visible&&!document.hidden)time+=dt;
 workers.forEach((w,i)=>{const t=time+w.phase,state=routines[i];w.root.visible=w.task==='fire'?loss:!loss;if(w.task==='fire'){w.arms.forEach((a,j)=>a.rotation.x=-.9+Math.sin(t*2+j)*.12);return;}
 if(time>=state.until){if(state.mode==='walk'){state.mode='work';state.until=time+4+Math.random()*7}else if(state.mode==='work'){state.mode='rest';state.until=time+2+Math.random()*5}else{state.mode='walk';state.goal.copy(state.home);if(w.task==='hammer'){state.goal.z=choose([-3,-2,-1])}else if(w.task==='water'){state.goal.x=choose([2,4,6,8])*1.22;state.goal.z=choose([4.2,5,6])}else{state.goal.x=choose([-4,-1,3,7])*1.22;state.goal.z=2.8;}state.until=Infinity;}}
 const walking=state.mode==='walk';if(walking){const delta=state.goal.clone().sub(w.root.position),distance=delta.length(),step=(!paused?dt:0)*.7;if(distance<.04){state.until=time}else{w.root.position.addScaledVector(delta.normalize(),Math.min(step,distance));w.root.rotation.y=Math.atan2(delta.x,delta.z)}}
 w.legs.forEach((leg,j)=>leg.rotation.x=walking?Math.sin(t*5+j*Math.PI)*.35:0);
 w.arms.forEach((arm,j)=>{arm.rotation.x=state.mode==='rest'?-.1:walking?-.5+Math.sin(t*5+j*Math.PI)*.12:-.65+Math.sin(t*(w.task==='hammer'?4:1.4)+j)*.25});
 });
 flames.forEach((f,i)=>{f.scale.y=.8+Math.sin(time*4+i)*.2;f.rotation.z=Math.sin(time*3+i)*.1;});fireSmoke.forEach((s,i)=>{s.position.y=4+((time*.45+i*.38)%3);s.position.x=5.8+Math.sin(time*.4+i)*.4;});water.forEach((w,i)=>{w.scale.setScalar(.65+Math.sin(time*5+i)*.3);});
 animals.forEach(a=>{const t=time+a.phase;if(a.kind==='duck'){a.g.position.x=a.home.x+Math.sin(t*.4)*.55;a.g.position.z=a.home.z+Math.cos(t*.4)*.3;a.g.rotation.y=-t*.4;}else{a.g.position.x=a.home.x+Math.sin(t*.25)*.6;a.g.rotation.y=Math.cos(t*.25)>0?0:Math.PI;a.g.rotation.z=a.kind==='chicken'?Math.sin(t*2)*.08:Math.sin(t*.4)*.025;a.legs.forEach((l,j)=>l.rotation.z=Math.sin(t*3+j*Math.PI)*.15);}});
 clouds.forEach((g,i)=>{g.position.x=-8+i*13+Math.sin(time*.035+i)*1.2;});
 trees.forEach((g,i)=>g.rotation.z=Math.sin(time*.6+i)*.009);smoke.forEach((s,i)=>{s.position.y=5+((time*.25+i*.4)%1.6);s.position.x=-4+Math.sin(time*.3+i)*.15;});
 estates.forEach(estate=>{const unlocked=Number(el.dataset.earned||0)>=estate.threshold;estate.root.visible=unlocked;if(!unlocked){estate.amount=0;return}estate.amount=paused?1:Math.min(1,estate.amount+dt*1.5);estate.building.scale.y=Math.max(.01,1-Math.pow(1-estate.amount,3));});
 const progress=Math.min(1,Math.max(0,Number(el.dataset.progress||0)));cropGroups.forEach((g,i)=>{g.scale.y=.65+progress*.35;g.visible=i<Math.max(2,Math.min(10,Number(el.dataset.beds||2)));});roofPieces.forEach((piece,i)=>{piece.visible=progress>(i+1)/15;});
 if(focusing){const immediate=paused||matchMedia('(prefers-reduced-motion: reduce)').matches,k=immediate?1:1-Math.exp(-dt*7);target.lerp(focusTarget,k);camera.zoom+=(focusZoom-camera.zoom)*k;if(target.distanceTo(focusTarget)<.005&&Math.abs(camera.zoom-focusZoom)<.002){target.copy(focusTarget);camera.zoom=focusZoom;focusing=false}placeCamera();}
 renderer.render(scene,camera);if((!paused||focusing)&&visible&&!document.hidden)frame=requestAnimationFrame(render);};
 const restart=()=>{cancelAnimationFrame(frame);last=0;frame=requestAnimationFrame(render)};
 // Camera interaction is independent of ambient animation, including when paused.
 const canvas=renderer.domElement,homeYaw=Math.atan2(18,25),homePitch=.55;
 let yaw=homeYaw,pitch=homePitch,held:{id:number;x:number;y:number;distance:number}|null=null;
 function placeCamera(){const radius=36;camera.position.set(target.x+radius*Math.cos(pitch)*Math.sin(yaw),target.y+radius*Math.sin(pitch),target.z+radius*Math.cos(pitch)*Math.cos(yaw));camera.lookAt(target);camera.updateProjectionMatrix()}
 const updateCamera=()=>{placeCamera();restart()};
 const places=[{name:'barn',center:new T.Vector3(7.32,1,-3.3),box:new T.Box3(new T.Vector3(4.7,0,-5.4),new T.Vector3(9.9,4,-1.3))},{name:'house',center:new T.Vector3(-3.66,1,-2),box:new T.Box3(new T.Vector3(-6.6,0,-4.2),new T.Vector3(-.7,4.5,.2))},{name:'orchard',center:new T.Vector3(-9.76,1,-4),box:new T.Box3(new T.Vector3(-12.2,0,-6),new T.Vector3(-7.3,3.5,-.5))}];
 const focus=(name:string)=>{const place=places.find(p=>p.name===name);if(!place)return;focusTarget.copy(place.center);focusZoom=1.4;focusing=true;restart()};
 const focusEvent=(event:Event)=>focus((event as CustomEvent<string>).detail);el.addEventListener('farm-focus',focusEvent);
 const down=(e:PointerEvent)=>{if(e.button!==0||held)return;focusing=false;held={id:e.pointerId,x:e.clientX,y:e.clientY,distance:0};canvas.setPointerCapture(e.pointerId)};
 const move=(e:PointerEvent)=>{if(!held||held.id!==e.pointerId)return;const dx=e.clientX-held.x,dy=e.clientY-held.y;held.distance+=Math.hypot(dx,dy);held.x=e.clientX;held.y=e.clientY;yaw=Math.max(homeYaw-.8,Math.min(homeYaw+.8,yaw-dx*.004));pitch=Math.max(.35,Math.min(.95,pitch+dy*.003));updateCamera()};
 const up=(e:PointerEvent)=>{if(!held||held.id!==e.pointerId)return;const click=held.distance<6;held=null;if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId);if(!click)return;const rect=canvas.getBoundingClientRect(),ray=new T.Raycaster();ray.setFromCamera(new T.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),camera);const hits=places.map(place=>({place,hit:ray.ray.intersectBox(place.box,new T.Vector3())})).filter(item=>item.hit).sort((a,b)=>ray.ray.origin.distanceTo(a.hit!)-ray.ray.origin.distanceTo(b.hit!));if(hits[0]){focus(hits[0].place.name);el.dispatchEvent(new CustomEvent('farm-place-select',{detail:hits[0].place.name}))}};
 const cancel=()=>{held=null};
 const wheel=(e:WheelEvent)=>{e.preventDefault();focusing=false;camera.zoom=Math.max(.85,Math.min(1.65,camera.zoom*Math.exp(-e.deltaY*.001)));updateCamera()};
 const reset=()=>{yaw=homeYaw;pitch=homePitch;focusTarget.set(1,0,0);focusZoom=1;focusing=true;restart()};
 const key=(e:KeyboardEvent)=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','Home'].includes(e.key))return;e.preventDefault();if(e.key==='Home'){reset();return}if(e.key==='ArrowLeft')yaw-=.08;if(e.key==='ArrowRight')yaw+=.08;if(e.key==='ArrowUp')pitch+=.06;if(e.key==='ArrowDown')pitch-=.06;if(e.key==='+')camera.zoom+=.1;if(e.key==='-')camera.zoom-=.1;yaw=Math.max(homeYaw-.8,Math.min(homeYaw+.8,yaw));pitch=Math.max(.35,Math.min(.95,pitch));camera.zoom=Math.max(.85,Math.min(1.65,camera.zoom));updateCamera()};
 canvas.tabIndex=0;canvas.setAttribute('aria-label','Farm camera. Drag or use arrow keys to orbit, scroll or use plus and minus to zoom. Home resets camera.');
 canvas.addEventListener('pointerdown',down);canvas.addEventListener('pointermove',move);canvas.addEventListener('pointerup',up);canvas.addEventListener('pointercancel',cancel);canvas.addEventListener('lostpointercapture',cancel);canvas.addEventListener('wheel',wheel,{passive:false});canvas.addEventListener('keydown',key);el.addEventListener('farm-reset-camera',reset);updateCamera();

 const resize=new ResizeObserver(()=>{const w=el.clientWidth,h=el.clientHeight;renderer.setSize(w,h);const aspect=w/h;const height=Math.max(24,42/aspect);camera.left=-height*aspect/2;camera.right=height*aspect/2;camera.top=height/2;camera.bottom=-height/2;camera.updateProjectionMatrix();restart()});resize.observe(el);
 const mutations=new MutationObserver(restart);mutations.observe(el,{attributes:true,attributeFilter:['data-paused','data-progress','data-loss','data-beds','data-earned']});const intersection=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;restart()});intersection.observe(el);document.addEventListener('visibilitychange',restart);
 const lost=(e:Event)=>{e.preventDefault();el.dispatchEvent(new Event('farm-unavailable'))};renderer.domElement.addEventListener('webglcontextlost',lost);restart();
 return()=>{dead=true;cancelAnimationFrame(frame);resize.disconnect();mutations.disconnect();intersection.disconnect();document.removeEventListener('visibilitychange',restart);canvas.removeEventListener('pointerdown',down);canvas.removeEventListener('pointermove',move);canvas.removeEventListener('pointerup',up);canvas.removeEventListener('pointercancel',cancel);canvas.removeEventListener('lostpointercapture',cancel);canvas.removeEventListener('wheel',wheel);canvas.removeEventListener('keydown',key);el.removeEventListener('farm-reset-camera',reset);el.removeEventListener('farm-focus',focusEvent);renderer.domElement.removeEventListener('webglcontextlost',lost);scene.traverse(o=>{if(o instanceof T.Mesh)o.geometry.dispose()});materials.forEach(m=>m.dispose());renderer.dispose();renderer.domElement.remove();};
}
