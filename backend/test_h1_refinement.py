import unittest
from unittest.mock import patch
from backend.h1_channel_research import trend_allowed,range_allowed,run
from backend.run_h1_refinement import diagnostics

def bar(t,c=10000):return dict(time=t,open=c,high=c+10,low=c-10,close=c,closed=True)

class H1RefinementTests(unittest.TestCase):
    def test_ema_direction_warmup_flat_and_gap(self):
        rising=[bar(i*3600,100+i) for i in range(60)]
        falling=[bar(i*3600,200-i) for i in range(60)]
        self.assertTrue(trend_allowed(rising,True));self.assertFalse(trend_allowed(rising,False))
        self.assertTrue(trend_allowed(falling,False));self.assertFalse(trend_allowed(rising[:54],True))
        self.assertFalse(trend_allowed([bar(i*3600,100) for i in range(60)],True))
        self.assertFalse(trend_allowed(rising[:30]+rising[31:],True))

    def test_range_uses_prior_atr_and_includes_equality(self):
        b=bar(0);self.assertTrue(range_allowed(b,10));self.assertFalse(range_allowed(b,9.99));self.assertFalse(range_allowed(b,None))

    def test_trend_rechecked_before_entry_without_entry_candle(self):
        bs=[bar(i*3600) for i in range(110)];start=60*3600;seen=[]
        def filter(completed,long):seen.append(completed[-1]['time']);return True
        with patch('backend.h1_channel_research.breakout',side_effect=lambda prior,b:True if b['time']==start else None),patch('backend.h1_channel_research.trend_allowed',side_effect=filter),patch('backend.h1_channel_research.channel_exit',return_value=False):
            result=run({'candles':{'H1':bs}},start,100*3600,profile='ema50')
        self.assertEqual(seen,[start,start]);self.assertEqual(result['open_position']['entered'],start+3600)
        self.assertEqual(result['active_bars']+result['risk_paused_bars'],40)

    def test_concentration_and_holding_proxy_are_accounting_only(self):
        r={'trades':[dict(pnl_excluding_swaps=100,lots=.01,hold_hours=48,reason='CHANNEL_EXIT'),dict(pnl_excluding_swaps=-5,lots=.01,hold_hours=2,reason='STOP')]}
        d=diagnostics(r)
        self.assertEqual(d['pnl_without_largest_winner_accounting_only'],-5)
        self.assertFalse(d['funding_verified'])
        self.assertAlmostEqual(d['holding_proxy_lot_days'],.01*51/24)
        self.assertAlmostEqual(d['holding_cost_sensitivity_accounting_only'][2]['pnl_after_proxy'],95-.01*51/24*30)

if __name__=='__main__':unittest.main()
