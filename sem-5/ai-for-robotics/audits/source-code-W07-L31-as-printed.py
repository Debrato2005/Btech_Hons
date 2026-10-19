# Source transcription of physical pages947,949,950. Not standalone runnable code.
# Layout order is preserved within each page. The source's incorrect mm annotation remains.
from machinevisiontoolbox import CentralCamera
camera = CentralCamera(f=0.015);
P = [0.3, 0.4, 5.0]
p = camera.project_point(P)
# Output: [[0.0009], [0.0012]] -> (1.5mm, 2.0mm)
p_moved = camera.project_point(P, pose=SE3.Tx(-0.5))
# Output: [[0.0024], [0.0012]] -> The image point moves to the right.
camera = CentralCamera(f=0.015, rho=10e-6, imagesize=[1280, 1024], pp=[640, 512])
p_pixel = camera.project_point(P)
# Output: [[730.0], [632.0]]
# Physical949
P_grid = mkgrid(n=3, side=0.2, pose=SE3.Tz(1.0))
p_pixel = camera.project_point(P_grid)
camera.plot_point(P_grid)
T_camera = SE3.Trans(-0.25, 0, 0);
camera.plot_point(P_grid, pose=T_camera);
from machinevisiontoolbox import mkgrid
import numpy as np
P_points = np.column_stack([[0, 0, 10], [10, 10, 10], [0.3, 0.4, 5]])
p, visible = camera.project_point(P_points, visibility=True)
# array([[640,2140,730],[512,2012,632]]); visible array([True,False,True])
# Physical950
X, Y, Z = mkcube(0.2, pose=SE3.Tz(1), edge=True)
camera.plot_wireframe(X, Y, Z)
T_camera = SE3.Trans(-0.25, 0, 0);
camera.plot_wireframe(X, Y, Z, pose=T_camera);
