#!/usr/bin/env python3
"""Visual Tools client: discover, generate/edit, segment, upscale and video lifecycle.
Run --help. POSTs are never automatically retried. Outputs must not already exist.
"""
import argparse,base64,io,json,mimetypes,os,re,time
from contextlib import ExitStack
from pathlib import Path
import requests
from PIL import Image

class Client:
    def __init__(self,base,timeout=300):
        self.base=base.rstrip('/');self.timeout=timeout;self.session=requests.Session()
        self.session.headers['User-Agent']='VisualTools-AIGC-Skill/1.0'
        if os.environ.get('VISUALTOOLS_API_KEY'):self.session.headers['Authorization']='Bearer '+os.environ['VISUALTOOLS_API_KEY']
    def request(self,method,path,**kw):
        r=self.session.request(method,self.base+path,timeout=self.timeout,**kw)
        r.raise_for_status();return r
    def json(self,method,path,**kw):
        try:return self.request(method,path,**kw).json()
        except requests.exceptions.JSONDecodeError as e:raise ValueError('Service returned non-JSON; inspect HTTP status/entrypoint') from e
    def model(self,key):
        rows=self.json('GET','/v1/models')['data'];m=next((x for x in rows if x.get('key')==key),None)
        if not m:raise ValueError('Model key not advertised: '+key)
        if m.get('healthy_worker_count')==0:raise ValueError('Model has no healthy worker')
        return m

def validate(m,args):
    if args.n>m.get('max_outputs',1):raise ValueError('n exceeds model capability')
    if len(getattr(args,'image',[]) or [])>m.get('max_reference_images',0):raise ValueError('Too many reference images')
    for k in ['steps','loras']:
        if getattr(args,k,None) is not None and k not in m.get('supported_parameters',[]):raise ValueError('Unsupported parameter: '+k)
    if args.steps is not None:
        spec=m.get('parameter_schema',{}).get('steps',{})
        if not spec.get('minimum',1)<=args.steps<=spec.get('maximum',50):raise ValueError('steps outside model range')
    if args.loras is not None:
        rows=json.loads(args.loras);spec=m.get('parameter_schema',{}).get('loras',{})
        if not isinstance(rows,list) or len(rows)>spec.get('max_items',0):raise ValueError('Invalid LoRA count')
        for item in rows:
            if item['name'] not in m.get('parameter_options',{}).get('lora_name',[]):raise ValueError('Unregistered LoRA')
            for k in ['strength_model','strength_clip']:
                v=item.get(k,1)
                if not spec.get('strength_minimum',-2)<=v<=spec.get('strength_maximum',2):raise ValueError('LoRA strength outside API range')

def image_bytes(raw):
    b=base64.b64decode(raw.split(',',1)[-1],validate=True)
    with Image.open(io.BytesIO(b)) as im:im.verify()
    return b

