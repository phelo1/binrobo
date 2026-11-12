"""Reduced-order vehicle dynamics for the Rev H test bench.

Each rigid body has 4 degrees of freedom: x (along the lane), z (up), pitch and roll. Wheels are circles that touch a
ground profile through a spring-damper (penalty contact) with regularised Coulomb friction. Left and right wheels can
run over different profiles, so one-sided bumps are represented. Driven wheels have a spin state and a velocity loop
with a torque limit, as in the Rev G MuJoCo study (kv 150, +/-60 N.m). Two bodies can be coupled by a pin joint
(stiff spring) to represent the Rev G tug + tilted bin for calibration.

Not modelled: yaw and lateral motion, tyre carcass enveloping, structural flex. Explicit integration at 0.2 ms.
This is a first-order check written for the concept review; it is not a replacement for MuJoCo or a bench test.
"""
import math

G = 9.81
KT, CT = 2.0e5, 1500.0        # tyre tread shear stiffness (N/m) and damping (N.s/m) for the stick-slip friction model
KB, CB = 4000.0, 30.0          # brake torsional stiffness (N.m/rad) and damping while holding


# ------------------------------------------------------------------------------------------------ ground profiles
class Ground:
    """Piecewise-linear profile z(x) given as a list of (x, z) vertices, extended flat at both ends."""
    def __init__(self, pts):
        self.p = [(float(a), float(b)) for a, b in pts]
        self.segs = []
        P = [(-1e3, self.p[0][1])] + self.p + [(1e3, self.p[-1][1])]
        for i in range(len(P) - 1):
            (x0, z0), (x1, z1) = P[i], P[i + 1]
            if abs(x1 - x0) + abs(z1 - z0) > 1e-9: self.segs.append((x0, z0, x1, z1))

    @staticmethod
    def flat(): return Ground([(0.0, 0.0)])

    @staticmethod
    def step(x0, h): return Ground([(x0, 0.0), (x0, h)])                      # square step up (h > 0) or down (h < 0)

    @staticmethod
    def bump(x0, length, h): return Ground([(x0, 0.0), (x0, h), (x0 + length, h), (x0 + length, 0.0)])

    @staticmethod
    def pothole(x0, length, depth): return Ground([(x0, 0.0), (x0, -depth), (x0 + length, -depth), (x0 + length, 0.0)])

    def contacts(self, cx, cz, r):
        """Contacts of a circle (cx, cz, r) with the solid ground: list of (penetration, nx, nz, px, pz).
        A contact on the interior of a segment is always valid. A contact at a vertex is valid only when BOTH segments that
        meet there have that vertex as their closest point (the wheel centre is in the corner's own region); otherwise the
        neighbouring face already carries the load and counting the vertex too would double the force."""
        cl = []                                                      # per segment: (d, px, pz, end) with end = -1 start, 0 interior, +1 end
        for (x0, z0, x1, z1) in self.segs:
            dx, dz = x1 - x0, z1 - z0; L2 = dx * dx + dz * dz
            t = ((cx - x0) * dx + (cz - z0) * dz) / L2
            end = 0
            if t <= 0.0: t = 0.0; end = -1
            elif t >= 1.0: t = 1.0; end = 1
            px, pz = x0 + t * dx, z0 + t * dz
            cl.append((math.hypot(cx - px, cz - pz), px, pz, end))
        out = []; n = len(cl)
        for i, (d, px, pz, end) in enumerate(cl):
            if d >= r or d < 1e-9: continue
            if end == 1:
                if i + 1 < n and cl[i + 1][3] != -1: continue        # neighbour has an interior (or far) closest point: not a corner contact
                if i + 1 < n: continue                                # true corner: reported once, by the following segment
            elif end == -1:
                if i > 0 and cl[i - 1][3] != 1: continue
            out.append((r - d, (cx - px) / d, (cz - pz) / d, px, pz))
        return out


