#!/usr/bin/env python3
"""Rev H2 isometric drawings: the robot from four sides, the pick-up sequence, and the robot carrying a bin.
Writes ../fig/iso_*.png. Geometry comes from params.py; details params.py does not fix (brackets, caster forks, braces,
lamp positions, the shape of the bin's front lip) are drawn as intended, not as designed. Concept illustration only.

Method: a small software renderer (numpy z-buffer, flat shading, depth-tested outlines) so hidden lines are right
without any 3D library. Orthographic isometric projection: elevation 35.264 deg, azimuth +/-45 or +/-135 deg.
The one section view is cut on a vertical plane and seen at a shallower angle."""
import os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import params as P
R = P.ROBOT
FIG = os.path.join(HERE, '..', 'fig'); os.makedirs(FIG, exist_ok=True)


def rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


SURF = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'
C = dict(frame=('#dbe8f8', '#2a78d6'), carriage=('#8fbaf0', '#1c5fb5'), comb=('#1c5fb5', '#0f3f80'), tyre=('#6b6f76', '#2b2d31'),
         hub=('#d5d8dd', '#52514e'), motor=('#c3c8cf', '#52514e'), batt=('#b9b8b1', '#52514e'), ebox=('#eeede8', '#52514e'),
         act=('#c3c8cf', '#52514e'), rod=('#f2f2ee', '#52514e'), lidar=('#4a4d52', '#1e2023'), lamp=('#fff1a8', '#8a7a1c'),
         beacon=('#f5a623', '#9a6410'), red=('#e05a4f', '#8f2a22'), strip=('#f7f7f4', '#8d8c85'), rubber=('#4a4d52', '#1e2023'),
         bin=('#fbe3d8', '#eb6834'), lid=('#f7cdb9', '#eb6834'), ground=('#f1f0ec', None), arrow=('#cfcdc5', None))
BIN_ID = 2; WHOLE_ID = 3                                         # object ids: 0 ground, 1 robot, 2 bin, 3 robot parts never cut by a section


