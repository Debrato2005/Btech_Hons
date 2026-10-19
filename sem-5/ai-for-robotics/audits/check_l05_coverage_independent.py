"""Independent source-based checks. Pure Python stubs are not a ROS runtime."""
import ast,contextlib,io,json,math,platform
from fractions import Fraction as F
from types import SimpleNamespace
from pathlib import Path
checks=[]
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected)
 checks.append({'name':name,'actual':actual,'expected':expected,'passed':True})
def period(f):
 if f<=0:raise ValueError('frequency must be positive')
 return 1/F(f)
def count(T,end):
 if T<=0 or end<0:raise ValueError('positive period and nonnegative duration required')
 return int(F(end)//F(T))
check('30 Hz period in ms',round(float(period(30)*1000),2),33.33)
check('0.1 s timer Hz',1/F('0.1'),10)
for end,expect in [('0',0),('0.099',0),('0.1',1),('1.999',19),('2.0',20),('2.001',20)]:check('positive ticks through '+end,count(F('0.1'),F(end)),expect)
check('camera events in (0,1]',count(F(1,30),1),30)
check('timer events in (0,1]',count(F(1,10),1),10)
check('camera to timer count ratio',F(30,10),3)
check('sustained backlog growth',30-1/F('0.1'),20)
invalid=0
for f in [0,-30]:
 try:period(f)
 except ValueError:invalid+=1
for T,end in [(0,1),(-1,1),(1,-1)]:
 try:count(T,end)
 except ValueError:invalid+=1
check('invalid mathematical domains rejected',invalid,5)
# Source p187 transcribed after actual pixel inspection; explicit rclpy/Node stubs.
lifecycle='''class MyNode(Node):
 def __init__(self):
  super().__init__('my_node')
def main():
 rclpy.init()
 node=MyNode()
 rclpy.spin(node)
 rclpy.shutdown()
if __name__=='__main__':
 main()
'''
trace=[]
class Node:
 def __init__(self,name):self.name=name;trace.append(('construct',name))
rclpy=SimpleNamespace(init=lambda:trace.append(('init',)),spin=lambda n:trace.append(('spin',n.name)),shutdown=lambda:trace.append(('shutdown',)))
exec(compile(lifecycle,'p187','exec'),{'Node':Node,'rclpy':rclpy,'__name__':'imported_module'})
check('module import guard does not launch main',trace,[])
exec(compile(lifecycle,'p187','exec'),{'Node':Node,'rclpy':rclpy,'__name__':'__main__'})
check('source main lifecycle order',trace,[('init',),('construct','my_node'),('spin','my_node'),('shutdown',)])
# p192 registration and callback logic, not delivery/scheduling validation.
pubsub='''class PubSubNode(Node):
 def __init__(self):
  super().__init__('pubsub_node')
  self.pub=self.create_publisher(String,'topic',10)
  self.sub=self.create_subscription(String,'topic',self.callback,10)
  self.timer=self.create_timer(0.1,self.publish_msg)
 def publish_msg(self):
  msg=String()
  msg.data='Hello ROS'
  self.pub.publish(msg)
 def callback(self,msg):
  print(f'Received: {msg.data}')
'''
class String:pass
class RegistrationNode:
 def __init__(self,name):self.name=name;self.events=[];self.sent=[]
 def create_publisher(self,typ,topic,depth):self.events.append(('publisher',typ.__name__,topic,depth));return SimpleNamespace(publish=lambda msg:self.sent.append(msg))
 def create_subscription(self,typ,topic,fn,depth):self.events.append(('subscription',typ.__name__,topic,fn.__name__,depth));return fn
 def create_timer(self,period,fn):self.events.append(('timer',period,fn.__name__));return fn
ns={'Node':RegistrationNode,'String':String};exec(pubsub,ns);node=ns['PubSubNode']()
check('publisher signature separate from timer',node.events[0],('publisher','String','topic',10))
check('subscription callback signature',node.events[1],('subscription','String','topic','callback',10))
check('timer uses period and publish callback',node.events[2],('timer',0.1,'publish_msg'))
check('construction does not itself publish',len(node.sent),0)
node.timer();check('manual timer callback constructs String',type(node.sent[0]).__name__,'String');check('published payload',node.sent[0].data,'Hello ROS')
out=io.StringIO()
with contextlib.redirect_stdout(out):node.sub(node.sent[0])
check('conditional subscription output',out.getvalue(),'Received: Hello ROS\n')
# p199 handler semantics, return identity and independent parameter print.
handler='''def handle_service(self,request,response):
 response.sum=request.a+request.b
 return response
'''
ns={};exec(handler,ns)
for a,b,expect in [(2,3,5),(-4,7,3),(0,0,0),(-4,4,0),(-2,-3,-5)]:
 response=SimpleNamespace();result=ns['handle_service'](None,SimpleNamespace(a=a,b=b),response)
 check(f'handler signed addition {a},{b}',result.sum,expect)
 check(f'handler returns response object {a},{b}',result is response,True)
for speed,expect in [(1.0,'Speed param: 1.0'),(2.5,'Speed param: 2.5')]:check('independent parameter print '+str(speed),f'Speed param: {speed}',expect)
# Static call_async assignment is not a result read; validate source-shape premise.
request='''def send_request(self):
 req=AddTwoInts.Request()
 req.a,req.b=2,3
 future=self.client.call_async(req)
 speed=self.get_parameter('speed').value
 print(f'Speed param: {speed}')
'''
tree=ast.parse(request);calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
check('request code contains call_async',any(isinstance(n.func,ast.Attribute) and n.func.attr=='call_async' for n in calls),True)
check('request code has no future.result call',any(isinstance(n.func,ast.Attribute) and n.func.attr=='result' for n in calls),False)
# Fixed camera mount relation is unchanged under global translation.
base_before=(1,2,3);base_after=(5,0,7);mount=(.2,.3,.4)
cam_before=tuple(a+b for a,b in zip(base_before,mount));cam_after=tuple(a+b for a,b in zip(base_after,mount))
check('global translation preserves relative mount',all(math.isclose(c-b,m) for c,b,m in zip(cam_after,base_after,mount)),True)
check('global camera position changes',cam_before!=cam_after,True)
# Numerical alternatives remain distinguishable for all six current numerical items.
option_values={22:[33.33,30,300,3330],23:[10,.1,100],26:[20,21,19,2],27:[20,10,30,0],72:[(30,10,3),(30,10,F(1,3)),(31,11,F(31,11)),(10,10,1)],77:[3,-11,11,-47]}
check('numeric alternatives distinct at displayed precision',all(len(vals)==len(set(vals)) for vals in option_values.values()),True)
def safe(o):
 if isinstance(o,F):return str(o)
 raise TypeError(type(o))
report={'reviewerId':'independent-reviewer-robotics-batches-v2','scope':'Fresh pure-Python arithmetic, AST and explicit stub traces from visually inspected source. No actual ROS middleware, DDS delivery, executor scheduling, hardware deadlines or installed API compatibility was tested. No frozen author script was used.','pythonVersion':platform.python_version(),'checks':checks,'passed':len(checks),'failed':0}
Path('audits/W01-L05-coverage-challenge-independent-computations.json').write_text(json.dumps(report,indent=2,default=safe)+'\n')
print('PASS',len(checks))