# ------------------------------------------------------------------------------------------------ model
class Wheel:
    def __init__(self, name, x, y, z, r, k, c, mu, driven=False, crr=0.03, t_lim=60.0, kv=150.0, brake=150.0, i_w=0.06, side=None):
        self.name, self.x, self.y, self.z, self.r = name, x, y, z, r          # body-frame hub position (z = hub height in body frame)
        self.k, self.c, self.mu, self.driven, self.crr = k, c, mu, driven, crr
        self.t_lim, self.kv, self.brake, self.i_w = t_lim, kv, brake, i_w
        self.side = side if side is not None else ('L' if y > 0 else 'R')
        self.w = 0.0                                                            # spin (rad/s), driven wheels only
        self.ang = 0.0; self.ang_ref = None                                     # wheel angle and brake reference (stick-slip brake)
        self.u = 0.0                                                            # tyre tread shear deflection (stick-slip friction)
        self.fn = 0.0; self.ft = 0.0; self.tq = 0.0


class Body:
    def __init__(self, name, m, iyy, ixx, x=0.0, z=0.0):
        self.name, self.m, self.iyy, self.ixx = name, m, iyy, ixx
        self.x, self.z, self.th, self.ph = x, z, 0.0, 0.0                      # CG position, pitch (about +y: nose-DOWN +), roll (left-up +)
        self.vx = self.vz = self.wth = self.wph = 0.0
        self.wheels = []

    def hub(self, w):
        """World position and velocity of a wheel hub. Wheel coordinates are relative to the CG."""
        c, s = math.cos(self.th), math.sin(self.th)
        px = self.x + w.x * c + w.z * s
        pz = self.z - w.x * s + w.z * c + w.y * self.ph
        vx = self.vx + self.wth * (-w.x * s + w.z * c)
        vz = self.vz + self.wth * (-w.x * c - w.z * s) + w.y * self.wph
        return px, pz, vx, vz

    def point(self, lx, lz):
        c, s = math.cos(self.th), math.sin(self.th)
        return (self.x + lx * c + lz * s, self.z - lx * s + lz * c,
                self.vx + self.wth * (-lx * s + lz * c), self.vz + self.wth * (-lx * c - lz * s))


