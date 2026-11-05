import tempfile, unittest
from pathlib import Path
from pydantic import ValidationError
from .process_reviews import ProcessReview, records
class ProcessReviewsTest(unittest.TestCase):
    def test_roundtrip_source_isolation_and_update(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.sqlite'
            record=ProcessReview(source='mt5',key='trade:42',plan='Wait for close',actual='Entered early',adherence='partly')
            records(path,'mt5',record)
            self.assertEqual(records(path,'mt5')['reviews']['trade:42']['plan'],'Wait for close')
            self.assertEqual(records(path,'manual')['reviews'],{})
            record.plan='Updated reflection';records(path,'mt5',record)
            self.assertEqual(len(records(path,'mt5')['reviews']),1)
            self.assertEqual(records(path,'mt5')['reviews']['trade:42']['plan'],'Updated reflection')
    def test_reject_invalid_record(self):
        for values in [dict(key='invalid'),dict(adherence='good-trader'),dict(plan='x'*2001),dict(source='other')]:
            with self.assertRaises(ValidationError):
                ProcessReview(**{**dict(source='mt5',key='week:2026-10-26'),**values})
