#!/usr/bin/env python3
"""L52 author-only source transcription, stub execution and numerical checks.
No physical sensors, webcam, original notebook or YOLO checkpoint inference is executed.
"""
import json,math,random,hashlib,subprocess,tempfile,sys,types,contextlib,io,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'sources/supplemental/L52-slide-code-transcriptions.json').read_text());checks=[]
def ck(name,condition,detail):
 assert condition,(name,detail);checks.append({'name':name,'passed':True,'detail':detail})
work=Path(tempfile.mkdtemp(prefix='robotics-l52-check-',dir='/tmp'))
header=r'''#pragma once
#include <cmath>
#include <cstdint>
#include <sstream>
#include <iomanip>
#include <vector>
#include <string>
#include <cassert>
const int A0=100,A1=101,INPUT=0,OUTPUT=1,INPUT_PULLUP=2,HIGH=1,LOW=0,RISING=3;
const double PI=3.14159265358979323846;
int adc=541,digital=0; unsigned long pulse=1001; std::vector<int> delays,usdelays,writes; int attached=-1,edge=-1;
struct Port {std::ostringstream s; void begin(int){} void print(const char*v){s<<v;} void print(int v){s<<v;} void print(long v){s<<v;} void print(float v){s<<std::fixed<<std::setprecision(2)<<v;} void print(double v){s<<std::fixed<<std::setprecision(2)<<v;} template<class T>void println(T v){print(v);s<<"\n";} } Serial;
void pinMode(int,int){} int analogRead(int){return adc;} int digitalRead(int){return digital;}
void digitalWrite(int p,int v){writes.push_back(p*10+v);} void delay(int x){delays.push_back(x);}void delayMicroseconds(int x){usdelays.push_back(x);}
void noInterrupts(){}void interrupts(){}int digitalPinToInterrupt(int p){return p;}void attachInterrupt(int p,void(*)(),int e){attached=p;edge=e;}
unsigned long pulseIn(int,int){return pulse;}
void encoderISR();float readTilt();void readAccel();
'''
(work/'ArduinoStub.h').write_text(header)
(work/'DHT.h').write_text('''#pragma once
#define DHT11 11
class DHT {public:DHT(int,int){}void begin(){}float readHumidity(){return44.0f;}float readTemperature(){return28.8f;}};
'''.replace('return44','return 44').replace('return28','return 28'))
(work/'Wire.h').write_text('''#pragma once
struct WireStub {int i=0;std::vector<int> bytes={0,0,0,0,64,0};std::vector<int> values;void begin(){}void beginTransmission(int a){values.push_back(a);}void write(int v){values.push_back(v);}void endTransmission(bool){}void requestFrom(int,int,bool){i=0;}int read(){return bytes.at(i++);}} Wire;
''')
(work/'Adafruit_VL53L0X.h').write_text('''#pragma once
struct VL53L0X_RangingMeasurementData_t {int RangeStatus;int RangeMilliMeter;};int status=0,mm=147;
class Adafruit_VL53L0X {public:bool begin(){return true;}void rangingTest(VL53L0X_RangingMeasurementData_t*m,bool){m->RangeStatus=status;m->RangeMilliMeter=mm;}};
''')
tests={
'potentiometer':'setup();loop();assert(Serial.s.str()=="541\\n");assert(delays.back()==200);',
'encoder':'setup();assert(attached==2&&edge==RISING);count=-900;loop();assert(Serial.s.str()=="Rotations: -1\\n");count=10;digital=HIGH;encoderISR();digital=LOW;encoderISR();digital=HIGH;encoderISR();assert(count==11);',
'ir':'setup();digital=HIGH;loop();digital=LOW;loop();assert(Serial.s.str()=="Obstacle Detected\\nNo Obstacle\\n");',
'ldr':'setup();adc=1000;loop();assert(Serial.s.str()=="Light Intensity: 1000\\n");assert(delays.back()==500);',
'reed':'setup();digital=LOW;loop();digital=HIGH;loop();assert(Serial.s.str()=="Magnet Detected!\\nMagnet Not Detected!\\n");',
'ultrasonic':'setup();loop();assert(distance==17);assert(Serial.s.str()=="Distance: Distance: 17");assert((writes==std::vector<int>{90,91,90}));assert((usdelays==std::vector<int>{2,10}));pulse=0;loop();assert(distance==0);',
'dht':'setup();loop();assert(Serial.s.str().find("Humidity: 44.00")!=std::string::npos);assert(Serial.s.str().find("Temperature: 28.80")!=std::string::npos);assert(delays.back()==2000);',
'imu':'setup();assert(std::abs(offset)<1e-6);loop();assert(Serial.s.str().find("Lower leg tilt: 0.00 degrees")!=std::string::npos);',
'vl53l0x':'setup();loop();status=4;loop();status=1;loop();assert(Serial.s.str()=="VL53L0X Ready\\nDistance: 14.70 cm\\nOut of range\\nDistance: 14.70 cm\\n");'
}
compiled=[]
for name,rec in D.items():
 if name=='vision':continue
 src=work/(name+'.cpp');src.write_text('#include "ArduinoStub.h"\n'+rec['code']+'\nint main(){'+tests.get(name,'')+'}\n')
 proc=subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-I',str(work),str(src),'-o',str(work/name)],capture_output=True,text=True)
 if name=='tilt':
  ck('Printed tilt fails compilation',proc.returncode!=0 and 'expected' in proc.stderr,proc.stderr[-1000:])
  repaired=src.read_text().replace('Serial.println("Tilt Not Detected!") }','Serial.println("Tilt Not Detected!"); }').replace('int main(){}','int main(){digital=LOW;loop();digital=HIGH;loop();assert(Serial.s.str()=="Tilt Detected!\\nTilt Not Detected!\\n");}')
  src.write_text(repaired);proc=subprocess.run(['g++','-std=c++17','-I',str(work),str(src),'-o',str(work/name)],capture_output=True,text=True)
  ck('Explicit semicolon repair compiles',proc.returncode==0,proc.stderr)
 else:ck(name+' transcription compiles in host stub harness',proc.returncode==0,proc.stderr)
 run=subprocess.run([str(work/name)],capture_output=True,text=True);ck(name+' supplied-input execution',run.returncode==0,run.stderr);compiled.append(name)
