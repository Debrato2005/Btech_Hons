"""Reviewer-owned source-first independent checks, written before author key reveal."""
import hashlib,json,math,datetime,os
from pathlib import Path
import numpy as np
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,condition,detail=''):
 assert condition,name
 checks.append({'name':name,'passed':True,'detail':detail})
a,b=s.symbols('a b',real=True);l1,l2=s.symbols('l1 l2',positive=True)
p=s.Matrix([l1*s.cos(a)+l2*s.cos(a+b),l1*s.sin(a)+l2*s.sin(a+b)])
J=s.simplify(p.jacobian([a,b]));check('planar determinant',s.simplify(J.det()-l1*l2*s.sin(b))==0,str(J))
check('radius identity',s.trigsimp(p.dot(p)-l1*l1-l2*l2-2*l1*l2*s.cos(b))==0)
check('point at pi/2,-pi/2',p.subs({a:s.pi/2,b:-s.pi/2,l1:5,l2:4})==s.Matrix([4,5]))
for th,rr in [(0,81),(s.pi,1),(-s.pi,1),(s.pi/2,41)]:
 check('radius squared at '+str(th),s.simplify(p.dot(p).subs({l1:5,l2:4,b:th})-rr)==0)
for th in [-s.pi,0,s.pi]:check('boundary singularity '+str(th),s.simplify(J.det().subs(b,th))==0)
check('nonboundary rank',J.subs({a:0,b:s.pi/2,l1:5,l2:4}).rank()==2)
check('inner target unreachable',s.Rational(6,10)**2*2<1)
check('annulus area',s.pi*(81-1)==80*s.pi)
check('full-stroke structural sum',s.Rational(4,10)+s.Rational(1,10)+s.Rational(3,10)+(s.Rational(7,10)-s.Rational(2,10))==s.Rational(13,10))
check('index6overcuberoot8',6/s.real_root(8,3)==3)
check('same-volume travel indices',(sum([1,1,8])/2,sum([2,2,2])/2)==(5,3))
k,L,W=s.symbols('k L W',positive=True)
check('index scale invariance',s.simplify(k*L/(k**3*W)**s.Rational(1,3)-L/W**s.Rational(1,3))==0)
check('ideal spherical benchmark',abs(float((s.Rational(3,4)/s.pi)**s.Rational(1,3))-.6203504908994)<1e-12)
check('square manipulability',s.sqrt((s.diag(2,-3)*s.diag(2,-3).T).det())==6)
R=s.Matrix([[1,0,0],[0,2,0]])
check('rectangular Gram',R*R.T==s.diag(1,4))
check('rectangular rank',R.rank()==2)
check('rectangular w',s.sqrt((R*R.T).det())==2)
A=s.diag(10,s.Rational(1,10));B=s.eye(2)
check('equal products unequal shapes',abs(A.det())==abs(B.det())==1 and A!=B)
check('condition ratios',10/s.Rational(1,10)==100)
JI=s.diag(s.Rational(1,2),1);Mx=JI.T*s.diag(8,3)*JI
check('Cartesian mass',Mx==s.diag(2,3))
check('quadratic intercept',4*s.Rational(1,2)**2==1)
check('isotropic positive scalar',s.diag(3,3).eigenvals()=={s.Integer(3):2})
check('offdiagonal anisotropic',s.Matrix([[2,1],[1,2]]).eigenvals()=={s.Integer(1):1,s.Integer(3):1})
check('zero entry not positive definite',not bool(s.diag(0,3).is_positive_definite))
angles=np.linspace(-np.pi,np.pi,200);x=[];y=[]
for t1 in angles:
 for t2 in angles:
  x.append(5*np.cos(t1)+4*np.cos(t1+t2));y.append(5*np.sin(t1)+4*np.sin(t1+t2))
r=np.hypot(x,y);expected=math.sqrt(41+40*math.cos(math.pi/199))
check('nested count',len(x)==len(y)==40000)
check('zip count',len(list(zip(angles,angles)))==200)
check('zero not sampled',not np.any(angles==0))
check('nearest grid angle',abs(np.min(abs(angles))-math.pi/199)<1e-14)
check('sampled radius max',abs(max(r)-expected)<1e-12,str(expected))
check('sampled radius below continuous',max(r)<9)
check('sampled inner radius',abs(min(r)-1)<1e-12)
check('grid quadrupling',400**2==4*200**2==160000)
check('periodic endpoint equivalence',np.allclose([x[0],y[0]],[x[199],y[199]],atol=1e-12))
try:compile("plt.title('Articulated Robot\nWorkspace')",'<source-title>','exec');bad=False
except SyntaxError:bad=True
check('literal newline parse failure',bad)
compile("plt.title('Articulated Robot Workspace')",'<rejoined-title>','exec')
check('rejoined title parses',True)
os.environ.setdefault('MPLCONFIGDIR','/tmp/robotics-review-mpl');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
plt.figure(figsize=(8,8));plt.scatter(x,y,s=1);plt.xlabel('X');plt.ylabel('Y');plt.title('Articulated Robot Workspace');plt.axis('equal');plt.grid(True)
check('equal axes aspect',plt.gca().get_aspect()==1.0)
plt.savefig(ROOT/'audits/W04-L18-independent-workspace.png',dpi=100);plt.close()
rng=np.random.default_rng(18);maxres=0
for i in range(1000):
 t1,t2=rng.uniform(-math.pi,math.pi,2);xx=5*math.cos(t1)+4*math.cos(t1+t2);yy=5*math.sin(t1)+4*math.sin(t1+t2)
 maxres=max(maxres,abs(xx*xx+yy*yy-(41+40*math.cos(t2))))
 assert 1-1e-12<=math.hypot(xx,yy)<=9+1e-12
check('1000 random radial identities',maxres<1e-12,str(maxres))
record={'reviewerId':'define_robotics_data_contracts:L18-independent-reviewer','authorKeysSeen':False,'performedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'assertionCount':len(checks),'randomCases':1000,'maxSquaredRadiusResidual':maxres,'gridRadiusMax':expected,'sourcePages':[566,567,568,569,570,571,572,573,574],'plotPath':'audits/W04-L18-independent-workspace.png'}
(ROOT/'audits/W04-L18-independent-checks.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['assertionCount','randomCases','maxSquaredRadiusResidual','gridRadiusMax']}))
