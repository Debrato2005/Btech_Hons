#!/usr/bin/env python3
"""L31 author checks only: independent review still required. No toolbox runtime claim."""
import json,hashlib,ast
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import sympy as s
R=Path(__file__).resolve().parents[1];records=[]
def check(name,condition,detail):
 if not bool(condition):raise AssertionError(name+': '+str(detail))
 records.append(dict(name=name,passed=True,detail=str(detail),independent=False))
E=[8,4];reflect=[F(1,4),F(1,2)];M=[F(1,2),1];L=[e*r for e,r in zip(E,reflect)]
check('spectral-band product and response',L==[2,2] and sum(l*m for l,m in zip(L,M))==3,L)
check('spectral foils',sum(e*m for e,m in zip(E,M))==8 and sum(L)==4 and F(3,2)==1.5,'omit R:8; omit M:4; average:1.5')
check('Bayer counts and missing channels',4*3-4==8 and [2,1,1]==[4//2,4//4,4//4],'2G1R1B;8 missing of12 entries')
check('supplied ADC floor and range',int(np.floor(8*.6))==4 and (1<<3)-1==7,'code4; range0..7; nearest would5')
check('white-balance gain and foils',np.allclose(np.array([.5,.4,.25])*[2,2.5,4],[1,1,1]),'g=(2,2.5,4); alternatives do not equalize')
for gains in ([.5,.4,.25],[4,2.5,2],[2,2,2]):check('white-balance foil '+str(gains),not np.allclose(np.array([.5,.4,.25])*gains,[1,1,1]),np.array([.5,.4,.25])*gains)
check('illustrative gamma',F(1,4)**F(1,2)==.5 and F(1,4)**2==F(1,16),'sqrt(.25)=.5; square=.0625')
color=np.array([[1,0,0,.1],[.2,.8,0,0],[0,0,2,0]])@np.array([.4,.5,.2,1])
check('affine color map',np.allclose(color,[.5,.48,.4]),color)
f=F(50);do=F(200);di=f*do/(do-f)
check('thin-lens real image',di==F(200,3) and 1/do+1/di==1/f,di)
check('thin-lens wrong plus denominator',f*do/(do+f)==40,'40 mm')
check('signed lens magnification',-di/do*30==-10,'m=-1/3; height=-10 mm')
x=s.symbols('x',positive=True);check('infinite-object focal limit',s.limit(50*x/(x-50),x,s.oo)==50,'50 mm')
def project(P,f=.015,rho=(1.,1.),pp=(0.,0.),rot=None,t=None):
 P=np.array(P,float);P=P[:,None] if P.ndim==1 else P
 rot=np.eye(3) if rot is None else np.array(rot,float);t=np.zeros(3) if t is None else np.array(t,float)
 pc=rot.T@(P-t[:,None]);K=np.array([[f/rho[0],0,pp[0]],[0,f/rho[1],pp[1]],[0,0,1.]])
 h=K@pc
 return h[:2]/h[2],pc,K
p,pc,K=project([.2,-.1,2],.02);check('basic metric projection',np.allclose(p[:,0],[.002,-.001]),p)
check('dehomogenization',np.allclose(np.array([.004,-.002])/2,[.002,-.001]),'(.002,-.001) m')
for v,expected in [([2,1,1],True),([-4,-2,-2],True),([6,3,1],False),([2,3,3],False)]:check('homogeneous representative '+str(v),bool(np.allclose(np.array(v[:2])/v[2],[2,1]))==expected,expected)
P=np.array([.3,.4,5]);p,_,_=project(P);check('printed metric output',np.allclose(p[:,0],[.0009,.0012]),p)
check('printed metric unit correction',np.allclose(p[:,0]*1000,[.9,1.2]) and not np.allclose(p[:,0]*1000,[1.5,2]),'correct(.9,1.2) mm; arrow wrong')
p,pc,_=project(P,t=[-.5,0,0]);check('camera-left metric output',np.allclose(pc[:,0],[.8,.4,5]) and np.allclose(p[:,0],[.0024,.0012]),p)
wrong,_,_=project(P,t=[.5,0,0]);check('camera-left sign foil',np.allclose(wrong[:,0],[-.0006,.0012]),wrong)
rot=np.array([[0,-1,0],[1,0,0],[0,0,1]]);t=np.array([1,2,0]);point=np.array([1,3,4]);pc=rot.T@(point-t)
check('inverse rigid pose',np.allclose(pc,[1,0,4]),pc)
check('forward rotation foil',np.allclose(rot@(point-t),[-1,0,4]),'(-1,0,4)')
check('rotate before subtract foil',np.allclose(rot.T@point-t,[2,-3,4]),'(2,-3,4)')
check('add origin foil',np.allclose(rot.T@(point+t),[5,-2,4]),'(5,-2,4)')
check('sensor dimensions',1280*F(1,100)==F(64,5) and 1024*F(1,100)==F(256,25),'12.8×10.24 mm')
check('unequal-pitch pixel map',np.allclose([1/.01+320,-.5/.02+240],[420,215]),'(420,215)')
_,_,K=project([1,1,1],.015,(1e-5,2e-5),(640,512));check('unequal-pitch K',np.allclose(K,[[1500,0,640],[0,750,512],[0,0,1]]),K)
check('explicit nearest-index rule',np.array_equal(np.rint([100.4,200.6]),[100,201]),'(100,201), no half ties')
p,_,K=project(P,.015,(1e-5,1e-5),(640,512));check('printed pixel output',np.allclose(p[:,0],[730,632]),p)
pwrong,_,_=project(P,.015,(1e-6,1e-6),(640,512));check('factor-ten pixel foil',np.allclose(pwrong[:,0],[1540,1712]),pwrong)
pts=np.column_stack([[0,0,10],[10,10,10],[.3,.4,5]]);check('exact column_stack layout',pts.shape==(3,3) and np.allclose(pts[:,1],[10,10,10]),pts)
p,pc,_=project(pts,.015,(1e-5,1e-5),(640,512));mask=(pc[2]>0)&(p[0]>=0)&(p[0]<1280)&(p[1]>=0)&(p[1]<1024)
check('three printed point outputs',np.allclose(p,[[640,2140,730],[512,2012,632]]),p)
check('printed visibility mask',np.array_equal(mask,[True,False,True]),mask)
coords=[-.1,0,.1];grid=np.array([[x,y,1] for x in coords for y in coords]).T
pg,_,_=project(grid,.015,(1e-5,1e-5),(640,512));pm,_,_=project(grid,.015,(1e-5,1e-5),(640,512),t=[-.25,0,0])
check('grid coordinates and spacing',np.allclose(np.unique(pg[0]),[490,640,790]) and np.allclose(np.unique(pg[1]),[362,512,662]),pg)
check('grid translated plot',np.allclose(pm-pg,np.tile([[375],[0]],(1,9))),pm)
check('cube depth-dependent shifts',round(375/.9,2)==416.67 and round(375/1.1,2)==340.91,'416.67,340.91 pixels')
tau=s.symbols('tau',nonnegative=True);line1=s.Matrix([tau/(1+tau),0]);line2=s.Matrix([tau/(1+tau),1/(1+tau)])
check('coplanar parallel world lines',s.Matrix([0,1,0]).cross(s.Matrix([1,0,1]))==s.Matrix([1,0,-1]),'both lines lie in plane X−Z=−1')
check('counterexample vanishing limit',[s.limit(z,tau,s.oo) for z in line1]==[1,0] and [s.limit(z,tau,s.oo) for z in line2]==[1,0],'both→(1,0)')
check('counterexample distinct image lines',s.simplify(sum(line2)-1)==0 and line1[1]==0,'line1 y=0; line2 x+y=1')
check('vanishing point in pixels',np.allclose([.02*2/4/1e-5+640,.02*1/4/1e-5+512],[1640,1012]),'(1640,1012)')
check('vanishing foils',np.allclose([.02*2/1e-5+640,.02*1/1e-5+512],[4640,2512]),'omit depth direction: (4640,2512)')
p,pc,K=project(point,.02,(1e-5,2e-5),(320,240),rot,t);check('full pose/K/bounds synthesis',np.allclose(pc[:,0],[1,0,4]) and np.allclose(p[:,0],[820,240]) and p[0,0]>=800,'(1,0,4) m→(820,240), outside')
# Mathematical stochastic consistency, not a replacement for toolbox execution.
rng=np.random.default_rng(3107)
for i in range(500):
 angle=rng.uniform(-np.pi,np.pi);co,si=np.cos(angle),np.sin(angle);rot=np.array([[co,-si,0],[si,co,0],[0,0,1.]])
 t=rng.normal(size=3);pc=np.r_[rng.normal(size=2),rng.uniform(.1,20)];pw=rot@pc+t
 f=rng.uniform(.005,.1);rho=rng.uniform(2e-6,30e-6,size=2);pp=rng.uniform(0,1000,size=2)
 p,got,K=project(pw,f,rho,pp,rot,t)
 T=np.eye(4);T[:3,:3]=rot;T[:3,3]=t;h=K@np.eye(3,4)@np.linalg.inv(T)@np.r_[pw,1.]
 assert np.allclose(got[:,0],pc) and np.allclose(p[:,0],h[:2]/h[2])
 scale=rng.uniform(.1,10);h2=K@(pc*scale);assert np.allclose(p[:,0],h2[:2]/h2[2])
 delta=rng.uniform(-.5,.5);base,_,_=project(pc,f,rho,pp);moved,_,_=project(pc,f,rho,pp,t=[delta,0,0]);assert np.allclose((moved-base)[:,0],[-f/rho[0]*delta/pc[2],0])
records.append(dict(name='500 random pose/projection/scale/translation cases',passed=True,cases=500,assertions=2000,independent=False))
for path in ['audits/source-code-W07-L31-as-printed.py','scripts/reproduce_W07_L31_toolbox.py']:
 ast.parse((R/path).read_text());records.append(dict(name='Syntax parsing only: '+path,passed=True,independent=False,notExecuted=True))
report=dict(batchId='W07-L31',role='author-checks-not-independent-review',checks=records,toolboxRuntimeExecuted=False,environmentAudit='audits/L31-execution-environment.json',randomCases=500)
(R/'audits/W07-L31-author-computations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('AUTHOR CHECKS',len(records),'passed; 500 random cases; toolbox not executed')
