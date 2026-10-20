from assignment_second_half_common import *
from fractions import Fraction as R
import sys,math,random
checks=[]
def ck(n,v):assert v,n;checks.append(n)
words=['chair','pick','red','ball','near'];one=lambda seq,w:[int(x==w)for x in seq]
ck('two vocabulary conventions',(one(words,'near'),one(sorted(words),'near'))==([0,0,0,0,1],[0,0,1,0,0]))
ck('supplied suffix rule','running'[:-3]=='runn')
q=[2,1];ks=[[3,1],[1,2],[0,1]];dots=[sum(a*b for a,b in zip(q,k))for k in ks];ck('all query key dot products',dots==[7,4,1])
def softmax(s):
 e=[math.exp(x-max(s))for x in s];return [x/sum(e)for x in e]
weights=softmax([x/math.sqrt(2)for x in dots]);ck('unrounded final vector',[round(x,4)for x in weights]==[.8816,.1057,.0127]);ck('weights normalize',abs(sum(weights)-1)<1e-15)
ck('no scale distractor',[round(x,4)for x in softmax(dots)]==[.9503,.0473,.0024]);ck('divide by d distractor',[round(x,4)for x in softmax([x/2 for x in dots])]==[.7856,.1753,.0391]);ck('linear normalization distractor',[round(x/sum(dots),4)for x in dots]==[.5833,.3333,.0833])
ck('temporal valid convolution pair',((100-2)//2+1,(100-2)//1+1)==(50,99))
ck('conditional chain exact',R('.5')*R('.4')*R('.2')==R('.04'))
ck('conditional omission distractors',(R('.5')*R('.2'),R('.5')*R('.4'),R('.4')*R('.2'))==(R('.1'),R('.2'),R('.08')))
def mm(A,B):
 assert len(A[0])==len(B)
 return [[sum(x*y for x,y in zip(row,col))for col in zip(*B)]for row in A]
X=[[i+j for j in range(64)]for i in range(12)];WQ=[[int(i==j)for j in range(16)]for i in range(64)];WV=[[int(i==j)for j in range(20)]for i in range(64)]
Q=mm(X,WQ);K=mm(X,WQ);V=mm(X,WV);S=mm(Q,list(map(list,zip(*K))));A=[softmax([v/4 for v in row])for row in S];H=mm(A,V)
ck('executed attention matrix shapes',[(len(m),len(m[0]))for m in [X,Q,K,V,A,H]]==[(12,64),(12,16),(12,16),(12,20),(12,12),(12,20)])
ck('actual projected value rows',V[0]==list(range(20)) and V[-1]==list(range(11,31)))
rng=random.Random(1010);cnt=0
for _ in range(1000):
 vals=[rng.uniform(-100,100)for _ in range(rng.randint(2,20))];p=softmax(vals);off=rng.uniform(-500,500)
 assert abs(sum(p)-1)<1e-12;cnt+=1
 assert all(abs(a-b)<1e-12 for a,b in zip(p,softmax([x+off for x in vals])));cnt+=1
 N=rng.randint(2,500);K=rng.randint(1,N);S=rng.randint(1,20)
 assert len(list(range(0,N-K+1,S)))==(N-K)//S+1;cnt+=1
 ps=[R(rng.randint(0,100),100)for _ in range(3)];prod=ps[0]*ps[1]*ps[2]
 assert 0<=prod<=min(ps);cnt+=1
out=dict(role='Author stdlib checks, not independent review',checkedAt=NOW(),pythonExecutable=sys.executable,checks=checks,variedCases=1000,variedAssertions=cnt,exactAttentionWeights=weights,restrictedRuntimeUsed=False,questionHashes={q['id']:qhash(q)for q in json.loads((ROOT/'data/question-batches/ASSIGN-W10.json').read_text())['questions']})
dump('audits/ASSIGN-W10-author-checks.json',out);print(len(checks),'groups',cnt,'assertions')
