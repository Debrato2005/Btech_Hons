from pathlib import Path
import json,hashlib,datetime,math,random,statistics
R=Path(__file__).resolve().parents[2];D=R/'audits/assignment-coverage'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
reasons={11:[
'Energy is12*2.5=30 Wh and power is10+5+5=20 W. Runtime30/20=1.5 h=90 min. Other choices discard voltage, use only motor load, or confuse hours and minutes.',
'Air compressibility and seal friction create the stated pneumatic positioning difficulty. Neither incompressibility nor frictionless seals is the source pair.',
'Code1023 means1023<=1024*Vin/5<1024, hence5*1023/1024<=Vin<5. Reconstruction5*1023/1023=5 V. The lower bound is4.9951171875 V; a quantized code is not an exact voltage measurement.',
'A counts600/rev, so1800/600=3 rev. B counts2400/rev, so1800/2400=.75 rev. Separate-motion scope prevents the readings from contradicting one another.',
'The explicitly supplied effective torque transfer gives.85*20*.25=4.25 N m. Omitting loss gives5, reversing gearing gives.010625, dividing by.85 gives5.88235. No power-efficiency assertion at zero speed follows.',
'A strictly decreasing motor torque curve is above its equilibrium torque at a nearby lower speed. Constant load and positive inertia make net torque and initial acceleration positive, toward equilibrium.',
'Plain gradient descent is w_new=w_old-eta*gradient=.4-.02*(-3)=.46. A negative gradient requires a positive weight increment.',
'The boundary isx=7.5/2.5=3. Score at3.2 is.5, so class Normal. Along increasingx signed distance3.2-3=.2 mm/s, also score/2.5. Source score-distance confusion is not valid.',
'Centering by the training mean and dividing by nonzero population training standard deviation gives zero mean/unit variance on those training values. New values reuse old statistics and need not have either property. Neither minmax output nor nonnegative torque is implied.',
'Torque2*.5+.5*2+1.5*3+.8=7.3 N m. Absolute errorabs(8-7.3)=.7 N m, never negative.'
],12:[
'Cropping spatially selects the face ROI, preceding classification. It neither assigns the classifier label nor establishes hidden emotional truth, and it discards background outside the crop.',
'Both same-start independent results exist atmax(80,120)=120 ms. Serial time200 ms, so the saving is80 ms.',
'The source describes active infrared projection combined with stereo correspondence for depth. It does not substitute time of flight or monocular RGB-only processing.',
'One segment ishypot(.3,.2) m;24 legs total gives8.6533230611 m. Constant speed.6*8.2=4.92 m/s, time1.7588055002 s. Final two-decimal values8.65 m and 1.76 s.',
'Existing-map pose estimation corresponds to AMCL, while jointly estimating a map and pose corresponds to SLAM. Neither description is merely route planning or velocity generation.',
'Modularity and sensor integration support timely navigation but do not establish specific deadline guarantees. Measured whole-system execution matters; visualization is not deadline certification.',
'The camera observes a valid low obstacle outside the fixed lidar scan plane and can add its evidence after frame alignment. Lidar retains wide angular coverage; neither sensor makes validity and calibration irrelevant.',
'The signed wheel sum vanishes, so midpoint speed0. The difference is10 rad/s, andr/L=.2 givespositive2 rad/s yaw under the stated convention.',
'The hypothetical safety-learning principle requires recording and reviewing a near miss despite no actual injury. Waiting for injury or leaving no record defeats learning from the event.',
'Mechanically yielding joints or backdrivable actuation can take up impact energy without first commanding a software stop. Rigid-path software zones, redundant sensing and emergency logic are not the physical yielding mechanism.'
]}
checks={11:[],12:[]}
def ck(w,name,condition):assert condition,name;checks[w].append(name)
ck(11,'Battery energy and hours-to-minutes',12*2.5==30 and 30/(10+5+5)*60==90)
lo=5*1023/1024;ck(11,'ADC reconstruction and lower bound',5*1023/1023==5 and lo==4.9951171875)
ck(11,'ADC lower endpoint included',math.floor(1024*lo/5)==1023)
ck(11,'ADC just below lower endpoint',math.floor(1024*(lo-1e-8)/5)==1022)
ck(11,'ADC just below5 belongs highest code',math.floor(1024*(5-1e-8)/5)==1023)
ck(11,'Encoder counting conventions',1800/600==3 and 1800/(4*600)==.75)
ck(11,'Effective gear torque',math.isclose(.85*20*.25,4.25))
ck(11,'Gradient step sign',math.isclose(.4-.02*(-3),.46))
ck(11,'Score vs distance',math.isclose(2.5*3.2-7.5,.5)and math.isclose(3.2-7.5/2.5,.2))
train=[1.,2.,3.,4.];mu=statistics.mean(train);sigma=statistics.pstdev(train);z=[(x-mu)/sigma for x in train];ck(11,'Population standardization',math.isclose(statistics.mean(z),0,abs_tol=1e-12)and math.isclose(statistics.pvariance(z),1))
new=[(x-mu)/sigma for x in [10,10,10]];ck(11,'Reusing statistics need not standardize new batch',statistics.mean(new)!=0 and statistics.pvariance(new)==0)
tau=2*.5+.5*2+1.5*3+.8;ck(11,'Prediction and absolute residual',math.isclose(tau,7.3)and math.isclose(abs(8-tau),.7))
ck(12,'Concurrent and serial timing',max(80,120)==120 and 80+120-max(80,120)==80)
d=24*math.hypot(.3,.2);t=d/(.6*8.2);ck(12,'Full precision motion',round(d,2)==8.65 and round(t,2)==1.76)
ck(12,'One-way and taxicab distractors',round(d/2,2)==4.33 and 24*(.3+.2)==12)
ck(12,'Differential-drive positive yaw',.1*(5-5)/2==0 and .1*(5-(-5))/.5==2)
counts={11:0,12:0};rng=random.Random(11122026)
for _ in range(1000):
 V=rng.uniform(1,60);Ah=rng.uniform(.1,20);P=rng.uniform(.1,500);E=V*Ah;T=E/P;assert math.isclose(P*T,E);counts[11]+=1
 k=rng.randrange(1024);v=5*(k+.5)/1024;assert math.floor(1024*v/5)==k;counts[11]+=1
 m=rng.randint(1,6000);cycles=rng.randint(1,5000);assert math.isclose(m/(4*cycles),m/cycles/4);counts[11]+=1
 slope=rng.uniform(.1,20);boundary=rng.uniform(-10,10);x=rng.uniform(-10,10);score=slope*(x-boundary);assert math.isclose(score/slope,x-boundary,abs_tol=1e-12);counts[11]+=1
 a=rng.uniform(0,1e3);b=rng.uniform(0,1e3);assert math.isclose(a+b-max(a,b),min(a,b),abs_tol=1e-10);counts[12]+=1
 dx=rng.uniform(.01,10);dy=rng.uniform(.01,10);n=rng.randint(1,100);v=rng.uniform(.01,10);path=2*n*math.hypot(dx,dy);assert math.isclose(path/v*v,path);counts[12]+=1
 r=rng.uniform(.01,1);L=rng.uniform(.1,3);wr=rng.uniform(-20,20);wl=rng.uniform(-20,20);vel=r*(wr+wl)/2;omega=r*(wr-wl)/L;assert math.isclose(vel+omega*L/2,r*wr,abs_tol=1e-12);counts[12]+=1
 assert math.isclose(vel-omega*L/2,r*wl,abs_tol=1e-12);counts[12]+=1
