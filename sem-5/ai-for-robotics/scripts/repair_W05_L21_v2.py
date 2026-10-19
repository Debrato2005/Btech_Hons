#!/usr/bin/env python3
"""Version only the twenty independently flagged L21 items; leave accepted hashes intact."""
import copy,datetime,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import formula,SHA
from validate import question_hash,schema_errors
P=R/'data/question-batches/W05-L21.json';A=R/'audits/batch-history/W05-L21-v1-before-repairs.json'
A.parent.mkdir(exist_ok=True)
if not A.exists():A.write_bytes(P.read_bytes())
old=json.loads(A.read_text());data=copy.deepcopy(old);qs={q['id']:q for q in data['questions']}
review=json.loads((R/'data/reviews/W05-L21-v1-independent-contracts.json').read_text())
rows=review['reviews'] if isinstance(review,dict) else review
approved={r['questionId']:r['questionSha256'] for r in rows if r['decision']=='verified'}
summary=json.loads((R/'audits/W05-L21-contracts-review-summary.json').read_text());flagged=set(summary['flaggedQuestionIds'])
AUTHOR='build_offline_study_interface:L21-v2-revision-author'
assert len(approved)==52 and len(flagged)==20
# Refuse to discard concurrent edits: the current file must match either the original or this repair identity/version.
current=json.loads(P.read_text())
for q in current['questions']:
 if q['id'] not in flagged:assert question_hash(q)==approved[q['id']],q['id']
 else:assert q['version']==1 or (q['version']==2 and AUTHOR in q.get('revisionAuthors',[])),q['id']
def q(n):return qs[f'W05-L21-Q{n:03d}']
def opt(n,oid,text,why):
 item=q(n);next(o for o in item['options'] if o['id']==oid)['text']=text;item['solution']['optionExplanations'][oid]=why
for id in flagged:
 item=qs[id];item['version']+=1;item['status']='draft';item['reviewIds']=[];item['revisionAuthors']=list(dict.fromkeys(item.get('revisionAuthors',[])+[AUTHOR]))
