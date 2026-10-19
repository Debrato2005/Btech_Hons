#!/usr/bin/env python3
"""Author-side algebra/code checks for L18; not independent answer verification."""
import datetime,hashlib,json,math,sys,os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/robotics-l18-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/robotics-l18-cache")
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
checks=[]
def check(label,condition):
 if not condition:raise AssertionError(label)
 checks.append(label)
check('Prismatic travel uses difference between limits',math.isclose(.4+.1+.3+(.7-.2),1.3))
check('Structural length numerical ratio',math.isclose(6/(8**(1/3)),3))
check('Cartesian elongated equal-volume index',math.isclose((1+1+8)/(8**(1/3)),5))
check('Cartesian equal-travel index',math.isclose((2+2+2)/(8**(1/3)),3))
check('Square determinant absolute value',math.isclose(np.sqrt(np.linalg.det(np.diag([2,-3])@np.diag([2,-3]).T)),6))
Jrect=np.array([[1.,0,0],[0,2,0]])
check('Rectangular full-row-rank manipulability',np.linalg.matrix_rank(Jrect)==2 and math.isclose(np.sqrt(np.linalg.det(Jrect@Jrect.T)),2))
check('Equal manipulability unequal conditioning',math.isclose(np.linalg.det(np.diag([10,.1])),1) and math.isclose(np.linalg.cond(np.diag([10,.1])),100))
J=np.diag([2.,1]);M=np.diag([8.,3]);Ji=np.linalg.inv(J)
check('Mass transformation numerical example',np.allclose(Ji.T@M@Ji,np.diag([2,3])))
check('Ellipse axis intercepts',math.isclose(4*(.5**2),1) and math.isclose(1**2,1))
check('Rotated metric alternative is anisotropic',np.allclose(np.linalg.eigvalsh([[2,1],[1,2]]),[1,3]))
def fk(t1,t2,l1=5.,l2=4.):return np.array([l1*np.cos(t1)+l2*np.cos(t1+t2),l1*np.sin(t1)+l2*np.sin(t1+t2)])
def jac(t1,t2,l1=5.,l2=4.):return np.array([[-l1*np.sin(t1)-l2*np.sin(t1+t2),-l2*np.sin(t1+t2)],[l1*np.cos(t1)+l2*np.cos(t1+t2),l2*np.cos(t1+t2)]])
check('Fixed frame FK at pi/2 and -pi/2',np.allclose(fk(np.pi/2,-np.pi/2),[4,5]))
check('Reachability target hole',math.hypot(.6,.6)<1 and all(1<=math.hypot(*p)<=9 for p in [(1,0),(0,9),(3,4)]))
check('Annulus area',math.isclose(math.pi*(81-1),80*math.pi))
bad_title="plt.title('Articulated Robot\nWorkspace')"
try:compile(bad_title,'literal-slide-title','exec')
except SyntaxError:checks.append('Literal unescaped title newline fails at parse time')
else:raise AssertionError('Literal title unexpectedly parsed')
source_code="""import numpy as np
import matplotlib.pyplot as plt
l1 = 5
l2 = 4
theta1 = np.linspace(-np.pi, np.pi, 200)
theta2 = np.linspace(-np.pi, np.pi, 200)
x_points = []
y_points = []
for t1 in theta1:
    for t2 in theta2:
        x = l1 * np.cos(t1) + l2 * np.cos(t1 + t2)
        y = l1 * np.sin(t1) + l2 * np.sin(t1 + t2)
        x_points.append(x)
        y_points.append(y)
plt.figure(figsize=(8,8))
plt.scatter(x_points, y_points, s=1)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Articulated Robot Workspace')
plt.axis('equal')
plt.grid(True)
plt.show()
"""
ns={};exec(compile(source_code,'slide-573-title-rejoined','exec'),ns)
plt.savefig(R/'audits/W04-L18-author-workspace.png',dpi=110);plt.close('all')
theta=ns['theta1'];radii=np.hypot(ns['x_points'],ns['y_points'])
check('Actual intended source code stores 40000 coordinate pairs',len(ns['x_points'])==len(ns['y_points'])==40000)
check('Inclusive endpoints',math.isclose(theta[0],-math.pi) and math.isclose(theta[-1],math.pi))
check('200-point even grid omits zero',not np.any(theta==0))
check('Closest grid angles',np.allclose(theta[99:101],[-math.pi/199,math.pi/199]))
check('Sampled radial minimum',math.isclose(float(radii.min()),1,abs_tol=1e-12))
expectedmax=math.sqrt(41+40*math.cos(math.pi/199))
check('Sampled radial maximum matches discrete formula below 9',math.isclose(float(radii.max()),expectedmax,abs_tol=1e-12) and radii.max()<9)
check('Zip produces 200 pairs',len(list(zip(ns['theta1'],ns['theta2'])))==200)
check('Periodic endpoint physical duplicate',np.allclose(fk(-np.pi,-np.pi),fk(np.pi,np.pi)))
check('Doubling both counts quadruples storage/evaluations',400*400==4*200*200)
rng=np.random.default_rng(180544)
for k in range(1000):
 t1,t2=rng.uniform(-np.pi,np.pi,2);l1,l2=rng.uniform(.1,10,2);p=fk(t1,t2,l1,l2)
 assert np.isclose(p@p,l1*l1+l2*l2+2*l1*l2*np.cos(t2),atol=1e-10)
 assert abs(l1-l2)-1e-10<=np.linalg.norm(p)<=l1+l2+1e-10
 J=jac(t1,t2,l1,l2)
 assert np.isclose(np.linalg.det(J),l1*l2*np.sin(t2),atol=1e-10)
 h=1e-6
 Jfd=np.column_stack(((fk(t1+h,t2,l1,l2)-fk(t1-h,t2,l1,l2))/(2*h),(fk(t1,t2+h,l1,l2)-fk(t1,t2-h,l1,l2))/(2*h)))
 assert np.allclose(J,Jfd,atol=1e-7)
 travels=rng.uniform(.01,20,3);L=travels.sum();W=travels.prod();s=float(rng.uniform(.01,20))
 assert L/W**(1/3)>=3-1e-12
 assert math.isclose(s*L/(s**3*W)**(1/3),L/W**(1/3),rel_tol=1e-12)
 A=rng.normal(size=(2,2));M=A.T@A+np.eye(2)
 angle=float(rng.uniform(-np.pi,np.pi));rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
 J=rot@np.diag(rng.uniform(.2,3,2));Ji=np.linalg.inv(J);Mx=Ji.T@M@Ji;qd=rng.normal(size=2);xd=J@qd
 assert np.allclose(Mx,Mx.T)
 assert np.all(np.linalg.eigvalsh(Mx)>0)
 assert math.isclose(float(qd@M@qd),float(xd@Mx@xd),rel_tol=1e-11)
 eigvals,eigvecs=np.linalg.eigh(Mx)
 for i in range(2):
  X=eigvecs[:,i]/np.sqrt(eigvals[i]);assert np.isclose(X@Mx@X,1)
check('1000 deterministic randomized FK/Jacobian/structural/inertia cases',True)
summary={'checkKind':'author-side calculations, not independent answer review','authorId':'build_offline_study_interface:L18-author','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'namedChecks':checks,'namedCheckCount':len(checks),'randomizedCases':1000,'randomSeed':180544,'sourceCodeAdjustment':'Rejoined the visibly wrapped ordinary title string onto one line; no mathematical change.','sourceCodeSha256':hashlib.sha256(source_code.encode()).hexdigest(),'sampleCount':len(radii),'sampleMinRadius':float(radii.min()),'sampleMaxRadius':float(radii.max()),'continuousRadii':[1,9],'result':'pass','independentReviewStillRequired':True}
(R/'audits/W04-L18-author-computations.json').write_text(json.dumps(summary,indent=2)+'\n')
(R/'audits/W04-L18-source-code-title-rejoined.py').write_text(source_code)
print(json.dumps({k:summary[k] for k in ['result','namedCheckCount','randomizedCases','sampleMaxRadius','independentReviewStillRequired']}))
