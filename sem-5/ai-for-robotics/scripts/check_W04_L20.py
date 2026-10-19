#!/usr/bin/env python3
"""Deterministic author calculations for L20. These are not an independent review."""
import math,random
from fractions import Fraction as F
import sympy as s
CHECKS=[]
def record(name,claim,ok=True,**extra):
 assert bool(ok),name
 CHECKS.append(dict(name=name,result='pass',method='author calculation, not independent review',claim=claim,**extra))
def near(a,b,tol=1e-9):return abs(float(a)-float(b))<tol
l1,l2,d1,d3=s.symbols('l1 l2 d1 d3',real=True)
t1,t2,t4=s.symbols('theta1 theta2 theta4',real=True)
def R(a):return s.Matrix([[s.cos(a),-s.sin(a),0],[s.sin(a),s.cos(a),0],[0,0,1]])
def H(a,p):return R(a).row_join(s.Matrix(p)).col_join(s.Matrix([[0,0,0,1]]))
A1=H(t1,[l1*s.cos(t1),l1*s.sin(t1),d1]);A2=H(t2,[l2*s.cos(t2),l2*s.sin(t2),0]);A3=H(0,[0,0,-d3]);A4=H(t4,[0,0,0])
T=s.simplify(A1*A2*A3*A4)
expected=H(t1+t2+t4,[l1*s.cos(t1)+l2*s.cos(t1+t2),l1*s.sin(t1)+l2*s.sin(t1+t2),d1-d3])
record('printed matrix product','The four printed615 transforms multiply to the stated horizontal pose, downward extension and summed yaw.',s.simplify(T-expected)==s.zeros(4))
# Explicit modified-DH reading: Tx(a_prev)Rz(theta)Tz(d), all alpha=0.
B1=H(t1,[0,0,d1]);B2=H(t2,[l1,0,0]);B3=H(0,[l2,0,d3]);B4=A4
BT=s.simplify(B1*B2*B3*B4)
record('modified table versus FK','The explicit modified-DH table gives the same horizontal position but heightd1+d3; its first transform has no horizontal translation.',all(s.simplify(BT[i,3]-expected[i,3])==0 for i in(0,1)) and BT[2,3]==d1+d3 and B1[0,3]==0)
pose=s.Matrix([expected[0,3],expected[1,3],d1-d3,t1+t2+t4]);q=s.Matrix([t1,t2,d3,t4]);J=pose.jacobian(q)
JJ=s.Matrix([[-l1*s.sin(t1)-l2*s.sin(t1+t2),-l2*s.sin(t1+t2),0,0],[l1*s.cos(t1)+l2*s.cos(t1+t2),l2*s.cos(t1+t2),0,0],[0,0,-1,0],[1,1,0,1]])
record('analytic Jacobian','Differentiating FK produces every printed Jacobian entry.',s.simplify(J-JJ)==s.zeros(4))
record('full determinant sign','For task and joint orders on619, detJ=−l1l2sinθ2.',s.simplify(J.det()+l1*l2*s.sin(t2))==0)
record('straight-arm missing direction','Atθ1=θ2=0 the x row vanishes, while y,z,yaw remain controllable for positive links.',J.subs({t1:0,t2:0})[0,:]==s.zeros(1,4) and J.subs({t1:0,t2:0,l1:2,l2:1}).rank()==3)
val=J.subs({t1:0,t2:s.pi/2,l1:s.Rational(1,4),l2:s.Rational(1,5)})*s.Matrix([1,2,s.Rational(3,100),-3])
record('Jacobian numerical velocity','Task rates are(−0.60,0.25,−0.03,0) in m/s andrad/s.',val==s.Matrix([-s.Rational(3,5),s.Rational(1,4),-s.Rational(3,100),0]))
Tv=T.subs({t1:0,t2:s.pi/2,t4:-s.pi/2,l1:250,l2:200,d1:400,d3:80})
record('full transform numerical pose','The specified0°,90°,−90° case has identity orientation and(250,200,320)mm translation.',Tv==s.Matrix([[1,0,0,250],[0,1,0,200],[0,0,1,320],[0,0,0,1]]))
x=250*math.cos(math.pi/4)+200*math.cos(5*math.pi/12);y=250*math.sin(math.pi/4)+200*math.sin(5*math.pi/12)
record('printed FK arithmetic discrepancy','Exact evaluatedx=228.54050431714103,y=369.9618605544505mm; round0.1mm to228.5,370.0.',round(x,1)==228.5 and round(y,1)==370.0,values={'xMm':x,'yMm':y})
record('height yaw and incremental stroke','400−80=320mm;45+30+15=90°; extra20mm extension lowers height20mm.',400-80==320 and 45+30+15==90 and (400-100)-(400-80)==-20)
D=F(250**2+150**2-250**2-200**2,2*250*200)
record('IK cosine-law argument','D=−7/40=−0.175 and target radius≈291.5476mm.',D==F(-7,40) and near(math.hypot(250,150),291.547594742265,1e-9))
branches=[]
for sign in(1,-1):
 b2=sign*math.acos(float(D));b1=math.atan2(150,250)-math.atan2(200*math.sin(b2),250+200*math.cos(b2));b4=math.pi/2-b1-b2
 xx=250*math.cos(b1)+200*math.cos(b1+b2);yy=250*math.sin(b1)+200*math.sin(b1+b2)
 assert near(xx,250) and near(yy,150) and near(b1+b2+b4,math.pi/2)
 branches.append([math.degrees(a) for a in(b1,b2,b4)])
