#!/usr/bin/env python3
"""Revision 5, second pass on the driving software (switch X_R5B=1). Applied to b2f_companion_x.py (backup: b2f_companion_x_r5a.py).

Found in the first 60-mission run of revision 5 (results kept in sitl_out/r5a_prefix):
  1. s3a seed 7, third trip: 1 mm from the right hedge at the s 73-77 bend. Cause: MY camera model returned the outer hedge of the bend
     as "left edge", and MY fusion rule took the nearer of lidar and camera. The right-face guard in B2-F had the wrong sign, and
     mapped hedges are filtered out of the obstacle check, so nothing stopped the robot.
  2. s3a seed 23: the robot turned 134 deg on the spot during a 40 s wait at pad F, and 13 deg just before the set-down
     (stop command = "hold the heading you have NOW", sent every cycle).
  3. s3b seed 7: false "bin tipped" - 15 scans merged in world coordinates while the heading estimate wobbles.
Changes:
  a. stop command latches the heading of the first stop cycle
  b. lidar hedge faces: returns in the +-20 deg cone straight ahead are not side faces
  c. camera model: the left boundary only (a detector tracks the left edge as a connected line)
  d. lidar/camera disagreement: take the reading that fits the lane width with the right face, else the lidar's
  e. side guard with the right sign: 0.35 m to the right face, 0.20 m to the left face, centre when both are short
  f. pose-free protective field: ANY lidar return inside the robot's own path up to 0.5 m ahead of the nose -> stop, back out 0.8 m,
     start again from the lidar/camera edges; three trips in two minutes -> hold and alert
  g. bin outline check: extent per scan, median over the 15 scans
"""
import sys
P = '/home/claude/b2f_run/sitl/b2f/scripts/b2f_companion_x.py'
s = open(P).read()
if 'X_R5B' in s:
    print('already patched'); sys.exit(0)
n = 0
def rep(old, new, count=1):
    global s, n
    if s.count(old) < 1: raise SystemExit('NOT FOUND: ' + old[:90])
    if count == 1 and s.count(old) != 1: raise SystemExit('NOT UNIQUE (%d): %s' % (s.count(old), old[:90]))
    s = s.replace(old, new); n += 1

# --- switches
rep("NOFIX_NOW = os.environ.get('X_NOFIX_NOW') == '1'",
    "R5B = os.environ.get('X_R5B') == '1'                     # [revision 5, second pass] stop latch, bend-proof edges, side guard, protective field, per-scan bin outline\n"
    "PF_D = float(os.environ.get('X_PF_D', '0.50')); PF_W = float(os.environ.get('X_PF_W', '0.03'))   # protective field: depth ahead of the nose, margin each side (m)\n"
    "NOFIX_NOW = os.environ.get('X_NOFIX_NOW') == '1'")

# --- a. stop latch
rep("    def att(self, yaw_enu=None, speed=0.0, rate_enu=None):\n",
    "    def att(self, yaw_enu=None, speed=0.0, rate_enu=None, _stop=False):\n")
rep("        self.speed_cmd = speed; thr = float(np.clip(speed / 0.5, -1, 1))\n",
    "        if not _stop: self._stop_yaw = None\n"
    "        self.speed_cmd = speed; thr = float(np.clip(speed / 0.5, -1, 1))\n")
rep("    def stop_cmd(self):\n        if self.yaw is not None: self.att(self.yaw, 0.0)\n",
    "    def stop_cmd(self):\n"
    "        if self.yaw is None: return\n"
    "        if R5B:   # hold the heading the robot had when it stopped (\"the heading you have now\", re-sent every cycle, let it creep round)\n"
    "            if getattr(self, '_stop_yaw', None) is None: self._stop_yaw = self.yaw\n"
    "            self.att(self._stop_yaw, 0.0, _stop=True)\n"
    "        else: self.att(self.yaw, 0.0)\n")

# --- b. faces: no forward cone
rep("        m = (B[:, 0] > 0.0) & (B[:, 0] < 4.0)\n        Lp = B[m & (B[:, 1] > 0.35)",
    "        m = (B[:, 0] > 0.0) & (B[:, 0] < 4.0)\n"
    "        if R5B: m &= np.abs(np.arctan2(B[:, 1], B[:, 0] - ROB['lidar_x'])) > math.radians(20.0)   # a hedge crossing the path at a bend is not a side face\n"
    "        Lp = B[m & (B[:, 1] > 0.35)")

