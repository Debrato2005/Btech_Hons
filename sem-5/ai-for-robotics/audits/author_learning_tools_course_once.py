"""One-time authoring of draft tools. Never writes approval, questions or bank."""
from pathlib import Path
import copy,datetime,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate import question_hash
AUTHOR='robotics-learning-resource-projection-author-20261019'
def read(p):return json.loads((ROOT/p).read_text())
def dump(p,v):p=ROOT/p;assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
bank=read('data/bank.json');qm={q['id']:q for q in bank['questions']};old=read('data/learning-tools-draft.json')['learningTools']
seen_pages={106,116,332,333,386,590,729,730,904,905,914,918,942,1068,1102,1107,1108,1109,1110,1111,1112,1113,1114,1115,1116,1117,1119,1120,1121,1122,1123,1378,1515,1628}
source=next(s for s in bank['sources'] if s['id']=='lectures')
def bind(r,qids,impl):
 qs=[qm[qid] for qid in qids];assert all(q['status']=='verified' for q in qs)
 r.update(authorId=AUTHOR,version=1,status='draft',reviewIds=[],questionIds=qids,questionBindings=[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in qs],conceptIds=sorted({c for q in qs for c in q['conceptIds']}))
 refs={json.dumps(c,sort_keys=True):copy.deepcopy(c) for q in qs for c in q['citations']};r['sourceRefs']=list(refs.values());r['slideIds']=sorted({c['slideId'] for c in r['sourceRefs']})
 assert all(c['sourceId']=='lectures' and c['physicalPage'] in seen_pages for c in r['sourceRefs']),(r['id'],r['sourceRefs'])
 r['implementationFiles']=[{'path':p,'sha256':sha(p)} for p in impl]
 r['questionEvidence']=[{'questionId':q['id'],'stem':q['stem'],'assumptions':q['assumptions'],'exactFormulas':copy.deepcopy(q['solution']['formulas'])} for q in qs]
 r['sourceQualifications']=[{'questionId':q['id'],'qualification':copy.deepcopy(q['conflictResolution'])} for q in qs if q.get('conflictResolution')]
 r['primaryEvidence']=[copy.deepcopy(e) for q in qs for e in q.get('primaryEvidence',[])]
 if r['sourceQualifications']:r['conflictResolution']={'status':'draft-resource-requires-independent-review','basis':'The linked approved question qualification is retained, not silently replaced. This newly authored resource requires its own independent review.','inheritedQualifications':copy.deepcopy(r['sourceQualifications'])}
 r['sourceInspectionAudit']='audits/learning-resource-completion-source-inspections.json'
 return r
numeric_map={
'bayes-two-hypotheses':['W01-L03-P0106-Q01','W01-L03-P0106-Q02'],
'q-learning-update':['W06-L30-Q027','W06-L30-Q056'],
'rotated-vector-x':['W02-L10-Q011'],
'net-force-component':['W03-L12-Q006'],
'series-stiffness':['W04-L19-P0590-Q02'],
'coupled-inertia-torque':['W05-L24-P0729-Q03'],
'epsilon-greedy-probability':['W06-L30-Q030'],
'pinhole-image-x':['W07-L31-P0942-Q04'],
'convolution-output-size':['W07-L35-Q017'],
'octile-grid-distance':['W08-L36-P1102-Q06'],
'lidar-roundtrip-range':['W09-L44-Q010'],
'uniform-sample-count':['W10-L48-Q009'],
'adc-uniform-bin-width':['W11-L52-P1628-Q02']}
program="const N=require('./app/course-numerical.js');console.log(JSON.stringify(Object.fromEntries(N.kinds.map(k=>{const d=N.getImplementation(k);return[k,{title:d.title,version:d.version,parameterDomains:d.parameterDomains}]}))))"
defs=json.loads(subprocess.check_output(['node','-e',program],cwd=ROOT,text=True));nums=[]
for kind,qids in numeric_map.items():
 q=qm[qids[0]]
 if kind in defs:info=defs[kind]
 else:
  oldr=next(r for r in old['numericalFamilies'] if r['generatorKind']==kind);info={'title':oldr['title'],'version':oldr['generatorVersion'],'parameterDomains':{'prior':'(0,1)','likelihoodTrue':'(0,1]','likelihoodFalse':'(0,1]'} if kind=='bayes-two-hypotheses' else {'oldQ':'finite','reward':'finite','maxNextQ':'finite','alpha':'[0,1]','gamma':'[0,1]','terminal':'boolean'}}
 r={'id':'course.numerical.'+kind,'title':info['title'],'week':q['week'],'lectureId':q['lectureId'],'generatorKind':kind,'generatorVersion':info['version'],'parameterDomains':info['parameterDomains'],'description':'Added parameterized exercises of the source-supported model. Values are generated within an explicitly bounded domain, not quoted slide measurements. Every instance rejects equivalent rounded alternatives.','assumptions':['The exact generated premise states the model, units and added assumptions.','These variants do not add unique-concept coverage and are not automatically independent mastery evidence.']}
 if kind=='bayes-two-hypotheses':r['assumptions'].append('Two hypotheses are exhaustive and mutually exclusive; the total-evidence denominator is derived by partitioning the evidence, not a literal two-hypothesis slide example.')
 nums.append(bind(r,qids,['app/learning-tools.js']+(['app/course-numerical.js'] if kind in defs else [])))
