#!/usr/bin/env python3
"""Independent L26 code/math reproduction transcribed from actual source pixels."""
import json, math, datetime, random
from pathlib import Path
import numpy as np
import sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,truth):
 assert truth,name
 checks.append(name)
BLACKLIST=['free money','click here','win prize','urgent']
def spam_filter(email_text):
 email_lower=email_text.lower()
 for word in BLACKLIST:
  if word in email_lower:
   return f"SPAM (trigger: '{word}')"
 return 'NOT SPAM'
emails=['You have won a FREE MONEY prize! Click here now.','Meeting agenda for tomorrow is attached.','Nigerian Prince offers complimentary financial assistance.','Get your FREE product today at no cost.']
outputs=[spam_filter(e) for e in emails]
check('source first spam and ordered trigger',outputs[0]=="SPAM (trigger: 'free money')")
check('source ordinary message',outputs[1]=='NOT SPAM')
check('source missed financial-assistance example',outputs[2]=='NOT SPAM')
check('source free-product variant',outputs[3]=='NOT SPAM')
check('blacklist order not message order',spam_filter('urgent: click here for free money')=="SPAM (trigger: 'free money')")
check('substring false positive',spam_filter('insurgent')=="SPAM (trigger: 'urgent')")
check('left alignment is minimum not truncation',f'{"a"*25:<20}'=='a'*25)
check('short string pads on right',f'{"NOT SPAM":<20}'=='NOT SPAM'+' '*12)
check('message slice takes first 55',len(emails[2][:55])==55 and emails[2][:55]==emails[2][0:55])
check('image count',256**64==2**512)
grid=np.array([[0,0,180,220,220,180,0,0],[0,180,240,120,120,240,180,0],[0,220,140,0,0,140,220,0],[0,240,120,0,0,120,240,0],[0,240,120,0,0,120,240,0],[0,220,140,0,0,140,220,0],[0,180,240,120,120,240,180,0],[0,0,180,220,220,180,0,0]])
check('source grid dimensions',grid.shape==(8,8));check('row-major flatten',grid.ravel().shape==(64,) and grid.ravel()[:4].tolist()==[0,0,180,220])
iris=load_iris();X_train,X_test,y_train,y_test=train_test_split(iris.data,iris.target,random_state=0)
model=KNeighborsClassifier(n_neighbors=1).fit(X_train,y_train)
pred=model.predict(X_test)
check('Iris split sizes',len(X_train)==112 and len(X_test)==38)
check('Iris correct count',int(np.sum(pred==y_test))==37)
check('source percent output',f'{model.score(X_test,y_test):.0%}'=='97%')
check('seed reproduces split',np.array_equal(X_test,train_test_split(iris.data,iris.target,random_state=0)[1]))
def rule_based_classifier(sepal_length,petal_length):
 if sepal_length<5.0:return 'setosa'
 elif petal_length<2.5:return 'setosa'
 else:return 'versicolor'
check('first rule wins',rule_based_classifier(4.9,5.0)=='setosa')
check('strict equality thresholds',rule_based_classifier(5.,2.5)=='versicolor')
check('second rule reachable',rule_based_classifier(6.,2.)=='setosa')
check('no virginica output',set(rule_based_classifier(a,b) for a in [4.,5.,6.] for b in [1.,2.5,5.])=={'setosa','versicolor'})
ml_model=KNeighborsClassifier(n_neighbors=5).fit(X_train,y_train)
check('two source neighbor counts',model.n_neighbors==1 and ml_model.n_neighbors==5)
check('scaled Euclidean calculation',math.dist((0,0),(3,4))==5)
check('majority vote',[1,0,1].count(1)==2)
X_terrain=np.array([[1.,10],[1.2,12],[.8,60],[.5,65],[.9,30],[1.,35]])
y_terrain=np.array([0,0,1,1,2,2])
check('terrain shapes',X_terrain.shape==(6,2) and y_terrain.shape==(6,))
check('specific terrain row',X_terrain[4].tolist()==[.9,30.] and y_terrain[4]==2)
classifier=KNeighborsClassifier(n_neighbors=1).fit(X_terrain,y_terrain)
new_point=[[.7,62]];pred=int(classifier.predict(new_point)[0])
terrain_names={0:'Smooth Floor (Blue)',1:'Gravel (Red)',2:'Grass (Green)'}
dist=np.sqrt(np.sum((X_terrain-np.array(new_point))**2,axis=1))
check('all raw terrain squared distances',np.allclose(dist**2,[2704.09,2500.25,4.01,9.04,1024.04,729.09]))
check('nearest raw terrain point',int(np.argmin(dist))==2)
check('terrain predicted numeric label',pred==1)
check('terrain string lookup',terrain_names[pred]=='Gravel (Red)')
check('one query output shape',classifier.predict(new_point).shape==(1,))
check('dot product with intercept',float(np.array([2,-1])@np.array([3,4])+.5)==2.5)
check('zero-based feature count',len(list(range(5+1)))==6)
resid=np.array([2,2,4])-np.array([1,3,5])
check('SSE',np.sum(resid**2)==3);check('MSE',np.mean(resid**2)==1)
# Different implementation cross-check of the trained 1NN model away from ties.
rng=np.random.default_rng(622026);queries=rng.uniform([-.5,0],[2.5,80],(1000,2));manual=np.array([y_terrain[min(range(6),key=lambda i:math.dist(q,X_terrain[i]))] for q in queries]);assert np.array_equal(manual,classifier.predict(queries))
# Positive objective scaling preserves candidate ordering for arbitrary residual vectors.
for _ in range(1000):
 a,b=rng.normal(size=(2,5));assert (np.sum(a*a)<np.sum(b*b))==(np.mean(a*a)<np.mean(b*b))
report={'reviewerId':'build_offline_study_interface:L26-independent-reviewer','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'namedChecks':len(checks),'checks':checks,'randomNearestNeighborQueries':1000,'randomObjectiveOrderingCases':1000,'software':{'numpy':np.__version__,'scikitLearn':sklearn.__version__},'sourceCodePages':[779,782,783,791,792,793],'sourceCodeReproduction':'Transcribed independently from inspected page pixels. Imports and diagnostic assertions explicitly added; no author-check code imported.','irisAccuracy':model.score(X_test,y_test),'terrainDistances':dist.tolist(),'status':'passed'}
(R/'audits/W06-L26-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
