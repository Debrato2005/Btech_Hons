"""Final pre-freeze author coverage and exact provenance checks; never independent approval."""
from pathlib import Path
import json,sys,copy,random
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import DraftBatch,formula
B='W12-L57';p=R/f'data/question-batches/{B}.json';data=json.loads(p.read_text());b=DraftBatch(B,12,'L57','Demonstration on KUKA KR5 Industrial Robot',1803,data['authorId']);b.questions=data['questions'];b.concepts={x['id']:x for x in data['concepts']}
# Two direct substantive angles not fully exercised by earlier cards.
q=b.add(1809,'motion-family','Motion-family matching','Which mapping distinguishes all four motion families listed in the lecture?', ['PTP: point-to-point joint motion; LIN: Cartesian line; CIRC: circular arc; SPLINE: smooth spline motion.','PTP: Cartesian line; LIN: joint-space point motion; CIRC: circular arc; SPLINE: smooth spline motion.','PTP: point-to-point joint motion; LIN: Cartesian line; CIRC: arbitrary spline; SPLINE: fixed-radius circular arc.','PTP: point-to-point joint motion; LIN: circular arc; CIRC: Cartesian line; SPLINE: smooth spline motion.'],0,'The source lists the four motion categories with their distinct path meanings.',['This keeps the four categories distinct.','PTP and LIN are reversed.','CIRC and SPLINE are reversed.','LIN and CIRC are reversed.'],typ='match',difficulty='easy')
q['citations'][0].update(kind='statement',locator='Lecture L57, physical page 1809, printed footer 7: KRL motion-command list PTP, LIN, CIRC and SPLINE.',role='explicit');random.Random(q['id']+':option-order').shuffle(q['options']);q['difficultyRationale']='Direct source motion-family matching.'
q=b.add(1825,'mask-pipeline','Ordering of mask preprocessing','Which sequence preserves the complete order stated for colour-based detection on p1825?', ['RGB → HSV → Gaussian blur → threshold mask → morphological cleanup → area-filtered contours.','RGB → HSV → contour extraction → Gaussian blur → threshold mask → morphological cleanup.','RGB → threshold mask → HSV → Gaussian blur → area-filtered contours → morphological cleanup.','RGB → HSV → Gaussian blur → morphology on the unthresholded HSV array → threshold mask → contours.'],0,'The printed pipeline blurs before the threshold mask, cleans the mask, and then extracts and filters contours.',['This follows the printed pipeline order.','The contours are obtained after thresholding and cleanup, not before the mask exists.','A binary threshold mask is not the original colour image for the specified HSV conversion.','The source places morphological cleanup after creating the threshold mask.'],typ='match',difficulty='easy')
q['citations'][0].update(kind='statement',locator='Lecture L57, physical page 1825, printed footer 23: full arrow-separated pipeline bullet, including Gaussian blur and area gate.',role='explicit');random.Random(q['id']+':option-order').shuffle(q['options']);q['difficultyRationale']='Direct source pipeline ordering.'
# Exact source kind: p1825 pipeline is a textual bullet, not an image diagram.
for n in [46,48]:
 for c in b.questions[n-1]['citations']:
  if c['physicalPage']==1825:c['kind']='statement'
# Comparison metric's closer, genuinely algorithmic wrong alternative.
q=b.questions[50];next(o for o in q['options'] if o['id']=='o3')['text']='π/8≈0.393.';q['solution']['optionExplanations']['o3']='This uses 2πA/P² instead of the stated 4πA/P².'
q['solution']['misconceptions']=[q['solution']['optionExplanations'][f'o{i}'] for i in range(2,5)]
# Standalone source-equation resource, not only generic transform algebra.
fchain=formula('T_W_R T_R_F(θ1,…,θ6) T_F_TCP T_TCP_O = T_W_R T_R_M T_M_C T_C_O',{'T_A_B':'4×4 homogeneous pose mapping frame B coordinates into A','W':'world frame','R':'robot reference frame','F':'flange frame','TCP':'tool-centre-point frame','O':'object frame','M':'marker frame','C':'camera frame','θ1,…,θ6':'six robot joint angles entering forward kinematics T_R_F'},{'rotation blocks and homogeneous last row':'dimensionless','translation blocks':'one common length unit','θ1,…,θ6':'rad or consistently converted angular units'},['Column-vector transform convention; both chains describe the same object pose; all links and calibration transforms use compatible frames and units.'])
b.questions[62]['solution']['formulas']=[fchain]
fgrasp=formula('T_R_F=T_R_O (T_TCP_O)⁻¹ (T_F_TCP)⁻¹',{'T_A_B':'4×4 rigid transform mapping B coordinates into A','R':'robot reference frame','F':'flange frame','TCP':'tool-centre-point frame','O':'object frame','T_R_O':'desired object pose','T_TCP_O':'specified grasp relationship','T_F_TCP':'calibrated rigid tool transform'},{'rotation blocks and homogeneous last row':'dimensionless','translation blocks':'one common length unit'},['Added desired-pose rearrangement of the source chain; matrix factors do not generally commute.'])
b.questions[65]['solution']['formulas']=[fgrasp]
# Preserve primary documentation actually read, without relying on an empty original repository page.
q=b.questions[55];q['primaryEvidence']=[e for e in q.get('primaryEvidence',[]) if e['url']!='https://github.com/ImtsSrl/openshowvar']
for n,key,url,loc in [(46,'morph','https://docs.opencv.org/4.13.0/d9/d61/tutorial_py_morphological_ops.html','Opening and closing definitions and structuring-element dependence.'),(49,'moments','https://docs.opencv.org/4.13.0/dd/d49/tutorial_py_contour_features.html','Moment centroid ratios, contour area and perimeter.')]:
 b.questions[n-1].setdefault('primaryEvidence',[]).append({'url':url,'locator':loc,'checkedAt':'2026-10-20T00:20:50+00:00'})
primaryp=R/f'audits/{B}-primary-evidence.json';pe=json.loads(primaryp.read_text());pe['records'].pop('cpp',None);pe['records']['morph']=b.questions[45]['primaryEvidence'][-1];pe['records']['moments']=b.questions[48]['primaryEvidence'][-1];primaryp.write_text(json.dumps(pe,ensure_ascii=False,indent=2)+'\n')
# Make correct option identifiers non-positional too, while preserving all explanation bindings.
for q in b.questions:
 rng=random.Random(q['id']+':opaque-option-ids');ids=['o1','o2','o3','o4'];rng.shuffle(ids);mapping=dict(zip(['o1','o2','o3','o4'],ids))
 for o in q['options']:o['id']=mapping[o['id']]
 q['correctOptionIds']=[mapping[i] for i in q['correctOptionIds']]
 q['solution']['optionExplanations']={mapping[k]:v for k,v in q['solution']['optionExplanations'].items()}
 # Every explanation is bound by option ID, not original position.
 q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
 b.concepts[q['conceptIds'][0]]['description']=q['solution']['justification']
b.save()
print('Final draft count',len(b.questions))
