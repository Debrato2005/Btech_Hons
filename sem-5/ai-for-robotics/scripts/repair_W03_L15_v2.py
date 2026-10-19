from pathlib import Path
import json,copy,datetime
from validate import question_hash
from authoring_helpers import formula,SHA
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W03-L15.json';b=json.loads(p.read_text());old=copy.deepcopy(b);ids={4,5,6,17,23,24,25,28,30,32,33,34,35,37,43,45,49};a=R/'audits/batch-history/W03-L15-v1-before-quality-repair.json';assert not a.exists();a.write_text(json.dumps([q for q in b['questions'] if int(q['id'][-3:]) in ids],ensure_ascii=False,indent=2)+'\n')
def choice(q,k,text,why=None):
 next(o for o in q['options'] if o['id']==k)['text']=text
 if why:q['solution']['optionExplanations'][k]=why

def cite(q,page,lecture,printed,kind='equation'):
 q['citations'].append(dict(slideId=f'lectures-p{page:04d}',sourceId='lectures',sourceSha256=SHA,physicalPage=page,kind=kind,locator=f'Lecture {lecture}, physical PDF page {page}, printed slide {printed}: defining premise',evidenceText=(R/f'sources/text/lectures/page-{page:04d}.txt').read_text().strip(),role='premise',region=None))
 for c in b['concepts']:
  if c['id'] in q['conceptIds'] and f'lectures-p{page:04d}'not in c['slideIds']:c['slideIds'].append(f'lectures-p{page:04d}')
