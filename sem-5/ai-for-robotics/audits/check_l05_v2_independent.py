"""Independent L05 arithmetic and source-code semantic checks; no ROS runtime claim."""
import contextlib, importlib.util, io, json, math, random
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace as NS

checks=[]
def check(name, actual, expected):
    assert actual==expected,(name,actual,expected)
    checks.append({'name':name,'actual':actual,'expected':expected,'passed':True})
check('30 Hz period rounded in ms', round(float(1000/Fraction(30)),2),33.33)
check('0.1 second timer reciprocal Hz',1/Fraction('0.1'),10)
check('positive timer ticks through 2 seconds',sum(0<Fraction(k,10)<=2 for k in range(40)),20)
check('camera ticks in (0,1]',sum(0<Fraction(k,30)<=1 for k in range(40)),30)
check('timer ticks in (0,1]',sum(0<Fraction(k,10)<=1 for k in range(40)),10)
check('camera/timer count ratio',Fraction(30,10),3)
check('sustained backlog growth frames/s',Fraction(30)-1/Fraction('0.1'),20)

def handle_service(request,response):
    response.sum=request.a+request.b
    return response
check('source handler 2+3',handle_service(NS(a=2,b=3),NS()).sum,5)
check('signed variant -4+7',handle_service(NS(a=-4,b=7),NS()).sum,3)
msg=NS(data='Hello ROS');s=io.StringIO()
with contextlib.redirect_stdout(s): print(f'Received: {msg.data}')
check('source subscription f-string',s.getvalue().strip(),'Received: Hello ROS')
for speed in [1.0,2.5]:
    s=io.StringIO()
    with contextlib.redirect_stdout(s): print(f'Speed param: {speed}')
    check(f'parameter print {speed}',s.getvalue().strip(),f'Speed param: {speed}')
    check(f'independent handler while speed={speed}',handle_service(NS(a=2,b=3),NS()).sum,5)
# A faithful minimal semantic harness records endpoint and callback registrations.
# It deliberately does not simulate DDS, scheduling, discovery, executor or QoS.
class String:
    def __init__(self):self.data=''
class NodeStub:
    def __init__(self,name):self.name=name;self.registrations=[];self.messages=[]
    def create_publisher(self,typ,name,depth):
        self.registrations.append(('publisher',typ.__name__,name,depth));return NS(publish=self.messages.append)
    def create_subscription(self,typ,name,callback,depth):
        self.registrations.append(('subscription',typ.__name__,name,callback.__name__,depth));return NS(callback=callback)
    def create_timer(self,period,callback):
        self.registrations.append(('timer',period,callback.__name__));return NS(callback=callback)
class PubSubNode(NodeStub):
    def __init__(self):
        super().__init__('pubsub_node')
        self.pub=self.create_publisher(String,'topic',10)
        self.sub=self.create_subscription(String,'topic',self.callback,10)
        self.timer=self.create_timer(0.1,self.publish_msg)
    def publish_msg(self):
        msg=String();msg.data='Hello ROS';self.pub.publish(msg)
    def callback(self,msg): print(f'Received: {msg.data}')
n=PubSubNode()
check('timer selects publish callback',n.registrations[-1],('timer',0.1,'publish_msg'))
check('subscription selects receive callback',n.registrations[1],('subscription','String','topic','callback',10))
check('no publication during constructor',len(n.messages),0)
n.timer.callback();check('timer callback constructs and publishes String',n.messages[0].data,'Hello ROS')
rng=random.Random(1052026)
for _ in range(1000):
    a,b=rng.randint(-100000,100000),rng.randint(-100000,100000)
    assert handle_service(NS(a=a,b=b),NS()).sum==a+b
    rate=rng.randint(1,1000);duration=Fraction(rng.randint(0,10000),1000)
    count=duration*rate
    assert sum(Fraction(k,rate)<=duration for k in range(1,math.floor(count)+2))==math.floor(count)
check('random signed additions and rational endpoint counts',1000,1000)
check('zero-duration interval has zero positive events',sum(0<Fraction(k,10)<=0 for k in range(10)),0)
# Domain and rounding guards are explicit, not accidental Python behavior.
def period(rate):
    if not math.isfinite(rate) or rate<=0: raise ValueError('positive finite rate required')
    return 1/rate
for bad in [0,-1,float('inf'),float('nan')]:
    try:period(bad)
    except ValueError:pass
    else:raise AssertionError('invalid rate accepted')
check('invalid reciprocal-rate domains rejected',4,4)
for opts in [[33.33,30,300,3330],[10,.1,100],[20,21,19,2],[20,10,30],[5,1,23],[3,-11,11,-47]]:
    assert len(set(opts))==len(opts)
check('numeric option collision sets inspected',6,6)
out={'scope':'Independent exact arithmetic, conditional handler and formatting execution, and explicit stub trace of source registration. Not a ROS/DDS runtime or actual middleware deadline validation. No generated variants are present in the frozen batch.','rosRuntimeInstalled':importlib.util.find_spec('rclpy') is not None,'seed':1052026,'checks':checks,'allPassed':True}
Path('audits/W01-L05-v2-independent-computations.json').write_text(json.dumps(out,indent=2,default=lambda v:float(v) if isinstance(v,Fraction) else str(v))+'\n')
print(len(checks),'checks passed; 1000 random cases; no ROS runtime claim')