# ------------------------------------------------------------------------------------------------ scene
class Scene:
    def __init__(self):
        self.faces = []; self.edges = []; self.cyls = []

    def poly(self, V, key, oid=1):
        self.faces.append((np.asarray(V, np.float64), key, oid))

    def solid(self, V, faces, key, oid=1, lw=1.0, edges=True):
        """Convex polyhedron: vertices V, faces as index loops. Every face-loop edge is outlined once."""
        V = np.asarray(V, np.float64); seen = set()
        for f in faces:
            self.faces.append((V[list(f)], key, oid))
            if edges and C[key][1]:
                for i in range(len(f)):
                    a, b = f[i], f[(i + 1) % len(f)]
                    if (min(a, b), max(a, b)) not in seen:
                        seen.add((min(a, b), max(a, b))); self.edges.append((V[a], V[b], rgb(C[key][1]), lw, oid))

    def hexa(self, bot, top, key, **kw):
        """bot, top: four corners each, same order round the loop."""
        self.solid(list(bot) + list(top), [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], key, **kw)

    def box(self, x0, x1, y0, y1, z0, z1, key, **kw):
        self.hexa([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], key, **kw)

    def prism(self, loop, lift, key, **kw):
        """Convex loop of 3D points swept by the vector lift."""
        n = len(loop); V = [tuple(p) for p in loop] + [tuple(np.add(p, lift)) for p in loop]
        faces = [tuple(range(n)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        self.solid(V, faces, key, **kw)

    def beam(self, p0, p1, w, h, key, **kw):
        """Rectangular bar from p0 to p1: w across (horizontal), h in the plane of the bar and the vertical."""
        p0 = np.asarray(p0, float); p1 = np.asarray(p1, float); a = p1 - p0; a /= np.linalg.norm(a)
        s = np.cross(a, (0, 0, 1.0)); s = s / np.linalg.norm(s) if np.linalg.norm(s) > 1e-6 else np.array((0, 1.0, 0)); u = np.cross(s, a)
        c = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        self.hexa([p0 + i * s + j * u for i, j in c], [p1 + i * s + j * u for i, j in c], key, **kw)

    def cyl(self, p0, p1, r, key, oid=1, lw=1.0, n=48):
        p0 = np.asarray(p0, float); p1 = np.asarray(p1, float); a = (p1 - p0) / np.linalg.norm(p1 - p0)
        t = np.cross(a, (0, 0, 1.0)); t = t / np.linalg.norm(t) if np.linalg.norm(t) > 1e-6 else np.array((1.0, 0, 0)); b = np.cross(a, t)
        ring = [r * (math.cos(2 * math.pi * i / n) * t + math.sin(2 * math.pi * i / n) * b) for i in range(n)]
        A = [p0 + q for q in ring]; B = [p1 + q for q in ring]; f = key
        self.faces.append((np.array(A), f, oid)); self.faces.append((np.array(B), f, oid))
        for i in range(n):
            j = (i + 1) % n; self.faces.append((np.array([A[i], A[j], B[j], B[i]]), f, oid))
        if C[key][1]:
            e = rgb(C[key][1])
            for i in range(n):
                j = (i + 1) % n; self.edges.append((A[i], A[j], e, lw, oid)); self.edges.append((B[i], B[j], e, lw, oid))
            self.cyls.append((p0, p1, a, r, e, lw, oid))


# ------------------------------------------------------------------------------------------------ robot
def add_robot(sc, comb_top):
    gi = R['leg_inner_gap'] / 2; mo = R['funnel_mouth'] / 2; xk = R['leg_tip_x'] + R['funnel_len']; tip = R['leg_tip_x']; nose = R['nose_tip_x']
    z0, z1 = 0.26, 0.31                                              # rail section 50 x 50, top face at 0.31 m
    mx0, mx1 = R['mast_x'] - 0.025, R['mast_x'] + 0.025; hs = R['mast_half_span']
    for sg in (1, -1):
        # side rail with its flared tip
        sc.box(xk, nose - 0.015, *sorted((sg * gi, sg * (gi + 0.05))), z0, z1, 'frame')
        loop = [(xk, sg * gi, z0), (tip, sg * mo, z0), (tip, sg * (mo + 0.05), z0), (xk, sg * (gi + 0.05), z0)]
        sc.prism(loop if sg > 0 else loop[::-1], (0, 0, z1 - z0), 'frame')
        sc.box(tip - 0.008, tip, *sorted((sg * mo, sg * (mo + 0.05))), z0, z1, 'rubber')                              # bump strip on the tip
        sc.box(tip + 0.055, tip + 0.085, *sorted((sg * (gi + 0.035), sg * (gi + 0.047))), z0 + 0.012, z1 - 0.012, 'rubber')   # gap sensor
        sc.box(tip, tip + 0.02, *sorted((sg * (mo + 0.012), sg * (mo + 0.038))), z1, z1 + 0.022, 'red')                # rear marker lamp
        sc.box(-0.20, 0.36, *sorted((sg * (gi - 0.010), sg * gi)), z0 + 0.004, z1 - 0.004, 'strip')                    # guide strip
        # anti-tip wheel under the tip
        yt = sg * R['tail_track'] / 2; zt = R['tail_r'] + R['tail_gap']
        sc.cyl((R['tail_x'], yt - 0.016, zt), (R['tail_x'], yt + 0.016, zt), R['tail_r'], 'tyre')
        sc.box(R['tail_x'] - 0.018, R['tail_x'] + 0.018, *sorted((yt + sg * 0.018, yt + sg * 0.026)), zt - 0.012, z0, 'motor')
        # battery on the rail, behind the drive wheel
        bx = R['batt_x']
        sc.box(bx - 0.0925, bx + 0.0925, *sorted((sg * (gi - 0.008), sg * (gi + 0.072))), z1, z1 + 0.167, 'batt')
        for xt in (bx - 0.055, bx + 0.055):
            sc.cyl((xt, sg * (gi + 0.032), z1 + 0.167), (xt, sg * (gi + 0.032), z1 + 0.180), 0.009, 'rubber')
        # drive unit: wheel outside the rail, gearbox under it, motor lying aft under the rail
        yw = sg * R['drive_track'] / 2; r = R['drive_r']
        sc.cyl((0, yw - 0.035, r), (0, yw + 0.035, r), r, 'tyre', lw=1.2)
        sc.cyl((0, yw - 0.039, r), (0, yw + 0.039, r), 0.072, 'hub')
        sc.cyl((0, yw - 0.043, r), (0, yw + 0.043, r), 0.022, 'motor')
        sc.box(-0.065, 0.065, *sorted((sg * gi, sg * (abs(yw) - 0.035))), 0.095, 0.225, 'motor')
        sc.box(-0.085, 0.085, *sorted((sg * gi, sg * (abs(yw) - 0.040))), 0.225, z0, 'frame')
        sc.cyl((-0.30, sg * (gi + 0.045), 0.16), (-0.065, sg * (gi + 0.045), 0.16), 0.045, 'motor')
        sc.cyl((-0.335, sg * (gi + 0.045), 0.16), (-0.30, sg * (gi + 0.045), 0.16), 0.040, 'rubber')                   # spring brake
        # nose caster under an outrigger plate
        yc = sg * R['nose_track'] / 2; rn = R['nose_r']; xc = R['nose_x']; xp = xc + 0.055
        sc.cyl((xc, yc - 0.032, rn), (xc, yc + 0.032, rn), rn, 'tyre', lw=1.2)
        sc.cyl((xc, yc - 0.036, rn), (xc, yc + 0.036, rn), 0.055, 'hub')
        for s2 in (1, -1):
            sc.beam((xc, yc + s2 * 0.044, rn), (xp - 0.01, yc + s2 * 0.044, 0.272), 0.006, 0.05, 'motor')
        sc.box(xp - 0.07, xp + 0.05, yc - 0.05, yc + 0.05, 0.268, 0.282, 'motor')
        sc.cyl((xp, yc, 0.282), (xp, yc, z1), 0.038, 'motor')
        sc.box(xp - 0.075, nose - 0.015, *sorted((sg * 0.215, sg * (gi + 0.05))), z1, z1 + 0.008, 'frame')
        # mast upright, roller-side brace to the rail
        sc.box(mx0, mx1, sg * hs - 0.025, sg * hs + 0.025, z1, R['height'], 'frame')
        sc.beam((mx1 + 0.004, sg * hs, 0.92), (nose - 0.10, sg * (gi + 0.025), z1 + 0.008), 0.03, 0.03, 'frame')
        # headlamp on the nose cross-member
        sc.cyl((nose - 0.062, sg * 0.20, z1 + 0.036), (nose - 0.018, sg * 0.20, z1 + 0.036), 0.028, 'motor')
        sc.cyl((nose - 0.018, sg * 0.20, z1 + 0.036), (nose - 0.012, sg * 0.20, z1 + 0.036), 0.024, 'lamp')
    # cross-members, bumper bar, mast ties
    sc.box(nose - 0.065, nose - 0.015, -(gi + 0.05), gi + 0.05, z0, z1, 'frame')
    sc.box(nose - 0.015, nose, -(gi + 0.05), gi + 0.05, z0 + 0.005, z1 - 0.005, 'rubber')
    sc.box(mx0, mx1, -(gi + 0.05), gi + 0.05, z0, z1, 'frame')
    sc.box(mx0, mx1, -(hs + 0.025), hs + 0.025, R['height'] - 0.05, R['height'], 'frame')
    # lift actuator between the uprights, on the nose side
    xa = mx1 + 0.03; rod_top = comb_top + 0.13
    sc.box(xa - 0.03, xa + 0.03, -0.03, 0.03, z1, z1 + 0.03, 'frame')
    sc.cyl((xa, 0, z1 + 0.03), (xa, 0, 0.86), 0.026, 'act')
    sc.box(xa - 0.03, xa + 0.07, -0.032, 0.032, z1 + 0.03, z1 + 0.10, 'act')
    sc.cyl((xa, 0, 0.86), (xa, 0, rod_top), 0.011, 'rod')
    # electronics box on the nose side of the mast, E-stop on its side
    sc.box(mx1 + 0.075, mx1 + 0.225, -0.14, 0.14, 0.45, 0.71, 'ebox', oid=WHOLE_ID)
    for sg in (1, -1):
        sc.box(mx1, mx1 + 0.075, sg * 0.10 - 0.012, sg * 0.10 + 0.012, 0.55, 0.58, 'frame', oid=WHOLE_ID)
    sc.box(mx1 + 0.11, mx1 + 0.19, 0.14, 0.165, 0.60, 0.68, 'lamp', oid=WHOLE_ID)
    sc.cyl((mx1 + 0.15, 0.165, 0.64), (mx1 + 0.15, 0.195, 0.64), 0.026, 'red', oid=WHOLE_ID)
    # lidar with a drip cap, rear camera, amber beacon
    lx = nose - 0.04
    sc.cyl((lx, 0, z1), (lx, 0, z1 + 0.012), 0.03, 'motor'); sc.cyl((lx, 0, z1 + 0.012), (lx, 0, z1 + 0.05), 0.036, 'lidar')
    sc.cyl((lx, 0, z1 + 0.056), (lx, 0, z1 + 0.062), 0.05, 'motor')
    sc.box(mx0 - 0.03, mx1, -0.035, 0.035, R['height'], R['height'] + 0.05, 'lidar')
    sc.cyl((mx0 - 0.036, 0, R['height'] + 0.025), (mx0 - 0.03, 0, R['height'] + 0.025), 0.016, 'hub')
    sc.cyl((R['mast_x'], 0.14, R['height']), (R['mast_x'], 0.14, R['height'] + 0.012), 0.036, 'motor')
    sc.cyl((R['mast_x'], 0.14, R['height'] + 0.012), (R['mast_x'], 0.14, R['height'] + 0.065), 0.03, 'beacon')
    add_carriage(sc, comb_top)


def add_carriage(sc, ct):
    """Roller carriage on the bin side of the mast. ct = height of the comb's top edge."""
    mx0, mx1 = R['mast_x'] - 0.025, R['mast_x'] + 0.025; hs = R['mast_half_span']; hw = R['comb_width'] / 2; px = R['pad_x']; pd = R['pad_drop']
    seat = px + 0.020                                                                              # comb tooth centre (seat line)
    sc.box(px + 0.030, mx0 - 0.004, -0.27, 0.27, ct - 0.10, ct - 0.04, 'carriage')                 # top bar
    sc.box(px + 0.024, px + 0.036, -0.05, 0.05, ct - 0.085, ct - 0.035, 'hub')                     # comb pivot block (yaw and roll float)
    sc.box(seat - 0.004, seat + 0.004, -hw, hw, ct - 0.075, ct - 0.014, 'comb')                    # comb plate, 640 mm ...
    n = 16; pitch = 2 * hw / n
    for i in range(n):                                                                             # ... and its teeth
        y = -hw + (i + 0.25) * pitch; sc.box(seat - 0.004, seat + 0.004, y, y + pitch / 2, ct - 0.014, ct, 'comb')
    for sg in (1, -1):
        sc.box(px + 0.030, mx0 - 0.004, sg * hs - 0.03, sg * hs + 0.03, ct - pd - 0.08, ct - 0.10, 'carriage')              # side member
        for zr in (ct - 0.17, ct - pd - 0.07):                                                     # roller blocks round the upright
            sc.box(mx0 - 0.004, mx1 + 0.008, *sorted((sg * (hs + 0.027), sg * (hs + 0.05))), zr, zr + 0.07, 'carriage')
            sc.cyl((R['mast_x'], sg * (hs + 0.05), zr + 0.035), (R['mast_x'], sg * (hs + 0.058), zr + 0.035), 0.018, 'hub')
    pf = seat - R['pad_setback']                                                                    # pad face: behind the seat line by the set-back
    sc.box(px + 0.030, mx0 - 0.004, -0.25, 0.25, ct - pd - 0.03, ct - pd + 0.03, 'carriage')       # lower bar
    sc.box(pf + 0.012, px + 0.030, -0.20, 0.20, ct - pd - 0.05, ct - pd + 0.05, 'carriage')        # slotted pad bracket
    sc.box(pf, pf + 0.012, -R['pad_width'] / 2, R['pad_width'] / 2, ct - pd - R['pad_height'] / 2, ct - pd + R['pad_height'] / 2, 'rubber')   # rubber rest pad
    sc.box(mx0 - 0.004, mx1 + 0.06, -0.022, 0.022, ct - 0.10, ct - 0.06, 'carriage')               # lug through the mast ...
    sc.box(mx1 + 0.012, mx1 + 0.048, -0.022, 0.022, ct - 0.06, ct + 0.15, 'carriage')              # ... and the horn the actuator rod pushes


# ------------------------------------------------------------------------------------------------ bin
def add_bin(sc, x_front, z_base, key='ESE240SL'):
    """240 L bin. x_front = robot-frame x of its front wall at rim height; the bin extends towards -x (handle to the rear)."""
    b = P.BINS[key]; hw = b['W'] / 2; bd = b['D'] - 0.105; zr = b['comb'] + 0.02; o = BIN_ID
    X = lambda xb: x_front - xb; Z = lambda z: z_base + z
    zc = zr - 0.06                                                    # collar under the rim
    top = [(X(0.004), -hw + 0.012, Z(zc)), (X(bd - 0.004), -hw + 0.012, Z(zc)), (X(bd - 0.004), hw - 0.012, Z(zc)), (X(0.004), hw - 0.012, Z(zc))]
    bot = [(X(0.038), -0.235, Z(0)), (X(bd - 0.125), -0.235, Z(0)), (X(bd - 0.125), 0.235, Z(0)), (X(0.038), 0.235, Z(0))]
    sc.hexa(bot, top, 'bin', oid=o, lw=1.2)
    sc.box(X(bd), X(0), -hw, hw, Z(zc), Z(zr), 'bin', oid=o, lw=1.2)
    # frontal comb receiver: a ledge with a turned-down flange
    sc.box(X(0), X(-0.038), -hw + 0.03, hw - 0.03, Z(zr - 0.02), Z(zr), 'bin', oid=o)
    sc.box(X(-0.030), X(-0.038), -hw + 0.03, hw - 0.03, Z(zr - 0.05), Z(zr - 0.02), 'bin', oid=o)
    # lid
    prof = [(-0.034, zr + 0.004), (-0.034, zr + 0.022), (0.10, zr + 0.045), (bd + 0.01, zr + 0.054), (bd + 0.03, zr + 0.03), (bd + 0.03, zr + 0.004)]
    sc.prism([(X(xb), -hw - 0.008, Z(z)) for xb, z in prof], (0, 2 * hw + 0.016, 0), 'lid', oid=o, lw=1.2)
    # handle
    for y in (-0.19, 0.0, 0.19):
        sc.box(X(bd + 0.085), X(bd), y - 0.012, y + 0.012, Z(zr - 0.045), Z(zr - 0.005), 'bin', oid=o)
    sc.cyl((X(bd + 0.085), -0.215, Z(zr - 0.022)), (X(bd + 0.085), 0.215, Z(zr - 0.022)), 0.014, 'lid', oid=o)
    # wheels and axle
    rw = b['wheel'] / 2; yw = b['track'] / 2 - 0.0225; xa = X(P.AXLE_TO_FRONT[key])
    sc.cyl((xa, -yw, Z(rw)), (xa, yw, Z(rw)), 0.011, 'motor', oid=o)
    for sg in (1, -1):
        sc.cyl((xa, sg * yw - 0.0225, Z(rw)), (xa, sg * yw + 0.0225, Z(rw)), rw, 'tyre', oid=o, lw=1.2)
        sc.cyl((xa, sg * yw - 0.026, Z(rw)), (xa, sg * yw + 0.026, Z(rw)), 0.045, 'hub', oid=o)
    return dict(wheel=(xa, yw, z_base), rim=Z(zr), lip=(x_front + 0.034, 0.0, Z(zr - 0.03)), handle=(X(bd + 0.085), 0.0, Z(zr - 0.022)), lid=(X(0.3), 0.0, Z(zr + 0.05)))


def add_ground(sc, x0, x1, y0, y1, arrows=()):
    sc.poly([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], 'ground', oid=0)
    for xa, ya, length, sgn in arrows:                               # flat arrow on the ground, pointing +x (sgn 1) or -x (sgn -1)
        z = 0.002; a = lambda dx, dy: (xa + sgn * dx, ya + dy, z)
        sc.poly([a(0, -0.03), a(length - 0.16, -0.03), a(length - 0.16, 0.03), a(0, 0.03)], 'arrow', oid=0)
        sc.poly([a(length - 0.16, -0.09), a(length, 0.0), a(length - 0.16, 0.09)], 'arrow', oid=0)


# ------------------------------------------------------------------------------------------------ renderer
class View:
    """Orthographic view. az = compass angle of the camera round the vertical (0 = on the nose side, 90 = on the robot's left)."""
    def __init__(self, az, scale, origin, size, el=35.264, ss=2):
        az, el = math.radians(az), math.radians(el)
        self.c = np.array((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))      # towards the camera
        self.r = np.array((-math.sin(az), math.cos(az), 0.0)); self.u = np.cross(self.c, self.r)
        self.scale, self.origin, self.size, self.ss = scale, origin, size, ss
        self.W, self.H = size[0] * ss, size[1] * ss
        L = -0.45 * self.r + 0.80 * self.u + 0.55 * self.c; self.L = L / np.linalg.norm(L)

    def proj(self, Pts):
        d = np.atleast_2d(np.asarray(Pts, float))
        return np.stack([(self.origin[0] + d @ self.r * self.scale) * self.ss, (self.origin[1] - d @ self.u * self.scale) * self.ss, d @ self.c], 1)

    def px(self, p):                                                 # position in the finished (downsampled) image
        q = self.proj(p)[0]; return q[0] / self.ss, q[1] / self.ss


def fit(az, scenes, size, margins=(60, 60, 140, 40), extra=(), scale=None, el=35.264):
    """View that fits every vertex of the scenes (and the extra points) inside the panel margins (left, right, top, bottom)."""
    v0 = View(az, 1.0, (0, 0), size, el=el)
    pts = np.concatenate([f[0] for sc in scenes for f in sc.faces] + ([np.asarray(extra, float)] if len(extra) else []))
    U = pts @ v0.r; Vv = pts @ v0.u; ml, mr, mt, mb = margins
    sc_fit = min((size[0] - ml - mr) / (U.max() - U.min()), (size[1] - mt - mb) / (Vv.max() - Vv.min()))
    k = sc_fit if scale is None else scale
    ox = ml + (size[0] - ml - mr) / 2 - (U.max() + U.min()) / 2 * k; oy = mt + (size[1] - mt - mb) / 2 + (Vv.max() + Vv.min()) / 2 * k
    return View(az, k, (ox, oy), size, el=el), sc_fit


def raster(sc, v, clip_y=None, hide=()):
    W, H = v.W, v.H; bg = rgb(SURF)
    zb = np.full((H, W), -1e9, np.float32); img = np.empty((H, W, 3), np.float32); img[:] = bg
    segs = [e for e in sc.edges if e[4] not in hide]
    for V, key, oid in sc.faces:
        if oid in hide: continue
        n = np.cross(V[1] - V[0], V[2] - V[0]); ln = np.linalg.norm(n)
        if ln < 1e-12: continue
        n /= ln
        if n @ v.c < 0: n = -n
        col = rgb(C[key][0]) * (1.0 if oid == 0 else 0.82 + 0.18 * max(0.0, float(n @ v.L)))
        cut_this = clip_y is not None and oid in (1, BIN_ID)
        if cut_this:
            if V[:, 1].min() >= clip_y: continue
            cut = []                                                 # outline of the cut through this face
            for i in range(len(V)):
                p, q = V[i], V[(i + 1) % len(V)]
                if (p[1] - clip_y) * (q[1] - clip_y) < 0: cut.append(p + (q - p) * (clip_y - p[1]) / (q[1] - p[1]))
            if len(cut) == 2 and C[key][1]: segs.append((cut[0], cut[1], rgb(C[key][1]), 1.8, oid))
        U = v.proj(V)
        for k in range(1, len(V) - 1):
            a, b, c = U[0], U[k], U[k + 1]
            x0 = max(int(math.floor(min(a[0], b[0], c[0]))), 0); x1 = min(int(math.ceil(max(a[0], b[0], c[0]))), W - 1)
            y0 = max(int(math.floor(min(a[1], b[1], c[1]))), 0); y1 = min(int(math.ceil(max(a[1], b[1], c[1]))), H - 1)
            if x0 > x1 or y0 > y1: continue
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-9: continue
            Xg = (np.arange(x0, x1 + 1, dtype=np.float32) + 0.5)[None, :]; Yg = (np.arange(y0, y1 + 1, dtype=np.float32) + 0.5)[:, None]
            w0 = ((b[1] - c[1]) * (Xg - c[0]) + (c[0] - b[0]) * (Yg - c[1])) / den
            w1 = ((c[1] - a[1]) * (Xg - c[0]) + (a[0] - c[0]) * (Yg - c[1])) / den
            w2 = 1.0 - w0 - w1
            z = w0 * a[2] + w1 * b[2] + w2 * c[2]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4) & (z > sub)
            if cut_this:
                m &= (w0 * V[0][1] + w1 * V[k][1] + w2 * V[k + 1][1]) <= clip_y
            if not m.any(): continue
            sub[m] = z[m]; img[y0:y1 + 1, x0:x1 + 1][m] = col
    # outlines, depth-tested against the finished z-buffer
    for p0, p1, a, r, e, lw, oid in sc.cyls:                          # silhouette generators of each cylinder for this view
        if oid in hide: continue
        s = np.cross(a, v.c); ls = np.linalg.norm(s)
        if ls > 1e-6:
            s = s / ls * r; segs += [(p0 + s, p1 + s, e, lw, oid), (p0 - s, p1 - s, e, lw, oid)]
    bias = 0.006
    for p0, p1, col, lw, oid in segs:
        A, B = v.proj([p0, p1]); n = int(max(abs(B[0] - A[0]), abs(B[1] - A[1]), 1.0)) + 2
        t = np.linspace(0.0, 1.0, n); xs = A[0] + (B[0] - A[0]) * t; ys = A[1] + (B[1] - A[1]) * t; zs = A[2] + (B[2] - A[2]) * t
        ix = xs.astype(np.int32); iy = ys.astype(np.int32); ok = (ix >= 2) & (ix < W - 2) & (iy >= 2) & (iy < H - 2)
        if clip_y is not None and oid in (1, BIN_ID): ok &= (p0[1] + (p1[1] - p0[1]) * t) <= clip_y + 1e-6
        ix, iy, zs = ix[ok], iy[ok], zs[ok]
        vis = zs >= zb[iy, ix] - bias; ix, iy = ix[vis], iy[vis]
        rad = 0.75 * lw * v.ss; k = int(math.ceil(rad))
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                if dx * dx + dy * dy <= rad * rad + 0.3:
                    img[np.clip(iy + dy, 0, H - 1), np.clip(ix + dx, 0, W - 1)] = col
    s = v.ss; out = img.reshape(v.size[1], s, v.size[0], s, 3).mean((1, 3))
    return np.clip(out, 0, 1), zb


# ------------------------------------------------------------------------------------------------ sheets
def scene(comb_top, bin_at=None, lift=0.0, ground=(-0.62, 1.05, -0.72, 0.72), arrows=()):
    sc = Scene(); add_ground(sc, *ground, arrows=arrows); add_robot(sc, comb_top)
    info = add_bin(sc, bin_at, lift) if bin_at is not None else None
    return sc, info


def place_labels(ax, v, labels, zb, name, top=0.15, bottom=0.96):
    """Labels go in the left or right margin at the height of what they point to, pushed apart so they never overlap."""
    W, H = v.size; items = []
    for lb in labels:
        text, world = lb[0], lb[1]; x, y = v.px(world); side = lb[2] if len(lb) > 2 else ('L' if x < W / 2 else 'R')
        X, Y, d = v.proj(world)[0]
        if 0 <= int(Y) < v.H and 0 <= int(X) < v.W and d < zb[int(Y), int(X)] - 0.02: print('   hidden anchor in', name, ':', text.replace('\n', ' '))
        items.append((text, x, y, side))
    for side in 'LR':
        grp = sorted([it for it in items if it[3] == side], key=lambda it: it[2])
        if not grp: continue
        h = [0.021 * (it[0].count('\n') + 1) + 0.020 for it in grp]; pos = [it[2] / H for it in grp]
        for i in range(len(pos)):
            pos[i] = max(pos[i], top + h[0] / 2 if i == 0 else pos[i - 1] + (h[i - 1] + h[i]) / 2)
        if pos[-1] > bottom - h[-1] / 2:
            pos[-1] = bottom - h[-1] / 2
            for i in range(len(pos) - 2, -1, -1): pos[i] = min(pos[i], pos[i + 1] - (h[i] + h[i + 1]) / 2)
        for (text, x, y, _), p in zip(grp, pos):
            ax.plot([x], [y], marker='o', ms=2.6, color=INK, zorder=6)
            ax.annotate(text, xy=(x, y), xytext=(0.025 if side == 'L' else 0.975, 1 - p), textcoords='axes fraction', ha='left' if side == 'L' else 'right', va='center',
                        fontsize=8.5, color=INK, zorder=7, bbox=dict(fc=SURF, ec='none', pad=1.2, alpha=0.85),
                        arrowprops=dict(arrowstyle='-', color=INK2, lw=0.7, shrinkA=3, shrinkB=0, relpos=(1.0 if side == 'L' else 0.0, 0.5)))


def dim3(v, p0, p1, text, off=(0, 0), ha='center', va='center'):
    def draw(ax, vv=v):
        a = vv.px(p0); b = vv.px(p1)
        ax.annotate('', xy=a, xytext=b, arrowprops=dict(arrowstyle='<->', color=INK, lw=0.9, shrinkA=0, shrinkB=0, mutation_scale=9), zorder=6)
        ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], text, fontsize=9, color=INK, ha=ha, va=va, zorder=7,
                bbox=dict(fc=SURF, ec='none', pad=1.5, alpha=0.9))
    return draw


