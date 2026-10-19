"""Reproduce actual L26 code and author arithmetic; no independent-review claim."""
from pathlib import Path
import json,math,hashlib,inspect
import numpy as np
import sklearn
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
# Actual source page779, transcribed from pixels. Four strings are supplied in screenshot.
BLACKLIST=['free money','click here','win prize','urgent']
def spam_filter(email_text):
 email_lower=email_text.lower()
 for word in BLACKLIST:
  if word in email_lower:return f"SPAM (trigger: '{word}')"
 return 'NOT SPAM'
emails=['You have won a FREE MONEY prize! Click here now.','Meeting agenda for tomorrow is attached.','Nigerian Prince offers complimentary financial assistance.','Get your FREE product today at no cost.']
spam_output=[f'{spam_filter(e):<20} | {e[:55]}'for e in emails]
check('four literal spam outputs',[spam_filter(e)for e in emails]==["SPAM (trigger: 'free money')",'NOT SPAM','NOT SPAM','NOT SPAM'])
check('case-insensitive matching',spam_filter('FREE MONEY')=="SPAM (trigger: 'free money')")
check('list order not earliest textual position',spam_filter('urgent; click here; free money')=="SPAM (trigger: 'free money')")
check('substring not word token matching',spam_filter('insurgent')=="SPAM (trigger: 'urgent')")
check('free alone not blacklisted',spam_filter('FREE product')=='NOT SPAM')
check('literal substring spacing',spam_filter('free  money')=='NOT SPAM')
check('exact printed slice truncates third message',len(emails[2])>55 and len(emails[2][:55])==55)
# Source782 Iris1NN and source7835NN share split but not neighbor count.
iris=load_iris();X_train,X_test,y_train,y_test=train_test_split(iris.data,iris.target,random_state=0)
model=KNeighborsClassifier(n_neighbors=1).fit(X_train,y_train)
score=model.score(X_test,y_test);pred=model.predict(X_test)
check('Iris matrix150x4',iris.data.shape==(150,4))
check('default split112train38test in installed sklearn',len(X_train)==112 and len(X_test)==38)
check('1NN exact heldout37of38',np.sum(pred==y_test)==37 and math.isclose(score,37/38))
check('formatted score97percent',f'{score:.0%}'=='97%')
check('fixed seed recreates same split',np.array_equal(X_train,train_test_split(iris.data,iris.target,random_state=0)[0]))
five=KNeighborsClassifier(n_neighbors=5).fit(X_train,y_train)
def rule_based_classifier(sepal_length,petal_length):
 if sepal_length<5.0:return 'setosa'
 elif petal_length<2.5:return 'setosa'
 else:return 'versicolor'
check('rule first if priority',rule_based_classifier(4.9,5)=='setosa')
check('rule strict thresholds',rule_based_classifier(5,2.5)=='versicolor')
check('rule second branch',rule_based_classifier(5,2.4)=='setosa')
check('rule never outputs virginica',set(rule_based_classifier(a,b)for a in[4.5,5,6,7]for b in[1,2.5,5,6])=={'setosa','versicolor'})
# Source791–793 exact numeric features, no scaling inserted.
X_terrain=np.array([[1.,10],[1.2,12],[.8,60],[.5,65],[.9,30],[1.,35]])
y_terrain=np.array([0,0,1,1,2,2]);classifier=KNeighborsClassifier(n_neighbors=1);classifier.fit(X_terrain,y_terrain)
new_point=[[.7,62]];predicted=classifier.predict(new_point)[0];dist=np.linalg.norm(X_terrain-np.array(new_point)[0],axis=1)
terrain_names={0:'Smooth Floor (Blue)',1:'Gravel (Red)',2:'Grass (Green)'}
check('terrain shapes',X_terrain.shape==(6,2)and y_terrain.shape==(6,))
check('terrain nearest row3 with distance sqrt4.01',np.argmin(dist)==2 and math.isclose(dist[2],math.sqrt(4.01)))
check('terrain class1',predicted==1 and terrain_names[int(predicted)]=='Gravel (Red)')
check('terrain second closest row4',np.argsort(dist)[1]==3 and math.isclose(dist[3],math.sqrt(9.04)))
check('3NN same query majority gravel',KNeighborsClassifier(n_neighbors=3).fit(X_terrain,y_terrain).predict(new_point)[0]==1)
check('hypothetical query.5,40 changes neighbor under feature rescaling',np.argmin(np.linalg.norm((X_terrain-[.5,40])*[1000,1],axis=1))!=np.argmin(np.linalg.norm(X_terrain-[.5,40],axis=1)))
# Actual64cell grid, row-major transcription.
grid=np.array([[0,0,180,220,220,180,0,0],[0,180,240,120,120,240,180,0],[0,220,140,0,0,140,220,0],[0,240,120,0,0,120,240,0],[0,240,120,0,0,120,240,0],[0,220,140,0,0,140,220,0],[0,180,240,120,120,240,180,0],[0,0,180,220,220,180,0,0]])
check('grayscale shape andrange',grid.shape==(8,8)and grid.min()==0 and grid.max()==240)
check('rowmajor first8cells',[int(x)for x in grid.ravel()[:8]]==[0,0,180,220,220,180,0,0])
check('all8bitarray cardinality',256**64==2**512)
check('fixedsize64bytes uncompressed intensity payload',64*8==512)
check('simple rawdistance345',math.dist([0,0],[3,4])==5)
check('linear predictor example',2*3+(-1)*4+.5==2.5)
true=np.array([1,3,5]);estimate=np.array([2,2,4]);sse=float(np.sum((estimate-true)**2));mse=float(np.mean((estimate-true)**2))
check('SSEvsMSE',sse==3 and mse==1)
check('pfeatures zerobased lastindex',len(list(range(4)))==4 and max(range(4))==3)
# Additional deterministic varied cases check exact nearest-distance and classifier agreement.
rng=np.random.default_rng(2601)
for _ in range(500):
 p=rng.uniform([0,0],[2,80]);raw=np.sum((X_terrain-p)**2,axis=1);idx=np.argmin(raw)
 assert classifier.predict([p])[0]==y_terrain[idx]
check('500rawdistance1NNcases',True)
output={'spamPrintedLines':spam_output,'irisShape':list(iris.data.shape),'trainCount':len(X_train),'testCount':len(X_test),'iris1NNcorrect':int(np.sum(pred==y_test)),'iris1NNscore':float(score),'iris1NNformatted':f'{score:.0%}','iris5NNscoreNotPrintedInSource':float(five.score(X_test,y_test)),'terrainDistancesInRawFeatureCoordinates':[float(x)for x in dist],'terrainPrediction':int(predicted),'terrainName':terrain_names[int(predicted)],'grid':grid.tolist(),'unrestricted8bitImageCount':str(256**64)}
report={'role':'author calculations, not independent verification','checksPassed':len(checks),'checks':checks,'randomCases':500,'numpyVersion':np.__version__,'sklearnVersion':sklearn.__version__,'sourcePages':[779,781,782,783,791,792,793,794,795],'codeScope':'Literal source snippets; add harness assertions and computation outputs only, not missing original plot code. Installed sklearn defaults explicitly version-bound.','outputs':output}
(R/'audits/W06-L26-author-checks.json').write_text(json.dumps(report,indent=2)+'\n');(R/'audits/W06-L26-reproduced-output.txt').write_text(json.dumps(output,indent=2)+'\n');print(len(checks),'checks+500cases passed',score,predicted,dist.tolist())
