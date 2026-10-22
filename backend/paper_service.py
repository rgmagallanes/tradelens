"""Transactional state/audit storage and read-only bridge adapter."""
import json,sqlite3,time,uuid
RUN_ID=str(uuid.uuid4())
from . import engine
from .history import read_history,archive

def read_margin(path,quote,now=None):
    now=time.time() if now is None else now
    try:
        d=json.loads(path.read_text())
        if d.get('version')!=1 or d.get('symbol')!='BTCUSDm' or d.get('currency')!='USD' or d.get('demo') is not True or d.get('terminal_connected') is not True:return {}
        for k in ('timestamp','bid','ask','margin_buy_per_lot','margin_sell_per_lot'):
            if type(d.get(k)) not in (float,int) or not __import__('math').isfinite(d[k]) or d[k]<=0:return {}
        if d['ask']<d['bid']:return {}
        if not 0<=now-d['timestamp']<15 or abs(d['bid']-quote.get('bid',0))>quote.get('bid',0)*.001:return {}
        return {k:d[k] for k in ('margin_buy_per_lot','margin_sell_per_lot')} | {'margin_export_timestamp':d['timestamp']}
    except (OSError,ValueError,TypeError,AttributeError):return {}

class PaperService:
    def __init__(self,db_path,quote_path,quote_reader):self.db_path=db_path;self.quote_path=quote_path;self.quote_reader=quote_reader
    def connection(self):
        c=sqlite3.connect(self.db_path,timeout=10);c.row_factory=sqlite3.Row
        c.execute('CREATE TABLE IF NOT EXISTS paper_engine(id INTEGER PRIMARY KEY CHECK(id=1),payload TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS paper_audit(id INTEGER PRIMARY KEY,received_utc REAL,kind TEXT,payload TEXT)')
        c.commit();return c
    def mutate(self,fn):
        with self.connection() as c:
            c.execute('BEGIN IMMEDIATE')
            r=c.execute('SELECT payload FROM paper_engine WHERE id=1').fetchone();s=json.loads(r['payload']) if r else engine.initial()
            result=fn(s)
            for e in s['events']:c.execute('INSERT INTO paper_audit(received_utc,kind,payload) VALUES(?,?,?)',(e['received_utc'],e['kind'],json.dumps(e)))
            s['events']=[]
            c.execute('INSERT OR REPLACE INTO paper_engine VALUES(1,?)',(json.dumps(s),))
            return result if result is not None else s
    def source(self):
        q=self.quote_reader();h=read_history(self.quote_path.with_name('btc-studio-candles.json'))
        data=h.get('data',{});bars=data.get('candles',{});snapshot=dict(q.get('snapshot',{}))
        margin=read_margin(self.quote_path.with_name('btc-studio-margin.json'),snapshot)
        if margin:snapshot.update(margin)
        ready=q.get('connected',False) and h['state']=='valid' and 0<=h['age_seconds']<15 and data.get('demo') is True and data.get('terminal_connected') is True
        for tf in ('M5','M15','H1'):
            series=bars.get(tf,[]);interval={'M5':300,'M15':900,'H1':3600}[tf]
            ready=ready and len(series)>=3 and 0<=snapshot.get('tick_time_msc',0)/1000-series[-1]['time']<interval*2
        return bars,snapshot,bool(ready)
    def restart(self):
        def update(s):
            for l in s['levels']:
                if l['state'] in engine.ACTIVE:engine.finish(s,l,'DATA_GAP',time.time(),reason='Service restart: pending attempt cancelled')
            s.update(recovering=True,recovery=0,last_bar=None,last_poll=None)
            if s['position']:
                s['position']['uncertainty']=True
                s['position'].update(clock_run_id=RUN_ID,deadline_monotonic=time.monotonic()+max(0,min(engine.P['max_hold_seconds'],s['position']['deadline']-time.time())))
                engine.event(s,'RESTART_RECOVERY',time.time(),trade_id=s['position']['id'],timer_recovery='UTC remaining duration, clamped; execution uncertainty recorded')
        self.mutate(update)
    def poll(self):
        bars,q,ready=self.source();now=time.time()
        self.mutate(lambda s:engine.step(s,bars,q,now,ready,time.monotonic(),RUN_ID))
    def status(self):
        bars,q,ready=self.source()
        s=self.mutate(lambda s:None)
        s['prerequisites']=engine.prerequisites(s['config'],q)
        if not ready:s['prerequisites'].append('Fresh synchronized demo feed required')
        if s['enabled'] and (s.get('last_poll') is None or time.time()-s['last_poll']>15):s['prerequisites'].append('Paper worker heartbeat stale');s['reason']='Paper worker heartbeat stale'
        s['feed_ready']=ready;s['version']=engine.VERSION;s['manifest']=engine.MANIFEST
        s['equity']=engine.P['initial_equity']+sum(p['pnl'] for p in s['closed'])
        s['closed_samples']={tf:next((b for b in reversed(bars.get(tf,[])) if b['closed']),None) for tf in ('M5','M15','H1')}
        s['broker_specs']={k:q.get(k) for k in ('chart_basis','currency','tick_size','contract_size','volume_min','volume_step','volume_max','margin_buy_per_lot','margin_sell_per_lot')}
        with self.connection() as c:s['audit']=[json.loads(r['payload']) for r in c.execute('SELECT payload FROM paper_audit ORDER BY id DESC LIMIT 50')]
        return s
    def configure(self,config):
        def update(s):
            if s['enabled'] or s['position']:raise ValueError('Pause engine and close its paper position before changing research settings.')
            s['config']=config;engine.event(s,'CONFIGURED',time.time(),config=config)
        self.mutate(update)
    def control(self,action):
        bars,q,ready=self.source();now=time.time()
        def update(s):
            if action=='start':
                missing=engine.prerequisites(s['config'],q)
                if not ready:missing.append('Fresh synchronized feed required')
                if missing:raise ValueError('; '.join(missing))
                if s.get('needs_resume'):raise ValueError('Use Resume on a later Manila date to clear the risk pause.')
                s.update(enabled=True,last_bar=next((b['time'] for b in reversed(bars['M5']) if b['closed']),None),reason='Watching newly registered levels')
            elif action=='pause':
                s['enabled']=False
                for l in s['levels']:
                    if l['state'] in engine.ACTIVE:engine.finish(s,l,'USER_CANCELLED',now,reason='Engine paused')
            elif action=='news':s['news_pause']=not s['news_pause']
            elif action=='resume':
                if not s['needs_resume'] or engine.day(now)<=s['pause_date']:raise ValueError('Risk pause can only resume on a later Manila date.')
                s.update(needs_resume=False,resume_after=now)
            else:raise ValueError('Unknown action')
            engine.event(s,'CONTROL',now,action=action)
        self.mutate(update)
    def register(self,price,side,touches,context):
        bars,q,ready=self.source()
        if not ready:raise ValueError('Fresh demo candles required to register evidence.')
        def update(s):
            level=engine.register(s,price,side,touches,bars['M15'],time.time(),context)
            level['registered_broker_tick']=q['tick_time_msc']
            level['registration_last_closed']=next((b['time'] for b in reversed(bars['M5']) if b['closed']),0)
            return level
        return self.mutate(update)
    def cancel(self,ident):
        def update(s):
            l=next((l for l in s['levels'] if l['id']==ident),None)
            if not l or l['state'] not in engine.ACTIVE:raise ValueError('Active level not found')
            engine.finish(s,l,'USER_CANCELLED',time.time())
        self.mutate(update)