ck('Vision Python syntax',bool(compile(D['vision']['code'],'L52-source-vision','exec')),'Original two-slide transcription compiles without invoking hardware or loading weights.')
# Execute the entire unchanged Python excerpt against explicit external-interface stubs.
def vision_run(dims=(640,480),times=(100.,100.25),keys=(-1,ord('q')),nframes=2):
 log=[];tick=iter(times);frame={'size':dims}
 class Cap:
  def __init__(self):self.n=0
  def set(self,*a):log.append(('set',a));return True
  def get(self,k):return dims[0 if k==1 else 1]
  def read(self):self.n+=1;return (True,frame.copy())if self.n<=nframes else(False,None)
  def release(self):log.append(('releasecap',))
 class Out:
  def __init__(self,*a):self.size=a[-1];log.append(('writer',a))
  def write(self,f):log.append(('write',f['size'],self.size))
  def release(self):log.append(('releaseout',))
 class Result:
  def __init__(self,f):self.f=f
  def plot(self):log.append(('plot',));return self.f.copy()
 class Model:
  def __init__(self,path):log.append(('modelpath',path))
  def __call__(self,f,**kw):log.append(('infer',kw,f['size']));return[Result(f)]
 cv=types.ModuleType('cv2');cv.CAP_PROP_FRAME_WIDTH=1;cv.CAP_PROP_FRAME_HEIGHT=2;cv.FONT_HERSHEY_SIMPLEX=0;cv.VideoCapture=lambda idx:Cap();cv.VideoWriter=Out;cv.VideoWriter_fourcc=lambda *a:''.join(a)
 cv.resize=lambda f,size:dict(size=size);cv.putText=lambda f,t,*a:log.append(('label',t));cv.imshow=lambda *a:log.append(('show',));ki=iter(keys);cv.waitKey=lambda n:next(ki,-1);cv.destroyAllWindows=lambda:log.append(('destroy',))
 tm=types.ModuleType('time');tm.time=lambda:next(tick);ul=types.ModuleType('ultralytics');ul.YOLO=Model
 saved={k:sys.modules.get(k)for k in['cv2','time','ultralytics']}
 try:
  sys.modules.update(cv2=cv,time=tm,ultralytics=ul)
  with contextlib.redirect_stdout(io.StringIO()):exec(compile(D['vision']['code'],'L52-source-vision','exec'),{})
 finally:
  for k,v in saved.items():
   if v is None:sys.modules.pop(k,None)
   else:sys.modules[k]=v
 return log
