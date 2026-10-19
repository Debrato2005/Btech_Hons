"""Printed L55 MLP code, with declared author seed and output/plot instrumentation.
No original notebook retrieved. No package installation. Never presented as the slide's exact run.
"""
from pathlib import Path
import json,time,datetime,hashlib
import numpy as np
import sklearn
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
np.random.seed(5519) # ADDED for this reproducible run; not printed on the source slides.
L1,L2=1.0,1.0
m1,m2=1.0,1.0
g_acc=9.81
def inverse_dynamics(q1,q2,dq1,dq2,ddq1,ddq2):
 M11=(m1+m2)*L1**2+m2*L2**2+2*m2*L1*L2*np.cos(q2)
 M12=m2*L2**2+m2*L1*L2*np.cos(q2)
 M22=m2*L2**2
 h=m2*L1*L2*np.sin(q2)
 C1=-h*dq2**2-2*h*dq1*dq2
 C2=h*dq1**2
 g1=(m1+m2)*g_acc*L1*np.cos(q1)+m2*g_acc*L2*np.cos(q1+q2)
 g2=m2*g_acc*L2*np.cos(q1+q2)
 tau1=M11*ddq1+M12*ddq2+C1+g1
 tau2=M12*ddq1+M22*ddq2+C2+g2
 return tau1,tau2
if __name__=='__main__':
 start=time.monotonic();N=50000
 q1=np.random.uniform(-np.pi,np.pi,N);q2=np.random.uniform(-np.pi,np.pi,N)
 dq1=np.random.uniform(-2*np.pi,2*np.pi,N);dq2=np.random.uniform(-2*np.pi,2*np.pi,N)
 ddq1=np.random.uniform(-10,10,N);ddq2=np.random.uniform(-10,10,N)
 tau1,tau2=inverse_dynamics(q1,q2,dq1,dq2,ddq1,ddq2)
 X=np.column_stack([q1,q2,dq1,dq2,ddq1,ddq2]);Y=np.column_stack([tau1,tau2])
 X_tr,X_te,Y_tr,Y_te=train_test_split(X,Y,test_size=.1,random_state=42)
 model=Pipeline([('sc',StandardScaler()),('mlp',MLPRegressor(hidden_layer_sizes=(256,256,128),activation='tanh',max_iter=500,learning_rate_init=1e-3,random_state=42,verbose=True))])
 model.fit(X_tr,Y_tr)
 Y_pred=model.predict(X_te);rmse=np.sqrt(np.mean((Y_pred-Y_te)**2,axis=0))
 # Added evaluation of the explicit sinusoidal trajectory printed later on p1772.
 t=np.linspace(0,4*np.pi,300);q1t=np.sin(t);q2t=.5*np.sin(2*t);dq1t=np.cos(t);dq2t=np.cos(2*t);ddq1t=-np.sin(t);ddq2t=-2*np.sin(2*t)
 Xt=np.column_stack([q1t,q2t,dq1t,dq2t,ddq1t,ddq2t]);Yt=np.column_stack(inverse_dynamics(q1t,q2t,dq1t,dq2t,ddq1t,ddq2t));pred=model.predict(Xt)
 fig,axs=plt.subplots(2,1,figsize=(10,6),sharex=True)
 for j,ax in enumerate(axs):ax.plot(t,Yt[:,j],label='Analytical label');ax.plot(t,pred[:,j],'--',label='Author seeded MLP run');ax.set_ylabel(f'Torque {j+1} (N m)');ax.legend();ax.grid(True)
 axs[-1].set_xlabel('Time (s)');fig.suptitle('L55 printed MLP parameters; author-added seed 5519');fig.tight_layout();plot=R/'audits/W11-L55-author-mlp-trajectory.png';fig.savefig(plot,dpi=130);plt.close(fig)
 result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Printed p1758–1761 MLP code with only an added NumPy seed5519 and reporting/plot instrumentation. Trajectory evaluation combines the printed p1772 trajectory with this MLP, not the omitted DeLaN class.','versions':{'numpy':np.__version__,'sklearn':sklearn.__version__},'sourcePages':[1758,1759,1760,1761,1772],'seedAdded':5519,'shapes':{'X':list(X.shape),'Y':list(Y.shape),'train':list(X_tr.shape),'test':list(X_te.shape)},'epochsActuallyExecuted':model.named_steps['mlp'].n_iter_,'parameterCount':sum(a.size for a in model.named_steps['mlp'].coefs_+model.named_steps['mlp'].intercepts_),'randomTestRMSE_Nm':rmse.tolist(),'trajectoryRMSE_Nm':np.sqrt(np.mean((pred-Yt)**2,axis=0)).tolist(),'sourceReportedRMSE_Nm':[.6311,.3734],'sourceExactOutputReproduced':False,'scalerTrainingMeanMatches':bool(np.allclose(model.named_steps['sc'].mean_,X_tr.mean(axis=0))),'seconds':time.monotonic()-start,'independentReview':False,'plot':str(plot.relative_to(R)),'plotSha256':hashlib.sha256(plot.read_bytes()).hexdigest()}
 (R/'audits/W11-L55-mlp-runtime.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
