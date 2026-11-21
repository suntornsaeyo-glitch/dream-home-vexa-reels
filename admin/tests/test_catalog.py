import io,unittest
import pandas as pd
from admin.catalog import import_table,merge,score
class CatalogTests(unittest.TestCase):
    def test_thai_excel_and_csv(self):
        df=pd.DataFrame([{'ชื่อสินค้า':'ที่วางมือถือ','ลิงก์':'https://s.shopee.co.th/test','ราคา (บาท)':'200','ค่าคอมมิชชัน (%)':'10','หมวดหมู่':'อุปกรณ์ไอที'}])
        x=io.BytesIO();df.to_excel(x,index=False)
        for f,name in [(df.to_csv(index=False).encode('utf-8-sig'),'a.csv'),(x.getvalue(),'a.xlsx')]:
            p=import_table(f,name)[0]
            self.assertEqual(p['title'],'ที่วางมือถือ')
            self.assertEqual(score(p),20)
            self.assertFalse(p['approved'])
            self.assertEqual(merge([p],[p])[1],0)
