#!/usr/bin/env python3
"""Post-blind-freeze checks of L25 v2 option rationales, independent of author code."""
import json
from pathlib import Path
from datetime import datetime, timezone
import sympy as s
R=Path(__file__).resolve().parents[1]
J=s.Matrix([[1,2],[0,1]]);D=s.Matrix([[0,1],[1,0]])
v=s.Matrix([3,1]);a=s.Matrix([2,4]);M=s.Matrix([[2,1],[1,3]])
items=[
 ('Q039 o1 omitted compensation',J.T*M*s.Matrix([1,-1]),s.Matrix([1,0])),
 ('Q054 o4 reordered inverse derivative',J.inv()*a-J.inv()**2*D*v,s.Matrix([5,1])),
 ('Q037 correct estimated/actual ratio',s.Rational(3,2)*4,s.Integer(6)),
 ('Q037 o4 actual/estimated ratio',s.Rational(2,3)*4,s.Rational(8,3)),
 ('Q037 inversion of actual/estimated ratio returns correct answer',1/s.Rational(2,3)*4,s.Integer(6))]
out=[]
for name,actual,expected in items:
 assert actual==expected,(name,actual,expected)
 out.append({'check':name,'actual':str(actual),'expected':str(expected),'passed':True})
p=R/'audits/W05-L25-v2-python-post-reveal-checks.json'
p.write_text(json.dumps({'createdAt':datetime.now(timezone.utc).isoformat(),'phase':'Post-answer-freeze rationale reconciliation, not blind solving','checks':out,'allPassed':True},indent=2)+'\n')
print('5 post-reveal rationale checks passed')
