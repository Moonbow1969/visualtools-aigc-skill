import base64,io,json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image,ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import visualtools as v
import mask_edit as m
class Tools(unittest.TestCase):
 def test_invalid_image(self):
  with self.assertRaises(Exception):v.image_bytes('not base64')
 def test_processing_failures(self):
  for x in [{'files':[]},{'files':[{}],'warnings':['fallback']},{'files':[{'warnings':['failure']}]}]:
   with self.assertRaises(ValueError):v.save_images(x,'unused','files')
 def test_capability(self):
  a=SimpleNamespace(n=2,image=['a','b'],steps=4,loras=None)
  with self.assertRaises(ValueError):v.validate({'max_outputs':1},a)
  a.n=1
  with self.assertRaises(ValueError):v.validate({'max_outputs':2,'max_reference_images':1},a)
 def test_failed_job(self):
  c=SimpleNamespace(json=lambda *a,**k:{'status':'failed','error':'bad'})
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(RuntimeError):v.fetch_video(c,'video_123',Path(d)/'x.mp4')
   with self.assertRaises(TimeoutError):v.fetch_video(c,'video_123',Path(d)/'x.mp4',deadline=0)
 def test_bad_id(self):
  with self.assertRaises(ValueError):v.check_id('../other')
 def test_mask_exact(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);src=Image.new('RGBA',(601,301),(10,20,30,90));src.save(p/'source.png');mask=Image.new('L',src.size);mask.paste(255,(0,50,75,250));mask.save(p/'mask.png')
   meta=m.prepare(p/'source.png',p/'mask.png',p/'prep');Image.new('RGB',meta['canvas'],'red').save(p/'edited.png')
   m.compose(p/'prep/manifest.json',p/'edited.png',p/'out.png');out=Image.open(p/'out.png')
   self.assertEqual(out.getpixel((200,200)),src.getpixel((200,200)));self.assertEqual(out.getpixel((20,80)),(255,0,0,90))
   diff=ImageChops.difference(src.convert('RGB'),out.convert('RGB'));diff.paste(0,(0,50,75,250));self.assertIsNone(diff.getbbox())
   self.assertEqual(src.getchannel('A').tobytes(),out.getchannel('A').tobytes())
 def test_empty_and_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);Image.new('RGB',(600,400)).save(p/'s.png');Image.new('L',(600,400)).save(p/'m.png')
   with self.assertRaises(ValueError):m.prepare(p/'s.png',p/'m.png',p/'o')
   Image.new('L',(500,500),255).save(p/'m.png')
   with self.assertRaises(ValueError):m.prepare(p/'s.png',p/'m.png',p/'o')
 def test_resize_and_reject(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);Image.new('RGB',(3000,900),'blue').save(p/'s.png');Image.new('L',(3000,900),255).save(p/'m.png');meta=m.prepare(p/'s.png',p/'m.png',p/'o');self.assertEqual(meta['canvas'][0],2048)
   Image.new('RGB',(512,512)).save(p/'e.png')
   with self.assertRaises(ValueError):m.compose(p/'o/manifest.json',p/'e.png',p/'x.png')
 def test_exif(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);im=Image.new('RGB',(600,400));ex=Image.Exif();ex[274]=6;im.save(p/'s.jpg',exif=ex);Image.new('L',(400,600),255).save(p/'m.png');m.prepare(p/'s.jpg',p/'m.png',p/'o');self.assertEqual(m.opened(p/'o/source.png').size,(400,600))
if __name__=='__main__':unittest.main()
