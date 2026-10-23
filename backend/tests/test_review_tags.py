import tempfile,unittest
from pathlib import Path
from backend import journaling

class ReviewTagsTest(unittest.TestCase):
    def test_reviews_are_source_isolated_and_do_not_modify_executions(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'journal.db'
            ident=journaling.add_trade(path,{'status':'closed','symbol':'BTCUSDm'})
            with journaling.connect(path) as c:before=journaling.records(c)
            journaling.tags(path,'manual',ident,[' Early entry '],['Wait for close'])
            self.assertEqual(journaling.tags(path,'manual')['tags'][ident]['mistakes'],['early entry'])
            self.assertEqual(journaling.tags(path,'mt5')['tags'],{})
            with journaling.connect(path) as c:self.assertEqual(journaling.records(c),before)
            with self.assertRaises(ValueError):journaling.tags(path,'mt5',ident,[],[])
            opened=journaling.add_trade(path,{'status':'open','symbol':'BTCUSDm'})
            with self.assertRaises(ValueError):journaling.tags(path,'manual',opened,[],[])
            with self.assertRaises(ValueError):journaling.tags(path,'manual',ident,['x'*61],[])

if __name__=='__main__':unittest.main()