record('both IK branch roundtrips','Positive and negative elbow solutions independently reconstruct the target and yaw.',True,anglesDegrees=branches)
record('workspace radii and volume','250/200mm links give50/450mm ideal radii and0.04πm³ for0.2m stroke.',F(45,100)**2-F(5,100)**2==F(1,5) and F(1,5)*F(1,5)==F(1,25))
rmin=math.sqrt(250**2+200**2+2*250*200*math.cos(math.radians(145)))
record('elbow-limited inner radius','The±145° elbow limit yields143.4740240290932mm, not50mm.',near(rmin,143.4740240290932),radiusMm=rmin)
L,a=s.symbols('L a',positive=True)
area=4*s.pi*a*(L-a)
record('fixed-sum area maximum','Area derivative vanishes at equal links and second derivative is negative.',s.diff(area,a).subs(a,L/2)==0 and s.diff(area,a,2)==-8*s.pi)
# Recover mass matrix from stated simplified kinetic energy.
m1,m2,m3,m4,I1,I2,I4=s.symbols('m1 m2 m3 m4 I1 I2 I4',positive=True)
w1,w2,v3,w4=s.symbols('w1 w2 v3 w4',real=True);qd=s.Matrix([w1,w2,v3,w4])
p1=s.Matrix([l1*s.cos(t1)/2,l1*s.sin(t1)/2]);p2=s.Matrix([l1*s.cos(t1)+l2*s.cos(t1+t2)/2,l1*s.sin(t1)+l2*s.sin(t1+t2)/2]);p3=pose[:2,0]
v1=p1.jacobian(q)*qd;v2=p2.jacobian(q)*qd;vxy=p3.jacobian(q)*qd
KE=(m1*v1.dot(v1)+m2*v2.dot(v2)+(m3+m4)*(vxy.dot(vxy)+v3**2)+I1*w1**2+I2*(w1+w2)**2+I4*(w1+w2+w4)**2)/2
M=s.simplify(s.hessian(KE,qd));m34=m3+m4
M11=I1+I2+I4+m1*(l1/2)**2+m2*(l1**2+(l2/2)**2+l1*l2*s.cos(t2))+m34*(l1**2+l2**2+2*l1*l2*s.cos(t2))
M12=I2+I4+m2*((l2/2)**2+l1*l2*s.cos(t2)/2)+m34*(l2**2+l1*l2*s.cos(t2));M22=I2+I4+m2*(l2/2)**2+m34*l2**2
ME=s.Matrix([[M11,M12,0,I4],[M12,M22,0,I4],[0,0,m34,0],[I4,I4,0,I4]])
record('mass matrix energy derivation','All16 entries of621 equal the Hessian of the explicitly scoped kinetic energy.',s.simplify(M-ME)==s.zeros(4))
V=s.zeros(4,1)
for i in range(4):
 for j in range(4):
  for k in range(4):V[i]+=(s.diff(M[i,j],q[k])+s.diff(M[i,k],q[j])-s.diff(M[j,k],q[i]))*qd[j]*qd[k]/2
