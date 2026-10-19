Vt = np.diag([0.02, np.deg2rad(0.5)]) ** 2
robot = Unicycle(covar=Vt, animation="car")
robot.control = RandomPath(workspace=5)
E0 = np.diag([0.05, 0.05, np.deg2rad(0.5)]) ** 2
ekf = EKF(robot=(robot, V), P0=E0)
ekf.run(T=20)
html = ekf.run_animation(T=20, format="html")
HTML(html)
robot.plot_xy(color="b")
ekf.plot_xy(color="r")
ekf.plot_ellipse(filled=True, facecolor="g", alpha=0.3)
