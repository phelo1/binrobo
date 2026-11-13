#!/usr/bin/env python3
"""Writes my test variants of the other agent's lane-driving code. Their files are not edited:
  sitl/b2f/scripts/b2f_companion_x.py  = b2f_companion.py + three switchable fixes (all off -> identical behaviour)
  sitl/b2f/scripts/b2f_runner_x.py     = b2f_runner.py importing the module named in env X_COMP (default b2f_companion)

Switches (environment, default off):
  X_FIX_RCC=1  lane(): sign of the "only the right hedge face is visible and it is too close" correction (RC-C in the
               other agent's report: the frozen code steers TOWARD the right hedge).
  X_FIX_RCA=1  leaving a home spot far off the centre-line (> 2 m): drive a planned C1 path from the post-pivot pose to
               the lane centre-line at s 21 (checked against the map and the known bins), instead of holding the lateral
               offset and ramping it inside lane() (RC-A: the three-bin drop ran into the hedge end at s 25.7).
  X_FIX_APP=1  reverse approach to the pre-grab pose: use the smooth C1 path (which ends on the bin axis) for lateral offsets
               up to 0.40 x the distance instead of 0.15 x; beyond that the frozen pivot - line - pivot is kept. Reason: the
               second pivot is made at the pre-grab point, the tightest spot at pad A, and its overshoot is what brings the
               nose nearest the hedge (0.11-0.22 m in my runs).
  X_FIX_RAL=1  the re-alignment that follows a camera correction is driven as two smooth paths (forward 0.8 m, back onto the
               corrected axis) with no pivot before each leg; the pivots swing the nose toward the hedge at pad A.
  X_FIX_RCB=1  at the pre-grab pose, read the bin's lateral offset with the rear docking camera (the same sensor the frozen
               code already uses, noise-free, for the final reverse; here truth + Gaussian noise X_CAM_SIG, default 0.010 m).
               If it is more than X_CAM_TOL (default 0.025 m) off, correct the bin estimate and re-align, before the frozen
               truth gate (RC-B: the frozen retry re-used the same wrong estimate).
usage: make_companion_x.py <sitl/b2f/scripts dir>
"""
import sys, os
D = sys.argv[1]
s = open(os.path.join(D, 'b2f_companion.py')).read()

def rep(s, old, new, n=1):
    assert s.count(old) == n, (s.count(old), old[:80])
    return s.replace(old, new)

# ---- switches
s = rep(s, "GATE_LAT, GATE_YAW = 0.05, math.radians(3.0)",
        "GATE_LAT, GATE_YAW = 0.05, math.radians(3.0)\n"
        "FIX_RCA = os.environ.get('X_FIX_RCA') == '1'; FIX_RCB = os.environ.get('X_FIX_RCB') == '1'; FIX_RCC = os.environ.get('X_FIX_RCC') == '1'; FIX_APP = os.environ.get('X_FIX_APP') == '1'; FIX_RAL = os.environ.get('X_FIX_RAL') == '1'\n"
        "CAM_SIG = float(os.environ.get('X_CAM_SIG', '0.010')); CAM_TOL = float(os.environ.get('X_CAM_TOL', '0.025'))")
s = rep(s, "\nimport math, numpy as np\n", "\nimport os\nimport math, numpy as np\n")   # the frozen file does not import os

# ---- RC-C: sign
s = rep(s, "elif in_lane and not ramping and dR is not None and dR - hw < KL_GAP + 0.6: m_face = -(KL_GAP + 0.6 - (dR - hw))",
        "elif in_lane and not ramping and dR is not None and dR - hw < KL_GAP + 0.6: m_face = (1.0 if FIX_RCC else -1.0) * (KL_GAP + 0.6 - (dR - hw))")

# ---- RC-A: planned yard exit
s = rep(s, """    def op_lane(self, s_goal, lat_end=0.0, hold_lat_until=None):
        yield from self.lane(s_goal, lat_end, hold_lat_until)
""", """    def op_lane(self, s_goal, lat_end=0.0, hold_lat_until=None):
        if FIX_RCA and hold_lat_until is not None and not self.st['op'].get('yx'):
            yield from self.yard_exit(); self.st['op']['yx'] = True
        yield from self.lane(s_goal, lat_end, hold_lat_until)

    def yard_exit(self, s_entry=21.0, hold=1.0, lat_min=2.0):
        \"\"\"[variant X_FIX_RCA] planned exit from a home spot far off the centre-line: straight ahead `hold` m, then a C1 curve
        to the lane centre-line at s_entry with the lane heading there. Checked against the map and the known bins first;
        if the check fails the frozen behaviour (lateral ramp inside lane()) is used.\"\"\"
        x, y, yaw = self.pose(); s, l = self.S.lane.project(np.array([x, y]))
        if abs(l) < lat_min or s > s_entry - 3.0: return
        p0 = (x + hold * math.cos(yaw), y + hold * math.sin(yaw)); x1, y1, h1 = self.S.pose(s_entry, 0.0, 0.0)
        path = [[x, y]] + self.hermite(p0, yaw, (float(x1), float(y1)), float(h1))
        P = np.array(path); poses = []
        for i in range(0, len(P) - 1, 4):
            j = min(i + 4, len(P) - 1); poses.append((float(P[i][0]), float(P[i][1]), math.atan2(P[j][1] - P[i][1], P[j][0] - P[i][0])))
        c = self.sweep_clear(poses, True); Lp = float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1)))
        self.st['metrics'].setdefault('yard_exit', []).append(dict(from_s=round(float(s), 1), from_lat=round(float(l), 2), path_m=round(Lp, 1), sweep_m=round(c, 2), used=bool(c >= 0.30)))
        self.r.ev('pi', 'yard exit path %.1f m from lateral %.2f m, map / known-object clearance %.2f m%s' % (Lp, l, c, '' if c >= 0.30 else ' -> not used'))
        if c < 0.30: return
        self.st['state'] = 'YARD_EXIT' + ('_LOADED' if self.w.carry else '')
        yield from self.follow(path, v=V_MAN)
""")