def ext3(v, p0, p1):
    def draw(ax, vv=v):
        a = vv.px(p0); b = vv.px(p1); ax.plot([a[0], b[0]], [a[1], b[1]], color=INK2, lw=0.6, ls=(0, (3, 3)), zorder=5)
    return draw


def sheet(panels, ncols, name, title, foot, psize, dpi=150):
    nrows = (len(panels) + ncols - 1) // ncols
    fw = ncols * psize[0] / dpi; fh = nrows * psize[1] / dpi + 0.95
    fig, axes = plt.subplots(nrows, ncols, figsize=(fw, fh)); fig.patch.set_facecolor(SURF); axes = np.atleast_1d(axes).ravel()
    for ax, pn in zip(axes, panels):
        img, zb = raster(pn['sc'], pn['v'], clip_y=pn.get('clip_y'), hide=pn.get('hide', ()))
        ax.imshow(img, interpolation='nearest'); ax.set_xlim(0, psize[0]); ax.set_ylim(psize[1], 0); ax.axis('off')
        if pn.get('crop'):                                           # cropped detail: clear the title band and frame the picture
            t = 0.125 * psize[1]
            ax.add_patch(plt.Rectangle((0, 0), psize[0], t, fc=SURF, ec='none', zorder=4))
            ax.add_patch(plt.Rectangle((6, t), psize[0] - 12, psize[1] - t - 6, fc='none', ec=INK2, lw=0.7, zorder=8))
        ax.text(0.025, 0.975, pn['title'], transform=ax.transAxes, fontsize=11, weight='bold', color=INK, ha='left', va='top', zorder=9)
        if pn.get('sub'): ax.text(0.025, 0.93, pn['sub'], transform=ax.transAxes, fontsize=8.5, color=INK2, ha='left', va='top', zorder=9)
        place_labels(ax, pn['v'], pn.get('labels', []), zb, pn['title'])
        for fn in pn.get('extra', []): fn(ax)
    for ax in axes[len(panels):]: ax.axis('off')
    fig.text(0.012, 1 - 0.36 / fh, title, fontsize=13, weight='bold', color=INK, ha='left', va='center')
    fig.text(0.012, 0.22 / fh, foot, fontsize=8.5, color=INK2, ha='left', va='center')
    fig.subplots_adjust(left=0.004, right=0.996, top=1 - 0.62 / fh, bottom=0.42 / fh, wspace=0.01, hspace=0.01)
    path = os.path.join(FIG, name); fig.savefig(path, dpi=dpi, facecolor=SURF); plt.close(fig); print('wrote', path)


