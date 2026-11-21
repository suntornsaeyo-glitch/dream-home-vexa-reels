"""Dream Home Vexa free-first reel factory. Illustration-based, not photorealistic AI-video."""
import datetime as dt
import json
import math
import os
import random
import subprocess
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
DATA = ROOT / 'data'
STATE = DATA / 'state.json'
OUT.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
TOPICS = [
    'Two Bedrooms in a Tiny Dream Home', 'A Tiny Tropical Paradise',
    'Concrete and Red Brick Dream House', 'A Small Home With a Big View',
    'The Smartest Tiny House Layout', 'A Backyard Transformation Concept',
    'A Minimalist House in the Jungle', 'One Floor Plan, Three Styles',
    'The Dream Home With a Courtyard', 'A Tiny Pool Villa Concept',
    'Modern Tropical House Design', 'A Home Built Around a Tree',
    'Five Clever Small-Space Ideas', 'A Cozy Home in the Rain',
    'A Futuristic Modular Dream Home', 'Concrete Versus Red Brick',
    'A Narrow Lot Dream Home', 'The Ultimate Open-Plan Living Room',
    'Tiny Kitchen, Smart Design', 'A Modern Home in the Mountains',
    'A Dream Home Under the Stars', 'The Perfect Outdoor Terrace',
    'A House Inspired by Nature', 'Three Amazing Tiny Home Concepts',
    'A Simple Home With Warm Lighting', 'An Incredible Rooftop Garden',
    'The Most Peaceful Tiny Retreat', 'A Hidden Garden Dream Home',
    'The House of Tomorrow', 'The Best Dream Home Designs'
]

def font(size, bold=False):
    paths = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
             '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def story(title):
    # API text is optional, never request paid image/video tiers.
    key = os.getenv('GEMINI_API_KEY', '')
    fallback = (f'Imagine a home that makes every square meter count. {title}. '
                'Natural light, smart spaces, warm materials, and a garden designed for everyday living. '
                'This is an original architectural concept, not a real construction project. '
                'Which detail would you keep in your dream home?')
    if not key:
        return fallback
    model = 'gemini-2.5-flash-lite'
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    prompt = (f'Write one fresh 50-65 word English narration for a Facebook Reel titled "{title}". '
              'Focus on tangible home design details, no unverifiable prices, no claims it exists, '
              'make clear it is a design concept, end with a question. Output narration only.')
    try:
        r = requests.post(url, params={'key': key}, json={'contents':[{'parts':[{'text':prompt}]}],
                  'generationConfig':{'temperature':0.8,'maxOutputTokens':220}}, timeout=25)
        if r.status_code in (429,403):
            print('Free-tier blocked or exhausted; using original fallback narration.')
            return fallback
        r.raise_for_status()
        result = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        if 30 <= len(result.split()) <= 100: return result
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        print(f'Text AI unavailable; fallback used: {str(exc)[:140]}')
    return fallback

