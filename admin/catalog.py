import io, json, math, uuid
import pandas as pd
CATEGORIES={'home_gadgets':'ของใช้ในบ้าน','pet_gadgets':'สัตว์เลี้ยง','kitchen_gadgets':'อุปกรณ์ครัว','desk_gadgets':'โต๊ะทำงาน','funny_gifts':'ของขวัญ','tech_accessories':'อุปกรณ์ไอที'}
ALIASES={'ชื่อสินค้า':'title','ชื่อ':'title','ลิงก์':'affiliate_url','ลิงก์ affiliate':'affiliate_url','ราคา':'price_thb','ราคา (บาท)':'price_thb','ค่าคอมมิชชัน (%)':'commission_pct','คอมมิชชัน':'commission_pct','หมวดหมู่':'category','คำอธิบาย':'visual_description','รหัส':'id'}
def number(v):
    try:
        n=float(str(v).strip().replace(',','').replace('%',''))
        return n if math.isfinite(n) and n>=0 else 0.0
    except (ValueError,TypeError): return 0.0
def normalize(row):
    row={ALIASES.get(str(k).strip().lower(),str(k).strip().lower()):v for k,v in row.items()}
    def txt(k): return str(row.get(k,'') or '').strip()
    cat=txt('category')
    cat={v:k for k,v in CATEGORIES.items()}.get(cat,cat)
    if cat not in CATEGORIES: cat='home_gadgets'
    return {'id':txt('id') or uuid.uuid4().hex[:12],'title':txt('title'),'category':cat,'affiliate_url':txt('affiliate_url'),'program':'Shopee Thailand','visual_description':txt('visual_description') or CATEGORIES[cat],'price_thb':number(row.get('price_thb')),'commission_pct':min(100,number(row.get('commission_pct'))),'usage_rights_confirmed':False,'approved':False}
def import_table(blob,name):
    if len(blob)>10*1024*1024: raise ValueError('ไฟล์ใหญ่เกิน 10 MB')
    if name.lower().endswith('.xlsx'):
        frame=pd.read_excel(io.BytesIO(blob),dtype=str,engine='openpyxl')
    elif name.lower().endswith('.csv'):
        try: frame=pd.read_csv(io.BytesIO(blob),dtype=str,encoding='utf-8-sig')
        except UnicodeDecodeError: frame=pd.read_csv(io.BytesIO(blob),dtype=str,encoding='cp874')
    else: raise ValueError('รองรับ CSV และ XLSX เท่านั้น')
    if len(frame)>2000: raise ValueError('รองรับสูงสุด 2,000 แถวต่อครั้ง')
    return [normalize(row) for row in frame.fillna('').to_dict('records')]
def score(p): return number(p.get('price_thb'))*min(100,number(p.get('commission_pct')))/100
def merge(existing,incoming):
    result=list(existing); ids={p['id'] for p in result}; urls={p.get('affiliate_url','') for p in result if p.get('affiliate_url')}
    added=skipped=0
    for p in incoming:
        if not p['title'] or not p['affiliate_url'] or p['id'] in ids or p['affiliate_url'] in urls: skipped+=1; continue
        result.append(p);ids.add(p['id']);urls.add(p['affiliate_url']);added+=1
    return result,added,skipped
