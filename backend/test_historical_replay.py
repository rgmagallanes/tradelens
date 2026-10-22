import unittest
from unittest.mock import patch
from backend.historical_replay import run

def bar(t,close=100):
    return dict(time=t,open=100,high=max(101,close),low=min(99,close),close=close,closed=True)

class ReplayChronology(unittest.TestCase):
    def test_future_m15_and_h1_not_visible(self):
        data={'candles':{'M5':[bar(3600),bar(3900,103)],'M15':[bar(0),bar(3600),bar(4500)],'H1':[bar(0),bar(3600)]}}
        seen=[]
        def eligible(bars,price,side):
            seen.append([b['time'] for b in bars])
            return [dict(time=0,index=0),dict(time=900,index=3)]
        with patch('backend.historical_replay.evidence',side_effect=eligible),patch('backend.historical_replay.context',return_value=False) as ctx:
            result=run(data,[(100,'resistance')])
        self.assertEqual(seen,[[0]])
        self.assertEqual([x['time'] for x in ctx.call_args.args[0]],[0])
        self.assertEqual(result['levels'][0]['outcome'],'CONTEXT_FAILED')

    def test_no_breakout_on_registration_bar_or_outside_window(self):
        data={'candles':{'M5':[bar(3300),bar(3600,103),bar(3900,104),bar(4200,99)],'M15':[],'H1':[]}}
        with patch('backend.historical_replay.evidence',return_value=[dict(time=0,index=0),dict(time=900,index=3)]):
            result=run(data,[(100,'resistance')],start=3600,end=4200)
        self.assertEqual(result['period']['closed_m5_bars'],2)
        self.assertEqual(result['levels'][0]['outcome'],'ARMED')
        self.assertNotIn('breakout',result['levels'][0])

if __name__=='__main__': unittest.main()
