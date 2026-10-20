"""Finalize source qualifications/coverage and readable prose before first L59 review."""
from pathlib import Path
import json,sys,hashlib,re
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from authoring_helpers import SHA
from inspect_W12_L59 import save,NOTES,EX
B='W12-L59';bp=R/f'data/question-batches/{B}.json';b=json.loads(bp.read_text())
# Individual numerical/symbol context remains declared. No formula or answer rewrites here.
for q in b['questions']:
 for k in ['stem']:
  q[k]=q[k].replace('of the2D','of the 2D').replace('Its2D','Its 2D').replace('the2D','the 2D').replace('at3.25x','at 3.25x')
 for o in q['options']:o['text']=o['text'].replace('Its2D','Its 2D').replace('the2D','the 2D')
 if q['type'] in ('numerical','derivation'):
  assert q['solution']['steps'] and q['solution']['formulas'],q['id']
 if 'conflictResolution' in q:
  q['conflictResolution']['basis']=q['solution']['justification']
  assert q['conflictResolution']['physicalPages'],q['id']
 assert set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']}
 assert len({o['text'] for o in q['options']})==4
bp.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');save(complete=True)
rows=[]
for p in range(1877,1909):
 linked=[q['id'] for q in b['questions'] if any(c['physicalPage']==p for c in q['citations'])];cs=[c['id'] for c in b['concepts'] if f'lectures-p{p:04d}' in c['slideIds']]
 assert p in EX or linked,(p,'No substantive coverage')
 rows.append({'physicalPage':p,'printedFooter':p-1876,'disposition':'excluded' if p in EX else 'drafted-awaiting-independent-review','exclusionReason':EX.get(p),'conceptIds':cs,'questionIds':linked,'actualObservation':NOTES[p]})
(R/f'audits/{B}-author-coverage.json').write_text(json.dumps({'batchId':B,'actualPagesInspected':32,'substantivePages':26,'questionCount':65,'conceptCount':len(b['concepts']),'pages':rows,'sourceCodePresent':False,'sourceImplementationReproduced':False,'boundedCoverageClaim':'Every substantive page has source-bound draft questions. This is author coverage only; independent correctness/quality and complete-coverage challenge remain pending.','integratedAngles':['Encoder counts through exact constant-curvature pose','Uniform wheel-rate feasibility scaling preserving curvature','Camera point using aligned depth and explicit calibration','Frame transform order and numerical composition','Scalar uncertainty update and particle probability normalization','Cost/feasibility route selection and finite-footprint corridor margin','Cross-layer load-response diagnosis']},ensure_ascii=False,indent=2)+'\n')
issues={'batchId':B,'sourceId':'lectures','sourceSha256':SHA,'questionBoundQualifications':{q['id']:q['conflictResolution'] for q in b['questions'] if 'conflictResolution' in q},'additionalSourceBoundaries':[{'physicalPages':[1880],'note':'The classical/AI comparison is a teaching contrast; this robot explicitly combines both approaches.'},{'physicalPages':[1889],'note':'No numerical extrinsics or automatic calibration method supplied; lower sensor tree shorthand not expanded into an invented actual TF graph.'},{'physicalPages':[1898],'note':'Node/executable shorthand does not document actual runtime process layout; ROS primary-doc access returned an access-denied page, so no retrieved implementation claim is attached.'},{'physicalPages':[1899],'note':'Conceptual sequential arrows are not treated as exact server scheduling or plugin configuration.'},{'physicalPages':[1900],'note':'Detection score is not shown calibrated; valid aligned depth, scale and calibration are explicitly added in numerical example.'},{'physicalPages':[1902],'note':'Robot Decision label repeats twice; no distinct second algorithm inferred.'},{'physicalPages':[1903],'note':'Pane labelled Terminal visibly shows properties/entities; no terminal command or original listing inferred.'},{'physicalPages':[1903,1904,1905],'note':'Only static PDF frames inspected; playback factors are not measured robot speed, latency, success rate or video execution.'}], 'implementationBoundary':'No executable source code, launch files, calibration values or original package/commit is provided. Added deterministic calculations are not a reproduction of the robot demonstration.','externalDocumentationReadStatus':{'denied':['https://docs.ros.org/en/humble/Concepts/Basic/About-Nodes.html','https://docs.ros.org/en/noetic/api/robot_localization/html/index.html','https://www.ros.org/reps/rep-0105.html'],'reason':'Returned Anubis Access Denied pages. No retry or alternative route used.','otherFailure':'https://docs.nav2.org/concepts/index.html returned404; not relied on.'},'globalSourceResolution':False}
(R/f'audits/{B}-source-issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2)+'\n');(R/f'audits/{B}-primary-evidence.json').write_text(json.dumps({'sourceId':'lectures','sourceSha256':SHA,'actualSourcePages':list(range(1877,1909)),'externalVerifiedContent':[],'note':'Questions are grounded in the supplied source pixels and explicitly derived/added math. Failed/denied external reads are not cited as evidence.'},indent=2)+'\n')
print('Coverage and source boundaries finalized')
