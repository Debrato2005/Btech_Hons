#!/usr/bin/env python3
"""L36 author calculations only; does not independently verify any question."""
import math,json,hashlib,heapq,random
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[1];records=[]
def ck(name,cond,detail=None):
 assert cond,name
 records.append(dict(name=name,passed=True,detail=detail))
ck('Robot side clearances and mistaken radius comparison',(F('0.8')/2,F('1')/2)==(F('.4'),F('.5')) and F('.5')<F('.8'))
ck('Half width deficit is not footprint radius',(F('1')-F('.8'))/2==F('.1') and F('.1')!=F('.5'))
# Exact conservative closed-cell raster rule.
def row(y,s):
 j=y//s;return j*s,(j+1)*s
coarse=row(F('.5'),F(1));fine=row(F('.5'),F('.2'))
free=lambda r:F('.3')<r[0] and r[1]<F('.9')
ck('Coarse endpoint cell intersects walls',coarse==(F(0),F(1)) and not free(coarse),list(map(str,coarse)))
ck('Fine endpoint cell wholly free',fine==(F('.4'),F('.6')) and free(fine),list(map(str,fine)))
ck('Fine endpoints are connected cell centers',(F('.5')/F('.2')-F('.5'),F('3.5')/F('.2')-F('.5'))==(2,17))
ck('Physical passage width does not change',F('.9')-F('.3')==F('.6'))
# Directed five-node minimum, including every distractor and omitted fifth path.
edges={'A':{'B':3,'C':1},'B':{'D':5,'E':1},'C':{'B':7,'D':2},'D':{'E':7},'E':{}}
def paths(g,u,target,p=()):
 if u==target:return [(p+(u,),0)]
 return [(path,c+w)for v,w in g[u].items()if v not in p for path,c in paths(g,v,target,p+(u,))]
pp=sorted(paths(edges,'A','E'),key=lambda z:z[1]);ck('All directed A-to-E path costs',[( ''.join(p),c)for p,c in pp]==[('ABE',4),('ACBE',9),('ACDE',10),('ABDE',15),('ACBDE',20)],pp)
ck('Connectivity distance exact expressions',F('.4')*(5+3)==F('3.2') and abs(.4*(2+3*math.sqrt(2))-(.8+1.2*math.sqrt(2)))<1e-12)
ck('Distance distractors differ',len({round(x,10)for x in[.8+1.2*math.sqrt(2),2.,.4*math.sqrt(34),3.2]})==4)
# Separate forward priority search with parent reconstruction and strict relaxation.
pairs=[('A','B',5),('A','C',2),('B','D',6),('B','E',3),('C','F',4),('E','F',1),('E','D',2),('D','G',6),('F','G',3)]
g={v:{}for v in'ABCDEFG'}
for u,v,c in pairs:g[u][v]=c;g[v][u]=c
h=dict(zip('ABCDEFG',[7,6,5,4,3,2,0]))
def search(g,start,goal,h=None):
 h=h or{v:0 for v in g};pq=[(h[start],start,0)];dist={start:0};parent={};done=[];changes=[]
 while pq:
  priority,u,old=heapq.heappop(pq)
  if u in done or old!=dist[u]:continue
  if u==goal:
   path=[u]
   while path[-1]!=start:path.append(parent[path[-1]])
   return done,list(reversed(path)),dist[u],changes,dist,parent
  done.append(u)
  for v,c in g[u].items():
   cand=dist[u]+c
   if v not in done and cand<dist.get(v,math.inf):
    changes.append((u,v,dist.get(v,None),cand));dist[v]=cand;parent[v]=u;heapq.heappush(pq,(cand+h[v],v,cand))
 return done,None,math.inf,changes,dist,parent
u=search(g,'A','G');a=search(g,'A','G',h)
ck('UCS full forward order and parent chain',u[:3]==(['A','C','B','F','E','D'],['A','C','F','G'],9),u)
ck('A-star full forward order and parent chain',a[:3]==(['A','C','F'],['A','C','F','G'],9),a)
ck('Two strict cheaper-route parent relaxations',('F','E',8,7)in u[3] and('E','D',11,9)in u[3])
ck('Worse candidate for G cannot overwrite parent',u[4]['D']+g['D']['G']==15 and u[4]['G']==9 and u[5]['G']=='F')
ck('Heuristic consistency for both edge directions',all(abs(h[x]-h[y])<=c for x,y,c in pairs))
ck('Goal excluded counts',len(u[0])==6 and len(a[0])==3 and len(u[0])+1==7 and len(a[0])+1==4)
ck('Generated goal would stop UCS too soon',next(i for i,v in enumerate(u[0])if v=='F')+1==4)
ck('All-option detour arithmetic',sum(g[x][y]for x,y in zip('ACFEDG','CFEDG'))==15)
# Deterministic varied checks guard order-dependence and the grid-distance formula.
rng=random.Random(361102);cases=0;assertions=0
for _ in range(500):
 gg={}
 for v,adj in g.items():
  ls=list(adj.items());rng.shuffle(ls);gg[v]=dict(ls)
 assert search(gg,'A','G')[:3]==u[:3];assert search(gg,'A','G',h)[:3]==a[:3];cases+=1;assertions+=2
# Independently build finite graphs and compute shortest costs for many displacements.
for _ in range(200):
 dx=rng.randrange(0,9);dy=rng.randrange(0,9);s=rng.choice([.1,.2,.4,.5,1.])
 for eight in(False,True):
  gg={}
  for x in range(10):
   for y in range(10):
    node=(x,y);gg[node]={}
    for ax,ay in[(1,0),(-1,0),(0,1),(0,-1)]+([(1,1),(1,-1),(-1,1),(-1,-1)]if eight else[]):
     z=(x+ax,y+ay)
     if 0<=z[0]<10 and 0<=z[1]<10:gg[node][z]=s*math.hypot(ax,ay)
  result=search(gg,(0,0),(dx,dy))[2]
  expected=s*(max(dx,dy)+(math.sqrt(2)-1)*min(dx,dy))if eight else s*(dx+dy)
  assert abs(result-expected)<1e-10;assertions+=1
 cases+=1
ck('Adjacency-order and independent grid checks',cases==700 and assertions==1400,dict(cases=cases,assertions=assertions))
write=dict(authorId='L36-gap-repair-author-20261019',independentReview=False,passed=True,groups=len(records),variedCases=cases,variedAssertions=assertions,checks=records)
(R/'audits/W08-L36-COVERAGE-GAP-v2-author-computations.json').write_text(json.dumps(write,ensure_ascii=False,indent=2)+'\n')
print('PASS',len(records),'groups;',cases,'cases;',assertions,'varied assertions')
