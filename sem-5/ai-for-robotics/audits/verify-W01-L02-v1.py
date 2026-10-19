"""Reproduce L02 review arithmetic, bindings, and preserved-provenance checks.
This is a batch-only audit, not the complete-bank or release validator.
"""
import datetime, hashlib, heapq, importlib.util, itertools, json
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validator', ROOT/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def read(p): return json.loads((ROOT/p).read_text())
def digest(x): return hashlib.sha256(v.canonical_json(x).encode()).hexdigest()
def astar(edges,h,reopen=True):
    frontier=[(h['S'],'S',0)];best={'S':0};closed=set();trace=[]
    while frontier:
        f,s,g=heapq.heappop(frontier)
        if g!=best[s] or s in closed:continue
        trace.append({'state':s,'g':g,'f':f})
        if s=='G':return g,trace
        closed.add(s)
        for t,w in edges.get(s,[]):
            ng=g+w
            if ng<best.get(t,float('inf')) and (t not in closed or reopen):
                best[t]=ng;closed.discard(t);heapq.heappush(frontier,(ng+h[t],t,ng))
    return None,trace
b=read('data/question-batches/W01-L02.json');qs=b['questions'];rs=read('data/reviews/W01-L02-v1-independent.json');blind=read('audits/blind-answers-W01-L02-v1.json');orig=read('audits/blind-answers-W01-L02-v1-original-87.json');schema=read('data/schema.bank.json')
assert len(qs)==len(rs)==len(blind['answers'])==105
assert blind['answers'][:87]==orig['answers'] and blind['pageObservations'][:35]==orig['pageObservations']
assert v.file_hash(ROOT/'audits/blind-answers-W01-L02-v1-original-87.json')==blind['continuationProvenance']['originalSnapshotSha256']
assert v.file_hash(ROOT/'audits/blind-W01-L02.json')==blind['packetSha256']
assert v.file_hash(ROOT/'sources/raw/AI_for_Robotics_All_Lectures.pdf')==blind['sourceVersions']['lectures']
assert blind['authorAnswerRevealed'] is False # frozen pre-reveal snapshot, never rewritten after reveal
assert all(a['solvedBeforeAnswerSeen'] for a in blind['answers'])
errors=[]
for kind,items in [('question',qs),('review',rs),('concept',b['concepts'])]:
    for item in items: errors+=v.schema_errors(item,schema['$defs'][kind],root=schema)
assert not errors,errors
rm={r['questionId']:r for r in rs};am={a['questionId']:a for a in blind['answers']}
for q in qs:
    r=rm[q['id']];a=am[q['id']];assert r['questionSha256']==a['questionSha256']==v.question_hash(q)
    assert r['questionVersion']==q['version'] and r['reviewerId']!=q['authorId']
    assert set(r['independentAnswerOptionIds'])==set(q['correctOptionIds'])
    assert r['blindSolverId']==a.get('reviewerId',blind['reviewerId'])
    assert r['blindRecordSha256']==digest(a)
    assert r['blindAnswerFileSha256']==v.file_hash(ROOT/'audits/blind-answers-W01-L02-v1.json')
    assert r['sourceVersions']==blind['sourceVersions']
    assert set(r['reviewedSlideIds'])=={c['slideId'] for c in q['citations']}
    assert set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']}
    assert len({v.normalized_text(o['text']) for o in q['options']})==len(q['options'])
    assert len(q['correctOptionIds'])==(1 if q['selectionMode']=='single' else len(q['correctOptionIds']))
    if q['status']=='verified':assert r['decision']=='verified' and all(r['checks'].values())
    else:assert q['status']=='flagged' and r['decision']=='flagged' and not all(r['checks'].values())
