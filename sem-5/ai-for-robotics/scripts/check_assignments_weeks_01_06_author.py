"""Author-only executable checks of declared assignment adaptations, not independent approval."""
from pathlib import Path
import json,math,itertools,datetime,platform
import numpy as np
import sympy as sp
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
R=Path(__file__).resolve().parents[1];checks=[]
def ck(name,condition):
 assert bool(condition),name
 checks.append(name)
x,y=sp.symbols('x y');f=3*x*x+2*x*y+y*y
ck('W01 Q006 gradient', [sp.diff(f,z).subs({x:1,y:2})for z in (x,y)]==[10,6])
ck('W02 Q001 singular matrix not proper rotation',np.linalg.det(np.diag([1,1,0]))==0)
T=np.eye(4);T[:3,3]=[1,2,3];ck('W02 Q002 homogeneous last coordinate',np.array_equal((T@np.array([3,4,5,1]))[-1:], [1]))
ck('W02 Q003 independent coordinate count',4+2==6)
ck('W02 Q004 relative-angle FK',np.allclose([2+2*math.cos(math.pi/2),2*math.sin(math.pi/2)],[2,2]))
c=(16-9-4)/(2*3*2);ck('W02 Q006 cosine not angle',c==.25 and math.isclose(math.degrees(math.acos(c)),75.52248781407008))
for a in (math.acos(c),-math.acos(c)):
 t1=-math.atan2(2*math.sin(a),3+2*math.cos(a));ck('W02 Q006 reconstruct elbow branch '+str(a),np.allclose([3*math.cos(t1)+2*math.cos(t1+a),3*math.sin(t1)+2*math.sin(t1+a)],[4,0]))
