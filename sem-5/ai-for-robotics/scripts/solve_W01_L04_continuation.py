"""Freeze 48 fresh blind answers; never overwrite inherited 83 answers."""
import pathlib,json,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
assert not (ROOT/'audits/W01-L04-author-reveal.json').exists(), 'Blind evidence is frozen; author answers have been revealed.'
p=ROOT/'audits/blind-answers-W01-L04-v1-continuation.json';d=json.loads(p.read_text());assert not d['authorAnswerRevealed']
old=json.loads((ROOT/d['inheritedEvidencePath']).read_text());assert hashlib.sha256((ROOT/d['inheritedEvidencePath']).read_bytes()).hexdigest()==d['inheritedEvidenceSha256']
packet=json.loads((ROOT/'audits/blind-W01-L04.json').read_text());hashes=json.loads((ROOT/d['questionHashManifestPath']).read_text())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
notes={
146:'Printed 22: training AI, predeployment testing/validation and safe experimentation; data-driven systems still rely on development simulations.',
147:'Printed 23: equations represented computationally, evaluated numerically, changed parameters and study conditions; mathematical assumptions are not automatically chosen or invalidated.',
155:'Printed 31: procedural/OOP/functional, dynamic typing/garbage collection, downloaded-installed-imported packages; RVC3 builds on two toolboxes plus NumPy/SciPy/Matplotlib. .py/.ipynb are both named but formats are not identical.',
158:'Printed 34 six module boxes. scipy.linalg explicitly says advanced linear algebra, LAPACK wrappers and Riccati equations/LQR. Other boxes integrate, optimize, signal, spatial and stats. ODE/PDE and Kalman wording is broad, not proof of specific APIs.',
159:'Printed 35 six visualization boxes. Heatmaps/Matrices names sns.heatmap/plt.imshow, confusion matrices, cost-to-go grids, occupancy maps. Animation names FuncAnimation+blitting and makes hardware-dependent 30+fps claim. sns is not Matplotlib itself.',
160:'Printed 36: DataFrame logs; right table resample aligns 50Hz IMU to 200Hz encoder, rolling/groupby/merge/join distinct. Left diff/time-diff expression has literal uncontinued newline after division; right read_hdf5 spelling must not be adopted as API. Source resampling description is not a claim of new physical data.'}
for page,note in notes.items():
 path=f'sources/previews/lectures/page-{page:04d}.webp'
 if not any(o['physicalPage']==page for o in d['pageObservations']):d['pageObservations'].append({'physicalPage':page,'sourceId':'lectures','sourceSha256':d['sourceVersions']['lectures'],'previewPath':path,'previewSha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'dimensions':[1800,1013],'method':'rendered_page','inspectorId':d['reviewerId'],'inspectedAt':now,'printedSlideNumber':str(page-124),'observations':note})
reasons={
'P0146-Q01':'Simulation supplies safe virtual training/evaluation and predeployment debugging/testing. The source explicitly retains physical validation, so neither elimination of real checks nor universal out-of-model safety follows.',
'P0147-Q01':'Computationally representing equations allows numerical reevaluation after changing parameters. The source contrasts this with paper-only solutions; Python does not choose or validate physical assumptions automatically.',
'P0155-Q01':'The source explicitly lists three programming styles and dynamic typing/garbage collection. Its package workflow is download, install, then import, contradicting the no-import distractor.',
'P0155-Q02':'The dependency statement is RVC3 built on roboticstoolbox and machinevisiontoolbox, themselves depending on NumPy, SciPy and Matplotlib. It is neither hardware nor an interpreter replacement.',
'P0161-Q01':'The quoted value is str, decimal literal 1.5 is float, and integer literal 4 is int. Confirmed by execution.',
'P0161-Q02':'Zero-based indices map 0→1.2, 1→1.5, 2→0.9, 3→2.0. The requested index exists and returns 0.9.',
'P0161-Q03':'Parenthesized comma-separated literals form a tuple; a set removes the repeated chair and has chair/table/wall, three members, not positional index entries.',
'P0161-Q04':'Only compute_distance is defined. In the explicitly fresh namespace, lookup of compute_travel_distance raises NameError before assignment to d. Direct literal execution confirmed.',
'P0161-Q05':'With the explicitly corrected name, return speed*time=10*5=50. (m/s)*s=m, so 50 m, not addition or division.',
'P0162-Q01':'math.pi is an attribute containing a numerical constant; parentheses in math.sqrt(441) call the square-root function with 441.',
'P0162-Q02':'21*21=441; math.sqrt returns the floating result 21.0. Executed independently.',
'P0162-Q03':'and/or/not combine or negate truth values; in/not in test membership. + and * are arithmetic operators, not membership tests.',
'P0162-Q04':'2.0 and 1.5 choose MOVE_FORWARD; 0.8 chooses Reduce speed and continues; 0.4 satisfies <0.5, assigns STOP and breaks before 0.2. Final variables are 0.4 and STOP.',
'P0162-Q05':'There is one line for each of 2.0, 1.5 and 0.8. The 0.4 break skips the body print, but the separate post-loop print emits 0.4 STOP. Total 3+1=4, independently captured stdout.',
'P0162-Q06':'The 0.8 continue skips the remaining body of that iteration only. The 0.4 break terminates the entire loop and prevents processing 0.2.',
'P0162-Q07':'At exactly 0.5, reading<0.5 is false but reading<1.0 is true, so Reduce speed. This strict-boundary variant was executed.',
'P0162-Q08':'At exactly 1.0, both strict less-than comparisons are false. The else assigns MOVE_FORWARD. Executed boundary variant.',
'P0163-Q01':'Robot defines the class. Calling it creates robot1, whose name/speed are instance data and whose move/status are methods.',
'P0163-Q02':'The initializer assigns the two arguments to self.name and self.speed. It does not set time or distance and contains no print.',
'P0163-Q03':'1.5*4=6.0; default action is moved, name is rover_1, and print appends meters. Captured output is rover_1 moved 6.0 meters.',
'P0163-Q04':'status contains two print calls in order: Robot: plus the name, then Speed: plus the speed. Output is two lines, not the movement message.',
'P0163-Q05':'The method prints but contains no return statement. Falling off its end implicitly returns None, so assignment stores None despite the local distance being 6.0.',
'P0164-Q01':'Neither subclass defines __init__, so attribute lookup uses the inherited Robot initializer with the same name/speed arguments.',
'P0164-Q02':'MobileRobot computes 1.5*3=4.5 and prints drives with m. Drone calls Robot.move with flies; 3.5*3=10.5 and the parent prints meters. Exact two-line output captured.',
'P0164-Q03':'super() selects the parent method bound to the same Drone instance. The action argument changes to flies while name/speed remain that instance\'s attributes.',
'P0164-Q04':'Both objects accept move(time), but method dispatch selects MobileRobot or Drone behavior. Drone can reuse its parent with super; polymorphism does not require identical output.',
'P0165-Q01':'The imports and calls distinguish NumPy arrays/updates, scipy.spatial.distance.euclidean, and Matplotlib path/goal plotting. Pandas is absent.',
'P0165-Q02':'Initial pose is [0,0], goal [5,4]; motions contains four rows of dx,dy pairs, hence shape (4,2). Executed shape assertion.',
'P0165-Q03':'The list contains the existing pose array as its first entry before the loop. It stores the starting position, not the goal or four empty slots.',
'P0166-Q01':'Cumulative additions give [0,0]→[1,1]→[2,1.5]→[3,2]→[4,3]. The initial entry is included, unlike the distractor with only four points.',
'P0166-Q02':'Final [4,3] differs from goal [5,4] by [1,1]. Euclidean norm sqrt(1²+1²)=sqrt(2)=1.414 to three decimals. No physical unit is specified.',
'P0166-Q03':'Four segment lengths are sqrt(2),sqrt(1.25),sqrt(1.25),sqrt(2). Sum=2sqrt(2)+2sqrt(1.25)=5.064495..., so 5.064 coordinate units, distinct from remaining distance or endpoint displacement.',
'P0166-Q04':'The actual figure shows blue connected circles ending at x4,y3 and separate red goal x5,y4. Axes are X position and Y position, not time.',
'P0166-Q05':'Colon selects all rows; column 0 is x and column 1 y. Negative row index -1 is the final position [4,3]. Executed selections match.',
'P0166-Q06':'Non-in-place addition allocates a new array. Rebinding pose leaves earlier array objects held by path unchanged; all five identities were distinct before stacking.',
'P0166-Q07':'The literal pose has integer dtype but motions has float dtype because of 0.5. In-place addition attempts a floating result into integer output and fails the default same_kind casting rule, even for the [1.,1.] first row. NumPy 2.3.5 raised UFuncTypeError; original non-in-place code succeeds.',
'P0167-Q01':'The conceptual bridge is simulation interpretation, debugging and testing before hardware, with physical validation retained by the later sim-to-real summary. Neither package use nor ROS output proves all real behavior.',
'P0168-Q01':'The second table row names exactly NumPy+SciPy+Matplotlib+Pandas. The accompanying 90% is not adopted as a measured universal bound.',
'P0168-Q02':'The seventh row explicitly pairs vectorization with NumPy, JIT with Numba, GPU arrays with CuPy/JAX and parallelism with Ray.',
'P0168-Q03':'The sixth row calls ROS 2 rclpy a Python simulation-to-hardware bridge. This identifies its interface role, not hardware-independent execution guarantees.',
'P0168-Q04':'The fifth row names PyBullet and MuJoCo as physics-based environments for locomotion/manipulation policy training, unlike editors or tabular-data packages.',
'P0168-Q05':'The final row lists parameter identification, domain randomization and validation against physical measurements. Plot resolution/editor choice does not substitute for matching reality.',
'P0155-Q03':'The source explicitly prints .py/.ipynb. Identifying both suffixes does not equate script and notebook formats or their execution paths.',
'P0158-Q07':'The lower-left scipy.linalg box explicitly labels advanced linear algebra as LAPACK wrappers, followed by Riccati/LQR usage.',
'P0159-Q04':'The Heatmaps/Matrices box lists confusion matrices, cost-to-go grids and occupancy maps. Both proposed visualization uses match; class definition and boot images do not.',
'P0159-Q05':'The Real-Time Animation box explicitly pairs FuncAnimation with blitting. This does not prove a guaranteed frame rate on arbitrary hardware/workloads.',
'P0160-Q08':'The right-table resample() row names aligning sensors at differing rates, with 50Hz IMU and 200Hz encoder as example. describe summarizes and to_csv exports; resampling does not create independent physical measurements.',
'P0168-Q06':'The fourth row assigns scipy.optimize inverse kinematics, PID auto-tuning and system identification. Formatting, flashing and fonts are unrelated to the stated numerical-optimization role.'}
done={a['questionId'] for a in old['answers']}
assert len(reasons)==48
for q in packet:
 if q['id'] in done:continue
 k=q['id'].replace('W01-L04-','');assert k in reasons
 if any(a['questionId']==q['id'] for a in d['answers']):continue
 d['answers'].append({'questionId':q['id'],'questionVersion':q['version'],'blindQuestionSha256':hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'independentAnswerOptionIds':['o1','o2'] if k in ['P0146-Q01','P0155-Q01','P0159-Q04'] else ['o1'],'reasoning':reasons[k],'assumptions':q['assumptions'],'uncertainties':[],'sourcePages':sorted({c['physicalPage'] for c in q['citations']}),'solvedAt':now,'solvedBeforeAnswerSeen':True,'reviewerId':d['reviewerId'],'questionSha256':hashes[q['id']]})
assert len(d['answers'])==48 and len(done|{a['questionId'] for a in d['answers']})==131
d['lastUpdatedAt']=now;d['independentChecksPath']='audits/W01-L04-v1-continuation-code-checks.json';d['independentChecksSha256']=hashlib.sha256((ROOT/d['independentChecksPath']).read_bytes()).hexdigest()
d['preRevealFindings']=['P0162-Q07 and Q08 strict-boundary traces are medium, not hard. P0163-Q05 missing return is medium, not hard. P0166-Q03 four simple Euclidean lengths is medium, not hard.','P0166-Q07 dtype/casting variant is a valid subtle trap, but o3 DataFrame and o4 Euclidean distance are implausible distractors; replace them with meaningful dtype/aliasing alternatives. Several other tool-identification questions also contain unrelated hardware/editor distractors and require quality review.']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Blind continuation frozen',len(d['answers']),len(d['pageObservations']),hashlib.sha256(p.read_bytes()).hexdigest())
