"""Independent v2 checks from visually inspected source equations, not author code."""
import json, math, random, hashlib, datetime
import numpy as np
from pathlib import Path
checks=[]
def check(label, value, expected, tol=1e-9):
    ok=bool(np.allclose(value,expected,atol=tol,rtol=tol))
    checks.append({'label':label,'actual':np.asarray(value).tolist(),'expected':np.asarray(expected).tolist(),'passed':ok})
    assert ok,label
l1,l2,x,y=.25,.2,.25,.15
D=(x*x+y*y-l1*l1-l2*l2)/(2*l1*l2)
t2=-math.acos(D);t1=math.atan2(y,x)-math.atan2(l2*math.sin(t2),l1+l2*math.cos(t2));t4=math.pi/2-t1-t2
check('IK cosine',D,-.175)
check('negative elbow joint angles degrees',np.degrees([t1,t2,t4]),[73.4496272930291,-100.07865810778767,116.62903081475858])
check('negative elbow one-decimal options',[round(a,1) for a in np.degrees([t1,t2,t4])],[73.4,-100.1,116.6])
check('IK independent FK reconstruction',[l1*math.cos(t1)+l2*math.cos(t1+t2),l1*math.sin(t1)+l2*math.sin(t1+t2)],[x,y])
check('IK vertical extension mm',400-320,80)
check('fully extended branches merge',math.acos(1),0)
check('ideal radii mm',[abs(250-200),250+200],[50,450])
check('vertical Jacobian derivative',((.4-(.08+1e-5))-(.4-.08))/1e-5,-1)
l1,l2,m2,md=.2,.16,2,1
c=l1*l2*(m2/2+md);h=c*math.sin(math.pi/2)
check('coupling coefficient kg m2',h,.064)
check('h full m2 misconception',l1*l2*(m2+md),.096)
check('velocity torque vector',[-h*(2*1*2+2**2),h*1**2],[-.512,.064])
check('velocity rates swapped distractor',[-h*(2*2*1+1**2),h*2**2],[-.320,.256])
check('full m2 coefficient distractor',[-.096*8,.096],[-.768,.096])
check('stationary elbow terms',[-h*(2*1*0+0),h*1],[0,.064])
check('actually exchanged expressions under stationary elbow',[h*1,-h*(2*1*0+0)],[.064,0])
# This positive sign explicitly contradicts the saved o3 rationale; flag remains.
check('potential gradient downward-positive',((md*9.81*(.4-(.08+1e-5)))-(md*9.81*(.4-.08)))/1e-5,-9.81)
check('mass matrix change at extension',[2*c,c,0],[.128,.064,0])
check('mass matrix inflated coefficient distractor',[2*l1*l2*(m2+md),l1*l2*(m2+md),0],[.192,.096,0])
p=[lambda t:t*t,lambda t:1+2*(t-1),lambda t:6-(4-t)**2]
v=[lambda t:2*t,lambda t:2,lambda t:2*(4-t)]
check('phase initial position and velocity',[p[0](0),v[0](0)],[0,0])
check('first phase switch positions',[p[0](1),p[1](1)],[1,1])
check('first phase switch velocities',[v[0](1),v[1](1)],[2,2])
check('second phase switch positions',[p[1](3),p[2](3)],[5,5])
check('second phase switch velocities',[v[1](3),v[2](3)],[2,2])
check('final phase position and velocity',[p[2](4),v[2](4)],[6,0])
check('cruise wrong offset starts at 3',1+2*1,3)
check('wrong deceleration sign starts at 7 with negative velocity',[6+(4-3)**2,-2*(4-3)],[7,-2])
check('wrong deceleration clock ends at minus10 with nonzero speed',[6-4**2,-2*4],[-10,-8])
check('ideal motor acceleration torque',.042*52.4/100,.022008)
check('output torque distractor',.042*52.4,2.2008)
check('inverted gear reduction distractor',.042*52.4*100,220.08)
check('upward payload force',1.3*(40+9.81),64.753)
check('static weight only distractor',1.3*9.81,12.753)
check('gravity omitted distractor',1.3*40,52)
check('BOM actuation subtotal',620+420+380+180,1600)
check('BOM controller subtotal',1800+4*220,2680)
check('BOM sensor subtotal',650+4*120,1130)
check('source percentages normalized',32+28+24+10+6,100)
# Independently derive cosine changes from full displayed entries across varied angles.
rng=random.Random(2026101920)
maxerr=0
for i in range(500):
    a,b,m,dist=[rng.uniform(.01,3) for _ in range(4)]
    q0,q1=[rng.uniform(-math.pi,math.pi) for _ in range(2)]
    I1,I2,I4,m1=[rng.uniform(.01,3) for _ in range(4)]
    def entries(q):
        co=math.cos(q)
        return np.array([I1+I2+I4+m1*(a/2)**2+m*(a*a+(b/2)**2+a*b*co)+dist*(a*a+b*b+2*a*b*co),I2+I4+m*((b/2)**2+a*b*co/2)+dist*(b*b+a*b*co),I2+I4+m*(b/2)**2+dist*b*b])
    actual=entries(q1)-entries(q0)
    expected=a*b*(m/2+dist)*(math.cos(q1)-math.cos(q0))*np.array([2,1,0])
    maxerr=max(maxerr,float(np.max(abs(actual-expected))))
    assert np.allclose(actual,expected,atol=1e-10)
report={'reviewerId':'independent-reviewer-robotics-batches-v2','recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'Visually inspected pages 615–623, 630–632. Independent code only; author code not opened or executed.','checks':checks,'passed':len(checks),'failed':0,'variedMassMatrixCases':500,'variedMassMatrixMaximumAbsoluteError':maxerr,'knownRationaleFlag':{'questionId':'W04-L20-P0622-Q02','optionId':'o3','actualExchangedV1':'+hω1²','displayedDistractorV1':'−hω1²','reason':'Exchanging expressions alone does not reproduce the distractor sign.'}}
Path('audits/W04-L20-v2-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