full=formula('τ=M(q)qddot+V(q,qdot)+G(q)+F_f(q,qdot); qddot=M(q)⁻¹[τ−V−G−F_f]',{'τ':'applied joint-effort vector','M':'joint inertia matrix','q':'joint-position vector','qdot':'joint-rate vector','qddot':'joint-acceleration vector','V':'velocity-dependent joint effort','G':'gravity joint effort','F_f':'compensating joint friction effort, source symbol F, not a Cartesian wrench'},{'τ,V,G,F_f':'N·m for revolute coordinates; N for prismatic coordinates','M_ij':'effort unit of coordinate i divided by acceleration unit of coordinate j','q':'rad for revolute coordinates; m for prismatic coordinates','qdot':'rad/s or m/s','qddot':'rad/s² or m/s²'},['M is nonsingular; all loads and coordinates use compatible conventions.'])
for q in b['questions']:
 n=int(q['id'][-3:])
 if n not in ids:continue
 assert q['version']==1;h=question_hash(q);author='robotics-integration-L15-v2-revision-author';q.update(version=2,status='draft',reviewIds=[]);q.setdefault('revisionAuthors',[]).append(author);q.setdefault('revisionHistory',[]).append({'version':2,'authorId':author,'priorQuestionSha256':h,'reason':'Repair independently identified rationale, self-contained metadata, sign convention and source-premise issues.','revisedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 if n==4:
  choice(q,'o2','A constant M22 implies that every entry of M is constant','One constant entry does not make the configuration-dependent off-diagonal and M11 terms constant.')
  choice(q,'o3','M must depend on θ1 because the same model’s gravity vector depends on θ1','Different dynamics terms can depend on different coordinate subsets; this M contains θ2 but not θ1.')
  choice(q,'o4','M22 must vary with θ2 because θ2 is one of the model’s coordinates','The displayed M22=m2l2² does not contain θ2; coordinate membership does not force entrywise dependence.')
 if n==5:q['assumptions']=['Use the locations explicitly marked by m1 and m2 in the cited two-link source diagram.']
 if n==6:choice(q,'o4','[[8,3],[3,3]]','This uses l2=1 instead of2: M11=3+5=8, and M12=M21=M22=3.')
 if n==17:
  cite(q,460,15,11);q['solution']['justification']='The slide uses τ=JᵀF with matching components; if v=Jqdot, then τᵀqdot=(JᵀF)ᵀqdot=Fᵀv. Thus F is paired with the task velocity represented by that J.';q['solution']['simpleExplanation']=q['solution']['justification'];q['solution']['steps']=['Use the matching task velocity v=Jqdot.','Substitute τ=JᵀF into joint power τᵀqdot.','Obtain τᵀqdot=FᵀJqdot=Fᵀv.'];choice(q,'o2','Any vector of the same length as F, regardless of the Jacobian’s velocity mapping','Matching dimensions alone do not establish the velocity/effort power relation.')
 if n in [23,24,25,32,33,34,35]:
  for f in q['solution']['formulas']:
   f['variables'].update({'qdot':'joint-rate vector','M':'joint inertia matrix','V':'velocity-dependent joint effort vector','G':'gravity joint effort vector'})
   f['units'].update({'qdot':'rad/s for revolute coordinates; m/s for prismatic coordinates','Jdot':'the corresponding J entry unit per second','M_ij':'joint-effort unit i divided by joint-acceleration unit j','V,G':'N·m for revolute coordinates; N for prismatic coordinates'})
 if n==28:choice(q,'o4','[[1,0],[−2,1]]','This leaves the second row doubled instead of dividing it by the diagonal2.')
 if n==30:
  cite(q,358,11,7);q['solution']['steps']=['Let R map tool components to inertial components, so v=R v_T.','Differentiate: a=R dot(v_T)+dot(R)v_T.','The source derivative-of-a-rotating-vector identity gives Rᵀdot(R)v_T=ω_T×v_T.','Premultiply by Rᵀ to obtain a_T=dot(v_T)+ω_T×v_T.'];q['assumptions'].append('R maps the rotating tool basis into inertial axes; this is the derivative of a free velocity vector, not a relative-position derivative with an unmodelled origin motion.')
 if n==32:choice(q,'o3','(−54,3) N','This is J⁻ᵀV without the Jacobian-derivative correction: [[1,−1],[0,1/2]](−48,6)ᵀ=(−54,3)ᵀ.')
 if n==34:cite(q,462,15,13)
 if n==35:
  choice(q,'o2','Only J⁻ᵀ is needed; the original velocity coefficients can be carried over without differentiating J','The acceleration substitution includes Jdot qdot, so an effort transformation alone misses a velocity-dependent contribution.')
  choice(q,'o3','The acceleration substitution adds +MJ⁻¹Jdot qdot to the original joint velocity term','Solving xddot=Jqddot+Jdot qdot gives a minus correction when qddot is substituted.')
  choice(q,'o4','Bx and Cx differ solely because the coordinate-dependent inertia is differentiated with respect to time in τ=Mqddot','This transformation comes from differentiating the velocity mapping, not inserting an Mdot term into the stated joint equation.')
 if n==37:q['assumptions'].append('The displayed positive terms are compensating actuator efforts c sgn(qdot) and v qdot; actual resisting friction torque has the opposite sign, with c,v≥0 and nonzero sliding velocity.')
 if n in [43,45,49]:q['solution']['formulas']=[copy.deepcopy(full)]
 if n==45:q['solution']['formulas'].append(formula('x=[q;v]; xdot=[v; M(q)⁻¹(τ−V(q,v)−G(q)−F_f(q,v))]',{'x':'stacked position and velocity state','q':'joint positions','v':'joint rates, equal to qdot','xdot':'state time derivative','M':'joint inertia','τ':'applied effort','V,G,F_f':'velocity, gravity and compensating friction efforts'},{'q':'rad or m by joint type','v':'rad/s or m/s','xdot blocks':'joint-rate units; joint-acceleration units','M_ij':'effort unit i divided by acceleration unit j','τ,V,G,F_f':'N·m or N by joint type'},['Use matching coordinate and effort conventions; M nonsingular.']))
 q['solution']['misconceptions']=[v for k,v in q['solution']['optionExplanations'].items() if k not in q['correctOptionIds']]
assert sum(question_hash(q)==question_hash(o) for q,o in zip(b['questions'],old['questions']))==32
b.setdefault('sourceIssues',[]).append({'sourceId':'lectures','sourceSha256':SHA,'physicalPage':462,'printedSlideNumber':'13','issue':'The final Vx argument label displays joint acceleration although the expanded right-hand side depends on q and qdot.','treatment':'Retain the visible argument-label typo; use the explicit velocity-dependent expression and qualified rotating-component convention, not a global source correction.'})
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');packet=[]
for q in b['questions']:
 if int(q['id'][-3:]) not in ids:continue
 x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
(R/'audits/blind-W03-L15-v2.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');print('17 repairs saved;32 accepted hashes unchanged.')