for o in blind['pageObservations']:assert v.file_hash(ROOT/o['previewPath'])==o['previewSha256']
checks=[]
def check(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    checks.append({'test':name,'actual':str(actual),'expected':str(expected),'passed':True})
check('Q017 strict AND all four options',[(s>50 and d<2) for s,d in [(50,1),(51,2),(51,1),(49,1)]],[False,False,True,False])
check('Q032 ReLU weighted sum including negative bias',max(0,3*2+4*(-1)-1),1)
check('Q032 stated input-sign-only distractor yields 9 not 11',3*2+4*1-1,9)
check('Q033 ReLU at boundary',max(0,0),0)
check('Q033 sigmoid at zero',F(1,1+1),F(1,2))
check('Q034 adjacent fully connected weights',3*4+4*4+4*3,40)
check('Q034 excluded one-per-noninput-neuron biases',4+4+3,11)
features=[(1,4),(3,2),(2,5)]
check('Q045 max-pooling over all six point-order permutations',{tuple(max(p[j] for p in perm) for j in [0,1]) for perm in itertools.permutations(features)},{(3,5)})
check('Q045 sum distractor',tuple(sum(p[j] for p in features) for j in [0,1]),(6,11))
check('Q045 mean distractor',tuple(F(sum(p[j] for p in features),3) for j in [0,1]),(F(2),F(11,3)))
nodes={'A':(2,8),'B':(5,1),'C':(3,4)}
check('Q055 UCS/greedy/A-star distinct priorities',(min(nodes,key=lambda n:nodes[n][0]),min(nodes,key=lambda n:nodes[n][1]),min(nodes,key=lambda n:sum(nodes[n]))),('A','B','B'))
check('Q060 finite return',2+F(1,2)*4+F(1,4)*8,6)
check('Q061 discounted policy B at 0.5 and 0.9',(8*F(1,2),8*F(9,10)),(4,F(36,5)))
check('Q061 policy indifference gamma',F(5,8),F(625,1000))
check('Q098 category ratio',F(1000,80),F(25,2))
check('Q098 inverse ratio',F(80,1000),F(8,100))
check('Q098 image-count distractor rounded to 2 decimals',round(1200000/330000,2),3.64)
edges={'S':[('G',10),('A',1)],'A':[('G',1)]};h={'S':0,'A':1,'G':-100}
assert all(h[n]<=dist for n,dist in {'S':2,'A':1,'G':0}.items())
negative_goal,trace=astar(edges,h);check('Q056 non-overestimating negative goal heuristic counterexample',negative_goal,10)
zero_goal,trace0=astar(edges,{**h,'G':0});check('Q056 h(goal)=0 repairs this example',zero_goal,2)
e2={'S':[('A',2),('B',1)],'B':[('A',F(1,2))],'A':[('G',2)]};h2={'S':0,'A':0,'B':F(5,2),'G':0}
no_reopen,t2=astar(e2,h2,False);with_reopen,t3=astar(e2,h2,True)
check('Q056 admissible inconsistent heuristic without reopening',no_reopen,4)
check('Q056 same graph with reopening',with_reopen,F(7,2))
report={'scope':'L02 batch only; not full-bank integrity or release validation','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'questions':105,'reviews':105,'verified':sum(q['status']=='verified' for q in qs),'flagged':sum(q['status']=='flagged' for q in qs),'blindAnswers':105,'preservedOriginalBlindAnswers':87,'continuationBlindAnswers':18,'originalPageObservations':35,'continuationPageObservations':6,'schemaErrors':errors,'allQuestionBindingsMatch':True,'originalProvenancePreserved':True,'allAnswerSetsAgree':True,'variantFamiliesPresent':0,'arithmeticChecks':checks,'negativeGoalCounterexampleTrace':trace,'correctedGoalCounterexampleTrace':trace0,'reopeningCounterexample':{'without':t2,'with':t3},'knownUnresolvedQuestionIds':[q['id'] for q in qs if q['status']=='flagged'],'hashes':{'batch':v.file_hash(ROOT/'data/question-batches/W01-L02.json'),'reviewFile':v.file_hash(ROOT/'data/reviews/W01-L02-v1-independent.json'),'blindAnswerFile':v.file_hash(ROOT/'audits/blind-answers-W01-L02-v1.json'),'sourcePDF':blind['sourceVersions']['lectures']}}
(ROOT/'audits/W01-L02-v1-review-validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str)+'\n')
print(json.dumps({k:report[k] for k in ['questions','reviews','verified','flagged','schemaErrors','allQuestionBindingsMatch','originalProvenancePreserved','allAnswerSetsAgree']}));print(len(checks),'arithmetic/boundary/algorithm checks passed; unresolved pedagogical/correctness findings retained.')
