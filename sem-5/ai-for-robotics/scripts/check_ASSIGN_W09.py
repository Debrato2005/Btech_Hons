from assignment_second_half_common import *
from fractions import Fraction as R
import sys,random,math
checks=[]
def ck(n,v):assert v,n;checks.append(n)
children=[R(2+6,2),R(3,2)*2-R(1,2)*6,-R(1,2)*2+R(3,2)*6]
ck('all linear crossover children',children==[4,0,8])
ck('two fitness ranks',set(sorted(children,key=lambda x:x,reverse=True)[:2])=={4,8}and set(sorted(children,key=lambda x:-(x-1)**2,reverse=True)[:2])=={0,4})
ck('encoding exact',R((11-1)*63,15)==42 and int('101010',2)==42)
ck('encoded candidate reals',[1+R(15*d,63)for d in [42,43,46,11]]==[R(11),R(236,21),R(251,21),R(76,21)])
obs={(1,1),(2,1),(2,2),(4,2),(2,3),(3,4)};pts=[(0,0),(0,1),(2,4),(5,5)]
def decode(points,order):
 path=[points[0]];dirs=[]
 for target in points[1:]:
  for axis in order:
   while path[-1][axis]!=target[axis]:
    old=path[-1];step=1 if target[axis]>old[axis]else-1;new=list(old);new[axis]+=step;path.append(tuple(new));dirs.append((axis,step))
 L=len(dirs);N=sum(p in obs for p in path[1:]);T=sum(a!=b for a,b in zip(dirs,dirs[1:]));return path,L,N,T,R(1,1+L+10*N+T)
a=decode(pts,[0,1]);b=decode(pts,[1,0]);ck('horizontal full metric',a[1:]==(10,5,4,R(1,65)));ck('vertical full metric',b[1:]==(10,0,3,R(1,14)))
ck('vertical literal cells',b[0]==[(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4),(2,5),(3,5),(4,5),(5,5)])
ck('all path distractor denominators',[1+10+10*4+4,1+10+10*6+4,1+10+10*5,1+10+10+3,1+10+4]==[55,75,61,24,15])
ck('network parameter scopes',(6*16,6*16+16*4,6*16+16*4+16+4)==(96,160,180))
ck('Gaussian means',(2+2,2+1)==(4,3));ck('Gaussian covariance',(R('.25')+R('.5'),R('.16')+R('.4'))==(R('.75'),R('.56')))
ck('SLAM dimensions',3+2*6==15 and 2*6==12 and 3+3*6==21)
def mm(A,B):return [[sum(a*b for a,b in zip(row,col))for col in zip(*B)]for row in A]
def tr(A):return list(map(list,zip(*A)))
J=[[R(1),0,0],[0,R(1),R(2)],[0,0,R(1)]];P=[[R('.04'),0,0],[0,R('.04'),0],[0,0,R('.01')]];V=[R('.01'),R('.01'),R('.0025')]
M=mm(mm(J,P),tr(J))
for i in range(3):M[i][i]+=V[i]
ck('exact EKF covariance',M==[[R('.05'),0,0],[0,R('.09'),R('.02')],[0,R('.02'),R('.0125')]])
ck('coupled two-by-two block PSD',M[1][1]*M[2][2]-M[1][2]**2>0)
rng=random.Random(909);cnt=0
for _ in range(1000):
 ps=[(rng.randrange(6),rng.randrange(6))for _ in range(4)]
 ah=decode(ps,[0,1]);av=decode(ps,[1,0]);expected=sum(abs(x2-x1)+abs(y2-y1)for (x1,y1),(x2,y2)in zip(ps,ps[1:]))
 assert ah[1]==av[1]==expected;cnt+=1
 assert 0<ah[4]<=1 and 0<av[4]<=1;cnt+=1
 d=R(rng.randint(-10,10),2);p=R(rng.randint(1,100),100);q=R(rng.randint(1,100),100);vy=R(rng.randint(0,100),100);vt=R(rng.randint(0,100),100)
 yy=p+d*d*q+vy;tt=q+vt;yt=d*q
 assert yy*tt-yt*yt>=0;cnt+=1
 n=rng.randint(1,30);a=R(-5);bb=R(12);code=rng.randrange(2**n);x=a+(bb-a)*code/(2**n-1)
 assert (x-a)*(2**n-1)/(bb-a)==code;cnt+=1
out=dict(role='Author exact arithmetic and deterministic traces, not independent review',checkedAt=NOW(),pythonExecutable=sys.executable,checks=checks,variedCases=1000,variedAssertions=cnt,sourceGridPaths={'horizontal':a if False else decode(pts,[0,1])[0],'vertical':decode(pts,[1,0])[0]},questionHashes={q['id']:qhash(q)for q in json.loads((ROOT/'data/question-batches/ASSIGN-W09.json').read_text())['questions']})
dump('audits/ASSIGN-W09-author-checks.json',out);print(len(checks),'groups',cnt,'varied assertions')
