import unittest
from unittest.mock import patch
from backend.pullback_research import swings,contiguous_tail,setup,confirmation,run

def bar(t,o=100,h=101,l=99,c=100):return dict(time=t,open=o,high=h,low=l,close=c,closed=True)

class PullbackTests(unittest.TestCase):
    def test_pivot_is_unknown_until_two_right_bars_complete(self):
        bs=[bar(i*300,h=105 if i==2 else 101) for i in range(5)]
        self.assertEqual(swings(bs[:4]),[])
        self.assertEqual(swings(bs)[0]['known'],1500)
        self.assertEqual(swings(bs)[0]['time'],600)

    def test_gap_resets_pivot_window(self):
        bs=[bar(i*300,h=105 if i==2 else 101) for i in range(6)]
        bs[-1]['time']=2100
        self.assertEqual(contiguous_tail(bs,300),[bs[-1]])
        self.assertEqual(swings(bs),[])

    def test_next_candle_confirmation_and_invalid_first(self):
        s=dict(side='resistance',price=10000,threshold=10050,extreme=9998,count=0)
        self.assertEqual(confirmation(s,bar(0,o=10040,h=10070,l=10000,c=10060)),'CONFIRMED')
        s=dict(side='resistance',price=10000,threshold=10050,extreme=9998,count=0)
        self.assertEqual(confirmation(s,bar(0,o=10040,h=10070,l=9990,c=10060)),'INVALIDATED')
        s=dict(side='support',price=10000,threshold=9950,extreme=10002,count=6)
        self.assertEqual(confirmation(s,bar(0,o=9950,h=10000,l=9930,c=9940)),'EXPIRED')

    def test_target_and_swing_known_before_touch_and_no_reuse(self):
        points=[dict(kind='high',price=110,time=0,known=900),dict(kind='low',price=90,time=300,known=1200),dict(kind='high',price=120,time=600,known=1500),dict(kind='low',price=100,time=900,known=1800),dict(kind='high',price=130,time=1500,known=2400)]
        m5=[bar(i*300) for i in range(8)];m5[-1]=bar(2100,o=100.01,h=100.04,l=99.99,c=100.02)
        m1=[bar(t,h=100.03) for t in (2220,2280,2340)];used=set()
        with patch('backend.pullback_research.swings',return_value=points),patch('backend.pullback_research.trend',return_value=True):
            s,reason=setup(m5,m1,[],True,used)
            self.assertIsNone(reason);self.assertEqual(s['target'],110);self.assertEqual(s['created'],2400)
            self.assertEqual(s['swing']['known'],1800)
            self.assertEqual(setup(m5,m1,[],True,used),(None,None))

    def test_entry_after_confirmation_and_time_exit(self):
        data={'candles':{'M1':[bar(t,o=10020,h=10022,l=10019,c=10021) for t in range(0,120000,60)],'M5':[bar(t) for t in range(-30000,120000,300)],'M15':[bar(t) for t in range(-60000,120000,900)]}}
        emitted=[]
        def activate(m5,m1,h,long,used):
            if emitted or not long:return None,None
            emitted.append(True)
            return dict(id='fixture',side='resistance',price=10000,created=m5[-1]['time']+300,touch=m5[-1]['time'],swing={},target=11000,target_evidence={},threshold=10020.5,extreme=9995,count=0,state='WAITING'),None
        with patch('backend.pullback_research.setup',side_effect=activate),patch('backend.pullback_research.trend',return_value=True):
            r=run(data,days=1)
        self.assertEqual(r['closed_trades'],1)
        t=r['trades'][0]
        self.assertEqual(t['entered'],t['confirmation']+60)
        self.assertGreater(t['entered'],t['pullback']+300)
        self.assertEqual(t['reason'],'TIME')
        self.assertEqual(t['exit_bar']-t['entered'],1800)
        self.assertAlmostEqual(t['pnl'],-16.4*t['lots'])

    def test_partial_window_blocked(self):
        data={'candles':{'M1':[bar(0)],'M5':[],'M15':[]}}
        self.assertEqual(run(data)['status'],'BLOCKED')

if __name__=='__main__':unittest.main()
