#!/usr/bin/env python3
"""Offline replay of the lane watch (b2f_r6.R6Mixin): the three lidars are simulated at the poses of a recorded trip (trace.json) and
the lane-watch code runs on the scans, without the firmware. A whole trip takes a few minutes, and any moment can be looked at.

usage (inside the settings: source r61/env_r61_fast.sh first; X_LID_BAD, X_LID_FILTER, X_R6_PROUD ... as wanted):
  harness.py replay <run dir> [t0 t1]         looks with a confirmed object inside the stand-still zone, lane legs only
  harness.py dump <run dir> <t>               what the lane watch makes of the scan at time t
  harness.py walker <run dir> <t> <gap>       someone stands <gap> m from the far hedge, 2 to 9 m ahead of the robot as it was at time t:
                                              share of looks in which they are a confirmed object
"""
import sys, os, math, json, types, glob
import numpy as np
SCR = '/home/claude/b2f_run/sitl/b2f/scripts'; sys.path.insert(0, SCR); sys.path.insert(0, os.path.join(SCR, '..', 'scripts_base'))
import b2f_world as BW
BW.ROB['x1'] += float(os.environ.get('X_NOSE_DX', '0')); BW.ROB['vmax'] = float(os.environ.get('X_ROB_VMAX', BW.ROB['vmax']))
import b2f_r6 as R
from b2f_world import ROB


class Fake(R.R6Mixin):
    def __init__(self, seed=7):
        self.w = BW.World(0.0, 0.0, 0.0, seed=seed); self.S = self.w.S; self.map_segs = self.S.hedge; self.st = {'known': [], 'metrics': {}}
        self.sc = {'seed': seed}; self.scan = None; self.r = types.SimpleNamespace(raw_fix=6, seed=seed); self._pose = None
        self._rng = np.random.default_rng(7070 + seed); self._lb = {}; self.no_pause = False

    def pose(self): return self._pose
    def cam_people(self): return None

    def look(self, q):
        w = self.w; w.t = q['t']; w.x, w.y, w.yaw, w.v, w.w = q['x'], q['y'], q['yaw'], q['v'], q['w']
        self._pose = (q['ekf'][0], q['ekf'][1], q['eyaw']) if q.get('ekf') and q.get('eyaw') is not None else (q['x'], q['y'], q['yaw'])
        self.r.raw_fix = {'rtk': 6, 'wrongfix': 6, 'float': 5, 'none': 1}.get(q.get('rq'), q.get('fix', 6)); r = w.lidar()
        if R.LID_BAD:
            ox = w.x + ROB['lidar_x'] * math.cos(w.yaw); oy = w.y + ROB['lidar_x'] * math.sin(w.yaw)
            r = R.lid_degrade(w, ox, oy, w.yaw + np.radians(np.arange(360)), r, self._rng, self._lb)
        if R.LID_FILTER: r = self.lid_filter(r, 'F', ROB['lidar_x'], 0.0, np.radians(np.arange(360)), circ=True)
        self.scan = r
        return self.r6_objects()


def load(rd):
    f = glob.glob(os.path.join(rd, 'runs', '*', 'trace.json')) if not os.path.exists(os.path.join(rd, 'trace.json')) else [os.path.join(rd, 'trace.json')]
    return json.load(open(f[0]))['trace']


def lane_rows(tr, t0=None, t1=None):
    return [q for q in tr if q['state'].startswith('LANE') and 35.0 < q['s'] < 610.0 and (t0 is None or q['t'] >= t0) and (t1 is None or q['t'] <= t1)]


