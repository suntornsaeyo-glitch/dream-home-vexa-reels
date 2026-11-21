import base64, json, os
import requests
class Repo:
    name='suntornsaeyo-glitch/dream-home-vexa-reels'
    def __init__(self):
        self.token=os.getenv('GITHUB_TOKEN','') or os.getenv('GH_TOKEN','')
        self.api='https://api.github.com/repos/'+self.name
        self.session=requests.Session()
        self.session.headers.update({'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
        if self.token:self.session.headers['Authorization']='Bearer '+self.token
    def request(self,method,path,**kw):
        r=self.session.request(method,self.api+path,timeout=25,**kw)
        if not r.ok: raise RuntimeError(f'GitHub HTTP {r.status_code}: ตรวจสิทธิ์และลองโหลดข้อมูลใหม่')
        return r
    def info(self):return self.request('GET','').json()
    def read(self,path):
        data=self.request('GET','/contents/'+path).json()
        return json.loads(base64.b64decode(data['content']).decode('utf-8')),data['sha']
    def write(self,path,value,sha):
        if not self.token:raise RuntimeError('ต้องเปิด Admin ใน Codespaces ที่มีสิทธิ์เขียน')
        payload={'message':'Vexa Admin: update '+path,'sha':sha,'content':base64.b64encode((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()).decode()}
        return self.request('PUT','/contents/'+path,json=payload).json()
    def runs(self):
        return self.request('GET','/actions/workflows/daily.yml/runs',params={'per_page':12}).json().get('workflow_runs',[])
    def artifacts(self,runid):
        return self.request('GET',f'/actions/runs/{int(runid)}/artifacts').json().get('artifacts',[])
    def dispatch(self,dry=True,again=False):
        if not self.token:raise RuntimeError('ต้องมีสิทธิ์ Actions write')
        branch=self.info()['default_branch']
        self.request('POST','/actions/workflows/daily.yml/dispatches',json={'ref':branch,'inputs':{'dry_run':str(dry).lower(),'allow_regenerate':str(again).lower()}})
