#!/usr/bin/env python3
"""Offline SAM selection -> crop -> exact protected-pixel pasteback. Run --help."""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageOps

def opened(path):
    with Image.open(path) as im:return ImageOps.exif_transpose(im).convert('RGBA' if 'A' in im.getbands() else 'RGB')
def prepare(source,mask,out,padding=32,model_grid=32):
    if padding<0 or model_grid!=32:raise ValueError('padding>=0 and model-grid=32 required')
    src=opened(source)
    with Image.open(mask) as m:m=ImageOps.exif_transpose(m).convert('L').point(lambda v:255 if v>127 else 0)
    if m.size!=src.size:raise ValueError('Source and mask dimensions differ')
    box=m.getbbox()
    if box is None:raise ValueError('Mask is empty')
    x0,y0,x1,y1=box;box=(max(0,x0-padding),max(0,y0-padding),min(src.width,x1+padding),min(src.height,y1+padding))
    crop=src.crop(box);scale=min(1,2048/max(crop.size));rw=max(1,round(crop.width*scale));rh=max(1,round(crop.height*scale))
    cw=max(512,math.ceil(rw/32)*32);ch=max(512,math.ceil(rh/32)*32);left=(cw-rw)//2;top=(ch-rh)//2
    canvas=Image.new('RGB',(cw,ch),(128,128,128));canvas.paste(crop.convert('RGB').resize((rw,rh),Image.Resampling.LANCZOS),(left,top))
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    src.save(out/'source.png');m.save(out/'mask.png');canvas.save(out/'crop.png')
    meta={'version':1,'source':'source.png','mask':'mask.png','box':list(box),'resized':[rw,rh],'canvas':[cw,ch],'offset':[left,top],'source_sha256':hashlib.sha256((out/'source.png').read_bytes()).hexdigest(),'mask_sha256':hashlib.sha256((out/'mask.png').read_bytes()).hexdigest()}
    (out/'manifest.json').write_text(json.dumps(meta,indent=2));return meta

def compose(manifest,edited,out):
    manifest=Path(manifest);meta=json.loads(manifest.read_text());root=manifest.parent;dest=Path(out)
    if dest.exists():raise FileExistsError(dest)
    if meta['version']!=1:raise ValueError('Unknown manifest version')
    # Use local, fixed names; reject modified source/selection.
    for name in ['source','mask']:
        if meta[name]!=name+'.png':raise ValueError('Invalid local manifest path')
        if hashlib.sha256((root/meta[name]).read_bytes()).hexdigest()!=meta[name+'_sha256']:raise ValueError('Source or mask changed after prepare')
    src=opened(root/'source.png');mask=Image.open(root/'mask.png').convert('L');edit=opened(edited)
    if list(edit.size)!=meta['canvas']:raise ValueError('Edited image must match prepared canvas exactly; do not stretch a reframed output')
    x,y=meta['offset'];rw,rh=meta['resized'];x0,y0,x1,y1=meta['box']
    patch=edit.crop((x,y,x+rw,y+rh)).convert('RGB').resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
    rgb=src.convert('RGB');rgb.paste(patch,(x0,y0),mask.crop((x0,y0,x1,y1)))
    if src.mode=='RGBA':rgb.putalpha(src.getchannel('A'))
    dest.parent.mkdir(parents=True,exist_ok=True);rgb.save(dest,format='PNG');return dest

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('prepare');q.add_argument('--source',required=True);q.add_argument('--mask',required=True);q.add_argument('--out',required=True);q.add_argument('--padding',type=int,default=32);q.add_argument('--model-grid',type=int,default=32)
    q=sub.add_parser('compose');q.add_argument('--manifest',required=True);q.add_argument('--edited',required=True);q.add_argument('--out',required=True)
    a=p.parse_args()
    if a.cmd=='prepare':print(json.dumps(prepare(a.source,a.mask,a.out,a.padding,a.model_grid)))
    else:print(compose(a.manifest,a.edited,a.out))
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError) as e:raise SystemExit(str(e))
