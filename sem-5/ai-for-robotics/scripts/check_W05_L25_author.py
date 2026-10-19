#!/usr/bin/env python3
"""Author-only algebra checks from L25 premises. Not independent verification."""
import json,math,random
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
checks=[]
def eq(name,a,b):
 assert np.allclose(a,b,atol=1e-10,rtol=1e-10),(name,a,b)
 checks.append(name)
J=np.array([[1.,1.],[0.,2.]])
eq('Desired velocity coupled solve',np.linalg.solve(J,[.3,.4]),[.1,.2])
eq('Scalar inverse derivative',-.5/2**2,-.125)
eq('Acceleration product rule',.6/2-.5*.4/4,.25)
eq('Finite difference alternating noise',(.01-(-.01))/.001,20.)
eq('Cartesian error',np.array([.4,.2,.5])-np.array([.3,.25,.45]),[.1,-.05,.05])
eq('Inverse joint correction',np.linalg.solve(J,[.02,.04]),[0,.02])
eq('Inverse controller torque',np.diag([2,3])@np.linalg.solve(J,[.02,.04]),[0,.06])
eq('Swapped gain order distractor',np.linalg.solve(J,np.diag([2,3])@np.array([.02,.04])),[-.02,.06])
J2=np.array([[1.,2.],[3.,4.]])
F=np.diag([10,20])@np.array([.1,-.05]);eq('Virtual force',F,[1,-1]);eq('Transpose torque',J2.T@F,[-2,-2]);eq('Inverse mapping distractor',np.linalg.solve(J2,F),[-3,2]);eq('Swapped gain-transpose distractor',np.diag([10,20])@J2.T@np.array([.1,-.05]),[-.5,0])
eq('Singular transpose nullspace',np.diag([1,0])@np.array([0,2]),[0,0])
M=np.array([[2.,1.],[1.,3.]])
eq('Cartesian dynamic force',M@np.array([1,-2])+np.array([.5,1])+np.array([1,4]),[1.5,0])
eq('Servo acceleration',np.array([.5,-.2])+np.diag([4,6])@np.array([-.05,.1])+np.diag([4,9])@np.array([.1,-.2]),[.7,-1.4])
eq('Critical gains',2*np.sqrt([4,9]),[4,6]);eq('Cross-coupled error',-np.array([[4,1],[1,9]])@np.array([0,1]),[-1,-9])
eq('Inertia mismatch',3*4/2,6)
F2=M@np.array([1,-1])+np.array([1,2]);eq('Full pipeline force',F2,[2,0]);eq('Full pipeline torque',np.array([[1,2],[0,1]]).T@F2,[2,4]);eq('Dual rate ratio',20/1,20)
rng=np.random.default_rng(25)
for i in range(1000):
 J=rng.normal(size=(3,3))+np.eye(3)*4;dJ=rng.normal(size=(3,3));A=np.linalg.inv(J);dA=-A@dJ@A
 assert np.allclose(dJ@A+J@dA,0,atol=1e-11)
 v=rng.normal(size=3);f=rng.normal(size=3)
 assert np.allclose(f@(J@v),(J.T@f)@v)
 Z=rng.normal(size=(3,3));M=Z.T@Z+np.eye(3);h=rng.normal(size=3);u=rng.normal(size=3)
 assert np.allclose(np.linalg.solve(M,M@u+h-h),u)
 xd2=rng.normal(size=3);e=rng.normal(size=3);de=rng.normal(size=3);kp=np.diag(rng.uniform(1,9,3));kv=2*np.sqrt(kp)
 u=xd2+kv@de+kp@e;dde=xd2-u
 assert np.allclose(dde+kv@de+kp@e,0)
results={'batchId':'W05-L25','kind':'author checks, not independent verification','allPassed':True,'assertionCount':len(checks),'checks':checks,'randomCases':1000,'randomProperties':['inverse derivative product identity','force/velocity virtual power','exact model cancellation','servo error equation'],'sourceCode':'No executable source code is printed; these are explicitly added calculations from cited mathematical premises.'}
(R/'audits/W05-L25-author-computations.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
