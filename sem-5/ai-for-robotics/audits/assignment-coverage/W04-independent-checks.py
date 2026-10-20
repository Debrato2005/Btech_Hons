"""Independent deterministic arithmetic, not author checks or a browser/runtime claim."""
from fractions import Fraction as F
import pathlib,json,math,datetime,hashlib,re
R=pathlib.Path(__file__).resolve().parents[2];D=R/'audits/assignment-coverage'
coeff={'o1':(F(3,2),F(-1,2)),'o2':(F(3,4),F(1,4)),'o3':(F(3,4),F(-1,4)),'o4':(F(1,2),F(-1,8))}
cubic={k:dict(q2=float(4*a+8*b),velocity2=float(4*a+12*b),allEndpointConstraints=(4*a+8*b==1 and 4*a+12*b==0))for k,(a,b)in coeff.items()};assert [k for k,v in cubic.items()if v['allEndpointConstraints']]==['o3']
angles={'o1':-20,'o2':340,'o3':180,'o4':-350};travel={k:dict(endDegrees=(10+d)%360,travelDegrees=abs(d),reachesTarget=(10+d)%360==350)for k,d in angles.items()};assert min((v['travelDegrees'],k)for k,v in travel.items()if v['reachesTarget'])[1]=='o1'
radii={'o1':5,'o2':9,'o3':.5,'o4':1};workspace={k:dict(radius=r,cosElbow=(r*r-41)/40,reachable=1<=r<=9)for k,r in radii.items()};assert [k for k,v in workspace.items()if not v['reachable']]==['o3']
singular={x:abs(math.sin(math.radians(x)))<1e-12 for x in [0,45,90,180,225,270]};assert [x for x,v in singular.items()if v]==[0,180]
q=json.loads((R/'data/question-batches/ASSIGN-W04.json').read_text())['questions'];norm=lambda s:re.sub(r'\W+','',s.casefold());exact=[]
for p in(R/'data/question-batches').glob('*.json'):
 d=json.loads(p.read_text());items=d if isinstance(d,list)else d.get('questions',[])
 for a in q:
  for b in items:
   if a['id']!=b['id'] and norm(a['stem'])==norm(b['stem']):exact.append([a['id'],b['id']])
assert not exact
out=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewerId='independent-reviewer-robotics-recovery-v3',runtime='Default installed Python standard library only. No software installation, author code, denied route, ROS, simulator, model inference or browser operation.',scriptSha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),checks={'Q001':{'endpointConstraintCount':6,'minimumGenericDegree':5,'uniquenessProof':'A difference polynomial satisfying homogeneous value/first/second derivative data at two distinct endpoints has both roots of multiplicity three, so a polynomial of degree at most five must be zero.'},'Q002':cubic,'Q003':{'leftVelocityLimit_m_s':1,'rightVelocityLimit_m_s':1,'leftAcceleration_m_s2':1,'rightAcceleration_m_s2':0,'junctionNote':'Interpret the ordinary blend as its continuous velocity joining extension; acceleration lacks a two-sided derivative at the switch.'},'Q004':travel,'Q006':workspace,'Q007':{'columns':7,'rank':6,'nullity':1},'Q010':singular},exactNormalizedStemCollisions=exact,semanticDuplicateFindings=[{'questionId':'ASSIGN-W04-Q007','matches':['W11-L54-P1719-Q02'],'finding':'Same seven-joint rank-six pose map, same 7-6 calculation and same null-space interpretation. No distinct examination angle beyond wording/additional distractor.'},{'questionId':'ASSIGN-W04-Q009','matches':['W04-L18-Q031','W04-L20-P0609-Q02'],'finding':'Same SCARA horizontal-compliance/vertical-stiffness distinction for insertion and alignment errors. Same reversed-direction/isotropic-stiffness distractor family. No distinct reasoning angle.'}],otherConceptOverlap='Q001 overlaps quintic endpoint facts but tests minimum degree from independent data, unlike identifying conditions or matching degree/count triples. Q006 is an explicit numerical annulus test, not counted as a new physical concept beyond annular workspace.')
(D/'W04-independent-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
