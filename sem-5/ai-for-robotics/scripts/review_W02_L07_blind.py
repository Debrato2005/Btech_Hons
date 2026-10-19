"""Independent L07 source observations and answer derivations, before author reveal."""
import json,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'audits/blind-W02-L07.json'
REVIEWER='define_robotics_data_contracts:L07-independent-reviewer'
NOTES={
243:'Printed 1. Lecture Number 7, Manipulator Kinematics, title and institutional marks only.',
244:'Printed 2. Objectives include DOF, homogeneous transformations, DH, FK, PUMA 560 and differential drive. The later lecture may not actually contain the promised PUMA worked example; objectives are not treated as proof of that coverage.',
245:'Printed 3. Four-part outline: introduction, DH parameters, FK and differential drive. Administrative outline only.',
246:'Printed 4. Text contrasts rigid-link joint-chain manipulators with differential-drive robots whose wheel velocities control motion. No additional mechanical diagram.',
247:'Printed 5. Kinematics studies motion without its causing forces, includes time derivatives, and assigns frames to links to track articulation. Lower-right box is blank, not a missing technical figure inferred from extraction.',
248:'Printed 6. FK applications: joint-command Cartesian observations, demonstration joint-to-task-space mapping, collision geometry, differentiable optimization and named simulator examples. Broad implementation claims are survey motivations rather than universal product-version guarantees.'}
for name in ['review_W02_L07_notes.py','review_W02_L07_answers.py']:
 path=ROOT/'scripts'/name
 if path.exists():exec(compile(path.read_text(),str(path),'exec'))
qs=json.loads(PACKET.read_text())
ANSWERS=[{'questionId':qs[n-1]['id'],'questionVersion':qs[n-1]['version'],'questionSha256':qs[n-1].get('questionSha256'),'independentAnswerOptionIds':['choice-'+i for i in ids.split(',')],'reasoning':reason,'solvedBeforeAnswerSeen':True,'uncertainPoints':[]} for n,(ids,reason) in sorted(DERIVED.items())]
def save():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 out={'schemaVersion':'1.0.0','batchId':'W02-L07','reviewerId':REVIEWER,'recordedAt':now,'status':'answers_persisted_before_author_reveal' if len(ANSWERS)==len(qs) else 'blind_review_in_progress','blindPacketPath':str(PACKET.relative_to(ROOT)),'blindPacketSha256':hashlib.sha256(PACKET.read_bytes()).hexdigest(),'exposureStatement':'Read only the frozen blind question/options/citations packet and actual source text/pixels; author batch and author scripts not opened. Independent answers and observations are persisted before revealing author keys.','sourceVersions':{'lectures':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'},'sourceVisualObservations':[{'physicalPage':p,'slideId':f'lectures-p{p:04d}','previewPath':f'sources/previews/lectures/page-{p:04d}.webp','dimensions':[1800,1013],'method':'rendered_page','notes':n} for p,n in NOTES.items()],'answers':ANSWERS}
 (ROOT/'audits/blind-answers-W02-L07-v1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(len(NOTES),'pages and',len(ANSWERS),'blind answers saved')
if __name__=='__main__':
 if (ROOT/'audits/W02-L07-review-summary.json').exists():
  raise SystemExit('Blind provenance is frozen after author reveal; do not regenerate its timestamp.')
 save()
