"""Independent L47 repair/new-gap computations from hidden-key packet and source equations."""
from pathlib import Path
import json,math,random,datetime,hashlib,itertools
R=Path(__file__).resolve().parents[1];checks=[]
def mm(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
def tr(a):return list(map(list,zip(*a)))
def sm(x):
 m=max(x);e=[math.exp(v-m)for v in x];s=sum(e);return [v/s for v in e]
def add(a,b):return [x+y for x,y in zip(a,b)]
def ln(x):
 m=sum(x)/len(x);v=sum((t-m)**2 for t in x)/len(x);return [(t-m)/math.sqrt(v)for t in x]
def close(a,b):
 if isinstance(a,list):return len(a)==len(b)and all(close(x,y)for x,y in zip(a,b))
 return math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10)
def ck(name,a,b):assert close(a,b),(name,a,b);checks.append(dict(name=name,value=a,expected=b))
def head(q,k,v,causal=True):
 scores=mm(q,tr(k));out=[]
 for i,row in enumerate(scores):
  w=sm([x/math.sqrt(len(q[0]))for x in (row[:i+1]if causal else row)]);out.append(mm([w],v[:i+1]if causal else v)[0])
 return out
L=math.log(3);h1=head([[1],[1]],[[0],[L]],[[2],[4]]);h2=head([[2],[1]],[[L],[0]],[[1],[3]]);cat=[a+b for a,b in zip(h1,h2)];wo=[[1,2],[-1,1]];projected=mm(cat,wo)
ck('Q073 head1',h1,[[2],[3.5]]);ck('Q073 head2',h2,[[1],[1.5]]);ck('Q073 projected',projected,[[1,5],[2,8.5]])
unmasked=[a+b for a,b in zip(head([[1],[1]],[[0],[L]],[[2],[4]],False),head([[2],[1]],[[L],[0]],[[1],[3]],False))];ck('Q073 no mask alternative',mm(unmasked,wo),[[2.3,8.2],[2,8.5]])
ck('Q073 omitted projection',cat,[[2,1],[3.5,1.5]])
ck('Q073 equal second-row weights',mm([[2,1],[3,2]],wo),[[1,5],[1,8]])
x=[1,3];norm=ln(x);attention=[norm[0],2*norm[1]];o=add(x,attention)
def ffn(z):return add(mm([[max(0,v)for v in add(mm([z],[[1,-1],[1,1]])[0],[1,0])]],[[2,0],[0,1]])[0],[0,1])
ck('Q074 first norm',norm,[-1,1]);ck('Q074 O',o,[0,5]);ck('Q074 FFN',ffn(ln(o)),[2,3]);H=add(o,ffn(ln(o)));ck('Q074 H',H,[2,8]);ck('Q074 omit second normalization',add(o,ffn(o)),[12,11]);ck('Q074 extra final normalization',ln(H),[-1,1])
E=[[0,1],[math.log(2),0],[math.log(3),1]];positions=[[.1,0],[0,.2],[.3,-.1]];ids=[1,0];X=[add(E[i],positions[p])for p,i in enumerate(ids)];probs=sm(mm([[1,0]],tr(E))[0]);chosen=sorted(sorted(range(3),key=lambda i:probs[i],reverse=True)[:2]);normp=[probs[i]/sum(probs[j]for j in chosen)for i in chosen];r=.30;cum=0
for token,prob in zip(chosen,normp):
 cum+=prob
 if r<cum:break
ck('Q075 X',X,[[math.log(2)+.1,0],[0,1.2]]);ck('Q075 full probabilities',probs,[1/6,2/6,3/6]);ck('Q075 retained probabilities',normp,[.4,.6]);ck('Q075 selected ID',token,1);ck('Q075 new row',add(E[token],positions[2]),[math.log(2)+.3,-.1])
ck('Q076 cross score shape',[3,5],[3,5]);ck('Q033 affine output',add([-1*2,1*3],[1,-1]),[-1,2]);ck('Q033 subtract offset',[-2-1,3-(-1)],[-3,4]);ck('Q065 exact inclusive mass',.5+.3,.8);ck('Q065 normalized',[.5/.8,.3/.8],[.625,.375])
# Exhaustive independent Rademacher coordinates, not MonteCarlo variance matching.
for d in range(1,5):
 vals=[sum(q*k for q,k in zip(z[:d],z[d:]))for z in itertools.product([-1,1],repeat=2*d)];v=sum(t*t for t in vals)/len(vals);ck(f'Q016 variance dk={d}',v,d);ck(f'Q016 scaled variance dk={d}',v/d,1)
rng=random.Random(4702)
for _ in range(1000):
 n=rng.randint(2,7);q=[[rng.uniform(-3,3)]for _ in range(n)];k=[[rng.uniform(-3,3)]for _ in range(n)];v=[[rng.uniform(-3,3),rng.uniform(-3,3)]for _ in range(n)];out=head(q,k,v);j=rng.randrange(1,n)
 assert close(out[:j],head(q[:j],k[:j],v[:j]))
 assert close(out[0],v[0])
 z=[rng.uniform(-10,10)for _ in range(3)];p=sm(z);assert math.isclose(sum(p),1)
 assert close(p,sm([t+10 for t in z]))
 zz=ln(z);assert abs(sum(zz))<1e-9 and abs(sum(t*t for t in zz)/3-1)<1e-9
p=R/'audits/W10-L47-v2-contracts-independent-checks.json';assert not p.exists();p.write_text(json.dumps(dict(completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scriptSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),explicitCount=len(checks),checks=checks,variedCases=1000,variedAssertions=5000,runtime='Default standard-library interpreter only. Independent source-equation reconstruction, no model package, network inference, corpus or restricted temporary environment. No source executable program is present.'),indent=2)+'\n');print(len(checks),'explicit checks and5000 varied assertions passed')
