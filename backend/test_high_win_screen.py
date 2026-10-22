import unittest
from unittest.mock import patch
from backend.high_win_screen import signal,plan,metrics,wilson,run,reverse_signal

def bar(t,o=100,h=101,l=99,c=100):return dict(time=t,open=o,high=h,low=l,close=c,closed=True)

class HighWinScreenTests(unittest.TestCase):
    def test_bb_reentry_uses_prior_bands_and_rejects_gap(self):
        prior=[bar(i*60) for i in range(21)];prior[-1]=bar(1200,o=100,h=100,l=90,c=90)
        context=[bar(-12000+i*300) for i in range(40)]
        b=bar(1260,o=91,h=98,l=89,c=97)
        s=signal('BB_REENTRY',prior,b,context)
        self.assertTrue(s['long']);self.assertAlmostEqual(s['target'],99.5)
        prior[-1]['time']=1140
        self.assertIsNone(signal('BB_REENTRY',prior,b,context))

    def test_80_percent_can_still_lose(self):
        trades=[dict(pnl=1,modeled_cost=0) for _ in range(8)]+[dict(pnl=-5,modeled_cost=0) for _ in range(2)]
        m=metrics(trades)
        self.assertEqual(m['win_rate'],.8);self.assertEqual(m['net_pnl'],-2)
        self.assertLess(m['profit_factor'],1)
        self.assertIsNone(wilson(0,0));lo,hi=wilson(80,100)
        self.assertLess(lo,.8);self.assertGreater(hi,.8)

    def test_net_rr_and_adverse_fills(self):
        s=dict(long=True,stop=9990,target=10100,signal=0)
        p,reason=plan(s,bar(60,o=10000),6.4,1,1000)
        self.assertIsNone(reason);self.assertAlmostEqual(p['entry'],10011.4)
        self.assertLessEqual((p['entry']-p['stop']+5)*p['lots'],5)
        _,reason=plan(dict(s,target=10010),bar(60,o=10000),6.4,.5,1000)
        self.assertEqual(reason,'COST_FAILED')

    def test_risk_sizing_changes_volume_not_edge_or_fill_prices(self):
        s=dict(long=True,stop=9990,target=10100,signal=0)
        ps=[plan(s,bar(60,o=10000),6.4,.5,1000,risk_fraction=r,max_risk=1000*r)[0] for r in [.005,.01,.02]]
        self.assertEqual(len({(p['entry'],p['stop'],p['target'],p['net_rr']) for p in ps}),1)
        self.assertTrue(ps[0]['lots']<ps[1]['lots']<ps[2]['lots'])
        for p,r in zip(ps,[.005,.01,.02]):self.assertLessEqual(p['planned_risk'],1000*r)
        with self.assertRaises(ValueError):plan(s,bar(60),6.4,.5,1000,risk_fraction=float('nan'))

    def test_target_caps_include_costs_and_preserve_stop_and_size(self):
        for long in [True,False]:
            s=dict(long=long,stop=9990 if long else 10040,target=10200 if long else 9800,signal=0)
            original,_=plan(s,bar(60,o=10000),6.4,.5,1000)
            for cap in [.5,.75,1.]:
                p,reason=plan(s,bar(60,o=10000),6.4,.5,1000,target_net_r=cap)
                self.assertIsNone(reason)
                self.assertEqual((p['entry'],p['stop'],p['lots']),(original['entry'],original['stop'],original['lots']))
                self.assertGreaterEqual(p['net_rr'],cap-1e-8)
                self.assertLessEqual(p['net_rr'],cap+.01/(p['planned_risk']/p['lots'])+1e-8)
                self.assertLessEqual(abs(p['target']-p['entry']),abs(original['target']-original['entry']))
        p,_=plan(dict(long=True,stop=9990,target=10040,signal=0),bar(60,o=10000),6.4,.5,1000,target_net_r=1.)
        self.assertEqual(p['target'],10040)
        with self.assertRaises(ValueError):plan(s,bar(60,o=10000),6.4,.5,1000,target_net_r=.1)

    def test_reversal_preserves_bid_boundaries_and_costs(self):
        original=dict(long=True,stop=9990,target=10100,signal=0)
        rev=reverse_signal(original,6.4)
        self.assertFalse(rev['long'])
        self.assertAlmostEqual(rev['stop']-6.4,original['target'])
        self.assertAlmostEqual(rev['target']-6.4,original['stop'])
        restored=reverse_signal(rev,6.4)
        self.assertTrue(restored['long']);self.assertAlmostEqual(restored['stop'],9990);self.assertAlmostEqual(restored['target'],10100)
        # Equal hypothetical bid endpoints and volume: costs are paid in both directions.
        bid0,bid1,lots=10000,10020,.1
        forward=((bid1-5)-(bid0+6.4+5))*lots
        reverse=((bid0-5)-(bid1+6.4+5))*lots
        self.assertAlmostEqual(reverse,-forward-2*(6.4+10)*lots)
        self.assertEqual(original['stop'],9990)

    def test_next_open_risk_pause_and_context_not_future(self):
        entries=[bar(t,o=10015,h=10040,l=9990,c=10020) for t in range(0,14400,60)]
        data={'candles':{'M1':entries,'M5':[bar(t) for t in range(-18000,14400,300)]}}
        seen=[]
        def fixed(family,prior,b,m5):
            self.assertTrue(all(x['time']+300<=b['time'] for x in m5))
            if b['time'] in (3660,3780,3900,4020):
                seen.append(b['time']);return dict(long=True,stop=10000,target=10100,signal=b['time'])
            return None
        with patch('backend.high_win_screen.signal',side_effect=fixed):r=run(data,'BB_REENTRY',6.4,.5,3600,14400)
        self.assertEqual(r['closed_trades'],3);self.assertTrue(r['risk_paused'])
        self.assertEqual(r['skips']['SIGNAL_DURING_RISK_PAUSE'],1)
        self.assertFalse(r['research_flag'])
        for t in r['trades']:self.assertEqual(t['entered'],t['signal']+60)

if __name__=='__main__':unittest.main()
