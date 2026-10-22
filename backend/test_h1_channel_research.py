import unittest
from unittest.mock import patch
from backend.h1_channel_research import atr_series,breakout,channel_exit,enter,stop_fill,run

def bar(t,o=10000,h=10010,l=9990,c=10000):return dict(time=t,open=o,high=h,low=l,close=c,closed=True)

class H1ChannelTests(unittest.TestCase):
    def test_wilder_atr_seed_and_gap_reset(self):
        bs=[bar(i*3600,o=100,h=101,l=99,c=100) for i in range(16)]
        bs[-1]=bar(15*3600,o=100,h=104,l=99,c=100)
        a=atr_series(bs)
        self.assertIsNone(a[13*3600]);self.assertEqual(a[14*3600],2)
        self.assertAlmostEqual(a[15*3600],(13*2+5)/14)
        bs.append(bar(17*3600));self.assertIsNone(atr_series(bs)[17*3600])

    def test_channels_exclude_signal_bar_and_equality(self):
        prior=[bar(i*3600,o=100,h=101,l=99,c=100) for i in range(20)]
        self.assertTrue(breakout(prior,bar(20*3600,o=100,h=110,l=99,c=102)))
        self.assertIsNone(breakout(prior,bar(20*3600,o=100,h=110,l=99,c=101)))
        self.assertTrue(channel_exit(prior,bar(20*3600,o=100,h=101,l=90,c=98),True))
        self.assertFalse(channel_exit(prior,bar(20*3600,o=100,h=101,l=90,c=99),True))

    def test_minimum_lots_and_gap_stop(self):
        s=dict(long=True,atr=1000,signal=0)
        self.assertEqual(enter(s,bar(3600),6.4,1000)[1],'SIZE_FAILED')
        p,reason=enter(s,bar(3600),6.4,10000)
        self.assertIsNone(reason);self.assertLessEqual(p['planned_loss'],50)
        self.assertEqual(p['lots'],.02)
        self.assertEqual(stop_fill(dict(long=True,stop=9900),bar(0,o=9800,h=9850,l=9790,c=9800),6.4),9795)
        self.assertAlmostEqual(stop_fill(dict(long=False,stop=10100),bar(0,o=10200,h=10210,l=10190,c=10200),6.4),10211.4)

    def test_next_open_entry_and_exit_no_forced_close(self):
        bs=[bar(i*3600) for i in range(60)];data={'candles':{'H1':bs}}
        start=24*3600;end=40*3600
        def fixed(prior,b):return True if b['time']==start else None
        def exit_at(prior,b,long):return b['time']==start+2*3600
        with patch('backend.h1_channel_research.breakout',side_effect=fixed),patch('backend.h1_channel_research.channel_exit',side_effect=exit_at):r=run(data,start,end)
        self.assertEqual(r['closed_trades'],1);t=r['trades'][0]
        self.assertEqual(t['entered'],start+3600);self.assertEqual(t['exit_bar'],start+3*3600)
        self.assertEqual(t['reason'],'CHANNEL_EXIT');self.assertLess(t['pnl_excluding_swaps'],0)
        with patch('backend.h1_channel_research.breakout',side_effect=fixed),patch('backend.h1_channel_research.channel_exit',return_value=False):r=run(data,start,end)
        self.assertEqual(r['closed_trades'],0);self.assertIsNotNone(r['open_position']);self.assertTrue(r['open_position_mark']['not_closed'])

    def test_gap_through_position_is_uncertain(self):
        start=24*3600;bs=[bar(i*3600) for i in range(60) if i!=27]
        with patch('backend.h1_channel_research.breakout',side_effect=lambda prior,b:True if b['time']==start else None),patch('backend.h1_channel_research.channel_exit',return_value=False):r=run({'candles':{'H1':bs}},start,40*3600)
        self.assertIsNotNone(r['uncertain_position']);self.assertEqual(r['closed_trades'],0)

if __name__=='__main__':unittest.main()