# --- c. camera: left boundary only
rep("        H = self.S.hedge_truth; P = np.concatenate([H[:, :2], H[:, 2:], 0.5 * (H[:, :2] + H[:, 2:])]); d = P - np.array([self.w.x, self.w.y])\n",
    "        H = self.S.hedge_truth; P = np.concatenate([H[:, :2], H[:, 2:], 0.5 * (H[:, :2] + H[:, 2:])])\n"
    "        if R5B:   # the detector follows the LEFT boundary as one connected line; it does not take the far hedge of a bend for it\n"
    "            if not hasattr(self, '_hside'): self._hside = np.array([1.0 if self.S.lane.project(q)[1] > 0 else -1.0 for q in P])\n"
    "            s_r, _l = self.S.lane.project(np.array([self.w.x, self.w.y]))\n"
    "            P = P[self._hside == (1.0 if math.cos(self.w.yaw - self.S.lane.heading(s_r)) > 0 else -1.0)]\n"
    "        d = P - np.array([self.w.x, self.w.y])\n")

# --- d. disagreement rule
rep("                    if abs(dL - cL) > 0.25: nv['disagree'] += 1; dL = min(dL, cL)\n",
    "                    if abs(dL - cL) > 0.25:\n"
    "                        nv['disagree'] += 1\n"
    "                        if R5B:   # take the reading that fits the lane width together with the right face; no right face -> the lidar's\n"
    "                            if dR is not None and abs(cL + dR - 2 * HL) < abs(dL + dR - 2 * HL): dL = cL; nv['dis_cam'] = nv.get('dis_cam', 0) + 1\n"
    "                        else: dL = min(dL, cL)\n")

# --- e. side guard
rep("            if in_lane and not ramping and both and m_face is not None:     # never closer than 0.35 m to the right face either\n",
    "            if R5B and in_lane and not ramping and m_face is not None and not degraded:\n"
    "                if dR is not None: m_face = max(m_face, 0.35 - (dR - hw))      # at least 0.35 m to the right face\n"
    "                if dL is not None: m_face = min(m_face, (dL - hw) - 0.20)      # never plan closer than 0.20 m to the left face\n"
    "                if both and (dL - hw) + (dR - hw) < 0.55: m_face = (dL - dR) / 2.0\n"
    "            elif in_lane and not ramping and both and m_face is not None:     # never closer than 0.35 m to the right face either\n")

# --- f. protective field: call in lane()
rep("            # heading = lane tangent (0.6 m preview) + lateral correction toward the target lateral (no chord corner-cutting:\n",
    "            if R5B and in_lane:\n"
    "                pg = self.prot_field()\n"
    "                if pg is not None:\n"
    "                    yield from self.prot_stop(pg); ltg_prev = None; continue\n"
    "            # heading = lane tangent (0.6 m preview) + lateral correction toward the target lateral (no chord corner-cutting:\n")
rep("    def no_fix_hold(self):\n",
    "    def prot_field(self):\n"
    "        \"\"\"[revision 5] pose-free protective field: ANY lidar return (hedge or not; the map is not used) inside the robot's own\n"
    "        path, from the nose to PF_D ahead, robot width + PF_W each side. Returns the gap ahead of the nose (m) or None.\"\"\"\n"
    "        if self.scan is None: return None\n"
    "        r = self.scan; ok = np.isfinite(r)\n"
    "        if not ok.any(): return None\n"
    "        ang = np.radians(np.arange(360))[ok]; bx = ROB['lidar_x'] + r[ok] * np.cos(ang); by = r[ok] * np.sin(ang)\n"
    "        m = (bx > ROB['x1'] - 0.02) & (bx < ROB['x1'] + PF_D) & (np.abs(by) < ROB['hw'] + PF_W)\n"
    "        return float(np.min(bx[m]) - ROB['x1']) if int(m.sum()) >= 2 else None\n"
    "    def prot_stop(self, gap):\n"
    "        \"\"\"stop, back out 0.8 m along the track just driven (rear lidar and rear camera watch the rear on the real robot; the rear\n"
    "        is not modelled here), forget the lateral offset and start again from the edges. Three trips in two minutes -> hold + alert.\"\"\"\n"
    "        st = self.st; t0 = self.w.t; self.no_pause = True\n"
    "        L_ = st['metrics'].setdefault('prot_stops', []); L_.append(dict(t=round(t0, 1), s=round(float(self.w.s_lat()[0]), 1), gap=round(gap, 2)))\n"
    "        self.r.ev('pi', 'protective field: return %.2f m ahead of the nose inside the robot\\'s own path -> stop, back out' % gap)\n"
    "        yield from self.rest(1.0)\n"
    "        if len([q for q in L_ if t0 - q['t'] < 120.0]) >= 3:\n"
    "            self.alert('protective field tripped 3 times in 2 minutes - holding in the lane'); self.finish('alert', 'path blocked')\n"
    "            while True: self.stop_cmd(); yield\n"
    "        y0 = self.yaw; t1 = self.w.t\n"
    "        while self.w.t - t1 < 8.0: self.att(y0, -0.10); yield\n"
    "        yield from self.rest(0.5)\n"
    "        st['lat_off'] = 0.0; st.pop('mf_prev', None); self.no_pause = False; st['nofix_t0'] = None\n"
    "\n"
    "    def no_fix_hold(self):\n")

