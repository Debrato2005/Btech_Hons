"""Author-side checks only; do not count as independent source review."""
import json,math,random
from pathlib import Path
import sympy as s
R=Path(__file__).resolve().parents[1];results=[]
def check(name,condition):
 assert bool(condition),name
 results.append({'name':name,'passed':True})
a,b,l1,l2=s.symbols('a b L1 L2',real=True)
J3=s.Matrix([[l1*s.sin(b),0],[l2+l1*s.cos(b),l2]])
rot=s.Matrix([[s.cos(a+b),-s.sin(a+b)],[s.sin(a+b),s.cos(a+b)]])
pos=s.Matrix([l1*s.cos(a)+l2*s.cos(a+b),l1*s.sin(a)+l2*s.sin(a+b)])
J0=pos.jacobian([a,b]);check('Frame rotation equals position derivative',s.simplify(rot*J3-J0)==s.zeros(2))
check('Body determinant',s.simplify(J3.det()-l1*l2*s.sin(b))==0)
check('Base determinant',s.simplify(J0.det()-l1*l2*s.sin(b))==0)
xi=s.symbols('xi',nonzero=True,real=True)
expr=s.Matrix([s.cos(a+b)/(l1*s.sin(b)),-s.cos(a)/(l2*s.sin(b))-s.cos(a+b)/(l1*s.sin(b))])
check('Inverse unit-X formula',s.simplify(J0*expr)==s.Matrix([1,0]))
check('Tangential finite-rate exception',s.simplify(expr.subs(a,s.pi/2))==s.Matrix([-1/l1,1/l1]))
check('Folded equal links rank1',J3.subs({b:s.pi,l1:2,l2:2}).rank()==1)
check('Example elbow velocity',s.Matrix([2*s.sin(s.pi/6),2*s.cos(s.pi/6)])==s.Matrix([1,s.sqrt(3)]))
check('Tip velocity example',J3.subs({b:s.pi/2,l1:2,l2:1})*s.Matrix([1,s.Rational(-1,2)])==s.Matrix([2,s.Rational(1,2)]))
check('Base command example',J0.subs({a:0,b:s.pi/2,l1:1,l2:1})*s.Matrix([0,-1])==s.Matrix([1,0]))
check('Two-link torques',J3.subs({b:s.pi/2,l1:2,l2:1}).T*s.Matrix([3,4])==s.Matrix([10,4]))
check('Rectangular torques',s.Matrix([[1,0,1],[0,2,1]]).T*s.Matrix([3,4])==s.Matrix([3,8,7]))
q=s.Matrix([s.Rational(1,5),s.Rational(-1,10),s.Rational(3,10)]);j=s.Matrix([[1,0,1],[0,2,1]]);f=s.Matrix([3,4]);check('Power example',(f.T*j*q)[0]==s.Rational(19,10))
def skew(p):return s.Matrix([[0,-p[2],p[1]],[p[2],0,-p[0]],[-p[1],p[0],0]])
ra=s.Matrix([[0,-1,0],[1,0,0],[0,0,1]]);rb=ra.T;p=s.Matrix([1,0,0]);X=rb.row_join(-rb*skew(p)).col_join(s.zeros(3).row_join(rb));Y=ra.row_join(s.zeros(3)).col_join((skew(p)*ra).row_join(ra))
check('Wrench map is velocity-map transpose',Y==X.T)
va=s.Matrix([1,0,0,0,0,2]);wb=s.Matrix([2,0,0,0,0,3]);check('Twist example',X*va==s.Matrix([2,-1,0,0,0,2]));check('Wrench example',Y*wb==s.Matrix([0,2,0,0,0,5]));check('Dual transformed power',(wb.T*X*va)[0]==((Y*wb).T*va)[0]==10)
# Numerical power identity on independent random 2×n matrices, including rectangular maps.
r=random.Random(1010)
for n in (2,3,7):
 for k in range(100):
  m=[[r.uniform(-3,3) for _ in range(n)] for _ in range(2)];force=[r.uniform(-5,5) for _ in range(2)];rates=[r.uniform(-2,2) for _ in range(n)]
  velocity=[sum(m[i][j]*rates[j] for j in range(n)) for i in range(2)];tau=[sum(m[i][j]*force[i] for i in range(2)) for j in range(n)]
  assert abs(sum(force[i]*velocity[i] for i in range(2))-sum(tau[j]*rates[j] for j in range(n)))<1e-10
check('300 randomized rectangular/square power identities',True)
bank=json.loads((R/'data/question-batches/W02-L10.json').read_text());check('Every substantive page has a cited concept',set(range(329,350))<={c['physicalPage'] for q in bank['questions'] for c in q['citations']})
check('No exact duplicate stems',len({q['stem'] for q in bank['questions']})==len(bank['questions']))
report={'reviewType':'author_checks_not_independent','passed':len(results),'randomizedCases':300,'checks':results,'sourceCoverageClaim':'All21 substantive pages have at least one cited concept; only independent review can challenge meaningful omissions.'}
(R/'audits/W02-L10-author-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':len(results),'randomizedCases':300}))
