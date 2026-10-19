import numpy as np
import matplotlib.pyplot as plt
l1 = 5
l2 = 4
theta1 = np.linspace(-np.pi, np.pi, 200)
theta2 = np.linspace(-np.pi, np.pi, 200)
x_points = []
y_points = []
for t1 in theta1:
    for t2 in theta2:
        x = l1 * np.cos(t1) + l2 * np.cos(t1 + t2)
        y = l1 * np.sin(t1) + l2 * np.sin(t1 + t2)
        x_points.append(x)
        y_points.append(y)
plt.figure(figsize=(8,8))
plt.scatter(x_points, y_points, s=1)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Articulated Robot Workspace')
plt.axis('equal')
plt.grid(True)
plt.show()
