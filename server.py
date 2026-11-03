import os,json,sqlite3,secrets,time,hmac,hashlib,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
ROOT=Path(__file__).parent
DATA=Path(os.getenv('DATA_DIR',str(ROOT/'data')));DATA.mkdir(parents=True,exist_ok=True)
PASSWORD=os.getenv('STUDIO_PASSWORD','')
if len(PASSWORD)<16: raise SystemExit('Set STUDIO_PASSWORD to a unique password of at least 16 characters.')
SALT=secrets.token_bytes(16)
HASH=hashlib.scrypt(PASSWORD.encode(),salt=SALT,n=16384,r=8,p=1)
PASSWORD=None
sessions={}; attempts=[]; lock=threading.Lock()
def db():
 c=sqlite3.connect(DATA/'studio.db');c.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, revision INTEGER, body TEXT)');c.execute("INSERT OR IGNORE INTO state VALUES (1,0,'[]')");c.commit();return c
with db(): pass
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT/'public'),**kw)
 def log_message(self,*args):pass
 def reply(self,status,data,cookie=None):
  body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.send_header('X-Content-Type-Options','nosniff')
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(body)
 def session(self):
  try:
   c=SimpleCookie(self.headers.get('Cookie','')); token=c['studio'].value
   return token if sessions.get(token,0)>time.time() else None
  except:return None
 def do_GET(self):
  if self.path=='/api/state':
   if not self.session():return self.reply(401,{'error':'Sign in required'})
   with db() as c:rev,body=c.execute('SELECT revision,body FROM state WHERE id=1').fetchone()
   return self.reply(200,{'revision':rev,'records':json.loads(body)})
  if self.path.startswith('/api/'):return self.reply(404,{'error':'Not found'})
  if self.path.split('?')[0] not in ['/','/index.html','/manifest.webmanifest','/icon-192.png','/icon-512.png']:return self.reply(404,{'error':'Not found'})
  super().do_GET()
 def do_POST(self):
  # Custom header blocks simple cross-origin requests; no CORS permissions granted.
  if self.headers.get('X-Studio-Request')!='1':return self.reply(403,{'error':'Invalid request'})
  try:
   size=int(self.headers.get('Content-Length',0))
   if size<1 or size>2000000:return self.reply(413,{'error':'Request too large'})
   body=json.loads(self.rfile.read(size))
  except:return self.reply(400,{'error':'Invalid JSON'})
  if self.path=='/api/login':
   with lock:
    now=time.time();attempts[:]=[t for t in attempts if now-t<600]
    if len(attempts)>=20:return self.reply(429,{'error':'Too many attempts. Try in 10 minutes.'})
    attempts.append(now)
   password=body.get('password','')
   if not isinstance(password,str) or len(password)>1024:return self.reply(400,{'error':'Invalid password'})
   if not hmac.compare_digest(HASH,hashlib.scrypt(password.encode(),salt=SALT,n=16384,r=8,p=1)):return self.reply(401,{'error':'Incorrect password'})
   token=secrets.token_urlsafe(32);sessions[token]=time.time()+86400
   secure='' if os.getenv('LOCAL_HTTP')=='1' else '; Secure'
   return self.reply(200,{'ok':True},'studio='+token+'; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400'+secure)
  token=self.session()
  if not token:return self.reply(401,{'error':'Sign in required'})
  if self.path=='/api/logout':
   sessions.pop(token,None);return self.reply(200,{'ok':True},'studio=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
  if self.path!='/api/state':return self.reply(404,{'error':'Not found'})
  records=body.get('records')
  if not isinstance(records,list) or len(records)>5000:return self.reply(400,{'error':'Invalid records'})
  ids=set()
  for r in records:
   if not isinstance(r,dict) or not isinstance(r.get('id'),str) or r['id'] in ids:return self.reply(400,{'error':'Invalid record ID'})
   ids.add(r['id'])
   if any(not isinstance(r.get(k),str) for k in ['client','project','stage','service','due','next']):return self.reply(400,{'error':'Invalid record fields'})
   if any(type(r.get(k)) not in [int,float] or r[k]<0 or r[k]>1e12 for k in ['value','paid','hours','revisions']):return self.reply(400,{'error':'Invalid amounts'})
   if r['paid']>r['value'] or not isinstance(r.get('checks'),list):return self.reply(400,{'error':'Invalid payment or checks'})
  with db() as c:
   cur=c.execute('UPDATE state SET revision=revision+1,body=? WHERE id=1 AND revision=?',(json.dumps(records,allow_nan=False),body.get('revision')))
   if cur.rowcount!=1:return self.reply(409,{'error':'Another device has changed this workspace. Export your local backup, then reload.'})
   rev=c.execute('SELECT revision FROM state WHERE id=1').fetchone()[0]
  self.reply(200,{'revision':rev})
ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','8080'))),Handler).serve_forever()
