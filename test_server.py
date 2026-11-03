import unittest,subprocess,os,tempfile,time,json,urllib.request,urllib.error,http.cookiejar,socket
from pathlib import Path
class TestServer(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();s=socket.socket();s.bind(('127.0.0.1',0));port=s.getsockname()[1];s.close();cls.url=f'http://127.0.0.1:{port}'
  cls.proc=subprocess.Popen(['python','server.py'],cwd=Path(__file__).parent,env={**os.environ,'PORT':str(port),'DATA_DIR':cls.tmp.name,'STUDIO_PASSWORD':'test-password-only-12345','LOCAL_HTTP':'1'})
  cls.client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
  for i in range(50):
   try:urllib.request.urlopen(cls.url);break
   except:time.sleep(.1)
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.wait();cls.tmp.cleanup()
 def request(self,path,data=None,auth=True,header=True):
  h={'Content-Type':'application/json'}
  if header:h['X-Studio-Request']='1'
  r=urllib.request.Request(self.url+path,data=json.dumps(data).encode() if data is not None else None,headers=h)
  try:
   with (self.client if auth else urllib.request).open(r) if auth else urllib.request.urlopen(r) as res:return res.status,json.load(res)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_full_flow(self):
  self.assertEqual(self.request('/api/state',auth=False)[0],401)
  self.assertEqual(self.request('/api/login',{'password':'wrong'})[0],401)
  self.assertEqual(self.request('/api/login',{'password':'test-password-only-12345'},header=False)[0],403)
  self.assertEqual(self.request('/api/login',{'password':'test-password-only-12345'})[0],200)
  self.assertEqual(self.request('/api/state')[1]['revision'],0)
  record=dict(id='test',client='Example',project='Poster',stage='Design',service='Event',due='',next='Review',value=10000,paid=5000,hours=2,revisions=1,checks=[])
  self.assertEqual(self.request('/api/state',{'revision':0,'records':[record]})[1]['revision'],1)
  self.assertEqual(self.request('/api/state')[1]['records'][0]['paid'],5000)
  self.assertEqual(self.request('/api/state',{'revision':0,'records':[]})[0],409)
  record['paid']=20000
  self.assertEqual(self.request('/api/state',{'revision':1,'records':[record]})[0],400)
  self.assertEqual(self.request('/api/logout',{})[0],200)
  self.assertEqual(self.request('/api/state')[0],401)
if __name__=='__main__':unittest.main()