algo_map={
'bfs':['W08-L36-P1107-Q01','W08-L36-P1108-Q02','W08-L36-P1109-Q02','W08-L36-P1110-Q01','W08-L36-P1110-Q02'],
'ucs':['W08-L36-P1117-Q02','W08-L36-P1112-Q01'],
'astar':['W08-L36-P1117-Q02','W08-L36-P1120-Q01'],
'dfs':['W01-L03-P0116-Q01','W08-L36-P1117-Q02'],
'q-learning':['W06-L30-Q026','W06-L30-Q030','W06-L30-Q056']}
algs=[]
for oldr in old['algorithmVisualizations']:
 r=copy.deepcopy(oldr);kind='q-learning' if 'qLearningConfig'in r else r['config']['algorithm'];r['id']='course.'+r['id'];r['revisionOf']=oldr['id'];r['description']=r.get('notes') or r.get('generatedExplanation') or 'Added sequential numerical illustration of the lecture Q-learning update, not a training run or a reproduced slide result.'
 if kind=='dfs':r['description']+=' This is the explicitly eager-discovery iterative stack variant, not recursive DFS with entry-time marking; the order need not match a recursive trace.'
 if kind=='astar':r['assumptions'].append('The supplied heuristic is tested against the exact remaining costs on this finite graph; arbitrary edited heuristics are not certified.')
 if kind=='q-learning':r['description']+=' True-terminal masking is an explicit qualification of p914; external time-limit truncation is not treated as terminal.'
 algs.append(bind(r,algo_map[kind],['app/learning-tools.js']))
out={'schemaVersion':'1.0.0','authorId':AUTHOR,'status':'draft','scope':'Separately authored source-linked algorithms and numerical families. No independent approval implied. Original 24 draft resources are preserved.','learningTools':{'formulaSheet':[],'confusionPairs':[],'traps':[],'algorithmVisualizations':algs,'numericalFamilies':nums}}
dump('data/learning-tools-course.json',out)
notes={106:'Bayes equation, positive denominator and prior/posterior distinction.',116:'LIFO/depth/backtracking definition; no claim that the different road-graph exercise reproduces this red trace.',332:'Local tip-velocity components precede the explicit coordinate map on the following page; new family uses supplied components rather than re-deriving this recursion.',333:'Explicit Rz(theta1+theta2) rotation and velocity-coordinate map.',386:'Net external force equals mass times center-of-mass acceleration.',590:'Parallel stiffness sum and series reciprocal-stiffness sum.',729:'Matrix inertia plus V and G; prose also mentions friction.',730:'Explicit additional F friction/non-rigid effects; generated inertia task sets V,G,F to zero.',904:'Full TD update with pre-update old value, learning rate eta and max bootstrap.',905:'Epsilon exploration branch; uniform-all-actions convention is explicit in new premise, not inferred from prose alone.',914:'Source bootstraps before terminated/truncated check; new true-terminal zero-bootstrap convention remains visibly qualified.',918:'Repeated Q-learning summary; source convergence/global optimality prose is not imported as an unconditional guarantee of the finite generated examples.',942:'Positive virtual-plane x=fX/Z and y=fY/Z, camera-frame inputs.',1068:'Floor output formula, per-side padding, stride; 28 to 24 source example.',1102:'Four- and eight-connected edges with cardinal1 and diagonal sqrt2 costs.',1378:'Round-trip d=ct/2; c=3e8 m/s; 40 ns gives 6 m.',1515:'Sampling rate in Hz; distinguish sample count from Nyquist frequency; no reconstruction claim at equality.',1628:'10-bit 0..1023 code range and 0..5 V prose; equal-bin denominator1024 must not be silently confused with endpoint interpolation1023.'}
for p in sorted(seen_pages):
 if p not in notes:notes[p]='Actual road-network pixels checked: topology, all displayed weights/heuristics, frontier states, goal-pop convention and non-goal expansion counts. Derived missing intermediate operations remain under explicit algorithm conventions.'
dump('audits/learning-resource-completion-source-inspections.json',{'authorId':AUTHOR,'inspectedAt':'2026-10-20T00:10:30Z/2026-10-20T00:18:25Z','method':'Actual faithful 1800-pixel lecture renders opened with view_image, individually readable; not text-only. This is new-resource author inspection, not independent review.','sourceId':'lectures','sourceSha256':source['sha256'],'pages':[{'physicalPage':p,'previewPath':f'sources/previews/lectures/page-{p:04}.webp','previewSha256':sha(f'sources/previews/lectures/page-{p:04}.webp'),'observations':notes[p]} for p in sorted(seen_pages)]})
print(json.dumps({'algorithms':len(algs),'numericalFamilies':len(nums),'sourcePagesViewed':len(seen_pages),'weeks':sorted({r['week'] for r in nums}),'bankSha256':sha('data/bank.json')}))
