"""Reviewer transcription from actual L54 slide pixels, without author artifacts."""
from pathlib import Path
import json,time,datetime,hashlib,sys,platform,warnings,inspect,importlib.util
import numpy as np, sklearn
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.neural_network import MLPRegressor
R=Path(__file__).resolve().parents[1];out=R/'audits/W11-L54-contracts-source-runtime.json';assert not out.exists()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
svm_source='''np.random.seed(0)
N = 600
X_norm = np.column_stack([
    np.random.normal(2.0, 0.2, N//2),
    np.random.normal(1500, 50, N//2),
    np.random.normal(45, 3, N//2),
])
X_over = np.column_stack([
    np.random.normal(5.5, 0.5, N//2),
    np.random.normal(900, 100, N//2),
    np.random.normal(72, 5, N//2),
])
X = np.vstack([X_norm, X_over])
y = np.array([0]*len(X_norm) + [1]*len(X_over))
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
svm = Pipeline([
    ('sc', StandardScaler()),
    ('svc', SVC(kernel='rbf', C=10, gamma='scale', class_weight='balanced'))
])
svm.fit(X_tr, y_tr)
y_pred = svm.predict(X_te)
print(classification_report(y_te, y_pred, target_names=['normal', 'overload']))
'''
ik_source='''L1, L2 = 1.0, 1.0
N = 40000
t1 = np.random.uniform(-np.pi, np.pi, N)
t2 = np.random.uniform(0, np.pi, N)
x = L1*np.cos(t1) + L2*np.cos(t1+t2)
y = L1*np.sin(t1) + L2*np.sin(t1+t2)
X = np.column_stack([x, y])
Y = np.column_stack([t1, t2])
X_tr, X_te, Y_tr, Y_te = train_test_split(X, Y, test_size=0.1)
model = Pipeline([
    ('sc', StandardScaler()),
    ('mlp', MLPRegressor(hidden_layer_sizes=(256,256,128),
        activation='tanh', max_iter=300,
        learning_rate_init=1e-3, random_state=42))
])
model.fit(X_tr, Y_tr)
pred = model.predict(X_te)
xp = L1*np.cos(pred[:,0]) + L2*np.cos(pred[:,0]+pred[:,1])
yp = L1*np.sin(pred[:,0]) + L2*np.sin(pred[:,0]+pred[:,1])
err = np.sqrt((xp-X_te[:,0])**2 + (yp-X_te[:,1])**2)
print(f'Mean position error: {err.mean()*100:.2f} cm')
prediction = model.predict([[-1.0, 1.0]])
theta1_rad = prediction[0][0]
theta2_rad = prediction[0][1]
print(f'Theta 1: {theta1_rad:.4f} radians -> {np.degrees(theta1_rad):.2f} degrees')
print(f'Theta 2: {theta2_rad:.4f} radians -> {np.degrees(theta2_rad):.2f} degrees')
'''
source_artifact=R/'audits/W11-L54-contracts-source-transcription.json';assert not source_artifact.exists();source_artifact.write_text(json.dumps(dict(reviewerId='robotics-contracts-reviewer-L54',transcribedAt=now(),sourceSha256='2dcca11fda764949d36f6f174bd72ccc2a83c2863f522635e7afd8539d88f84c',sourcePages={'svm':list(range(1727,1731)),'ik':list(range(1736,1741))},svm=svm_source,ik=ik_source,qualification='Transcribed directly from actual pixels. Imports shared above; spacing normalized only. IK source has no generator or split seed. This run executes it after the SVM source in the same default interpreter so its initial random state is documented, not claimed historically identical. No model or dependency retrieval. Illustration-only mglearn call is not a model-training program.'),indent=2)+'\n')
report=dict(reviewerId='robotics-contracts-reviewer-L54',startedAt=now(),status='running',python=sys.version,executable=sys.executable,numpy=np.__version__,sklearn=sklearn.__version__,platform=platform.platform(),transcriptionPath=str(source_artifact.relative_to(R)),transcriptionSha256=hashlib.sha256(source_artifact.read_bytes()).hexdigest(),plotDependencyAvailable=importlib.util.find_spec('mglearn')is not None,runtimeQualification='Default installed interpreter and packages only. No network, package/model/audio/NLTK download, restricted temporary environment or hardware operation.',apiDefaults=MLPRegressor().get_params())
t=time.monotonic();ns=globals();exec(svm_source,ns);report['svm']=dict(seconds=time.monotonic()-t,trainShape=list(X_tr.shape),testShape=list(X_te.shape),trainClassCounts=np.bincount(y_tr).tolist(),testClassCounts=np.bincount(y_te).tolist(),report=classification_report(y_te,y_pred,target_names=['normal','overload'],output_dict=True),gamma=float(svm.named_steps['svc']._gamma),classWeights=svm.named_steps['svc'].class_weight_.tolist(),supportCounts=svm.named_steps['svc'].n_support_.tolist(),scalerMean=svm.named_steps['sc'].mean_.tolist());out.write_text(json.dumps(report,indent=2)+'\n');print('SVM report saved; beginning complete 40,000-row IK fit',flush=True)
t=time.monotonic()
with warnings.catch_warnings(record=True)as ws:
 warnings.simplefilter('always');exec(ik_source,ns)
report['ik']=dict(seconds=time.monotonic()-t,trainShape=list(X_tr.shape),testShape=list(X_te.shape),predictionShape=list(pred.shape),errorShape=list(err.shape),meanPositionErrorCm=float(err.mean()*100),medianPositionErrorCm=float(np.median(err)*100),maxPositionErrorCm=float(err.max()*100),historicalMeanPositionErrorCm=9.82,examplePrediction=prediction.tolist(),iterationCount=int(model.named_steps['mlp'].n_iter_),loss=float(model.named_steps['mlp'].loss_),outputActivation=model.named_steps['mlp'].out_activation_,weightShapes=[list(x.shape)for x in model.named_steps['mlp'].coefs_],biasShapes=[list(x.shape)for x in model.named_steps['mlp'].intercepts_],parameterCount=sum(x.size for x in model.named_steps['mlp'].coefs_+model.named_steps['mlp'].intercepts_),warnings=[dict(category=w.category.__name__,message=str(w.message))for w in ws],randomContext='Unseeded IK generator and split inherit state after the exact seed-0 SVM generator; MLP uses its printed random_state=42. One disclosed fresh execution, not a reproduction claim for undocumented historical randomness.')
report['completedAt']=now();report['status']='completed';out.write_text(json.dumps(report,indent=2)+'\n');print('Completed reviewer source runtime',report['ik']['seconds'],flush=True)
