"""Curated affiliate catalog. No automatic product invention, scraping or affiliate signup."""
import json
import os
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
    if u.hostname in ('example.com','localhost') or u.hostname.endswith('.example'):
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

def select_affiliate(date_string,products):
    """70% of a 30-day cycle is affiliate-ready. Never fabricate a product."""
    if not products:
        return None
    date=dt.date.fromisoformat(date_string)
    ix=(date-dt.date(2026,11,21)).days
    if ix%10 in (7,8,9): # 30% organic comedy
        return None
    return products[(ix//1)%len(products)]

def affiliate_caption(title,p):
    return (f'{title}\\n\\n'
        'AI-generated comedy skit. The product shown is a fictional illustration, '
        'not a real demonstration or review.\\n'
        f'Product listing: {p["title"]}\\n'
        'Affiliate disclosure: I may earn a commission if you purchase through this link, at no extra cost to you.\\n'
        f'{p["affiliate_url"]}\\n\\n'
        '#VexaViral #AIFunny #AffiliateFinds #GadgetFinds #ComedyReels')

def affiliate_story(p):
    # A product is never presented as tested, personally used, or performing invented feats.
    subject=p['visual_description']
    return (
        'AI Product Comedy',
        f'When a {p["category"].replace("_"," ")} Gadget Becomes the Boss',
        f'An imaginative fictional comedy scene featuring a generic {subject}. '
        'The gadget acts like an overly confident cartoon boss in a colorful household. '
        'No text or real brand marks on the fictional prop.',
        'The gadget gives everyone a performance review, including the toaster.'
    )
