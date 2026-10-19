#!/usr/bin/env python3
"""Repair 21 independent quality flags while preserving 59 accepted hashes."""
from pathlib import Path
import copy,json
from validate import question_hash
R=Path(__file__).resolve().parents[1];p=R/'data/question-batches/W01-L05.json';b=json.loads(p.read_text());old=copy.deepcopy(b)
medium={27,30,40,41,52,57,70,71,72,74,75,79,80};easy={55}
replacements={
3:{'o3':('Vendor-neutral DDS: application interfaces restricted to one middleware supplier','Vendor-neutral support concerns communication middleware without requiring a single supplier; it is not an interface lock-in requirement.')},
21:{'o2':('sensor_msgs/Image for camera calibration parameters; geometry_msgs/Twist for absolute robot position','This confuses pixel image data with calibration, and velocity with position.'),'o3':('sensor_msgs/Image for camera pixels; geometry_msgs/Twist for joint positions','The image pairing fits, but the slide uses Twist for linear and angular velocity, not joint positions.'),'o4':('sensor_msgs/Image for camera pixels; geometry_msgs/Twist for force and torque commands','The image pairing fits, but force and torque are not the velocity quantities in the slide’s Twist example.')},
37:{'o2':('Retrieve the parameter before declaration and treat that read as setting its default','A retrieval does not perform the explicit declaration and default setup shown.'),'o3':('Declare a default and reuse that literal value instead of reading the current parameter','The displayed later get_parameter call obtains the current value rather than simply reusing the initialization literal.'),'o4':('Declare a default and treat each subsequent read as resetting a changed value to that default','Reading the current value is not a reset to the original default.')},
47:{'o4':('Visual geometry: the mass and inertia values used by the physical model','Rendered geometry and mass-related inertial properties are separate fields in the slide.')},
57:{'o2':('Any connected transform is sufficient even when its parent and child frames are reversed','Frame direction matters; the required relation may need inversion rather than direct use.'),'o3':('A transform with matching frame names is sufficient even when its values come from a different sensor calibration','Matching names do not establish that the numerical relation is valid for the actual sensor mounting.')},
64:{'o2':('Loading collision geometry into an RViz RobotModel also starts contact-force integration','Geometry describes shapes; loading a visualization is not starting a dynamics simulation.'),'o3':('Publishing changing transforms to RViz computes the forces that produced those motions','Displaying supplied poses does not solve the forces or dynamics that would produce them.'),'o4':('Setting inertial values in the model makes RViz itself simulate gravity and friction','Physical parameters are inputs a simulator can use; their presence does not turn visualization into a dynamics engine.')},
73:{'o2':('The visual mesh volume, without examining the separately assigned mass data','A visual mesh alone does not establish the model’s assigned mass.'),'o3':('The joint damping value, rather than any mass-related model data','Damping concerns motion resistance, not the direct mass value asked for.'),'o4':('The collision friction setting, rather than any mass-related model data','Friction describes contact resistance, not the direct mass value asked for.')},
76:{'o2':('Middleware selection alone establishes that security is enabled for this deployment','Availability of security mechanisms does not show that this deployment configured them.'),'o3':('A successful average-rate test establishes that every worst-case deadline will be met','Average timing does not establish a worst-case deadline guarantee.'),'o4':('A reliable message-delivery setting establishes a bounded end-to-end execution time','Delivery reliability and bounded processing latency are different properties.')}
}
changed=medium|easy|set(replacements)
assert len(changed)==21
h=R/'audits/batch-history/W01-L05-v1-before-quality-repair.json';assert not h.exists();h.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
for q in b['questions']:
 n=int(q['id'].split('-')[-1])
 if n not in changed:continue
 assert q['version']==1
 q.update(version=2,status='draft',reviewIds=[])
 q['revisionAuthors']=list(dict.fromkeys(q.get('revisionAuthors',[])+['robotics-integration-revision-author']))
 if n in medium:q['difficulty']='medium'
 if n in easy:q['difficulty']='easy'
 for opt in q['options']:
  if opt['id'] in replacements.get(n,{}):
   opt['text'],q['solution']['optionExplanations'][opt['id']]=replacements[n][opt['id']]
before={q['id']:question_hash(q) for q in old['questions']}
assert all(question_hash(q)==before[q['id']] for q in b['questions'] if int(q['id'].split('-')[-1]) not in changed)
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
packet=[{k:q[k] for k in ('id','version','stem','selectionMode','type','difficulty','options','assumptions','citations')} for q in b['questions'] if int(q['id'].split('-')[-1]) in changed]
(R/'audits/blind-W01-L05-v2.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
print('Revised 21 questions; 59 approved hashes unchanged; independent review required.')