def save_images(x,out,kind,expected=None):
    rows=x.get(kind,[])
    if x.get('warnings') or any(r.get('warnings') for r in rows):raise ValueError('Processing warnings; inspect response before accepting result')
    if not rows or (expected is not None and len(rows)!=expected):raise ValueError('Unexpected result count')
    # Validate all candidates before creating the output directory.
    blobs=[image_bytes(r.get('b64_json',r.get('base64',''))) for r in rows]
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    for i,b in enumerate(blobs):
        with Image.open(io.BytesIO(b)) as im:im.save(out/f'candidate-{i:03d}.png')
    meta={k:v for k,v in x.items() if k not in {'data','files'}}
    if kind=='files':meta['files']=[{k:v for k,v in r.items() if k not in {'base64','b64_json'}} for r in rows]
    (out/'response.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))

def upload(st,path):
    p=Path(path);return (p.name,st.enter_context(p.open('rb')),mimetypes.guess_type(p.name)[0] or 'application/octet-stream')

def check_id(value,advanced=False):
    if advanced:
        from uuid import UUID
        return str(UUID(value))
    if not re.fullmatch(r'video_[A-Za-z0-9_-]+',value):raise ValueError('Expected legacy video_ ID')
    return value

def fetch_video(c,job_id,out,deadline=600,advanced=False):
    path=('/v1/h3/videos/' if advanced else '/v1/videos/')+check_id(job_id,advanced)
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    end=time.monotonic()+deadline
    while time.monotonic()<end:
        x=c.json('GET',path)
        if x['status']=='failed':raise RuntimeError('Video failed: '+str(x.get('error','unknown')))
        if x['status']=='completed':
            r=c.request('GET',path+'/content',stream=True);out.parent.mkdir(parents=True,exist_ok=True)
            part=out.with_name(out.name+'.part')
            try:
                with r,part.open('xb') as f:
                    for chunk in r.iter_content(1024*1024):f.write(chunk)
                if part.stat().st_size<1024:raise ValueError('Empty video response')
                part.rename(out)
            except Exception:
                part.unlink(missing_ok=True);raise
            return x
        time.sleep(min(5,max(0,end-time.monotonic())))
    raise TimeoutError('Polling deadline reached; job is not cancelled; retain receipt')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-url',default=os.getenv('VISUALTOOLS_BASE_URL','https://visualtools.frederickpi.com'));p.add_argument('--timeout',type=float,default=300)
    sub=p.add_subparsers(dest='cmd',required=True);sub.add_parser('discover')
    for name in ['generate','edit']:
        q=sub.add_parser(name);q.add_argument('--model',required=True);q.add_argument('--prompt',required=True);q.add_argument('--size',default='1024x1024');q.add_argument('--steps',type=int);q.add_argument('--seed',type=int);q.add_argument('--n',type=int,choices=[1,2],default=1);q.add_argument('--loras');q.add_argument('--out',required=True)
        if name=='edit':q.add_argument('--image',action='append',required=True)
    q=sub.add_parser('segment');q.add_argument('--image',required=True);q.add_argument('--text');q.add_argument('--positive-coords');q.add_argument('--negative-coords');q.add_argument('--boxes');q.add_argument('--out',required=True)
    q=sub.add_parser('upscale');q.add_argument('--image',required=True);q.add_argument('--out',required=True)
    q=sub.add_parser('video-submit');q.add_argument('--model',default='minimax_h3_titanium');q.add_argument('--prompt',required=True);q.add_argument('--image');q.add_argument('--size',default='544x960');q.add_argument('--seconds',default='5');q.add_argument('--upscale',default='none');q.add_argument('--out',required=True)
    q=sub.add_parser('video-fetch');q.add_argument('--id',required=True);q.add_argument('--out',required=True);q.add_argument('--deadline',type=float,default=600);q.add_argument('--advanced',action='store_true')
    a=p.parse_args();c=Client(a.base_url,a.timeout)
    if a.cmd=='discover':
        rows=c.json('GET','/v1/models')['data'];print(json.dumps([{k:m.get(k) for k in ['key','id','generation_type','healthy_worker_count','max_reference_images','max_outputs','supported_parameters']} for m in rows],indent=2));return
    if Path(a.out).exists():raise FileExistsError(a.out)
    if a.cmd in {'generate','edit'}:
        validate(c.model(a.model),a);d={k:getattr(a,k) for k in ['model','prompt','size','steps','seed','n'] if getattr(a,k) is not None};d['response_format']='b64_json'
        if a.loras is not None:d['loras']=json.loads(a.loras)
        if a.cmd=='generate':x=c.json('POST','/v1/images/generations',json=d)
        else:
            if 'loras' in d:d['loras']=json.dumps(d['loras'])
            with ExitStack() as st:x=c.json('POST','/v1/images/edits',data=d,files=[('image',upload(st,f)) for f in a.image])
        save_images(x,a.out,'data',a.n)
        (Path(a.out)/'request.json').write_text(json.dumps(d,indent=2))
    elif a.cmd=='segment':
        d={k:getattr(a,k) for k in ['text','positive_coords','negative_coords','boxes'] if getattr(a,k)}
        if not d:raise ValueError('Supply text, points or boxes')
        d.update(individual='true',threshold='0.5')
        with ExitStack() as st:x=c.json('POST','/v1/segment',data=d,files={'image':upload(st,a.image)})
        if not x.get('masks'):raise ValueError('No segment detected; select a point/box')
        save_images({'data':[{'b64_json':v} for v in x['masks']]},a.out,'data')
        (Path(a.out)/'segments.json').write_text(json.dumps({k:v for k,v in x.items() if k!='masks'},indent=2))
    elif a.cmd=='upscale':
        with ExitStack() as st:x=c.json('POST','/api/process',data={'task_type':'super_resolution','model_key':'seedvr2_3b_serv11','response_format':'json'},files={'files':upload(st,a.image)})
        save_images(x,a.out,'files',1)
    elif a.cmd=='video-submit':
        c.model(a.model)
        Path(a.out).parent.mkdir(parents=True,exist_ok=True)
        with ExitStack() as st:x=c.json('POST','/v1/videos',data={k:getattr(a,k) for k in ['model','prompt','size','seconds','upscale']},files={'input_reference':upload(st,a.image)} if a.image else None)
        with Path(a.out).open('x') as f:json.dump(x,f,indent=2)
        print(x['id'])
    else:fetch_video(c,a.id,a.out,a.deadline,a.advanced)
    print('Saved',a.out)
if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,OSError,requests.RequestException) as e:raise SystemExit(str(e))
