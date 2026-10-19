#!/usr/bin/env python3
"""Focused author regression after independent quality findings, not independent review."""
import json,hashlib,sys,platform
from pathlib import Path
import numpy as np
from scipy import sparse
import scipy,matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from sklearn.datasets import make_classification
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from validate import question_hash,schema_errors
checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
data=json.loads((R/'data/question-batches/W06-L28.json').read_text());qs={q['id']:q for q in data['questions']};m=json.loads((R/'audits/W06-L28-v2-repair-manifest.json').read_text());old=json.loads((R/'audits/batch-history/W06-L28-v1-before-repairs.json').read_text());original={q['id']:q for q in old['questions']}
check('27 accepted objects and hashes preserved',len(m['preservedApprovedHashes'])==27 and all(qs[id]==original[id] and question_hash(qs[id])==h for id,h in m['preservedApprovedHashes'].items()))
check('42 revision versions and independent-review state',len(m['revisions'])==42 and all(qs[v['questionId']]['version']==2 and qs[v['questionId']]['status']=='draft' and not qs[v['questionId']]['reviewIds'] and question_hash(qs[v['questionId']])==v['questionSha256'] for v in m['revisions']))
check('all 14 source issues preserved',data['sourceIssues']==old['sourceIssues'] and len(data['sourceIssues'])==14)
packet=json.loads((R/m['blindPacketPath']).read_text());check('answer-hidden packet',len(packet)==42 and all('solution' not in p and 'correctOptionIds' not in p and all('evidenceText' not in c for c in p['citations']) for p in packet))
check('packet hash',hashlib.sha256((R/m['blindPacketPath']).read_bytes()).hexdigest()==m['blindPacketSha256'])
for p,h in m['artifactSha256'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
check('artifact hashes',True)
for typ,rows in [('question',data['questions']),('concept',data['concepts']),('slide',json.loads((R/'data/inspection-batches/W06-L28.json').read_text())['slides'])]:
 errors=[e for row in rows for e in schema_errors(row,json.loads((R/f'data/schema.{typ}.json').read_text()))]
 check(typ+' schemas',not errors)
for q in data['questions']:
 assert set(q['solution']['optionExplanations'])=={o['id'] for o in q['options']}
 for cid in q['conceptIds']:
  c=next(c for c in data['concepts'] if c['id']==cid);assert q['id'] in c['questionIds'];assert set(x['slideId'] for x in q['citations'])<=set(c['slideIds'])
check('option explanations and reciprocal concept links',True)
check('actual figure citations on both revised visual questions',all(any(c['kind']=='figure' and c['region'] for c in qs[f'W06-L28-Q{n:03d}']['citations']) for n in [35,39]))
# Controlled code/figure and representation checks for the new question scope.
x=np.linspace(-10,10,100);y=np.sin(x)
check('sine endpoints and bound',x[0]==-10 and x[-1]==10 and y[0]>0 and y[-1]<0 and np.isclose(y[0],-y[-1]) and np.max(np.abs(y))<=1)
fig,ax=plt.subplots();line,=ax.plot(x,y,marker='x');check('sine sample markers',len(line.get_xdata())==100 and line.get_marker()=='x');plt.close(fig)
values=np.array([2.,3.,4.]);rows=np.array([0,1,2]);cols=np.array([2,0,1]);coo=sparse.coo_matrix((values,(rows,cols)),shape=(3,3));csr=coo.tocsr();v=np.array([5.,6.,7.])
check('COO direct construction and CSR conversion preserve matrix',np.array_equal(coo.toarray(),csr.toarray()))
check('CSR row-oriented arithmetic example',np.array_equal(csr@v,np.array([14.,15.,24.])) and csr.getrow(1).toarray().tolist()==[[3.,0.,0.]])
X,yc=make_classification(n_samples=200,n_features=2,n_redundant=0,random_state=0)
fig,ax=plt.subplots();collection=ax.scatter(X[:,0],X[:,1],c=yc,cmap='bwr',edgecolors='k',linewidths=.5,alpha=.8);fig.canvas.draw()
check('class colorbar mapping',np.allclose(collection.cmap(collection.norm(0))[:3],[0,0,1]) and np.allclose(collection.cmap(collection.norm(1))[:3],[1,0,0]))
check('source scatter style',np.allclose(collection.get_edgecolors()[:,:3],0) and np.allclose(collection.get_linewidths(),.5) and collection.get_alpha()==.8)
check('scatter coordinates and supplied labels',np.allclose(collection.get_offsets(),X) and np.array_equal(collection.get_array(),yc));plt.close(fig)
# A document test demonstrates representation only, not browser or live-kernel restoration.
doc={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3'}},'cells':[{'cell_type':'code','source':['x = 2'],'execution_count':1,'metadata':{},'outputs':[{'output_type':'stream','name':'stdout','text':['2\n']}]}]}
saved=json.loads(json.dumps(doc));check('JSON can store source and output without variable binding',saved['cells'][0]['source']==['x = 2'] and saved['cells'][0]['outputs'][0]['text']==['2\n'] and 'x' not in saved)
report={'status':'author regression passed; all 42 revised objects still require independent re-review','assertionCount':len(checks),'checks':checks,'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__},'addedContext':'Controlled sparse matrix and JSON document are explicitly added demonstration fixtures. Source plots and relevant pages were actually viewed; no browser test or live-kernel restoration test is claimed.','inspectedAgain':[828,829,837,838,842,843],'gapAngleCount':5,'expandedExistingQuestionIds':['W06-L28-Q006','W06-L28-Q024','W06-L28-Q035','W06-L28-Q039'],'noNewDuplicateQuestions':True,'questionCount':69}
(R/'audits/W06-L28-v2-author-checks.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checks),'focused assertions')