FOOT = 'Rev H2. Isometric projection, drawn from sim/params.py. Blue: robot. Orange: 240 L bin (ESE 240 SL data-sheet size). Concept illustration, not a drawing to build from.'
B = P.BINS['ESE240SL']; COMB = B['comb']                             # the comb's top edge bears under the lip at this height
LOW = COMB - 0.105                                                    # carriage lowered to pass under the lip
MX = R['mast_x']; NOSE = R['nose_tip_x']; TIP = R['leg_tip_x']; GI = R['leg_inner_gap'] / 2; PX = R['pad_x']; HT = R['height']


def sheet_robot():
    PS = (1250, 1180); M = (185, 185, 130, 30); sc, _ = scene(LOW, ground=(-0.52, 0.96, -0.60, 0.60))
    dims = [(TIP, -0.74, 0), (NOSE, -0.74, 0), (1.02, -0.52, 0), (1.02, 0.52, 0), (MX, 0.82, 0), (MX, 0.82, HT)]
    k = min(fit(a, [sc], PS, M, extra=dims if a == -45 else ())[1] for a in (45, -45, 135, -135))
    v = {a: fit(a, [sc], PS, M, extra=dims if a == -45 else (), scale=k)[0] for a in (45, -45, 135, -135)}
    p1 = dict(sc=sc, v=v[45], title='Front left', sub='Nose towards you. The robot travels nose-first on the lane.', labels=[
        ('Lidar under\na drip cap', (NOSE - 0.04, 0, 0.372)),
        ('Headlamps', (NOSE - 0.012, 0.20, 0.346)),
        ('Safety bumper bar', (NOSE, -0.22, 0.285)),
        ('260 mm nose caster,\nfree to swivel', (R['nose_x'], 0.333, 0.09), 'R'),
        ('Electronics box\nwith E-stop', (MX + 0.25, -0.06, 0.62), 'L'),
        ('Lift actuator,\n4 kN, 400 mm stroke', (MX + 0.081, 0.0, 0.80), 'L'),
        ('Amber beacon', (MX, 0.14, HT + 0.05), 'R'),
        ('Mast: two 50 x 50\nsteel uprights', (MX + 0.025, 0.22, 1.10), 'R'),
        ('Brace', (MX + 0.18, 0.29, 0.62), 'R'),
        ('Battery, one\non each rail', (R['batt_x'], 0.402, 0.40), 'R'),
        ('Drive wheel from\na donor powerchair', (0.0, 0.52, 0.20), 'R')])
    w = v[-45]
    p2 = dict(sc=sc, v=w, title='Front right', sub='Overall size.', extra=[
        ext3(w, (TIP, -0.46, 0), (TIP, -0.78, 0)), ext3(w, (NOSE, -0.40, 0), (NOSE, -0.78, 0)),
        ext3(w, (0.92, -0.52, 0), (1.06, -0.52, 0)), ext3(w, (0.92, 0.52, 0), (1.06, 0.52, 0)),
        ext3(w, (MX, 0.26, HT), (MX, 0.86, HT)),
        dim3(w, (TIP, -0.74, 0), (NOSE, -0.74, 0), '%.2f m long' % (NOSE - TIP), off=(-30, 22)),
        dim3(w, (1.02, -0.52, 0), (1.02, 0.52, 0), '1.04 m wide\nover the drive wheels', off=(70, 30)),
        dim3(w, (MX, 0.82, 0), (MX, 0.82, HT), '%.2f m to the\ntop of the mast' % HT, off=(62, 0))])
    w = v[135]
    p3 = dict(sc=sc, v=w, title='Rear left', sub='Open end towards you. The bin goes in here, front face first.', labels=[
        ('Rear camera', (MX - 0.058, 0, HT + 0.025), 'R'),
        ('Self-aligning comb, 640 mm:\ngoes under the bin\'s front lip', (PX + 0.02, -0.12, LOW), 'R'),
        ('Carriage, runs on\nrollers up the mast', (PX + 0.016, 0.22, LOW - 0.30), 'L'),
        ('Rubber rest pad,\ndepth adjustable', (PX - 0.005, 0.10, LOW - R['pad_drop'] - 0.02), 'L'),
        ('Motor and brake\nunder the rail', (-0.20, -(GI + 0.002), 0.16), 'R'),
        ('Rear corner bumper', (TIP - 0.008, -(R['funnel_mouth'] / 2 + 0.025), 0.285), 'R'),
        ('Flared rail tip\nwith a gap sensor', (TIP + 0.07, -(GI + 0.036), 0.285), 'R'),
        ('Anti-tip wheel,\n75 mm off the ground', (R['tail_x'], R['tail_track'] / 2 + 0.017, 0.11), 'L'),
        ('Plastic guide strip', (0.10, -(GI - 0.011), 0.285), 'R')],
        extra=[dim3(w, (0.22, -GI, 0.31), (0.22, GI, 0.31), '660 mm clear', off=(0, 0))])
    p4 = dict(sc=sc, v=v[-135], title='Rear right')
    sheet([p1, p2, p3, p4], 2, 'iso_1_robot.png', 'Bin Tug Rev H2: the robot from four sides', FOOT + ' Mass %.0f kg.' % P.robot_mass()['m'], PS)


