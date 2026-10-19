# Transcribed from actual pixels, lecture physical pages 499–500, printed 27–28.
# This file preserves the runnable code, not an OCR guess or repaired version.
import numpy as np
import matplotlib.pyplot as plt

# Inputs
theta_0 = 10
theta_f = 70
theta_dot_0 = 0
theta_dot_f = 0
tf = 5

# Coefficients
a0 = theta_0
a1 = theta_dot_0
A = np.array([[tf**2, tf**3],
              [2*tf, 3*tf**2]])
B = np.array([theta_f - a0 - a1*tf,
              theta_dot_f - a1])
[a2, a3] = np.linalg.solve(A, B)

# Time
t = np.linspace(0, tf, 100)

# Trajectory
theta = a0 + a1*t + a2*t**2 + a3*t**3
theta_dot = a1 + 2*a2*t + 3*a3*t**2
theta_ddot = 2*a2 + 6*a3*t

# Plot
plt.figure(figsize=(10,6))

# Position
plt.subplot(3,1,1)
plt.plot(t, theta)
plt.title(r'Joint Trajectory $\theta(t)$')
plt.ylabel(r'$\theta(t)$')

# Velocity
plt.subplot(3,1,2)
plt.plot(t, theta_dot)
plt.title(r'Joint Velocity $\dot{\theta}(t)$')
plt.ylabel(r'$\dot{\theta}(t)$')

# Acceleration
plt.subplot(3,1,3)
plt.plot(t, theta_ddot)
plt.title(r'Joint Acceleration $\ddot{\theta}(t)$')
plt.ylabel(r'$\ddot{\theta}(t)$')
plt.xlabel('Time (s)')

plt.tight_layout()
plt.show()