for n in [9,10,33,44,47,55,62,67]:q(n)['difficulty']='easy'
q(8)['solution']['formulas']=copy.deepcopy(q(4)['solution']['formulas'])
opt(19,'o2','The phrase still ranks critical damping fastest when the comparison allows a specified nonzero overshoot.','Allowing oscillation/overshoot changes the comparison class; an underdamped design can reach a chosen response criterion sooner.')
opt(19,'o4','The phrase guarantees the minimum 2% settling time for every initial position and velocity at that natural frequency.','Initial-condition coefficients and the chosen settling band affect a specific settling-time comparison; the source shorthand is not that universal optimization claim.')
opt(23,'o1','The response can be approximated by an exponential with decay rate equal to the mean of the two pole magnitudes, 10.5 s⁻¹.','A weighted modal sum does not acquire the arithmetic-mean pole; with the slow coefficient zero the remaining mode decays at 20 s⁻¹.')
opt(23,'o2','The −1 s⁻¹ term dominates at sufficiently late time even when its coefficient is exactly zero.','Late-time dominance requires that the slow mode actually be present; zero weight means no contribution at any time.')
opt(23,'o4','An exactly zero slow coefficient has the same late-time consequence as an arbitrarily small but nonzero slow coefficient.','A nonzero slow mode can eventually dominate a faster mode, whereas an exactly absent slow mode cannot.')
opt(25,'o4','A=c₁+c₂ and B=−i(c₁−c₂).','This reverses the sine sign obtained from e^(iμt)=cos(μt)+i sin(μt) and e^(−iμt)=cos(μt)−i sin(μt).')
opt(30,'o3','A nonzero free response grows without bound because undamped systems can resonate.','Resonant growth requires suitable external forcing; this question specifies free response, whose finite initial-condition sinusoid remains bounded but does not decay.')
q(38)['assumptions']=['Use the characteristic polynomial ms²+b′ s+k′=0 with m>0; strict asymptotic stability is stronger than bounded motion for selected initial states.']
q(38)['solution']['formulas']=[formula('ms²+b′ s+k′=0; s₁,₂=[−b′±√(b′²−4mk′)]/(2m)',{'m':'positive physical mass','b′':'effective damping coefficient including direct feedback','k′':'effective stiffness including direct feedback','s':'complex characteristic rate','s₁,s₂':'two characteristic poles'},{'m':'kg','b′':'N·s/m','k′':'N/m','s,s₁,s₂':'s⁻¹'},['Constant real coefficients; strict asymptotic stability requires b′>0 and k′>0 when m>0.'])]
q(43)['solution']['formulas']=[formula('mẍ+bẋ+kx=f; f=m̂f′+b̂ẋ+k̂x; mẍ=m̂f′+(b̂−b)ẋ+(k̂−k)x',{'m':'true positive mass','m̂':'controller estimate of mass','b':'true viscous damping coefficient','b̂':'controller estimate of viscous damping','k':'true spring stiffness','k̂':'controller estimate of stiffness','x':'actual displacement used by the plant and compensation','ẋ':'actual velocity used by the plant and compensation','ẍ':'actual acceleration','f':'physical actuator force','f′':'normalized servo acceleration command'},{'m,m̂':'kg','b,b̂':'N·s/m','k,k̂':'N/m','x':'m','ẋ':'m/s','ẍ,f′':'m/s²','f':'N'},['The same actual state is used in compensation; no additional external force; exact estimates are not assumed.'])]
opt(44,'o1','20 s⁻¹.','This uses 4√25 instead of the stated critical relation 2√25, doubling the required damping gain.')
opt(48,'o1','The partitioned force expands to (−16x−8ẋ)+x=−15x−8ẋ.','This omits the positive damping compensation ẋ, so its velocity coefficient does not equal the direct design’s −7.')
opt(48,'o3','The partitioned force expands to (−16x−8ẋ)−(x+ẋ)=−17x−9ẋ.','This reverses both compensation signs; the source adds β=x+ẋ.')
# Replace the redundant three-signal recall with the independently requested integrated underdamped response.
item=q(49);oldcid=item['conceptIds'][0]
item.update(stem='A free mass–spring–damper system has m=2 kg, b=4 N·s/m and k=10 N/m, with x(0)=0.2 m and ẋ(0)=0.4 m/s. Which complete underdamped response satisfies both the model and these initial conditions? In each expression t is in seconds and x is in metres.',type='numerical',difficulty='medium',cognitiveSkill='numerical',subtopic='Complete underdamped response from physical parameters and initial state',tags=['underdamped-initial-response'],conceptIds=['W05-L21-C-underdamped-initial-response'],assumptions=['Free response of the stated constant-coefficient linear model; t≥0; trigonometric arguments use radians.'])
item['options']=[{'id':'o1','text':'x(t)=e^(−t)[0.2 cos(2t)+0.3 sin(2t)].'},{'id':'o2','text':'x(t)=e^(−t)[0.2 cos(2t)+0.2 sin(2t)].'},{'id':'o3','text':'x(t)=e^(−t)[0.2 cos(√5 t)+(0.6/√5) sin(√5 t)].'},{'id':'o4','text':'x(t)=e^(−2t)[0.2 cos(2t)+0.4 sin(2t)].'}]
item['correctOptionIds']=['o1']
item['citations']=[{'slideId':f'lectures-p{p:04d}','sourceId':'lectures','sourceSha256':SHA,'physicalPage':p,'kind':'equation','locator':f'Lecture 21, physical PDF page {p}, actual printed footer {p-636}: '+loc,'evidenceText':(R/f'sources/text/lectures/page-{p:04d}.txt').read_text().strip(),'role':'premise','region':None} for p,loc in [(649,'real cosine/sine form of conjugate modes'),(650,'real amplitude-phase form and atan2'),(651,'mass/damping/stiffness to decay and damped frequency')]]
item['solution']={'justification':'Normalize 2ẍ+4ẋ+10x=0 to ẍ+2ẋ+5x=0. Its poles are −1±2i, so x=e^(−t)[A cos(2t)+B sin(2t)]. The initial position gives A=0.2; ẋ(0)=−A+2B=0.4 gives B=0.3. Thus the selected expression meets both the differential equation and initial conditions.','optionExplanations':{'o1':'λ=−1 s⁻¹, μ=2 rad/s, A=0.2 m and B=(0.4+0.2)/2=0.3 m.','o2':'This sets B=ẋ(0)/μ and ignores the λA contribution from differentiating the exponential; its initial velocity is −0.2+0.4=0.2 m/s.','o3':'This substitutes the undamped natural frequency √5 for the damped frequency 2. It matches the chosen initial state but does not solve ẍ+2ẋ+5x=0.','o4':'This uses decay −b/m=−2 instead of −b/(2m)=−1. Its adjusted sine coefficient gives the initial velocity, but its poles do not match the stated plant.'},'steps':['Divide the physical equation by m: ẍ+2ẋ+5x=0.','Compute ω_n=√5 rad/s and ζ=1/√5, hence λ=−ζω_n=−1 s⁻¹ and μ=ω_n√(1−ζ²)=2 rad/s.','Use the source real-mode form x=e^(λt)[A cos(μt)+B sin(μt)].','At t=0, A=x(0)=0.2 m and ẋ(0)=λA+μB=0.4 m/s.','Solve B=(0.4−(−1)(0.2))/2=0.3 m.','Optional equivalent amplitude-phase form: r=√(0.2²+0.3²)=√0.13≈0.360555 m and δ=atan2(0.3,0.2)≈0.982794 rad, giving x=r e^(−t)cos(2t−δ).'],'formulas':[formula('ω_n=√(k/m); ζ=b/(2√(km)); λ=−b/(2m); μ=√(k/m−λ²); x(t)=e^(λt)[A cos(μt)+B sin(μt)]; A=x₀; B=(v₀−λx₀)/μ; r=√(A²+B²); δ=atan2(B,A)',{'m':'positive mass','b':'positive viscous damping coefficient','k':'positive spring stiffness','ω_n':'undamped natural angular frequency','ζ':'damping ratio','λ':'negative real part of each underdamped pole','μ':'positive damped oscillation angular frequency','x(t)':'free displacement response','t':'elapsed time','x₀':'initial displacement x(0)','v₀':'initial velocity ẋ(0)','A':'real cosine-mode displacement coefficient','B':'real sine-mode displacement coefficient','r':'positive oscillation-envelope coefficient','δ':'phase in the form cos(μt−δ)'},{'m':'kg','b':'N·s/m','k':'N/m','ω_n,μ':'rad/s','ζ':'dimensionless','λ':'s⁻¹','x,x₀,A,B,r':'m','v₀':'m/s','t':'s','δ':'rad'},['Constant coefficients, free response, m,k>0 and 0<b<2√(mk); A and B are real trigonometric coefficients, not the earlier complex-exponential coefficients.'])],'simpleExplanation':'The damping determines the exponential decay, stiffness and mass determine the oscillation rate, and both initial displacement and velocity determine the two real amplitudes. The velocity condition includes the derivative of the exponential.','memoryAid':'Differentiate both the envelope and the sine/cosine part before applying initial velocity.','misconceptions':[],'examTraps':['Undamped frequency is not the damped frequency.','The initial velocity is λA+μB, not just μB.'],'prerequisiteConceptIds':[]}
for c in data['concepts']:
 if c['id']==oldcid:c['questionIds'].remove(item['id'])