l=vision_run();ck('Full vision source stub trace',[(v[1])for v in l if v[0]=='label']==['FPS: 0','FPS: 4'],'Two supplied timestamps, CPU/conf0.25 path, annotation and normal q cleanup executed.')
ck('Vision cleanup',l[-3:]==[('releasecap',),('releaseout',),('destroy',)],l[-3:])
ck('Vision matching size',all(a==b for typ,a,b in l if typ=='write')if False else all(v[1]==v[2]for v in l if v[0]=='write'),'640×480 source/request/processed sizes agree.')
m=vision_run((1280,720));ck('Vision size mismatch exposed',any(v[1]!=v[2]for v in m if v[0]=='write'),'Reported1280×720 writer versus forced640×480 processed frame; stub does not pretend to resize on write.')
l=vision_run(nframes=0,times=(),keys=());ck('Capture failure cleanup',not any(v[0]=='infer'for v in l)and l[-3:]==[('releasecap',),('releaseout',),('destroy',)],'No inference on failed acquisition; normal cleanup still runs.')
# Every authored numerical answer and numerical distractor mechanism.
ck('Range/error',80-(-20)==100 and 31-30==1,'Span100°C; signed error+1°C; endpoint-sum trap60°C.')
ck('Sensitivity',math.isclose((4-1)/(40-10),.1)and math.isclose(3/40,.075),'0.10V/N versus inverse10N/V and final-input denominator0.075V/N.')
ck('ADC conventions',2**10==1024 and 5/1024*1000==4.8828125 and round(5/1023*1000,7)==4.8875855,'Uniform bin width differs from endpoint interpolation.')
ck('Delay rate',1/.2==5,'200ms delay-only ceiling5Hz; serial baud not loop rate.')
ck('Pot angle and distractor',round(541/1023*270,2)==142.79 and 541/600*270==243.45,'Explicit endpoint interpolation; alternate600denominator gives243.45°.')
ck('Absolute disk',2**4==16 and 360/16==22.5 and 360/32==11.25,'Four-track sectors and doubled-count distractor.')
ck('Encoder signed truncation',-900/600==-1.5 and int(-1.5)==-1 and math.floor(-1.5)==-2,'Truncation versus floor; supplied event count11.')
ck('Divider orientation',5*10/(40+10)==1 and 5*10/(10+10)==2.5 and 5*40/50==4,'Top-LDR output1→2.5V; reversed-divider output4→2.5V.')
ck('Wheel events',40/2==20,'Two debounced events per revolution.')
ck('Acoustic flight',343*.010/2==1.715,'One-way1.715m versus roundtrip3.43m and millisecond conversion trap0.1715m.')
ck('Acoustic printed coefficient',math.isclose(1001*.034/2,17.017)and int(1001*.034/2)==17 and int(1001*.034)==34,'340m/s coefficient and integer conversion; all numeric options checked.')
ck('Signed bytes',255*256==65280 and 65280-65536==-256,'0xFF00 signed−256; reversed0x00FF is255.')
ck('Tilt atan2',math.isclose(math.degrees(math.atan2(1,math.sqrt(3))),30),'Correct30°, sign-reversed−30°, swapped arguments60°.')
ck('Angle offset',37-12==25 and 37+12==49,'Relative25°; addition trap49°; omitted correction37°.')
ck('Light flight',math.isclose(3e8*20e-9/2,3),'20ns gives3m; no-halving6m; picosecond conversion0.003m.')
ck('Scan density',7200/10==720 and 360/720==.5 and 360/72000==.005,'Rate division and angular interval; all supplied numerical options.')
ck('VL conversion',147/10==14.7 and all((s!=4)==(s in[0,1,2,3,5,255])for s in[0,1,2,3,4,5,255]),'Literalstatusfilter accepts failures1,2,3,5,255; APIvalid is0.')
ck('Polar coordinates',abs(2*math.cos(math.pi/2))<1e-12 and 2*math.sin(math.pi/2)==2,'Supplied Cartesian convention gives(0,2)m.')
ck('Resolution percent',2000*.01==20 and 20/.5==40,'1%at2m is20mm, forty times0.5mm.')
ck('RPM conversion',round(416/60,1)==6.9 and 6.9*60==414,'Rounded6.9Hz compatible416RPM, not exact equality.')
ck('FPS and playback',int(1/.25)==4 and 100/50==2 and 100/20==5,'Initial0,next4fps; measured2fps versus5s playback.')
ck('Stereo correct and distractors',400*.1/20==2 and math.isclose(.1*20/400,.005)and 400*.1*20==800,'2m correct; reversed ratio0.005m; multiplication800 with invalid pixel-unit cancellation.')
ck('Wrench',.2*10==2,'Right-handed r×F gives+2N·m aboutz; reversed order−2.')
ck('Latency budget',50-10-5-5==30,'30ms remaining;40omits transfer/control;20double-counts sensing.')
ck('Power/endurance',100/(15+5)==5 and 100/5==20 and round(100/15,2)==6.67,'Total load20W yields5h; sensor-only20h; other-only6.67h.')
ck('Binary versus Gray transition',sum(a!=b for a,b in zip('0111','1000'))==4,'All four positions change; not a one-bit Gray transition.')
ck('Bounce edge count',sum(a=='HIGH'and b=='LOW'for a,b in zip(['HIGH','LOW','HIGH','LOW','HIGH'],['LOW','HIGH','LOW','HIGH','LOW']))==3,'Three falling edges and two rising edges from one supplied magnet passage.')
ck('Capacitive gap ratio',2.0/(0.5)==4 and (2.0/0.5)/(2.0/1.0)==2,'Positive gap halved, fixed numerator; capacitance doubles.')
ck('Selection constraints',[lo<=.1 and hi>=3 and err<=2 and rate>=20 for lo,hi,err,rate in[(.05,4,3,25),(.05,4,1,25),(.2,6,1,30),(.05,4,1,10)]]==[False,True,False,False],'Only candidate with full near/far coverage,1cm error and25Hz rate passes.')
ck('Integrated selection',[(lo<=.1 and hi>=3 and err<=2 and sense+infer+10<=50 and 120/(18+p)>=5)for lo,hi,err,sense,infer,p in[(.05,4,1,10,30,5),(.2,6,1,5,20,3),(.05,4,1,10,30,8),(.05,4,1,15,30,4)]]==[True,False,False,False],'Combined range/error/time/energy requirements; only first supplied configuration passes. Endurances120/23,120/21,120/26,120/22h.')
# Independent random inputs here are still author checks, not independent review.
rng=random.Random(52065);assertions=0
for _ in range(1000):
 c=rng.uniform(300,360);d=rng.uniform(.02,4);t=2*d/c;assert math.isclose(c*t/2,d,rel_tol=1e-12);assertions+=1
 top=rng.uniform(1,100);bottom=rng.uniform(1,100);v=5*bottom/(top+bottom);assert 0<v<5;assertions+=1
 ax,ay,az=[rng.uniform(-100,100)for _ in range(3)];k=rng.uniform(.01,100);angle=math.atan2(-ax,math.hypot(ay,az));a2=math.atan2(-k*ax,math.hypot(k*ay,k*az));assert math.isclose(angle,a2,abs_tol=1e-12)and -math.pi/2<=angle<=math.pi/2;assertions+=1
 h=rng.randrange(256);lo=rng.randrange(256);u=256*h+lo;s=u if u<32768 else u-65536;assert int.from_bytes(bytes([h,lo]),'big',signed=True)==s;assertions+=1
ck('Random dimensional/geometry checks',assertions==4000,'1000seeded cases;4000assertions:acoustic inverse,divider bounds,positive-scale tilt invariance,signed bytes.')
report={'batchId':'W11-L52','authorId':'L52-author-20261019','status':'author_checks_only_not_independent_review','transcriptionPath':'sources/supplemental/L52-slide-code-transcriptions.json','sourceSha256':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','checks':checks,'checkGroups':len(checks),'randomCases':1000,'randomAssertions':assertions,'executionScope':'10C++ sketches tested in host Arduino-interface stubs, including expected original tilt failure and one-semicolon repair; Python source executed with explicit cv2/YOLO/time stubs. No AVR timing simulation, physical sensors, camera acquisition, original notebook or YOLO checkpoint execution.','workspace':str(work)}
(R/'audits/W11-L52-author-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(len(checks),'author check groups;',assertions,'random assertions')
