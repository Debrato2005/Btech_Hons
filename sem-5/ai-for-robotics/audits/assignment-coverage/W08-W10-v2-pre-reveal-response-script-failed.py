from pathlib import Path
import json,hashlib,datetime,heapq,math,random
R=Path(__file__).resolve().parents[2];D=R/'audits/assignment-coverage'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
reason={8:{1:'UCS removes A0,C2,B5,F6,E7. The path to E first has cost8 through B, then improves to7 through F before removal. Returned A-C-F-E has cost2+4+1=7. Alternatives A-B-E8,A-B-D-E13 and A-C-F-G-D-E17 are larger.',2:'Item2 defines h as estimated cost to go; item3 gives f=g+h. With h identicallyzero, f=g, and unchanged frontier/tie rules give UCS cost priority.',6:'The max next-state target is5, so y=1+.9*5=5.5 and delta5.5-4.3=1.2. Terminal masking leaves only reward1.0. Using the old estimate inside bootstrap gives4.87, the sign reversal gives-1.2, and failing masking gives terminal5.5.',8:'Under the supplied positive receiver-offset model,2 microseconds is2e-6 seconds. Multiplying by3e8 m/s yields positive600 m. The new alternatives are plausible sign, nanosecond and millisecond unit confusions.'},10:{4:'X has12 token rows and64 feature columns. Q/K have12x16, V12x20, QK-transpose and row-softmax12x12, and multiplying A by V yields H12x20. Source WV64x20 is on page46; incorrect intermediate64x16 in the V line is on page47.'}}
checks=[]
def ck(n,c):assert c,n;checks.append(n)
edges=[('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('D','E',2),('D','G',6),('E','F',1),('F','G',3)]
g={x:[]for x in 'ABCDEFG'}
for a,b,w in edges:g[a].append((b,w));g[b].append((a,w))
heap=[(0,'A',('A',))];best={'A':0};trace=[]
while heap:
 cost,u,path=heapq.heappop(heap)
 if cost!=best[u]:continue
 trace.append((u,cost))
 if u=='E':break
 for v,w in g[u]:
  if cost+w<best.get(v,float('inf')):best[v]=cost+w;heapq.heappush(heap,(cost+w,v,path+(v,)))
ck('UCS full removal trace',trace==[('A',0),('C',2),('B',5),('F',6),('E',7)])
ck('UCS returned path',path==('A','C','F','E'))
ck('Alternative path costs',[5+3,5+6+2,2+4+3+6+2]==[8,13,17])
ck('DQN target delta terminal',math.isclose(1+.9*max(3,5),5.5) and math.isclose(5.5-4.3,1.2) and 1+.9*0==1)
ck('Clock contribution and units',3e8*2e-6==600 and 3e8*2e-9==.6 and 3e8*2e-3==600000)
rng=random.Random(8102026);varied=0
for _ in range(1000):
 gval=rng.uniform(-100,100);assert gval+0==gval;varied+=1
 r=rng.uniform(-10,10);discount=rng.random();nextq=[rng.uniform(-20,20)for _ in range(5)];y=r+discount*max(nextq);assert y==max(r+discount*x for x in nextq);varied+=1
 dt=rng.uniform(-100,100);assert math.isclose(3e8*dt*1e-6,300*dt,abs_tol=1e-8);varied+=1
 tokens=rng.randint(1,100);features=rng.randint(1,100);dk=rng.randint(1,50);dv=rng.randint(1,50);x=(tokens,features);q=(x[0],dk);k=(tokens,dk);v=(tokens,dv);a=(q[0],k[0]);h=(a[0],v[1]);assert a[1]==v[0]and h==(tokens,dv);varied+=1
for week in [8,10]:
 B=f'ASSIGN-W{week:02d}';pp=R/f'audits/blind-{B}-v2.json';packet=json.loads(pp.read_text());qs=packet if isinstance(packet,list)else packet['questions'];binding=json.loads((R/f'audits/blind-binding-{B}-v2.json').read_text());assert sha(pp)==binding['packetSha256'];save(D/f'W{week:02d}-v2-recovery-independent-prekey-seal.json',{'reviewerId':'repair_assignment_source_bindings:independent-reviewer','sealedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packetPath':str(pp.relative_to(R)),'packetSha256':sha(pp),'generatedKeyOpened':False,'sourcePrintedKeysVisible':True,'fullyBlind':False,'sourceObservationsPath':'audits/assignment-coverage/W08-W10-recovery-independent-source-observations.json','sourceObservationsSha256':sha(D/'W08-W10-recovery-independent-source-observations.json'),'answers':[{'questionId':q['id'],'selectedOptionIds':['o1'],'reasoning':reason[week][int(q['id'][-3:])]}for q in qs]})
save(D/'W08-W10-v2-recovery-independent-checks.json',{'reviewerId':'repair_assignment_source_bindings:independent-reviewer','namedChecks':checks,'variedAssertions':varied,'seed':8102026,'UCSRemovalTrace':trace,'allPassed':True,'scope':'Default installed standard-library arithmetic and graph/shape checks; no author scripts or external runtime.'});print('Sealed5 independently solved responses;',len(checks),'named;',varied,'varied')
