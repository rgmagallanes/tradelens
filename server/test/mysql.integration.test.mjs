import {fixture} from './fixtures/market.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import {database,migrate} from '../src/db.mjs';
import {createApp} from '../src/app.mjs';
const enabled=process.env.TEST_MYSQL==='1';
test('real MySQL tenant isolation, auth, replay protection and device revocation',{skip:!enabled},async()=>{
 if(process.env.DB_NAME!=='tradelens_qa')throw Error('Integration tests require the isolated tradelens_qa database.');
 const pool=database();await migrate(pool);
 // Only the uniquely named disposable test database may be cleared.
 for(const table of ['tl_snapshots','tl_trades','tl_notes','tl_settings','tl_devices','tl_sessions','tl_users','tl_limits'])await pool.query('DELETE FROM '+table);
 const origin='http://127.0.0.1',inviteCode='local-invitation-code-for-isolated-test-only';const app=createApp(pool,{origin,inviteCode,production:false});const server=app.listen(0,'127.0.0.1');await new Promise(resolve=>server.once('listening',resolve));const base='http://127.0.0.1:'+server.address().port;
 async function call(path,{method='GET',body,cookie,bearer,requestOrigin=origin}={}){const r=await fetch(base+'/api/'+path,{method,headers:{...(method!=='GET'?{'Content-Type':'application/json'}:{}),Origin:requestOrigin,...(cookie?{Cookie:cookie}:{}),...(bearer?{Authorization:'Bearer '+bearer}:{})},...(body?{body:JSON.stringify(body)}:{})});return {status:r.status,body:await r.json(),cookie:r.headers.get('set-cookie')?.split(';')[0]}}
 try{
 assert.equal((await call('health')).status,200);assert.equal((await call('trading-journal')).status,401);
 const alice=await call('auth/register',{method:'POST',body:{email:'alice@example.test',password:'alice-test-password-123',invite:inviteCode}});assert.equal(alice.status,200);assert.match(alice.cookie,/^tl_session=/);
 const bob=await call('auth/register',{method:'POST',body:{email:'bob@example.test',password:'bob-test-password-12345',invite:inviteCode}});assert.equal(bob.status,200);
 assert.equal((await call('auth/register',{method:'POST',body:{email:'third@example.test',password:'third-test-password-123',invite:inviteCode}})).status,403);
 assert.equal((await call('auth/login',{method:'POST',body:{email:'alice@example.test',password:'incorrect-password'}})).status,401);
 assert.equal((await call('trading-journal/notes',{method:'POST',cookie:alice.cookie,requestOrigin:'https://attacker.example',body:{source:'manual',day:'2026-09-01',note:'blocked'}})).status,403);
 const manual={symbol:'BTCUSDm',side:'buy',lots:.01,entry:100,exit:102,opened_at:'2026-09-01T00:00:00Z',closed_at:'2026-09-01T00:10:00Z',pnl:1.25,strategy:'test',note:'private to Alice'};
 const created=await call('trading-journal/trades',{method:'POST',cookie:alice.cookie,body:manual});assert.equal(created.status,200);
 assert.equal((await call('trading-journal?source=manual&month=2026-09',{cookie:alice.cookie})).body.summary.pnl,1.25);
 assert.equal((await call('trading-journal?source=manual&month=2026-09',{cookie:bob.cookie})).body.summary.closed_count,0);
 assert.equal((await call('trading-journal/trades/'+created.body.id,{method:'DELETE',cookie:bob.cookie})).status,404);
 assert.equal((await call('trading-journal/trades/'+created.body.id,{method:'PUT',cookie:bob.cookie,body:manual})).status,404);
 await call('trading-journal/balance',{method:'POST',cookie:alice.cookie,body:{initial_balance:100}});
 await call('trading-journal/notes',{method:'POST',cookie:alice.cookie,body:{source:'manual',day:'2026-09-01',note:'Alice only'}});
 const bobsJournal=(await call('trading-journal?source=manual&month=2026-09',{cookie:bob.cookie})).body;assert.equal(bobsJournal.initial_balance,0);assert.equal(bobsJournal.days[0].note,'');
 const device=await call('devices',{method:'POST',cookie:alice.cookie,body:{label:'Test Mac'}});assert.equal(device.status,201);
 assert.equal((await call('devices',{cookie:bob.cookie})).body.devices.length,0);assert.equal((await call('devices/'+device.body.id,{method:'DELETE',cookie:bob.cookie,body:{}})).status,404);
 const now=Math.floor(Date.now()/1000),trade={id:'mt5-one',symbol:'BTCUSDm',side:'buy',lots:.1,entry:100,exit:99,opened_at:now-500,closed_at:now-300,status:'closed',pnl:-.5,strategy:'',note:''};
 const up={version:1,account_hash:'a'.repeat(64),timestamp:now-10,currency:'USD',demo:true,account_balance:500,trades:[trade],open_positions:[],markets:[fixture('BTCUSDm'),fixture('XAUUSDm')]};
 assert.equal((await call('device/upload',{method:'POST',bearer:device.body.token,body:up})).status,200);
 for(const symbol of ['BTCUSDm','XAUUSDm'])for(const tf of ['M5','M15','H1','H4']){
 const own=await call('market?source=exness&symbol='+symbol+'&tf='+tf,{cookie:alice.cookie});assert.equal(own.status,200);assert.equal(own.body.candles.length,2);assert.equal(own.body.candles[0].tick_volume,20);
 const other=await call('market?source=exness&symbol='+symbol+'&tf='+tf,{cookie:bob.cookie});assert.equal(other.body.candles.length,0);
 }
 assert.equal((await call('bridge?symbol=XAUUSDm',{cookie:alice.cookie})).body.connected,true);
 assert.equal((await call('bridge?symbol=XAUUSDm',{cookie:bob.cookie})).body.snapshot,undefined);
 assert.equal((await call('device/upload',{method:'POST',bearer:device.body.token,body:up})).status,409);
 const review={source:'mt5',trade_id:'mt5-one',mistakes:['Entered early'],lessons:['Wait for close']};
 assert.equal((await call('trading-journal/tags',{method:'POST',cookie:alice.cookie,body:review})).status,200);
 assert.equal((await call('trading-journal/tags',{method:'POST',cookie:bob.cookie,body:review})).status,404);
 assert.deepEqual((await call('trading-journal/tags?source=mt5',{cookie:bob.cookie})).body.tags,{});
 assert.deepEqual((await call('trading-journal/tags?source=manual',{cookie:alice.cookie})).body.tags,{});
 assert.deepEqual((await call('trading-journal/tags?source=mt5',{cookie:alice.cookie})).body.tags['mt5-one'].mistakes,['entered early']);

 assert.equal((await call('device/upload',{method:'POST',bearer:device.body.token,body:{...up,timestamp:now-9,account_hash:'b'.repeat(64)}})).status,409);
 assert.equal((await call('trading-journal/mt5-status',{cookie:bob.cookie})).body.timestamp,undefined);
 const status=(await call('trading-journal/mt5-status',{cookie:alice.cookie})).body;assert.equal(status.account_balance,500);assert.equal(status.account_hash,undefined);
 assert.equal((await call('device/upload',{method:'POST',bearer:device.body.token,body:{...up,timestamp:now-8,trades:[]}})).status,200);
 assert.deepEqual((await call('trading-journal/tags?source=mt5',{cookie:alice.cookie})).body.tags['mt5-one'].lessons,['wait for close']);
 const date=new Date((now+28800)*1000).toISOString().slice(0,7);assert.equal((await call('trading-journal?source=mt5&month='+date,{cookie:alice.cookie})).body.summary.closed_count,1);
 assert.equal((await call('devices/'+device.body.id,{method:'DELETE',cookie:alice.cookie,body:{}})).status,200);
 assert.equal((await call('device/upload',{method:'POST',bearer:device.body.token,body:{...up,timestamp:now-7}})).status,401);
 assert.equal((await call('trading-journal/ideas?source=mt5',{cookie:alice.cookie})).status,501);
 const bobLogin=await call('auth/login',{method:'POST',body:{email:'bob@example.test',password:'bob-test-password-12345'}});assert.equal(bobLogin.status,200);assert.equal((await call('auth/session',{cookie:bobLogin.cookie})).body.user.email,'bob@example.test');
 for(let i=0;i<9;i++)await call('auth/login',{method:'POST',body:{email:'alice@example.test',password:'incorrect-password'}});assert.equal((await call('auth/login',{method:'POST',body:{email:'alice@example.test',password:'incorrect-password'}})).status,429);
 assert.equal((await call('auth/logout',{method:'POST',cookie:alice.cookie,body:{}})).status,200);assert.equal((await call('auth/session',{cookie:alice.cookie})).status,401);
 const [sessions]=await pool.query('SELECT token_hash FROM tl_sessions');assert.ok(sessions.every(s=>!s.token_hash.includes('tl_session')));
 }finally{await new Promise(resolve=>server.close(resolve));await pool.end()}
});
