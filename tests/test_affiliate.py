import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import affiliate

class AffiliateTests(unittest.TestCase):
    def test_unapproved_rejected(self):
        x={'id':'p1','title':'A','category':'pet_gadgets','affiliate_url':'https://shop.example.org/product',
           'program':'partner','visual_description':'generic cat toy','usage_rights_confirmed':True}
        self.assertFalse(affiliate.valid_product(x))
        x['approved']=True
        self.assertTrue(affiliate.valid_product(x))
    def test_bad_placeholder_rejected(self):
        x={'id':'p1','title':'A','category':'pet_gadgets','affiliate_url':'https://example.com/product',
           'program':'partner','visual_description':'generic cat toy','usage_rights_confirmed':True,'approved':True}
        self.assertFalse(affiliate.valid_product(x))
    def test_schedule_without_products(self):
        self.assertIsNone(affiliate.select_affiliate('2026-11-21',[]))
    def test_disclosure(self):
        x={'title':'Cat Toy','affiliate_url':'https://shop.example.org/product'}
        caption=affiliate.affiliate_caption('Funny Cat',x)
        self.assertIn('Affiliate disclosure:',caption)
        self.assertIn('https://shop.example.org/product',caption)
        self.assertIn('\n',caption)
    def test_ratio(self):
        p=[{'id':'a'}]
        import datetime as dt
        start=dt.date(2026,11,21)
        n=sum(affiliate.select_affiliate((start+dt.timedelta(days=i)).isoformat(),p) is not None for i in range(30))
        self.assertEqual(n,21)

if __name__=='__main__': unittest.main()
