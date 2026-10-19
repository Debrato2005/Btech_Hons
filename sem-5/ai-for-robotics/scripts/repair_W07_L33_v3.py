"""One-time five-item v3 authoring, preserving all78 accepted hashes."""
from pathlib import Path
import json,hashlib,copy,datetime
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W07-L33.json';b=json.loads(p.read_text());before=copy.deepcopy(b);summary=json.loads((R/'audits/W07-L33-v2-contracts-review-summary.json').read_text());qs={int(q['id'].split('Q')[-1]):q for q in b['questions']};changed=[5,7,50,74,78];(R/'audits/batch-history/W07-L33-pre-v3.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
def replace(n,stem,options,why):
 q=qs[n];q['stem']=stem
 for o,text in zip(sorted(q['options'],key=lambda o:o['id']),options):o['text']=text
 q['solution']['optionExplanations']={f'o{i+1}':x for i,x in enumerate(why)}
replace(5,'Which pair of causes is specifically illustrated by the car partly behind the tree and the same red ball under bright versus dim lighting?',[
 'Car: occlusion; ball: illumination change.','Car: perspective scale change; ball: illumination change.','Car: occlusion; ball: change in surface reflectance.','Car: perspective scale change; ball: change in surface reflectance.'],[
 'The tree hides part of the car, while the light source changes the same ball’s appearance.','The car panel illustrates a foreground obstruction, not a change in camera-object distance.','The ball panel changes lighting, not the ball’s material reflectance.','Both diagnoses replace the actual illustrated changes with different mechanisms.'])
replace(7,'For the sign example, which pair matches the slide’s segmentation task and robustness criterion?',[
 'Assign letter identities to the mask; assess degradation when imaging assumptions weaken.','Separate foreground regions; assess accuracy only under the nominal imaging assumptions.','Separate foreground regions; assess degradation when imaging assumptions weaken.','Assign letter identities to the mask; assess accuracy only under the nominal imaging assumptions.'],[
 'The degradation criterion fits, but the segmentation result does not itself assign letter identities.','Foreground separation fits, but nominal-condition accuracy alone does not assess robustness to violated assumptions.','This combines the stated region partition with graceful degradation under violated assumptions.','Letter recognition is a separate operation, and nominal-only accuracy does not test the stated robustness.'])
replace(50,'Which representation best describes the right-hand result in the inspected street-scene comparison?',[
 'An intensity histogram that retains gray-value frequency but discards spatial position.','A dense appearance image that retains local shading and surface texture.','A set of isolated interest-point locations and their local descriptors.','Selected image-boundary positions and orientations, with much of the shading and texture omitted.'],[
 'The result preserves a spatial drawing of boundaries, not merely intensity-frequency counts.','Large filled intensity regions and much texture are removed in the line rendering.','The shown structures are extended lines and outlines rather than isolated point markers.','The right-hand drawing retains geometric boundary structure while suppressing much appearance detail.'])
q=qs[74]
for c in q['citations']:
 if c['physicalPage']==1001:c['role']='premise'
q['conflictResolution']={'status':'explicit-qualification-awaiting-independent-review','sourceClaim':'Pages1014 and1018 broadly group point features, including Harris, under scale robustness/invariance.','basis':'Page1015 explicitly motivates scale-space search because a fixed-scale corner can change into an edge; ordinary fixed-scale Harris is not by itself a scale-invariant cross-view matcher.','method':'Use the explicitly stated touching-mask and scale-change assumptions, keep candidates distinct from guaranteed correspondences, and retain the source qualification.'}
q['primaryEvidence']=copy.deepcopy(qs[65].get('primaryEvidence',[]))
for o in qs[78]['options']:
 o['text']={'o1':'t=0.','o2':'t=1.','o3':'t=2.','o4':'All three thresholds tie.'}[o['id']]
for n in changed:
 q=qs[n];q['version']+=1;q['status']='draft';q['reviewIds']=[];q.setdefault('revisionAuthors',[]).append('robotics-integration-L33-v3-reviser');q['solution']['misconceptions']=[q['solution']['optionExplanations'][o['id']] for o in q['options'] if o['id'] not in q['correctOptionIds']]
hashq=lambda q:hashlib.sha256(json.dumps({k:v for k,v in q.items() if k not in ('status','reviewIds')},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
for q in b['questions']:
 if q['id'] in summary['acceptedQuestionHashes']:assert hashq(q)==summary['acceptedQuestionHashes'][q['id']],q['id']
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');packet=[]
for n in changed:
 q=qs[n];x={k:copy.deepcopy(q[k]) for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')}
 for c in x['citations']:c.pop('evidenceText',None)
 packet.append(x)
pf=R/'audits/blind-W07-L33-v3.json';pf.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n');m={'frozenAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packet':str(pf.relative_to(R)),'packetSha256':hashlib.sha256(pf.read_bytes()).hexdigest(),'questionHashes':{qs[n]['id']:hashq(qs[n]) for n in changed},'acceptedPreserved':78,'fixes':{'Q005':'Parallel occlusion/perspective and illumination/reflectance pairs.','Q007':'Parallel segmentation/recognition and robustness/nominal-accuracy pairs.','Q050':'Parallel common image representations.','Q074':'Explicit Harris scale qualification and corrected p1001 premise role.','Q078':'Removed all supplied variance scores; histogram calculation now required.'},'sourceReinspection':'Actual pages992,994,1008 revisited2026-10-19T21:04:33Z; remaining source premises and arithmetic retained from previously inspected/reviewed versions.'};(R/'audits/W07-L33-v3-repair-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(m['packetSha256'])
