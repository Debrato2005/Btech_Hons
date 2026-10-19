"""One-time source/rationale and distractor repairs, retaining accepted objects."""
from pathlib import Path
import copy,json,hashlib,sys,datetime
from validate import question_hash
R=Path(__file__).resolve().parents[1]
def repair(batch,nums,edit):
 p=R/f'data/question-batches/{batch}.json';b=json.loads(p.read_text());old=copy.deepcopy(b);ids={f'{batch}-Q{x:03d}'for x in nums};preserved={q['id']:question_hash(q)for q in b['questions']if q['id']not in ids};changed=[]
 for q in b['questions']:
  if q['id']not in ids:continue
  edit(q);q['version']+=1;q['status']='draft';q['reviewIds']=[];q['revisionAuthors']=sorted(set(q.get('revisionAuthors',[])+['robotics-integration-residual-repairs']));q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']]for o in q['options']if o['id']not in q['correctOptionIds']];changed.append(q)
 assert preserved=={q['id']:question_hash(q)for q in b['questions']if q['id']not in ids}
 (R/f'audits/batch-history/{batch}-before-residual-repairs.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
 packet=[]
 for q in changed:
  x={k:copy.deepcopy(q[k])for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
  for c in x['citations']:c.pop('evidenceText',None)
  packet.append(x)
 pp=R/f'audits/blind-{batch}-residual-repairs.json';pp.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');m={'batchId':batch,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blindPacketPath':str(pp.relative_to(R)),'blindPacketSha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'questionCount':len(changed),'questions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)}for q in changed],'preservedQuestionHashes':preserved}
 (R/f'audits/{batch}-residual-repairs-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(batch,len(changed),m['blindPacketSha256'])
def opt(q,oid,text,why):
 next(o for o in q['options']if o['id']==oid)['text']=text;q['solution']['optionExplanations'][oid]=why
def e25(q):
 n=int(q['id'][-3:])
 if n==35:
  c=next(c for c in q['citations']if c['physicalPage']==762);c['kind']='statement';c['locator']='Physical page 762: prose goal of critically damped error response; the numerical gains are derived from the error dynamics on pages 764–765.'
 elif n==37:
  q['solution']['optionExplanations']['o4']='This uses (actual inertia / estimated inertia) × u = (2/3) × 4 = 8/3, rather than the required (estimated / actual) × u = (3/2) × 4 = 6.'
  c=next(c for c in q['citations']if c['physicalPage']==769);c['kind']='statement';c['locator']='Physical page 769: prose explaining loss of exact cancellation with inaccurate parameters; the numerical example is derived from the plant and command equations on pages 763–764.'
 elif n==41:
  q['stem']='A position Jacobian J_base maps joint velocity to tool-point velocity in the base frame. The same-point force is measured as F_tool. Define the proper rotation R by v_tool=R v_base. Which rule correctly prepares the force for τ=J_base^T F_base?'
  q['assumptions']=['Both representations concern the same tool point; only a force vector, not a displaced wrench, is involved.','R is orthogonal with R^T R=I; the rule must apply to a general rotation and force, not only special vectors or symmetric rotations.']
  opt(q,'o1','Use F_base=R^T F_tool, or transform the Jacobian consistently to the tool frame.','The coordinate map is defined by v_tool=R v_base; power invariance gives F_base=R^T F_tool, so force and velocity use compatible representations.')
  opt(q,'o4','Use F_base=R F_tool while retaining J_base.','R maps base components to tool components by the stated definition; applying it again to tool force components is not the general inverse map, which is R^T.')
  q['solution']['justification']=q['solution']['simpleExplanation']='The compatible-frame requirement is inferred from the work/power pairing: F_tool^T v_tool = F_tool^T R v_base = (R^T F_tool)^T v_base. Thus F_base=R^T F_tool and τ=J_base^T F_base.'
  q['solution']['steps']=['Use the defined component map v_tool=R v_base.','Equate physical power in both frames: F_base^T v_base=F_tool^T v_tool.','Substitute the velocity map and identify F_base=R^T F_tool.','Use the source transpose mapping with the now-compatible force and Jacobian.']
  for c in q['citations']:c['kind']='equation';c['role']='premise';c['locator']=f"Physical page {c['physicalPage']}: transpose force/torque mapping used as a premise; the frame-compatibility condition is derived here from equal physical power, not quoted as an explicit source statement."
 elif n==54:q['difficulty']='medium'
def e26(q):
 n=int(q['id'][-3:])
 if n==10:opt(q,'o4','Fully transparent and fully opaque, respectively','That interpretation belongs to an alpha/transparency channel, not the stated grayscale intensity convention.')
 elif n==33:opt(q,'o4','Class 0 from the blue point at the larger distance d2','This selects the farther of the two shown points; 1NN uses the smaller distance d1.')
 elif n==41:opt(q,'o4','2, gravel','The numeric row target is 2, but the source maps target 2 to grass, not gravel.')
 elif n==44:
  opt(q,'o2','The outer list represents two one-feature samples; [0] selects the prediction for the first','The shape is one row by two columns, so it represents one two-feature sample, not two samples.')
  opt(q,'o3','The outer list represents one two-feature sample; [0] selects its first input feature','The indexing is applied to the returned prediction array, not to the input feature row.')
  opt(q,'o4','The outer list represents one two-feature sample; predict already returns a scalar so [0] is unnecessary','predict returns a one-element array for this one-row input; [0] extracts its scalar label.')
 elif n==45:
  opt(q,'o2','It reports the fraction of the six training labels that the model predicts correctly','A training score would require comparing predictions against the training labels; the shown call only predicts this new query.')
  opt(q,'o3','It reports accuracy on an independently labeled held-out test set','The query has no supplied true target, so no held-out accuracy has been calculated.')
  opt(q,'o4','It returns the predicted probability assigned to the gravel class','The shown predict call returns a class label, not the per-class probabilities from predict_proba.')
 elif n==49:
  q['stem']='In y_hat=w0*x0+w1*x1+b, which option is the complete set of learned affine-model parameters?'
  opt(q,'o2','w0 and w1 only','These are learned weights, but the complete affine model also includes the learned intercept b.')
  opt(q,'o3','b, x0 and x1','This includes the intercept but replaces learned weights with the current sample input values.')
  opt(q,'o4','y_hat, w0 and w1','The prediction y_hat is an output for a sample, not a learned parameter; this also omits the intercept.')
 elif n==55:
  q['stem']='In the ordinary regression of y on x shown in the figure, what is the purpose of the red fitted line?'
  opt(q,'o4','Minimize squared horizontal x-displacements while treating y as the input','That reverses the stated regression direction; ordinary least squares of y on x minimizes vertical y residuals.')
 elif n==56:
  q['assumptions']=['For the derived direct solution, use an augmented real design matrix A whose columns include the intercept and are linearly independent; θ contains the weights and intercept.','The diagram supplies the squared-error fitting premise; the normal equations below are an explicit derivation, not a printed claim on the slide.']
  q['solution']['justification']=q['solution']['simpleExplanation']='The same squared-error objective can have different solvers. For S(θ)=||Aθ−y||², ∇S=2A^T(Aθ−y). Setting this to zero gives A^T Aθ=A^T y; full column rank makes A^T A invertible, yielding θ=(A^T A)^−1 A^T y without an initial slope.'
  q['solution']['steps']=['Write the explicitly derived objective S(θ)=(Aθ−y)^T(Aθ−y).','Differentiate: ∇S=2A^T(Aθ−y).','At a minimum, solve A^T Aθ=A^T y.','With full column rank, A^T A is positive definite and invertible, so θ=(A^T A)^−1 A^T y.','This establishes a direct mathematical solution under the stated condition; numerically stable implementations can use QR or SVD rather than explicitly forming the inverse. Rank-deficient designs do not justify that inverse formula.']
  q['solution']['formulas']=[{'expression':'S(θ)=||Aθ−y||²; ∇S=2A^T(Aθ−y); A^T Aθ=A^T y','variables':{'A':'augmented design matrix with intercept column','θ':'weights and intercept','y':'target vector','S':'sum of squared residuals'},'units':{'A':'normalized dimensionless features for this derivation','θ,y':'target units','S':'squared target units'},'assumptions':['Full column rank for the unique inverse-form solution; fixed finite dataset and ordinary unweighted squared error.']}]
  q['difficulty']='medium';q['citations'][0]['role']='premise';q['citations'][0]['locator']='Physical page 795: squared-error objective and iterative fitting diagram used as premises for the explicit normal-equation derivation in the solution.'
 elif n==60:opt(q,'o2','A higher-dimensional image tensor cannot be converted into a sample-by-feature matrix','A complete image can be flattened or mapped to extracted features; a structured native representation does not prevent a tabular feature representation.')
repair('W05-L25',[35,37,41,54],e25);repair('W06-L26',[10,33,41,44,45,49,55,56,60],e26)
