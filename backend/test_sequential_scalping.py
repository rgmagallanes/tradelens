import unittest
from datetime import datetime,timezone
from unittest.mock import patch
from backend.high_win_screen import run,manila_day

def bar(t):return dict(time=t,open=10015,high=10040,low=9990,close=10020,closed=True)
def fixture(start,end):return {'candles':{'M1':[bar(t) for t in range(start-3600,end,60)],'M5':[bar(t) for t in range((start-21600)//300*300,end,300)]}}
def fixed(times):
    def emit(family,prior,b,m5):return dict(long=True,stop=10000,target=10100,signal=b['time']) if b['time'] in times else None
    return emit

class SequentialScalpingTests(unittest.TestCase):
    def test_daily_pause_resets_without_resetting_equity(self):
        start=int(datetime(2026,8,19,15,50,tzinfo=timezone.utc).timestamp());end=start+1800
        times=[start,start+120,start+240,start+360,start+660]
        with patch('backend.high_win_screen.signal',side_effect=fixed(times)):
            r=run(fixture(start,end),'EMA_TREND_RECLAIM',6.4,1.,start,end,daily_reset=True,max_daily_entries=10,drawdown_limit=100)
        self.assertEqual(r['closed_trades'],4)
        ds=list(r['daily'].values());self.assertEqual(ds[0]['entries'],3);self.assertTrue(ds[0]['loss_paused']);self.assertEqual(ds[1]['entries'],1)
        self.assertAlmostEqual(r['trades'][-1]['risk_budget'],5*(1+sum(t['pnl'] for t in r['trades'][:-1])/1000))
        self.assertEqual(manila_day(start),'2026-08-19');self.assertEqual(manila_day(start+600),'2026-08-20')

    def test_cooldown_requires_two_full_candles_after_exit_candle(self):
        start=3600;end=7200;times=[3600,3660,3720,3780]
        with patch('backend.high_win_screen.signal',side_effect=fixed(times)):
            r=run(fixture(start,end),'EMA_TREND_RECLAIM',6.4,1.,start,end,daily_reset=True,cooldown_seconds=120,max_daily_entries=10,drawdown_limit=100)
        self.assertEqual(r['closed_trades'],2)
        a,b=r['trades'];self.assertEqual(a['entered'],3660);self.assertEqual(b['entered'],3840)
        self.assertGreaterEqual(b['entered'],a['exit_bar']+180)
        self.assertGreater(r['skips']['EXIT_COOLDOWN'],0)

    def test_daily_entry_cap_and_permanent_drawdown_survive_day_change(self):
        start=int(datetime(2026,8,19,15,50,tzinfo=timezone.utc).timestamp());end=start+1800;times=[start,start+120,start+660]
        with patch('backend.high_win_screen.signal',side_effect=fixed(times)):
            capped=run(fixture(start,end),'EMA_TREND_RECLAIM',6.4,1.,start,end,daily_reset=True,max_daily_entries=1,drawdown_limit=100)
        self.assertEqual(capped['closed_trades'],2);self.assertTrue(all(d['entries']<=1 for d in capped['daily'].values()))
        with patch('backend.high_win_screen.signal',side_effect=fixed(times)):
            stopped=run(fixture(start,end),'EMA_TREND_RECLAIM',6.4,1.,start,end,daily_reset=True,max_daily_entries=10,drawdown_limit=1)
        self.assertEqual(stopped['closed_trades'],1);self.assertTrue(stopped['permanent_pause']);self.assertTrue(stopped['risk_paused'])
        self.assertEqual(stopped['pause_events'][-1]['kind'],'ACCOUNT_DRAWDOWN_STOP')

if __name__=='__main__':unittest.main()
