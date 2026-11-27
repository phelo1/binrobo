"""B2-F companion (Pi) for the ArduPilot Rover 4.6.2 SITL. Talks MAVLink to the firmware on SERIAL0 (tcp 5760).
Motion is commanded in GUIDED with SET_ATTITUDE_TARGET: heading + speed (lane legs, lines, reversing) or turn rate + speed
(pivots). ArduPilot's own heading / turn-rate / speed controllers drive the skid-steer wheels (SERVO1/SERVO3); firmware
failsafes (GCS heartbeat, polygon geofence, battery, EKF) act on their own.
Pi functions: lane following on the EKF pose with a lidar hedge-face corridor offset (keep-left, centring in narrowings),
path stop for unmapped objects, RTK float / no-fix policy with wheel-odometry dead reckoning, grab / lift / carry / set-down
/ release, bin verification by lidar, energy guard, weather no-go, [county] bye-law clock, geofence pre-check.
Restart-safe: all mission state is in self.st (pickled at chunk ends); each op re-plans from the current pose when resumed."""
import os
import math, numpy as np
from pymavlink import mavutil
from world import ll2xy, xy2ll, wrap
from scene import seg_dist
import b2f_world as BW
from b2f_world import ROB, BIN_T

MODES = {0: 'MANUAL', 4: 'HOLD', 15: 'GUIDED', 16: 'INITIALISING', 10: 'AUTO', 11: 'RTL', 12: 'SMART_RTL'}
HL = 3.6 / 2 + 0.25            # surveyed hedge line from the lane centre-line (map)
KL_GAP = float(os.environ.get('X_KL_GAP', '0.42'))   # keep-left: robot left side to the hedge face (B2-F lane fit 0.42; [revision 5] X_KL_GAP)
V_CRUISE, V_SLOW, V_MAN, V_REV, V_DOCK = 0.45, 0.3, 0.25, 0.20, 0.10   # cruise 0.45 command: speed-loop overshoot keeps the truth speed <= ~0.5
V_REV = float(os.environ.get('X_VREV', V_REV))          # [revision 5] every reverse move at this speed (0.10 asked: the rear has 25 mm of foam)
VLOOK = float(os.environ.get('X_VLOOK', '0'))            # [revision 5] the slope speed rule looks this far ahead (m)
BYELAW = os.environ.get('X_BYELAW') == '1'               # [revision 5] the bye-law as two windows, with the measured trip time
TRIP_MIN = float(os.environ.get('X_TRIP_MIN', '78'))     #   first estimate of a trip (min) until one has been measured
QUIET_END = float(os.environ.get('X_QUIET_END', str(22.5 * 60)))   #   drops must be home by this time of the evening (min; Brian's choice, not the bye-law)
PICK_FROM = float(os.environ.get('X_PICK_FROM', str(10 * 60)))     #   returns may start from this time on collection day (min)
PICK_CLOCK = os.environ.get('X_PICKUP_CLOCK')            #   test only: start the collection-day scenarios at this time 'HH:MM' instead of 18:00
NAV_CAM = os.environ.get('X_NAV_CAM') == '1'             # [revision 5] the front camera also measures the left edge of the lane (second source beside the lidar)
NAV_CAM_SIG = float(os.environ.get('X_NAV_CAM_SIG', '0.04')); NAV_CAM_MISS = float(os.environ.get('X_NAV_CAM_MISS', '0.10')); LID_FACE_OFF = os.environ.get('X_LID_FACE_OFF') == '1'   # stress: lidar gives no hedge faces
R5B = os.environ.get('X_R5B') == '1'                     # [revision 5, second pass] stop latch, bend-proof edges, side guard, protective field, per-scan bin outline
FAULTS = [dict(kind=q.split(':')[0], s=float(q.split(':')[1]), dur=float(q.split(':')[2]), val=float(q.split(':')[3]), t0=None) for q in os.environ.get('X_FAULT', '').split(',') if q]
#   X_FAULT='<kind>:<station m>:<seconds>:<value>,...'  fault injection for tests, started when the robot first passes the station going down:
#     lid   = the lidar's left-face reading is wrong by <value> m;  cam = the camera's left-edge reading is stuck at <value> m;
#     steer = the steering correction is forced to <value> m (+ = to the robot's left) after every guard
PIVOT_RATE = float(os.environ.get('X_PIVOT_RATE', '0.13'))   # rad/s cap on pivot turns (second pass)
CAM_PEOPLE = os.environ.get('X_CAM_PEOPLE', '1') == '1'; PPL_W = float(os.environ.get('X_PPL_W', '0.50'))   # second pass: the front camera's person detector stops the robot for a person or dog within PPL_W of its sides, whatever the map and the satellite fix say
PPL_PAUSE = os.environ.get('X_PPL_PAUSE') == '1'   # [22 Nov, Brian: "have software pause robot when kids nearby or anyone"] pause whenever the front camera has a person or animal within PPL_PAUSE_R
PPL_PAUSE_R = float(os.environ.get('X_PPL_PAUSE_R', '5.0')); PPL_PAUSE_MAX = float(os.environ.get('X_PPL_PAUSE_MAX', '900'))   # m from the camera; s before it gives up and holds
PPL_P = os.environ.get('X_PPL_P')   # detection probability per frame (default 0.85 by day, 0.60 at night)
HDG_RATE = float(os.environ.get('X_HDG_RATE', '0.15'))   # rad/s: how fast the heading command may change in the lane (second pass). A 20 deg step swung the nose corner 0.4 m sideways in 0.7 s.
PF_D = float(os.environ.get('X_PF_D', '0.60')); PF_W = float(os.environ.get('X_PF_W', '0.08'))   # protective field: depth ahead of the nose, margin each side (m)
NOFIX_NOW = os.environ.get('X_NOFIX_NOW') == '1'         # [revision 5] a fence trip during a no-fix hold is reported as the no-fix hold it is
TRIP_WH = float(os.environ.get('X_TRIP_WH', '50.0'))   # C6 per-trip budget (energy guard plans with it); X_TRIP_WH raises it for a heavier robot (their value: 50.0)
RESERVE = 0.10                 # never plan below 10 % of usable energy
T_LIFT, T_SETDOWN, T_UNDOCK, T_DOCK, T_PHOTO = 33.0, 26.0, 10.0, 35.0, 5.0
_ls = float(os.environ.get('X_LIFT_SCALE', '1')); T_LIFT *= _ls; T_SETDOWN *= _ls   # longer lift travel: lift and set-down times scaled (1.4 for 350 mm against 250 mm)
PREGRAB = 1.2                  # MuJoCo G1 start: 1.2 m out on the bin axis
GATE_LAT, GATE_YAW = 0.05, math.radians(3.0)
FIX_RCA = os.environ.get('X_FIX_RCA') == '1'; FIX_RCB = os.environ.get('X_FIX_RCB') == '1'; FIX_RCC = os.environ.get('X_FIX_RCC') == '1'; FIX_APP = os.environ.get('X_FIX_APP') == '1'; FIX_RAL = os.environ.get('X_FIX_RAL') == '1'
CAM_SIG = float(os.environ.get('X_CAM_SIG', '0.010')); CAM_TOL = float(os.environ.get('X_CAM_TOL', '0.025'))
# added 14 Nov after the review of revision 2 (all OFF by default = the behaviour of every earlier run):
#   X_CAM_RNG=1      camera error drawn independently for every check, seeded by (run seed, number of checks so far): survives a checkpoint resume
#   X_CAM_REFUSE=1   up to X_CAM_TRIES re-alignments (default 3); if the camera still reads more than X_CAM_TOL off, or cannot see the bin, refuse the grab
#   X_FIX_RTH=1      after any refused grab drive home and dock instead of stopping where the robot stands
#   X_CAM_BIAS=<m>, X_CAM_MISS=<p>   stress only: constant camera offset; probability that a check returns no reading
CAM_RNG = os.environ.get('X_CAM_RNG') == '1'; CAM_REFUSE = os.environ.get('X_CAM_REFUSE') == '1'; CAM_TRIES = int(os.environ.get('X_CAM_TRIES', '3')); FIX_RTH = os.environ.get('X_FIX_RTH') == '1'
CAM_BIAS = float(os.environ.get('X_CAM_BIAS', '0')); CAM_MISS = float(os.environ.get('X_CAM_MISS', '0'))
# revision 4 switches (20 Nov 2026, after the re-test of revision 3), all OFF by default (then the code behaves as the revision 3 copy):
#   X_CAM_AVG=<n>    each camera check averages n frames (default 1); it has "no reading" only when every frame is missing
#   X_CAM_GAIN=<g>   fraction of the camera reading applied as a correction of the bin estimate (default 1.0)
#   X_GATE_CAM=1     the pre-grab gate DECIDES on a camera reading, as a real robot must (default: on ground truth). Truth is still logged
#                    (lat_m, yaw_deg, ok) so the frozen scorer can tell when a grab was made outside the true envelope. X_GATE_CAM_TOL: decision band (0.035 m)
#   X_FINAL_CAM=1    the final reverse steers on the camera reading of the bin axis (truth + X_CAM_BIAS + one error draw), not on the true bin pose
#   X_SEAT=<m>       seating check at the dock, before the lift: the two leg-tip gap sensors give the bin's sideways offset between the legs
#                    (truth + noise X_SEAT_SIG, default 5 mm; independent of the camera). Over the limit: pull out, line up again with the camera
#                    reading corrected by the sensor value, dock again. Still over the limit: no lift, refuse, drive home.
#   X_VSLOPE="g:v_bin:v_empty,..."  speed limit on a downhill slope steeper than g (0.08 = 8 %): the person-stop rule. X_VMAX: cruise command cap
CAM_AVG = int(os.environ.get('X_CAM_AVG', '1')); CAM_GAIN = float(os.environ.get('X_CAM_GAIN', '1.0')); GATE_CAM = os.environ.get('X_GATE_CAM') == '1'; GATE_CAM_TOL = float(os.environ.get('X_GATE_CAM_TOL', '0.035'))
FINAL_CAM = os.environ.get('X_FINAL_CAM') == '1'; SEAT = float(os.environ.get('X_SEAT', '0')); SEAT_SIG = float(os.environ.get('X_SEAT_SIG', '0.005'))
VSLOPE = sorted(tuple(float(v) for v in t.split(':')) for t in os.environ.get('X_VSLOPE', '').split(',') if t); VMAX = float(os.environ.get('X_VMAX', '9'))
def cam_frames(rng_, n):
    """mean error of the frames that gave a reading, and whether any did (same draws as the single-frame code when n = 1)"""
    fr_ = [(float(rng_.normal(0.0, CAM_SIG)), not (CAM_MISS > 0 and float(rng_.random()) < CAM_MISS)) for _k in range(max(1, n))]
    ok_ = [e for e, s2 in fr_ if s2]
    return (float(np.mean(ok_)) if ok_ else fr_[0][0]), len(ok_) > 0


