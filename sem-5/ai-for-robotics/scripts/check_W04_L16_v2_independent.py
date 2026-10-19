"""Independent source-based checks of the two replacement L16 questions."""
from pathlib import Path
import sympy as s,json,datetime,hashlib
R=Path(__file__).resolve().parents[1];t=s.symbols('t');checks=[]
def check(n,c):
 assert bool(c),n
 checks.append(n)
left=1+3*t+2*t**2+t**3
check('Incoming endpoint position',left.subs(t,2)==23)
check('Incoming endpoint rate',s.diff(left,t).subs(t,2)==23)
check('Incoming endpoint acceleration',s.diff(left,t,2).subs(t,2)==16)
b,c=s.symbols('b c');right=23+23*t+b*t**2+c*t**3
check('Matching b',s.solve(s.diff(right,t,2).subs(t,0)-16,b)==[8])
a3,a4,a5=s.symbols('a3 a4 a5');q=1+2*t+3*t**2+a3*t**3+a4*t**4+a5*t**5
sol=s.solve([q.subs(t,1)-5,s.diff(q,t).subs(t,1),s.diff(q,t,2).subs(t,1)-2],[a3,a4,a5]);check('General quintic coefficients',sol=={a3:20,a4:-37,a5:16})
for k,value in [(0,1),(1,2),(2,6)]:check(f'Initial derivative{k}',s.diff(q.subs(sol),t,k).subs(t,0)==value)
for k,value in [(0,5),(1,0),(2,2)]:check(f'Final derivative{k}',s.diff(q.subs(sol),t,k).subs(t,1)==value)
for triplet,acc in [((19,-35,15),0),((22,-41,18),6),((18,-33,14),-2)]:
 poly=q.subs(dict(zip([a3,a4,a5],triplet)));check(f'Distractor{triplet}',poly.subs(t,1)==5 and s.diff(poly,t).subs(t,1)==0 and s.diff(poly,t,2).subs(t,1)==acc)
# Confirm the divided-row explanation independently.
A=s.Matrix([[25,125],[10,75]]);target=s.Matrix([60,0]);x=A.inv()*target
check('Original cubic coefficient solve',x==s.Matrix([s.Rational(36,5),-s.Rational(24,25)]))
check('Divided velocity row valid',(s.Matrix([[2,15]])*x)[0]==0)
check('Divided position RHS is12',(s.Matrix([[5,25]])*x)[0]==12)
out={'reviewerId':'define_robotics_data_contracts:L16-independent-reviewer','runAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'priorV1KeyExposure':True,'currentV2KeySeen':False,'sourcePages':[487,493,497],'assertionCount':len(checks),'assertions':checks,'generalQuintic':str(q.subs(sol)),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(R/'audits/W04-L16-v2-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
