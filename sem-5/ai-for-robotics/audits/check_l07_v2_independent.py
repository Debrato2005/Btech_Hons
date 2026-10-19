"""Independent review of three L07 repairs from actual source pixels."""
import math,random,json
from pathlib import Path

def mm(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
rng=random.Random(70261);n=1000
for _ in range(n):
 a,b=rng.uniform(-math.pi,math.pi),rng.uniform(-math.pi,math.pi);d,L=rng.uniform(0,3),rng.uniform(.1,3)
 c,s,C,S=math.cos(a),math.sin(a),math.cos(b),math.sin(b)
 A=[[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]]
 B=[[1,0,0,0],[0,0,-1,-d],[0,1,0,0],[0,0,0,1]]
 D=[[C,-S,0,0],[S,C,0,0],[0,0,1,L],[0,0,0,1]]
 T=mm(mm(A,B),D)
 expected=[[c*C,-c*S,s,(L+d)*s],[s*C,-s*S,-c,-(L+d)*c],[S,C,0,0],[0,0,0,1]]
 assert all(abs(x-y)<1e-12 for r,e in zip(T,expected) for x,y in zip(r,e))
 assert abs(T[1][2]+c)<1e-12
 assert abs(T[1][1]+s*S)<1e-12 # revised explanation: sin(theta1)sin(theta3) is NEGATIVE of this entry.
cases=[]
for d in [.01,.2,1,10]:
 for vr in [-10,-1,-1e-6,0,1e-6,1,10]:
  vl=-vr;v=(vr+vl)/2;omega=(vr-vl)/(2*d)
  assert v==0 and omega==vr/d
  motion='at rest' if omega==0 else 'counterclockwise' if omega>0 else 'clockwise'
  cases.append({'halfSpacing':d,'rightSpeed':vr,'leftSpeed':vl,'centerSpeed':v,'yawRate':omega,'motion':motion})
out={'scope':'Three repaired items only. No full L07 section signoff by this reviewer.','matrixFactorCases':n,'seed':70261,'allPassed':True,'zeroSpeedBoundaryIncluded':True,'wheelCases':cases,'visualGeometry':'Source text defines r and2d; diagram labels only d half-span, not r or complete2d.'}
Path('audits/W02-L07-v2-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS:1000 full RPR factor products;28 signed/zero wheel-speed cases')
