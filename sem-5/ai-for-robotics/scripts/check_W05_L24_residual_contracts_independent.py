"""Reproduce the five independent matrix assertions saved before L24 v3 key access.

These calculations were first executed in the source-first freeze operation and
recorded in audits/blind-answers-W05-L24-residual-contracts-reviewer.json.
This standalone file preserves those exact calculations for recovery. Running it
later is a reproducibility check, not a newly blind solve.
"""
import numpy as np
M=np.array([[2.,1.],[1.,2.]])
D=np.diag([3.,4.]);mi=np.linalg.inv(M);tau=np.array([3.,0.])
checks=[('left gain product retains off diagonals',mi@D,[[2,-4/3],[-1,8/3]]),
        ('right multiplication differs',D@mi,[[2,-1],[-4/3,8/3]]),
        ('negative actual perturbation',-mi@tau,[-2,1]),
        ('positive error perturbation',-(-mi@tau),[2,-1]),
        ('current versus other pose',np.linalg.solve(np.diag([4.,2.]),tau),[.75,0])]
for name,actual,expected in checks:
    assert np.allclose(actual,expected),(name,actual,expected)
print('PASS: five reproduced source-first matrix assertions.')
