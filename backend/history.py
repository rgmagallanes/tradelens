"""Validate broker-clock OHLC exports; never substitute sample data."""
import json, math, sqlite3, time
from pathlib import Path
INTERVALS={'M1':60,'M5':300,'M15':900,'H1':3600}
def read_history(path, now=None, max_bars=400, expected_symbol='BTCUSDm'):
    now=time.time() if now is None else now
    try:
        raw=Path(path).read_text(); data=json.loads(raw)
        if data.get('version')!=1 or data.get('symbol')!=expected_symbol or data.get('clock')!='broker-server': raise ValueError('Unexpected source')
        stamp=data.get('timestamp')
        if type(stamp) not in (int,float) or not math.isfinite(stamp): raise ValueError('Invalid timestamp')
        series=data.get('candles')
        if not isinstance(series,dict): raise ValueError('Missing candles')
        for tf,interval in {**INTERVALS,**({'H4':14400} if 'H4' in series else {}),**({'D1':86400} if 'D1' in series else {})}.items():
            bars=series.get(tf)
            if not isinstance(bars,list) or len(bars)>max_bars: raise ValueError('Invalid series')
            previous=0
            for index,b in enumerate(bars):
                if not isinstance(b,dict): raise ValueError('Invalid bar')
                if type(b.get('time')) is not int or b['time']<=previous or b['time']%interval: raise ValueError('Invalid bar chronology')
                if any(type(b.get(k)) not in (int,float) or not math.isfinite(b[k]) or b[k]<=0 for k in ('open','high','low','close')): raise ValueError('Invalid prices')
                if b['high']<max(b['open'],b['close']) or b['low']>min(b['open'],b['close']) or b['low']>b['high']: raise ValueError('Invalid OHLC range')
                for volume_key in ('tick_volume','real_volume'):
                    if volume_key in b and (type(b[volume_key]) is not int or b[volume_key]<0): raise ValueError('Invalid volume')
                if b.get('closed') is not (index<len(bars)-1): raise ValueError('Invalid candle state')
                previous=b['time']
        return dict(state='valid',data=data,age_seconds=round(now-stamp,1))
    except FileNotFoundError: return dict(state='missing',message='Waiting for the updated MT5 candle exporter. Reattach BTCStudioQuotes in MT5.')
    except (OSError,ValueError,TypeError,AttributeError): return dict(state='invalid',message='Incomplete or invalid candle export. Waiting for the next valid update.')

def archive(data, db_path):
    with sqlite3.connect(db_path) as c:
        c.execute('BEGIN IMMEDIATE')
        c.execute('CREATE TABLE IF NOT EXISTS broker_candles(symbol TEXT, timeframe TEXT, broker_time INTEGER, open REAL, high REAL, low REAL, close REAL, closed INTEGER, received_at REAL, export_timestamp REAL, PRIMARY KEY(symbol,timeframe,broker_time))')
        columns={r[1] for r in c.execute('PRAGMA table_info(broker_candles)')}
        for name in ('tick_volume','real_volume'):
            if name not in columns:c.execute('ALTER TABLE broker_candles ADD COLUMN '+name+' INTEGER')
        rows=[(data['symbol'],tf,b['time'],b['open'],b['high'],b['low'],b['close'],int(b['closed']),time.time(),data['timestamp'],b.get('tick_volume'),b.get('real_volume')) for tf,bars in data['candles'].items() for b in bars]
        c.executemany('INSERT OR REPLACE INTO broker_candles (symbol,timeframe,broker_time,open,high,low,close,closed,received_at,export_timestamp,tick_volume,real_volume) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',rows)
