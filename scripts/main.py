"""Vexa Viral Thailand: Thai comedy and Shopee affiliate preview studio.
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
    ("สัตว์ตลก", "เมื่อแมวเป็นประธานบริษัท", "แมวส้มใส่สูทนั่งประชุมในออฟฟิศ พนักงานมองด้วยความงุนงง", "กฎข้อแรกของบริษัทคือเปลี่ยนเวลาประชุมเป็นเวลานอน"),
    ("เรื่องเหนือจริง", "กล้วยแจ้งตำรวจ", "กล้วยพูดได้เดินเข้าโรงพักด้วยสีหน้าตกใจ", "เพื่อนของมันถูกปอกเปลือก"),
    ("มีม", "นาฬิกาปลุกขอลาออก", "นาฬิกาปลุกมีชีวิตลากกระเป๋าเดินทางออกจากห้องนอน", "แม้แต่นาฬิกาปลุกก็อยากนอนต่อ"),
    ("เรื่องหักมุม", "หุ่นยนต์เข้าครัว", "หุ่นยนต์พ่อครัวกำลังทำอาหารเช้าในครัวแสนวุ่นวาย", "เครื่องตรวจจับควันกลายเป็นกรรมการชิมอาหาร"),
    ("สัตว์ตลก", "หมาไปสมัครงาน", "สุนัขโกลเด้นนั่งสัมภาษณ์งานอย่างมั่นใจ", "เงินเดือนที่ขอคือขนมไม่จำกัด"),
    ("เรื่องเหนือจริง", "สับปะรดยักษ์รอรถเมล์", "สับปะรดยักษ์ยืนต่อแถวรอรถเมล์กับคนทั่วไป", "คนขับบอกว่าห้ามนำอาหารขึ้นรถ"),
    ("มีม", "ไวไฟก็มีหัวใจ", "เราเตอร์มีชีวิตทำท่าเหมือนตัวเอกละครน้ำเน่า", "พอใครบอกว่าเน็ตช้ามันก็ตัดสัญญาณทันที"),
    ("เรื่องหักมุม", "นักเดินทางข้ามเวลาสายเสมอ", "นักเดินทางข้ามเวลามาถึงงานเลี้ยงผิดวัน", "ประดิษฐ์เครื่องย้อนเวลาแล้วก็ยังมาสาย"),
    ("สัตว์ตลก", "เพนกวินเข้าฟิตเนส", "เพนกวินออกกำลังกายท่ามกลางนักกล้าม", "ท่าที่ถนัดที่สุดคือไถลไปหาขนม"),
    ("เรื่องเหนือจริง", "มันฝรั่งเป็นประธานตู้เย็น", "มันฝรั่งสวมมงกุฎกล่าวสุนทรพจน์ในตู้เย็น", "ทุกคนโหวตให้ยกเว้นเฟรนช์ฟรายส์"),
    ("มีม", "วันจันทร์มาปิกนิก", "ตัวละครวันจันทร์หน้าบึ้งโผล่กลางงานปิกนิกวันหยุด", "ทุกคนวิ่งไปหลบหลังวันอังคาร"),
    ("เรื่องหักมุม", "ผีที่กลัวคน", "ผีน้อยน่ารักซ่อนอยู่ในบ้านเก่าเมื่อมีแขกมาเยือน", "ผีร้องดังยิ่งกว่าแขก"),
    ("สัตว์ตลก", "แมวพยากรณ์อากาศ", "แมวดำขาวยืนหน้ากล้องในสตูดิโอข่าวอากาศ", "วันนี้มีโอกาสนอนเก้าสิบเปอร์เซ็นต์"),
    ("เรื่องเหนือจริง", "อะโวคาโดเปิดสปา", "อะโวคาโดมีชีวิตเปิดสปาหรูสำหรับผัก", "แตงกวาขอมาสก์หน้า"),
    ("มีม", "มือถือหึงโน้ตบุ๊ก", "มือถือและโน้ตบุ๊กมีชีวิตเถียงกันบนโต๊ะทำงาน", "มือถือส่งแจ้งเตือนให้ตัวเองทั้งวัน"),
    ("เรื่องหักมุม", "ฮีโร่พลังตามหาถุงเท้า", "ซูเปอร์ฮีโร่ชุดต้นฉบับพยายามช่วยชาวเมือง", "พลังพิเศษคือหาถุงเท้าหายได้ทุกคู่"),
    ("สัตว์ตลก", "แฮมสเตอร์ได้เลื่อนตำแหน่ง", "แฮมสเตอร์ตัวจิ๋วนั่งเก้าอี้ผู้บริหารตัวใหญ่", "คำสั่งแรกคือนัดประชุมบนวงล้อ"),
    ("เรื่องเหนือจริง", "แตงโมเป็นตำรวจจราจร", "แตงโมมีชีวิตโบกรถในเมืองสมมติ", "มันแจกใบสั่งให้สมูทตี้ที่ขับเร็ว"),
    ("มีม", "กาแฟเถียงเจ้าของ", "แก้วกาแฟมีชีวิตคุยกับเจ้าของที่ยังง่วงในครัว", "กาแฟบอกว่าตัวเองก็ยังไม่ตื่น"),
    ("เรื่องหักมุม", "เอเลี่ยนตามหาขนม", "เอเลี่ยนน่ารักเข้าร้านสะดวกซื้อครั้งแรก", "ข้ามกาแล็กซีมาซื้อแค่มันฝรั่งทอด"),
]

def envbool(k, default=False): return os.getenv(k,str(default)).lower() in ('1','true','yes')
def reqpost(url, **kwargs):
    r=requests.post(url,timeout=180,**kwargs)
    if not r.ok: raise RuntimeError(f'Provider error {r.status_code}: {r.text[:350]}')
    return r

def load_state():
    try: data=json.loads(STATE.read_text())
    except FileNotFoundError: data={}
    data.setdefault('generated',{}); data.setdefault('published',{}); data.setdefault('spent_estimate_by_month',{})
    return data

def save_state(data): STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def reserve(state, amount, service):
    # Conservative estimates, not measured invoices. Persist before API call to avoid runaway retries.
    cap=float(os.getenv('MONTHLY_SPEND_CAP_USD','5.00'))
    current=float(state['spent_estimate_by_month'].get(MONTH,0))
    if current+amount>cap+1e-9: raise RuntimeError(f'Budget guard stopped {service}: estimated ${current+amount:.3f} exceeds ${cap:.2f}. No new call.')
    state['spent_estimate_by_month'][MONTH]=round(current+amount,5); save_state(state)
    print(f'Reserved estimate ${amount:.3f} for {service}; estimated month total ${current+amount:.3f} (not verified billing)')

def thai_fallback(title,desc,punchline,affiliate=None):
    text=f'เรื่องมันเริ่มจาก{desc} แล้วความวุ่นวายก็เกิดขึ้น ใครจะคิดว่า{punchline}'
    if affiliate:
        text += ' นี่เป็นเรื่องสมมติจากเอไอ ไม่ใช่การทดลองสินค้าจริง สนใจสินค้าที่เกี่ยวข้องดูรายละเอียดจากลิงก์ช้อปปี้ได้ เพจอาจได้รับค่าคอมมิชชัน'
    return text

def gemini_script(title,desc,punchline,genre,affiliate=None):
    fallback=thai_fallback(title,desc,punchline,affiliate)
    key=os.getenv('GEMINI_API_KEY','')
    if not key: return fallback,'template'
    try:
        prompt=(f'เขียนบทพากย์ภาษาไทยธรรมชาติสำหรับคลิปตลก 20 ถึง 35 วินาที หัวข้อ {title} '
          f'เหตุการณ์ {desc} จุดหักมุม {punchline} เปิดเรื่องให้น่าสนใจ ใช้ภาษาพูดทั่วไป '
          'ตอบเฉพาะบทพากย์ภาษาไทย ไม่ต้องใส่ชื่อผู้พูด ไม่ล้อเลียนบุคคลจริง '
          'ไม่ใช้เนื้อหาอันตรายหรืออ้างข้อมูลเท็จ '
          +('เป็นเรื่องสมมติจากเอไอเกี่ยวกับอุปกรณ์ทั่วไป ห้ามอ้างสรรพคุณ ราคา ผลทดลอง หรือรีวิวจริง' if affiliate else ''))
        r=requests.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent',
          headers={'x-goog-api-key':key},json={'contents':[{'parts':[{'text':prompt}]}],
          'generationConfig':{'temperature':0.85,'maxOutputTokens':600}},timeout=35)
        if r.ok:
            txt=r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            if 60<=len(txt)<=480 and len(re.findall('[ก-๙]',txt))>=40:
                if affiliate:
                    txt += ' นี่เป็นเรื่องสมมติจากเอไอ ไม่ใช่รีวิวจริง ดูสินค้าที่เกี่ยวข้องจากลิงก์ช้อปปี้ เพจอาจได้รับค่าคอมมิชชัน'
                return txt,'gemini'
    except Exception:
        print('Gemini unavailable; using Thai fallback')
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
    tags=['#VexaViral','#คลิปตลก','#ตลกเอไอ']
    tags.append({'สัตว์ตลก':'#สัตว์ตลก','มีม':'#มีม','เรื่องเหนือจริง':'#เรื่องแปลก'}.get(genre,'#เรื่องหักมุม'))
    return f'{title}\n\n{desc}\nดูให้จบแล้วจะรู้ว่าเกิดอะไรขึ้น!\n\nเรื่องสมมติจากเอไอ\n'+' '.join(tags)

def voice(key,text,file):
    model=os.getenv('VOICE_MODEL','gpt-4o-mini-tts'); name=os.getenv('VOICE_NAME','onyx')
    payload={'model':model,'voice':name,'input':text,'response_format':'mp3','speed':0.96}
    if model=='gpt-4o-mini-tts': payload['instructions']='Speak native Central Thai with natural Thai pronunciation, tones and conversational rhythm. Friendly humorous Thai creator, expressive pauses before punchlines, no foreign accent, no exaggerated delivery. Read the Thai script exactly.'
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
        path='/usr/share/fonts/truetype/tlwg/Garuda-Bold.ttf'; path2='/usr/share/fonts/truetype/tlwg/Garuda.ttf'
        f1=ImageFont.truetype(path,46); f2=ImageFont.truetype(path2,30); f3=ImageFont.truetype(path2,23)
        d.text((88,120),'VEXA VIRAL',font=f1,fill=(255,217,161))
        d.text((88,202),subtitle,font=f2,fill='white')
        d.rounded_rectangle((50,1773,1030,1860),radius=15,fill=(7,21,28,150))
        d.text((82,1795),'เรื่องสมมติจากเอไอ ไม่ใช่การรีวิวจริง',font=f3,fill='white')
        Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB').save(out,quality=91)

def assemble(frames,audio,out):
    # 3 large stills with slow Ken Burns effect; camera motion, NOT generative video.
    sound_d=duration(audio); total=max(20.0,sound_d+1.5)
    if total>60: raise RuntimeError('Thai narration exceeds 60 seconds; review before retry')
    fps=24
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
        narration=thai_fallback(title,desc,punchline,affiliate)
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
    if TODAY in state['generated'] and not envbool('ALLOW_REGENERATE'):
        print('Already generated today; skipping duplicate paid generation'); return
    key=os.getenv('OPENAI_API_KEY','')
    if not key: raise RuntimeError('OPENAI_API_KEY missing: Entertainment mode needs a valid image API key.')
    images_n=int(os.getenv('IMAGES_PER_REEL','3'))
    if not 1<=images_n<=3: raise ValueError('IMAGES_PER_REEL must be 1..3')
    est_img=float(os.getenv('IMAGE_ESTIMATE_USD','0.12'))
    est_voice=float(os.getenv('VOICE_ESTIMATE_USD','0.05'))
    # Verify budget before any call, including voice; reserved amount persisted prior to calls.
    remaining=images_n*est_img+est_voice+(0.01 if os.getenv('GEMINI_API_KEY') else 0)
    cap=float(os.getenv('MONTHLY_SPEND_CAP_USD','5'))
    used=float(state['spent_estimate_by_month'].get(MONTH,0))
    if not all(math.isfinite(x) and x>=0 for x in (est_img,est_voice,cap,used)) or est_img<=0 or est_voice<=0: raise ValueError('Invalid budget estimates')
    if remaining+used>cap: raise RuntimeError(f'Estimated budget too low for this run: current ${used:.2f}, run ${remaining:.2f}, cap ${cap:.2f}')
    if envbool('USE_PAID_VOICE',True) is False: raise RuntimeError('Thai TTS required')
    if os.getenv('GEMINI_API_KEY'): reserve(state,0.01,'Gemini script estimate')
    narration,script_source=gemini_script(title,desc,punchline,genre,affiliate)
    (OUT/'narration.txt').write_text(narration,encoding='utf-8')
    frames=[]
    shots=[
        ('เรื่องเริ่มขึ้น',f'Wide cinematic comedy establishing shot. {desc}. Make the situation instantly readable.'),
        ('ความวุ่นวาย',f'Closer medium shot of EXACT SAME main character and matching location, escalating funny confusion from {desc}. Comedic visual storytelling.'),
        ('จุดหักมุม',f'The EXACT SAME character and location in the hilarious punchline moment: {punchline}. Strong facial expression or comic physical action.')
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
    reserve(state,est_voice,'Thai AI voice')
    voice(key,narration,voice_path)
    result=OUT/'reel.mp4'; assemble(frames,voice_path,result)
    caption=affiliate_caption(title,affiliate) if affiliate else create_caption(title,desc,genre,punchline)
    (OUT/'caption.txt').write_text(caption,encoding='utf-8')
    meta={'date':TODAY,'title':title,'genre':genre,'caption':caption,'script_source':script_source,'voice_source':voice_source,'images':images_n,'brand':'Vexa Viral','language':'th-TH','affiliate_id':affiliate['id'] if affiliate else None,'affiliate_ready':bool(affiliate),'estimated_run_usd':round(remaining,4),
          'estimated_month_usd':state['spent_estimate_by_month'].get(MONTH),'NOTE':'Illustrated video with Ken Burns motion, NOT native AI video. Estimates are not billed amounts; confirm provider limits.'}
    (OUT/'metadata.json').write_text(json.dumps(meta,indent=2))
    state['generated'][TODAY]={'title':title,'affiliate_id':affiliate['id'] if affiliate else None}; save_state(state)
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
