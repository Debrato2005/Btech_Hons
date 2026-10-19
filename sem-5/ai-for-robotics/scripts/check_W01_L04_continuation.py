"""Independent checks from visually read source pages 161–166, not author code."""
import json,datetime,pathlib,hashlib,sys,io,contextlib,math
import numpy as np
from scipy.spatial.distance import euclidean
ROOT=pathlib.Path(__file__).resolve().parents[1]
checks=[]
def check(name,actual,expected):
 ok=actual==expected
 checks.append({'name':name,'actual':actual,'expected':expected,'pass':ok})
 assert ok,name
check('p161 value types',[type(v).__name__ for v in ['mobile robot',1.5,4]],['str','float','int'])
check('p161 zero index',[1.2,1.5,.9,2][2],.9)
check('p161 tuple and distinct set',[type((2.3,1.2,.5)).__name__,len({'chair','table','wall','chair'})],['tuple',3])
try:exec('def compute_distance(speed,time):\n distance=speed*time\n return distance\nd=compute_travel_distance(10,5)',{})
except Exception as e:check('p161 literal call error',type(e).__name__,'NameError')
ns={};exec('def compute_distance(speed,time):\n distance=speed*time\n return distance\nd=compute_distance(10,5)',ns);check('p161 explicit repaired call',ns['d'],50)
check('p162 sqrt441',math.sqrt(441),21.0)
loop='''sensor_data = [2.0, 1.5, 0.8, 0.4, 0.2]
for reading in sensor_data:
    if reading < 0.5:
        action = "STOP"
        break
    if reading < 1.0:
        action = "Reduce speed"
        print("Distance:", reading, "Robot action:", action)
        continue
    else:
        action = "MOVE_FORWARD"
    print("Distance:", reading, "Robot action:", action)
print("Distance:", reading, "Final Robot action:", action)
'''
buf=io.StringIO();ns={}
with contextlib.redirect_stdout(buf):exec(loop,ns)
check('p162 final reading/action',[ns['reading'],ns['action']],[.4,'STOP'])
check('p162 line count',len(buf.getvalue().splitlines()),4)
check('p162 exact outputs',buf.getvalue().splitlines(),['Distance: 2.0 Robot action: MOVE_FORWARD','Distance: 1.5 Robot action: MOVE_FORWARD','Distance: 0.8 Robot action: Reduce speed','Distance: 0.4 Final Robot action: STOP'])
for x,expected in [(.5,'Reduce speed'),(1.0,'MOVE_FORWARD')]:
 ns={};b=io.StringIO()
 with contextlib.redirect_stdout(b):exec(loop.replace('[2.0, 1.5, 0.8, 0.4, 0.2]',repr([x])),ns)
 check(f'p162 supplied boundary {x}',ns['action'],expected)
classes='''class Robot:
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed
    def move(self, time, action="moved"):
        distance = self.speed * time
        print(self.name, action, distance, "meters")
    def status(self):
        print("Robot:", self.name)
        print("Speed:", self.speed)
class MobileRobot(Robot):
    def move(self, time):
        distance = self.speed * time
        print(self.name, "drives", distance, "m")
class Drone(Robot):
    def move(self, time):
        super().move(time, "flies")
'''
ns={};exec(classes,ns);robot=ns['Robot']('rover_1',1.5)
check('p163 initializer',[robot.name,robot.speed],['rover_1',1.5])
b=io.StringIO()
with contextlib.redirect_stdout(b):robot.status()
check('p163 status',b.getvalue().splitlines(),['Robot: rover_1','Speed: 1.5'])
b=io.StringIO()
with contextlib.redirect_stdout(b):result=robot.move(4)
check('p163 move print',b.getvalue().strip(),'rover_1 moved 6.0 meters')
check('p163 return',result,None)
r1=ns['MobileRobot']('rover',1.5);r2=ns['Drone']('quadrotor',3.5)
check('p164 inherited initializer',[r1.name,r1.speed,r2.name,r2.speed],['rover',1.5,'quadrotor',3.5])
b=io.StringIO()
with contextlib.redirect_stdout(b):r1.move(3);r2.move(3)
check('p164 overridden and super outputs',b.getvalue().splitlines(),['rover drives 4.5 m','quadrotor flies 10.5 meters'])
pose=np.array([0,0]);goal=np.array([5,4]);motions=np.array([[1,1],[1,.5],[1,.5],[1,1]]);path=[pose]
check('p165 shape',list(motions.shape),[4,2])
for m in motions:
 pose=pose+m;path.append(pose)
check('p166 array identities distinct',len({id(x) for x in path}),5)
path=np.array(path)
check('p166 path',path.tolist(),[[0,0],[1,1],[2,1.5],[3,2],[4,3]])
check('p166 remaining distance 3dp',round(euclidean(path[-1],goal),3),1.414)
check('p166 path length 3dp',round(float(sum(np.linalg.norm(x) for x in np.diff(path,axis=0))),3),5.064)
check('p166 columns and last',[path[:,0].tolist(),path[:,1].tolist(),path[-1].tolist()],[[0,1,2,3,4],[0,1,1.5,2,3],[4,3]])
pose=np.array([0,0])
try:pose+=motions[0]
except Exception as e:
 check('p166 in-place cast error',type(e).__name__,'UFuncTypeError');casting_error=str(e)
else:raise AssertionError('expected output-casting error')
report={'reviewerId':'define_robotics_data_contracts:L04-continuation-reviewer','executedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pythonVersion':sys.version,'numpyVersion':np.__version__,'scriptSha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'checks':checks,'castingErrorMessage':casting_error,'total':len(checks),'passed':sum(c['pass'] for c in checks),'sourcePages':[161,162,163,164,165,166],'scope':'Fresh continuation code transcriptions from actual source pixels. Original reviewer checks remain unchanged.'}
(ROOT/'audits/W01-L04-v1-continuation-code-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'total':report['total'],'passed':report['passed'],'numpy':np.__version__}))
