from assignment_second_half_common import *
from fractions import Fraction as R
import numpy as np,sys,math,random
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('projection mm with metre ratios',20*R(1,2)-20*R(1,4)==5)
ck('depth scale',R(1,2)==R(20,4)/R(20,2))
I=np.array([230],dtype=np.uint8)
ck('actual array uint8 output and dtype',(I+np.uint8(50)).dtype==np.uint8 and int((I+np.uint8(50))[0])==24)
ck('actual cast before addition',(I.astype(float)+50)[0]==280.0)
ck('cast after wrap is different',float((I+np.uint8(50))[0])==24.0)
a=[[1,2,3],[4,5,6],[7,8,9]];k=[[1,2,0],[0,-1,1],[2,0,-2]]
ck('correlation exact',sum(a[i][j]*k[i][j]for i in range(3)for j in range(3))==2)
ck('convolution exact',sum(a[i][j]*k[2-i][2-j]for i in range(3)for j in range(3))==28)
ck('flipped kernel literal',[[k[2-i][2-j]for j in range(3)]for i in range(3)]==[[-2,0,2],[1,-1,0],[0,2,1]])
ck('circularity',R(4*100,40**2)==R(1,4))
ck('bias conventions',(R(1,2)*2-3+1,R(1,2)*2-3-1)==(-1,-3))
ck('both activations',int(-1>=0)==0 and int(-3>=0)==0)
ck('kernel candidate outputs',[(28-k)//1+1 for k in (3,4,5,6,16)]==[26,25,24,23,13])
rng=random.Random(707);assertions=0
for _ in range(1000):
 x=rng.randrange(256);y=rng.randrange(256);z=np.array([x],dtype=np.uint8)+np.uint8(y)
 assert int(z[0])==(x+y)%256;assertions+=1
 assert float((np.array([x],dtype=np.uint8).astype(float)+y)[0])==x+y;assertions+=1
 s=rng.randint(1,100);assert abs((4*math.pi*s*s/(4*s)**2)-math.pi/4)<1e-12;assertions+=1
 f=rng.randint(1,100);z=rng.randint(1,100);h=rng.randint(1,100)
 assert R(f*h,2*z)==R(f*h,z)/2;assertions+=1
 # Shared depth maps parallel direction vectors to equal directions, not finite intersections.
 d=(rng.randint(1,10),rng.randint(1,10));assert (R(f*d[0],z),R(f*d[1],z))==(R(f,z)*d[0],R(f,z)*d[1]);assertions+=1
out=dict(role='Author calculations, not independent review',checkedAt=NOW(),pythonExecutable=sys.executable,numpyVersion=np.__version__,installationsPerformed=False,checks=checks,variedCases=1000,variedAssertions=assertions,questionHashes={q['id']:qhash(q) for q in json.loads((ROOT/'data/question-batches/ASSIGN-W07.json').read_text())['questions']})
dump('audits/ASSIGN-W07-author-checks.json',out);print(len(checks),'groups;',assertions,'varied assertions')
