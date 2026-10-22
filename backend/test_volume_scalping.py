import unittest
from unittest.mock import patch
from backend.high_win_screen import run,volume_confirmation
from backend.test_sequential_scalping import fixture,fixed

class VolumeTests(unittest.TestCase):
    def test_previous_twenty_and_strict_threshold(self):
        prior=[dict(time=t*60,tick_volume=100) for t in range(20)]
        self.assertEqual(volume_confirmation(prior,dict(time=1200,tick_volume=150)),(False,1.5))
        self.assertEqual(volume_confirmation(prior,dict(time=1200,tick_volume=151)),(True,1.51))
        self.assertFalse(volume_confirmation(prior,dict(time=1260,tick_volume=200))[0])
        prior[0]['tick_volume']=True
        self.assertEqual(volume_confirmation(prior,dict(time=1200,tick_volume=200)),(False,None))

    def test_missing_volume_blocks_not_synthetic(self):
        r=run(fixture(3600,7200),'EMA_TREND_RECLAIM',6.4,1.,3600,7200,volume_multiplier=1.5)
        self.assertEqual(r['status'],'BLOCKED')

    def test_filter_changes_entries_without_polluting_raw_cache(self):
        data=fixture(3600,7200)
        for b in data['candles']['M1']:b['tick_volume']=100
        next(b for b in data['candles']['M1'] if b['time']==3780)['tick_volume']=200
        cache={};kw=dict(signal_cache=cache,daily_reset=True,cooldown_seconds=120,max_daily_entries=10,drawdown_limit=100)
        with patch('backend.high_win_screen.signal',side_effect=fixed([3600,3780])):
            filtered=run(data,'EMA_TREND_RECLAIM',6.4,1.,3600,7200,volume_multiplier=1.5,**kw)
        baseline=run(data,'EMA_TREND_RECLAIM',6.4,1.,3600,7200,**kw)
        self.assertEqual(filtered['closed_trades'],1);self.assertEqual(filtered['trades'][0]['signal'],3780)
        self.assertEqual(filtered['skips']['VOLUME_FAILED'],1)
        self.assertEqual(baseline['closed_trades'],2)
        self.assertNotIn('relative_tick_volume',cache[('EMA_TREND_RECLAIM',3780)])

if __name__=='__main__':unittest.main()
