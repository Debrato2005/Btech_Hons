"""Independent algebra checks from visually inspected lecture matrices; no author code imported."""
import math, random, json
from pathlib import Path
from datetime import datetime, timezone

def mm(A,B):return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]
def mv(A,v):return [sum(a*b for a,b in zip(row,v)) for row in A]
def tr(A):return list(map(list,zip(*A)))
def rx(t):
 c,s=math.cos(t),math.sin(t);return [[1,0,0],[0,c,-s],[0,s,c]]
def ry(t):
 c,s=math.cos(t),math.sin(t);return [[c,0,s],[0,1,0],[-s,0,c]]
def rz(t):
 c,s=math.cos(t),math.sin(t);return [[c,-s,0],[s,c,0],[0,0,1]]
def T(R,p):return [row+[p[i]] for i,row in enumerate(R)]+[[0,0,0,1]]
def inv(R,p):return T(tr(R),[-x for x in mv(tr(R),p)])
def det(R):return sum((1 if i%2==0 else -1)*R[0][i]*(R[1][(i+1)%3]*R[2][(i+2)%3]-R[1][(i+2)%3]*R[2][(i+1)%3])*(1 if i%2==0 else -1) for i in range(3))
def near(a,b,tol=1e-10):
 if isinstance(a,list):return len(a)==len(b) and all(near(x,y,tol) for x,y in zip(a,b))
 return abs(a-b)<tol
I=[[1,0,0],[0,1,0],[0,0,1]];half=math.pi/2
out={}
out['Rx90_Ry90']=mm(rx(half),ry(half));assert near(out['Rx90_Ry90'],[[0,0,1],[1,0,0],[0,1,0]])
out['Ry90_Rx90']=mm(ry(half),rx(half));assert near(mv(out['Ry90_Rx90'],[0,0,1]),[0,-1,0])
out['quarter_turns']={'Rx_eY':mv(rx(half),[0,1,0]),'Ry_eX':mv(ry(half),[1,0,0]),'Rz_point':mv(rz(half),[2,-1,5])}
assert near(out['quarter_turns']['Rz_point'],[1,2,5])
out['composed_translation']=[row[3] for row in mm(T(rz(half),[1,0,0]),T(I,[2,0,0]))[:3]];assert near(out['composed_translation'],[1,2,0])
out['inverse_translation']=[row[3] for row in inv(rz(half),[2,3,0])[:3]];assert near(out['inverse_translation'],[-3,2,0])
R=rz(math.pi/6);p=[10,5,0]
out['worked_example_point']=mv(T(R,p),[3,7,0,1]);assert near(out['worked_example_point'],[9.098076211353316,12.562177826491071,0,1])
out['worked_example_inverse_origin']=[row[3] for row in inv(R,p)[:3]];assert near(out['worked_example_inverse_origin'],[-11.160254037844387,0.6698729810778055,0])
out['rounded_R_orthogonality_diagonal']=.866**2+.5**2;assert near(out['rounded_R_orthogonality_diagonal'],.999956)
a,b,g=math.pi/3,math.pi/6,math.pi/4
out['fixed_intermediate']=mm(ry(b),rx(g));out['intrinsic_intermediate']=mm(rz(a),ry(b));out['final_fixed']=mm(rz(a),out['fixed_intermediate']);out['final_intrinsic']=mm(out['intrinsic_intermediate'],rx(g));assert near(out['final_fixed'],out['final_intrinsic'])
assert near([r[0] for r in out['fixed_intermediate']],[math.sqrt(3)/2,0,-.5])
assert near([r[1] for r in out['intrinsic_intermediate']],[-math.sqrt(3)/2,.5,0])
assert near(out['final_fixed'][1][2],(math.sqrt(6)-2*math.sqrt(2))/8)
out['inverse_angles_degrees']={'pitch':math.degrees(math.atan2(.5,math.sqrt(3/16+9/16))),'yaw':math.degrees(math.atan2(math.sqrt(3)/2,-.5)),'roll':math.degrees(math.atan2(-1/math.sqrt(2),1/math.sqrt(2)))}
assert near(list(out['inverse_angles_degrees'].values()),[30,120,-45])
rng=random.Random(60239);n=1000
for _ in range(n):
 a,b,g=[rng.uniform(-math.pi,math.pi) for i in range(3)];R=mm(mm(rz(a),ry(b)),rx(g));p=[rng.uniform(-50,50) for i in range(3)];v=[rng.uniform(-20,20) for i in range(3)]
 assert near(mm(tr(R),R),I) and near(det(R),1)
 assert near(mv(inv(R,p),mv(T(R,p),v+[1])),v+[1])
 assert near(mv(T(R,p),v+[0])[:3],mv(R,v))
 beta=math.atan2(-R[2][0],math.hypot(R[0][0],R[1][0]));assert -half<beta<half
 alpha=math.atan2(R[1][0]/math.cos(beta),R[0][0]/math.cos(beta));gamma=math.atan2(R[2][1]/math.cos(beta),R[2][2]/math.cos(beta));assert near(mm(mm(rz(alpha),ry(beta)),rx(gamma)),R)
 # At pitch +90 degrees only alpha-gamma remains.
 d=a-g;sing=[[0,-math.sin(d),math.cos(d)],[0,math.cos(d),math.sin(d)],[-1,0,0]]
 assert near(mm(mm(rz(a),ry(half)),rx(g)),sing)
 assert near(mm(mm(rz(a+.3),ry(half)),rx(g+.3)),sing)
