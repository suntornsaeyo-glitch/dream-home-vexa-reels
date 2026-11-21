import json, math, os
from pathlib import Path
DEFAULTS={'monthly_cap_usd':5.0,'daily_cap_usd':0.5,'images_per_reel':3,'image_estimate_usd':0.12,'voice_estimate_usd':0.05}
def validate_settings(data):
    result={}
    for key,default in DEFAULTS.items():
        val=float(data.get(key,default))
        if not math.isfinite(val) or val<0: raise ValueError('Invalid setting: '+key)
        if key=='images_per_reel':
            if val not in (1,2,3): raise ValueError('Images must be 1 to 3')
            val=int(val)
        if key in ('image_estimate_usd','voice_estimate_usd') and val<=0: raise ValueError('Estimates must be positive')
        result[key]=val
    return result
def settings():
    p=Path(__file__).resolve().parents[1]/'data/settings.json'
    data=validate_settings(json.loads(p.read_text()) if p.exists() else {})
    for key,env in [('monthly_cap_usd','MONTHLY_SPEND_CAP_USD'),('daily_cap_usd','DAILY_SPEND_CAP_USD')]:
        if os.getenv(env): data[key]=min(data[key],float(os.environ[env]))
    for key,env in [('image_estimate_usd','IMAGE_ESTIMATE_USD'),('voice_estimate_usd','VOICE_ESTIMATE_USD')]:
        if os.getenv(env): data[key]=max(data[key],float(os.environ[env]))
    if os.getenv('IMAGES_PER_REEL'): data['images_per_reel']=int(os.environ['IMAGES_PER_REEL'])
    return validate_settings(data)
