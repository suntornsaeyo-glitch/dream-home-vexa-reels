"""Dream Home Vexa V2: photographic AI stills, humanlike narration, Ken Burns videos.
Use preview mode first. API charges are estimates, NOT an enforceable provider billing limit.
"""
from __future__ import annotations
import base64, datetime as dt, json, math, os, random, re, subprocess, sys, time
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
STATE=ROOT/'data/state.json'; TZ=dt.timezone(dt.timedelta(hours=7))
TODAY=dt.datetime.now(TZ).date().isoformat(); MONTH=TODAY[:7]
TOPICS=[
('Two Bedrooms in a Tiny Dream Home','compact two-bedroom tropical concrete house with red brick accent and landscaped courtyard'),
('A Tiny Tropical Paradise','small luxury tropical bungalow with lush garden and plunge pool'),
('Concrete and Red Brick Dream House','affordable minimal concrete house with artisanal exposed red brick details'),
('A Small Home With a Big View','small contemporary hillside house with panoramic ocean view'),
('The Smartest Tiny House Layout','clever small modern house with practical open-plan living area'),
('A Backyard Transformation Concept','beautiful modern garden pavilion and landscaped backyard'),
('A Minimalist House in the Jungle','minimalist tropical concrete house in a rain forest'),
('One Floor Plan, Three Styles','modern contemporary single story home with timber and concrete'),
('The Dream Home With a Courtyard','small house wrapped around a green central courtyard'),
('A Tiny Pool Villa Concept','tiny single storey luxury villa next to a compact swimming pool'),
('Modern Tropical House Design','contemporary tropical home with slatted timber shading'),
('A Home Built Around a Tree','sustainable house wrapping around a preserved large tree'),
('Five Clever Small-Space Ideas','ingenious compact luxury residential architecture'),
('A Cozy Home in the Rain','warm tropical villa with a covered terrace in gentle rain'),
('A Futuristic Modular Dream Home','realistic prefabricated modular eco house'),
('Concrete Versus Red Brick','minimal tropical house made with concrete and red brick'),
('A Narrow Lot Dream Home','slim narrow-lot house with a beautiful garden entrance'),
('The Ultimate Open-Plan Living Room','luxurious warm open plan kitchen and living room'),
('Tiny Kitchen, Smart Design','beautiful efficient compact kitchen inside tiny home'),
('A Modern Home in the Mountains','small mountain getaway with natural stone details'),
('A Dream Home Under the Stars','small luminous contemporary home on a serene night'),
('The Perfect Outdoor Terrace','modern home with a garden terrace and outdoor lounge'),
('A House Inspired by Nature','sustainable elegant house with an organic garden'),
('Three Amazing Tiny Home Concepts','innovative single story small home design'),
('A Simple Home With Warm Lighting','minimalist cozy villa with beautiful warm lighting'),
('An Incredible Rooftop Garden','compact contemporary home with green rooftop'),
('The Most Peaceful Tiny Retreat','quiet zen tiny house nestled in a tropical garden'),
('A Hidden Garden Dream Home','beautiful private hidden courtyard home'),
('The House of Tomorrow','plausible near future eco friendly smart house'),
('The Best Dream Home Designs','award-worthy simple modern tropical home'),
]

def envbool(k, default=False): return os.getenv(k,str(default)).lower() in ('1','true','yes')
def reqpost(url, **kwargs):
    r=requests.post(url,timeout=180,**kwargs)
    if not r.ok: raise RuntimeError(f'Provider error {r.status_code}: {r.text[:350]}')
    return r

def load_state():
    try: data=json.loads(STATE.read_text())
    except (FileNotFoundError,json.JSONDecodeError): data={}
    data.setdefault('published',{}); data.setdefault('spent_estimate_by_month',{})
    return data

def save_state(data): STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def reserve(state, amount, service):
    # Conservative estimates, not measured invoices. Persist before API call to avoid runaway retries.
    cap=float(os.getenv('MONTHLY_SPEND_CAP_USD','5.00'))
    current=float(state['spent_estimate_by_month'].get(MONTH,0))
    if current+amount>cap+1e-9: raise RuntimeError(f'Budget guard stopped {service}: estimated ${current+amount:.3f} exceeds ${cap:.2f}. No new call.')
    state['spent_estimate_by_month'][MONTH]=round(current+amount,5); save_state(state)
    print(f'Reserved estimate ${amount:.3f} for {service}; estimated month total ${current+amount:.3f} (not verified billing)')

def gemini_script(title,desc):
    fallback=(f'Could this be your dream home? Imagine {desc}. '
      'The design combines natural light, practical spaces, and a welcoming connection to the garden. '
      'Every detail is created as an architectural concept, not a real property or construction project. '
      'Which feature would you add to make it yours?')
    key=os.getenv('GEMINI_API_KEY','')
    if not key: return fallback,'template'
    try:
        url='https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent'
        prompt=f'Write 56-72 words of original English video narration for a luxury design reel titled {title!r}, depicting {desc}. Natural cinematic documentary cadence. Begin with a striking hook, describe credible architectural features, do not claim a real home exists or give unverified prices, end with a question. Narration text only.'
        r=requests.post(url,headers={'x-goog-api-key':key},json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'temperature':0.85,'maxOutputTokens':250}},timeout=35)
        if not r.ok: print('Gemini unavailable; using local narration. HTTP',r.status_code); return fallback,'template'
        txt=r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        if 40<=len(txt.split())<=100: return txt,'gemini'
    except Exception as e: print('Gemini fallback:',str(e)[:150])
    return fallback,'template'