# --- g. bin outline per scan
rep("        res.update(width_m=round(ext_perp, 2), depth_m=round(ext_al, 2))\n",
    "        if R5B:   # extent per scan, median over the scans: merging 15 scans in world coordinates smears the outline when the heading estimate wobbles\n"
    "            ex_ = []\n"
    "            for Wk in Ws:\n"
    "                if len(Wk) == 0: continue\n"
    "                nk = Wk[np.hypot(Wk[:, 0] - bx, Wk[:, 1] - by) < 1.0]\n"
    "                if len(nk) >= 4: dk = nk - np.array([bx, by]); ex_.append((float(np.ptp(-dk[:, 0] * s_ + dk[:, 1] * c)), float(np.ptp(dk[:, 0] * c + dk[:, 1] * s_))))\n"
    "            if ex_: res['merged_m'] = [round(ext_perp, 2), round(ext_al, 2)]; ext_perp = float(np.median([q[0] for q in ex_])); ext_al = float(np.median([q[1] for q in ex_]))\n"
    "        res.update(width_m=round(ext_perp, 2), depth_m=round(ext_al, 2))\n")

open(P, 'w').write(s)
print('patched, %d replacements' % n)

# NOTE (21 Nov, after the first patch): a pivot-rate cap was added by hand in the same pass:
#   PIVOT_RATE = X_PIVOT_RATE (0.20 rad/s); in pivot(): if R5B: rmax = min(rmax, PIVOT_RATE); pivot timeout 50 s instead of 30 s.
#   Then, after the first fault-injection tests (a forced 20 deg heading step swung the nose corner to 4 mm from the hedge before anything stopped it):
#   HDG_RATE = X_HDG_RATE (0.15 rad/s) limit on the heading command in lane(); protective field 0.60 m ahead (X_PF_D), 0.08 m each side (X_PF_W),
#   and reaching back beside the nose (from 0.15 m behind the lidar); X_FAULT fault injection (lid / cam / steer).
#   The file as run is in the evidence pack (model_switches/b2f_companion_x.py); this script documents the first step only.
#   Last (22:11): follow() turns to the path's first direction with a capped pivot before it moves (a heading step sent with the first
#   speed command had the firmware spin the robot at up to 0.9 rad/s).
#   22:18: pivot command profile (ramp up 0.1 rad/s^2, cruise X_PIVOT_RATE 0.13 (0.18 still overshot to 0.27), proportional run-out, heading hold from 2 deg) because the firmware
#   overshot a flat 0.2 rad/s command to 0.31 and snapped back at 0.36 at the end; final reverse onto the bin capped at V_REV (was 0.15 m/s).
#   23:30: people beside the path. Test r5b0_person*: a person standing 0.17 m from the robot's side was passed without a stop (outside B2-F's
#   0.20 m corridor, and partly hidden by the pose-free "hedge face" filter). Now, in the lane: the face filter only removes LONG lines of returns;
#   stop corridor = robot + X_STOP_W (0.50 m) each side, slow to 0.25 m/s within X_SLOW_W (0.80 m); the hold uses the same corridor.
#   23:40, after the 60 missions: test r5b0_person60 (the person of scenario s5a made to stand in the path for 60 s) showed that the lidar stop
#   logic inherited from B2-F does not see a person standing within 1.2 m of a hedge while the satellite fix is degraded (its map filter widens
#   to 1.2 m), and never stops for anyone more than 0.20 m from the robot's side: seed 23 passed the person at 0.16 m without slowing.
#   Added: cam_people() / ppl_gap() / hold_for_person(): the front camera's person detector (model; ASSUMED rates) slows the robot at 4 m and
#   stops it at 1.5 m for a person or dog within X_PPL_W (0.50 m) of its sides, independent of map and fix. It does nothing when no person or
#   dog is in the scenario, so the 57 missions without one were not re-run; s5a and the person tests were.
#   (A wider lidar corridor and a long-line face filter were tried first and did not cure it: b2f_companion_x_r5b_widecorridor_trial.py.)
