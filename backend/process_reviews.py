"""User-authored reflections, separate from broker execution records."""
import json, sqlite3, time
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
class ProcessReview(BaseModel):
    model_config=ConfigDict(extra='forbid')
    source: Literal['manual','engine','sample','mt5']
    key: str=Field(min_length=1,max_length=150,pattern=r'^(trade:|week:)')
    plan: str=Field(default='',max_length=2000)
    actual: str=Field(default='',max_length=2000)
    focus: str=Field(default='',max_length=1000)
    adherence: Literal['unreviewed','followed','partly','not-followed','no-plan']='unreviewed'
def records(path,source,record=None):
    with sqlite3.connect(path) as c:
        c.execute('CREATE TABLE IF NOT EXISTS process_reviews(source TEXT,key TEXT,payload TEXT NOT NULL,PRIMARY KEY(source,key))')
        if record is not None:
            payload=record.model_dump();payload['updated_at']=int(time.time())
            c.execute('INSERT INTO process_reviews VALUES(?,?,?) ON CONFLICT(source,key) DO UPDATE SET payload=excluded.payload',(source,record.key,json.dumps(payload)))
            return {'saved':True}
        return {'reviews':{key:json.loads(payload) for key,payload in c.execute('SELECT key,payload FROM process_reviews WHERE source=?',(source,))}}
