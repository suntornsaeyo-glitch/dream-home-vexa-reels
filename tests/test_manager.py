import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from settings import validate_settings
from affiliate import select_affiliate, score

class ManagerTests(unittest.TestCase):
    def test_budget(self):
        self.assertEqual(validate_settings({})['daily_cap_usd'],.5)
        for x in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):validate_settings({'monthly_cap_usd':x})
        with self.assertRaises(ValueError):validate_settings({'images_per_reel':4})
    def test_rotation(self):
        a={'id':'a','price_thb':100,'commission_pct':10}
        b={'id':'b','price_thb':300,'commission_pct':10}
        self.assertEqual(score(b),30)
        self.assertEqual(select_affiliate('2026-11-21',[a,b],{})['id'],'b')
        self.assertEqual(select_affiliate('2026-11-22',[a,b],{'2026-11-21':{'affiliate_id':'b'}})['id'],'a')
        self.assertIsNone(select_affiliate('2026-11-28',[a,b],{}))
