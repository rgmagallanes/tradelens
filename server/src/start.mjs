import {fileURLToPath} from 'node:url';
import {database} from './db.mjs';
import {createApp} from './app.mjs';
const pool=database();await pool.query('SELECT 1');
const app=createApp(pool,{origin:process.env.APP_ORIGIN,inviteCode:process.env.REGISTRATION_INVITE,production:process.env.NODE_ENV!=='development',maxUsers:Number(process.env.MAX_USERS||2),staticDir:fileURLToPath(new URL('../public',import.meta.url))});
const server=app.listen(Number(process.env.PORT||3000),'0.0.0.0',()=>console.log('TradeLens hosted journal listening.'));
const stop=()=>server.close(async()=>{await pool.end();process.exit(0)});process.on('SIGTERM',stop);process.on('SIGINT',stop);
