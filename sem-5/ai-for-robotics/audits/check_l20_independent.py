"""Independent L20 arithmetic and mechanics; does not read author data or checks."""
from pathlib import Path
import numpy as np, math, json, random
from datetime import datetime, timezone
checks=[]
def ck(name,actual,expected,tol=1e-8):
 if isinstance(actual,(list,tuple)) and actual and isinstance(actual[0],str):
  ok=actual==expected
 elif isinstance(actual,(np.ndarray,list,tuple)):
  ok=bool(np.allclose(actual,expected,atol=tol,rtol=tol));actual=np.asarray(actual).tolist();expected=np.asarray(expected).tolist()
 elif isinstance(actual,(float,int)) and not isinstance(actual,bool):ok=math.isclose(actual,expected,abs_tol=tol,rel_tol=tol)
 else:ok=actual==expected
 checks.append(dict(name=name,actual=actual,expected=expected,passed=ok));assert ok,(name,actual,expected)
rad=math.radians;sin=math.sin;cos=math.cos

def fk(q,l1=.25,l2=.20,d1=.40):
 a,b,d,c=q
 return np.array([l1*cos(a)+l2*cos(a+b),l1*sin(a)+l2*sin(a+b),d1-d,a+b+c])
def jac(q,l1=.25,l2=.20):
 a,b,d,c=q
 return np.array([[-l1*sin(a)-l2*sin(a+b),-l2*sin(a+b),0,0],[l1*cos(a)+l2*cos(a+b),l2*cos(a+b),0,0],[0,0,-1,0],[1,1,0,1]])
def transform(theta,x,y,z):
 return np.array([[cos(theta),-sin(theta),0,x],[sin(theta),cos(theta),0,y],[0,0,1,z],[0,0,0,1]])
def tf(q,l1=.25,l2=.2,d1=.4):
 a,b,d,c=q
 return transform(a,l1*cos(a),l1*sin(a),d1)@transform(b,l2*cos(b),l2*sin(b),0)@transform(0,0,0,-d)@transform(c,0,0,0)
q=np.array([rad(45),rad(30),.08,rad(15)])
xy=fk(q)*np.array([1000,1000,1000,180/math.pi])
ck('worked FK x to .1mm',round(xy[0],1),228.5);ck('worked FK y to .1mm',round(xy[1],1),370.)
ck('worked FK z/yaw',xy[2:],[320,90]);ck('printed y369.7 is not valid .1 rounding',round(xy[1],1)!=369.7,True)
ck('hypothetical matrix',tf([0,rad(90),.08,rad(-90)]),[[1,0,0,.25],[0,1,0,.20],[0,0,1,.32],[0,0,0,1]])
D=(.25**2+.15**2-.25**2-.20**2)/(2*.25*.20);ck('IK cosine D',D,-.175)
branches=[]
for sign in [1,-1]:
 b=sign*math.acos(D);a=math.atan2(.15,.25)-math.atan2(.2*sin(b),.25+.2*cos(b));c=rad(90)-a-b
 q0=[a,b,.08,c];branches.append([math.degrees(a),math.degrees(b),80,math.degrees(c)])
 ck(f'IK branch {sign} forward recovery',fk(q0),[.25,.15,.32,rad(90)])
ck('IK positive rounded',np.round(branches[0],1),[-11.5,100.1,80,1.4]);ck('IK negative rounded',np.round(branches[1],1),[73.4,-100.1,80,116.6])
ck('radial ideal bounds',[abs(.25-.20),.25+.20],[.05,.45])
ck('annular prism volume',math.pi*(.45**2-.05**2)*.2,.04*math.pi)
ck('145degree elbow min radius mm',round(math.sqrt(250**2+200**2+2*250*200*cos(rad(145))),1),143.5)
ck('Jacobian full determinant',np.linalg.det(jac(q)),-.25*.2*sin(q[1]))
ck('task rate vector',jac([0,rad(90),0,0])@np.array([1,2,.03,-3]),[-.6,.25,-.03,0])
ck('straight arm x row',jac([0,0,0,0])[0],[0,0,0,0])