if __name__ == '__main__':
    mode, rd = sys.argv[1], sys.argv[2]; tr = load(rd); F = Fake()
    if mode == 'replay':
        t0 = float(sys.argv[3]) if len(sys.argv) > 3 else None; t1 = float(sys.argv[4]) if len(sys.argv) > 4 else None
        rows = lane_rows(tr, t0, t1); n = 0; hits = []; ev = []; far = 0
        for q in rows:
            objs = [o for o in F.look(q) if o['conf']]; n += 1
            near = [o for o in objs if o['d'] < R.NEAR]
            if any(o['d'] < 10.0 and o['x'] > ROB['x1'] for o in objs): far += 1
            if near:
                o = min(near, key=lambda o: o['d']); so, lo = F.S.lane.project(np.array(o['w'])); hits.append(q['t'])
                if not ev or q['t'] - ev[-1]['t1'] > 1.0: ev.append(dict(t=q['t'], t1=q['t'], s=round(float(q['s']), 1), v=round(q['v'], 2), obj_s=round(float(so), 1), obj_lat=round(float(lo), 2), n=o['n'], d=round(o['d'], 2), ext=round(o['ext'], 2)))
                else: ev[-1]['t1'] = q['t']
        dist = sum(abs(q['v']) * 0.12 for q in rows)
        print(json.dumps(dict(looks=n, metres=round(dist), looks_with_object_in_zone=len(hits), events=len(ev), looks_with_object_ahead_within_10m=far,
                              bad=os.environ.get('X_LID_BAD', ''), filter=R.LID_FILTER, proud=R.PROUD)))
        for e in ev[:40]: print('   ', e)
    elif mode == 'dump':
        t = float(sys.argv[3]); q = min(tr, key=lambda q: abs(q['t'] - t)); i = tr.index(q)
        for qq in tr[max(0, i - 12):i + 1]: objs = F.look(qq)
        hd = float(F.S.lane.heading(q['s'])); print('t %.2f s %.1f lat %.2f yaw-lane %.1f deg v %.2f fix %s' % (q['t'], q['s'], q['lat'], math.degrees((q['yaw'] - hd + math.pi) % (2 * math.pi) - math.pi), q['v'], q.get('fix')))
        for o in objs:
            so, lo = F.S.lane.project(np.array(o['w'])); print('   object n %d d %.2f ext %.2f conf %s at robot (%.2f, %.2f) = lane s %.1f lat %.2f moved %s walker %s' % (o['n'], o['d'], o['ext'], o['conf'], o['x'], o['y'], so, lo, o['moved'], o.get('walker')))
        print('   hedge returns %d' % len(F._r6_hedge))
    elif mode == 'walker':
        t = float(sys.argv[3]); gap = float(sys.argv[4]); q0 = min(tr, key=lambda q: abs(q['t'] - t)); i0 = tr.index(q0); S = F.S
        sgn = 1.0 if 'DOWN' in q0['state'] else -1.0; out = {}
        mids = [(S.lane.project(0.5 * (seg[:2] + seg[2:])), seg) for seg in S.hedge_truth]; mids = [(float(sl[0]), float(sl[1])) for sl, seg in mids]
        for ahead in (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0):
            # the far hedge is on the robot's right: its lateral position at that station, from the truth lines
            s_p = q0['s'] + sgn * (ahead + ROB['x1']); cand = [(abs(ss - s_p), ll) for ss, ll in mids if ll * (-sgn) > 0.5 and abs(ss - s_p) < 3.0]
            if not cand: continue
            best = min(cand)
            lat_p = best[1] - math.copysign(gap + 0.25, best[1]); px, py, _ = S.pose(s_p, lat_p, 0.0); F2 = Fake(); F2.w.movers_now = lambda px=px, py=py: [(px, py, 0.25, 'person')]
            seen = 0; n = 0; ct, st_ = math.cos(q0['yaw']), math.sin(q0['yaw'])      # where they are in the robot's own frame (true pose)
            bx = (px - q0['x']) * ct + (py - q0['y']) * st_; by = -(px - q0['x']) * st_ + (py - q0['y']) * ct
            for k in range(40):      # the robot stands; 40 looks
                qq = dict(q0); qq['t'] = q0['t'] + 0.12 * k; qq['v'] = 0.0; qq['w'] = 0.0
                objs = [o for o in F2.look(qq) if o['conf']]
                if k >= 5:
                    n += 1; seen += any(math.hypot(o['x'] - bx, o['y'] - by) < 0.6 for o in objs)
            out[ahead] = round(seen / max(1, n), 2)
        print(json.dumps(dict(t=q0['t'], s=round(q0['s'], 1), gap_from_hedge=gap, share_of_looks_seen_by_distance_ahead=out, bad=os.environ.get('X_LID_BAD', ''), filter=R.LID_FILTER, proud=R.PROUD)))
