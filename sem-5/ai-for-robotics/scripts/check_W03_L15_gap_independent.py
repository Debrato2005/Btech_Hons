"""Fresh source-derived L15 GAP calculation before its author key/solution reveal."""
import sympy as s,hashlib,datetime,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sqrt=s.sqrt
checks=[]
def check(name,condition):
 assert bool(condition),name
 checks.append(name)
M=s.Matrix([[23,15],[15,12]]);V=s.Matrix([-24*sqrt(3),3*sqrt(3)]);G=s.Matrix([25*sqrt(3),0])
J=s.Matrix([[sqrt(3)/2,0],[s.Rational(5,2),2]]);Jd=s.Matrix([[1,0],[-sqrt(3),0]])
w=s.Matrix([1,2]);acc=s.Matrix([s.Rational(1,2),-s.Rational(1,4)])
Mx=s.simplify(J.inv().T*M*J.inv());Vx=s.simplify(J.inv().T*(V-M*J.inv()*Jd*w));Gx=s.simplify(J.inv().T*G)
ac=s.simplify(J*acc+Jd*w);F=s.simplify(Mx*ac+Vx+Gx);tau=s.simplify(J.T*F)
check('Mass transform',Mx==s.diag(s.Rational(17,3),3));check('Expanded Vx',Vx==s.Matrix([-s.Rational(367,6),9*sqrt(3)/2]));check('Gravity transform',Gx==s.Matrix([50,0]));check('Component acceleration',ac==s.Matrix([1+sqrt(3)/4,s.Rational(3,4)-sqrt(3)]));check('Full task force',F==s.Matrix([-s.Rational(11,2)+17*sqrt(3)/12,s.Rational(9,4)+3*sqrt(3)/2]));check('Back transformed torque',tau==s.Matrix([s.Rational(31,4)+sqrt(3),s.Rational(9,2)+3*sqrt(3)]));check('Independent direct joint equation',s.simplify(tau-(M*acc+V+G))==s.zeros(2,1));check('Power pairing',s.simplify((F.T*J*w)[0]-(tau.T*w)[0])==0)
# Independently identify the plausible mistakes in the three distractor tuples.
Vx2=s.simplify(J.inv().T*V);F2=s.simplify(Mx*ac+Vx2+Gx);tau2=s.simplify(J.T*F2)
Vx3=s.Matrix([-54,9*sqrt(3)/2]);F3=s.simplify(Mx*ac+Vx3+Gx);tau3=s.simplify(J.T*F3)
tau4=s.simplify(J*F)
def dec(x):return [round(float(v),3) for v in x]
check('o1 rounding',dec(Vx)==[-61.167,7.794] and dec(F)==[-3.046,4.848] and dec(tau)==[9.482,9.696])
check('o2 omitted Jdot correction',dec(Vx2)==[-55.5,2.598] and dec(F2)==[2.62,-.348] and dec(tau2)==[1.399,-.696])
check('o3 omitted cosine terms',dec(Vx3)==[-54,7.794] and dec(F3)==[4.12,4.848] and dec(tau3)==[15.689,9.696])
check('o4 wrong effort map J not transpose',dec(tau4)==[-2.638,2.08])
# Repaired older numeric distractors, with prior version exposure explicitly disclosed.
check('Q006 mass matrix',s.Matrix([[12+5,12],[12,12]])==s.Matrix([[17,12],[12,12]]))
check('Q006 l2=1 distractor',s.Matrix([[3+5,3],[3,3]])==s.Matrix([[8,3],[3,3]]))
Jold=s.Matrix([[1,0],[2,2]]);check('Q028 inverse',Jold.inv()==s.Matrix([[1,0],[-1,s.Rational(1,2)]]))
check('Q028 unnormalized row',2*Jold.inv()[1,:]==s.Matrix([[-2,1]]))
check('Q032 no correction distractor',Jold.inv().T*s.Matrix([-48,6])==s.Matrix([-54,3]))
out={'reviewerId':'define_robotics_data_contracts:L15-independent-reviewer','runAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gapAuthorKeySeen':False,'priorV1RevisionKeyExposure':True,'assertionCount':len(checks),'assertions':checks,'derivedValues':{name:{'exact':str(x),'rounded':dec(x)} for name,x in [('Vx',Vx),('componentAcceleration',ac),('Gx',Gx),('F',F),('tau',tau)]},'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(R/'audits/W03-L15-gap-independent-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
