"""Public feed adapter; the local web workspace already requires Node."""
import json, shutil, subprocess, threading, time
from pathlib import Path
_cache = None
_checked = 0
_lock = threading.Lock()
def news():
    global _cache, _checked
    with _lock:
        if _cache is not None and time.time()-_checked < 300:
            return _cache
        try:
            node=shutil.which('node')
            if not node: raise RuntimeError('Node unavailable')
            result=subprocess.run([node,str(Path(__file__).resolve().parents[1]/'server/src/news-cli.mjs')],capture_output=True,text=True,timeout=30,check=True)
            value=json.loads(result.stdout)
            if _cache:
                for source in value['sources']:
                    if not source['ok']:
                        old=next((s for s in _cache['sources'] if s['id']==source['id']),{})
                        source['updated']=old.get('updated')
                        value['items'] += [i for i in _cache['items'] if i['feed']==source['id']]
                if not value['calendarOk']: value['events']=_cache['events']
            _cache=value
        except Exception:
            _cache={**(_cache or {'items':[],'sources':[],'events':[]}), 'unavailable':True,'calendarOk':False}
        _checked=time.time()
        return _cache
