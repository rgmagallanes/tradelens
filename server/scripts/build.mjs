import {cpSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
for(const args of [['--prefix','../app','ci','--include=dev'],['--prefix','../app','run','build']]){const r=spawnSync('npm',args,{stdio:'inherit',env:{...process.env,VITE_HOSTED:'true'}});if(r.status!==0)process.exit(r.status||1)}

rmSync('public',{recursive:true,force:true});
cpSync('../app/dist/client','public',{recursive:true});