def openai_image(key,prompt,file):
    model=os.getenv('IMAGE_MODEL','gpt-image-1-mini')
    payload={'model':model,'prompt':prompt,'size':'1024x1536','quality':'medium','n':1}
    data=reqpost('https://api.openai.com/v1/images/generations',headers={'Authorization':'Bearer '+key},json=payload).json()
    raw=base64.b64decode(data['data'][0]['b64_json']); file.write_bytes(raw)
    with Image.open(file) as im: im.verify()

def voice(key,text,file):
    model=os.getenv('VOICE_MODEL','gpt-4o-mini-tts'); name=os.getenv('VOICE_NAME','onyx')
    payload={'model':model,'voice':name,'input':text,'response_format':'mp3','speed':0.96}
    if model=='gpt-4o-mini-tts': payload['instructions']='Narrate in natural American English for a premium architectural documentary. Warm, confident, relaxed and personable. Subtle wonder, gentle expressive pauses, no shouting, no advertisement voice. Maintain natural human phrasing.'
    r=reqpost('https://api.openai.com/v1/audio/speech',headers={'Authorization':'Bearer '+key},json=payload)
    if len(r.content)<3000: raise RuntimeError('Suspiciously short TTS audio')
    file.write_bytes(r.content)

def fallback_voice(text,file):
    wav=OUT/'fallback.wav'
    subprocess.run(['espeak-ng','-v','en-us','-s','142','-w',str(wav),text],check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-codec:a','libmp3lame','-qscale:a','4',str(file)],check=True)

def duration(f):
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(f)],capture_output=True,text=True,check=True)
    return float(result.stdout.strip())

def fit_canvas(inp,out,title,subtitle):
    with Image.open(inp) as source:
        im=source.convert('RGB')
        # Input portrait, fit cover to 1080x1920 with restrained title overlays
        W,H=1080,1920; sw,sh=im.size; scale=max(W/sw,H/sh)
        nw,nh=math.ceil(sw*scale),math.ceil(sh*scale)
        im=im.resize((nw,nh),Image.Resampling.LANCZOS)
        left=(nw-W)//2; top=(nh-H)//2; im=im.crop((left,top,left+W,top+H))
        overlay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(overlay)
        d.rounded_rectangle((52,92,1028,270),radius=28,fill=(7,21,28,184))
        path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; path2='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        f1=ImageFont.truetype(path,46); f2=ImageFont.truetype(path2,30); f3=ImageFont.truetype(path2,23)
        d.text((88,120),'DREAM HOME VEXA',font=f1,fill=(255,217,161))
        d.text((88,202),subtitle,font=f2,fill='white')
        d.rounded_rectangle((50,1773,1030,1860),radius=15,fill=(7,21,28,150))
        d.text((82,1795),'AI DESIGN CONCEPT  •  NOT A REAL PROPERTY',font=f3,fill='white')
        Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB').save(out,quality=91)

def assemble(frames,audio,out):
    # 3 large stills with slow Ken Burns effect; camera motion, NOT generative video.
    sound_d=duration(audio); total=max(29.0,min(43.0,sound_d+2.3)); fps=24
    segments=[]
    for i,p in enumerate(frames):
        seconds=total/len(frames); count=math.ceil(seconds*fps)
        vid=OUT/f'clip{i}.mp4'
        z='min(zoom+0.00022,1.13)' if i%2==0 else 'max(1.13-on*0.00020,1.0)'
        filt=f'scale=1200:2134,zoompan=z=\'{z}\':x=\'(iw-iw/zoom)/2\':y=\'(ih-ih/zoom)/2\':d={count}:s=1080x1920:fps={fps},format=yuv420p'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',str(p),'-vf',filt,'-t',str(seconds),'-r',str(fps),'-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-an',str(vid)],check=True)
        segments.append(vid)
    listing=OUT/'concat.txt'; listing.write_text('\n'.join("file '%s'"%s for s in segments)+'\n')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-af','loudnorm=I=-16:TP=-1.5:LRA=10,apad','-t',str(total),'-movflags','+faststart',str(out)],check=True)

def graph_post(path,data):
    version=os.getenv('GRAPH_VERSION','v27.0'); token=os.environ['FB_PAGE_ACCESS_TOKEN']
    return reqpost(f'https://graph.facebook.com/{version}/{path}',headers={'Authorization':'Bearer '+token},data=data).json()