h=l1*l2*(m2/2+m3+m4)*s.sin(t2);VE=s.Matrix([-h*(2*w1*w2+w2**2),h*w1**2,0,0])
record('Coriolis from Christoffel symbols','Every velocity-dependent term on622 follows from621 mass matrix under the same model.',s.simplify(V-VE)==s.zeros(4,1))
g=s.symbols('g',positive=True);U=m34*g*(d1-d3)
record('gravity gradient sign','The potential gradient in downward-positive d3 is−(m3+m4)g.',s.simplify(s.Matrix([s.diff(U,x) for x in q])-s.Matrix([0,0,-m34*g,0]))==s.zeros(4,1))
subs={m1:1,m2:2,m3:s.Rational(1,2),m4:s.Rational(1,2),l1:s.Rational(1,5),l2:s.Rational(4,25),I1:s.Rational(1,100),I2:s.Rational(1,50),I4:s.Rational(1,200),t2:s.pi/2}
MN=ME.subs(subs)
record('mass entries at right elbow','M11=0.2034;M12=M22=0.0634;M33=1;M44=0.005.',MN[0,0]==s.Rational(1017,5000) and MN[0,1]==s.Rational(317,5000) and MN[1,1]==s.Rational(317,5000) and MN[2,2]==1 and MN[3,3]==s.Rational(1,200))
MN0=ME.subs({**subs,t2:0})
record('mass-entry distractor audit','At zero elbow, M11=0.3314 andM12=0.1274, explaining two plausible angle-confusion options.',MN0[0,0]==s.Rational(1657,5000) and MN0[0,1]==s.Rational(637,5000))
record('wrist coupling and prismatic mass','Wrist torque0.005(1+2+3)=0.030Nm; translating mass coefficient is sum1.2kg.',F(5,1000)*6==F(3,100))
record('velocity-term numerical values','h=0.064 andrates1,2giveV1=−0.512,V2=0.064Nm.',h.subs(subs)==s.Rational(8,125) and VE.subs({**subs,w1:1,w2:2})==s.Matrix([-s.Rational(64,125),s.Rational(8,125),0,0]))
record('static hold sign','A1.2kg translating mass requires−11.772N generalized hold force.',-F(12,10)*F(981,100)==-F(2943,250))
record('stated trajectory impossible','WithT0.38s andacceleration300deg/s², max rest-to-rest displacement is10.83deg.',F(300)*F(38,100)**2/4==F(1083,100))
Tmin=2*math.sqrt(90/300);peak=math.sqrt(90*300)
record('minimum-time triangular move','T=1.095445115s andpeak164.316767deg/s<400.',near(Tmin,1.0954451150103321) and peak<400,values={'timeS':Tmin,'peakDegreesPerS':peak})
ta=F(38,100)-F(90,400);cruise=F(38,100)-2*ta;acc=F(400)/ta
record('explicitly revised trapezoid','Ramp0.155s,cruise0.07s,acceleration80000/31≈2580.645deg/s² integrates to90deg.',ta==F(31,200) and cruise==F(7,100) and acc==F(80000,31) and F(400)*(ta+cruise)==90)
record('specification and stiffness arithmetic','250/20=12.5;100N atK>200N/μm givesδ<0.5μm.',F(250,20)==F(25,2) and F(100,200)==F(1,2))
record('ideal gear numerical relation','100:1 maps3000rpm,0.5Nm to30rpm,50Nm.',F(3000,100)==30 and F(1,2)*100==50)
record('screw numerical distractors','Efficiency-multiplication option0.1512Nm, missing2π option1.0526Nm and lossless option0.1592Nm differ from required0.1675Nm.',round(100*.01*.95/(2*math.pi),4)==.1512 and round(100*.01/.95,4)==1.0526 and round(100*.01/(2*math.pi),4)==.1592)
record('simultaneous wrist shaft power','3Nm at2000rpm gives200πW≈628.3185W, not the separate final-design100W rating.',near(3*2000*2*math.pi/60,200*math.pi))
record('screw turns and efficiency','130mm/10mm-per-rev=13rev;100N with0.01m lead andη0.95 needs0.167531519Nm.',F(130,10)==13 and near(100*.01/(2*math.pi*.95),0.16753151904410036))
record('payload scenarios and capacity ratio','Literal0.5g+0.8kg=0.8005kg; table0.5kg+0.8kg=1.3kg; capacity ratio30/13.',F(5,10000)+F(8,10)==F(1601,2000) and F(5,10)+F(8,10)==F(13,10) and F(3)/F(13,10)==F(30,13))
record('stroke margin discrepancy','Required130,selected180 gives5/13≈38.4615% extra;20% would select156.',F(180-130,130)==F(5,13) and F(130)*F(6,5)==156)
record('encoder resolution','20bits means1048576 codes and0.00034332275390625deg/code.',2**20==1048576 and F(360,2**20)==F(45,131072))
record('selected workspace and box area','200/160mm give40/360mm;40×30 box with3mm wall gives34×24void and384mm²material.',abs(200-160)==40 and 200+160==360 and 40*30-34*24==384)
record('wrist compensation','45−150=−105deg lies within±180deg.',45-150==-105 and -180<=-105<=180)
record('angular acceleration conversion','300deg/s²=5π/3rad/s²;52.4rad/s²is about3002.3deg/s².',s.Rational(300)*s.pi/180==5*s.pi/3,wrongAnnotationDegreesPerS2=52.4*180/math.pi)
record('load-only motor torques','Literal52.4 givesJ1=0.022008Nm andJ2=0.01179Nm after ideal reduction.',F(42,1000)*F(524,10)/100==F(2751,125000) and F(18,1000)*F(524,10)/80==F(1179,100000))
record('upward acceleration force','1.3kg accelerated upward40m/s² requires64.753N, not18N.',F(13,10)*(40+F(981,100))==F(64753,1000))
record('wrist isolated torque and lossy gearing','0.0008×200=0.16Nm;0.32/0.16=2;8/(0.8×80)=0.125Nm.',F(8,10000)*200==F(16,100) and F(32,100)/F(16,100)==2 and F(8)/(F(8,10)*80)==F(1,8))
rows=[620,420,380,180,1200,850,320,420,350,1800,4*220,480]
record('BOM first page','Every printed extended line sums to7900USD.',sum(rows)==7900,extendedLines=rows)
record('BOM category subtotals','Actuation1600,Transmission2370,Controller2680,Sensing1130USD.',sum(rows[:4])==1600 and sum(rows[4:7])==2370 and rows[9]+rows[10]==2680 and 650+4*120==1130)
literal=sum(rows)+650+4*120+180+420;unique=literal-420
record('BOM duplicate reconciliation','Literal two-page total9630; one-system total9210;710 above8500target.',literal==9630 and unique==9210 and unique-8500==710)
record('BOM target reduction and shares','Target reduction43/85≈50.5882%;printed shares sum100 but exact categories differ.',F(8500-4200,8500)==F(43,85) and sum([32,28,24,10,6])==100 and F(1600,9210)!=F(24,100))
# Reproducible random-domain checks, not extra question/coverage counts.
rng=random.Random(20261019620)
for i in range(500):
 a=rng.uniform(.05,.5);b=rng.uniform(.05,.5);u=rng.uniform(-2,2);v=rng.choice([-1,1])*rng.uniform(.1,2.4);yaw=rng.uniform(-2,2)
 xx=a*math.cos(u)+b*math.cos(u+v);yy=a*math.sin(u)+b*math.sin(u+v)
 dd=(xx*xx+yy*yy-a*a-b*b)/(2*a*b)
 assert -1<dd<1
 for sign in(-1,1):
  vv=sign*math.acos(dd);uu=math.atan2(yy,xx)-math.atan2(b*math.sin(vv),a+b*math.cos(vv));ww=yaw-uu-vv
  assert near(a*math.cos(uu)+b*math.cos(uu+vv),xx,1e-10)
  assert near(a*math.sin(uu)+b*math.sin(uu+vv),yy,1e-10)
  assert near(uu+vv+ww,yaw,1e-10)
 assert abs(a-b)-1e-12<=math.hypot(xx,yy)<=a+b+1e-12
record('500 deterministic FK/IK and envelope cases','Both algebraic elbow branches roundtrip500 nonsingular reachable targets; all radii satisfy the ideal annulus.',True,seed=20261019620,cases=500,branchRoundtrips=1000)
if __name__=='__main__':
 import json
 from pathlib import Path
 root=Path(__file__).resolve().parents[1]
 (root/'audits/author-checks-W04-L20.json').write_text(json.dumps(CHECKS,ensure_ascii=False,indent=2)+'\n')
 print(f'{len(CHECKS)} author checks passed, including500 deterministic cases.')
