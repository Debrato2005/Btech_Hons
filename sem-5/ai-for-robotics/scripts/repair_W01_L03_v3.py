from pathlib import Path
import json,copy,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W01-L03.json';b=json.loads(p.read_text());old=copy.deepcopy(b);rs=json.loads((R/'data/reviews/W01-L03-v2-independent.json').read_text());ids={x['questionId'] for x in rs if x['decision']=='flagged'}
a=R/'audits/batch-history/W01-L03-v2-before-full-quality-repair.json';assert not a.exists();a.write_text(json.dumps([q for q in b['questions'] if q['id'] in ids],ensure_ascii=False,indent=2)+'\n')
def opt(q,id,t,e):next(o for o in q['options'] if o['id']==id)['text']=t;q['solution']['optionExplanations'][id]=e
for q in b['questions']:
 if q['id'] not in ids:continue
 assert q['version']==2;h=question_hash(q);au='robotics-integration-L03-v3-revision-author';q.update(version=3,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(au);q.setdefault('revisionHistory',[]).append({'version':3,'authorId':au,'priorQuestionSha256':h,'reason':'Repair newly completed full independent review of distractors and standalone assumptions.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 sid=q['id'].removeprefix('W01-L03-')
 if sid=='P0101-Q03':
  opt(q,'o2','The smallest singular value is small but strictly positive, with full rank retained','This can indicate poor conditioning near a singularity, but is not itself rank loss.')
  opt(q,'o3','One entry of a square Jacobian is zero while its determinant remains nonzero','An individual zero entry does not make an invertible matrix singular.')
  opt(q,'o4','A square Jacobian has negative rather than positive determinant','A negative nonzero determinant still describes an invertible local map.')
 if sid=='P0102-Q02':
  opt(q,'o2','Allowing a zero eigenvector would force every eigenvalue to be zero','The equation A0=λ0 holds for every λ, not only zero.')
  opt(q,'o3','Excluding the zero eigenvector makes every matrix invertible','A singular matrix can have a nonzero eigenvector with eigenvalue zero.')
  opt(q,'o4','A zero eigenvalue can occur only when the eigenvector is also zero','A zero eigenvalue means a nonzero vector lies in the nullspace.')
 if sid=='P0107-Q03':
  q['stem']='For a continuous random variable X with density f_X and finite mean, which expression gives E[X]?';q['assumptions']=['The integral of |x| f_X(x) over the real line is finite.']
  q['solution']['formulas'][0]['assumptions']=['The integral of |x| f_X(x) is finite.'];q['solution']['formulas'][0]['units']={'X,E(X)':'units of the measured variable','f_X':'inverse units of X'}
  q['solution']['justification']='When the mean exists, integrating x weighted by its density gives the expected value; normalization alone does not ensure existence.';q['solution']['simpleExplanation']=q['solution']['justification']
 if sid=='P0118-Q04':
  opt(q,'o2','A high prediction-accuracy score by itself explains the force choice for this object','Accuracy measures performance; an explicit path of tests supplies the per-object explanation.')
  opt(q,'o3','The training split with largest information gain is itself the complete explanation of every later decision','Information gain helps choose splits, but a particular prediction is explained by the tests followed for that input.')
  opt(q,'o4','Using low force on a glass example proves the decision rule has passed every physical safety test','A traceable decision is not a substitute for physical safety validation.')
 if sid=='P0121-Q03':
  q['stem']='For a feasible planning problem under the planner’s stated applicability assumptions, which statement expresses probabilistic completeness?';q['assumptions']=['A solution exists and the instance satisfies the conditions under which probabilistic completeness is asserted.']
  opt(q,'o1','The probability of finding a solution tends to1 as search time tends to infinity','This is the limiting success property for a feasible instance, not a guarantee for every finite run.')
  q['solution']['justification']='On a feasible instance within the planner’s assumptions, success probability approaches1 with unbounded search; infeasible instances cannot satisfy a success guarantee.';q['solution']['simpleExplanation']=q['solution']['justification']
 if sid=='P0121-Q04':
  q['stem']='Which statement matches the lecture’s finite-step optimality caveat for genetic-algorithm path planning?'
  opt(q,'o1','A near-optimal path may be found quickly, without a guarantee of finding the absolute shortest path in finite steps','This preserves the source distinction between useful empirical results and guaranteed finite-step optimality.')
  opt(q,'o2','A near-optimal path found in one run proves that every later run reaches the absolute shortest path in finite steps','A successful or near-optimal run does not prove a universal finite-run guarantee.')
  opt(q,'o3','Absence of a finite-step optimality guarantee means no finite run can ever find a feasible path','A missing guarantee does not make successful finite runs impossible.')
  opt(q,'o4','Probabilistic completeness means every finite run returns the shortest path rather than merely a feasible one','Completeness concerns finding a solution, while optimality concerns its cost; the finite-run claim also overstates the limiting definition.')
 if sid=='P0122-Q01':
  q['stem']='Which mathematical-tool/application pairing is explicitly given in the lecture summary?'
  opt(q,'o2','Graph theory and search: evaluating the eigenvalues of a rigid-body inertia matrix','The summary associates graph search with planning/navigation; eigenvalue methods appear under linear algebra.')
  opt(q,'o3','Complexity analysis: Bayesian estimation of uncertain sensor measurements','The summary assigns Bayesian estimation to probability/statistics and algorithm-performance analysis to complexity.')
  opt(q,'o4','Transforms and control: selecting tree splits using entropy and information gain','The summary associates transforms/control with state-space models; entropy belongs to the uncertainty and decision-tree material.')
 q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
assert all(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']) if q['id'] not in ids)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');packet=[]
for q in b['questions']:
 if q['id'] not in ids:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W01-L03-v3.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print('7 v3 repairs frozen;80 base-batch objects unchanged;2 accepted gaps unchanged.')
