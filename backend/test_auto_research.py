import unittest
from backend.auto_research import pivots,trend,fill_plan,exit_fill,run

def bar(t,o=100,h=101,l=99,c=100):return dict(time=t,open=o,high=h,low=l,close=c,closed=True)

class AutoResearchTests(unittest.TestCase):
    def test_pivot_waits_for_right_bars_and_reaction(self):
        bars=[bar(i*300,h=103 if i==2 else 101) for i in range(5)]
        self.assertFalse(any(p['time']==600 for p in pivots(bars[:4])))
        self.assertTrue(any(p['time']==600 and p['side']=='resistance' for p in pivots(bars)))
        equal=[dict(b,high=103) for b in bars]
        self.assertFalse(any(p['side']=='resistance' for p in pivots(equal)))

    def test_context_rejects_gap_and_needs_warmup(self):
        bars=[bar(i*900,c=100+i) for i in range(40)]
        self.assertTrue(trend(bars,900,True));self.assertFalse(trend(bars[:39],900,True))
        self.assertFalse(trend(bars[:20]+bars[21:],900,True))

    def test_bid_ask_costs_and_two_r_gate(self):
        level=dict(side='resistance',price=10000,extreme=9980,target=10200,id=1)
        p,reason=fill_plan(level,bar(0,o=10020),6.4,1000)
        self.assertIsNone(reason);self.assertAlmostEqual(p['entry'],10031.4)
        self.assertLessEqual(((p['entry']-p['stop'])+5)*p['lots'],5)
        _,reason=fill_plan(dict(level,target=10040),bar(0,o=10020),6.4,1000)
        self.assertEqual(reason,'COST_FAILED')

    def test_ambiguous_stop_first_and_gap_stop(self):
        p=dict(long=True,stop=90,target=120)
        fill,reason,amb=exit_fill(p,bar(0,o=85,h=125,l=80),6.4)
        self.assertEqual((fill,reason,amb),(80,'STOP',True))
        short=dict(long=False,stop=110,target=80)
        fill,reason,amb=exit_fill(short,bar(0,o=100,h=105,l=90),6.4)
        self.assertEqual(reason,'STOP');self.assertEqual(fill,115)

    def test_partial_week_is_blocked(self):
        data={'candles':{'M1':[bar(i*60) for i in range(100)],'M5':[],'M15':[],'H1':[]}}
        self.assertEqual(run(data)['status'],'BLOCKED')

if __name__=='__main__':unittest.main()
