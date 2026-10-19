"""Executable toy-array checks; no claim of executing unavailable source image assets."""
import numpy as np,json,datetime
from pathlib import Path
from scipy.signal import correlate2d,convolve2d
R=Path(__file__).resolve().parents[1];checks=[]
def check(name,ok,actual=None):
 assert bool(ok),name
 checks.append({'name':name,'passed':True,'actual':actual})
a=np.zeros((640,426,3),dtype=np.uint8)
check('source NumPy crop is empty width',a[250:400,450:600,:].shape==(150,0,3),list(a[250:400,450:600,:].shape))
check('intended crop has150 rows150 columns',a[450:600,250:400,:].shape==(150,150,3))
check('uint8 overflow at256',(np.array([200],dtype=np.uint8)+np.uint8(100)).item()==44)
check('negative96',255-96==159)
check('threshold100',np.array([99,100,101]).__ge__(100).tolist()==[False,True,True])
stretch=255*(118-91)/(138-91);gamma=255*(np.array([91.,118.,138.])/255)**7.5
check('stretch118',np.isclose(stretch,146.48936170212767),float(stretch))
check('gamma118',np.isclose(gamma[1],.7881409299213445),gamma.tolist())
check('CDF example',np.array([1,2,1,0]).cumsum().tolist()==[1,3,4,4])
check('CDF100 at.32',np.isclose(255*.32,81.6))
H=np.array([[0,255,0,255,0],[0,255,0,255,0],[0,255,255,255,0],[0,255,0,255,0],[0,255,0,255,0]],dtype=float)
box=np.ones((3,3))/9
v=correlate2d(H,box,mode='valid')
check('H bright pixel count',(H>0).sum()==11)
check('box left113.333',np.isclose(v[0,0],113.33333333333333),float(v[0,0]))
check('box middle198.333',np.isclose(v[0,1],198.33333333333333),float(v[0,1]))
G=np.array([[1,2,1],[2,4,2],[1,2,1]],float)/16;g=correlate2d(H,G,mode='valid')
check('binomial sum',np.isclose(G.sum(),1))
check('binomial left143.4375',np.isclose(g[0,0],143.4375),float(g[0,0]))
check('binomial middle159.375',np.isclose(g[0,1],159.375),float(g[0,1]))
i,j=np.meshgrid(np.arange(-1,2),np.arange(-1,2));sigma=.85
raw=np.exp(-(i*i+j*j)/(2*sigma*sigma))/(2*np.pi*sigma*sigma);norm=raw/raw.sum()
check('standard Gaussian central coefficient',np.isclose(raw[1,1],1/(2*np.pi*sigma*sigma)),{'raw':float(raw[1,1]),'normalized':float(norm[1,1]),'finiteSum':float(raw.sum())})
check('Gaussian not exact binomial',not np.allclose(norm,G))
X=np.array([[1,2,3],[4,5,6],[7,8,9.]])
K=np.array([[1,2,0],[3,1,0],[0,0,0.]])
check('conv rotates not transposes',np.allclose(convolve2d(X,K,mode='valid'),correlate2d(X,K[::-1,::-1],mode='valid')))
D=np.array([[1,2,0],[2,0,0],[0,0,3.]])
check('transpose symmetric not sufficient',np.array_equal(D,D.T) and not np.array_equal(D,D[::-1,::-1]))
S=np.array([[1,0,-1],[2,0,-2],[1,0,-1]],float)/8
ramp=np.tile(np.arange(5.),(5,1))
check('source convolution Sobel positive ramp',np.allclose(convolve2d(ramp,S,mode='valid'),1))
check('correlation same Sobel negative ramp',np.allclose(correlate2d(ramp,S,mode='valid'),-1))
check('transposed kernel vertical ramp',np.allclose(convolve2d(ramp.T,S.T,mode='valid'),1))
check('central difference ramp',np.isclose((7-3)/2,2))
check('40 profile values39differences',len(np.diff(np.arange(560,600)))==39)
check('valid output dimensions',convolve2d(np.ones((9,11)),np.ones((3,3)),mode='valid').shape==(7,9))
for mode,expected in [('constant',510/9),('edge',765/9),('reflect',1530/9)]:
 padded=np.pad(H,1,mode=mode);res=correlate2d(padded,box,mode='valid')[0,0];check('border '+mode,np.isclose(res,expected),float(res))
M=np.array([[10,11,10,0,0],[9,10,11,1,0],[10,9,10,0,2],[11,10,9,10,9],[9,10,11,9,99]])
check('median first center10',np.median(M[:3,:3])==10)
check('median second center9',np.median(M[2:,2:])==9)
x=np.array([0,0,1]);y=np.array([0,1,0]);check('median nonadditive',np.median(x+y)!=np.median(x)+np.median(y))
check('rank median',9//2==4 and 25//2==12)
rng=np.random.default_rng(320019)
for n in range(500):
 X=rng.normal(size=(9,11));K=rng.normal(size=(3,3));assert np.allclose(convolve2d(X,K,mode='valid'),correlate2d(X,K[::-1,::-1],mode='valid'));assert np.isclose(np.median(X[:3,:3]),np.sort(X[:3,:3].ravel())[4]);assert np.isclose((K/K.sum()).sum(),1)
out={'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceId':'lectures','sourceSha256':'2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c','checks':checks,'assertions':len(checks),'variedTrials':500,'checksPerTrial':3,'allPassed':True,'numpyVersion':np.__version__,'scope':'Hand-built toy arrays and explicit slide formulas only; original flower/pollen/castle image assets and machinevision-toolbox Image methods were not executed.'}
(R/'audits/W07-L32-author-code-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
