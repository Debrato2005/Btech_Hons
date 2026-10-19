"""Independent default-Python checks. No hardware, cv2, model, venv, or network imports."""
import sys,math,json,re,pathlib,datetime,hashlib,ast
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]; checks=[]
def ck(name,condition,detail):
 assert condition,name
 checks.append({'name':name,'passed':True,'detail':detail})
ck('Span and signed error',80-(-20)==100 and 26-25==1,'100°C span and+1°C error')
ck('Sensitivity',math.isclose((4-1)/(40-10),.1),'0.1V/N')
ck('ADC bins',2**10==1024 and math.isclose(5/1024,.0048828125),'Uniform1024bins distinct from endpoint scale1023')
ck('Potentiometer supplied calibration',math.isclose(541/1023*270,142.78592375366568),'142.7859237537degrees')
ck('Sampling delay',1000/200==5,'Ignoring overhead5Hz')
ck('Absolute binary sectors',2**4==16 and 360/16==22.5,'Singleturn16sectors22.5degree')
ck('Binary transition',sum(a!=b for a,b in zip('0111','1000'))==4,'Four bits flip;not Gray')
ck('Encoder truncation',int(-900/600)==-1 and int(599/600)==0,'C++intcast model truncatestowardzero')
c=10
for high in[True,False,True]:c+=1 if high else -1
ck('Encoder signed edges',c==11,'A-rising sampled B high/low/high')
ck('Voltage divider',5*10000/(40000+10000)==1 and 5*10000/(10000+10000)==2.5,'LDRabovefixedresistortoground')
ck('Pullup branch',[('detected'if x==0 else'not')for x in[0,1]]==['detected','not'],'Explicitrepairedtilt/reed branches')
s=[1,0,1,0,1,0];ck('Debounced falling edges',sum(a==1 and b==0 for a,b in zip(s,s[1:]))==3,'Three passages,notlevelpollcount')
ck('Ultrasound roundtrip',math.isclose(.010*343/2,1.715),'Source343m/s,1.715m')
cm=int(1001*.034/2);ck('Ultrasound code conversion',cm==17,'Truncates17.017to17cm;printedcodeuses340m/s')
ck('Literal ultrasound text','Distance: '+'Distance: '+str(cm)=='Distance: Distance: 17','No newline is appended by source print calls')
ck('Pulse timeout modeled',int(0*.034/2)==0,'Zero textcannotdistinguishnoecho frommeasuredzero;not hardwareexecuted')
ck('Signed high-first decode',int.from_bytes(bytes([255,0]),'big',signed=True)==-256,'0xFF00−65536')
ck('Tilt sign',math.isclose(math.degrees(math.atan2(1,math.sqrt(3))),30),'−ax denominatorgravitymagnitude')
ck('Offset',37-12==25,'Sameframe subtraction')
ck('Light roundtrip',math.isclose(20e-9*3e8/2,3),'3m')
ck('Planar angular spacing',7200/10==720 and 360/720==.5,'720points,.5degrees')
ck('Range conversion',147/10.0==14.7,'mm→cm float')
ck('Range status predicate',[s for s in range(5)if s!=4]==[0,1,2,3],'PrintedconditionacceptsSigmaFail1')
ck('Polar convention',np.allclose([2*math.cos(math.pi/2),2*math.sin(math.pi/2)],[0,2]),'Explicit+x0,+y90')
ck('Resolution mismatch',.01*2000==20 and 20/.5==40,'20mmvs.5mmfactor40')
ck('RPM rounding',round(416/60,1)==6.9,'6.9333Hz')
prev=0;fps=[]
for t in[100.,100.25]:fps.append(int(1/(t-prev)if prev else 0));prev=t
ck('FPS two iterations',fps==[0,4],'Actualsourceconditional/int arithmetic')
ck('Throughput playback',100/50==2 and 100/20==5,'2fps acquisition,5splayback')
ck('Subunit FPS truncation',int(1/1.25)==0,'Successfulframecanlabel0')
ck('Stereo extension',400*.1/20==2,'SuppliedfB/dnotprintedsourceequation')
ck('Moment cross product',np.allclose(np.cross([.2,0,0],[0,10,0]),[0,0,2]),'Right-handedr×F')
ck('Capacitance ratio',(1/(.5))/(1/1)==2,'FixedepsilonA')
ck('Latency',50-10-5-5==30,'30ms')
ck('Endurance',100/(15+5)==5,'5hours')
a=[(.05,4,1,10,30,5),(.05,4,1,15,30,4),(.2,6,1,5,20,3),(.05,4,1,10,30,8)]
valid=[i+1 for i,(lo,hi,e,t,inf,p)in enumerate(a)if lo<=.1 and hi>=3 and e<=2 and t+inf+10<=50 and 120/(18+p)>=5]
ck('Multiconstraint selection',valid==[1],'Only1passesrange,error,latency,endurance')
yaml=(ROOT/'sources/supplemental/L52-ultralytics-open-images-v7.yaml').read_text();idx=[int(x)for x in re.findall(r'^  (\d+): ',yaml,re.M)]
ck('Saved YAML metadata',idx==list(range(601)),'601names;readtextonly,downloadcodeunexecuted')
# Explicit source-reconstructed Python loop with stubs. This is not cv2/model execution.
loop='''while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (640,480))
    results = model(frame, device=device, conf=0.25)
    annotated = results[0].plot()
    current_time = time.time()
    fps_display = 1/(current_time-prev_time) if prev_time else 0
    prev_time=current_time
    cv2.putText(annotated, f"FPS: {int(fps_display)}", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)
    out.write(annotated)
    cv2.imshow("Max Objects Detection (600 classes)",annotated)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break
cap.release()
out.release()
cv2.destroyAllWindows()
'''
class Cap:
 def __init__(self,frames,events):self.frames=iter(frames);self.e=events
 def read(self):self.e.append('read');return next(self.frames,(False,None))
 def release(self):self.e.append('cap.release')
