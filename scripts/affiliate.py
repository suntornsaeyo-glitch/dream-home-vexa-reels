"""Curated affiliate catalog. No automatic product invention, scraping or affiliate signup."""
import json
import os
import math
import datetime as dt
from pathlib import Path
from urllib.parse import urlparse

BASE=Path(__file__).resolve().parents[1]
CATALOG=BASE/'data'/'affiliate_products.json'
CATEGORIES={'home_gadgets','pet_gadgets','kitchen_gadgets','desk_gadgets','funny_gifts','tech_accessories'}

def valid_product(item):
    if not isinstance(item,dict) or item.get('approved') is not True:
        return False
    if item.get('category') not in CATEGORIES:
        return False
    for key in ('id','title','affiliate_url','program','visual_description'):
        if not isinstance(item.get(key),str) or not item[key].strip():
            return False
    if item.get('usage_rights_confirmed') is not True:
        return False
    u=urlparse(item['affiliate_url'])
    if u.scheme!='https' or not u.hostname or u.username or u.password:
        return False
    if u.hostname != 'shopee.co.th' and not u.hostname.endswith('.shopee.co.th') and u.hostname != 'shope.ee':
        return False
    if item['program'] != 'Shopee Thailand':
        return False
    if any(x in item['affiliate_url'].lower() for x in ('your-link','placeholder','affiliate-link-here')):
        return False
    return True

def approved_products():
    if not CATALOG.exists():
        return []
    data=json.loads(CATALOG.read_text(encoding='utf-8'))
    entries=data.get('products',[])
    if not isinstance(entries,list):
        raise ValueError('affiliate_products.json: products must be a list')
    seen=set(); result=[]
    for item in entries:
        if valid_product(item) and item['id'] not in seen:
            result.append(item)
            seen.add(item['id'])
    return result

def score(p):
    try:
        price=float(p.get('price_thb',0)); pct=float(p.get('commission_pct',0))
        return price*pct/100 if math.isfinite(price) and math.isfinite(pct) and price>=0 and 0<=pct<=100 else 0
    except (ValueError,TypeError): return 0

def select_affiliate(date_string,products,history=None):
    """70% of a 30-day cycle is affiliate-ready. Never fabricate a product."""
    if not products:
        return None
    date=dt.date.fromisoformat(date_string)
    ix=(date-dt.date(2026,11,21)).days
    if ix%10 in (7,8,9): # 30% organic comedy
        return None
    if history is None:
        return products[((ix//10)*7+ix%10)%len(products)]
    last={}
    for day,rec in history.items():
        pid=rec.get('affiliate_id')
        if pid: last[pid]=max(day,last.get(pid,''))
    return sorted(products,key=lambda p:(last.get(p['id'],''),-score(p),p['id']))[0]

def affiliate_caption(title,p):
    return (f'{title}\n\n'
        'คลิปตลกจาก AI เป็นเรื่องสมมติ ไม่ใช่ภาพทดสอบหรือรีวิวสินค้าจริง\n'
        f'สินค้าที่เกี่ยวข้อง: {p["title"]}\n'
        'ดูรายละเอียดและราคาปัจจุบันที่ Shopee\n'
        'ลิงก์แอฟฟิลิเอต: เพจอาจได้รับค่าคอมมิชชันหากคุณซื้อผ่านลิงก์นี้\n'
        f'{p["affiliate_url"]}\n\n'
        '#VexaViral #คลิปตลก #ป้ายยา #ของน่าใช้ #ช้อปปี้')

def affiliate_story(p):
    category={'home_gadgets':'ของใช้ในบ้าน','pet_gadgets':'ของใช้สัตว์เลี้ยง',
        'kitchen_gadgets':'ของใช้ในครัว','desk_gadgets':'อุปกรณ์โต๊ะทำงาน',
        'funny_gifts':'ของขวัญ','tech_accessories':'อุปกรณ์ไอที'}[p['category']]
    return ('ตลกสินค้า',f'เมื่อ{category}อยากเป็นเจ้านาย',
        f'ฉากตลกสมมติที่มีอุปกรณ์ทั่วไปประเภท {p["visual_description"]} ทำตัวเป็นเจ้านายจอมสั่ง ไม่ใช่สินค้าจริง',
        'สุดท้ายเจ้านายสั่งให้ทุกคนพัก แต่ตัวเองกลับต้องทำงานแทนทั้งหมด')