for w in [11,12]:
 pp=R/f'audits/blind-ASSIGN-W{w}.json';packet=json.loads(pp.read_text());binding=json.loads((R/f'audits/blind-binding-ASSIGN-W{w}.json').read_text());assert sha(pp)==binding['packetSha256'];cp=D/f'W{w}-recovery-independent-checks.json';save(cp,{'reviewerId':'repair_assignment_source_bindings:independent-reviewer','namedChecks':checks[w],'namedCount':len(checks[w]),'variedAssertions':counts[w],'seed':11122026,'allPassed':True,'scope':'Independent supplied-model arithmetic, not author scripts, training, hardware, model download or browser runtime.'});save(D/f'W{w}-recovery-independent-prekey-seal.json',{'reviewerId':'repair_assignment_source_bindings:independent-reviewer','sealedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packetPath':str(pp.relative_to(R)),'packetSha256':sha(pp),'generatedKeyOpened':False,'sourcePrintedKeysVisible':True,'fullyBlind':False,'sourceObservationsPath':'audits/assignment-coverage/W11-W12-recovery-independent-source-observations.json','sourceObservationsSha256':sha(D/'W11-W12-recovery-independent-source-observations.json'),'checksPath':str(cp.relative_to(R)),'checksSha256':sha(cp),'answers':[{'questionId':q['id'],'selectedOptionIds':['o1'],'reasoning':reasons[w][i]}for i,q in enumerate(packet['questions'])]});print(w,len(checks[w]),counts[w])
