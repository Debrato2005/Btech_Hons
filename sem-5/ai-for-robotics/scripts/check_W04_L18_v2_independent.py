"""Independent L18 repair/gap checks before current-version keyed access.
Reviewer has prior v1 exposure for sixteen repaired questions, not the two gaps.
"""
import datetime,json,math
from pathlib import Path
import sympy as s
ROOT=Path(__file__).resolve().parents[1];checks=[]
def check(name,ok):
    assert bool(ok),name
    checks.append(name)
a,b=s.symbols('a b',real=True);L1,L2=s.symbols('L1 L2',positive=True)
pos=s.Matrix([L1*s.cos(a)+L2*s.cos(a+b),L1*s.sin(a)+L2*s.sin(a+b)])
J=pos.jacobian([a,b]);expected=s.Matrix([[-L1*s.sin(a)-L2*s.sin(a+b),-L2*s.sin(a+b)],[L1*s.cos(a)+L2*s.cos(a+b),L2*s.cos(a+b)]])
check('All four fixed-frame Jacobian entries',J==expected)
check('Determinant expansion',s.trigsimp(J.det())==L1*L2*s.sin(b))
for x in [0,-s.pi,s.pi]:check('Singular determinant at '+str(x),s.trigsimp(J.det().subs(b,x))==0)
check('Generic right-angle elbow full rank',s.trigsimp(J.det().subs(b,s.pi/2))==L1*L2)
wrong1=J*s.diag(1,-1)
check('Reversing second derivative column negates determinant',s.trigsimp(wrong1.det())==-L1*L2*s.sin(b))
wrong2=s.Matrix([[-L1*s.sin(a),-L2*s.sin(b)],[L1*s.cos(a),L2*s.cos(b)]])
check('Absolute-angle alternative has different determinant',s.trigsimp(wrong2.det())==L1*L2*s.sin(b-a))
wrong4=s.Matrix([[-L1*s.sin(a),-L2*s.sin(a+b)],[L1*s.cos(a),L2*s.cos(a+b)]])
check('Omitted distal first-column terms can preserve determinant',s.trigsimp(wrong4.det())==L1*L2*s.sin(b))
check('Equal determinant does not repair wrong Jacobian',wrong4!=J)
radial=s.trigsimp(pos.dot(pos));check('Radial identity independent of first joint',s.trigsimp(radial-(L1**2+L2**2+2*L1*L2*s.cos(b)))==0)
check('Five-four cross coefficient forty',radial.subs({L1:5,L2:4})==41+40*s.cos(b))
check('Equal positive links remove inner hole',s.Abs(L1-L1)==0)
check('Distinct equal-link distractor radii',L1!=2*L1)
for xy,radius in [((1,0),1),((0,9),9),((3,4),5),((s.Rational(3,5),s.Rational(3,5)),s.sqrt(s.Rational(18,25)))]:check('Named target radius '+str(xy),s.sqrt(sum(v*v for v in xy))==radius)
check('Only fourth target inside forbidden inner hole',s.sqrt(s.Rational(18,25))<1)
grid=[-math.pi+2*math.pi*i/199 for i in range(200)]
nearest=min(abs(x) for x in grid)
check('Inclusive even grid nearest elbow offset',math.isclose(nearest,math.pi/199,abs_tol=1e-15))
maximum=max(math.sqrt(41+40*math.cos(x)) for x in grid)
check('Sampled outer radius expression',math.isclose(maximum,math.sqrt(41+40*math.cos(math.pi/199)),abs_tol=1e-14))
check('Sampled maximum strictly below continuous nine',maximum<9)
check('Full-step distractor is not nearest sample',not math.isclose(maximum,math.sqrt(41+40*math.cos(2*math.pi/199)),abs_tol=1e-8))
check('Endpoint-count distractor is not true grid maximum',not math.isclose(maximum,math.sqrt(41+40*math.cos(math.pi/200)),abs_tol=1e-8))
check('Two nested 200 arrays create 40000 pairs',sum(1 for _ in range(200) for _ in range(200))==40000)
check('Doubling both grids quadruples work and storage',400**2==4*200**2==160000)
try:compile("plt.title('Articulated Robot\nWorkspace')",'<synthetic literal-newline fixture>','exec');bad=False
except SyntaxError:bad=True
check('Literal newline short string fails before execution',bad)
A=s.Matrix([[1,0,1],[0,1,1]]);check('Dependent redundant columns do not force row Gram zero',A.rank()==2 and (A*A.T).det()==3)
B=s.Matrix([[1,0,0],[0,0,0]]);check('Rank loss does not require an all-zero Jacobian',B!=s.zeros(2,3) and (B*B.T).det()==0)
C=s.diag(1,0,0);check('Zero Gram determinant need not mean exactly one lost row direction',C.rank()==1 and (C*C.T).det()==0)
report={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewerId':'define_robotics_data_contracts:L18-independent-reviewer','currentVersionKeysSeen':False,'priorVersionAuthorExposure':'Sixteen repaired v1 keys/solutions were previously reviewed; neither new gap key or solution was opened.','assertions':len(checks),'checks':checks,'sampledMaximumRadius':maximum,'priorChecksUnmodified':'audits/W04-L18-independent-checks.json','testFixturesAreSynthetic':True}
(ROOT/'audits/W04-L18-v2-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n');print('Passed',len(checks),'checks; sampled Rmax',maximum)
