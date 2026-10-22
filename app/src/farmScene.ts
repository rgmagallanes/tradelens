import * as T from 'three';
/** Decorative diorama; progress follows review checkpoints, never account equity. */
export function createFarm(el:HTMLElement){
 const renderer=new T.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.setClearColor(0x0b1b27,0);el.appendChild(renderer.domElement);
 const scene=new T.Scene(),camera=new T.OrthographicCamera(-15,15,10,-10,.1,100);camera.position.set(19,19,25);camera.lookAt(0,0,0);
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
 for(let row=0;row<4;row++){const g=new T.Group();scene.add(g);cropGroups.push(g);box(4.8,.15,4.7+row*.7,7.2,.2,.53,0x54472e,g);for(let i=0;i<12;i++){const x=1.6+i*.57,z=4.7+row*.7;pole(x,.43,z,.035,.5,0x5d7430,g);for(const s of [-1,1]){const leaf=ball(x+s*.12,.4,z,.16,row%2?0x679443:0x3c773e,g);leaf.scale.y=.5;}if(row%2===0)ball(x,.62,z,.1,0xc7462b,g);else ball(x,.3,z,.08,0xd7a03b,g);}}
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
 let frame=0,time=0,last=0,visible=true,dead=false;
 const render=(now:number)=>{if(dead)return;const dt=last?Math.min(.05,(now-last)/1000):0;last=now;const paused=el.dataset.paused==='true',loss=el.dataset.loss==='true';fire.visible=loss;if(!paused&&visible&&!document.hidden)time+=dt;
 workers.forEach((w,i)=>{const t=time+w.phase;w.root.visible=w.task==='fire'?loss:!loss;if(w.task==='fire'){w.arms.forEach((a,j)=>a.rotation.x=-.9+Math.sin(t*2+j)*.12);return;}if(w.task==='carry'||w.task==='barrow'){const direction=Math.cos(t*.35)>=0?1:-1;w.root.position.x=(i===4?7:-2)+Math.sin(t*.35)*(i===4?1.2:3);w.root.rotation.y=direction*Math.PI/2;w.legs.forEach((l,j)=>l.rotation.x=Math.sin(t*6+j*Math.PI)*.5);w.arms.forEach((a,j)=>a.rotation.x=w.task==='carry'?-.8:Math.sin(t*6+j*Math.PI)*.15-.6);}else if(w.task==='hammer'){w.arms[1].rotation.x=-1+Math.sin(t*5)*.7;}else{w.root.rotation.y=-.5;w.arms[1].rotation.x=-.7+Math.sin(t)*.1;} });
 flames.forEach((f,i)=>{f.scale.y=.8+Math.sin(time*4+i)*.2;f.rotation.z=Math.sin(time*3+i)*.1;});fireSmoke.forEach((s,i)=>{s.position.y=4+((time*.45+i*.38)%3);s.position.x=5.8+Math.sin(time*.4+i)*.4;});water.forEach((w,i)=>{w.scale.setScalar(.65+Math.sin(time*5+i)*.3);});
 animals.forEach(a=>{const t=time+a.phase;if(a.kind==='duck'){a.g.position.x=a.home.x+Math.sin(t*.4)*.55;a.g.position.z=a.home.z+Math.cos(t*.4)*.3;a.g.rotation.y=-t*.4;}else{a.g.position.x=a.home.x+Math.sin(t*.25)*.6;a.g.rotation.y=Math.cos(t*.25)>0?0:Math.PI;a.g.rotation.z=a.kind==='chicken'?Math.sin(t*2)*.08:Math.sin(t*.4)*.025;a.legs.forEach((l,j)=>l.rotation.z=Math.sin(t*3+j*Math.PI)*.15);}});
 trees.forEach((g,i)=>g.rotation.z=Math.sin(time*.6+i)*.009);smoke.forEach((s,i)=>{s.position.y=5+((time*.25+i*.4)%1.6);s.position.x=-4+Math.sin(time*.3+i)*.15;});
 const progress=Math.min(1,Math.max(0,Number(el.dataset.progress||0)));cropGroups.forEach((g,i)=>{g.scale.y=.65+progress*.35;g.visible=i<2||progress>.25;});roofPieces.forEach((piece,i)=>{piece.visible=progress>(i+1)/15;});
 renderer.render(scene,camera);if(!paused&&visible&&!document.hidden)frame=requestAnimationFrame(render);};
 const restart=()=>{cancelAnimationFrame(frame);last=0;frame=requestAnimationFrame(render)};
 const resize=new ResizeObserver(()=>{const w=el.clientWidth,h=el.clientHeight;renderer.setSize(w,h);const aspect=w/h;const height=Math.max(17,29/aspect);camera.left=-height*aspect/2;camera.right=height*aspect/2;camera.top=height/2;camera.bottom=-height/2;camera.updateProjectionMatrix();restart()});resize.observe(el);
 const mutations=new MutationObserver(restart);mutations.observe(el,{attributes:true,attributeFilter:['data-paused','data-progress','data-loss']});const intersection=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;restart()});intersection.observe(el);document.addEventListener('visibilitychange',restart);
 const lost=(e:Event)=>{e.preventDefault();el.dispatchEvent(new Event('farm-unavailable'))};renderer.domElement.addEventListener('webglcontextlost',lost);restart();
 return()=>{dead=true;cancelAnimationFrame(frame);resize.disconnect();mutations.disconnect();intersection.disconnect();document.removeEventListener('visibilitychange',restart);renderer.domElement.removeEventListener('webglcontextlost',lost);scene.traverse(o=>{if(o instanceof T.Mesh)o.geometry.dispose()});materials.forEach(m=>m.dispose());renderer.dispose();renderer.domElement.remove();};
}