class Sim:
    def __init__(self, bodies, ground_L, ground_R=None, grade=0.0, dt=2e-4, joint=None):
        self.b = bodies; self.gL = ground_L; self.gR = ground_R if ground_R is not None else ground_L
        self.grade = grade                                                      # +grade = lane rises in +x (gravity pulls back)
        self.dt = dt; self.t = 0.0
        self.joint = joint                                                      # (bodyA, (lx, lz), bodyB, (lx, lz), k, c)
        self.v_cmd = 0.0; self.braked = False
        self.log = []

    def step(self):
        dt = self.dt
        gx = -G * math.sin(math.atan(self.grade)); gz = -G * math.cos(math.atan(self.grade))
        F = {id(b): [b.m * gx, b.m * gz, 0.0, 0.0] for b in self.b}             # Fx, Fz, pitch moment, roll moment
        for b in self.b:
            c, s = math.cos(b.th), math.sin(b.th)
            for w in b.wheels:
                px, pz, vx, vz = b.hub(w)
                g = self.gL if w.side == 'L' else self.gR
                fx = fz = 0.0; fn_tot = 0.0; ft_tot = 0.0; slip_main = 0.0
                cons = g.contacts(px, pz, w.r)
                for (pen, nx, nz, _, _) in cons:
                    vn = vx * nx + vz * nz
                    fn = w.k * pen - w.c * vn
                    if fn <= 0.0: continue
                    tx, tz = nz, -nx                                             # tangent pointing forward on level ground
                    vt = vx * tx + vz * tz
                    if w.driven:
                        slip = w.w * w.r - vt
                        ft = KT * w.u + CT * slip                                # elastic tread (stick) ...
                        lim = w.mu * fn
                        if ft > lim: ft = lim; w.u = lim / KT                   # ... sliding at the Coulomb limit
                        elif ft < -lim: ft = -lim; w.u = -lim / KT
                        slip_main = slip
                    else:
                        ft = -w.crr * fn * math.tanh(vt / 0.02)
                    fx += fn * nx + ft * tx; fz += fn * nz + ft * tz; fn_tot += fn; ft_tot += ft
                w.fn, w.ft = fn_tot, ft_tot
                if w.driven:
                    if fn_tot > 0.0: w.u += dt * slip_main
                    else: w.u = 0.0
                    if self.braked:                                              # spring brake: holds up to w.brake, then slips at that torque
                        if w.ang_ref is None: w.ang_ref = w.ang
                        tq = -KB * (w.ang - w.ang_ref) - CB * w.w
                        if tq > w.brake: tq = w.brake; w.ang_ref = w.ang + tq / KB
                        elif tq < -w.brake: tq = -w.brake; w.ang_ref = w.ang + tq / KB
                    else:
                        w.ang_ref = None
                        tq = max(-w.t_lim, min(w.t_lim, w.kv * (self.v_cmd / w.r - w.w)))
                    w.tq = tq
                    rr = w.crr * fn_tot * w.r * math.tanh(w.w / 0.2)
                    w.w += dt * (tq - ft_tot * w.r - rr) / w.i_w
                    w.ang += dt * w.w
                A = F[id(b)]
                A[0] += fx; A[1] += fz
                lx = w.x * c + w.z * s; lz = -w.x * s + w.z * c                 # lever arm from the CG in world axes
                A[2] += lz * fx - lx * fz                                        # moment about +y
                A[3] += w.y * fz
        if self.joint:
            a, pa, bb, pb, k, cc = self.joint
            ax, az, avx, avz = a.point(*pa); bx, bz, bvx, bvz = bb.point(*pb)
            fx = k * (bx - ax) + cc * (bvx - avx); fz = k * (bz - az) + cc * (bvz - avz)
            for body, p, sgn in ((a, pa, 1.0), (bb, pb, -1.0)):
                c, s = math.cos(body.th), math.sin(body.th)
                lx = p[0] * c + p[1] * s; lz = -p[0] * s + p[1] * c
                A = F[id(body)]; A[0] += sgn * fx; A[1] += sgn * fz; A[2] += sgn * (lz * fx - lx * fz)
            self.joint_force = (fx, fz)
        for b in self.b:
            A = F[id(b)]
            b.ax, b.az = A[0] / b.m, A[1] / b.m
            b.vx += dt * b.ax; b.vz += dt * b.az
            b.wth += dt * A[2] / b.iyy                                           # th = rotation about +y (nose-DOWN positive)
            b.wph += dt * A[3] / b.ixx
            b.x += dt * b.vx; b.z += dt * b.vz; b.th += dt * b.wth; b.ph += dt * b.wph
        self.t += dt

    def run(self, t_end, log_every=0.005, hook=None):
        n_log = max(1, int(round(log_every / self.dt))); i = 0
        while self.t < t_end:
            if hook: hook(self)
            self.step()
            if i % n_log == 0:
                self.log.append(self.snapshot())
            i += 1
        return self.log

    def snapshot(self):
        b0 = self.b[0]
        d = dict(t=self.t, x=b0.x, z=b0.z, th=b0.th, ph=b0.ph, vx=b0.vx, vz=b0.vz, ax=getattr(b0, 'ax', 0.0), az=getattr(b0, 'az', 0.0),
                 wth=b0.wth)
        for b in self.b:
            for w in b.wheels:
                d['fn_' + w.name] = w.fn
                if w.driven: d['tq_' + w.name] = w.tq; d['w_' + w.name] = w.w
        return d


def settle(sim, t=1.0):
    """Let the vehicle settle on its tyres with the brakes on."""
    sim.braked = True
    while sim.t < t: sim.step()
    sim.braked = False; sim.t = 0.0; sim.log = []
