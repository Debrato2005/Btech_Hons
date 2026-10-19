#!/usr/bin/env python3
"""Independent L11 derivation checks, not imported from the author's checks."""
import datetime
import itertools
import json
import math
import platform
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(110352378)
groups = []


def eq(a, b, tol=1e-9):
    np.testing.assert_allclose(a, b, atol=tol, rtol=tol)


def record(name, cases):
    groups.append({"group": name, "cases": cases, "passed": True})


def skew(w):
    x, y, z = w
    return np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]], float)


def rot(w):
    a = np.linalg.norm(w)
    if a < 1e-18:
        return np.eye(3)
    k = skew(w / a)
    return np.eye(3) + math.sin(a) * k + (1 - math.cos(a)) * (k @ k)


def vee(w):
    return np.array([w[2, 1], w[0, 2], w[1, 0]])


def tensor(points, masses):
    return sum(m * ((p @ p) * np.eye(3) - np.outer(p, p))
               for p, m in zip(points, masses))


def acceleration(a0, ar, w, alpha, r, vr):
    return (a0 + ar + 2 * np.cross(w, vr) + np.cross(alpha, r)
            + np.cross(w, np.cross(w, r)))


z = np.zeros(3)
eq(acceleration(z, z, [0, 0, 2], z, [3, 0, 0], z), [-12, 0, 0])
eq(acceleration(z, z, z, [0, 0, 3], [2, 0, 0], z), [0, 6, 0])
eq(acceleration(z, z, [0, 0, 3], [0, 0, 2], [2, 0, 0], [1, 0, 0]), [-18, 10, 0])
eq(acceleration(np.array([1, 2, 0]), z, [0, 0, 2], [0, 0, 1], [2, 0, 0], z), [-7, 4, 0])
eq(np.cross([0, 0, 2], [3, 0, 0]), [0, 6, 0])
R90 = rot(np.array([0, 0, math.pi / 2]))
eq(np.array([1, 0, 0]) + R90 @ [2, 0, 0] + np.cross([0, 0, 1], R90 @ [3, 0, 0]), [-2, 2, 0])
eq(tensor([np.array([1, 2, 3])], [2]), [[26, -4, -6], [-4, 20, -12], [-6, -12, 10]])
eq(np.array([1, 2, 3]) * np.array([2, 3, 1]) * 2, [4, 12, 6])
eq((2 * 0 + 1 * 3) / 3, 1)
eq((1 * np.array([0, 0, 0]) + 3 * np.array([2, 4, 0])) / 4, [1.5, 3, 0])
eq(3 * 2**2 / 12 + 3 * (2 / 2)**2, 4)
eq(6 * (2**2 + 4**2) / 12, 10)
eq([2 * .6**2, 2 * .3**2], [.72, .18])
eq((.72 - .18) / .72, .75)
eq(2 * 2 * 3**2, 36)
I = np.array([[2, 1, 0], [1, 2, 0], [0, 0, 4]])
v = np.array([1, 1, 0]) / np.sqrt(2)
eq(I @ v, 3 * v)
record("Sixteen direct numeric and vector examples", 16)

# Differentiate the actual point trajectory in A, including a moving origin,
# time-varying angular speed and quadratic B-relative point motion.
for _ in range(500):
    axis = rng.normal(size=3)
    axis /= np.linalg.norm(axis)
    theta, rate, angular_acc = rng.normal(size=3)
    p0, vel0, acc0, q0, qv, qa = rng.normal(size=(6, 3))
    R0 = rot(rng.normal(size=3))

    def R(t):
        return rot(axis * (theta + rate*t + .5*angular_acc*t*t)) @ R0

    def position(t):
        return p0 + vel0*t + .5*acc0*t*t + R(t) @ (q0 + qv*t + .5*qa*t*t)

    h = 2e-4
    finite = (position(h) - 2*position(0) + position(-h)) / h**2
    expected = acceleration(acc0, R(0) @ qa, axis*rate, axis*angular_acc,
                            R(0) @ q0, R(0) @ qv)
    eq(finite, expected, 6e-6)
record("Full acceleration transport versus second differences", 500)

# Recover angular acceleration from independent composed orientation matrices:
# alpha^ = Rddot R^T + Rdot Rdot^T. No author trace/formula implementation used.
for _ in range(250):
    wb, ab, wc, ac = rng.normal(size=(4, 3))
    RB0 = rot(rng.normal(size=3))
    RC0 = rot(rng.normal(size=3))

    def RB(t):
        return rot(wb*t + .5*ab*t*t) @ RB0

    def RC(t):
        return rot(wc*t + .5*ac*t*t) @ RC0

    def total(t):
        return RB(t) @ RC(t)

    h = 1e-4
    d = (total(h) - total(-h)) / (2*h)
    dd = (total(h) - 2*total(0) + total(-h)) / h**2
    finite_alpha = vee(dd @ total(0).T + d @ d.T)
    expected = ab + RB0 @ ac + np.cross(wb, RB0 @ wc)
    eq(finite_alpha, expected, 4e-6)
