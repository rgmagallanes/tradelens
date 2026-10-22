import unittest
from unittest.mock import patch
from backend.run_two_month_news import START,END,run_windows
from backend.high_win_screen import run,signal

def bar(t):return dict(time=t,open=100,high=101,low=99,close=100,closed=True)

class TwoMonthResearchTests(unittest.TestCase):
    def test_calendar_month_window_and_nonoverlapping_reset_weeks(self):
        windows=run_windows();self.assertEqual((END-START)//86400,61)
        self.assertEqual(windows[0],('continuous_two_months',START,END))
        weeks=windows[1:];self.assertEqual(len(weeks),9)
        self.assertEqual(weeks[0][1],START);self.assertEqual(weeks[-1][2],END)
        self.assertEqual(weeks[-1][2]-weeks[-1][1],5*86400)
        self.assertTrue(all(a[2]==b[1] for a,b in zip(weeks,weeks[1:])))
        self.assertEqual(sum(b-a for _,a,b in weeks),END-START)

    def test_source_scoped_signal_cache_does_not_change_replay(self):
        data={'candles':{'M1':[bar(t) for t in range(0,14400,60)],'M5':[bar(t) for t in range(-18000,14400,300)]}}
        cache={}
        with patch('backend.high_win_screen.signal',wraps=signal) as mocked:
            a=run(data,'EMA_TREND_RECLAIM',6.4,.5,3600,14400,signal_cache=cache)
            calls=mocked.call_count
            b=run(data,'EMA_TREND_RECLAIM',6.4,.5,3600,14400,signal_cache=cache)
            self.assertEqual(mocked.call_count,calls)
        c=run(data,'EMA_TREND_RECLAIM',6.4,.5,3600,14400)
        self.assertEqual(a,b);self.assertEqual(a,c)

if __name__=='__main__':unittest.main()