def clock_fmt(m):
    d = int(math.floor(m / 1440.0)); mm = m - 1440 * d
    return 'D%s %02d:%02d' % (('%+d' % d) if d else '0', int(mm // 60), int(mm % 60))


class Companion:
    def __init__(self, runner, sc, st=None):
        self.r = runner; self.w = runner.w; self.sc = sc; self.S = self.w.S; self.L = self.S.L
        self.mode = '?'; self.armed = False; self.ekf_xy = None; self.yaw = None; self.gfix = 0; self.fence_breach = 0
        self.pause_req = False; self.paused = False; self.booted = False; self.gen = None; self.bootgen = None
        self.speed_cmd = 0.0; self.hb_t = -9.0; self.hc_now = None; self.lat_tgt = None; self.scan = None; self.upl = None
        self._rest_t = None; self.no_pause = False; self.last_stat = {}; self.ap_gs = None; self.ap_thr = None; self.ekf_v = None; self.corr_v = (0.0, 0.0); self.ekf_gps = False; self.ekf_fs = False; self._reguided = -9.0; self.dLR = (None, None)
        H = self.S.hedge; self.map_segs = H
        if st is None:
            st = dict(plan=list(sc['plan']), i=0, op={}, opname='', state='BOOT', result='running', outcome='', alerts=[], crashed=False,
                      metrics=dict(placements=[], grabs=[], trips=[], stops=[], gates=[]), clock0=sc.get('clock_min'), first_motion=None,
                      dr=None, dr_m=0.0, dr_active=False, lat_off=0.0, narrow_until=-1e9, known=[], hold_since=None, crash=None,
                      estop=None, trip=None, nogps_since=None, last_dock=None)
        self.st = st
        if st.get('known_init') is None:
            st['known_init'] = True
            for k, b in sc['expect_bins'].items():
                if self.w.carry == k: continue
                st['known'].append([k, dict(x=b['x'], y=b['y'], yaw=b['yaw'], L=BIN_T[b['size']]['D'], W=BIN_T[b['size']]['W'])])
            st['known'].append(['dock', self.dock_box()])
        self.chunk_t0 = self.w.t

    def state_for_ckpt(self): return self.st

    # ------------------------------------------------------------ MAVLink in
    def on_msg(self, m):
        t = m.get_type()
        if t == 'HEARTBEAT' and m.get_srcSystem() == 1 and m.type != mavutil.mavlink.MAV_TYPE_GCS:
            nm = MODES.get(m.custom_mode, str(m.custom_mode))
            if nm != self.mode and self.booted: self.r.ev('fw', 'mode %s -> %s' % (self.mode, nm))
            self.mode = nm; self.armed = bool(m.base_mode & 128)
        elif t == 'GLOBAL_POSITION_INT':
            if m.lat != 0: self.ekf_xy = list(ll2xy(m.lat / 1e7, m.lon / 1e7)); self.ekf_v = math.hypot(m.vx, m.vy) / 100.0
        elif t == 'ATTITUDE': self.yaw = wrap(math.pi / 2 - m.yaw)
        elif t == 'GPS_RAW_INT': self.gfix = m.fix_type
        elif t == 'VFR_HUD': self.ap_gs = m.groundspeed; self.ap_thr = m.throttle
        elif t in ('MISSION_REQUEST', 'MISSION_REQUEST_INT') and self.upl is not None and getattr(m, 'mission_type', 0) == 1: self.send_fence_item(m.seq)
        elif t == 'MISSION_ACK' and self.upl is not None and getattr(m, 'mission_type', 0) == 1: self.upl['ack'] = m.type
        elif t == 'STATUSTEXT':
            if 'is using GPS' in m.text: self.ekf_gps = True
            if 'EKF failsafe cleared' in m.text: self.ekf_fs = False
            elif 'EKF failsafe' in m.text: self.ekf_fs = True
        elif t == 'FENCE_STATUS':
            if m.breach_status and not self.fence_breach: self.r.ev('fw', 'FENCE BREACH reported by the firmware (type %d)' % m.breach_type)
            self.fence_breach = m.breach_status

    @property
    def mav(self): return self.r.gcs.mav

    # ------------------------------------------------------------ MAVLink out
    def set_mode(self, num): self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 1, num, 0, 0, 0, 0, 0)
    def arm(self): self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    def att(self, yaw_enu=None, speed=0.0, rate_enu=None, _stop=False):
        """GUIDED: heading (ENU rad) + speed (m/s, negative = reverse), or turn rate (ENU rad/s, CCW +) + speed."""
        if not _stop: self._stop_yaw = None
        self.speed_cmd = speed; thr = float(np.clip(speed / 0.5, -1, 1))
        if rate_enu is None:
            yn = wrap(math.pi / 2 - yaw_enu); q = [math.cos(yn / 2), 0.0, 0.0, math.sin(yn / 2)]
            self.mav.set_attitude_target_send(0, 1, 1, 0b00000111, q, 0, 0, 0, thr)
        else:
            self.mav.set_attitude_target_send(0, 1, 1, 0b10000011, [1, 0, 0, 0], 0, 0, -float(rate_enu), thr)
    def stop_cmd(self):
        if self.yaw is None: return
        if R5B:   # hold the heading the robot had when it stopped ("the heading you have now", re-sent every cycle, let it creep round)
            if getattr(self, '_stop_yaw', None) is None: self._stop_yaw = self.yaw
            self.att(self._stop_yaw, 0.0, _stop=True)
        else: self.att(self.yaw, 0.0)
    def servo(self, ch, pwm): self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, ch, pwm, 0, 0, 0, 0, 0)

    # ------------------------------------------------------------ fence (inclusion polygon of private ground for the AXLE)
    def fence_polygon(self):
        S = self.S; L = S.L; left = []; right = []
        def half(s):
            if s < 25.0: return 5.6
            if s >= S.lane.mouth[0]: return 4.2
            return 2.6           # axle fence in the lane (hedges are the physical limit; DP simplification eats ~0.2-0.3 m)
        def okp(p): return S.road_dist(p) >= S.boundary + 1.6       # axle 1.6 m inside the private boundary (nose 1.11 m + stop 0.3 m + 0.2)
        ss = list(np.arange(-4.0, 25.0, 3.0)) + [24.9, 25.1] + list(np.arange(30.0, S.lane.mouth[0], 6.0)) + [S.lane.mouth[0] - 0.1, S.lane.mouth[0] + 0.1]
        ss += list(np.arange(S.lane.mouth[0] + 1.0, L + 6.0, 1.0))
        for s in ss:
            for side, arr in ((1, left), (-1, right)):
                p = S.lane.point(s, side * (half(s) - (0.4 if 25.0 <= s < S.lane.mouth[0] else 0.0) * 0))
                if okp(p): arr.append(p)
                else:
                    for f in np.linspace(1.0, 0.0, 21):     # shrink toward the centre-line until on private ground
                        q = S.lane.point(s, side * half(s) * f)
                        if okp(q): arr.append(q); break
        P = np.array(left + right[::-1])
        # Rover 4.6 SITL stores at most 84 fence items: Douglas-Peucker on each side, tolerance raised until it fits
        def dp(Q, tol):
            if len(Q) < 3: return Q
            a, b = Q[0], Q[-1]; ab = b - a; n = np.linalg.norm(ab) + 1e-9
            d = np.abs(ab[0] * (Q[:, 1] - a[1]) - ab[1] * (Q[:, 0] - a[0])) / n; i = int(np.argmax(d))
            if d[i] <= tol: return np.array([a, b])
            return np.r_[dp(Q[:i + 1], tol)[:-1], dp(Q[i:], tol)]
        Lp = np.array(left); Rp = np.array(right[::-1])
        for tol in (0.05, 0.08, 0.12, 0.16, 0.2, 0.25, 0.3, 0.4):
            out = np.r_[dp(Lp, tol), dp(Rp, tol)]
            if len(out) <= 82: break
        self.fence_tol = tol
        return [list(map(float, q)) for q in out]

    def upload_fence(self):
        pts = self.fence_polygon(); self.fence_pts = pts
        self.upl = dict(items=pts, ack=None)
        self.mav.mission_count_send(1, 1, len(pts), 1)

    def send_fence_item(self, seq):
        p = self.upl['items'][seq]; lat, lon = xy2ll(*p)
        self.mav.mission_item_int_send(1, 1, seq, mavutil.mavlink.MAV_FRAME_GLOBAL, 5001, 0, 1, len(self.upl['items']), 0, 0, 0,
                                       int(lat * 1e7), int(lon * 1e7), 0, 1)

    # ------------------------------------------------------------ Pi sensors / estimates
    def on_scan(self, r): self.scan = r
    def pose(self):
        if self.ekf_xy is None or self.yaw is None: return None
        return self.ekf_xy[0], self.ekf_xy[1], self.yaw
    def s_lat(self):
        p = self.pose(); return self.S.lane.project(np.array(p[:2]))
    def odometry(self, dt):
        """wheel encoders (scale error ~1 %, noise) + firmware yaw -> Pi odometry pose (st['dr'])."""
        st = self.st
        if self.yaw is None or st['dr'] is None: return
        # Pi heading for odometry = its own IMU (BNO085-class, gyro-integrated, ASSUMED drift random walk 0.05 deg/sqrt(s)),
        # NOT the firmware EKF yaw: feeding EKF-yaw odometry back as GPS_INPUT made the EKF yaw unobservable (-12 deg drift, dev s1a)
        st['pi_herr'] = st.get('pi_herr', 0.0) + float(self.w.rng.normal(0, math.radians(0.05) * math.sqrt(dt)))
        hyaw = self.w.yaw + st['pi_herr']
        v = self.w.v * self.w.odo_k + float(self.w.rng.normal(0, 0.005))
        st['dr'][0] += v * math.cos(hyaw) * dt; st['dr'][1] += v * math.sin(hyaw) * dt
        if self.r.raw_fix == 1: st['dr_m'] += abs(v) * dt
    def gnss_fuse(self, fix, x, y, dt=0.2):
        """Pi GNSS gate (as G6 LaneFusion, simplified): the odometry pose is pulled to RTK-fixed fixes quickly (tau 0.5 s), to
        Float fixes slowly (tau 30 s - Float jumps of 0.5-1.5 m under canopy must not reach the EKF as a step), and runs on
        odometry alone with no fix (limit 25 m with hedge faces, 8 m without). Returns what is sent as GPS_INPUT."""
        st = self.st; self.corr_v = (0.0, 0.0)
        if st['dr'] is None: st['dr'] = [x, y]
        if fix == 6:
            # pull to the RTK fix; the correction speed is limited to 0.15 m/s so a re-fix after a Float episode is not a step
            # (a 1 m step made the EKF ground speed wrong for ~5 s and the speed loop ran the robot at 0.72 m/s)
            d = np.array([x - st['dr'][0], y - st['dr'][1]]); k = min(1.0, dt / 0.5); step = d * k; n = float(np.linalg.norm(step))
            if n > 0.15 * dt: step *= 0.15 * dt / n
            st['dr'][0] += float(step[0]); st['dr'][1] += float(step[1]); self.corr_v = (float(step[0]) / dt, float(step[1]) / dt)
            if st['dr_active']: self.r.ev('pi', 'GNSS fix back after %.1f m dead reckoning' % st['dr_m']); st['dr_active'] = False
            st['dr_m'] = 0.0; return st['dr'][0], st['dr'][1], 6, 0.05
        if fix == 5:
            k = dt / 30.0; c0 = (x - st['dr'][0]) * k; c1 = (y - st['dr'][1]) * k; st['dr'][0] += c0; st['dr'][1] += c1; self.corr_v = (c0 / dt, c1 / dt)
            if st['dr_active']: st['dr_active'] = False
            st['dr_m'] = 0.0; return st['dr'][0], st['dr'][1], 6, 0.05      # the Pi forwards ONE smooth pose (G6 practice)
        if not st['dr_active']: st['dr_active'] = True; self.r.ev('pi', 'GNSS no fix -> wheel-odometry dead reckoning')
        if self.dr_ok(): return st['dr'][0], st['dr'][1], 6, 0.05
        return None
    def dr_ok(self):
        st = self.st
        if st['dr'] is None or st['crashed']: return False
        lim = 25.0 if self.faces_valid() else 8.0
        return st['dr_m'] <= lim
    def dr_xy(self): return tuple(self.st['dr'])

    def scan_pts(self):
        """scan -> world points (EKF pose), with the Pi map filter: returns on/behind the surveyed hedge lines removed."""
        p = self.pose()
        if p is None or self.scan is None: return np.zeros((0, 2)), np.zeros((0, 2))
        x, y, yaw = p; r = self.scan; ok = np.isfinite(r)
        if not ok.any(): return np.zeros((0, 2)), np.zeros((0, 2))
        ox = x + ROB['lidar_x'] * math.cos(yaw); oy = y + ROB['lidar_x'] * math.sin(yaw); ang = yaw + np.radians(np.arange(360))[ok]
        W = np.c_[ox + r[ok] * np.cos(ang), oy + r[ok] * np.sin(ang)]
        c, s = math.cos(yaw), math.sin(yaw); d = W - np.array([x, y]); B = np.c_[d[:, 0] * c + d[:, 1] * s, -d[:, 0] * s + d[:, 1] * c]
        return W, B

    def faces(self):
        """hedge faces from the lidar in the robot frame: (dL, dR) lateral distances (robot frame y) of the near faces ahead."""
        W, B = self.scan_pts()
        if len(B) == 0: return None, None
        m = (B[:, 0] > 0.0) & (B[:, 0] < 4.0)
        if R5B: m &= np.abs(np.arctan2(B[:, 1], B[:, 0] - ROB['lidar_x'])) > math.radians(20.0)   # a hedge crossing the path at a bend is not a side face
        Lp = B[m & (B[:, 1] > 0.35) & (B[:, 1] < 3.2), 1]; Rp = -B[m & (B[:, 1] < -0.35) & (B[:, 1] > (-4.5 if R5B else -3.2)), 1]   # second pass: the far (right) face is 3.2 m away when keeping left - look to 4.5 m so it is not lost
        dL = float(np.percentile(Lp, 15)) if len(Lp) >= 8 else None; dR = float(np.percentile(Rp, 15)) if len(Rp) >= 8 else None
        return dL, dR
    def cam_left(self):
        """[revision 5] front camera: sideways distance to the left edge of the lane 0.5 to 5 m ahead (model: the true hedge line seen from the
        true pose, plus noise; some frames give nothing). Independent of the lidar."""
        if not hasattr(self, '_navrng'): self._navrng = np.random.default_rng(4242 + int(self.sc.get('seed', 0) or 0))
        if self._navrng.random() < NAV_CAM_MISS: return None
        H = self.S.hedge_truth; P = np.concatenate([H[:, :2], H[:, 2:], 0.5 * (H[:, :2] + H[:, 2:])])
        if R5B:   # the detector follows the LEFT boundary as one connected line; it does not take the far hedge of a bend for it
            if not hasattr(self, '_hside'): self._hside = np.array([1.0 if self.S.lane.project(q)[1] > 0 else -1.0 for q in P])
            s_r, _l = self.S.lane.project(np.array([self.w.x, self.w.y]))
            P = P[self._hside == (1.0 if math.cos(self.w.yaw - self.S.lane.heading(s_r)) > 0 else -1.0)]
        d = P - np.array([self.w.x, self.w.y])
        P = d[np.linalg.norm(d, axis=1) < 7.0]
        if len(P) == 0: return None
        c_, s_ = math.cos(self.w.yaw), math.sin(self.w.yaw); bx = P[:, 0] * c_ + P[:, 1] * s_; by = -P[:, 0] * s_ + P[:, 1] * c_
        Lp = by[(bx > 0.5) & (bx < 5.0) & (by > 0.35) & (by < 3.2)]
        return float(np.percentile(Lp, 15) + self._navrng.normal(0.0, NAV_CAM_SIG)) if len(Lp) >= 3 else None
    def cam_people(self):
        """[revision 5] front camera person detector (model): a person or dog within 6 m and +-55 deg of straight ahead is found in a frame with
        probability 0.85 by day, 0.60 at night under infra-red (ASSUMED); 5 frames a second; two detections in a row confirm; a confirmed track is
        kept for 1 s after its last detection. Position = truth + 50 mm noise. Independent of the map, the hedge-face fit and the satellite fix.
        Returns [(m ahead of the axle, m to the left, radius, kind)] for the confirmed tracks."""
        st = self.st; T = st.setdefault('cam_trk', {}); now = self.w.t
        if now - st.get('cam_ppl_t', -9.0) >= 0.2 - 1e-6:
            st['cam_ppl_t'] = now
            if not hasattr(self, '_pplrng'): self._pplrng = np.random.default_rng(977 + int(self.sc.get('seed', 0) or 0))
            p_ = float(PPL_P) if PPL_P else (0.60 if getattr(self.w, 'night', False) else 0.85)
            c_, s_ = math.cos(self.w.yaw), math.sin(self.w.yaw)
            for x_, y_, r_, kind in self.w.movers_now():
                dx, dy = x_ - self.w.x, y_ - self.w.y; bx = dx * c_ + dy * s_; by = -dx * s_ + dy * c_; tr = T.setdefault(kind, dict(n=0, last=-9.0, until=-9.0))
                if math.hypot(bx - 1.04, by) < 6.0 and abs(math.atan2(by, bx - 1.04)) < math.radians(55.0) and self._pplrng.random() < p_:
                    tr['n'] = tr['n'] + 1 if now - tr['last'] < 0.25 else 1; tr['last'] = now
                    tr['pos'] = (bx + float(self._pplrng.normal(0, 0.05)), by + float(self._pplrng.normal(0, 0.05)), r_, kind)
                    if tr['n'] >= 2: tr['until'] = now + 1.0
        return [tr['pos'] for tr in T.values() if tr.get('until', -9.0) > now and 'pos' in tr]
    def ppl_gap(self):
        """nearest confirmed person / dog inside the robot's width + PPL_W each side: gap ahead of the nose (m), or None."""
        g_ = None
        for bx_, by_, r_, k_ in self.cam_people():
            q_ = bx_ - r_ - ROB['x1']
            if abs(by_) - r_ < ROB['hw'] + PPL_W and -0.5 < q_ < 6.0: g_ = q_ if g_ is None else min(g_, q_)
        return g_
    def ppl_near(self):
        """distance (m, from the front camera) to the nearest confirmed person or animal in its view, or None."""
        r_ = None
        for bx_, by_, rr_, k_ in self.cam_people():
            q_ = math.hypot(bx_ - 1.04, by_) - rr_; r_ = q_ if r_ is None else min(r_, q_)
        return r_
    def pause_for_people(self, rng):
        """[22 Nov] someone is near: stop and wait. Carry on when the camera has seen nobody within PPL_PAUSE_R + 0.5 m for 3 s. Tell the owner
        after 2 minutes (and keep waiting); give up and hold after PPL_PAUSE_MAX."""
        st = self.st; t0 = self.w.t; clear = None; told = False; np0 = self.no_pause; self.no_pause = True
        rec_ = dict(t=round(t0, 1), range=round(rng, 2), s=round(float(self.w.s_lat()[0]), 1)); st['metrics'].setdefault('ppl_pauses', []).append(rec_)
        self.r.ev('pi', 'camera: person or animal %.1f m away -> pause' % rng)
        while True:
            self.stop_cmd(); yield
            q_ = self.ppl_near()
            if q_ is None or q_ > PPL_PAUSE_R + 0.5: clear = clear or self.w.t
            else: clear = None
            if clear and self.w.t - clear > 3.0: self.r.ev('pi', 'camera: nobody near for 3 s -> carry on'); break
            if not told and self.w.t - t0 > 120.0: told = True; self.alert('waiting: someone has been near the robot for 2 minutes (it carries on by itself when they have gone)')
            if self.w.t - t0 > PPL_PAUSE_MAX:
                self.alert('someone has been near the robot for %d minutes - holding' % round(PPL_PAUSE_MAX / 60.0)); self.finish('alert', 'path blocked')
                while True: self.stop_cmd(); yield
        rec_['wait_s'] = round(self.w.t - t0, 1); self.no_pause = np0; self.st['nofix_t0'] = None
    def hold_for_person(self, gap):
        """stop for a person or dog the camera has found; wait until the camera has seen nobody in the way for 3 s; alert after 120 s."""
        st = self.st; t0 = self.w.t; clear = None; self.no_pause = True
        st['metrics'].setdefault('cam_stops', []).append(dict(t=round(t0, 1), gap=round(gap, 2), s=round(float(self.w.s_lat()[0]), 1)))
        self.r.ev('pi', 'camera: person or animal %.2f m ahead, within %.1f m of the robot\'s side -> stop' % (gap, PPL_W))
        while True:
            self.stop_cmd(); yield
            g_ = self.ppl_gap()
            if g_ is None or g_ > 3.0: clear = clear or self.w.t
            else: clear = None
            if clear and self.w.t - clear > 3.0: self.r.ev('pi', 'camera: nobody in the way for 3 s -> resume'); break
            if self.w.t - t0 > 120.0:
                self.alert('path blocked for 120 s (camera: person or animal %.1f m ahead)' % (g_ or 0)); self.finish('alert', 'path blocked')
                while True: self.stop_cmd(); yield
        self.no_pause = False; self.st['nofix_t0'] = None
    def faces_valid(self):
        dL, dR = self.faces(); return dL is not None or dR is not None

    def known_boxes(self):
        out = []
        for k, b in self.st['known']: out.append(b)
        return out
    def obstacle_ahead(self, reverse=False, look=5.0, extra_w=0.20):
        """unmapped returns in the straight corridor ahead (forward travel only - the rear is blind): (gap m, is_hedge_like).
        Filters: surveyed hedge lines (map, EKF pose; radius grows with a degraded fix), the lidar-fitted hedge faces (robot frame,
        pose-free), known objects (placed / target bins, dock). A long return line beside the corridor = hedge face, not an object."""
        if reverse: return None, False
        W, B = self.scan_pts()
        if len(B) == 0: return None, False
        nose = ROB['x1']
        m = (B[:, 0] > nose - 0.05) & (B[:, 0] < nose + look) & (np.abs(B[:, 1]) < ROB['hw'] + extra_w)
        if not m.any(): return None, False
        Wm = W[m]; Bm = B[m]
        H = self.map_segs; mid = 0.5 * (H[:, :2] + H[:, 2:]); p = self.pose()
        Hn = H[np.linalg.norm(mid - np.array(p[:2]), axis=1) < look + 6]
        rad = 0.40 if self.r.raw_fix == 6 else 1.2
        keep = np.ones(len(Wm), bool)
        if len(Hn): keep &= np.min(seg_dist(Wm[:, None, :], Hn[None, :, :2], Hn[None, :, 2:]), axis=1) > rad
        dL, dR = self.faces()
        if dL is not None: keep &= np.abs(Bm[:, 1] - dL) > 0.25
        if dR is not None: keep &= np.abs(Bm[:, 1] + dR) > 0.25
        for k, b in self.st['known']:
            g = np.array([BW.gap_pts_box(Wm[i:i + 1], dict(b, L=b['L'] + 0.5, W=b['W'] + 0.5)) for i in range(len(Wm))])
            keep &= g > 0.0
        if not keep.any(): return None, False
        Bm = Bm[keep]
        hedge_like = bool(np.ptp(Bm[:, 0]) > 1.2 and np.min(np.abs(Bm[:, 1])) > 0.30 and len(Bm) > 6)
        return float(np.min(Bm[:, 0]) - nose), hedge_like

    # ------------------------------------------------------------ clock / alerts / end
    def clock(self):
        c0 = self.st['clock0']; return None if c0 is None else c0 + self.w.t / 60.0
    def clock_str(self):
        c = self.clock(); return None if c is None else clock_fmt(c)
    def alert(self, text):
        self.st['alerts'].append(text); self.r.ev('ALERT', text)
    def finish(self, result, outcome):
        if self.st['result'] != 'running': return
        self.st['result'] = result; self.st['outcome'] = outcome; self.r.ev('pi', 'FINISH %s: %s' % (result, outcome))

    # ------------------------------------------------------------ tick (10 Hz)
    def tick(self, t):
        st = self.st
        if st['crashed']: self.crash_monitor(t); return
        if t - self.hb_t >= 0.2:      # 5 Hz heartbeat (dev s6a: at 1 Hz the GCS failsafe came 1.9 s after a freeze, 1.05 m rolled)
            self.hb_t = t; self.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
        if st['first_motion'] is None and abs(self.w.v) > 0.03 and self.booted:
            st['first_motion'] = self.clock_str(); st['metrics']['first_motion_clock'] = st['first_motion']; st['metrics']['first_motion_t'] = round(t, 1)
        self.update_lights()
        if not self.booted:
            if self.bootgen is None: self.bootgen = self.boot()
            try: next(self.bootgen)
            except StopIteration: self.booted = True; self.r.ev('pi', 'boot done (GUIDED, armed, fence %d pts)' % len(self.fence_pts))
            return
        self.injections(t)
        if st['crashed']: return
        if not self.w.chain_ok and not self.w.estop and st['result'] == 'running':
            self.alert('bump strip / body contact - stop chain open, robot stopped (%s)' % (self.w.chain_trips[-1]['why'] if self.w.chain_trips else '?'))
            self.finish('alert', 'contact stop'); return
        if self.pause_req and not self.no_pause and self.r.raw_fix == 6 and self.w.chain_ok:
            self.stop_cmd()
            if abs(self.w.v) < 0.01 and abs(self.w.w) < 0.06:
                self._rest_t = self._rest_t or t
                if t - self._rest_t > 0.5: self.paused = True
            else: self._rest_t = None
            return
        if st['i'] >= len(st['plan']):
            self.finish(self.sc.get('end_result', 'pass'), 'plan completed'); return
        if self.gen is None:
            op = st['plan'][st['i']]; st['opname'] = op[0]
            self.gen = getattr(self, 'op_' + op[0])(*op[1:])
        try: next(self.gen)
        except StopIteration:
            self.gen = None; st['i'] += 1; st['op'] = {}; self.no_pause = False
        if self.mode == 'HOLD' and self.booted and st['result'] == 'running' and not st['crashed'] and not self.fence_breach and not self.ekf_fs \
                and self.r.w.S.road_dist(np.array([self.w.x, self.w.y])) >= 9.0 and t - self._reguided > 5.0:
            self._reguided = t; self.r.ev('pi', 'unexpected firmware HOLD (EKF failsafe %s) -> request GUIDED' % self.ekf_fs); self.set_mode(15)
        if self.mode == 'HOLD' and self.booted and st['result'] == 'running' and not st['crashed'] and not self.sc.get('allow_hold'):
            if NOFIX_NOW and st.get('nofix_t0') is not None and self.fence_breach:
                self.alert('no GNSS fix: holding in the lane (the position estimate drifted past the fence after %.0f s without a fix)' % (t - st['nofix_t0'])); self.finish('alert', 'no fix hold')
            elif self.fence_breach or self.r.w.S.road_dist(np.array([self.w.x, self.w.y])) < 9.0:
                self.alert('firmware geofence HOLD at the road edge'); st['metrics']['fence_hold'] = dict(t=round(t, 1), legal_min=round(self.w.legal_min, 3))
                self.finish('alert', 'firmware fence hold')

    def boot(self):
        self.st['state'] = 'BOOT'; t0 = self.w.t
        while self.ekf_xy is None or self.gfix < 3 or self.yaw is None or self.w.t - t0 < 6.0 or (not self.ekf_gps and self.w.t - t0 < 70) or self.ekf_fs:
            if self.w.t - t0 > 150: self.r.ev('pi', 'boot: EKF not ready after 150 s'); break
            yield
        self.upload_fence(); t1 = self.w.t
        while self.upl['ack'] is None and self.w.t - t1 < 10: yield
        self.r.ev('pi', 'fence upload ack=%s (%d vertices)' % (self.upl['ack'], len(self.upl['items'])))
        self.mav.param_set_send(1, 1, b'FENCE_ENABLE', 1.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
        while True:
            self.set_mode(15); self.arm()
            for _ in range(10): yield
            if self.armed and self.mode == 'GUIDED': break
            if self.w.t - t0 > 150: self.r.ev('pi', 'boot: could not arm/GUIDED (mode %s armed %s)' % (self.mode, self.armed)); break
        self.stop_cmd()

    # ------------------------------------------------------------ test injections
    def injections(self, t):
        st = self.st; sc = self.sc
        cr = sc.get('crash')
        if cr and st['opname'] == cr[0] and not st['crashed']:
            ok = True
            if cr[0] == 'lane' and float(self.w.s_lat()[0]) < cr[1]: ok = False
            if cr[0] == 'grab' and st['op'].get('phase') != 'final': ok = False
            if ok and abs(self.w.v) > 0.05:
                st['crashed'] = True; st['state'] = 'CRASHED'; self.no_pause = True
                st['crash'] = dict(t=round(t, 2), v=round(self.w.v, 3), odo=self.w.odo, mode=self.mode, op=st['opname'])
                self.r.ev('pi', '*** COMPANION FREEZE INJECTED (op %s, v=%.2f m/s): heartbeat, attitude targets and lidar feed stop' % (st['opname'], self.w.v))
        es = sc.get('estop')
        if es and st['estop'] is None and st['opname'] == 'lane' and float(self.w.s_lat()[0]) >= es and abs(self.w.v) > 0.4:
            self.w.estop = True; self.w.chain_trip('E-STOP pressed'); st['estop'] = dict(t=round(t, 2), v=round(self.w.v, 3), odo=self.w.odo)
            self.r.ev('hw', 'E-STOP pressed at %.2f m/s (hard-wired chain opens, spring brakes)' % self.w.v)
        if st['estop'] is not None and 'stop_m' not in st['estop'] and abs(self.w.v) < 0.01:
            e = st['estop']; e['stop_m'] = round(self.w.odo - e['odo'], 3); e['stop_s'] = round(t - e['t'], 2); e.pop('odo', None)
            st['metrics']['estop'] = e; self.alert('E-stop pressed: robot stopped %.2f m / %.1f s' % (e['stop_m'], e['stop_s']))
        if st['estop'] is not None and 'stop_m' in st['estop'] and t - st['estop']['t'] > 8: self.finish('alert', 'e-stop')

    def crash_monitor(self, t):
        c = self.st['crash']
        if 'hold_t' not in c and self.mode == 'HOLD': c['hold_t'] = round(t - c['t'], 2); self.r.ev('fw', 'firmware HOLD %.2f s after the freeze' % c['hold_t'])
        if 'stop_t' not in c and abs(self.w.v) < 0.01: c['stop_t'] = round(t - c['t'], 2); c['stop_m'] = round(self.w.odo - c['odo'], 3)
        if t - c['t'] > 30:
            c['rolled_30s_m'] = round(self.w.odo - c['odo'], 3); c.pop('odo', None); self.st['metrics']['crash'] = c
            self.finish('alert', 'companion freeze -> firmware %s' % self.mode)

    # ------------------------------------------------------------ lights / hotel
    def update_lights(self):
        st = self.st['state']; active = st not in ('DOCKED', 'DONE', 'BOOT', 'IDLE')
        w = 2.0 if active else 0.0
        if self.w.night and active: w += 7.0 + (8.0 if abs(self.w.v) > 0.02 else 0.0)
        self.w.lights_w = w

    # ------------------------------------------------------------ primitives (generators)
    def rest(self, sec=0.5):
        t0 = self.w.t
        while self.w.t - t0 < sec or abs(self.w.v) > 0.01:
            self.stop_cmd(); yield
    def wait(self, sec, label, nopause=True):
        op = self.st['op']; key = 'wait_' + label
        if key not in op: op[key] = self.w.t + sec; self.r.ev('pi', '%s (%.0f s)' % (label, sec))
        self.no_pause = nopause
        while self.w.t < op[key]: self.stop_cmd(); yield
        self.no_pause = False; self.st['nofix_t0'] = None

    def pivot(self, yaw_tgt, loaded=None, tol=math.radians(1.2)):
        """pivot in place: turn-rate command while far (rate-capped, 0.45 rad/s loaded / 0.6 empty), then the firmware
        heading controller (GUIDED heading + zero speed) for the last 8 deg; done when within tol for 0.5 s (timeout 30 s:
        accepted if within 3 deg)."""
        if R5B and PPL_PAUSE:   # do not start a turn on the spot with someone near
            pr_ = self.ppl_near()
            if pr_ is not None and pr_ < PPL_PAUSE_R: yield from self.pause_for_people(pr_)
        rmax = 0.45 if self.w.carry else 0.6; t0 = self.w.t; ok_since = None
        if R5B: rmax = min(rmax, PIVOT_RATE)   # [revision 5] pivot slowly: the nose corner is 1.42 m from the axle, 0.2 rad/s keeps it under 0.3 m/s
        while True:
            e = wrap(yaw_tgt - self.yaw)
            if abs(e) < tol:
                ok_since = ok_since or self.w.t
                if self.w.t - ok_since > 0.5: break
            else: ok_since = None
            if self.w.t - t0 > (50.0 if R5B else 30.0):
                if abs(e) > math.radians(3.0): self.r.ev('pi', 'pivot timeout, %.1f deg left' % math.degrees(e))
                break
            # rate profile that brakes toward the target (decel 0.4 rad/s^2): the firmware turn-rate loop overshoots its command
            # (0.89 rad/s seen for a 0.6 cap) and the hand-over to the heading controller then overshot 20 deg - into the left
            # hedge end at pad A (B2-F dev s1a / s6b, truth clearance 0.15-0.17 m)
            rcap = min(rmax, max(0.10, math.sqrt(2 * 0.4 * max(abs(e) - math.radians(4.0), 0.0))))
            if R5B:   # gentle pivot: the rate command ramps up at 0.1 rad/s^2, comes down in proportion to the angle left, heading hold takes over at 2 deg
                rcap = min(rmax, 0.03 + 0.10 * (self.w.t - t0), max(0.04, 1.0 * abs(e)))
                if abs(e) > math.radians(2.0): self.att(rate_enu=float(math.copysign(rcap, e)), speed=0.0)
                else: self.att(yaw_tgt, 0.0)
            elif abs(e) > math.radians(6.0): self.att(rate_enu=float(np.clip(1.2 * e, -rcap, rcap)), speed=0.0)
            else: self.att(yaw_tgt, 0.0)
            yield
        yield from self.rest(0.3)

    def hold_for_obstacle(self, gap, what='object'):
        """stop + wait for the path to clear (3 s clear), alert after 120 s."""
        st = self.st; t0 = self.w.t; clear = None; self.no_pause = True
        st['metrics']['stops'].append(dict(t=round(t0, 1), gap=round(gap, 2), s=round(float(self.w.s_lat()[0]), 1)))
        self.r.ev('pi', 'unmapped %s %.2f m ahead -> stop' % (what, gap))
        while True:
            self.stop_cmd(); yield
            g, hl = self.obstacle_ahead()
            if g is None or g > 3.0 or hl: clear = clear or self.w.t
            else: clear = None
            if clear and self.w.t - clear > 3.0: self.r.ev('pi', 'path clear for 3 s -> resume'); break
            if self.w.t - t0 > 120.0:
                self.alert('path blocked for 120 s (unmapped object %.1f m ahead)' % (g or 0)); self.finish('alert', 'path blocked'); 
                while True: self.stop_cmd(); yield
        self.no_pause = False; self.st['nofix_t0'] = None

    def lat_nominal(self, s, sgn):
        """keep-left lateral target in the lane (m, + = left of house->road); 0 in the yard / mouth; ramps to 0 near sharp
        bends (heading change > 12 deg over +-4 m, as G6 bend-centring)."""
        if s < 25.0 or s > self.L - 13.0: return 0.0
        if not hasattr(self, '_bend'):
            ss = np.arange(0.0, self.L + 1.0, 1.0); hh = np.array([self.S.lane.heading(q) for q in ss])
            dh = np.array([abs(wrap(hh[min(i + 4, len(ss) - 1)] - hh[max(i - 4, 0)])) for i in range(len(ss))])
            f = np.clip((math.radians(25.0) - dh) / math.radians(13.0), 0.0, 1.0)
            f = np.array([f[max(0, i - 4):i + 5].min() for i in range(len(f))]); self._bend = f
        f = float(np.interp(s, np.arange(len(self._bend)), self._bend))
        if os.environ.get('X_BEND_KEEP') == '1': f = 1.0   # [revision 5 trial] stay on the left edge through bends too (no centring)
        return sgn * (HL - ROB['hw'] - KL_GAP) * f

    def lane(self, s_goal, lat_end=0.0, hold_lat_until=None, v_max=V_CRUISE, end_ramp=8.0):
        """follow the lane from the current station to s_goal (EKF pose + lidar face offset), keep-left between, lat_end at the end."""
        st = self.st; S = self.S; x, y, yaw = self.pose(); s0, l0 = S.lane.project(np.array([x, y]))
        sgn = 1 if s_goal > s0 else -1; st['state'] = 'LANE_%s%s' % ('DOWN' if sgn > 0 else 'UP', '_LOADED' if self.w.carry else '')
        lat_start = l0 if hold_lat_until is None else l0
        ltg_prev = None
        while True:
            x, y, yaw = self.pose(); s, l = S.lane.project(np.array([x, y]))
            rem = sgn * (s_goal - s)
            if rem < 0.12: break
            q = self.r.raw_fix; degraded = q < 6
            # nominal lateral target with ramps
            lat_n = self.lat_nominal(s, sgn)
            if degraded: lat_n = 0.0
            if hold_lat_until is not None and sgn * (hold_lat_until - s) > 0: lat_n = lat_start
            elif hold_lat_until is not None:
                f = min(1.0, sgn * (s - hold_lat_until) / 6.0); lat_n = lat_start + (lat_n - lat_start) * f
            if rem < end_ramp and lat_end is not None: f = max(0.0, rem / end_ramp); lat_n = lat_end + (lat_n - lat_end) * f
            # lidar hedge-face corridor offset: keep-left on the measured left face (bulges / irregular faces handled), centring
            # between both faces under a degraded fix; offset decays when no face is seen (gaps, yard, mouth)
            dL, dR = self.faces(); hw = ROB['hw']; o_meas = None
            if LID_FACE_OFF: dL, dR = None, None
            if FAULTS:
                fv_ = self.fault('lid', s, sgn)
                if fv_ is not None and dL is not None: dL = dL + fv_
            if NAV_CAM:   # the camera's reading of the left edge: bridges gaps in the lidar faces; if the two disagree by more than 0.25 m the nearer one is used
                cL = self.cam_left()
                if FAULTS:
                    fv_ = self.fault('cam', s, sgn)
                    if fv_ is not None: cL = fv_
                nv = st['metrics'].setdefault('navcam', dict(n=0, cam_only=0, both=0, disagree=0, none=0)); nv['n'] += 1
                if dL is None and cL is not None: dL = cL; nv['cam_only'] += 1
                elif dL is not None and cL is not None:
                    nv['both'] += 1
                    if abs(dL - cL) > 0.25:
                        nv['disagree'] += 1
                        if R5B:   # take the reading that fits the lane width together with the right face; no right face -> the nearer one
                            if dR is not None:
                                if abs(cL + dR - 2 * HL) < abs(dL + dR - 2 * HL): dL = cL; nv['dis_cam'] = nv.get('dis_cam', 0) + 1
                            else:   # no right face in view (then it is more than 4.5 m away): the nearer reading keeps the robot off the left hedge
                                nv['dis_near'] = nv.get('dis_near', 0) + 1
                                if cL < dL: dL = cL; nv['dis_cam'] = nv.get('dis_cam', 0) + 1
                        else: dL = min(dL, cL)
                    else: dL = 0.5 * (dL + cL)
                elif dL is None: nv['none'] += 1
            self.dLR = (dL, dR)
            in_lane = 25.0 < s < self.L - 13.0
            both = dL is not None and dR is not None
            narrow = (both and dL + dR < 3.3) or self.w.t < st['narrow_until']
            ramping = (rem < end_ramp and lat_end is not None) or (hold_lat_until is not None and sgn * (s - hold_lat_until) < 6.0)
            m_face = None          # wanted move to the robot's LEFT (m), measured on the hedge faces (pose-free)
            if in_lane and degraded and both: m_face = (dL - dR) / 2.0
            elif in_lane and not ramping and dL is not None: m_face = (dL - hw) - (HL - hw - sgn * lat_n)   # = KL_GAP on straights, centred at bends
            elif in_lane and not ramping and dR is not None and dR - hw < KL_GAP + 0.6: m_face = (1.0 if FIX_RCC else -1.0) * (KL_GAP + 0.6 - (dR - hw))
            if R5B and in_lane and not ramping and m_face is not None and not degraded:
                if dR is not None: m_face = max(m_face, 0.35 - (dR - hw))      # at least 0.35 m to the right face
                if dL is not None: m_face = min(m_face, (dL - hw) - 0.20)      # never plan closer than 0.20 m to the left face
                if both and (dL - hw) + (dR - hw) < 0.55: m_face = (dL - dR) / 2.0
            elif in_lane and not ramping and both and m_face is not None:     # never closer than 0.35 m to the right face either
                m_face = min(m_face, (dR - hw) - 0.35) if (dR - hw) < 0.35 + max(m_face, 0) else m_face
            dt = 0.1
            if m_face is not None:
                o_meas = (l + sgn * m_face) - lat_n      # EKF-frame offset that would put the robot there (bridges hedge gaps)
                st['lat_off'] += float(np.clip((float(np.clip(o_meas, -1.0, 1.0)) - st['lat_off']) * dt / 1.5, -0.03, 0.03))
            else: st['lat_off'] *= math.exp(-dt / 8.0)
            ltg = lat_n + st['lat_off']
            if ltg_prev is not None: ltg = ltg_prev + float(np.clip(ltg - ltg_prev, -0.012, 0.012))
            ltg_prev = ltg; self.lat_tgt = round(ltg, 3)
            if m_face is not None:
                mf = float(np.clip(m_face, -0.6, 0.6)); mprev = st.get('mf_prev', mf); mf = mprev + float(np.clip(mf - mprev, -0.02, 0.02)); st['mf_prev'] = mf
                e_left = mf
            else: e_left = sgn * (ltg - l); st['mf_prev'] = e_left
            if FAULTS:
                fv_ = self.fault('steer', s, sgn)
                if fv_ is not None: e_left = fv_
            # clearance estimate (Pi side) for the log
            self.hc_now = None if dL is None and dR is None else min([d - hw for d in (dL, dR) if d is not None])
            # speed policy
            v = min(v_max, VMAX)
            if VSLOPE:   # person-stop rule: slower on a downhill slope (the stop after a bumper touch must end inside the bumper's travel)
                hd_ = self.w.yaw; gdown = -9.0
                for dk_ in range(int(VLOOK) + 1):   # steepest downhill slope here and up to VLOOK metres ahead
                    gx_, gy_ = self.S.ter.grad(self.w.x + dk_ * math.cos(hd_), self.w.y + dk_ * math.sin(hd_)); gdown = max(gdown, -(gx_ * math.cos(hd_) + gy_ * math.sin(hd_)))
                for thr_, vb_, ve_ in VSLOPE:
                    if gdown >= thr_: v = min(v, vb_ if (self.w.carry and self.w.bins[self.w.carry]['mass'] >= 40.0) else ve_)   # an empty bin does not load the braked wheels
            if degraded: v = min(v, V_SLOW)
            if s < 25.0 or s > self.L - 14.0: v = min(v, V_SLOW)
            if narrow: v = min(v, V_SLOW)
            v = min(v, 0.12 + 0.38 * rem / 3.0)
            # GNSS loss policy: dead reckoning limit -> hold
            if q == 1 and not self.dr_ok():
                yield from self.no_fix_hold()
                continue
            # obstacles
            g, hl = self.obstacle_ahead()
            if g is not None:
                if hl: st['narrow_until'] = self.w.t + 16.0
                elif g < 1.5: yield from self.hold_for_obstacle(g); continue
                elif g < 4.0: v = min(v, 0.25)
            if R5B and PPL_PAUSE:   # anyone near, anywhere in the camera's view: pause
                pr_ = self.ppl_near()
                if pr_ is not None and pr_ < PPL_PAUSE_R: yield from self.pause_for_people(pr_); continue
            if R5B and CAM_PEOPLE:   # the camera's person detector: independent of the map and of the fix
                gp_ = self.ppl_gap()
                if gp_ is not None:
                    if gp_ < 1.5: yield from self.hold_for_person(gp_); continue
                    if gp_ < 4.0: v = min(v, 0.25)
            if R5B and in_lane:
                pg = self.prot_field()
                if pg is not None:
                    yield from self.prot_stop(pg); ltg_prev = None; continue
            # heading = lane tangent (0.6 m preview) + lateral correction toward the target lateral (no chord corner-cutting:
            # geometric pure pursuit on the 2 m chord cut the s 270-277 bend by 0.4 m into the left hedge)
            Ld = 1.6
            h = S.lane.heading(s + sgn * 0.6) + (0.0 if sgn > 0 else math.pi)
            hdg = wrap(h + math.atan2(e_left, Ld))
            if R5B:   # the heading command may only change at HDG_RATE: whatever goes wrong upstream, the nose swings slowly enough for the protective field
                hp_ = st.get('hdg_prev') if self.w.t - st.get('hdg_t', -9.0) < 0.5 else self.yaw
                hdg = wrap(hp_ + float(np.clip(wrap(hdg - hp_), -HDG_RATE * 0.1, HDG_RATE * 0.1))); st['hdg_prev'] = hdg; st['hdg_t'] = self.w.t
            self.att(hdg, v); yield
        self.lat_tgt = None
        yield from self.rest(0.4)

    def fault(self, kind, s=None, sgn=1):
        """value of an active injected fault of this kind, else None (X_FAULT, tests only)."""
        for f in FAULTS:
            if f['kind'] != kind: continue
            if f['t0'] is None and s is not None and sgn > 0 and s >= f['s']:
                f['t0'] = self.w.t; self.r.ev('test', 'FAULT INJECTED: %s = %+.2f for %.0f s at s %.1f' % (kind, f['val'], f['dur'], s))
                self.st['metrics'].setdefault('faults', []).append(dict(kind=kind, t=round(self.w.t, 1), s=round(s, 1), val=f['val'], dur=f['dur']))
            if f['t0'] is not None and self.w.t - f['t0'] < f['dur']: return f['val']
        return None
    def prot_field(self):
        """[revision 5] pose-free protective field: ANY lidar return (hedge or not; the map is not used) inside the robot's own
        path, from the nose to PF_D ahead, robot width + PF_W each side. Returns the gap ahead of the nose (m) or None."""
        if self.scan is None: return None
        r = self.scan; ok = np.isfinite(r)
        if not ok.any(): return None
        ang = np.radians(np.arange(360))[ok]; bx = ROB['lidar_x'] + r[ok] * np.cos(ang); by = r[ok] * np.sin(ang)
        m = (bx > ROB['lidar_x'] - 0.15) & (bx < ROB['x1'] + PF_D) & (np.abs(by) < ROB['hw'] + PF_W)   # beside the nose as well as ahead of it
        return float(max(np.min(bx[m]) - ROB['x1'], 0.0)) if int(m.sum()) >= 2 else None
    def prot_stop(self, gap):
        """stop, back out 0.8 m along the track just driven (rear lidar and rear camera watch the rear on the real robot; the rear
        is not modelled here), forget the lateral offset and start again from the edges. Three trips in two minutes -> hold + alert."""
        st = self.st; t0 = self.w.t; self.no_pause = True
        L_ = st['metrics'].setdefault('prot_stops', []); L_.append(dict(t=round(t0, 1), s=round(float(self.w.s_lat()[0]), 1), gap=round(gap, 2)))
        self.r.ev('pi', 'protective field: return %.2f m ahead of the nose inside the robot\'s own path (or beside the nose) -> stop, back out' % gap)
        yield from self.rest(1.0)
        if len([q for q in L_ if t0 - q['t'] < 120.0]) >= 3:
            self.alert('protective field tripped 3 times in 2 minutes - holding in the lane'); self.finish('alert', 'path blocked')
            while True: self.stop_cmd(); yield
        y0 = self.yaw; t1 = self.w.t
        while self.w.t - t1 < 8.0: self.att(y0, -0.10); yield
        yield from self.rest(0.5)
        st['lat_off'] = 0.0; st.pop('mf_prev', None); self.no_pause = False; st['nofix_t0'] = None

    def no_fix_hold(self):
        st = self.st; t0 = self.w.t; self.no_pause = True; st['nofix_t0'] = t0
        self.r.ev('pi', 'no GNSS fix and dead-reckoning limit (%.1f m) reached -> HOLD, waiting for a fix' % st['dr_m'])
        st['metrics'].setdefault('nofix_holds', []).append(dict(t=round(t0, 1), s=round(float(self.w.s_lat()[0]), 1), dr_m=round(st['dr_m'], 1)))
        while self.r.raw_fix == 1:
            self.stop_cmd(); yield
            if self.w.t - t0 > 60.0:
                self.alert('no GNSS fix for 60 s after %.0f m dead reckoning - holding in the lane' % st['dr_m']); self.finish('alert', 'no fix hold')
                while True: self.stop_cmd(); yield
        self.no_pause = False; self.st['nofix_t0'] = None

    def follow(self, pts, reverse=False, v=V_MAN, tol=0.03, Ld=0.6):
        """pure pursuit on a short path (list of xy) forward or reverse; heading command = path tangent direction (+pi reversing)."""
        P = np.array(pts, float)
        if len(P) >= 2:      # densify to 5 cm (a 2-point path ended half-way: nearest-vertex progress)
            Q = [P[0]]
            for a_, b_ in zip(P[:-1], P[1:]):
                k = max(1, int(np.ceil(np.linalg.norm(b_ - a_) / 0.05)))
                Q += [a_ + (b_ - a_) * (j / k) for j in range(1, k + 1)]
            P = np.array(Q)
        n = len(P)
        cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]; Ltot = cum[-1]; i_prev = 0; t0 = self.w.t
        if R5B and n > 1:   # [revision 5] turn to the path's first direction as a slow pivot BEFORE moving: a heading step sent with the first speed
            # command made the firmware spin the robot at up to 0.9 rad/s (nose corner 1.2 m/s)
            x, y, yaw = self.pose(); j0 = int(np.searchsorted(cum, min(Ld, Ltot))); tg0 = P[min(j0, n - 1)]
            if np.linalg.norm(tg0 - np.array([x, y])) > 0.10:
                d0 = math.atan2(tg0[1] - y, tg0[0] - x); h0 = wrap(d0 + math.pi) if reverse else d0
                if abs(wrap(h0 - yaw)) > math.radians(8.0): yield from self.pivot(h0); t0 = self.w.t
        while True:
            if R5B and PPL_PAUSE:
                pr_ = self.ppl_near()
                if pr_ is not None and pr_ < PPL_PAUSE_R: tw_ = self.w.t; yield from self.pause_for_people(pr_); t0 += self.w.t - tw_; continue
            x, y, yaw = self.pose(); p = np.array([x, y])
            j1 = min(n, i_prev + 30); d = np.linalg.norm(P[i_prev:j1] - p, axis=1); i = i_prev + int(np.argmin(d)); i_prev = i; sp = cum[i]
            if self.w.t - t0 > 30.0 + 8.0 * Ltot / max(v, 0.05): self.r.ev('pi', 'follow timeout (%.2f m left)' % (Ltot - sp)); break
            rem = Ltot - sp
            last = P[-1]; tang = P[-1] - P[-2] if n > 1 else np.array([1.0, 0.0]); tang = tang / (np.linalg.norm(tang) + 1e-9)
            if rem < tol or float((p - last) @ tang) > -tol: break
            sa = sp + Ld; j = int(np.searchsorted(cum, sa)); tgt = P[min(j, n - 1)]
            if np.linalg.norm(tgt - p) < 0.05: tgt = last
            dirn = math.atan2(tgt[1] - y, tgt[0] - x)
            if rem < 0.30:
                # last 0.3 m: hold the path's end tangent (aiming at the end point itself swung the heading command and the
                # firmware spun the robot at 0.9 rad/s, 20 deg past the hold heading, at the pad A hedge end - dev s1a / s6b)
                dirn = math.atan2(tang[1], tang[0])
            vv = min(v, 0.06 + 0.5 * rem)
            if not reverse:
                g, hl = self.obstacle_ahead(look=3.0)
                if g is not None and g < 0.6 and not hl: yield from self.hold_for_obstacle(g); continue
            if reverse: self.att(wrap(dirn + math.pi), -vv)
            else: self.att(dirn, vv)
            yield
        yield from self.rest(0.4)

    def hermite(self, p0, yaw0, p1, yaw1, reverse=False, k=None):
        """C1 path from pose 0 to pose 1 (travel direction = yaw, +pi when reversing)."""
        d0 = yaw0 + (math.pi if reverse else 0.0); d1 = yaw1 + (math.pi if reverse else 0.0)
        D = float(np.linalg.norm(np.array(p1) - np.array(p0))); k = k or D
        t = np.linspace(0, 1, max(10, int(D / 0.05)))[:, None]
        h00 = 2 * t ** 3 - 3 * t ** 2 + 1; h10 = t ** 3 - 2 * t ** 2 + t; h01 = -2 * t ** 3 + 3 * t ** 2; h11 = t ** 3 - t ** 2
        m0 = k * np.array([math.cos(d0), math.sin(d0)]); m1 = k * np.array([math.cos(d1), math.sin(d1)])
        return (h00 * np.array(p0) + h10 * m0 + h01 * np.array(p1) + h11 * m1).tolist()

    def goto_pose(self, x1, y1, yaw1, reverse, v=V_MAN, mode='ppl'):
        """pivot-line-pivot (skid steer): turn to face the line (or put the tail on it), drive the straight line, turn to yaw1."""
        x, y, yaw = self.pose(); D = math.hypot(x1 - x, y1 - y)
        if D > 0.04:
            dirn = math.atan2(y1 - y, x1 - x); h = wrap(dirn + math.pi) if reverse else dirn
            if abs(wrap(h - yaw)) > math.radians(1.5): yield from self.pivot(h)
            x, y, yaw = self.pose()
            yield from self.follow([[x, y], [x1, y1]] if D < 0.3 else np.linspace([x, y], [x1, y1], int(D / 0.05) + 2).tolist(), reverse=reverse, v=v)
        if yaw1 is not None: yield from self.pivot(yaw1)

    # ------------------------------------------------------------ sweep check (Pi planning, map + known objects)
    def sweep_clear(self, poses, loaded):
        H = self.map_segs; best = 9.0
        for (x, y, yaw) in poses:
            P = BW.rect_pts(x, y, yaw, ROB['x0'], ROB['x1'], ROB['hw'], 8)
            if loaded and self.w.carry:
                b = self.w.bins[self.w.carry]; T = BIN_T[b['size']]; bx = self.w.bin_pose_in_robot(b)
                P = np.r_[P, BW.rect_pts(x, y, yaw, bx - T['D'] / 2, bx + T['D'] / 2, T['W'] / 2, 5)]
            mid = 0.5 * (H[:, :2] + H[:, 2:]); Hn = H[np.linalg.norm(mid - np.array([x, y]), axis=1) < 5]
            if len(Hn): best = min(best, float(np.min(seg_dist(P[:, None, :], Hn[None, :, :2], Hn[None, :, 2:]))))
            for k, b in self.st['known']:
                if b.get('ignore'): continue
                best = min(best, BW.gap_pts_box(P, b) + 0.0)
        return best
    def pivot_poses(self, x, y, y0, y1, n=12):
        return [(x, y, y0 + wrap(y1 - y0) * f) for f in np.linspace(0, 1, n)]

    # ------------------------------------------------------------ geometry helpers
    def hold_pose(self, bx, by, byaw, size):
        """robot pose holding a bin whose handle points byaw: robot faces byaw+pi, bin centre at robot x = comb - D/2."""
        ryaw = wrap(byaw + math.pi); xb = ROB['comb_x'] - BIN_T[size]['D'] / 2
        return bx - xb * math.cos(ryaw), by - xb * math.sin(ryaw), ryaw
    def pad_xy(self, pad):
        d = self.sc['pads'][pad]; x, y, h = self.S.pose(d['s'], d['lat'], 0.0); return x, y, h     # handle toward the road (down-lane)
    def home_xy(self, col):
        d = self.sc['home'][col]; x, y, h = self.S.pose(d['s'], d['lat'], 0.0); return x, y, h
    def set_known(self, name, box):
        self.st['known'] = [kb for kb in self.st['known'] if kb[0] != name] + ([[name, box]] if box else [])

    # ------------------------------------------------------------ ops
    def op_idle(self, sec):
        self.st['state'] = 'IDLE'; yield from self.wait(sec, 'idle', nopause=False)

    def op_preflight(self, kind):
        """weather no-go, energy guard (C6), [county] bye-law window (18:00-21:00)."""
        st = self.st; sc = self.sc; self.st['state'] = 'DOCKED'
        wx = sc.get('weather', {})
        if wx.get('gust', 5.0) >= 15.0:
            self.alert('weather no-go: wind gust %.0f m/s >= 15 m/s - bins stay home' % wx['gust']); self.finish('alert', 'wind no-go'); return
        if wx.get('frost') and wx.get('air_c', 5.0) <= 0.0:
            self.alert('weather no-go: frost / ice on the lane (air %.1f C) - bins stay home' % wx['air_c']); self.finish('alert', 'frost no-go'); return
        cold = float(np.interp(self.w.air_c, [-20, -10, 0, 10, 25], [0.60, 0.75, 0.88, 0.95, 1.0])); usable = BW.PACK['wh'] * cold
        avail = self.w.soc * usable - RESERVE * usable
        st['metrics'].setdefault('guard', []).append(dict(t=round(self.w.t, 1), soc=round(self.w.soc, 3), avail_wh=round(avail, 1), budget_wh=TRIP_WH, kind=kind))
        if avail < TRIP_WH:
            self.alert('energy guard: %.0f Wh available above the 10 %% reserve < %.0f Wh trip budget - trip refused, staying on the dock' % (avail, TRIP_WH))
            self.finish('alert', 'energy guard'); return
        c = self.clock()
        if BYELAW and c is not None:
            if kind.startswith('pickup') and PICK_CLOCK and not st.get('clk_shift'):   # test: collection-day returns start earlier, once the crew has been
                hh_, mm_ = PICK_CLOCK.split(':'); st['clock0'] = int(hh_) * 60 + int(mm_) - self.w.t / 60.0; st['clk_shift'] = True; c = self.clock()
            done_ = [t_['min'] for t_ in st['metrics'].get('trips', []) if 'min' in t_]; est = (max(done_) * 1.05) if done_ else TRIP_MIN; m_ = c % 1440
            st['metrics'].setdefault('window', []).append(dict(kind=kind.split(' ')[0], clock=clock_fmt(c), est_min=round(est, 1)))
            if kind.startswith('drop'):     # the evening before: not before 18:00; no bye-law end, only the quiet-hours limit
                if 6 * 60 < m_ < 18 * 60: self.alert('bye-law: before 18:00, waiting'); self.finish('alert', 'too early'); return
                if m_ >= 18 * 60 and m_ + est > QUIET_END: self.alert('quiet hours: a drop started now would end after %s - not started' % clock_fmt(QUIET_END)); self.finish('alert', 'too late'); return
            else:                           # collection day: back by 21:00; may start once the crew has been (PICK_FROM)
                if m_ < PICK_FROM: self.alert('collection day: before %s, waiting' % clock_fmt(PICK_FROM)); self.finish('alert', 'too early'); return
                if m_ + est > 21 * 60: self.alert('bye-law: a return started now would end after 21:00 (trip %.0f min) - not started' % est); self.finish('alert', 'too late'); return
        elif c is not None:
            if c % 1440 < 18 * 60 and c % 1440 > 6 * 60:
                self.alert('bye-law: before 18:00, waiting'); self.finish('alert', 'too early'); return
            if (c + 50.0) % 1440 > 21 * 60 and (c % 1440) >= 18 * 60:
                self.alert('bye-law: a trip now would end after 21:00 - not started'); self.finish('alert', 'too late'); return
        st['trip'] = dict(kind=kind, t0=round(self.w.t, 1), wh0=round(self.w.energy_wh, 3), clk0=self.clock_str())
        self.r.ev('pi', 'preflight OK (%s): %.0f Wh available, clock %s' % (kind, avail, self.clock_str()))
        yield

    def op_trip_end(self):
        st = self.st; tr = st['trip']
        if tr:
            tr.update(t1=round(self.w.t, 1), wh=round(self.w.energy_wh - tr['wh0'], 2), clk1=self.clock_str(), min=round((self.w.t - tr['t0']) / 60.0, 1))
            st['metrics']['trips'].append(tr); self.r.ev('pi', 'trip done: %.1f Wh, %.1f min, back %s' % (tr['wh'], tr['min'], tr['clk1'])); st['trip'] = None
        st['last_dock'] = self.clock_str(); st['metrics']['last_dock_clock'] = st['last_dock']
        yield

    def op_undock(self):
        st = self.st; st['state'] = 'UNDOCK'
        yield from self.wait(T_UNDOCK, 'undock: charger off, beacon + pre-motion warning')
        x, y, yaw = self.pose()
        yield from self.follow([[x, y], [x - 1.2 * math.cos(yaw), y - 1.2 * math.sin(yaw)]], reverse=True, v=V_REV)

    def op_lane(self, s_goal, lat_end=0.0, hold_lat_until=None):
        if FIX_RCA and hold_lat_until is not None and not self.st['op'].get('yx'):
            yield from self.yard_exit(); self.st['op']['yx'] = True
        yield from self.lane(s_goal, lat_end, hold_lat_until)

    def yard_exit(self, s_entry=21.0, hold=1.0, lat_min=2.0):
        """[variant X_FIX_RCA] planned exit from a home spot far off the centre-line: straight ahead `hold` m, then a C1 curve
        to the lane centre-line at s_entry with the lane heading there. Checked against the map and the known bins first;
        if the check fails the frozen behaviour (lateral ramp inside lane()) is used."""
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

    def op_pivot_dir(self, which):
        """pivot to face down-lane ('down') or up-lane ('up') at the current station."""
        s, l = self.s_lat(); h = self.S.lane.heading(s); self.st['state'] = 'PIVOT' + ('_LOADED' if self.w.carry else '')
        tgt = h if which == 'down' else wrap(h + math.pi)
        x, y, yaw = self.pose(); c = self.sweep_clear(self.pivot_poses(x, y, yaw, tgt), True)
        if c < 0.15: self.r.ev('pi', 'pivot sweep clearance only %.2f m (map)' % c)
        yield from self.pivot(tgt)

    def op_verify_bin(self, name, where):
        """lidar check of the bin at its expected spot before committing (missing / tipped / approach blocked)."""
        st = self.st; st['state'] = 'VERIFY'; yield from self.rest(0.5)
        Ws = []
        for _ in range(15):
            self.stop_cmd(); yield
            Wk, Bk = self.scan_pts(); Ws.append(Wk)
        b = self.sc['expect_bins'][name]; bx, by, byaw = b['x'], b['y'], b['yaw']; size = b['size']
        W = np.concatenate(Ws) if Ws else np.zeros((0, 2)); T = BIN_T[size]
        near = W[np.hypot(W[:, 0] - bx, W[:, 1] - by) < 1.0] if len(W) else W
        hx, hy, hyaw = self.hold_pose(bx, by, byaw, size)
        res = dict(bin=name, n_pts=int(len(near)))
        if len(near) < 4:
            res['verdict'] = 'missing'; st['metrics']['verify'] = res
            self.alert('bin %s not found at %s (lidar: %d returns) - photo sent, heading home empty' % (name, where, len(near)))
            self.st['plan'] = self.st['plan'][:self.st['i'] + 1] + [('lane_short', -1, 20.0), ('end', 'alert', 'bin missing')]; return
        c, s_ = math.cos(byaw), math.sin(byaw); d = near - np.array([bx, by])
        ext_perp = float(np.ptp(-d[:, 0] * s_ + d[:, 1] * c)); ext_al = float(np.ptp(d[:, 0] * c + d[:, 1] * s_))
        if R5B:   # extent per scan, median over the scans: merging 15 scans in world coordinates smears the outline when the heading estimate wobbles
            ex_ = []
            for Wk in Ws:
                if len(Wk) == 0: continue
                nk = Wk[np.hypot(Wk[:, 0] - bx, Wk[:, 1] - by) < 1.0]
                if len(nk) >= 4: dk = nk - np.array([bx, by]); ex_.append((float(np.ptp(-dk[:, 0] * s_ + dk[:, 1] * c)), float(np.ptp(dk[:, 0] * c + dk[:, 1] * s_))))
            if ex_: res['merged_m'] = [round(ext_perp, 2), round(ext_al, 2)]; ext_perp = float(np.median([q[0] for q in ex_])); ext_al = float(np.median([q[1] for q in ex_]))
        res.update(width_m=round(ext_perp, 2), depth_m=round(ext_al, 2))
        if ext_perp > T['W'] + 0.25 or ext_al > T['D'] + 0.25:
            res['verdict'] = 'tipped'; st['metrics']['verify'] = res
            self.alert('bin %s at %s does not look upright (lidar outline %.2f x %.2f m) - not grabbing, photo sent' % (name, where, ext_perp, ext_al))
            self.st['plan'] = self.st['plan'][:self.st['i'] + 1] + [('end', 'alert', 'bin tipped')]; return
        # approach corridor (pivot spot -> pre-grab -> hold) must be free of unmapped returns other than the bin itself
        far = W[np.hypot(W[:, 0] - bx, W[:, 1] - by) >= 0.75] if len(W) else W
        ryaw = hyaw; cc, ss = math.cos(ryaw), math.sin(ryaw)
        busy = 0
        for q in far:
            dq = q - np.array([hx, hy]); u = dq[0] * cc + dq[1] * ss; v = -dq[0] * ss + dq[1] * cc     # (was 'd': shadowed the bin points below)
            if -0.2 < u < PREGRAB + ROB['x1'] + 3.2 and abs(v) < ROB['hw'] + 0.25:
                if self.S.hedge_dist(q) > 0.4: busy += 1
        res['corridor_returns'] = busy
        if busy >= 3:
            res['verdict'] = 'blocked'; st['metrics']['verify'] = res
            self.alert('approach to bin %s at %s is blocked (%d unmapped returns in the approach corridor) - not grabbing' % (name, where, busy))
            self.st['plan'] = self.st['plan'][:self.st['i'] + 1] + [('end', 'alert', 'bin blocked')]; return
        # refine the bin pose from the visible front-wall face (lateral = median across the face, along = face + D/2)
        u = d[:, 0] * c + d[:, 1] * s_; v = -d[:, 0] * s_ + d[:, 1] * c
        face = (u - u.min()) < 0.06
        if face.sum() >= 10 and np.ptp(v[face]) > 0.3:
            slope = float(np.polyfit(v[face], u[face], 1)[0]); th = -math.atan(slope)
            if abs(th) < math.radians(8):
                byaw = wrap(byaw + th); c, s_ = math.cos(byaw), math.sin(byaw); u = d[:, 0] * c + d[:, 1] * s_; v = -d[:, 0] * s_ + d[:, 1] * c
                face = (u - u.min()) < 0.06; res['refine_yaw_deg'] = round(math.degrees(th), 2)
        if face.sum() >= 3:
            v_c = float(np.median(v[face])) if np.ptp(v[face]) > 0.4 * T['W'] else 0.0
            u_f = float(np.median(u[face]))
            # front wall is the face nearest the robot: on the -handle side (u < 0) for a handles-out bin seen from up-lane
            du = (u_f + T['D'] / 2) if u_f < 0 else 0.0
            if abs(v_c) < 0.15 and abs(du) < 0.15:
                nb = dict(b); nb['x'] = bx + du * c - v_c * s_; nb['y'] = by + du * s_ + v_c * c; nb['yaw'] = byaw; self.sc['expect_bins'][name] = nb
                res['refine_m'] = [round(du, 3), round(v_c, 3)]
        res['verdict'] = 'ok'; st['metrics']['verify'] = res; self.r.ev('pi', 'bin %s verified at %s (%d returns, %.2f x %.2f m)' % (name, where, len(near), ext_perp, ext_al))
        yield

    def op_pad_check(self, pad):
        """Pi geofence pre-check before setting off with a bin for a pad: placed bin + robot at the hold pose >= 0.3 m inside
        the private boundary (the firmware fence is the second layer)."""
        st = self.st; tx, ty, tyaw = self.pad_xy(pad); size = self.sc['carry_size']
        hx, hy, hyaw = self.hold_pose(tx, ty, tyaw, size)
        P = np.r_[BW.rect_pts(hx, hy, hyaw, ROB['x0'], ROB['x1'], ROB['hw'], 8), BW.rect_pts(tx, ty, tyaw, -BIN_T[size]['D'] / 2, BIN_T[size]['D'] / 2, BIN_T[size]['W'] / 2, 6)]
        m = min(self.S.road_dist(p) for p in P) - self.S.boundary
        st['metrics']['pad_check'] = dict(pad=pad, margin_m=round(m, 2))
        if m < 0.3 and not self.sc.get('pi_fence_bypass'):
            self.alert('drop spot %s is %.2f m from the road-verge boundary (< 0.3 m): not going - please re-draw the pad in the app' % (pad, m))
            self.finish('alert', 'pad outside geofence'); return
        yield

    def op_wait_clear(self, pad, tmax=180.0):
        """at the stage before a pad: the pad zone (hold footprint + reverse corridor) and the mouth must be free of unmapped
        lidar returns for 3 s (vehicles turning in the bell-mouth, people); wait up to tmax, then alert."""
        st = self.st; st['state'] = 'WAIT_CLEAR'; self.no_pause = True; t0 = self.w.t; clear = None; n_last = 0
        tx, ty, tyaw = self.pad_xy(pad); sp, lp = self.S.lane.project(np.array([tx, ty]))
        while True:
            self.stop_cmd(); yield
            W, B = self.scan_pts(); n = 0
            for q in W:
                sq, lq = self.S.lane.project(q)
                if sp - 3.5 <= sq <= min(sp + 4.0, self.L - 6.5) and abs(lq) < 3.0 and self.S.hedge_dist(q) > 0.4:
                    if not any(BW.gap_pts_box(q[None], dict(b, L=b['L'] + 0.4, W=b['W'] + 0.4)) == 0.0 for k, b in st['known']): n += 1
            n_last = n
            if n < 3: clear = clear or self.w.t
            else: clear = None
            if clear is not None and self.w.t - clear >= 3.0: break
            if self.w.t - t0 > tmax:
                self.alert('pad %s / bell-mouth not clear for %.0f s - holding at the stage' % (pad, tmax)); self.finish('alert', 'pad not clear')
                while True: self.stop_cmd(); yield
        w8 = round(self.w.t - t0, 1); st['metrics'].setdefault('waits', []).append(dict(pad=pad, wait_s=w8))
        if w8 > 4.0: self.r.ev('pi', 'pad %s clear after %.0f s wait' % (pad, w8))
        self.no_pause = False; self.st['nofix_t0'] = None

    def op_lane_short(self, sgn, dist):
        s, l = self.s_lat(); h = self.S.lane.heading(s); tgt = h if sgn > 0 else wrap(h + math.pi)
        if abs(wrap(tgt - self.yaw)) > 0.3: yield from self.pivot(tgt)
        yield from self.lane(s + sgn * dist, lat_end=0.0)

    def op_end(self, result, outcome):
        yield from self.rest(1.0); self.finish(result, outcome); yield

    def op_grab(self, name, where):
        """pre-grab pose (1.2 m out on the bin axis, MuJoCo G1 start) -> C8 gate -> camera/ToF-guided reverse onto the front wall
        (0.15 -> 0.06 m/s) -> comb engage + lift + pad (MuJoCo gate front dock 90/90) -> bin rigid on the comb."""
        st = self.st; op = st['op']; b = self.w.bins[name]; st['state'] = 'GRAB_APPROACH'
        exp = self.sc['expect_bins'][name]
        hx, hy, hyaw = self.hold_pose(exp['x'], exp['y'], exp['yaw'], exp['size'])
        px, py = hx + PREGRAB * math.cos(hyaw), hy + PREGRAB * math.sin(hyaw)
        self.set_known(name, dict(x=exp['x'], y=exp['y'], yaw=exp['yaw'], L=BIN_T[exp['size']]['D'], W=BIN_T[exp['size']]['W']))
        if op.get('phase') is None:
            x, y, yaw = self.pose(); fwd = math.cos(wrap(math.atan2(py - y, px - x) - yaw)) > 0 if math.hypot(px - x, py - y) > 0.05 else True
            # reverse onto the pre-grab pose if the robot already faces the hold heading (pre-grab is behind it)
            rev = abs(wrap(yaw - hyaw)) < math.pi / 2 and not fwd
            ca, sa_ = math.cos(hyaw), math.sin(hyaw); al = abs((px - x) * ca + (py - y) * sa_); lt = abs(-(px - x) * sa_ + (py - y) * ca)
            if al > 1.0 and lt < (0.40 if FIX_APP else 0.15) * al and abs(wrap(yaw - hyaw)) < math.radians(20):
                path = self.hermite((x, y), yaw, (px, py), hyaw, reverse=rev)
                yield from self.follow(path, reverse=rev, v=V_REV if rev else V_MAN)
            else:
                yield from self.goto_pose(px, py, None, reverse=rev, v=V_REV if rev else V_MAN)
            yield from self.pivot(hyaw, tol=math.radians(0.8))
            op['phase'] = 'gate'
        if FIX_RCB and not op.get('cam_done'):
            # [variant X_FIX_RCB] rear docking camera at the pre-grab pose: lateral offset of the bin axis (truth + noise CAM_SIG).
            # More than CAM_TOL off -> correct the bin estimate by the difference and re-align, before the frozen truth gate.
            if not hasattr(self, '_cam_rng'): self._cam_rng = np.random.default_rng(int(self.r.seed) * 7919 + 13)
            cam_ok = True
            for k_ in range(CAM_TRIES + 1 if CAM_REFUSE else 2):
                thx_, thy_, thyaw_ = self.hold_pose(b['x'], b['y'], b['yaw'], b['size'])
                tpx_, tpy_ = thx_ + PREGRAB * math.cos(thyaw_), thy_ + PREGRAB * math.sin(thyaw_)
                lat_true = -(self.w.x - tpx_) * math.sin(thyaw_) + (self.w.y - tpy_) * math.cos(thyaw_)
                rng_ = np.random.default_rng([int(self.r.seed), 7919, len(st['metrics'].get('cam_checks', []))]) if CAM_RNG else self._cam_rng
                e_cam, seen = cam_frames(rng_, CAM_AVG); lat_cam = lat_true + CAM_BIAS + e_cam
                x, y, yaw = self.pose(); e_est = -(x - px) * math.sin(hyaw) + (y - py) * math.cos(hyaw)
                st['metrics'].setdefault('cam_checks', []).append(dict(bin=name, k=k_, lat_cam=round(lat_cam, 3), lat_true=round(lat_true, 3), e_est=round(e_est, 3), seen=seen))
                if seen and abs(lat_cam) <= CAM_TOL: break
                if CAM_REFUSE and k_ == CAM_TRIES: cam_ok = False; break
                if not seen:   # no reading: re-align on the present estimate and look again
                    self.r.ev('pi', 'rear camera: no reading of bin %s, re-aligning' % name); lat_cam = e_est
                d_ = CAM_GAIN * (e_est - lat_cam)
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
            if not cam_ok:
                self.alert('could not line up on bin %s (rear camera still more than %.0f mm off, or no reading, after %d re-alignments) - not grabbing' % (name, CAM_TOL * 1000, CAM_TRIES))
                st['metrics'].setdefault('refused', []).append(dict(bin=name, why='camera'))
                if FIX_RTH: self.st['plan'] = self.st['plan'][:self.st['i'] + 1] + ([('lane', 8.0, 0.0)] if where != 'home' else []) + [('dock',), ('trip_end',), ('end', 'alert', 'grab refused, back on the dock')]; return
                self.finish('alert', 'grab gate'); return
        # C8 gate (truth) - the MuJoCo G1 start envelope
        thx, thy, thyaw = self.hold_pose(b['x'], b['y'], b['yaw'], b['size'])          # TRUE bin axis (truth, for the gate)
        tpx, tpy = thx + PREGRAB * math.cos(thyaw), thy + PREGRAB * math.sin(thyaw)
        for attempt in range(2):
            c, s_ = math.cos(thyaw), math.sin(thyaw); dx, dy = self.w.x - tpx, self.w.y - tpy
            lat_e = -dx * s_ + dy * c; yaw_e = wrap(self.w.yaw - thyaw)
            g = dict(bin=name, attempt=attempt, lat_m=round(lat_e, 3), along_m=round(dx * c + dy * s_, 3), yaw_deg=round(math.degrees(yaw_e), 2))
            g['ok'] = abs(lat_e) <= GATE_LAT and abs(yaw_e) <= GATE_YAW; st['metrics']['gates'].append(g)
            dec = g['ok']
            if GATE_CAM:
                rg_ = np.random.default_rng([int(self.r.seed), 104729, len(st['metrics']['gates'])]); e_c, seen_c = cam_frames(rg_, CAM_AVG)
                lat_c = lat_e + CAM_BIAS + e_c; yaw_c = yaw_e + float(rg_.normal(0.0, math.radians(0.5)))
                dec = bool(seen_c and abs(lat_c) <= GATE_CAM_TOL and abs(yaw_c) <= GATE_YAW); g.update(lat_cam=round(lat_c, 3), yaw_cam_deg=round(math.degrees(yaw_c), 2), ok_cam=dec)
                self.r.ev('pi', 'pre-grab gate %s on the camera: lateral %.3f m, yaw %.2f deg (truth: %.3f m, %.2f deg, %s)' % ('OK' if dec else 'MISS', lat_c, math.degrees(yaw_c), lat_e, math.degrees(yaw_e), 'inside' if g['ok'] else 'OUTSIDE'))
            else: self.r.ev('pi', 'pre-grab gate %s: lateral %.3f m, yaw %.2f deg (truth)' % ('OK' if g['ok'] else 'MISS', lat_e, math.degrees(yaw_e)))
            if dec: break
            if attempt == 0:   # one re-alignment: forward 0.8 m on the axis, then back to the pre-grab pose
                ca, sa_ = math.cos(hyaw), math.sin(hyaw)
                yield from self.goto_pose(px + 0.8 * ca, py + 0.8 * sa_, hyaw, reverse=False, v=V_MAN)
                yield from self.goto_pose(px, py, hyaw, reverse=True, v=V_REV)
        if not dec:
            self.alert('could not line up on bin %s (pre-grab gate missed twice) - not grabbing' % name)
            st['metrics'].setdefault('refused', []).append(dict(bin=name, why='gate'))
            if FIX_RTH: self.st['plan'] = self.st['plan'][:self.st['i'] + 1] + ([('lane', 8.0, 0.0)] if where != 'home' else []) + [('dock',), ('trip_end',), ('end', 'alert', 'grab refused, back on the dock')]; return
            self.finish('alert', 'grab gate'); return
        # final reverse onto the bin's front wall (camera-guided reversing; stop on the comb ToF = nib at the front wall)
        op['phase'] = 'final'; self.no_pause = True; st['state'] = 'GRAB_DOCK'
        b['engaged'] = True; self.set_known(name, None)
        yield from self.wait(3.0, 'pre-motion warning (beacon, chime)')
        T = BIN_T[b['size']]
        rf_ = np.random.default_rng([int(self.r.seed), 15485863, len(st['metrics']['grabs']) + len(st['metrics'].get('refused', []))])
        cam_err = (CAM_BIAS + float(rf_.normal(0.0, CAM_SIG))) if FINAL_CAM else 0.0; seat_corr = 0.0
        for seat_try in range(2):
            while True:
                # ToF: distance from the comb face to the bin's front wall along the robot axis (truth geometry = sensor)
                c, s_ = math.cos(self.w.yaw), math.sin(self.w.yaw)
                fx = b['x'] + (T['D'] / 2) * math.cos(b['yaw'] + math.pi); fy = b['y'] + (T['D'] / 2) * math.sin(b['yaw'] + math.pi)
                comb = (self.w.x + ROB['comb_x'] * c, self.w.y + ROB['comb_x'] * s_)
                gap = (comb[0] - fx) * c + (comb[1] - fy) * s_
                if gap <= 0.004: break
                v = (min(0.15, V_REV) if R5B else 0.15) if gap > 0.20 else 0.06
                if gap < 0.06: v = 0.03
                # heading hold on the bin axis with camera lateral correction (MuJoCo F9 taper: 10 deg far -> 2 deg near)
                dxb, dyb = self.w.x - b['x'], self.w.y - b['y']; lat_b = -dxb * math.sin(hyaw) + dyb * math.cos(hyaw) + cam_err + seat_corr
                corr = float(np.clip(-1.5 * lat_b, -math.radians(10), math.radians(10))) * (1 if gap > 0.5 else max(0.2, gap / 0.5))
                self.att(wrap(hyaw - corr), -v); yield
            yield from self.rest(0.5)
            dxb, dyb = self.w.x - b['x'], self.w.y - b['y']
            dock = dict(bin=name, lat_mm=round(1000 * (-dxb * math.sin(self.w.yaw) + dyb * math.cos(self.w.yaw)), 1), yaw_deg=round(math.degrees(wrap(self.w.yaw - hyaw)), 2))
            if SEAT <= 0: break
            meas = dock['lat_mm'] / 1000.0 + float(rf_.normal(0.0, SEAT_SIG))
            st['metrics'].setdefault('seat_checks', []).append(dict(bin=name, k=seat_try, meas_mm=round(meas * 1000, 1), true_mm=dock['lat_mm'], ok=bool(abs(meas) <= SEAT)))
            if abs(meas) <= SEAT: break
            self.r.ev('pi', 'seating check: bin %s sits %.0f mm off centre between the legs (limit %.0f mm; truth %.0f mm) - %s' % (name, meas * 1000, SEAT * 1000, dock['lat_mm'], 'pulling out to line up again' if seat_try == 0 else 'not lifting'))
            x_, y_, yaw_ = self.pose(); yield from self.follow([[x_, y_], [x_ + PREGRAB * math.cos(yaw_), y_ + PREGRAB * math.sin(yaw_)]], reverse=False, v=V_REV)
            if seat_try == 1:
                b['engaged'] = False; self.set_known(name, dict(x=b['x'], y=b['y'], yaw=b['yaw'], L=BIN_T[b['size']]['D'], W=BIN_T[b['size']]['W'])); self.no_pause = False
                self.alert('bin %s still sits more than %.0f mm off centre after a second approach - not lifting' % (name, SEAT * 1000))
                st['metrics'].setdefault('refused', []).append(dict(bin=name, why='seating'))
                if FIX_RTH: self.st['plan'] = self.st['plan'][:self.st['i'] + 1] + ([('lane', 8.0, 0.0)] if where != 'home' else []) + [('dock',), ('trip_end',), ('end', 'alert', 'grab refused, back on the dock')]; return
                self.finish('alert', 'grab gate'); return
            seat_corr += meas; yield from self.pivot(hyaw, tol=math.radians(0.8))
        st['state'] = 'LIFT'
        yield from self.wait(3.0, 'pre-motion warning before the lift')
        self.servo(5, 1900); self.w.lift_busy = T_LIFT
        yield from self.wait(T_LIFT, 'comb engage + lift + pad lock (MuJoCo G1 front dock: 90/90)')
        self.servo(6, 1900)
        # bin is now rigid on the comb (self-aligning comb takes the residual lateral offset)
        self.w.carry = name; b['state'] = 'carried'; b['engaged'] = False; self.w.lift_q = 0.239; self.w.pad_on = True
        dock['result'] = 'success (MuJoCo gate)'; st['metrics']['grabs'].append(dock)
        self.r.ev('pi', 'bin %s lifted: comb seated, pad locked, %.0f kg on board' % (name, b['mass']))
        self.no_pause = False; self.st['nofix_t0'] = None

    def op_setdown(self, target_kind, key):
        """place the carried bin: robot drives the bin onto the spot (reverse Hermite at the pads / forward at home),
        lower, pad release, comb out by withdrawing forward through the open tail."""
        st = self.st; op = st['op']; name = self.w.carry
        if name is None and op.get('phase') is None: return
        if target_kind == 'pad': tx, ty, tyaw = self.pad_xy(key)
        else: tx, ty, tyaw = self.home_xy(key)
        if target_kind == 'pad' and op.get('phase') is None and not self.sc.get('pi_fence_bypass'):
            # Pi pre-check: the placed bin and the robot at the hold pose stay >= 0.3 m inside the private boundary
            size = self.w.bins[name]['size']; hx, hy, hyaw = self.hold_pose(tx, ty, tyaw, size)
            P = np.r_[BW.rect_pts(hx, hy, hyaw, ROB['x0'], ROB['x1'], ROB['hw'], 8), BW.rect_pts(tx, ty, tyaw, -BIN_T[size]['D'] / 2, BIN_T[size]['D'] / 2, BIN_T[size]['W'] / 2, 6)]
            m = min(self.S.road_dist(p) for p in P) - self.S.boundary
            st['metrics']['pad_check'] = dict(pad=key, margin_m=round(m, 2))
            if m < 0.3:
                self.alert('drop spot %s is %.2f m from the road verge boundary (< 0.3 m): not placing - please re-draw the pad in the app' % (key, m))
                self.st['plan'] = self.st['plan'][:self.st['i'] + 1] + [('end', 'alert', 'pad outside geofence')]; return
        size = self.w.bins[name]['size']; hx, hy, hyaw = self.hold_pose(tx, ty, tyaw, size)
        if op.get('phase') is None:
            st['state'] = 'PLACE'
            x, y, yaw = self.pose()
            rev = math.cos(wrap(math.atan2(hy - y, hx - x) - yaw)) < 0
            ca, sa_ = math.cos(hyaw), math.sin(hyaw); al = abs((hx - x) * ca + (hy - y) * sa_); lt = abs(-(hx - x) * sa_ + (hy - y) * ca)
            if al > 1.0 and lt < 0.4 * al and abs(wrap(yaw - hyaw)) < math.radians(30):
                path = self.hermite((x, y), yaw, (hx, hy), hyaw, reverse=rev)
                yield from self.follow(path, reverse=rev, v=V_REV if rev else V_MAN, Ld=0.5)
            else:
                yield from self.goto_pose(hx, hy, None, reverse=rev, v=V_REV if rev else V_MAN)
            yield from self.pivot(hyaw, tol=math.radians(1.0))
            op['phase'] = 'lower'
        if op.get('phase') == 'lower':
            self.no_pause = True; st['state'] = 'SETDOWN'
            yield from self.wait(3.0, 'pre-motion warning before the set-down')
            self.servo(6, 1100); self.servo(5, 1100); self.w.lift_busy = T_SETDOWN
            yield from self.wait(T_SETDOWN, 'lower bin + pad release')
            b = self.w.bins[name]; bx, by, byaw = self.w.carried_xy(); b.update(x=bx, y=by, yaw=byaw, state='up', engaged=True)
            self.w.carry = None; self.w.lift_q = 0.0; self.w.pad_on = False
            err = math.hypot(bx - tx, by - ty); herr = abs(math.degrees(wrap(byaw - tyaw)))
            st['metrics']['placements'].append(dict(bin=name, where=target_kind + ':' + key, err_m=round(err, 3), handle_err_deg=round(herr, 2), clock=self.clock_str(), t=round(self.w.t, 1)))
            self.r.ev('pi', 'bin %s set down at %s: %.3f m / %.1f deg from the spot (truth)' % (name, key, err, herr))
            op['phase'] = 'withdraw'
        if op.get('phase') == 'withdraw':
            st['state'] = 'WITHDRAW'; b = self.w.bins[name]
            x, y, yaw = self.pose(); dist = op.get('wd', 1.3 if target_kind == 'pad' else 2.0)
            yield from self.follow([[x, y], [x + dist * math.cos(yaw), y + dist * math.sin(yaw)]], reverse=False, v=V_REV)
            b['engaged'] = False; self.set_known(name, dict(x=b['x'], y=b['y'], yaw=b['yaw'], L=BIN_T[b['size']]['D'], W=BIN_T[b['size']]['W']))
            yield from self.wait(T_PHOTO, 'photo of the placed bin (app)'); self.no_pause = False

    def op_pivot_safe(self, which, step=0.5, maxrun=3.0):
        """pivot to face down/up-lane; if the map / known-object sweep is tight, first move forward along the current heading."""
        s, l = self.s_lat(); h = self.S.lane.heading(s); tgt = h if which == 'down' else wrap(h + math.pi)
        x, y, yaw = self.pose(); run = 0.0; self.st['state'] = 'PIVOT' + ('_LOADED' if self.w.carry else '')
        while run <= maxrun:
            xx, yy = x + run * math.cos(yaw), y + run * math.sin(yaw)
            c = self.sweep_clear(self.pivot_poses(xx, yy, yaw, tgt), True)
            if c >= 0.30: break
            run += step
        if run > 0: yield from self.follow([[x, y], [x + run * math.cos(yaw), y + run * math.sin(yaw)]], v=V_MAN)
        yield from self.pivot(tgt)

    def op_dock(self):
        """drive to the dock pre-pose (1.0 m out, facing up-lane) and forward onto the dock contacts at the nose."""
        st = self.st; st['state'] = 'DOCKING'; S = self.S; d = self.sc['dock']
        dx, dy, dh = S.pose(d['s'], d['lat'], 0.0); ryaw = wrap(dh + math.pi)
        ax, ay = dx - (ROB['x1'] + 0.02) * math.cos(ryaw), dy - (ROB['x1'] + 0.02) * math.sin(ryaw)     # axle when docked
        px, py = ax - 1.0 * math.cos(ryaw), ay - 1.0 * math.sin(ryaw)
        x, y, yaw = self.pose()
        if math.hypot(px - x, py - y) > 0.05: yield from self.goto_pose(px, py, ryaw, reverse=False)
        else: yield from self.pivot(ryaw)
        self.set_known('dock', None)
        x, y, yaw = self.pose(); yield from self.follow([[x, y], [ax, ay]], v=V_DOCK, tol=0.02)
        self.set_known('dock', self.dock_box())
        st['state'] = 'DOCKED'; yield from self.wait(5.0, 'dock contacts closed, charging')
        st['state'] = 'DOCKED'
    def dock_box(self):
        d = self.sc['dock']; dx, dy, dh = self.S.pose(d['s'], d['lat'], 0.0)
        return dict(x=dx - 0.2 * math.cos(dh + math.pi), y=dy - 0.2 * math.sin(dh + math.pi), yaw=dh, L=0.4, W=0.7)

    def op_bypass_drive(self, s_goal):
        """s12b only: Pi geofence check bypassed - drive the lane centre-line straight on toward the road (bug injection)."""
        st = self.st; st['state'] = 'BYPASS'; self.no_pause = True
        while True:
            x, y, yaw = self.pose(); s, l = self.S.lane.project(np.array([x, y]))
            p = self.S.lane.point(s + 2.0, 0.0); self.att(math.atan2(p[1] - y, p[0] - x), 0.5); yield
            if self.mode == 'HOLD': break
            if s > s_goal: break
        yield from self.rest(1.0)