data['concepts'].append({'id':item['conceptIds'][0],'title':item['subtopic'],'description':item['solution']['justification'],'slideIds':[c['slideId'] for c in item['citations']],'questionIds':[item['id']],'status':'drafted','topic':item['topic'],'subtopic':item['subtopic'],'prerequisiteConceptIds':[],'examinationAngles':['numerical','initial-condition synthesis','damped versus undamped frequency']})
q(53)['solution']['formulas']=[formula('e=x_d−x; ė=ẋ_d−ẋ; f′=k_v ė+k_p e; ẍ=f′; ë+k_v ė+k_p e=ẍ_d',{'x_d':'desired displacement','ẋ_d':'desired velocity','ẍ_d':'desired acceleration','x':'actual displacement','ẋ':'actual velocity','ẍ':'actual acceleration','e':'desired-minus-actual position error','ė':'error velocity','ë':'error acceleration','f′':'modified normalized acceleration command without desired-acceleration feedforward','k_v':'normalized velocity-error gain','k_p':'normalized position-error gain'},{'x_d,x,e':'m','ẋ_d,ẋ,ė':'m/s','ẍ_d,ẍ,ë,f′':'m/s²','k_v':'s⁻¹','k_p':'s⁻²'},['This is the question’s deliberately modified law, not the source’s full feedforward law; ideal compensated plant, smooth desired trajectory and no external force.'])]
opt(55,'o2','A chosen pair of stable poles uniquely fixes the same settling time for all initial position and velocity errors.','The pole locations set modal rates, but initial-condition coefficients and the settling criterion affect a particular observed settling time.')
opt(55,'o4','A finite stable pole choice from the ideal equation is sufficient to certify actuator feasibility without checking the commanded force.','Even finite requested poles may require force beyond actuator limits for the intended initial state or trajectory.')
q(57)['solution']['formulas']=[formula('e=x_d−x; f′=ẍ_d+k_v ė+k_p e; ẍ=f′+F_ext/m; ë+k_v ė+k_p e=−F_ext/m',{'F_ext':'signed additive external physical force in the actual-motion positive direction','m':'positive actual mass','x_d':'desired displacement','ẍ_d':'desired acceleration','x':'actual displacement','ẍ':'actual acceleration','e':'desired-minus-actual displacement error','ė':'first error derivative','ë':'second error derivative','f′':'normalized servo acceleration command','k_v':'normalized velocity-error gain','k_p':'normalized position-error gain'},{'F_ext':'N','m':'kg','x_d,x,e':'m','ė':'m/s','ẍ_d,ẍ,ë,f′':'m/s²','k_v':'s⁻¹','k_p':'s⁻²'},['This question explicitly uses an ADDITIVE physical force, unlike the resisting-force sign in the source diagram; model compensation is otherwise exact.'])]
opt(72,'o4','The differentiated model permits e(0), ė(0), ë(0) and z(0) to be chosen independently without checking the original equation.','They must satisfy ë(0)+k_v ė(0)+k_p e(0)+k_i z(0)=d(0) on an appropriate smooth initial interval; the stored integrator state is not an independent fourth free datum.')
for id in flagged:
 item=qs[id];item['solution']['misconceptions']=[item['solution']['optionExplanations'][o['id']] for o in item['options'] if o['id'] not in item['correctOptionIds']]
