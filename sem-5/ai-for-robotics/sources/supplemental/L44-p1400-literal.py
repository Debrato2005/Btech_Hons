map = LandmarkMap(20, workspace=10)
V = np.diag([0.02, np.deg2rad(0.5)]) ** 2
robot = Unicycle(covar=V, animation="car")
robot.control = RandomPath(workspace=map)
W = np.diag([0.1, np.deg2rad(1)]) ** 2
sensor = RangeBearingSensor(robot=robot, map=map, covar=W,
    angle=[-np.pi/2, np.pi/2], range=4, animate=True)
P0 = np.diag([0.05, 0.05, np.deg2rad(0.5)]) ** 2
ekf = EKF(robot=(robot, V), P0=P0, map=map, sensor=(sensor, W))
ekf.run(T=20)
map.plot()
robot.plot_xy(color="b")
ekf.plot_xy(color="r")
ekf.plot_ellipse()
