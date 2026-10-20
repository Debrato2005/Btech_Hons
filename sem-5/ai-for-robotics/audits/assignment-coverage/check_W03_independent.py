"""Independent, default-standard-library checks. No author scripts or external runtime."""
import math,random,json,pathlib,datetime,itertools
R=pathlib.Path(__file__).resolve().parents[2];rng=random.Random(2026102003)
def near(a,b):assert math.isclose(a,b,rel_tol=2e-10,abs_tol=2e-10),(a,b)
def matrix(m1,m2,l1,l2,q2):
 c=math.cos(q2);return [[(m1+m2)*l1*l1+m2*l2*l2+2*m2*l1*l2*c,m2*l2*l2+m2*l1*l2*c],[m2*l2*l2+m2*l1*l2*c,m2*l2*l2]]
near(.1+2*(.3**2+.4**2),.6);near(.5*6*.2**2,.12);near(4*math.sqrt(3**2+4**2),20);near(.5*2*25+.5*.5*4,26)
M=matrix(2,3,1,2,math.pi/3)
for row,expected in zip(M,[[23,15],[15,12]]):
 for a,b in zip(row,expected):near(a,b)
assert list(itertools.combinations(range(4),2))==[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
for _ in range(1000):
 m1,m2,l1,l2=[rng.uniform(.1,10)for _ in range(4)];q1,q2,w1,w2=[rng.uniform(-4,4)for _ in range(4)];M=matrix(m1,m2,l1,l2,q2)
 v1=(-l1*math.sin(q1)*w1,l1*math.cos(q1)*w1)
 v2=(v1[0]-l2*math.sin(q1+q2)*(w1+w2),v1[1]+l2*math.cos(q1+q2)*(w1+w2))
 kpoints=.5*m1*sum(x*x for x in v1)+.5*m2*sum(x*x for x in v2)
 kmatrix=.5*(M[0][0]*w1*w1+2*M[0][1]*w1*w2+M[1][1]*w2*w2)
 near(kpoints,kmatrix);assert M[0][0]>0 and M[0][0]*M[1][1]-M[0][1]**2>0
 # A centered symmetric point cloud independently checks the parallel z-axis shift.
 x,y,z,dx,dy,dz=[rng.uniform(-3,3)for _ in range(6)];mass=rng.uniform(.1,10)
 izc=mass*(x*x+y*y)
 iza=.5*mass*sum((sx*x-dx)**2+(sx*y-dy)**2 for sx in [-1,1])
 near(iza,izc+mass*(dx*dx+dy*dy))
for n in range(1,101):assert len(list(itertools.combinations(range(n),2)))==n*(n-1)//2
# A stationary mass needs upward support m*g even though its actual acceleration is zero.
physical_gravity=(0,-9.81);fictitious=tuple(-x for x in physical_gravity);assert fictitious==(0,9.81)
out=dict(executedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),interpreter='Default Python standard library',fixedResults={'parallelAxisKgM2':.6,'axialCylinderKgM2':.12,'netForceN':20,'kineticEnergyJ':26,'pointMassMatrixKgM2':[[23,15],[15,12]],'mixedProductMatrixShape':[4,6],'fictitiousBaseAcceleration':[0,9.81]},variedCases=1000,assertionsPerVariedCase=3,variedGroups=['point-position velocity energy equals derived mass-matrix quadratic form','positive-definite point-mass matrix for strictly positive masses and lengths','parallel-axis z component independent of axial displacement'],mixedProductCountChecks=100,runtimeBoundary='No downloaded dependencies, author scripts, ROS/Gazebo/hardware, model, browser or restricted environment was used.')
(R/'audits/assignment-coverage/W03-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