for id,h in approved.items():assert question_hash(qs[id])==h,id
assert data['sourceIssues']==old['sourceIssues']
# Update only reciprocal concept/slide records affected by replacing Q049.
inspection_path=R/'data/inspection-batches/W05-L21.json';ins=json.loads(inspection_path.read_text())
for s in ins['slides']:s['conceptIds']=[c['id'] for c in data['concepts'] if s['id'] in c['slideIds']]
for typ,entries in [('question',data['questions']),('concept',data['concepts']),('slide',ins['slides'])]:
 schema=json.loads((R/f'data/schema.{typ}.json').read_text());errs=[err for entry in entries for err in schema_errors(entry,schema)];assert not errs,(typ,errs)
P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');inspection_path.write_text(json.dumps(ins,ensure_ascii=False,indent=2)+'\n')
revisions=[q for q in data['questions'] if q['id'] in flagged];packet=[]
for item in revisions:
 a={k:copy.deepcopy(item[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in a['citations']:c.pop('evidenceText',None)
 packet.append(a)
packetpath=R/'audits/blind-W05-L21-v2.json';packetpath.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
manifest={'batchId':'W05-L21','revisionAuthor':AUTHOR,'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revisedQuestionCount':len(revisions),'preservedApprovedCount':len(approved),'preservedApprovedHashes':approved,'sourceIssuesPreserved':True,'blindPacketPath':str(packetpath.relative_to(R)),'blindPacketSha256':hashlib.sha256(packetpath.read_bytes()).hexdigest(),'revisions':[{'questionId':q['id'],'questionVersion':q['version'],'questionSha256':question_hash(q)} for q in revisions],'coverageRepair':'Q049 replaces duplicated three-signal recall with integrated underdamped response from m,b,k and both initial conditions, including optional amplitude/phase. Existing Q050 retains trajectory-signal concept coverage.','independentReviewRequired':True}
(R/'audits/W05-L21-v2-repair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
coverage=json.loads((R/'audits/W05-L21-author-coverage-ledger.json').read_text())
for row in coverage['pages']:
 sid=row['slideId'];row['conceptIds']=[c['id'] for c in data['concepts'] if sid in c['slideIds']];row['questionIds']=[q['id'] for q in data['questions'] if any(c['slideId']==sid for c in q['citations'])]
coverage['status']='Version 2 author proposal after independent flags; 52 accepted hashes preserved, 20 revisions require re-review.'
(R/'audits/W05-L21-author-coverage-ledger-v2.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['revisedQuestionCount','preservedApprovedCount','blindPacketSha256','coverageRepair']}))