def scene(title, index, seed, output):
    rng = random.Random(seed + index * 1201)
    W,H=540,960
    img=Image.new('RGB',(W,H))
    d=ImageDraw.Draw(img)
    scheme=[((15,37,58),(83,156,180)),((23,38,52),(142,153,142)),((23,31,51),(165,126,108)),((18,50,51),(109,170,146))][seed%4]
    for y in range(H):
        t=y/H
        col=tuple(int(scheme[0][v]*(1-t)+scheme[1][v]*t) for v in range(3))
        d.line((0,y,W,y), fill=col)
    # Stars/clouds and tropical landscape
    for _ in range(18):
        x=rng.randrange(W); y=rng.randrange(120,480); r=rng.randrange(1,3)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(208,228,222))
    d.ellipse((370,150,454,234),fill=(249,204,129))
    d.polygon([(0,650),(100,600),(230,660),(390,590),(540,640),(540,960),(0,960)],fill=(39,82,70))
    d.rectangle((0,720,W,H),fill=(62,112,82))
    # Different facade architectural concepts
    x=68+((index%3)-1)*8; y=445+(index%2)*15
    ww=410; hh=280
    d.rectangle((x+17,y+18,x+ww+18,y+hh+18),fill=(22,45,45))
    d.rectangle((x,y,x+ww,y+hh),fill=(220,207,181) if index%2 else (193,190,171))
    d.polygon([(x-22,y+2),(x+ww+21,y+2),(x+ww+5,y-31),(x+12,y-31)],fill=(36,39,45))
    # Brick accent
    d.rectangle((x+ww-100,y,x+ww,y+hh), fill=(151,74,57))
    for by in range(y+16,y+hh,24):
        d.line((x+ww-100,by,x+ww,by),fill=(196,125,98),width=2)
        for bx in range(x+ww-100 + (12 if (by//24)%2 else 0),x+ww,42):
            d.line((bx,by,bx,by+24),fill=(196,125,98),width=2)
    # Window panes & warm interior
    for cx in [x+35,x+143]:
        d.rectangle((cx,y+54,cx+88,y+229),fill=(28,68,75),outline=(34,41,43),width=7)
        d.rectangle((cx+12,y+69,cx+75,y+215),fill=(221,177,119))
        d.line((cx+45,y+60,cx+45,y+222), fill=(47,57,62),width=7)
    d.rectangle((x+258,y+65,x+315,y+hh),fill=(45,69,72),outline=(27,36,38),width=7)
    d.ellipse((x+297,y+180,x+302,y+185),fill=(240,208,149))
    # Landscape foreground
    for xx in [35,500]:
        d.line((xx,800,xx+12,605), fill=(90,61,40),width=13)
        for a in range(-2,3):
            d.ellipse((xx+a*26-45,570+abs(a)*9,xx+a*26+55,650+abs(a)*9), fill=(34,108+rng.randrange(25),72))
    d.polygon([(0,845),(210,777),(348,777),(540,845),(540,960),(0,960)], fill=(163,149,113))
    # Onscreen hook, title in two-line safe zone
    d.rounded_rectangle((28,44,512,160),radius=18,fill=(18,33,42))
    d.text((46,61),'DREAM HOME VEXA',font=font(24,True),fill=(246,204,133))
    small=['AI HOME CONCEPT','TINY HOUSE IDEAS','MODERN HOME DESIGN','DREAM HOME REVEAL','TROPICAL ARCHITECTURE'][index]
    d.text((46,108),small,font=font(21),fill=(232,242,239))
    d.text((28,904),'AI-GENERATED DESIGN CONCEPT',font=font(15,True),fill=(251,250,236))
    img.save(output)

def execute(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

def render(title, narration, seed):
    frames=[]
    for i in range(5):
        target=OUT/f'scene_{i}.png'
        scene(title,i,seed,target)
        frames.append(target)
    (OUT/'narration.txt').write_text(narration,encoding='utf-8')
    execute('espeak-ng','-v','en-us','-s','143','-w',str(OUT/'voice.wav'),narration)
    lines=[]
    for p in frames: lines += [f"file '{p}'",'duration 6']
    lines += [f"file '{frames[-1]}'"]
    (OUT/'slides.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    execute('ffmpeg','-y','-loglevel','error','-safe','0','-f','concat','-i',str(OUT/'slides.txt'),
            '-i',str(OUT/'voice.wav'),'-af','apad','-t','30','-r','24','-vf','scale=540:960,format=yuv420p',
            '-c:v','libx264','-preset','veryfast','-crf','27','-c:a','aac','-b:a','96k',
            '-movflags','+faststart',str(OUT/'reel.mp4'))

def graph_post(path, data=None, headers=None, json_payload=False):
    base='https://graph.facebook.com/'+os.getenv('GRAPH_VERSION','v27.0')
    token=os.environ['FB_PAGE_ACCESS_TOKEN']
    req={'headers':{'Authorization':f'Bearer {token}',**(headers or {})},'timeout':120}
    if json_payload: req['json']=data
    else: req['data']=data
    r=requests.post(base+'/'+path,**req)
    r.raise_for_status()
    return r.json()

def publish(reel, title, caption):
    page=os.environ['FB_PAGE_ID']; token=os.environ['FB_PAGE_ACCESS_TOKEN']
    start=graph_post(f'{page}/video_reels',{'upload_phase':'start'})
    video_id=start['video_id']
    upload_url=start.get('upload_url',f'https://rupload.facebook.com/video-upload/{os.getenv("GRAPH_VERSION","v27.0")}/{video_id}')
    body=reel.read_bytes()
    r=requests.post(upload_url,headers={'Authorization':f'OAuth {token}',
                'offset':'0','file_size':str(len(body)),'Content-Type':'application/octet-stream'},data=body,timeout=240)
    r.raise_for_status()
    result=graph_post(f'{page}/video_reels',{'upload_phase':'finish','video_id':video_id,
                     'video_state':'PUBLISHED','title':title,'description':caption})
    return {'video_id':video_id,'publish_response':result}

def main():
    today=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).date().isoformat()
    state=json.loads(STATE.read_text()) if STATE.exists() else {'published':{}}
    if today in state['published']:
        print('Already recorded a published Reel today; refusing duplicate publish.')
        return
    idx=(dt.date.fromisoformat(today)-dt.date(2026,11,21)).days % len(TOPICS)
    title=TOPICS[idx]
    caption=f'{title} | An original architectural concept. Which design would you choose? #DreamHome #HomeDesign #TinyHouse #AIArchitecture'
    narration=story(title)
    render(title,narration,seed=idx)
    (OUT/'metadata.json').write_text(json.dumps({'date':today,'title':title,'caption':caption,
                                 'narration':narration,'note':'Illustrated architectural concept, not AI-generated photoreal footage'},indent=2),encoding='utf-8')
    print('Created:',OUT/'reel.mp4', '| date:',today)
    if os.getenv('ENABLE_PUBLISH','false').lower() != 'true':
        print('Preview mode: posting disabled. Set repository variable ENABLE_PUBLISH=true after Meta authorization.')
        return
    if not (os.getenv('FB_PAGE_ID') and os.getenv('FB_PAGE_ACCESS_TOKEN')):
        raise RuntimeError('Facebook publishing enabled but FB_PAGE_ID / FB_PAGE_ACCESS_TOKEN missing.')
    result=publish(OUT/'reel.mp4',title,caption)
    state['published'][today]=result
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Reel upload/publish requested:',json.dumps(result))
    print('IMPORTANT: Check processing/published status in Meta before treating the Reel as publicly visible.')

if __name__=='__main__': main()
