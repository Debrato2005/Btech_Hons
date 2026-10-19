#!/usr/bin/env python3
"""Explicitly repaired setup for L31. Syntax checked; NOT runtime executed here.
Repairs: all imports precede use; metric and pixel cameras have distinct names;
metric calibration is explicit; source's incorrect mm annotation is not copied.
Requires optional machinevision-toolbox-python and spatialmath-python packages.
"""
import numpy as np
from machinevisiontoolbox import CentralCamera,mkgrid,mkcube
from spatialmath import SE3
metric=CentralCamera(f=.015,rho=1,pp=[0,0])
P=np.array([.3,.4,5.])
p=metric.project_point(P)
assert np.allclose(p,[[.0009],[.0012]])
assert np.allclose(p*1000,[[.9],[1.2]])
assert np.allclose(metric.project_point(P,pose=SE3.Tx(-.5)),[[.0024],[.0012]])
camera=CentralCamera(f=.015,rho=10e-6,imagesize=[1280,1024],pp=[640,512])
assert np.allclose(camera.project_point(P),[[730],[632]])
P_grid=mkgrid(n=3,side=.2,pose=SE3.Tz(1))
grid=camera.project_point(P_grid)
shifted=camera.project_point(P_grid,pose=SE3.Trans(-.25,0,0))
assert np.allclose(shifted-grid,np.tile([[375],[0]],(1,9)))
P_points=np.column_stack([[0,0,10],[10,10,10],[.3,.4,5]])
p,visible=camera.project_point(P_points,visibility=True)
assert np.allclose(p,[[640,2140,730],[512,2012,632]])
assert np.array_equal(visible,[True,False,True])
X,Y,Z=mkcube(.2,pose=SE3.Tz(1),edge=True)
# Optional source plots; require a working display/backend when invoked.
if __name__=='__main__':
 print('Toolbox reproduction passed with explicit setup.')
