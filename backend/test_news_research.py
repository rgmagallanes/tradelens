import unittest
from unittest.mock import patch
from backend.high_win_screen import news_blocked,run
from backend.run_news_comparison import calendar_windows

def bar(t,o=10015,h=10040,l=10010,c=10020):return dict(time=t,open=o,high=h,low=l,close=c,closed=True)
def data():return {'candles':{'M1':[bar(t) for t in range(0,14400,60)],'M5':[bar(t) for t in range(-18000,14400,300)]}}

class NewsResearchTests(unittest.TestCase):
    def test_half_open_boundaries(self):
        windows=[dict(start=100,end=200)]
        self.assertFalse(news_blocked(99,windows));self.assertTrue(news_blocked(100,windows));self.assertTrue(news_blocked(199,windows));self.assertFalse(news_blocked(200,windows));self.assertFalse(news_blocked(100,None))

    def test_eastern_dst_conversion(self):
        def event(day):return dict(id='test',local_datetime=day+'T08:30:00',timezone='America/New_York',minutes_before=30,minutes_after=30,source='fixture')
        w=calendar_windows({'events':[event('2026-10-14'),event('2026-01-14')]})
        self.assertEqual(w[0]['event_utc'],'2026-10-14T12:30:00+00:00')
        self.assertEqual(w[1]['event_utc'],'2026-01-14T13:30:00+00:00')
        self.assertEqual(w[0]['end']-w[0]['start'],3600)

    def test_signal_blocked_at_detection_and_new_signal_allowed_at_end(self):
        def fixed(family,prior,b,m5):
            if b['time'] in (3660,3780):return dict(long=True,stop=10000,target=10100,signal=b['time'])
            return None
        with patch('backend.high_win_screen.signal',side_effect=fixed):
            r=run(data(),'EMA_TREND_RECLAIM',6.4,.5,3600,14400,news_windows=[dict(start=3720,end=3840)])
        self.assertEqual(r['skips']['NEWS_SIGNAL_BLOCKED'],1)
        self.assertEqual(r['closed_trades'],1)
        self.assertEqual(r['trades'][0]['signal'],3780)
        self.assertEqual(r['trades'][0]['entered'],3840)

    def test_existing_position_keeps_target_inside_blackout(self):
        d=data();next(b for b in d['candles']['M1'] if b['time']==3780)['high']=10110
        def fixed(family,prior,b,m5):return dict(long=True,stop=10000,target=10100,signal=b['time']) if b['time']==3600 else None
        with patch('backend.high_win_screen.signal',side_effect=fixed):
            r=run(d,'EMA_TREND_RECLAIM',6.4,.5,3600,14400,news_windows=[dict(start=3720,end=3900)])
        self.assertEqual(r['closed_trades'],1);t=r['trades'][0]
        self.assertEqual(t['entered'],3660);self.assertEqual(t['exit_bar'],3780);self.assertEqual(t['reason'],'TARGET')

if __name__=='__main__':unittest.main()