# M reconstructed from independent kinetic-energy contributions.
def mass(q,l1=.2,l2=.16,m1=1,m2=2,m3=.5,m4=.5,I1=.01,I2=.02,I4=.005):
 a,b,d,c=q
 # Translational kinetic energy using each COM Jacobian.
 J1=np.zeros((3,4));J1[:2,0]=[-l1/2*sin(a),l1/2*cos(a)]
 J2=np.zeros((3,4));J2[:2,0]=[-l1*sin(a)-l2/2*sin(a+b),l1*cos(a)+l2/2*cos(a+b)];J2[:2,1]=[-l2/2*sin(a+b),l2/2*cos(a+b)]
 Je=jac(q,l1,l2)[:3,:]
 w1=np.array([1,0,0,0]);w2=np.array([1,1,0,0]);w4=np.array([1,1,0,1])
 return m1*J1.T@J1+m2*J2.T@J2+(m3+m4)*Je.T@Je+I1*np.outer(w1,w1)+I2*np.outer(w2,w2)+I4*np.outer(w4,w4)
M=mass([0,rad(90),0,0]);ck('M11 independently assembled COM energy',M[0,0],.2034);ck('M12 and M22 independently assembled', [M[0,1],M[1,1]],[.0634,.0634]);ck('M33',M[2,2],1)
ck('wrist coupled effort',(M@np.array([1,2,0,3]))[3],.03)
ck('velocity terms given h',[-.064*(2*1*2+2**2),.064*1**2],[-.512,.064])
ck('velocity omega2 zero',[-.064*(2*1*0+0**2),.064*1**2],[0,.064])
ck('hold actuator force downward coordinate',-1.2*9.81,-11.772)
# Randomized exact/finite-difference cross-checks, never author checks.
rng=random.Random(20201019);max_jerr=max_tferr=max_verr=0.;min_eig=1.
for n in range(500):
 q=np.array([rng.uniform(-3,3),rng.uniform(-3,3),rng.uniform(0,.2),rng.uniform(-3,3)])
 f=fk(q);T=tf(q);max_tferr=max(max_tferr,float(np.max(np.abs(T[:3,3]-f[:3]))))
 eps=1e-6;num=np.column_stack([(fk(q+np.eye(4)[k]*eps)-fk(q-np.eye(4)[k]*eps))/(2*eps) for k in range(4)])
 max_jerr=max(max_jerr,float(np.max(np.abs(num-jac(q)))))
 assert abs(np.linalg.det(jac(q))+.25*.20*sin(q[1]))<1e-12
 if n<150:
  M=mass(q);assert np.allclose(M,M.T);min_eig=min(min_eig,float(np.linalg.eigvalsh(M)[0]));assert np.linalg.eigvalsh(M)[0]>0
  deriv=np.stack([(mass(q+np.eye(4)[k]*eps)-mass(q-np.eye(4)[k]*eps))/(2*eps) for k in range(4)])
  v=np.array([rng.uniform(-2,2) for _ in range(4)])
  christ=np.zeros(4)
  for i in range(4):
   for j in range(4):
    for k in range(4):christ[i]+=.5*(deriv[k,i,j]+deriv[j,i,k]-deriv[i,j,k])*v[j]*v[k]
  h=.2*sin(q[1])*(2*.16/2+(.5+.5)*.16)
  analytic=np.array([-h*(2*v[0]*v[1]+v[1]**2),h*v[0]**2,0,0])
  max_verr=max(max_verr,float(np.max(np.abs(christ-analytic))))