def sheet_pickup():
    PS = (1250, 1120); M = (165, 165, 130, 30); ground = (-1.30, 0.96, -0.60, 0.92); ct = COMB + R['lift']
    scA, iA = scene(LOW, bin_at=PX - 0.80, ground=ground, arrows=[(0.55, 0.78, 0.55, -1)])
    scB, iB = scene(LOW, bin_at=PX, ground=ground)
    scC, iC = scene(ct, bin_at=PX, lift=R['lift'], ground=ground)
    v = fit(135, [scA, scB, scC], PS, M)[0]
    xw, yw, zw = iC['wheel']; xA = iA['wheel'][0]; hwb = B['W'] / 2
    p1 = dict(sc=scA, v=v, title='1. Reverse around the bin', sub='Carriage low. Gap sensors in the rail tips keep the bin centred.', labels=[
        ('Bin stands with its\nfront face to the robot', (xA + 0.35, hwb - 0.012, 0.55), 'R'), ('Handle faces away\nfrom the robot', iA['handle'], 'R'),
        ('Robot reverses', (0.22, 0.78, 0.0), 'L'), ('Comb, lowered', (PX + 0.02, -0.15, LOW), 'R')])
    p2 = dict(sc=scB, v=v, title='2. Square up against the bin', sub='Two switches on the carriage confirm contact. The comb is still below the lip.', labels=[
        ('Bin still on\nits own wheels', (xw, -0.10, B['wheel'] / 2), 'R')])
    p3 = dict(sc=scC, v=v, title='3. Raise the comb until the wheels are clear', sub='Comb switches confirm the lip is seated; two clearance sensors confirm the wheels are off the ground. Nominal lift 100 mm.',
              extra=[ext3(v, (xw, -yw, zw), (xw - 0.20, -yw, zw)), dim3(v, (xw - 0.16, -yw, 0.0), (xw - 0.16, -yw, zw), '100 mm clear', off=(62, 0))],
              labels=[('Lid stays shut:\nthe bin never tilts', iC['lid'], 'R')])
    # section through the lift, cut on a vertical plane just left of the centreline, seen from the robot's left
    yc = 0.08; ctr = np.array((PX + 0.02, yc, ct - 0.22)); k4 = 1500.0
    v4 = View(112, k4, (0, 0), PS, el=18); q = v4.proj(ctr)[0] / v4.ss
    v4 = View(112, k4, (PS[0] * 0.47 - q[0], PS[1] * 0.56 - q[1]), PS, el=18)
    wall = lambda z: (PX - (0.038 - 0.034 * (z - R['lift']) / (B['comb'] - 0.04)), yc, z)       # point on the cut front wall at height z
    p4 = dict(sc=scC, v=v4, clip_y=yc, crop=True, hide=(WHOLE_ID,), title='Detail: how the bin hangs',
              sub='Robot and bin cut open just left of the centreline, seen from the robot\'s left. Nose to the left. Electronics box not drawn.', labels=[
        ('Comb tooth bears\nunder the lip', (PX + 0.020, yc, ct - 0.006), 'L'),
        ('Carriage top bar', (PX + 0.04, yc, ct - 0.04), 'L'),
        ('Horn from the carriage:\nthe actuator rod pushes here', (MX + 0.055, 0.022, ct + 0.05), 'L'),

        ('Actuator body', (MX + 0.055, 0.026, ct - 0.46), 'L'),
        ('Carriage lower bar', (PX + 0.03, yc, ct - R['pad_drop'] + 0.01), 'L'),
        ('Lid', (PX - 0.14, yc, ct + 0.065), 'R'),
        ('Front lip of the bin\n(EN 840 comb receiver)', (PX + 0.034, yc, ct - 0.015), 'R'),
        ('Bin\'s front wall', wall(0.82), 'R'),
        ('Rubber rest pad takes\nthe bin\'s lean', (PX - 0.003, yc, ct - R['pad_drop'] - 0.02), 'R')])
    sheet([p1, p2, p3, p4], 2, 'iso_2_pickup.png', 'Bin Tug Rev H2: picking up a bin', FOOT + ' Set-down is the same steps in reverse.', PS)


