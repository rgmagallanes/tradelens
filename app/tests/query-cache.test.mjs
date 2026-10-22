import test from 'node:test';
import assert from 'node:assert/strict';
import {QueryObserver} from '@tanstack/react-query';
import {createAccountQueryClient,releaseAccountQueryClient} from '../src/queryClient.ts';
const clientForTest=()=>{const client=createAccountQueryClient();client.setDefaultOptions({queries:{...client.getDefaultOptions().queries,gcTime:Infinity}});return client};
test('account caches never share financial data and release cancels late responses',async()=>{
 const alice=clientForTest(),bob=clientForTest();
 alice.setQueryData(['journal','mt5','2026-10','none'],{private:'alice'});
 assert.equal(bob.getQueryData(['journal','mt5','2026-10','none']),undefined);
 let aborted=false,resolve;
 const pending=alice.fetchQuery({queryKey:['mt5-status'],queryFn:({signal})=>new Promise(r=>{resolve=r;signal.addEventListener('abort',()=>{aborted=true})})}).catch(()=>{});
 releaseAccountQueryClient(alice);assert.equal(aborted,true);resolve({private:'late Alice response'});await pending;
 assert.equal(alice.getQueryCache().getAll().length,0);assert.equal(bob.getQueryCache().getAll().length,0);
 releaseAccountQueryClient(bob);
});
test('same journal requests deduplicate; sources/months/demo stay isolated; refresh refetches',async()=>{
 const client=clientForTest();let calls=0;
 const options={queryKey:['journal','mt5','2026-10','none'],queryFn:async()=>({revision:++calls})};
 await Promise.all([client.fetchQuery(options),client.fetchQuery(options)]);assert.equal(calls,1);
 assert.equal(client.getQueryData(['journal','manual','2026-10','none']),undefined);
 assert.equal(client.getQueryData(['journal','mt5','2026-09','none']),undefined);
 assert.equal(client.getQueryData(['journal','mt5','2026-10','mixed']),undefined);
 const observer=new QueryObserver(client,options),unsubscribe=observer.subscribe(()=>{});
 await client.invalidateQueries({queryKey:['journal']});assert.equal(calls,2);assert.equal(client.getQueryData(options.queryKey).revision,2);
 unsubscribe();releaseAccountQueryClient(client);
});