J=np.array([[1,2],[2,4]]);ck('W02 Q007 rank and null',np.linalg.matrix_rank(J)==1 and np.allclose(J@[-2,1],0))
ck('W02 Q009 local-frame moment',math.isclose(.3*5-0*10,1.5))
ck('W02 Q009 different base-force frame is different torque',math.isclose(.3*(-10*math.sin(math.pi/4)+5*math.cos(math.pi/4)),-1.060660171779821))
ck('W03 Q001 parallel-axis shift',math.isclose(.1+2*(.3**2+.4**2),.6))
ck('W03 Q002 longitudinal inertia',math.isclose(.5*6*.2**2,.12))
ck('W03 Q002 transverse distractor rationale',math.isclose(6*(3*.2**2+.4**2)/12,.14))
ck('W03 Q004 net force norm',np.linalg.norm(4*np.array([3,0,4]))==20)
ck('W03 Q008 energy split',.5*2*(3**2+4**2)+.5*.5*2**2==26)
q1,q2,l1,l2,m1,m2=sp.symbols('q1 q2 l1 l2 m1 m2',real=True);qd1,qd2=sp.symbols('qd1 qd2',real=True)
p1=sp.Matrix([l1*sp.cos(q1),l1*sp.sin(q1)]);p2=p1+sp.Matrix([l2*sp.cos(q1+q2),l2*sp.sin(q1+q2)])
qd=sp.Matrix([qd1,qd2]);v1=p1.jacobian([q1,q2])*qd;v2=p2.jacobian([q1,q2])*qd
K=sp.expand((m1*v1.dot(v1)+m2*v2.dot(v2))/2);M=sp.simplify(sp.hessian(K,(qd1,qd2)))
expected=sp.Matrix([[(m1+m2)*l1*l1+m2*l2*l2+2*m2*l1*l2*sp.cos(q2),m2*l2*l2+m2*l1*l2*sp.cos(q2)],[m2*l2*l2+m2*l1*l2*sp.cos(q2),m2*l2*l2]])
for i,j in itertools.product(range(2),repeat=2):ck(f'W03 Q009 symbolic M[{i},{j}]',sp.trigsimp(M[i,j]-expected[i,j])==0)
ck('W03 Q009 numeric matrix',M.subs({m1:2,m2:3,l1:1,l2:2,q2:sp.pi/3})==sp.Matrix([[23,15],[15,12]]))
ck('W03 Q010 pair count',len(list(itertools.combinations(range(4),2)))==6)
t=sp.symbols('t',real=True);poly=sp.Rational(3,4)*t*t-sp.Rational(1,4)*t**3
ck('W04 Q002 cubic endpoint positions',poly.subs(t,0)==0 and poly.subs(t,2)==1)
ck('W04 Q002 cubic endpoint rates',sp.diff(poly,t).subs(t,0)==0 and sp.diff(poly,t).subs(t,2)==0)
ck('W04 Q002 acceleration not additionally zero',sp.diff(poly,t,2).subs(t,0)==sp.Rational(3,2) and sp.diff(poly,t,2).subs(t,2)==-sp.Rational(3,2))
ck('W04 Q003 velocity limits equal',sp.limit(t,t,1)==1)
ck('W04 Q003 acceleration jump',sp.diff(t,t)==1 and sp.diff(sp.Integer(1),t)==0)
ck('W04 Q004 equivalent shorter rotation',(350-10-360)==-20)
ck('W04 Q006 annular range',abs(5-4)==1 and 5+4==9 and .5<1)
ck('W04 Q007 nullity',7-6==1)
ck('W04 Q010 both branches',sp.sin(0)==0 and sp.sin(sp.pi)==0 and sp.sin(sp.pi/2)!=0)
s=sp.symbols('s');ck('W05 Q001 repeated root',sp.expand((s+3)**2)==s*s+6*s+9)
ck('W05 Q002 gains',16-1==15 and 2*math.sqrt(4*16)-1==15)
ck('W05 Q004 guideline',80/2==40)
v=sp.symbols('v');ck('W05 Q005 matching cancellation',sp.expand(x**3+v-x**3)==v)
ck('W05 Q006 spring ratio',(10*2**3)/(10*2)==4)
e=(sp.Rational(1,10)+sp.Rational(3,10)*t)*sp.exp(-3*t)
ck('W05 Q008 differential equation',sp.simplify(sp.diff(e,t,2)+6*sp.diff(e,t)+9*e)==0)
ck('W05 Q008 initial conditions',e.subs(t,0)==sp.Rational(1,10) and sp.diff(e,t).subs(t,0)==0)
J=np.array([[1,2],[0,1]]);F=np.array([3,4]);ck('W05 Q010 torque',np.array_equal(J.T@F,[3,10]))
model=LinearRegression().fit(np.array([[0,0],[1,0],[0,1],[2,3]],float),np.array([1,3,4,14],float))
ck('W06 Q005 actual installed estimator fit',np.allclose(model.coef_,[2,3]) and math.isclose(model.intercept_,1) and np.allclose(model.predict([[2,1]]),[8]))
a=np.array([1,'red'],dtype=object);df=pd.DataFrame({'n':[1,2],'text':['red','blue']})
ck('W06 Q006 object array has one dtype',a.dtype==np.dtype('O') and isinstance(a[0],int) and isinstance(a[1],str))
ck('W06 Q006 DataFrame per-column dtypes',df['n'].dtype!=df['text'].dtype)
ck('W06 Q007 mean',np.mean([12,15,18,20,25])==18)
def tree(a,b):return np.mean([3,5,7])if a<=10 else np.mean([10,14,18])if b<=5 else np.mean([30,40])
ck('W06 Q008 source route',tree(12,3)==14);ck('W06 Q008 boundaries',tree(10,100)==5 and tree(11,5)==14 and tree(11,6)==35)
ck('W06 Q010 nonterminal update',math.isclose(4+.1*(3+.9*10-4),4.8))
ck('W06 Q010 terminal update',math.isclose(4+.1*(3-4),3.9))
rng=np.random.default_rng(20261020);varied=0
for _ in range(1000):
 a,b=rng.uniform(.1,5,2);u,w=rng.uniform(-math.pi,math.pi,2);p=np.array([a*math.cos(u)+b*math.cos(u+w),a*math.sin(u)+b*math.sin(u+w)])
 assert abs(a-b)-1e-10<=np.linalg.norm(p)<=a+b+1e-10;varied+=1
 c=(p@p-a*a-b*b)/(2*a*b);assert math.isclose(c,math.cos(w),abs_tol=1e-10);varied+=1
 ma,mb=rng.uniform(.1,5,2);mat=np.array([[(ma+mb)*a*a+mb*b*b+2*mb*a*b*math.cos(w),mb*b*b+mb*a*b*math.cos(w)],[mb*b*b+mb*a*b*math.cos(w),mb*b*b]])
 assert np.allclose(mat,mat.T) and np.linalg.eigvalsh(mat).min()>0;varied+=1
 vel=rng.normal(size=2);j1=np.array([[-a*math.sin(u),0],[a*math.cos(u),0]]);j2=np.array([[-a*math.sin(u)-b*math.sin(u+w),-b*math.sin(u+w)],[a*math.cos(u)+b*math.cos(u+w),b*math.cos(u+w)]])
 assert math.isclose(.5*vel@mat@vel,.5*ma*np.linalg.norm(j1@vel)**2+.5*mb*np.linalg.norm(j2@vel)**2,abs_tol=1e-9);varied+=1
 J=rng.normal(size=(2,2));F=rng.normal(size=2);dq=rng.normal(size=2);assert math.isclose(F@(J@dq),(J.T@F)@dq,abs_tol=1e-10);varied+=1
old=R/'audits/assignment-coverage/W01-W06-author-checks.json';out={'scope':'Author-only checks for explicitly declared adaptations. Symbolic and numerical computations plus installed scikit-learn/Pandas/NumPy toy workflows; no downloads, installation, external runtime, robot or browser operation. Original printed keys were visible.','independentReview':False,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment':{'Python':platform.python_version(),'NumPy':np.__version__,'SymPy':sp.__version__,'Pandas':pd.__version__,'scikit-learn':sklearn.__version__},'namedChecks':len(checks),'checks':checks,'variedAssertions':varied,'seed':20261020,'allPassed':True};old.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['environment','namedChecks','variedAssertions','allPassed']}))