def sheet_carry():
    PS = (1250, 1180); M = (185, 185, 130, 30); ground = (-0.52, 1.52, -0.60, 0.60); ct = COMB + R['lift']
    scC, iC = scene(ct, bin_at=PX, lift=R['lift'], ground=ground, arrows=[(0.98, 0.0, 0.48, 1)])
    k = min(fit(a, [scC], PS, M)[1] for a in (45, -45, 135, -135))
    v = {a: fit(a, [scC], PS, M, scale=k)[0] for a in (45, -45, 135, -135)}
    xw, yw, zw = iC['wheel']
    p1 = dict(sc=scC, v=v[45], title='Front left', sub='Carrying nose-first at 0.5 m/s, or 0.8 m/s on the open lane if that is agreed.', labels=[
        ('Direction of travel', (1.30, 0.0, 0.0), 'L'),
        ('Bin upright,\nlid shut by gravity', (iC['lid'][0], 0.15, iC['lid'][2]), 'R'),
        ('Bin sits between\nthe drive wheels', (0.0, 0.52, 0.22), 'R')])
    p2 = dict(sc=scC, v=v[-45], title='Front right', labels=[
        ('Carriage holds the bin\nby its front lip', (MX - 0.029, -0.10, ct - 0.07), 'R'),
        ('Travel', (1.30, 0.0, 0.0), 'R')])
    w = v[135]
    p3 = dict(sc=scC, v=w, title='Rear left', labels=[
        ('Handle to the rear', iC['handle'], 'R'),
        ('153 of 201 kg rides on\nthe two drive wheels', (0.0, 0.52, 0.22), 'L')],
        extra=[ext3(w, (xw, -yw, zw), (xw - 0.20, -yw, zw)), dim3(w, (xw - 0.16, -yw, 0.0), (xw - 0.16, -yw, zw), '100 mm clear', off=(56, 0))])
    p4 = dict(sc=scC, v=v[-135], title='Rear right', labels=[
        ('If a comb switch opens,\nthe robot stops and lowers', (PX + 0.02, -0.29, ct - 0.01), 'R')])
    sheet([p1, p2, p3, p4], 2, 'iso_3_carry.png', 'Bin Tug Rev H2: carrying a full 240 L bin', FOOT + ' %.0f kg all up with a full bin.' % P.combined('ESE240SL', 1.0)['m'], PS)


if __name__ == '__main__':
    which = sys.argv[1:] or ['robot', 'pickup', 'carry']
    if 'robot' in which: sheet_robot()
    if 'pickup' in which: sheet_pickup()
    if 'carry' in which: sheet_carry()
