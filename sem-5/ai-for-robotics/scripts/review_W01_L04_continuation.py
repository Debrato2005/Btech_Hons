"""Persist only the continuation reviewer's independently observed L04 evidence.
The original 83 solves/36 inspections are immutable and separately attributed.
Do not regenerate after the author answer has been revealed.
"""
import hashlib,json,datetime,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
assert not (ROOT/'audits/W01-L04-author-reveal.json').exists(), 'Blind evidence is frozen; author answers have been revealed.'
P=ROOT/'audits/blind-answers-W01-L04-v1-continuation.json'
OLD=ROOT/'audits/blind-answers-W01-L04-v1.json'
assert hashlib.sha256(OLD.read_bytes()).hexdigest()=='50b0106805308529ca51b0a49f2f475a57917bb6fbbb7bc7a631dbe4e346fa5e'
R='define_robotics_data_contracts:L04-continuation-reviewer'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
if P.exists():
 d=json.loads(P.read_text());assert not d.get('authorAnswerRevealed')
else:
 d={'reviewerId':R,'packetSha256':'e3c0f4d0b0eb1b3bc163c53b133d9940c458216a51721df6726b22eb89952715','sourceVersions':{'lectures':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c'},'authorAnswerRevealed':False,'inheritedEvidencePath':str(OLD.relative_to(ROOT)),'inheritedEvidenceSha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'inheritedReviewerId':'reviewer-independent-python-modeling-20261019','inheritedAnswerCount':83,'inheritedPageCount':36,'questionHashManifestPath':'audits/W01-L04-frozen-question-hashes.json','questionHashManifestSha256':'8ca05d783f544903357d9cab7523f2821f0e2d627ad38f15e9e63de62419880e','pageObservations':[],'answers':[],'notes':['Original 83 blind solves and 36 page observations remain unchanged in the inherited evidence file. This file contains only the continuation reviewer\'s work.']}
notes={
161:'Printed 37. Screenshot types string mobile robot, float 1.5, integer 4; list [1.2,1.5,0.9,2.0], tuple (2.3,1.2,0.5), set with repeated chair. Function defines compute_distance(speed,time), multiplies and returns distance, but calls compute_travel_distance(10,5): literal fresh-namespace NameError, not an implicit correction. Empty bottom-right rectangle contains no output.',
162:'Printed 38. math import, pi, sqrt(441). Sensor list [2.0,1.5,0.8,0.4,0.2]. First if reading<0.5 sets STOP and breaks. Next if reading<1.0 prints Reduce speed and continues, else MOVE_FORWARD; final loop-body print and separate post-loop print visible with commas. Three loop-body messages then final 0.4 STOP, no processing of 0.2. Strict boundaries 0.5 slow, 1.0 forward. Empty output rectangle.',
163:'Printed 39. Robot initializer stores name and speed. move(time,action="moved") computes local distance and prints, with no return. status has two print statements. robot1=Robot("rover_1",1.5); status() then move(4). Empty output rectangle, so execution results must be derived not claimed printed on slide.',
164:'Printed 40. MobileRobot(Robot).move prints drives and unit m. Drone(Robot).move calls super().move(time,"flies"). Neither overrides __init__. r1=MobileRobot("rover",1.5), r2=Drone("quadrotor",3.5), both move(3). Parent implementation from p163 needed. No output is displayed.',
165:'Printed 41. Imports numpy as np, scipy.spatial.distance.euclidean, matplotlib.pyplot as plt. Integer initial pose np.array([0,0]), goal [5,4], motions [[1,1],[1,0.5],[1,0.5],[1,1]] (floating dtype), path=[pose]. No physical distance units stated.',
166:'Printed 42. For m in motions, pose=pose+m and path.append(pose), then array conversion and euclidean(path[-1],goal). Plot source uses path[:,0], path[:,1], blue o- default and red goal. Actual plot shows points (0,0),(1,1),(2,1.5),(3,2),(4,3), separate red goal (5,4), axes X position/Y position. Non-in-place addition is important for dtype and aliasing.',
167:'Printed 43. Programming tools reused for virtual robot simulation, testing before deployment and AI integration. Python modeling prepares interpretation of ROS simulations, logical debugging and simulation-to-real transition. Does not establish automatic physical correctness.',
168:'Printed 44. Eight-row summary names NumPy/SymPy modeling, python-control/do-mpc control, PyBullet/MuJoCo physics and Gymnasium/SB3 RL. Core NumPy/SciPy/Matplotlib/Pandas; 90% and 5–10-line statements are promotional generalizations, not demonstrated universal bounds. solve_ivp ODE, optimize IK/PID tuning/identification, rclpy bridge, NumPy vectorization/Numba JIT/CuPy-JAX GPU/Ray parallelism. Sim-to-real row explicitly requires parameter identification, domain randomization and physical-measurement validation.',
169:'Printed 45 summary. Simplified real-system model; simulation studies behavior over time; reduces risk/cost/development time; Python practical flexible repeatable simulations; package use helps numerical algorithm deployment. No new equations, numerical values or executable code.',
170:'Printed 46. Thank You only. Decorative footer/logos and otherwise blank, no examinable topic.'}
seen={x['physicalPage'] for x in d['pageObservations']}
for p,n in notes.items():
 if p in seen:continue
 path=f'sources/previews/lectures/page-{p:04d}.webp'
 d['pageObservations'].append({'physicalPage':p,'sourceId':'lectures','sourceSha256':d['sourceVersions']['lectures'],'previewPath':path,'previewSha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'dimensions':[1800,1013],'method':'rendered_page','inspectorId':R,'inspectedAt':now,'printedSlideNumber':str(p-124),'observations':n})
d['lastUpdatedAt']=now
P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Saved',len(d['pageObservations']),'personal page observations;',len(d['answers']),'personal answers. Original evidence unchanged.')