out['random_checks']={'seed':60239,'trials':n,'passed':['SO(3) orthogonality/determinant','rigid inverse point roundtrip','direction translation suppression','principal-angle branch and reconstruction','positive-pitch singular difference and equivalent yaw-roll pairs']}
out['scope']='Independent reimplementation of lecture equations; not execution or verification of a particular installed spatialmath library.'

# New revision checks use independent normalized quaternions to sample target orientations.
# Reconstruct with the fixed-X-Y-Z angles, including both singular branches separately.
def recover_zyx(R):
 beta=math.atan2(-R[2][0],math.hypot(R[0][0],R[1][0]))
 if abs(math.cos(beta))<1e-9:
  return math.atan2(-R[0][1],R[1][1]),beta,0.0
 return math.atan2(R[1][0],R[0][0]),beta,math.atan2(R[2][1],R[2][2])
for _ in range(1000):
 w,x,y,z=[rng.gauss(0,1) for _ in range(4)];norm=math.sqrt(w*w+x*x+y*y+z*z);w,x,y,z=[v/norm for v in(w,x,y,z)]
 Q=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
 aa,bb,gg=recover_zyx(Q);assert near(mm(mm(rz(aa),ry(bb)),rx(gg)),Q)
for beta in[-half,half]:
 for alpha,gamma in[(0,0),(.7,-.8),(math.pi,-math.pi),(-2.3,.9)]:
  R=mm(mm(rz(alpha),ry(beta)),rx(gamma));aa,bb,gg=recover_zyx(R);assert near(mm(mm(rz(aa),ry(bb)),rx(gg)),R)
  if beta>0:assert near(mm(mm(rz(alpha+.4),ry(beta)),rx(gamma+.4)),R)
  else:assert near(mm(mm(rz(alpha+.4),ry(beta)),rx(gamma-.4)),R)
# Normalizing the literal rounded cosine/sine pair repairs norm, not the lost intended angle.
rounded_angle=math.atan2(.5,.866);assert abs(rounded_angle-math.pi/6)>1e-6
out['new_revision_checks']={'independent_quaternion_target_reconstructions':1000,'singular_branch_cases':8,'rounded_normalized_angle_degrees':math.degrees(rounded_angle),'allPassed':True,'scope':'Numerical checks corroborate the mathematical source result; random sampling alone is not a proof of all SO(3).'}

out['checkedAt']=datetime.now(timezone.utc).isoformat()
Path('audits/W02-L06-v2-independent-computations.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS: fixed calculations and 1000 independent rotation/inverse/singularity cases')
