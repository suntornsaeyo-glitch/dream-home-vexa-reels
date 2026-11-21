"""Vexa Viral: AI entertainment stills, natural comedy voice, 30 original daily concepts.
Use preview mode first. API charges are estimates, NOT an enforceable provider billing limit.
"""
from __future__ import annotations
import base64, datetime as dt, json, math, os, random, re, subprocess, sys, time
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from affiliate import approved_products, select_affiliate, affiliate_story, affiliate_caption

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
STATE=ROOT/'data/state.json'; TZ=dt.timezone(dt.timedelta(hours=7))
TODAY=dt.datetime.now(TZ).date().isoformat(); MONTH=TODAY[:7]
TOPICS=[
    ("Funny Animals", "My Cat Became the CEO", "a serious orange cat in a tiny business suit running an office full of confused humans", "The cat's first company rule: meetings are replaced by naps."),
    ("Absurd Comedy", "The Banana That Called the Police", "a talking banana at a grocery store reporting an outrageous crime", "Someone peeled its best friend."),
    ("AI Memes", "When Your Alarm Clock Quits", "an expressive alarm clock storming out of a messy bedroom carrying a suitcase", "Even the alarm needs a day off."),
    ("Comedy Stories", "The Robot Who Tried to Cook", "a friendly household robot proudly cooking a wildly chaotic breakfast", "The smoke alarm becomes the food critic."),
    ("Funny Animals", "Dog Applies for a Human Job", "a fluffy golden dog giving a confident job interview in a modern office", "His only requested salary is unlimited treats."),
    ("Absurd Comedy", "Giant Pineapple at the Bus Stop", "a giant friendly pineapple politely waiting among ordinary commuters", "The bus driver says no food allowed."),
    ("AI Memes", "My Wi-Fi Has Feelings", "a home internet router acting like a dramatic soap opera star", "It disconnects whenever someone calls it slow."),
    ("Comedy Stories", "The World's Worst Time Traveler", "a hapless time traveler arriving five minutes early to the wrong party", "He invented time travel just to be late again."),
    ("Funny Animals", "A Penguin at the Gym", "a determined penguin training beside oversized bodybuilders", "The penguin's secret workout is sliding to the snacks."),
    ("Absurd Comedy", "A Potato Becomes President of the Fridge", "a regal potato addressing vegetables inside a refrigerator", "Every vegetable votes yes except the French fries."),
    ("AI Memes", "When Monday Becomes a Person", "a grumpy personified Monday appearing at a bright weekend picnic", "Everyone tries to hide behind Tuesday."),
    ("Comedy Stories", "The Ghost Who Is Afraid of Humans", "a harmless translucent cartoonish ghost nervously hiding in a charming old house", "The ghost screams louder than its visitors."),
    ("Funny Animals", "The Cat Who Stole the Weather Forecast", "a sophisticated tuxedo cat presenting weather on a TV studio set", "The forecast is ninety percent chance of naps."),
    ("Absurd Comedy", "An Avocado Opens a Spa", "a smiling avocado running a luxury wellness spa for vegetables", "The cucumber requests a face mask."),
    ("AI Memes", "My Phone Is Jealous of My Laptop", "a phone and laptop portrayed as expressive fictional tech characters on a desk", "The phone starts sending itself notifications."),
    ("Comedy Stories", "A Superhero With One Useless Power", "a kind superhero in an original colorful costume saving a city in tiny unhelpful ways", "Their superpower is finding lost socks."),
    ("Funny Animals", "The Office Hamster Gets Promoted", "a tiny hamster in a CEO chair with a massive desk and employees", "The hamster immediately schedules a wheel meeting."),
    ("Absurd Comedy", "A Watermelon Joins the Police", "a cheerful watermelon police officer directing traffic in a fictional city", "The watermelon issues a ticket for speeding smoothies."),
    ("AI Memes", "When Your Coffee Talks Back", "a paper coffee cup with expressive face in a sleepy home kitchen", "It refuses to wake up before its owner."),
    ("Comedy Stories", "The Alien Who Loves Earth Snacks", "a cute original alien visiting a convenience store for the first time", "It travels galaxies to buy potato chips."),
    ("Funny Animals", "Grandma Duck vs Smart Home", "an elderly duck trying to command a futuristic voice-controlled house", "The house only understands quack."),
    ("Absurd Comedy", "The Giant Donut Escape", "a huge runaway donut rolling through a pastel city street", "The police officer follows with a cup of coffee."),
    ("AI Memes", "When Your Fridge Judges You", "a refrigerator with a skeptical expressive face watching midnight snacking", "It turns the light off in disappointment."),
    ("Comedy Stories", "A Wizard Who Forgot His Password", "a funny original wizard trying to unlock a glowing magic spellbook", "The password hint is abracadabra123."),
    ("Funny Animals", "A Dog Hosts a Cooking Show", "a corgi wearing chef clothes presenting a ridiculous TV food show", "Every recipe ends with dog biscuits."),
    ("Absurd Comedy", "An Angry Lemon at the Restaurant", "an expressive lemon complaining to a waiter in a whimsical cafe", "The waiter asks it to stop being sour."),
    ("AI Memes", "My Vacuum Cleaner Wants a Vacation", "a robot vacuum with a tiny beach hat escaping across a living room", "It refuses to clean another crumb."),
    ("Comedy Stories", "The Most Polite Monster Ever", "a giant gentle original fuzzy monster carefully navigating a crowded city", "It apologizes to every building it bumps."),
    ("Funny Animals", "A Cat Opens a Luxury Hotel", "a smug fluffy cat welcoming guests to an extravagant fictional pet hotel", "Check-in requires a belly rub."),
    ("Absurd Comedy", "The Great Fruit Dance-Off", "original lively fruit characters competing in a colorful dance competition", "The banana slips before the music even starts."),
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

def gemini_script(title,desc,punchline,genre,affiliate=None):
    fallback=(f'Okay, nobody expected this. {desc.capitalize()}. '
       'At first, everything seems perfectly normal. Then the situation gets more ridiculous by the second. '
       f'Just when everyone thinks it cannot get stranger, {punchline[0].lower()+punchline[1:]} '
       'That is one way to solve a problem.')
    key=os.getenv('GEMINI_API_KEY','')
    if not key: return fallback,'template'
    try:
        url='https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent'
        prompt=(f'Create a 45-65 word ORIGINAL English comedy voiceover for a 25-40 second Facebook Reel. '
          f'Genre: {genre}; title: {title}; premise: {desc}; mandatory final punchline: {punchline}. '
          'Structure: irresistible first-2-second hook, setup, escalating ridiculous twist, punchline in final sentence. '
          'Fun, punchy, naturally spoken American English, family friendly, no real-world misinformation, '
          'no copyrighted characters, no hateful or sexual jokes, no real celebrities, no speech labels, narration only. '
          +(f'This is a fictional AI skit featuring a generic prop in the category {affiliate["category"]}. '
            'Never claim the product was tested, works as shown, solves problems, or has any verified feature or price. '
            'Do not create an endorsement or review.' if affiliate else ''))
        r=requests.post(url,headers={'x-goog-api-key':key},json={'contents':[{'parts':[{'text':prompt}]}],
                    'generationConfig':{'temperature':0.95,'maxOutputTokens':260}},timeout=35)
        if not r.ok:
            print('Gemini unavailable; using local comic voiceover. HTTP',r.status_code)
            return fallback,'template'
        txt=r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        if 35<=len(txt.split())<=95: return txt,'gemini'
    except Exception as e: print('Gemini fallback:',str(e)[:140])
    return fallback,'template'

def openai_image(key,prompt,file):
    model=os.getenv('IMAGE_MODEL','gpt-image-1-mini')
    payload={'model':model,'prompt':prompt,'size':'1024x1536','quality':'medium','n':1}
    data=reqpost('https://api.openai.com/v1/images/generations',headers={'Authorization':'Bearer '+key},json=payload).json()
    raw=base64.b64decode(data['data'][0]['b64_json']); file.write_bytes(raw)
    with Image.open(file) as im: im.verify()

def openai_image_reference(key,prompt,reference,file):
    """Generate a changed camera view based on the original house photo."""
    model=os.getenv('IMAGE_MODEL','gpt-image-1-mini')
    with open(reference,'rb') as fh:
        r=requests.post('https://api.openai.com/v1/images/edits',
            headers={'Authorization':'Bearer '+key},
            data={'model':model,'prompt':prompt,'size':'1024x1536','quality':'medium','n':'1'},
            files={'image':(reference.name,fh,'image/png')},timeout=220)
    if not r.ok: raise RuntimeError(f'Image edit failed {r.status_code}: {r.text[:350]}')
    file.write_bytes(base64.b64decode(r.json()['data'][0]['b64_json']))
    with Image.open(file) as im: im.verify()

def create_caption(title,desc,genre,punchline):
    tags=['#VexaViral','#FunnyReels','#AIComedy']
    if genre=='Funny Animals': tags+=['#FunnyAnimals','#AnimalComedy']
    elif genre=='Absurd Comedy': tags+=['#AbsurdHumor','#SurrealComedy']
    elif genre=='AI Memes': tags+=['#AIMemes','#RelatableMemes']
    else: tags+=['#ComedyShorts','#FunnyStories']
    return (f'{title}\n\n{desc.capitalize()}. '
            f'Plot twist: {punchline} '
            'Which character should return next?'
            '\n\nAI-generated fictional comedy.\n\n'+' '.join(tags[:6]))

def voice(key,text,file):
    model=os.getenv('VOICE_MODEL','gpt-4o-mini-tts'); name=os.getenv('VOICE_NAME','onyx')
    payload={'model':model,'voice':name,'input':text,'response_format':'mp3','speed':0.96}
    if model=='gpt-4o-mini-tts': payload['instructions']='Perform a fun English comedy narrator voiceover with a warm, expressive, natural American accent. Playful timing and micro-pauses before jokes. Clear delivery, lively but not shouty, entertaining and human-like. Let the last punchline land with a deliberate pause.'
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
        d.text((88,120),'VEXA VIRAL',font=f1,fill=(255,217,161))
        d.text((88,202),subtitle,font=f2,fill='white')
        d.rounded_rectangle((50,1773,1030,1860),radius=15,fill=(7,21,28,150))
        d.text((82,1795),'AI-GENERATED FICTIONAL COMEDY',font=f3,fill='white')
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
    genre,title,desc,punchline=TOPICS[idx]
    products=approved_products()
    affiliate=select_affiliate(TODAY,products)
    if affiliate:
        genre,title,desc,punchline=affiliate_story(affiliate)
    if envbool('DRY_RUN'):
        caption=affiliate_caption(title,affiliate) if affiliate else create_caption(title,desc,genre,punchline)
        narration=(f'Okay, nobody expected this. {desc.capitalize()}. '
                   f'Then things got really weird. {punchline}')
        (OUT/'caption.txt').write_text(caption,encoding='utf-8')
        (OUT/'narration.txt').write_text(narration,encoding='utf-8')
        (OUT/'preview_plan.json').write_text(json.dumps({
            'brand':'Vexa Viral','genre':genre,'title':title,'premise':desc,
            'affiliate_id':affiliate['id'] if affiliate else None,'affiliate_ready':bool(affiliate),
            'punchline':punchline,'caption':caption,'mode':'OFFLINE DRY RUN',
            'api_calls':0,'facebook_publish':False
        },ensure_ascii=False,indent=2),encoding='utf-8')
        print('OFFLINE DRY RUN: output/preview_plan.json; no paid API or Facebook request')
        return
    narration,script_source=gemini_script(title,desc,punchline,genre,affiliate)
    (OUT/'narration.txt').write_text(narration)
    key=os.getenv('OPENAI_API_KEY','')
    if not key: raise RuntimeError('OPENAI_API_KEY missing: Entertainment mode needs a valid image API key.')
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
    shots=[
        ('THE SETUP',f'Wide cinematic comedy establishing shot. {desc}. Make the situation instantly readable.'),
        ('IT GETS WORSE',f'Closer medium shot of EXACT SAME main character and matching location, escalating funny confusion from {desc}. Comedic visual storytelling.'),
        ('PLOT TWIST',f'The EXACT SAME character and location in the hilarious punchline moment: {punchline}. Strong facial expression or comic physical action.')
    ]
    design_identity=(f'Original AI comedy series {genre}. TITLE {title}. '
        f'Main premise: {desc}. '
        'Create striking photorealistic but absurd safe-for-work visual comedy with expressive fictional characters, '
        'consistent character face, costume, proportions and location across all scenes. '
        'High production value, cinematic lighting, 35mm lens, bold visual staging, vibrant attractive colors, '
        'portrait 2:3 composition, no real people or celebrities, no brand logos, no signs, no subtitles, '
        'no lettering, no collage, no watermarks. Clearly imaginative fiction. '
        +'NEVER portray a generic gadget as a factual product demonstration or invent performance results.')
    reference=None
    for i in range(images_n):
        image_path=OUT/f'photo_{i}.png'
        prompt=(design_identity+' Shot '+str(i+1)+' of '+str(images_n)+': '+shots[i][1]
          +' Reference is the same character and scene. Preserve character identity and overall visual continuity.')
        reserve(state,est_img,f'Entertainment AI scene {i+1}/{images_n}')
        if i==0:
            openai_image(key,prompt,image_path); reference=image_path
        else:
            openai_image_reference(key,prompt,reference,image_path)
        frame=OUT/f'frame_{i}.jpg'
        fit_canvas(image_path,frame,title,shots[i][0]); frames.append(frame)
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
    caption=affiliate_caption(title,affiliate) if affiliate else create_caption(title,desc,genre,punchline)
    (OUT/'caption.txt').write_text(caption,encoding='utf-8')
    meta={'date':TODAY,'title':title,'genre':genre,'caption':caption,'script_source':script_source,'voice_source':voice_source,'images':images_n,'brand':'Vexa Viral','affiliate_id':affiliate['id'] if affiliate else None,'affiliate_ready':bool(affiliate),'estimated_run_usd':round(remaining,4),
          'estimated_month_usd':state['spent_estimate_by_month'].get(MONTH),'NOTE':'Illustrated video with Ken Burns motion, NOT native AI video. Estimates are not billed amounts; confirm provider limits.'}
    (OUT/'metadata.json').write_text(json.dumps(meta,indent=2))
    print('SUCCESS: created',result,'bytes',result.stat().st_size, 'VOICE',voice_source)
    if not (envbool('ENABLE_PUBLISH') and envbool('FB_LIVE_APPROVED')):
        print('PREVIEW ONLY: publishing requires BOTH ENABLE_PUBLISH and FB_LIVE_APPROVED=true');return
    if not (os.getenv('FB_PAGE_ID') and os.getenv('FB_PAGE_ACCESS_TOKEN')): raise RuntimeError('Missing Facebook page secrets')
    response=publish(result,title,caption); print('Facebook response:',response)
    state['published'][TODAY]=response;save_state(state)

if __name__=='__main__':
    try: main()
    except Exception as ex:
        print('ERROR:',ex,file=sys.stderr); sys.exit(1)