record("Angular-acceleration composition from orientation derivatives", 250)

for _ in range(500):
    pts = rng.normal(size=(20, 3))
    masses = rng.uniform(.01, 5, size=20)
    mass = masses.sum()
    com = np.sum(masses[:, None] * pts, axis=0) / mass
    centered = pts - com
    Ic = tensor(centered, masses)
    Ia = tensor(pts, masses)
    shift = mass * ((com @ com)*np.eye(3) - np.outer(com, com))
    eq(Ia, Ic + shift)
    raw_a = sum(m*p[0]*p[1] for p, m in zip(pts, masses))
    raw_c = sum(m*p[0]*p[1] for p, m in zip(centered, masses))
    eq(raw_a, raw_c + mass*com[0]*com[1])
    eq(Ia[0, 1], -raw_a)
    eq(np.trace(shift), 2*mass*(com @ com))
    R = rot(rng.normal(size=3))
    Ir = tensor(pts @ R.T, masses)
    eq(Ir, R @ Ia @ R.T)
    eq(np.trace(Ir), np.trace(Ia))
    eq(np.linalg.eigvalsh(Ir), np.linalg.eigvalsh(Ia))
    vals = np.linalg.eigvalsh(Ia)
    assert min(vals) > 0 and vals[-1] <= vals[0] + vals[1] + 1e-8
record("COM, signed/raw shifts, tensor rotations and physical inequalities", 500)

# Three-point Gauss quadrature is exact for each polynomial in the box tensor.
nodes, weights = np.polynomial.legendre.leggauss(3)
for mass, w, length, height in [(12, 2, 4, 6), *rng.uniform(.2, 6, size=(99, 4))]:
    lengths = np.array([w, length, height])
    samples = []
    dm = []
    for i, j, k in itertools.product(range(3), repeat=3):
        samples.append((np.array([nodes[i], nodes[j], nodes[k]])+1)*lengths/2)
        dm.append(mass*weights[i]*weights[j]*weights[k]/8)
    samples = np.array(samples)
    Ic = tensor(samples - lengths/2, dm)
    Ia = tensor(samples, dm)
    diag = mass*np.array([length**2+height**2, w**2+height**2, w**2+length**2])
    eq(np.diag(Ia), diag/3)
    eq(Ia[np.triu_indices(3, 1)], -mass*np.array([w*length, w*height, length*height])/4)
    eq(Ic, np.diag(diag/12))
record("Exact volume quadrature for corner and COM box tensors", 100)

for _ in range(250):
    points = rng.normal(size=(10, 3))
    reflected = points * [1, 1, -1]
    pairs = np.vstack([points, reflected])
    m = np.tile(rng.uniform(.1, 2, 10), 2)
    I = tensor(pairs, m)
    eq(I[0, 2], 0)
    eq(I[1, 2], 0)
    eq(I[0, 0] + I[1, 1] - I[2, 2], 2*np.sum(m*pairs[:, 2]**2))
record("Single-plane symmetry and moment triangle identity", 250)

line = np.array([[1, 0, 0], [-1, 0, 0]])
eq(tensor(line, [1, 1]), np.diag([0, 2, 2]))
eq(tensor([np.zeros(3)], [1]), np.zeros((3, 3)))
nonphysical = np.diag([1., 1., 3.])
assert min(np.linalg.eigvalsh(nonphysical)) > 0
assert nonphysical[0, 0] + nonphysical[1, 1] - nonphysical[2, 2] < 0
# A single xy symmetry plane does not force Pxy=0.
eq(tensor([np.array([1, 1, 1]), np.array([1, 1, -1])], [1, 1])[0, 1], -2)
record("Degenerate distributions and SPD-only counterexample", 4)

xml = '''<link name="forearm"><inertial><mass value="1.5"/>
<origin xyz="0 0 0.15" rpy="0 0 0"/>
<inertia ixx="0.003" ixy="0" ixz="0" iyy="0.003" iyz="0" izz="0.001"/>
</inertial></link>'''
root = ET.fromstring(xml)
mass = float(root.find("inertial/mass").attrib["value"])
offset = np.array([float(x) for x in root.find("inertial/origin").attrib["xyz"].split()])
values = root.find("inertial/inertia").attrib
assert values['izz'] == '0.001' and isinstance(values['izz'], str)
Ic = np.diag([float(values[x]) for x in ['ixx', 'iyy', 'izz']])
eq(Ic + mass*((offset @ offset)*np.eye(3)-np.outer(offset, offset)),
   np.diag([.03675, .03675, .001]))
eq(np.linalg.eigvalsh(Ic), [.001, .003, .003])
record("Literal source XML parsing and link-origin inertia", 3)

out = {"checkedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "independentOfAuthorChecks": True, "seed": 110352378,
       "python": platform.python_version(), "numpy": np.__version__,
       "groups": groups, "caseCount": sum(g['cases'] for g in groups),
       "allPassed": True,
       "scope": "Checks concern the stated kinematics and inertia models, not unconditional robot stability, efficiency, safety, or tool availability."}
(ROOT/'audits/W03-L11-independent-computations.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