ck('500 finite-difference Jacobians maximum error',max_jerr,0,1e-8)
ck('500 matrix products maximum translation error',max_tferr,0,1e-10)
ck('150 energy-derived Christoffel vectors maximum error',max_verr,0,1e-8)
ck('150 generalized mass matrices positive definite',min_eig>0,True)
ck('accel-limited distance .38s',300*.38**2/4,10.83)
ck('minimum triangular time',2*math.sqrt(90/300),1.0954451150103321)
ck('triangular peak below cap',math.sqrt(90*300)<400,True)
ck('repaired trapezoid acceleration',400/(.38-90/400),2580.6451612903224)
ck('repaired trapezoid positive cruise',.38-2*(.38-90/400),.07)
ck('ideal stiffness ratio',250/20,12.5)
ck('gear speed and torque',[3000/100,.5*100],[30,50])
ck('screw stroke revolutions',130/10,13)
ck('forward screw torque',100*.01/(2*math.pi*.95),.16753151904410037)
ck('stiffness deflection upper limit microns',100/200,.5)
ck('wrist power at simultaneous point',3*2000*2*math.pi/60,628.3185307179587)
ck('literal grams moving mass',.5/1000+.8,.8005)
ck('table capacity ratio',3/(.5+.8),30/13)
ck('stroke percent margin',100*(180-130)/130,500/13)
ck('encoder codes and angle',[2**20,360/2**20],[1048576,.00034332275390625])
ck('chosen link radii',[200+160,abs(200-160)],[360,40])
ck('hollow rectangular area',40*30-(40-6)*(30-6),384)
ck('300 degrees acceleration conversion',rad(300),5*math.pi/3)
ck('J1 load only motor torque',.042*52.4/100,.022008)
ck('J2 load only motor torque',.018*52.4/80,.01179)
ck('upward payload force',1.3*(40+9.81),64.753)
ck('wrist load torque',.0008*200,.16)
ck('reducer forward efficiency',8/(80*.8),.125)
ck('unwrapped wrist yaw',45-150,-105)
items1=[620,420,380,180,1200,850,320,420,350,1800,4*220,480]
ck('servo drives extended',4*220,880);ck('controller subtotal',1800+4*220,2680);ck('transmission subtotal',1200+850+320,2370)
ck('actuation subtotal',sum(items1[:4]),1600);ck('first BOM',sum(items1),7900);ck('sensing subtotal',650+4*120,1130)
ck('literal two-page BOM',sum(items1)+650+4*120+180+420,9630);ck('one-system BOM',sum(items1)+650+4*120+180,9210)
ck('one-system over target',9210-8500,710);ck('production target reduction',100*(8500-4200)/8500,50.588235294117645)
ck('reported shares normalize',32+28+24+10+6,100)
ck('reported actuation share is not exact one-system share',math.isclose(1600/9210,.24),False)
ck('largest category order',sorted({'controller':2680,'transmission':2370,'actuation':1600,'sensing':1130,'vision':480,'safety':420,'structure':350,'misc':180},key=lambda k:{'controller':2680,'transmission':2370,'actuation':1600,'sensing':1130,'vision':480,'safety':420,'structure':350,'misc':180}[k],reverse=True)[:2],['controller','transmission'])
report={'reviewerId':'independent-reviewer-robotics-batches-v2','completedAt':datetime.now(timezone.utc).isoformat(),'method':'Source-pixel formulas independently implemented. Mass matrix reconstructed from COM and angular kinetic-energy Jacobians, and velocity terms cross-checked via finite-difference Christoffel symbols. No author data, script or keyed answers read.','checks':checks,'passed':int(sum(x['passed'] for x in checks)),'failed':int(sum(not x['passed'] for x in checks)),'randomCases':{'fkAndJacobian':500,'massAndChristoffel':150},'workedValues':{'FKmmDegrees':xy.tolist(),'IKBranchesDegreesMm':branches}}
Path('audits/W04-L20-independent-computations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n')
print(json.dumps({'passed':report['passed'],'failed':report['failed'],'randomCases':report['randomCases'],'workedValues':report['workedValues']}))