# ---- approach: C1 path instead of pivot-line-pivot for moderate lateral offsets
s = rep(s, "if al > 1.0 and lt < 0.15 * al and abs(wrap(yaw - hyaw)) < math.radians(20):",
        "if al > 1.0 and lt < (0.40 if FIX_APP else 0.15) * al and abs(wrap(yaw - hyaw)) < math.radians(20):")

# ---- RC-B: rear-camera check at the pre-grab pose
s = rep(s, """        # C8 gate (truth) - the MuJoCo G1 start envelope
""", """        if FIX_RCB and not op.get('cam_done'):
            # [variant X_FIX_RCB] rear docking camera at the pre-grab pose: lateral offset of the bin axis (truth + noise CAM_SIG).
            # More than CAM_TOL off -> correct the bin estimate by the difference and re-align, before the frozen truth gate.
            if not hasattr(self, '_cam_rng'): self._cam_rng = np.random.default_rng(int(self.r.seed) * 7919 + 13)
            for k_ in range(2):
                thx_, thy_, thyaw_ = self.hold_pose(b['x'], b['y'], b['yaw'], b['size'])
                tpx_, tpy_ = thx_ + PREGRAB * math.cos(thyaw_), thy_ + PREGRAB * math.sin(thyaw_)
                lat_true = -(self.w.x - tpx_) * math.sin(thyaw_) + (self.w.y - tpy_) * math.cos(thyaw_)
                lat_cam = lat_true + float(self._cam_rng.normal(0.0, CAM_SIG))
                x, y, yaw = self.pose(); e_est = -(x - px) * math.sin(hyaw) + (y - py) * math.cos(hyaw)
                st['metrics'].setdefault('cam_checks', []).append(dict(bin=name, k=k_, lat_cam=round(lat_cam, 3), lat_true=round(lat_true, 3), e_est=round(e_est, 3)))
                if abs(lat_cam) <= CAM_TOL: break
                d_ = e_est - lat_cam
                exp = dict(exp); exp['x'] = exp['x'] - d_ * math.sin(hyaw); exp['y'] = exp['y'] + d_ * math.cos(hyaw); self.sc['expect_bins'][name] = exp
                hx, hy, hyaw = self.hold_pose(exp['x'], exp['y'], exp['yaw'], exp['size'])
                px, py = hx + PREGRAB * math.cos(hyaw), hy + PREGRAB * math.sin(hyaw)
                self.set_known(name, dict(x=exp['x'], y=exp['y'], yaw=exp['yaw'], L=BIN_T[exp['size']]['D'], W=BIN_T[exp['size']]['W']))
                self.r.ev('pi', 'rear camera: bin axis %.3f m off the estimate (camera %.3f m) -> estimate corrected, re-aligning' % (d_, lat_cam))
                ca, sa_ = math.cos(hyaw), math.sin(hyaw)
                if FIX_RAL:
                    x_, y_, yaw_ = self.pose()
                    yield from self.follow(self.hermite((x_, y_), yaw_, (px + 0.8 * ca, py + 0.8 * sa_), hyaw), reverse=False, v=V_MAN)
                    x_, y_, yaw_ = self.pose()
                    yield from self.follow(self.hermite((x_, y_), yaw_, (px, py), hyaw, reverse=True), reverse=True, v=V_REV)
                    yield from self.pivot(hyaw, tol=math.radians(0.8))
                else:
                    yield from self.goto_pose(px + 0.8 * ca, py + 0.8 * sa_, hyaw, reverse=False, v=V_MAN)
                    yield from self.goto_pose(px, py, hyaw, reverse=True, v=V_REV)
            op['cam_done'] = True
        # C8 gate (truth) - the MuJoCo G1 start envelope
""")
open(os.path.join(D, 'b2f_companion_x.py'), 'w').write(s)

r = open(os.path.join(D, 'b2f_runner.py')).read()
r = rep(r, "import b2f_companion as CP", "import importlib; CP = importlib.import_module(os.environ.get('X_COMP', 'b2f_companion'))\n"
        "INST = int(os.environ.get('X_INST', '0'))   # second SITL instance on shifted ports, so two campaigns can run side by side")
r = rep(r, "CK = os.path.join(ROOT, 'ckpt')", "CK = os.path.join(ROOT, 'ckpt' + os.environ.get('X_CK', ''))")
r = rep(r, "        port = 9002\n", "        port = 9002 + 10 * INST\n")
r = rep(r, "for p_ in (5760, 5762, 5763):", "for p_ in (5760 + 10 * INST, 5762 + 10 * INST, 5763 + 10 * INST):")
r = rep(r, "'-I0', '--sim-port-out'", "'-I%d' % INST, '--sim-port-out'")
r = rep(r, "mavutil.mavlink_connection('tcp:127.0.0.1:5760',", "mavutil.mavlink_connection('tcp:127.0.0.1:%d' % (5760 + 10 * INST),")
r = rep(r, "mavutil.mavlink_connection('tcp:127.0.0.1:5762',", "mavutil.mavlink_connection('tcp:127.0.0.1:%d' % (5762 + 10 * INST),")
open(os.path.join(D, 'b2f_runner_x.py'), 'w').write(r)
print('written b2f_companion_x.py, b2f_runner_x.py')