def publish(reel,title,caption):
    page=os.environ['FB_PAGE_ID']; token=os.environ['FB_PAGE_ACCESS_TOKEN']; version=os.getenv('GRAPH_VERSION','v27.0')
    init=graph_post(f'{page}/video_reels',{'upload_phase':'start'}); vid=init['video_id']
    upload_url=init.get('upload_url',f'https://rupload.facebook.com/video-upload/{version}/{vid}')
    payload=reel.read_bytes()
    reqpost(upload_url,headers={'Authorization':'OAuth '+token,'offset':'0','file_size':str(len(payload)),'Content-Type':'application/octet-stream'},data=payload)
    result=graph_post(f'{page}/video_reels',{'upload_phase':'finish','video_id':vid,'video_state':'PUBLISHED','title':title,'description':caption})
    return {'video_id':vid,'response':result,'note':'Publishing requested; confirm actual video status in Meta.'}

def main():
    state=load_state()
    if TODAY in state['published']:
        print('Already published this date; refusing duplicate.'); return
    idx=(dt.date.fromisoformat(TODAY)-dt.date(2026,11,21)).days%len(TOPICS)
    title,desc=TOPICS[idx]
    narration,script_source=gemini_script(title,desc)
    (OUT/'narration.txt').write_text(narration)
    key=os.getenv('OPENAI_API_KEY','')
    if not key: raise RuntimeError('OPENAI_API_KEY missing: V2 does not silently revert to cartoon images.')
    images_n=int(os.getenv('IMAGES_PER_REEL','3'))
    if not 1<=images_n<=3: raise ValueError('IMAGES_PER_REEL must be 1..3')
    est_img=float(os.getenv('IMAGE_ESTIMATE_USD','0.12'))
    est_voice=float(os.getenv('VOICE_ESTIMATE_USD','0.05'))
    # Verify budget before any call, including voice; reserved amount persisted prior to calls.
    remaining=images_n*est_img+est_voice
    cap=float(os.getenv('MONTHLY_SPEND_CAP_USD','5'))
    used=float(state['spent_estimate_by_month'].get(MONTH,0))
    if remaining+used>cap: raise RuntimeError(f'Estimated budget too low for this run: current ${used:.2f}, run ${remaining:.2f}, cap ${cap:.2f}')
    frames=[]
    shot=['wide exterior establishing shot, 3/4 architectural angle','new complementary view of the same architectural style, close-up facade details','open plan living kitchen interior matching the same architecture']
    for i in range(images_n):
        image_path=OUT/f'photo_{i}.png'
        prompt=(f'Photorealistic high-end architectural photography. Subject: {desc}. '
                f'Shot: {shot[i]}. Realistic buildable proportions, consistent tropical modern aesthetic, '
                'concrete, warm natural timber, optional red brick. Beautiful realistic late afternoon light, '
                'refined landscaping, believable materials, tasteful luxurious atmosphere, 35mm architectural photography, '
                'original design. VERTICAL 2:3 composition. NO captions, NO letters, NO watermarks, NO diagrams, NO drawings, NO cartoon, NO people. '
                'Design concept, not a real listing.')
        reserve(state,est_img,f'AI image {i+1}/{images_n}')
        openai_image(key,prompt,image_path)
        frame=OUT/f'frame_{i}.jpg'; fit_canvas(image_path,frame,title,['PHOTOREALISTIC HOME CONCEPT','DESIGN DETAILS','INSIDE THE DREAM HOME'][i]); frames.append(frame)
    voice_path=OUT/'voice.mp3'; voice_source='OpenAI '+os.getenv('VOICE_MODEL','gpt-4o-mini-tts')
    if envbool('USE_PAID_VOICE',True):
        reserve(state,est_voice,'AI voice')
        try: voice(key,narration,voice_path)
        except Exception as exc:
            if not envbool('ALLOW_FALLBACK_VOICE',False): raise
            print('Paid voice failed; use eSpeak backup:',str(exc)[:150]); fallback_voice(narration,voice_path); voice_source='eSpeak backup'
    else:
        fallback_voice(narration,voice_path); voice_source='eSpeak backup'
    result=OUT/'reel.mp4'; assemble(frames,voice_path,result)
    meta={'date':TODAY,'title':title,'script_source':script_source,'voice_source':voice_source,'images':images_n,'estimated_run_usd':round(remaining,4),
          'estimated_month_usd':state['spent_estimate_by_month'].get(MONTH),'NOTE':'These are not actual billing statements. Confirm pricing and provider budget limits.'}
    (OUT/'metadata.json').write_text(json.dumps(meta,indent=2))
    print('SUCCESS: created',result,'bytes',result.stat().st_size, 'VOICE',voice_source)
    if not envbool('ENABLE_PUBLISH'):
        print('PREVIEW ONLY: publishing is OFF');return
    if not (os.getenv('FB_PAGE_ID') and os.getenv('FB_PAGE_ACCESS_TOKEN')): raise RuntimeError('Missing Facebook page secrets')
    caption=f'{title} — AI-generated architectural concept. Which feature would you choose? #DreamHome #HomeDesign #AIArchitecture #TinyHouse'
    response=publish(result,title,caption); print('Facebook response:',response)
    state['published'][TODAY]=response;save_state(state)

if __name__=='__main__':
    try: main()
    except Exception as ex:
        print('ERROR:',ex,file=sys.stderr); sys.exit(1)