class Cv:
 FONT_HERSHEY_SIMPLEX=0
 def __init__(self,e,key):self.e=e;self.key=key
 def resize(self,f,size):self.e.append(('resize',size));return np.zeros((size[1],size[0],3),dtype=np.uint8)
 def putText(self,*a):self.e.append(('text',a[1]))
 def imshow(self,*a):self.e.append('show')
 def waitKey(self,*a):return self.key
 def destroyAllWindows(self):self.e.append('destroy')
class Out:
 def __init__(self,e,size):self.e=e;self.size=size;self.matches=[]
 def write(self,f):self.matches.append((f.shape[1],f.shape[0])==self.size);self.e.append('write')
 def release(self):self.e.append('out.release')
def run(frames,key,size=(640,480)):
 e=[];cap=Cap(frames,e);cv=Cv(e,key);out=Out(e,size)
 def model(f,**kw):
  e.append(('infer',kw))
  class Result:
   def plot(self):e.append('plot');return f
  return[Result()]
 class Time:
  def __init__(self):self.t=99.75
  def time(self):self.t+=.25;return self.t
 ns=dict(cap=cap,cv2=cv,out=out,model=model,device='cpu',time=Time(),prev_time=0)
 exec(compile(loop,'source_reconstructed_loop','exec'),ns)
 return e,out.matches
im=np.zeros((720,1280,3),dtype=np.uint8)
e,m=run([(True,im),(True,im)],-1)
ck('Stub loop order and cleanup',e[:6]==['read',('resize',(640,480)),('infer',{'device':'cpu','conf':.25}),'plot',('text','FPS: 0'),'write']and e[-3:]==['cap.release','out.release','destroy'],'Source code executed with explicit mocks only')
ck('Stub second FPS',('text','FPS: 4')in e,'Second iteration interval.25')
e,m=run([(True,im),(True,im)],ord('q'));ck('Stub q termination',e.count('read')==1 and m==[True],'Oneframebeforeqthenpostloopcleanup')
e,m=run([(False,None)],-1);ck('Stub failed capture',e==['read','cap.release','out.release','destroy'],'No infer/write uponretfalse')
e,m=run([(True,im)],ord('q'),(1280,720));ck('Stub dimension invariant',m==[False],'Comparedshapeonly;notcodecbackendbehavior')
rng=np.random.default_rng(520019)
for _ in range(1000):
 angle=rng.uniform(-89,89);r=math.radians(angle);a=(-math.sin(r),0,math.cos(r));scale=rng.uniform(.01,10)
 assert math.isclose(math.degrees(math.atan2(-a[0]*scale,math.hypot(a[1]*scale,a[2]*scale))),angle,abs_tol=1e-9)
 signed=int(rng.integers(-32768,32768));assert int.from_bytes(signed.to_bytes(2,'big',signed=True),'big',signed=True)==signed
 depth=rng.uniform(.1,50);f=rng.uniform(100,2000);b=rng.uniform(.02,.4);disp=f*b/depth;assert math.isclose(f*b/disp,depth)
 distance=rng.uniform(.01,50);speed=rng.uniform(300,350);t=2*distance/speed;assert math.isclose(t*speed/2,distance)
ck('Four varied families',True,'1000each:tiltscale,signedbytes,stereo,roundtrip=4000cases')
result={'reviewerId':'independent-reviewer-robotics-batches-v2','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.executable,'numpyVersion':np.__version__,'source':'Own actual-slide derivations; no author checking script or keyed objects read','groups':len(checks),'variedCases':4000,'checks':checks,'boundaries':['No cv2,Ultralytics,torch,Transformers,Arduino hardware,model/checkpoint,pretrained inference,codec or camera execution.','Only saved YAML text,default NumPy and explicit source-derived stubs. Stub writes are shape checks,not actual VideoWriter acceptance.','No incident virtual environment,dependencies,audio,install,NLTK corpus or denied L49 notebook route.','Historical author vision checks are not independent validation.']}
out=ROOT/'audits/W11-L52-independent-computations.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'groups':len(checks),'variedCases':4000,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
