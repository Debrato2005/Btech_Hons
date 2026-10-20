import math,random,json,datetime,pathlib
D=pathlib.Path(__file__).resolve().parent
c=(16-9-4)/(2*3*2);assert c==.25;angle=math.degrees(math.acos(c));assert round(angle,2)==75.52
x=2*math.cos(0)+2*math.cos(math.pi/2);y=2*math.sin(0)+2*math.sin(math.pi/2);assert math.isclose(x,2)and math.isclose(y,2)
assert [1*(-2)+2*1,2*(-2)+4*1]==[0,0];assert 1*4-2*2==0 and 1!=0
assert .3*5-0*10==1.5
rng=random.Random(2026102002)
for _ in range(1000):
 l1,l2=rng.uniform(.1,10),rng.uniform(.1,10);a,b=rng.uniform(-math.pi,math.pi),rng.uniform(-math.pi,math.pi)
 xx=l1*math.cos(a)+l2*math.cos(a+b);yy=l1*math.sin(a)+l2*math.sin(a+b);cc=(xx*xx+yy*yy-l1*l1-l2*l2)/(2*l1*l2)
 assert math.isclose(cc,math.cos(b),abs_tol=1e-12)
 r=[rng.uniform(-5,5),rng.uniform(-5,5)];f=[rng.uniform(-5,5),rng.uniform(-5,5)];rot=lambda v:[math.cos(a)*v[0]-math.sin(a)*v[1],math.sin(a)*v[0]+math.cos(a)*v[1]];rp,fp=rot(r),rot(f)
 assert math.isclose(r[0]*f[1]-r[1]*f[0],rp[0]*fp[1]-rp[1]*fp[0],abs_tol=1e-12)
 u,v=[rng.uniform(-10,10)for _ in range(2)];out=[u+2*v,2*u+4*v];assert math.isclose(out[1],2*out[0],abs_tol=1e-12)
# Reachability and two branches: inner/outer radii, rather than only a too-far condition.
assert ((.5**2-9-4)/12)<-1 and ((6**2-9-4)/12)>1
for b in [math.acos(.25),-math.acos(.25)]:
 a=-math.atan2(2*math.sin(b),3+2*math.cos(b));assert math.isclose(3*math.cos(a)+2*math.cos(a+b),4,abs_tol=1e-12);assert math.isclose(3*math.sin(a)+2*math.sin(a+b),0,abs_tol=1e-12)
(D/'W02-independent-checks.json').write_text(json.dumps(dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),fk=[x,y],elbowCosine=c,elbowAnglesDeg=[angle,-angle],nullVector=[-2,1],outputDirection=[1,2],torqueNm=1.5,variedTrials=1000,variedAssertions=3000,extraBoundaries='Inner/outer unreachable radii; both explicit IK branch reconstructions.',scope='Default standard-library arithmetic only; source printed keys exposed after initial independent responses. No robot or model runtime.'),indent=2)+'\n')
print('W02 fixed arithmetic, two IK branches, two reachability exclusions and 3000 varied assertions passed.')
