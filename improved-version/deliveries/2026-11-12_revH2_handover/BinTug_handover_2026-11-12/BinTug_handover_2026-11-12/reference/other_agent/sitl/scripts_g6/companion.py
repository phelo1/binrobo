"""Companion computer (Pi Zero 2 W) state machine for the bin-tug, talking MAVLink to the real ArduPilot Rover firmware.
 - Lane legs: uploads a waypoint mission along the surveyed lane and runs it in AUTO (firmware navigation).
 - Close manoeuvres (view / dock / U-turn / nudge / park): MANUAL + RC_CHANNELS_OVERRIDE (firmware does the skid-steer mixing).
 - Sensors it uses: firmware EKF pose (GLOBAL_POSITION_INT, ATTITUDE), GPS_RAW_INT fix type, its own LD06 scan,
   the rear camera image (real OpenCV ArUco + PnP), the seat and bumper switches; hook via MAV_CMD_DO_SET_SERVO 5.
 - Policies: lidar stop for unmapped objects in the path (resume after 3 s clear); static object -> detour mission inside
   the hedges or stop + alert; RTK float -> 0.3 m/s; no fix -> dead-reckon <= 8 m then hold 60 s then stop + alert;
   bin recovery: drive round to the handle side if there is room -> orbit-nudge 90 deg at a time (room + hedge + geofence
   check) -> re-dock once -> 4G alert + photo and go home.
Generator-based: every `yield` hands control back to the lock-step loop for one 0.1 s tick.
"""
import math, os, numpy as np, cv2
from pymavlink import mavutil
from world import TUG, BIN, ll2xy, xy2ll, wrap
from scene import detect, tag_to_world, DOCK_OFF, M_BIN_FULL, M_BIN_EMPTY, seg_dist, id0_of, owner_of, face_of, OUR_ID0, PACK_WH_NOM, pack_cold_factor
import scenarios as SC
import g4_features as G4
from g4_features import kl_lat, KL_ZONE, DropLayout, BinCalendar, RouteFile, DropAreas, _pip
from g6_features import hitch_gov, CorridorFit
import g6_features as G6
from world import HITCH_CAP_DEG
STEER_K = 0.43              # steer command per rad/s of tug yaw rate (skid-steer mix, as used by uturn() since G3)
import json

MODES = {0: 'MANUAL', 1: 'ACRO', 3: 'STEERING', 4: 'HOLD', 5: 'LOITER', 10: 'AUTO', 11: 'RTL', 12: 'SMART_RTL', 15: 'GUIDED', 16: 'INITIALISING'}
MNUM = {v: k for k, v in MODES.items()}
_FO = {0: 0.0, 1: math.pi, 2: math.pi / 2, 3: -math.pi / 2}; _FH = {0: BIN['d'] / 2, 1: BIN['d'] / 2, 2: BIN['w'] / 2, 3: BIN['w'] / 2}
class _ByFace(dict):        # Rev G3: tag ID -> face (each bin carries one 4-tag set, id0 + face)
    def __init__(self, base): super().__init__(); self.b = base
    def __getitem__(self, tag): return self.b[face_of(tag)]
FACE_OFF = _ByFace(_FO)     # face normal yaw - bin yaw
FACE_HALF = _ByFace(_FH)
TRIP_WH = 47.0              # Rev G3: pack energy budget per bin trip (one drop or one pickup incl. lights at night, SIM ~41-44 Wh) + margin
RESERVE = 0.10              # Rev G3: never plan below 10 % state of charge
SLEEP_W = 1.0               # Rev G3: RTC sleep load (Pi off, 4G + RTK off, FC + RTC + BMS) - ASSUMED
STANDBY_W = 9.0             # awake, idle (the old always-on standby)
RADAR_W = 1.0               # Rev G4: two 24 GHz radar modules (~0.5 W each, ASSUMED)
AUDIO_W = dict(off=0.0, idle=0.1, announce=2.5, ringing=0.3, call=2.0)    # Rev G4: I2S amp + mic + Opus encode on the Pi (ASSUMED)
YARD_UTURN = dict(ds=-1.0, dlat=5.8, R=float(os.environ.get('BT_YARD_R', '2.9')))   # G6 s4: env BT_YARD_R = study only (default 2.9)
# Rev G6: yard U-turn start = slot s-1 m, lat slot+5.8 m; R 2.9 m (28 deg kingpin stop)
UTURN_G4 = dict(start_from_end=11.5, lat=-1.5, R=1.45, stop_early=0.2, line=1.35)   # Rev G4: mouth U-turn moved fully into the bell-mouth (no hedge overlap)
VSTOP = dict(r_stop=5.5, closing=0.3, ttc_s=3.0, r_ttc=12.0, r_clear=8.0, clear_s=3.0, creep_after_s=10.0, creep_v=0.3, max_hold_s=300.0,
             snr_vehicle=18.0)      # Rev G4 vehicle-approach stop thresholds
CLIPS = {'vehicle': 'Bin robot stopped - please pass slowly', 'pinch': 'Please stand clear of the bin robot',
         'centre_gap': 'Please step away from behind the bin robot', 'hello': 'Hello - this is the bin robot'}
def clock_str(m):
    d = int(math.floor(m / 1440.0)); mm = m - 1440 * d
    return 'D%s %02d:%02d' % (('%+d' % d) if d else '0', int(mm // 60), int(mm % 60))
def parse_clock(txt):
    """'D-1 18:00' / 'D0 06:00' / '08:00' -> minutes from 00:00 on collection day (D0)."""
    if txt is None: return None
    d = 0; t = txt
    if txt.startswith('D'): ds, t = txt.split(); d = int(ds[1:])
    return 1440 * d + int(t[:2]) * 60 + int(t[3:5])


class _Abort(Exception): pass
# Rev G3: detection sweep (out/detect_sweep.json) shows the 3 W rear work lamp does not extend the night tag range (IR + retro
# tags dominate: 2.0-3.8 m with or without it), so it stays OFF while viewing/docking and is used for the alert photo + warnings only.
LAMP_STATES = ()


def l_shape_yaw(Q):
    """Rev G: box axis (deg, mod 90) from a lidar cluster by the L-shape closeness criterion (Zhang et al. 2017): for each
    trial angle, rotate the points and score how tightly they hug the two nearest bounding-box edges. minAreaRect alone
    was ~20-40 deg off when only one face plus a corner was seen (cold-eye review / HANDOVER s.9 4d)."""
    best = (1e9, 0.0)
    for th in np.radians(np.arange(0.0, 90.0, 1.0)):
        c, s_ = math.cos(th), math.sin(th)
        u = Q[:, 0] * c + Q[:, 1] * s_; v = -Q[:, 0] * s_ + Q[:, 1] * c
        du = np.minimum(u - u.min(), u.max() - u); dv = np.minimum(v - v.min(), v.max() - v)
        cost = np.sum(np.minimum(du, dv) ** 2)
        if cost < best[0]: best = (cost, th)
    return math.degrees(best[1])


class Companion:
    def __init__(self, runner, sc):
        self.r = runner; self.w = runner.w; self.sc = sc; self.S = sc['site']
        self.state = 'BOOT'; self.mode = '?'; self.armed = False; self.leg = 'boot'
        self.ekf_xy = None; self.yaw = None; self.vel = 0.0; self.fix = 0
        self.hook_pwm = 1100; self.done = False; self.result = 'running'; self.outcome_text = ''
        self.alert_flag = None; self.alerts = []; self.stops = []; self.metrics = {}; self.leg_time = {}
        self.last_det_summary = None; self.speed_cmd = 0.0; self.upl = None; self.reached = -1; self.mission_n = 0
        self.gen = self.main(); self.ignore_ids = set(); self.nudges = 0; self.docks = 0
        self.dr = None; self.base_speed = 0.5; self._rc = None; self._blk = None; self.obst_pts = []
        # Rev G: companion heartbeat (firmware GCS failsafe), crash-injection test hook, lights, pre-motion warning
        self.crashed = False; self._hb_t = -9.0; self._crash_cfg = sc.get('crash'); self._crash_enter = None
        self.warn = False; self.lights = dict(beacon=False, head=False, tail=False, ir=False, work=False)
        # Rev G3: multi-bin target, mission clock (bye-law timing), sleep/RTC, stop-chain monitor, crossbeam check, release handling
        self.target = 'black'; self.mission = sc.get('mission', 'drop' if 'house_grab' in sc['plan'] else 'pickup')
        self.clock0 = parse_clock(sc.get('clock')); self.skip_s = 0.0; self.sleeping = False; self.sleep_log = []
        self.chain_seen = 0; self.chain_clear_t = None; self.bins_done = []; self.bins_left = []
        self.first_motion_clock = None; self.release_hold = None
        # Rev G4: plan is a mutable list (calendar expands it), keep-left flag, vehicle-stop state, audio, layout, route (teach/repeat)
        self.plan = list(sc['plan']); self.kl_active = False; self.vstop_state = None; self.vstops = []
        self.audio = dict(state='idle', log=[], until=0.0, call=None); self._owner_call = sc.get('owner_call')
        self.layout = DropLayout(sc.get('layout')) ; self.route = None; self.home_override = None; self.drop_override = None
        self.hitch_gov_on = sc.get('hitch_gov', True); self.hitch_events = []; self.lat_target_now = None   # Rev G6
        self.keep_left = sc.get('keep_left', True); self.slot_exempt_log = []; self.route_mode = False; self.pad_for = sc.get('pad_for')
        if sc.get('pre_done'): self.bins_done = list(sc['pre_done']); self._first_trip_t = 0.0
        if sc.get('placed0'): self.placed = [np.array(p_, float) for p_ in sc['placed0']]      # Rev G6: bins already on the pad
        # Rev G4 g) adaptive drop spot: allowed areas + keep-outs (installed into the site geofence), drop log, app notifications
        self.adaptive = sc.get('adaptive', True)
        self.areas = DropAreas(self.S, sc.get('drop_areas'), sc.get('keepouts_extra', ())).install()
        self.app_notes = []; self.drop_log = {}; self.home_target = None; self._home_check = None; self._seek_prior = None
        if sc.get('route_file'):
            self.route = RouteFile.load(sc['route_file']); self.home_override = self.route['home_pose']; self.drop_override = self.route['drop_pose']
    # ---------------- MAVLink in ----------------
    def on_msg(self, m):
        t = m.get_type()
        if t == 'HEARTBEAT' and m.get_srcSystem() == 1 and m.type != mavutil.mavlink.MAV_TYPE_GCS:
            self.mode = MODES.get(m.custom_mode, str(m.custom_mode)); self.armed = bool(m.base_mode & 128)
        elif t == 'GLOBAL_POSITION_INT':
            if m.lat != 0:
                self.ekf_xy = list(map(lambda q: round(q, 3), ll2xy(m.lat / 1e7, m.lon / 1e7))); self.vel = math.hypot(m.vx, m.vy) / 100.0
        elif t == 'ATTITUDE': self.yaw = wrap(math.pi / 2 - m.yaw); self.yawspeed = m.yawspeed; self._yaw_t = self.w.t
        elif t == 'GPS_RAW_INT': self.fix = m.fix_type
        elif t in ('MISSION_REQUEST', 'MISSION_REQUEST_INT') and self.upl is not None: self.send_item(m.seq)
        elif t == 'MISSION_ACK' and self.upl is not None: self.upl['acked'] = m.type
        elif t == 'MISSION_ITEM_REACHED': self.reached = m.seq

    # ---------------- MAVLink out ----------------
    @property
    def mav(self): return self.r.gcs.mav

    def set_mode(self, name):
        if name == 'AUTO': self._auto_cmd_t = self.w.t
        # Rev G6: on towing legs the Pi follows the planned path itself (MANUAL + RC override, hitch-governed pure pursuit);
        # 'AUTO' then means 'Pi path follower on'. Every firmware failsafe (GCS heartbeat, battery, EKF) still acts in MANUAL.
        self.following = (name == 'AUTO' and getattr(self, 'pi_follow', False))
        if self.following: name = 'MANUAL'; self._fol_t = self.w.t
        self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 1, MNUM[name], 0, 0, 0, 0, 0)

    def leg_auto(self):
        """True while the lane leg is under path following (firmware AUTO, or the Pi follower on towing legs)."""
        return self.mode == 'AUTO' or (getattr(self, 'following', False) and self.mode == 'MANUAL')

    def follow_step(self):
        """Rev G6 Pi path follower (towing legs): pure pursuit on the planned smoothed path (cur_pts), look-ahead 1.6 m + 0.8 s,
        tug yaw rate bounded by the hitch governor (drive()). Speed = base_speed (0.5; 0.3 in RTK float / narrowings), 0.3 when the
        path bends away by > 20 deg. Marks the leg reached when within 0.6 m of the last point (or past it)."""
        P = getattr(self, 'cur_pts', None)
        if not P or self.mode != 'MANUAL': return
        x, y, yaw = self.pose(); p = np.array([x, y]); i0 = getattr(self, '_fi', 0); best = None
        for i in range(max(0, i0 - 1), min(len(P) - 1, i0 + 8)):
            a = np.array(P[i]); b = np.array(P[i + 1]); ab = b - a; L2 = float(ab @ ab) or 1e-9
            u = float(np.clip((p - a) @ ab / L2, 0.0, 1.0)); d = float(np.linalg.norm(a + u * ab - p))
            if best is None or d < best[0]: best = (d, i, u)
        if best is None: return
        _, i, u = best; self._fi = i
        v = float(self.base_speed); Ld = 1.6 + 0.8 * v
        rem = Ld; q = np.array(P[i]) + u * (np.array(P[i + 1]) - np.array(P[i])); j = i; tgt = None
        while j < len(P) - 1:
            seg = np.array(P[j + 1]) - q; ls = float(np.linalg.norm(seg))
            if ls >= rem: tgt = q + seg * (rem / max(ls, 1e-9)); break
            rem -= ls; q = np.array(P[j + 1]); j += 1
        last = np.array(P[-1]); d_end = float(np.linalg.norm(last - p))
        if tgt is None: tgt = last
        hl = np.array(P[-1]) - np.array(P[-2]) if len(P) > 1 else np.array([math.cos(yaw), math.sin(yaw)])
        if d_end < 0.6 or (i >= len(P) - 2 and float((p - last) @ hl) > 0): self.reached = self.mission_n - 1; self.stop(); return
        al = wrap(math.atan2(tgt[1] - y, tgt[0] - x) - yaw)
        if abs(al) > math.radians(20): v = min(v, 0.3)
        w_cmd = float(np.clip(2.0 * v * math.sin(al) / Ld, -0.6, 0.6))
        self.drive(-STEER_K * w_cmd, self.thr_ctl(v))
    def arm(self): self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

    def servo(self, pwm):
        self.hook_pwm = pwm
        self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0, 5, pwm, 0, 0, 0, 0, 0)

    def change_speed(self, v):
        self.speed_cmd = v
        self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 1, v, -1, 0, 0, 0, 0)

    def rc(self, steer, thr):
        """steer: +1 = turn right (clockwise); thr: -1..1"""
        s = int(1500 + 500 * float(np.clip(steer, -1, 1))); th = int(1500 + 500 * float(np.clip(thr, -1, 1)))
        self.mav.rc_channels_override_send(1, 1, s, 0, th, 0, 0, 0, 0, 0)

    def rc_release(self): self.mav.rc_channels_override_send(1, 1, 0, 0, 0, 0, 0, 0, 0, 0)

    def upload(self, pts):
        items = [pts[0]] + list(pts)           # seq 0 = home placeholder
        self.upl = dict(items=items, acked=None); self.mission_n = len(items); self.reached = -1
        self.mav.mission_count_send(1, 1, len(items), 0)

    def send_item(self, seq):
        it = self.upl['items'][seq]; lat, lon = xy2ll(*it)
        self.mav.mission_item_int_send(1, 1, seq, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                                       0, 1, 0, 0, 0, 0, int(lat * 1e7), int(lon * 1e7), 0, 0)

    # ---------------- helpers ----------------
    def ev(self, text, **kw): self.r.ev('comp', text, **kw)

    def pose(self):
        if self.dr is not None: return self.dr[0], self.dr[1], self.yaw
        return self.ekf_xy[0], self.ekf_xy[1], self.yaw

    def s_lat(self):
        x, y, _ = self.pose(); return self.S.lane.project(np.array([x, y]))

    def wait(self, sec):
        t0 = self.w.t
        while self.w.t - t0 < sec: yield

    def clock(self):
        """Mission clock (minutes from 00:00 on collection day), including RTC-sleep time skipped by the simulation."""
        return None if self.clock0 is None else self.clock0 + (self.w.t + self.skip_s) / 60.0

    def tick(self, t):
        if self.done: return
        if t - self._hb_t >= 1.0 and not self.sleeping:   # 1 Hz heartbeat: FS_GCS_ENABLE makes the firmware HOLD if the Pi goes silent
            self._hb_t = t
            self.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
        if self._crash_cfg is not None and self._check_crash(t): return
        es = self.sc.get('estop')         # Rev G3 test hook (ported): a person presses the E-stop at lane station es[1]
        if es and not self.w.estop and self.leg == es[0] and self.ekf_xy is not None and self.s_lat()[0] >= es[1]:
            self.w.press_estop(); self.r.ev('hw', 'E-STOP pressed by a person (hard-wired chain opens)')
        self.chain_monitor()
        if self.first_motion_clock is None and abs(self.w.v) > 0.05 and self.clock0 is not None:
            self.first_motion_clock = self.clock(); self.metrics['first_motion_clock'] = clock_str(self.first_motion_clock)
        try: next(self.gen)
        except StopIteration: self.done = True
        if self.armed and self.mode == 'MANUAL' and self._rc is not None and not self.sleeping: self.rc(*self._rc)
        self.audio_tick()
        self.update_lights()

    # ---------------- Rev G3: hard-wired stop chain monitor (ported from revG_alt; the Pi only reads it / requests a reset) ----------------
    def chain_monitor(self):
        w = self.w
        if len(w.chain_trips) > self.chain_seen:
            for tr in w.chain_trips[self.chain_seen:]:
                self.r.ev('hw', 'stop chain OPEN: %s at %.2f m/s -> motor enable cut, spring brakes on' % (tr['reason'], tr['v']))
            self.chain_seen = len(w.chain_trips)
        if not w.chain_ok and not w.estop:
            if not w.bumper:
                self.chain_clear_t = self.chain_clear_t or w.t
                # manoeuvre contacts (docking, nudging, viewing) may be reset by the Pi after 1 s clear; a contact in a lane leg
                # is handled by auto_leg (stop + alert) and is never reset automatically
                if w.t - self.chain_clear_t > 1.0 and self.state.startswith(('DOCK', 'NUDGE', 'REDOCK', 'VIEW', 'TO_', 'PLACE', 'RELEASE', 'GRAB', 'PARK', 'REPLAN', 'SEEK')):
                    w.chain_reset(); self.chain_clear_t = None; self.r.ev('hw', 'bump strip clear for 1 s -> Pi requests safety-relay reset')
            else: self.chain_clear_t = None

    # ---------------- Rev G: companion-crash test (Pi hangs: no heartbeat, no RC override, no lidar feed) ----------------
    def _check_crash(self, t):
        pre, delay = self._crash_cfg
        if self._crash_enter is None and self.state.startswith(pre): self._crash_enter = t
        if self._crash_enter is not None and t - self._crash_enter >= delay:
            self.crashed = True; self.crash = dict(t=round(t, 1), state=self.state, mode=self.mode, odo=self.w.odo, v=round(self.w.v, 2),
                                                    fs=self.sc.get('fs_label', 'FS_GCS_ENABLE 1'))
            self.ev('*** COMPANION CRASH INJECTED in %s (mode %s, v=%.2f m/s): heartbeat, RC override and lidar feed stop' % (self.state, self.mode, self.w.v))
            self.state = 'CRASHED'; return True
        return False

    def crash_monitor(self, t):
        """Runs instead of tick() after the injected crash: observes the firmware only (evaluation, not control)."""
        c = self.crash
        if 'hold_t' not in c and self.mode == 'HOLD':
            c['hold_t'] = round(t - c['t'], 2); self.ev('firmware switched to HOLD %.2f s after the crash' % c['hold_t'])
        if 'stop_t' not in c and abs(self.w.v) < 0.02:
            c['stop_t'] = round(t - c['t'], 2); c['stop_dist_m'] = round(self.w.odo - c['odo'], 2)
        if t - c['t'] >= 40.0:
            c['dist_40s_m'] = round(self.w.odo - c['odo'], 2); c['mode_40s'] = self.mode
            c.pop('odo', None); self.metrics['crash'] = c
            ok = c.get('hold_t', 99) <= 2.5 and 'stop_t' in c and c['dist_40s_m'] < 2.0      # pass: HOLD <= 2.5 s, < 2 m rolled
            self.finish('pass' if ok else 'fail', ('tug stopped %.1f s / %.2f m after the companion crash (mode %s)' % (c['stop_t'], c['stop_dist_m'], self.mode)) if 'stop_t' in c
                        else 'tug DID NOT STOP: %.1f m driven in 40 s after the companion crash (mode %s)' % (c['dist_40s_m'], self.mode))

    # ---------------- Rev G: lights ----------------
    LIGHT_W = dict(beacon=2.0, head=6.0, tail=1.0, ir=5.0, work=3.0)

    def update_lights(self):
        night = self.w.night; st = self.state; moving = abs(self.w.v) > 0.02
        active = st not in ('DOCKED', 'DONE', 'BOOT')
        L = self.lights
        L['beacon'] = bool(active and (moving or self.warn or st in ('GRAB', 'RELEASE') or self.vstop_state is not None))   # amber, flashing (G4: also in a vehicle stop)
        L['head'] = bool(night and active and (moving or st.startswith(('SEEK', 'VIEW'))))          # 2 x 3 W white, dipped, forward
        L['tail'] = bool(night and active)                                                          # red markers: mast top + rear frame
        L['ir'] = bool(night and st.startswith(('VIEW', 'DOCK', 'SEEK', 'NUDGE', 'REDOCK', 'PARK')))  # 850 nm on the rear camera
        L['work'] = bool(night and (st in ('GRAB', 'RELEASE') or self.warn or st.startswith(LAMP_STATES)))   # white rear flood
        self.w.lamp_work = L['work']

    def lights_w(self): return sum(self.LIGHT_W[k] for k, v in self.lights.items() if v)

    def lights_str(self): return ''.join(k[0].upper() for k, v in self.lights.items() if v)

    def pre_motion(self, what):
        """Rev G pinch-point rule: beacon + work light flash 3 s before any actuator motion, and the lidar must see nothing
        unmapped within 1.5 m (rear hitch sector excluded: occluded by the bin). Waits up to 20 s for the zone to clear."""
        self.warn = True; t0 = self.w.t; clear_since = None; self.update_lights()
        while True:
            yield
            busy = self.pinch_busy()                 # Rev G4: same 1.5 m rule + adjacent programmed bin slots exempt (pinch_eval)
            if not busy: clear_since = clear_since or self.w.t
            else: clear_since = None
            if clear_since is not None and self.w.t - t0 >= 3.0 and self.w.t - clear_since >= 1.0: break
            if self.w.t - t0 > 20.0:
                self.warn = False; self.announce('pinch')
                self.alert('%s refused: something within 1.5 m of the tug for 20 s' % what); return False
        self.warn = False; self.metrics['pre_motion_checks'] = self.metrics.get('pre_motion_checks', 0) + 1
        return True

    def drive(self, steer, thr):
        if self.w.attached and self.hitch_gov_on:     # Rev G6: hitch governor on every MANUAL manoeuvre with the bin in tow
            phi = math.radians(self.kingpin_deg()); v = self.w.v           # kingpin encoder + wheel encoders (ASSUMED sensors)
            w_cmd = -steer / STEER_K
            w_ok = hitch_gov(w_cmd, v, phi)
            if abs(w_ok - w_cmd) > 1e-3:
                steer = -STEER_K * w_ok; self._gov_n = getattr(self, '_gov_n', 0) + 1
        self._rc = (steer, thr)

    def yaw_now(self):
        """Rev G6: autopilot yaw extrapolated with its yaw rate to now (ATTITUDE arrives at 20 Hz; odometry runs at the physics rate)."""
        if self.yaw is None: return None
        return wrap(self.yaw - getattr(self, 'yawspeed', 0.0) * min(0.2, self.w.t - getattr(self, '_yaw_t', self.w.t)))

    def kingpin_deg(self):
        """Rev G6: kingpin angle sensor (tug yaw - bin yaw), magnetic encoder, +/-0.5 deg noise (ASSUMED part, see report)."""
        return self.w.hitch + float(self.w.rng.normal(0, 0.5))

    def kl_target(self):
        """Rev G6: (travel-left lane side, keep-left lateral) while keep-left is active, for the corridor fusion; else None."""
        if not self.kl_active: self.lat_target_now = None; return None
        sg = getattr(self, '_leg_sgn', 1); t = kl_lat(self.S.lane.width, sg)
        pl = self.plan_lat(self.s_lat()[0])          # G6: the planned (smoothed, bend-centred) line, not the nominal keep-left lat
        if pl is not None: t = pl
        f = getattr(self.r, 'fus', None); off = f.lat_offset if f is not None else 0.0
        # G6 fix: the commanded TRUE lateral is (keep-left target - the narrowing reference offset the fusion adds to the forwarded
        # position) whether or not the narrowing flag is still set: the offset decays at a bounded rate after a narrowing, so the
        # old 'narrow-only' rule made the logged target jump back to keep-left while the tug was (correctly) still easing over.
        self.lat_target_now = round(t - off, 3)
        return (sg, t)

    def hitch_guard(self, leg):
        """Rev G6: AUTO legs with the bin in tow. The autopilot does not know the hitch angle, so the Pi watches the kingpin encoder:
        |phi| > cap - 5 deg -> take over (MANUAL) and STEER THE TUG BACK ONTO THE BIN HEADING at 0.2 m/s (yaw rate -K*phi, so phi decays
        in ~1 s with almost no lateral drift: the bin is near the lane heading), until |phi| < 6 deg (max 2.0 m / 15 s), stopping if the
        hedge face comes within 0.25 m; then resume AUTO at a waypoint >= 5 m ahead so the re-join is gentle.
        G6 v1 drove straight on instead: with the tug 20-28 deg off the lane that moved it ~1 m sideways per event and the re-join
        swung the hitch back to the stop (limit cycle, s25a hedge touch at s=71)."""
        if not self.w.attached or self.mode != 'AUTO': return None
        phi = self.kingpin_deg()
        if abs(phi) < HITCH_CAP_DEG - 5.0: return None
        st0 = self.state; self.state = 'HITCH_GUARD'; self.set_mode('MANUAL'); x0, y0, _ = self.pose(); t0 = self.w.t
        ev = dict(t=round(self.w.t, 1), leg=leg, phi_deg=round(phi, 1), s=round(self.s_lat()[0], 1))
        lat_drift = None
        while True:
            yield
            phi = self.kingpin_deg(); x, y, _ = self.pose()
            if abs(phi) < 6.0 or math.hypot(x - x0, y - y0) > 2.0 or self.w.t - t0 > 15: break
            w_ = float(np.clip(-1.2 * math.radians(phi), -0.6, 0.6))           # tug yaw rate towards the bin heading
            w_ = hitch_gov(w_, self.w.v, math.radians(phi))
            self.drive(-STEER_K * w_, self.thr_ctl(0.2))
        # Rev G6 v3 phase 2 - REJOIN under the Pi's governed steering (not AUTO from standstill: the autopilot then turns hard at low
        # speed, where the bin cannot follow, and the guard fired again - 15 events in a row in the yard hairpin, s1 v2).
        # Pure pursuit to the planned path 2.5 m ahead at 0.3 m/s, yaw rate bounded by the hitch governor, until on the path heading.
        t1 = self.w.t
        yield from self.rejoin()
        ev.update(rejoin_s=round(self.w.t - t1, 1))
        ev.update(dur_s=round(self.w.t - t0, 1), end_phi=round(self.kingpin_deg(), 1), moved_m=round(math.hypot(x - x0, y - y0), 2)); self.hitch_events.append(ev)
        self.ev('hitch guard: kingpin %.0f deg in AUTO -> onto the bin heading + governed re-join (%.1f s), resume AUTO' % (ev['phi_deg'], ev['dur_s']))
        self.mav.mission_set_current_send(1, 1, self.next_wp_ahead(getattr(self, '_leg_sgn', 1), margin=2.0))
        self.set_mode('AUTO'); self.state = st0; return 'resumed'

    def rejoin(self, v=0.3):
        """Rev G6: governed re-join of the planned AUTO path with the bin in tow (MANUAL, the Pi's steering): pure pursuit to the path
        2.5 m ahead, tug yaw rate bounded by the hitch governor, until on the path heading with |phi| < 8 deg (max 6 m / 30 s)."""
        x0, y0, _ = self.pose(); t0 = self.w.t; sgn = getattr(self, '_leg_sgn', 1); pts = getattr(self, 'cur_pts', None) or []
        while pts:
            yield
            x, y, yaw = self.pose(); s_n = self.s_lat()[0]
            ahead = [p_ for p_ in pts if sgn * (self.S.lane.project(np.array(p_))[0] - s_n) > 2.5]
            if not ahead: break
            tx, ty = ahead[0]; e = wrap(math.atan2(ty - y, tx - x) - yaw)
            nxt = ahead[1] if len(ahead) > 1 else ahead[0]; eh = wrap(math.atan2(nxt[1] - ty, nxt[0] - tx) - yaw) if len(ahead) > 1 else e
            phi = self.kingpin_deg()
            if (abs(e) < math.radians(8) and abs(phi) < 8.0) or math.hypot(x - x0, y - y0) > 4.0 or self.w.t - t0 > 20: break
            w_ = hitch_gov(float(np.clip(1.2 * e, -0.5, 0.5)), self.w.v, math.radians(phi))
            self.drive(-STEER_K * w_, self.thr_ctl(v))

    def stop(self): self._rc = (0.0, 0.0)

    def ahead(self, d):
        x, y, yaw = self.pose(); return x + d * math.cos(yaw), y + d * math.sin(yaw)

    # ---------------- top level ----------------
    def main(self):
        try:
            i_step = 0
            while i_step < len(self.plan):
                step = self.plan[i_step]; i_step += 1
                name = step if isinstance(step, str) else step[0]
                t0 = self.w.t
                if name == 'boot': yield from self.boot()
                elif name == 'auto':
                    _, s0, s1, lat, leg = step
                    ok = yield from self.auto_leg(s0, s1, lat, leg)
                    if ok == 'stopped': self.finish('stopped', self.outcome_text or 'stopped safely'); return
                elif name == 'house_grab': yield from self.house_grab()
                elif name == 'uturn_mouth':
                    pa = (self.pad_for or {}).get(self.target, 'A')
                    if self.adaptive and self.w.attached and pa == 'A' and not self.drop_override:     # Rev G4 g): is spot A clear before turning into it?
                        vA = yield from self.slot_check(self.layout.bin_pose(self.S, 'A'))
                        self.metrics.setdefault('adaptive_slot', []).append(dict(t=round(self.w.t, 1), slot='A', bin=self.target, primary_check=vA, chosen='primary' if vA['clear'] else None, n_alts=0))
                        if not vA['clear']:
                            self.set_mode('HOLD'); self.alert('mouth drop spot A blocked (%d occluded samples) - U-turn not attempted, holding with the bin' % vA['occl'])
                            self.finish('alert', 'spot A blocked -> holding bin + alert'); return
                    if self.sc.get('uturn_g4', True):
                        yield from self.uturn(+1, UTURN_G4['R'], 'uturn_mouth', line_lat=self.drop_override['lat'] if self.drop_override else UTURN_G4['line'])
                    else: yield from self.uturn(+1, 2.0, 'uturn_mouth')
                elif name == 'drop_out':       # Rev G6: handles-out drop (no mouth U-turn with the bin: infeasible at the 28 deg kingpin stop)
                    ok = yield from self.drop_out(step[1])
                    if not ok: self.finish('alert', self.outcome_text); return
                elif name in ('release_mouth', 'release_pad'):
                    ok = yield from (self.release('release_mouth') if name == 'release_mouth' else self.release_pad(step[1]))
                    if not ok:       # Rev G3 (F4/F2): bin still hooked -> the tug stays holding on the pad, owner alerted
                        self.finish('alert', self.outcome_text); return
                elif name == 'seek':
                    res = yield from self.seek()
                    if res != 'grabbed':
                        yield from self.go_home(); return
                elif name == 'uturn_yard':
                    hb = self.home_target or self.home_override or SC.HOME_SPOTS.get(self.target, SC.HOUSE_BIN)
                    # Rev G6: with a 28 deg kingpin stop the towed bin needs R >= ~3 m; the U-turn starts at slot s-1 m, lat slot+5.8 m
                    yield from self.uturn(+1, YARD_UTURN['R'] if HITCH_CAP_DEG < 45 else 2.0, 'uturn_yard', line_lat=hb['lat'] if self.sc.get('uturn_g4', True) else None)
                    if self.result != 'running': return
                elif name == 'place_house': yield from self.place_house()
                elif name == 'park': yield from self.park()
                elif name == 'junction_wait':
                    ok = yield from self.junction_wait()
                    if ok == 'stopped':
                        if self.w.attached: self.set_mode('HOLD'); self.finish('alert', self.outcome_text + ' (holding at the wait point with the bin)'); return
                        yield from self.go_home(); return
                elif name == 'sleep_until': yield from self.sleep_until(step[1])
                elif name == 'select':
                    go = yield from self.select(step[1])
                    if not go: break            # energy / bye-law guard refused the next trip: stay docked
                    continue
                elif name == 'to_seek':
                    r_ = yield from self.to_seek(step[1])
                    if r_ == 'stopped': self.finish('stopped', self.outcome_text or 'stopped safely'); return
                    if r_ == 'home': yield from self.go_home(); return
                elif name == 'calendar':       # Rev G4: the bin calendar decides tonight's bins -> expand the plan
                    ext = self.calendar_plan(step[1])
                    self.plan[i_step:i_step] = ext
                    if not ext: break
                elif name == 'teach': yield from self.teach_run(step[1])
                elif name == 'route_check':
                    rc = RouteFile.validate(self.S, self.route); self.metrics['route_check'] = rc
                    self.ev('route file %s: %s' % (os.path.basename(self.sc['route_file']), 'valid' if rc['ok'] else 'REJECTED %s' % rc))
                    if not rc['ok']: self.alert('taught route rejected by the validator - not driving it'); self.finish('alert', 'route rejected'); return
                elif name == 'route_leg':
                    ok = yield from self.route_leg(*step[1:])
                    if ok == 'stopped': self.finish('stopped', self.outcome_text or 'stopped safely'); return
                elif name == 'release_route':
                    ok = yield from self.release_at_pose(self.drop_override, 'release_route')
                    if not ok: self.finish('alert', self.outcome_text); return
                elif name == 'turn_solo':
                    ok = yield from self.solo_turnaround()
                    if not ok: self.finish('alert', 'no room to turn after drop'); return
                elif name == 'up_tow_home':
                    hs = SC.HOME_SPOTS[self.target]
                    ok = yield from self.auto_leg(None, hs['s'] + YARD_UTURN['ds'], hs['lat'] + YARD_UTURN['dlat'], 'up_tow')
                    if ok == 'stopped': self.finish('stopped', self.outcome_text or 'stopped safely'); return
                key = step[-1] if name == 'auto' else name
                if self.sc.get('multi'): key = '%s:%s' % (self.target, key)
                self.leg_time[key] = round(self.leg_time.get(key, 0) + self.w.t - t0, 1)
            self.finish('pass' if not self.bins_left else 'alert', self.outcome_text or 'completed')
        except _Abort as a:
            self.finish('fail', str(a))

    def finish(self, res, text):
        self.result = res if self.result == 'running' else self.result; self.outcome_text = text; self.done = True
        if self.clock0 is not None:
            self.metrics['finish_clock'] = clock_str(self.clock())
            if self.mission == 'pickup' and self.sc.get('multi'):      # bye-law: pickup finished by 21:00 on collection day
                self.metrics['deadline_margin_min'] = round(parse_clock('D0 21:00') - self.clock(), 1)
        self.metrics['soc_end'] = round(self.w.soc, 3)
        self.state = 'DONE'; self.ev('finished: %s - %s' % (res, text))

    # ---------------- Rev G3: multi-bin trips, sleep / RTC wake, bye-law and energy guards ----------------
    def target_ids(self):
        i0 = self.w.bin.get('id0', 0) if self.w.bin else 0
        return set(range(i0, i0 + 4))

    def energy_avail(self):
        return (self.w.soc - RESERVE) * PACK_WH_NOM * pack_cold_factor(self.w.air_c)

    def select(self, owner):
        """Pick which of Brian's bins this trip handles (ported from revG_alt). Guards before each trip: battery energy
        for one more trip above the 10 % reserve, and the bye-law clock (drop not before 18:00 D-1; pickup done by 21:00 D0)."""
        w = self.w
        if self.clock0 is not None and self.mission == 'pickup' and self.sc.get('multi'):
            per = self.metrics.get('trip_min_meas') or 47.0          # measured trip time so far, else ~47 min
            eta = self.clock() + per
            if eta > parse_clock('D0 21:00'):
                self.bins_left.append(owner)
                self.alert('bye-law: the %s bin cannot be back by 21:00 (ETA %s) - left on the pad, please bring it in' % (owner, clock_str(eta)))
                self.outcome_text = 'pickup deadline guard -> %s bin left + alert' % owner; yield; return False
        if self.energy_avail() < TRIP_WH and not self.sc.get('skip_soc_gate'):
            self.bins_left.append(owner)
            self.alert('battery: %.0f Wh above reserve (SOC %.0f %%, %.1f C, charging %s) < %.0f Wh for one more trip - the %s bin stays %s'
                       % (self.energy_avail(), 100 * w.soc, w.air_c, 'inhibited' if w.air_c < 3 else 'possible', TRIP_WH, owner,
                          'at home' if self.mission == 'drop' else 'on the pad'))
            self.outcome_text = 'energy guard -> %s bin not moved + alert' % owner; yield; return False
        self.target = owner
        if getattr(w, 'bins', None):
            w.bin = w.bins[owner]; w.bin_mass = w.bin.get('mass', w.bin_mass)
            w.others = [b for k, b in w.bins.items() if k != owner] + list(getattr(w, 'neighbours', []))
        self.ignore_ids = set(); self.nudges = 0; self.docks = 0; self._trip_t0 = self.w.t
        if self.bins_done:
            n = len(self.bins_done); self.metrics['trip_min_meas'] = round((self.w.t - self._first_trip_t) / 60.0 / n, 1)
        else: self._first_trip_t = self.w.t
        self.bins_done.append(owner)
        self.ev('trip %d: %s bin (tags %d-%d), %.0f Wh available above reserve, clock %s' % (len(self.bins_done), owner, min(self.target_ids()),
                max(self.target_ids()), self.energy_avail(), clock_str(self.clock()) if self.clock0 is not None else '-'))
        if self.mode != 'MANUAL' and self.ekf_xy is not None:      # coming off the dock (HOLD) for the next trip
            self.set_mode('MANUAL'); self._rc = (0, 0); yield from self.wait(1.0)
            for k in range(10):
                if self.armed: break
                self.arm(); yield from self.wait(0.5)
        yield; return True

    def sleep_until(self, when):
        """Rev G3 sleep / RTC wake. The Pi powers down 4G + RTK and itself; the RTC alarm wakes it. The simulation runs 20 s of
        the sleep in lock-step (no heartbeat -> firmware GCS failsafe while disarmed, harmless) and skips the rest of the night
        on the mission clock; sleep energy (SLEEP_W) is booked analytically (from the dock supply when docked). On wake: RTK
        re-convergence is simulated (no fix 20 s, float 25 s), then self-test and re-arm."""
        tgt = parse_clock(when); now = self.clock()
        if now is None or tgt <= now + 0.5:
            self.ev('RTC: wake time %s already passed (clock %s) - no sleep' % (when, clock_str(now) if now is not None else '-')); return
        self.state = 'SLEEP'; self.leg = 'sleep'; self.stop(); self.set_mode('HOLD'); yield from self.wait(0.5)
        self.mav.command_long_send(1, 1, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0); yield from self.wait(0.5)
        self.ev('sleep: disarmed, 4G + RTK + Pi off, RTC alarm set for %s (clock %s)' % (clock_str(tgt), clock_str(now)))
        self.sleeping = True; t0 = self.w.t
        yield from self.wait(20.0)
        skipped = max(0.0, (tgt - self.clock()) * 60.0)
        self.skip_s += skipped
        on_dock = bool(self.w.dock_v)
        e = SLEEP_W * skipped / 3600.0
        self.r.book_sleep(e, skipped, on_dock)
        if on_dock: self.overnight_charge(skipped)
        self.sleep_log.append(dict(start=clock_str(now), wake=clock_str(self.clock()), hours=round((skipped + 20) / 3600.0, 2), wh=round(e, 1), on_dock_power=on_dock,
                                   wh_if_awake=round(STANDBY_W * skipped / 3600.0, 1)))
        self.metrics['sleep'] = self.sleep_log
        self.sleeping = False
        self.r.gps_hold = [(self.w.t, self.w.t + 20.0, 'none'), (self.w.t + 20.0, self.w.t + 45.0, 'float')]
        self.ev('RTC wake at %s: Pi boots, 4G + RTK on (slept %.1f h, %.1f Wh %s)' % (clock_str(self.clock()), (skipped + 20) / 3600.0, e,
                'from the dock supply' if on_dock else 'from the pack'))
        self.state = 'WAKE'; t1 = self.w.t
        while self.fix < 6 or self.w.t - t1 < 2.0:
            yield
            if self.w.t - t1 > 180: raise _Abort('no RTK fix after RTC wake')
        self.metrics['rtk_reconverge_s'] = round(self.w.t - t1, 1)
        self.state = 'BOOT'

    def boot(self):
        self.state = 'BOOT'; self.leg = 'boot'
        while self.ekf_xy is None or self.yaw is None or self.w.t < 12: yield
        # Rev G3 bye-law guard: a drop must not start before 18:00 on the evening before collection -> sleep until then
        if self.clock0 is not None and self.mission == 'drop' and self.sc.get('multi') and self.clock() < parse_clock('D-1 18:00'):
            self.ev('bye-law: clock %s is before 18:00 on the eve of collection -> sleep until 18:00' % clock_str(self.clock()))
            yield from self.sleep_until('D-1 18:00'); self.state = 'BOOT'; self.leg = 'boot'
            while self.fix < 6: yield
        tb = self.w.t
        while True:      # wait until the EKF uses the RTK fix and agrees with it
            x, y, _ = self.pose(); gx, gy = self.r.gps_sent_pos
            using = any('is using GPS' in e['text'] for e in self.r.events)
            if using and math.hypot(x - gx, y - gy) < 0.3: break
            if self.w.t > 120 and self.w.t - tb > 120: raise _Abort('EKF never started using GPS')
            yield
        # Rev G3 (ported from revG_alt): weather no-go at wake, only when a job starts from the dock. Air temperature sensor +
        # forecast frost flag + forecast gusts / Met Eireann wind warning. Bin is not moved; owner alerted.
        dk = SC.DOCK; near_dock = math.hypot(*(np.array(self.pose()[:2]) - np.array(self.S.lane.point(dk['s'], dk['lat'])))) < 6.0
        if near_dock and not self.metrics.get('weather'):
            wx = self.sc.get('weather') or {}
            temp = wx.get('temp_c', self.w.air_c); gust = wx.get('gust_ms', self.w.wind_gust); frost = wx.get('frost', False)
            self.metrics['weather'] = dict(temp_c=temp, gust_ms=gust, frost=frost, warning=wx.get('warning'))
            why = []
            if temp < 0.0 or frost: why.append('ice/frost risk (air %.1f C%s)' % (temp, ', frost flag' if frost else ''))
            if gust >= 18.0 or wx.get('warning') in ('yellow', 'orange', 'red'):
                why.append('high wind (gusts %.0f m/s%s)' % (gust, ', %s wind warning' % wx['warning'] if wx.get('warning') else ''))
            if why:
                self.alert('job skipped - weather no-go: %s. Bin NOT moved; staying on the dock' % '; '.join(why))
                self.outcome_text = 'weather no-go -> skip + alert (stays docked)'; self.state = 'DOCKED'
                self.finish('alert', self.outcome_text); yield; return
        self.set_mode('MANUAL'); self._rc = (0, 0)
        for k in range(30):
            if self.armed: break
            self.arm(); yield from self.wait(0.5)
        if not self.armed: raise _Abort('could not arm')
        self.servo(1900 if self.w.attached else 1100)
        self.change_speed(0.5)
        self.ev('armed, EKF ok, pose %.2f %.2f' % tuple(self.pose()[:2]))
        yield

    # ---------------- AUTO lane legs (firmware navigation) ----------------
    def kl_zone(self, s):
        return self.keep_left and KL_ZONE[0] <= s <= self.S.L - KL_ZONE[1]

    def bend_factor(self, s):
        """Rev G6: keep-left scale near sharp corners of the surveyed centre-line (1 = full keep-left, 0 = centred). The lane survey is a
        5 m polyline with 25-53 deg corners (yard hairpin, s=59, the s=74-84 dog-leg): a towed bin with a 28 deg kingpin stop cannot
        follow a kink, so the planned path is smoothed (R >= ~8 m), and keep-left eases to the centre within 4 m of a corner > 12 deg
        (ramp 6 m) so the smoothed path keeps its hedge margin. Cars cannot pass the tug in those corners anyway."""
        V = getattr(self, '_sharp_v', None)
        if V is None:
            P = self.S.lane.P; ss = self.S.lane.s; V = []
            for k in range(1, len(P) - 1):
                a = abs(math.degrees(wrap(math.atan2(*(P[k + 1] - P[k])[::-1]) - math.atan2(*(P[k] - P[k - 1])[::-1]))))
                if a > 12.0: V.append((float(ss[k]), min(1.0, (a - 12.0) / 12.0)))
            self._sharp_v = V
        w = 0.0
        for sv, fc in V: w = max(w, fc * float(np.clip(1.0 - (abs(s - sv) - 4.0) / 6.0, 0.0, 1.0)))
        return 1.0 - w

    def lane_pts(self, s0, s1, lat, spacing=8.0):
        # a waypoint every 8 m on straights, or whenever the lane heading has turned 12 deg (hairpin by the house)
        # Rev G4 keep-left: inside the keep-left zone a waypoint every 2 m at the keep-left offset for the travel direction
        # Rev G6: smoothed path (2 m spacing everywhere, 3 passes of a [1/4 1/2 1/4] filter, ends fixed) + bend-centring, see bend_factor()
        sgn = 1 if s1 > s0 else -1; ss = []; last = s0; h0 = self.S.lane.heading(s0)
        smooth = self.sc.get('smooth_path', True)
        for s in np.arange(s0 + sgn, s1, sgn * 1.0):
            sp = self.sc.get('kl_spacing', float(os.environ.get('BT_KL_SPACING', '2.0'))) if (self.kl_zone(s) or smooth) else spacing
            if abs(s - last) >= sp or abs(wrap(self.S.lane.heading(s) - h0)) > math.radians(12):
                ss.append(s); last = s; h0 = self.S.lane.heading(s)
        ss.append(s1)
        pts = []
        L = self.S.L; W = self.S.lane.width
        for s in ss:
            l = lat if (abs(s - s1) < 15 or abs(lat) < 0.01) else 0.0
            if self.kl_zone(s) and abs(s - s1) > 6.0: l = kl_lat(W, sgn) * (self.bend_factor(s) if smooth else 1.0)          # Rev G4 keep-left
            if (self.sc.get('multi') or getattr(self, 'placed', None)) and L - 24.0 < s < L - 9.0 and abs(s - s1) > 1.0 and abs(l) < 0.01:
                l = -0.5         # Rev G3: pass the in-lane pad spots (lat +1.1) on the far side (G6: also past spot A after a drop)
            if s < self.S.lane.mouth[0] - 0.3 and not (self.S.lane.yard[0] <= s <= self.S.lane.yard[1]):
                l = float(np.clip(l, -1.55, 1.55))      # Rev G4: body stays >= 0.12 m inside the hedge lines before the bell-mouth
            if self.S.keepouts: l = self.ko_lat(s, l)
            pts.append(tuple(self.S.lane.point(s, l)))
        if smooth and len(pts) > 4:
            q = np.array(pts, float)
            for _ in range(3): q[1:-1] = 0.25 * q[:-2] + 0.5 * q[1:-1] + 0.25 * q[2:]
            q[-2] = 0.5 * (q[-2] + np.array(pts[-2]))        # keep the approach to the leg end close to the planned line
            pts = [tuple(map(float, p)) for p in q]
        sl = np.array([self.S.lane.project(np.array(p)) for p in pts]); o = np.argsort(sl[:, 0])
        self._plan_sl = (sl[o, 0], sl[o, 1])          # Rev G6: planned lateral vs s (the commanded line for XTE / fusion)
        return pts

    def plan_lat(self, s):
        p = getattr(self, '_plan_sl', None)
        if p is None or len(p[0]) < 2: return None
        return float(np.interp(s, p[0], p[1]))

    def start_mission(self, pts):
        self.cur_pts = list(pts)
        self.upload(pts)
        while self.upl['acked'] is None: yield
        self.upl = None
        self.mav.mission_set_current_send(1, 1, 1)

    def auto_leg(self, s0, s1, lat, leg, pts=None, stop_s=None):
        self.leg = leg; self.state = 'AUTO_' + leg.upper()
        if s0 is None: s0 = self.s_lat()[0]
        if leg == 'down_tow_mouth' and self.sc.get('uturn_g4', True):
            # Rev G4: the U-turn starts at L-11.5 m, lat -1.5 m (inside the bell-mouth: no hedge overlap; R 1.5 m). The firmware
            # waypoint radius (1.5 m) made G3 legs end ~1.5 m short, so the last waypoint is set beyond and the leg is cut at stop_s.
            s1 = self.S.L - UTURN_G4['start_from_end'] + 1.5; lat = UTURN_G4['lat']
            stop_s = self.S.L - UTURN_G4['start_from_end'] - UTURN_G4['stop_early']
        if pts is None: pts = self.lane_pts(s0, s1, lat)
        if self.adaptive and leg == 'up_tow' and self.w.attached and self._home_check is None and self.mission != 'teach' and s0 > 20:
            hb = self.home_override or SC.HOME_SPOTS.get(self.target, SC.HOUSE_BIN)
            self._home_check = dict(s=hb['s'], primary=dict(s=hb['s'], lat=hb['lat']))
        yield from self.start_mission(pts)
        sgn0 = 1 if s1 > s0 else -1; self._leg_sgn = sgn0; self._fi = 0
        self.pi_follow = bool(self.w.attached and self.sc.get('pi_follow', os.environ.get('BT_PI_FOLLOW', '1') != '0'))
        if self.w.attached and self.hitch_gov_on and self.sc.get('gov_launch', True) and self.mode == 'MANUAL' and not self.pi_follow:
            yield from self.rejoin()         # Rev G6: governed launch onto the path (AUTO from standstill turned hard -> hitch stop)
            self.mav.mission_set_current_send(1, 1, self.next_wp_ahead(sgn0, margin=2.0))
        self.rc_release(); self._rc = None
        self.base_speed = 0.5; self.change_speed(0.5)
        self.set_mode('AUTO'); yield from self.wait(0.5)
        last = self.mission_n - 1; held = None; t_prog = self.w.t; s_prog = self.s_lat()[0]; self._fi = 0
        detour = None; self._obs_n = 0; sgn = 1 if s1 > s0 else -1; self._leg_sgn = sgn
        while True:
            yield
            if getattr(self, 'following', False) and held is None and self.vstop_state is None: self.follow_step()
            s_here = self.s_lat()[0]
            self.kl_active = bool(self.keep_left and pts is not None and self.kl_zone(s_here) and abs(s_here - s1) > 8.0 and abs(s_here - s0) > 8.0 and held is None
                                  and detour is None and self.leg_auto() and self.vstop_state is None and not self.route_mode
                                  and not any(abs(k['s'] - s_here) < 6.0 for k in self.metrics.get('keepout_shifts', [])))
            if stop_s is not None and s_here >= stop_s: break
            if self.reached >= last or (self.mode == 'HOLD' and held is None and self.vstop_state is None and self.reached >= last - 1
                                        and math.hypot(*(np.array(self.pose()[:2]) - np.array(pts[-1]))) < 2.0):
                break
            hc = self._home_check                            # Rev G4 g): look at the home slot while approaching the yard
            if hc is not None and not hc.get('done') and (math.hypot(*(np.array(self.S.lane.point(hc['s'], hc['primary']['lat'])) - self.pose()[:2])) < 10.8 or s_here <= hc['s'] + 6.0):
                hc['done'] = True; tgt = yield from self.choose_home_slot(final=s_here <= hc['s'] + 6.0)
                if tgt == 'defer': hc['done'] = False; tgt = hc['primary']     # G4 fix: slot hidden behind the hedge -> look again on the way in
                if tgt is None: self.kl_active = False; return 'stopped'
                if tgt is not hc['primary']:
                    self.kl_active = False; self.set_mode('MANUAL'); self._rc = (0, 0); yield from self.wait(0.8)
                    s_end = tgt['s'] + YARD_UTURN['ds']; lat_end = float(np.clip(tgt['lat'] + YARD_UTURN['dlat'], -5.0, 5.0))
                    self.ev('home slot blocked -> re-plan the yard approach to the alternate (U-turn from s=%.1f, lat %.1f)' % (s_end, lat_end))
                    return (yield from self.auto_leg(None, s_end, lat_end, leg))
            vs = yield from self.vehicle_watch(leg)          # Rev G4: vehicle-approach stop (front/rear radar + lidar)
            if vs == 'stopped': self.kl_active = False; return 'stopped'
            if vs == 'held': t_prog = self.w.t; continue
            if not self.w.chain_ok:          # Rev G3 (ported): hard-wired chain opened (E-stop or a bump strip) -> hold + alert
                self.set_mode('HOLD'); self.stop(); tr = self.w.chain_trips[-1]; t0c = self.w.t
                while abs(self.w.v) > 0.003 and self.w.t - t0c < 6: yield
                self.metrics['chain_stop'] = dict(t=round(self.w.t, 1), reason=self.w.chain_reason, v_at_trip=tr['v'],
                                                  stop_dist_m=round(math.hypot(self.w.x - tr['x'], self.w.y - tr['y']), 3), stop_time_s=round(self.w.t - tr['t'], 2))
                if self.w.estop:
                    self.alert('E-stop pressed: motors cut by the hard-wired chain; holding (manual twist-reset needed)')
                    self.outcome_text = 'E-stop -> stopped (hardware) + alert'
                else:
                    self.alert('bump strip hit something the lidar did not see: motors cut by the hard-wired chain; holding')
                    self.outcome_text = 'bump strip -> stopped (hardware) + alert'
                return 'stopped'
            if self.mode != 'AUTO' and held is None and self.w.t - getattr(self, '_auto_cmd_t', -9) > 3.0 and self.mode in ('HOLD', 'RTL', 'SMART_RTL'):
                # Rev G3 (ported): the firmware left AUTO on its own -> a firmware failsafe fired (battery / EKF)
                txt = [e['text'] for e in self.r.events if e['kind'] == 'fw' and e['t'] > self.w.t - 8]
                self.alert('firmware failsafe: autopilot switched to %s (%s); holding with spring brakes' % (self.mode, '; '.join(txt[-2:]) or 'no text'))
                self.metrics['fw_failsafe'] = dict(t=round(self.w.t, 1), mode=self.mode, text=txt[-3:], soc=round(self.w.soc, 3), pack_v=round(self.w.pack_v, 2))
                self.outcome_text = 'firmware failsafe -> %s + alert' % self.mode; return 'stopped'
            hg = yield from self.hitch_guard(leg)
            if hg == 'resumed': t_prog = self.w.t; continue
            r = yield from self.gps_policy(leg)
            if r == 'stopped': return 'stopped'
            if r == 'resumed': continue
            obs = self.path_obstacle(1.5 if held is None else 2.2)
            if held is None and abs(getattr(self, 'yawspeed', 0.0)) > 0.5: obs = None    # Rev G4: map gate unreliable while yawing fast (EKF/scan skew)
            self._obs_n = (self._obs_n + 1) if obs is not None else 0
            if held is None and self._obs_n < 3: obs = None          # must persist for 3 scans (0.3 s)
            if held is None and obs is not None and detour is None:
                self.set_mode('HOLD'); held = self.w.t; self.state = 'OBSTACLE_HOLD'; self.min_gap = 9.0
                stop_info = dict(t=round(self.w.t, 1), leg=leg, lidar_range=round(obs[0], 2), truth_gap=round(self.truth_gap(), 2), v_at_detect=round(self.w.v, 2))
                self.ev('lidar: unmapped object %.2f m ahead -> HOLD' % obs[0]); clear_since = None; moved = False; first = obs[1]; win = self.w.t
            elif held is not None:
                self.min_gap = min(self.min_gap, self.truth_gap())
                if obs is None:
                    clear_since = clear_since or self.w.t
                    if self.w.t - clear_since > 3.0:
                        stop_info.update(wait_s=round(self.w.t - held, 1), stopped_gap=round(self.min_gap, 2), kind='moving')
                        self.stops.append(stop_info); self.ev('path clear for 3 s -> resume AUTO')
                        self.set_mode('AUTO'); held = None; self.state = 'AUTO_' + leg.upper()
                else:
                    clear_since = None
                    if np.linalg.norm(np.array(obs[1]) - np.array(first)) > 0.4: moved = True
                    if self.w.t - held > 300.0:            # Rev G2: never hold forever (seed sweep found a 1,400 s hold)
                        self.alert('lane blocked for 5 min by something that keeps moving'); self.outcome_text = 'blocked lane -> stopped + alert'; return 'stopped'
                    if moved and self.w.t - win > 8.0:      # Rev G2: re-judge in fresh 8 s windows (noisy returns used to latch 'moving')
                        win = self.w.t; first = obs[1]; moved = False
                    elif self.w.t - win > 8.0 and not moved:
                        stop_info.update(wait_s=round(self.w.t - held, 1), stopped_gap=round(self.min_gap, 2), kind='static'); self.stops.append(stop_info)
                        det = self.detour_pts(s1)
                        if det is None:
                            self.alert('lane blocked by a static object - no room to pass inside the hedges')
                            self.outcome_text = 'lane blocked -> stopped + alert'; return 'stopped'
                        pts, off, s_obs = det
                        self.ev('static object at s=%.1f -> detour mission, %.2f m lateral offset' % (s_obs, off))
                        self.metrics['detour_offset_m'] = round(off, 2)
                        yield from self.start_mission(pts); last = self.mission_n - 1; self._fi = 0
                        detour = (self.w.t, s_obs); held = None
                        self.state = 'AUTO_DETOUR'; self.set_mode('AUTO')
            if detour is not None:
                s_now = self.s_lat()[0]
                if sgn * (s_now - detour[1]) > 4.0:
                    detour = None; self.state = 'AUTO_' + leg.upper(); self.ev('passed the obstacle'); self.metrics['detour_passed'] = True
                elif self.w.t - detour[0] > 120:
                    self.set_mode('HOLD'); self.alert('lane blocked: detour made no progress in 120 s')
                    self.outcome_text = 'blocked lane -> stopped + alert'; return 'stopped'
            if abs(self.s_lat()[0] - s_prog) > 1.0: s_prog = self.s_lat()[0]; t_prog = self.w.t
            if held is None and self.w.t - t_prog > 120:
                self.set_mode('HOLD'); self.alert('no progress for 120 s in AUTO'); self.outcome_text = 'stuck -> alert'; return 'stopped'
        self.kl_active = False; self.pi_follow = False
        self.set_mode('MANUAL'); self._rc = (0, 0); yield from self.wait(0.5)
        self.ev('leg %s done at s=%.1f' % (leg, self.s_lat()[0]))
        if stop_s is not None:
            sl = self.s_lat(); self.metrics.setdefault('uturn_start', []).append(dict(s_from_end=round(self.S.L - sl[0], 2), lat=round(sl[1], 2)))
        return 'ok'

    def junction_wait(self):
        """Rev G3 junction wait point (L-23 m: 15.7 m from the carriageway edge, 12.7 m inside the assumed private boundary).
        The tug always stops here, looks toward the mouth with the lidar and only goes on when the lane ahead and the mouth
        entrance (as far as the 12 m LD06 reaches) have been clear for 5 s. It never waits in the mouth. Blocked > 15 min ->
        alert, go home. Known bins on the pad are not traffic."""
        self.state = 'JUNCTION_WAIT'; self.leg = 'junction_wait'; self.stop(); yield from self.wait(1.0)
        L = self.S.L; t0 = self.w.t; clear_since = None; seen = False; s_here = self.s_lat()[0]
        self.metrics.setdefault('junction_wait', []).append(dict(s_from_end=round(L - s_here, 1), boundary_m=round(self.S.boundary_dist(self.pose()[:2]), 1)))
        hist = []
        while True:
            for k in range(5): yield                         # re-judge twice a second
            cands, big = self.lidar_candidates(); busy = None
            def in_area(c):
                sc_, lc_ = self.S.lane.project(np.asarray(c, float))
                return s_here + 1.5 < sc_ < L + 2 and abs(lc_) < self.S.mouth_half + 0.5
            big = [b for b in big if in_area(b['c'])]
            small = [np.asarray(c['c']) for c in cands if in_area(c['c'])]
            if big: busy = 'vehicle-sized object (%.1f m)' % max(b['ext'] for b in big)
            hist.append((self.w.t, small)); hist = [h for h in hist if self.w.t - h[0] < 2.6]
            if busy is None and len(hist) >= 4:              # bin-sized objects are expected (bins on the pad); only MOVING ones count
                old = hist[0][1]
                for c in small:
                    if old and min(np.linalg.norm(c - o) for o in old) > 0.45: busy = 'moving object (person/animal)'
            if busy:
                if not seen: self.ev('junction: %s in the lane/mouth ahead -> wait here (%.1f m inside the boundary, %.1f m from the carriageway edge)'
                                     % (busy, self.S.boundary_dist(self.pose()[:2]), self.S.road_dist(self.pose()[:2]) - self.S.road_half))
                seen = True; clear_since = None
            else: clear_since = clear_since or self.w.t
            if clear_since is not None and self.w.t - clear_since >= (5.0 if seen else 1.5): break
            if self.w.t - t0 > 600:
                self.alert('junction mouth occupied for 10 min (%s) - not entering; returning home' % busy); self.outcome_text = 'mouth blocked -> alert, home'
                self.metrics['junction_wait'][-1].update(waited_s=round(self.w.t - t0, 1), saw_traffic=True)
                return 'stopped'
        w_s = round(self.w.t - t0, 1); self.metrics['junction_wait'][-1].update(waited_s=w_s, saw_traffic=seen)
        if seen: self.ev('junction: mouth clear for 5 s after %.0f s -> go on' % w_s)
        return 'ok'

    def known_pad_bins(self):
        """Pad spots that hold (or should hold) one of Brian's bins: placed this evening, or due for pickup."""
        out = list(getattr(self, 'placed', []))
        if self.mission == 'pickup' and self.sc.get('multi'):
            sp = self.layout.spots(self.S); out += [np.asarray(self.S.lane.point(v['s'], v['lat'])) for v in sp.values()]
        return out

    def to_seek(self, pad):
        """Rev G3: drive down to the look-out for this trip's pad spot (A at the mouth: junction wait point first)."""
        L = self.S.L
        if pad == 'LOG':      # Rev G4 g): go to wherever the bin was actually left (drop log), then search by lidar + tags
            e = (self.sc.get('drop_log') or {}).get(self.target)
            if e is None: self.ev('drop log has no entry for the %s bin -> programmed pad %s' % (self.target, self.pad_for.get(self.target, 'A') if self.pad_for else 'A')); pad = (self.pad_for or {}).get(self.target, 'A')
            else:
                self._seek_prior = e; self.ev('drop log: %s bin left at L-%.2f m, lat %.2f (%s) -> search there' % (self.target, L - e['s'], e['lat'], e.get('slot', '?')))
                pad = 'A' if e['s'] > L - 12.5 else 'LOGLANE'
        sp = self.layout.spot(self.S, pad) if pad in self.layout.d['spots'] else dict(s=self._seek_prior['s'], lat=self._seek_prior['lat'])
        # G6 session 3: leg results are now checked. G6 v1 ignored them, so after a 'lane blocked' stop half-way down the lane the
        # seek ran where the tug stood and took a hedge bulge for a bin lying on its side (s10b 'tipped bin' at s=500).
        self._seek_pad = pad
        if pad == 'A':
            r = yield from self.auto_leg(None, L - SC.JUNCTION_WAIT, 0.0, 'down_empty')
            if r == 'stopped': return 'stopped'
            r = yield from self.junction_wait()
            if r == 'stopped': return 'home'
            r = yield from self.auto_leg(None, L - 16, 0.0, 'down_empty_mouth')
            if r == 'stopped': return 'stopped'
        else:
            r = yield from self.auto_leg(None, sp['s'] - 7.0, -0.5, 'down_empty')
            if r == 'stopped': return 'stopped'
        return 'ok'

    def release_pad(self, pad):
        """Rev G3: after the mouth U-turn, release at pad spot A (as before) or tow back up the lane to spot M/F and release
        there (bin handle facing up-lane, ready for the pickup). The pull-away then moves to the far side of the lane."""
        bx, by, byaw = self.layout.bin_pose(self.S, pad); u = np.array([math.cos(byaw), math.sin(byaw)])
        axle = np.array([bx, by]) + 0.985 * u                   # released bin centre sits 0.985 m behind the drive axle
        if pad == 'A':
            x, y, yaw = self.pose(); ahead_m = (axle - np.array([x, y])) @ np.array([math.cos(yaw), math.sin(yaw)])
            if 0.3 < ahead_m < 4.0:                              # Rev G4: programmed spot A ahead of the U-turn end -> drive on to it
                self.state = 'TO_PAD'; yield from self.goto(*axle, v=0.25, tol=0.2)
            r = yield from self.release('release_mouth', pull=not self.sc.get('multi'))     # G4: no blind 1 m pull toward the bin on pad M
            if r: self.placement(pad, (bx, by, byaw))
            if r and self.sc.get('multi'):      # Rev G3: other bins wait on the in-lane spots (lat +0.85): move to the far side first
                yield from self.goto(*self.S.lane.point(self.S.L - 12.8, -0.6), v=0.3, tol=0.4)
            return r
        sp = self.layout.spot(self.S, pad); self.state = 'TO_PAD'; self.leg = 'place_pad'
        via = 0.6; slot_name = pad
        if self.adaptive:                                    # Rev G4 g): is the programmed slot clear? else nearest clear legal alternate
            tgt = yield from self.choose_pad_slot(pad, (bx, by, byaw))
            if tgt is None:
                self.set_mode('HOLD'); self.state = 'RELEASE_HOLD'
                self.alert('no clear drop slot: pad %s and all %d alternates blocked - holding with the %s bin hooked' % (pad, self.metrics['adaptive_slot'][-1]['n_alts'], self.target))
                self.outcome_text = 'all drop slots blocked -> holding bin + alert'; return False
            if tgt != (bx, by, byaw):
                bx, by, byaw = tgt; u = np.array([math.cos(byaw), math.sin(byaw)]); axle = np.array([bx, by]) + 0.985 * u; via = -0.5; slot_name = pad + "'"
        ax = float(self.S.lane.project(axle)[0])
        pre = axle - 2.2 * u; s_pre, l_pre = self.S.lane.project(pre)
        yield from self.goto_lane(s_pre, l_pre + 0.2 if via > 0 else l_pre, v=0.3, via_lat=via, tol=0.4)
        yield from self.goto(*axle, v=0.25, tol=0.2)
        r = yield from self.release('release_pad', pull=False)
        if not r: return r
        self.placement(slot_name, (bx, by, byaw))
        yield from self.goto(*self.S.lane.point(ax - 1.4, 0.3), v=0.25, tol=0.3)
        yield from self.goto(*self.S.lane.point(ax - 3.0, -0.5), v=0.3, tol=0.4)
        return True

    # ---------------- Rev G6: handles-out drop ----------------
    def drop_out(self, pad):
        """Rev G6 handles-out drop (approved by Brian; mouth U-turn with the bin is infeasible at a 28 or 40 deg kingpin stop).
        From the junction wait point: check the slot with the lidar (and pick a legal alternate or hold + alert HERE, with the bin,
        before entering), tow straight down to the slot with the hitch governor, release (handle faces the road), pull forward and
        turn round SOLO (pivot, never with a bin). Drop order A -> M -> F, so the tug never passes a placed bin while towing."""
        S = self.S; L = S.L
        bx, by, byaw = self.layout.bin_pose(S, pad); slot_name = pad
        u = np.array([math.cos(byaw), math.sin(byaw)])           # handle direction = down-lane = tug heading at release
        self.state = 'SLOT_CHECK'; self.leg = 'slot_check'
        placed = [np.asarray(p) for p in getattr(self, 'placed', [])]
        s_pl = [float(S.lane.project(p)[0]) for p in placed]
        def reach_ok(a):             # tug front at release must stop >= 0.6 m short of every placed bin (never pass one while towing)
            sa = float(S.lane.project(np.array(a[:2]))[0]); front = sa + 0.985 + TUG['front']
            return all(front <= sp_ - BIN['d'] / 2 - 0.6 for sp_ in s_pl)
        if not reach_ok((bx, by, byaw)):
            self.metrics.setdefault('tow_past_placed', []).append(dict(pad=pad, bin=self.target))
        if self.adaptive:
            sp = self.layout.spot(S, pad)
            def room(x, y, yaw):     # release pose (tug body down-lane of the bin) inside the fence, off the hedges
                ax_ = np.array([x, y]) + u * 0.985; fr = ax_ + u * (TUG['front'] + 0.2)
                return S.in_fence(ax_, margin=0.2) and S.fp_ok(tuple(fr), 0.3) and S.hedge_dist(fr) > 0.45
            def extra(a): return reach_ok(a)
            tgt = yield from self._choose(pad, (bx, by, byaw), lambda: self.areas.alternates(pad, (bx, by, byaw), sp['hedge_clear_m'], self._others_for(pad), sp['spacing_m'], room), extra)
            if tgt is None:
                self.set_mode('HOLD'); self.state = 'SLOT_HOLD'
                self.alert('no clear drop slot from the wait point: pad %s and all %d alternates blocked - holding with the %s bin hooked, not entering'
                           % (pad, self.metrics['adaptive_slot'][-1].get('n_alts', 0), self.target))
                self.outcome_text = 'all drop slots blocked -> holding bin at the wait point + alert'; return False
            if tuple(tgt) != (bx, by, byaw):
                bx, by, byaw = tgt; u = np.array([math.cos(byaw), math.sin(byaw)]); slot_name = pad + "'"
        axle = np.array([bx, by]) + 0.985 * u
        sa, la = S.lane.project(axle)
        self.state = 'TO_PAD'; self.leg = 'place_pad'
        s0, l0 = self.s_lat()
        yield from self.goto_lane(sa - 4.0, la, v=0.35, via_lat=float(np.clip(0.5 * (l0 + la), -1.3, 1.3)), tol=0.35)    # straight 4 m run-in: bin lines up
        yield from self.goto(*axle, v=0.25, tol=0.2)
        r = yield from self.release('release_pad', pull=True)
        if not r: return False
        self.placement(slot_name, (bx, by, byaw))
        ok = yield from self.solo_turnaround()
        return True if ok else (yield from self._turn_fail())

    def _turn_fail(self):
        self.set_mode('HOLD'); self.alert('released the bin but found no room to turn round solo - holding'); self.outcome_text = 'no room to turn after drop -> alert'
        yield; return False

    def solo_turnaround(self):
        """Rev G6: after a handles-out release the tug faces down-lane with its bin just behind. Drive 0.6-2.0 m on (and toward the
        lane centre) to a pivot point whose 1.15 m swept circle is inside the geofence (bumper rule), off the hedges and clear of
        every placed bin, then pivot to face up-lane. Solo pivots are fine (no bin, no hitch)."""
        S = self.S; x, y, yaw = self.pose(); s_n, l_n = self.s_lat(); dirn = 1 if math.cos(wrap(yaw - S.lane.heading(s_n))) > 0 else -1
        bins = [np.asarray(p) for p in getattr(self, 'placed', [])] + [np.asarray(p) for p in (self.obst_pts or [])]
        best = None
        for d in (0.0, 0.3, 0.6, 1.0, 1.4):
            for dl in (0.0, -0.3, -0.6, -0.9, 0.3):
                sq = s_n + dirn * d; lq = l_n + dl * (1 if l_n >= 0 else -1)
                Q = np.asarray(S.lane.point(sq, lq), float); ok = True
                for k in range(16):
                    a = 2 * math.pi * k / 16; c = Q + 1.15 * np.array([math.cos(a), math.sin(a)])
                    if not S.fp_ok(tuple(c), 0.15) or S.hedge_dist(c) < 0.12 or any(np.linalg.norm(c - b_) < 0.55 for b_ in bins): ok = False; break
                if ok: best = Q; break
            if best is not None: break
        if best is None: self.ev('solo turnaround: no clear pivot point'); return False
        self.state = 'TURN_SOLO'
        yield from self.goto(*best, v=0.25, tol=0.2)
        h = S.lane.heading(S.lane.project(best)[0]) + (math.pi if dirn > 0 else 0.0)
        yield from self.pivot(wrap(h))
        # the bin just released (and any placed bin) may now be straight ahead: side-step to its lane-centre side before the AUTO leg
        s_q, l_q = S.lane.project(best)
        for b_ in getattr(self, 'placed', []):
            sb, lb = S.lane.project(np.asarray(b_)); ahead_b = -dirn * (sb - s_q)
            if 0.0 < ahead_b < 4.0 and abs(lb - l_q) < 1.05:
                side = -1.0 if lb >= 0 else 1.0; lt = lb + side * 1.95
                st = s_q                                # straight across at the pivot station (the bin face is >= 0.9 m ahead)
                self.ev('side-step past our bin at L-%.1f m: to lat %.2f' % (S.L - sb, lt))
                yield from self.goto(*S.lane.point(st, lt), v=0.25, tol=0.3); break
        self.metrics.setdefault('solo_turn', []).append(dict(at=[round(float(S.lane.project(best)[0]) - S.L, 2), round(float(S.lane.project(best)[1]), 2)]))
        return True

    def detour_pts(self, s1):
        """Lateral detour round a static object inside the hedged lane (tug half-width 0.38 m + 0.3 m margin)."""
        x, y, yaw = self.pose(); P, _ = self.scan_points(); S = self.S
        s_now, _ = S.lane.project(np.array([x, y])); sgn = 1 if s1 > s_now else -1
        if not len(P): return None
        SL = np.array([S.lane.project(p) for p in P])
        m = (sgn * (SL[:, 0] - s_now) > 0) & (sgn * (SL[:, 0] - s_now) < 6) & (np.abs(SL[:, 1]) < 2.0)
        if not m.any(): return None
        lmin, lmax = SL[m, 1].min(), SL[m, 1].max(); s_a, s_b = SL[m, 0].min(), SL[m, 0].max()
        half = S.lane.width / 2 + 0.25 - 0.38 - 0.2
        need = 0.38 + 0.3
        near, far = (s_a, s_b) if sgn > 0 else (s_b, s_a)
        tail = 1.5 + (BIN['L'] + 0.6 if self.w.attached else 0.0)
        # G6 session 3: the free lateral interval comes from the RAW scan (hedge faces included) over the whole stretch the tug and
        # bin will occupy, not from the survey line: G6 v1 detoured round a hedge bulge straight into the opposite (real) hedge
        # (s1 s=399 -0.72 m, s3 s=73 -0.80 m truth clearance).
        sl = G6.scan_lane(S.lane, np.array([x, y]), self.yaw_now(), self.r.scan)
        opts = []
        if sl is not None:
            ss, ll = sl[0], sl[1]
            w_ = (sgn * (ss - near) > -1.0) & (sgn * (ss - far) < tail + 1.0) & (np.abs(ll) < 3.2)
            v = np.sort(np.r_[ll[w_], -G6.HL_NOM, G6.HL_NOM]); v = v[(v >= -G6.HL_NOM) & (v <= G6.HL_NOM)]
            for a_, b_ in zip(v[:-1], v[1:]):
                if b_ - a_ >= 2 * need:
                    o = float(np.clip(0.0, a_ + need, b_ - need))
                    if abs(o) <= half: opts.append(o)
        else:
            opts = [o for o in (lmax + need, lmin - need) if abs(o) <= half]
        if not opts: return None
        off = min(opts, key=abs); s_obs = 0.5 * (s_a + s_b)
        lat_now = S.lane.project(np.array([x, y]))[1]
        # hold the offset until the towed bin (1.35 m behind the axle, off-tracking on the turntable) is past the object.
        # Entry starts AHEAD of the tug (G6 v1 put the first waypoint 3 m before the object = behind a tug stopped 1.5 m short,
        # so AUTO pivoted round to reach it: s22b spun in place at s=474 for 10 min).
        pts = []
        if sgn * (near - s_now) > 2.0: pts.append(tuple(S.lane.point(s_now + sgn * 0.8, lat_now + 0.6 * (off - lat_now))))
        pts += [tuple(S.lane.point(near - sgn * 0.6, off)),
                tuple(S.lane.point(far + sgn * tail, off)), tuple(S.lane.point(far + sgn * (tail + 4.0), 0.5 * off))]
        pts += self.lane_pts(far + sgn * (tail + 4.0), s1, 0.0)
        return pts, off, s_obs

    def truth_gap(self):
        """Evaluation metric only (not used for control): front bumper to nearest mover / static obstacle."""
        w = self.w; fx = w.x + TUG['front'] * math.cos(w.yaw); fy = w.y + TUG['front'] * math.sin(w.yaw)
        d = [math.hypot(fx - m['pos'](w.t)[0], fy - m['pos'](w.t)[1]) - m['r'] for m in w.movers]
        for o in w.obst: d.append(math.hypot(fx - o['x'], fy - o['y']) - 0.5 * o['W'])
        return min(d) if d else 99.0

    def scan_points(self):
        """Current lidar scan in world xy (firmware EKF pose), with returns on the surveyed hedge map removed."""
        r = self.r.scan
        if r is None: return np.zeros((0, 2)), np.zeros(0)
        x, y, yaw = self.pose()
        ox = x + TUG['lidar_x'] * math.cos(yaw); oy = y + TUG['lidar_x'] * math.sin(yaw)
        ang = yaw + np.radians(np.arange(360)); ok = np.isfinite(r)
        P = np.c_[ox + r[ok] * np.cos(ang[ok]), oy + r[ok] * np.sin(ang[ok])]; rr = r[ok]
        H = self.S.hedges_near((x, y), 16.0)
        if len(P) and len(H):
            d = np.min(seg_dist(P[:, None, :], H[None, :, :2], H[None, :, 2:]), axis=1)
            keep = d > (0.45 if self.fix >= 6 else 0.9); P = P[keep]; rr = rr[keep]     # wider map gate when the pose is RTK-float
        walls = getattr(self.r, 'walls', None)
        if walls and len(P) and self.sc.get('wall_mask', True):
            # Rev G6: drop returns that lie on a fitted hedge FACE (tug frame, pose-free) - overgrown bulges and bends stand
            # 0.2-0.6 m off the surveyed hedge line and caused false 'unmapped object' holds. Only long, near-parallel faces
            # >= 0.6 m to the side are used (CorridorFit), so a bin, a person or the rear of a car across the path stays an obstacle.
            c, s_ = math.cos(yaw), math.sin(yaw); rel = P - np.array([ox, oy])
            px = TUG['lidar_x'] + rel @ np.array([c, s_]); py = rel @ np.array([-s_, c])
            wv = {sd: {k: v for k, v in ws.items() if v['dist'] >= 0.6} for sd, ws in walls.items()}
            m = CorridorFit.on_wall(px, py, wv)
            if m.any(): self._wall_masked = getattr(self, '_wall_masked', 0) + int(m.sum()); P = P[~m]; rr = rr[~m]
        return P, rr

    def turn_obstacle(self, direction, reach=0.55):
        """Rev G6: lidar returns (map-filtered) within `reach` m of the front bumper corners or ahead on the turning side."""
        x, y, yaw = self.pose(); P, rr = self.scan_points()
        if not len(P): return None
        c, s_ = math.cos(yaw), math.sin(yaw); rel = P - np.array([x, y])
        fwd = rel @ np.array([c, s_]); lat = rel @ np.array([-s_, c])
        m = (fwd > TUG['front'] - 0.25) & (fwd < TUG['front'] + reach) & (lat * direction > -TUG['half_w'] - 0.15) & (np.abs(lat) < TUG['half_w'] + reach)
        if not m.any(): return None
        return float(np.min(fwd[m]) - TUG['front'])

    def path_obstacle(self, ahead):
        x, y, yaw = self.pose(); P, rr = self.scan_points()
        if not len(P): return None
        c, s = math.cos(yaw), math.sin(yaw); rel = P - np.array([x, y])
        fwd = rel @ np.array([c, s]); lat = rel @ np.array([-s, c])
        m = (fwd > TUG['front'] - 0.1) & (fwd < TUG['front'] + ahead) & (np.abs(lat) < TUG['half_w'] + 0.35)
        if not m.any(): return None
        i = np.argmin(fwd[m]); return float(fwd[m][i] - TUG['front']), P[m][i].tolist()

    # ---------------- GPS policy ----------------
    def gps_policy(self, leg):
        f = getattr(self.r, 'fus', None); wm = f.width_meas if (f is not None and f.width_meas is not None and self.kl_active) else 9.0
        nar = bool(f is not None and self.kl_active and f.narrow)       # G6 s3: the clearance clamp is binding (or latched)
        self._nar_n = (getattr(self, '_nar_n', 0) + 1) if (wm < 3.1 or nar) else 0; self._wide_n = (getattr(self, '_wide_n', 0) + 1) if (wm > 3.25 and not nar) else 0
        if self._nar_n >= 3 and self.base_speed > 0.3:     # Rev G6: narrowing seen for 0.8 s -> 0.3 m/s while centring (time for the shift)
            self.base_speed = 0.3; self.change_speed(0.3); self._nar_slow = True; self.ev('narrowing ahead (%.2f m between hedge faces) -> centre, 0.3 m/s' % wm)
            self.metrics['narrow_slow'] = self.metrics.get('narrow_slow', 0) + 1
        elif getattr(self, '_nar_slow', False) and self._wide_n >= 30 and self.fix >= 6:
            self._nar_slow = False; self.base_speed = 0.5; self.change_speed(0.5)
        if self.fix == 5 and self.base_speed > 0.3:
            self.base_speed = 0.3; self.change_speed(0.3); self.ev('RTK float -> slow to 0.3 m/s'); self.state = 'AUTO_FLOAT_SLOW'
        elif self.fix >= 6 and self.base_speed < 0.5 and not getattr(self, '_nar_slow', False):
            self.base_speed = 0.5; self.change_speed(0.5); self.ev('RTK fixed again -> 0.5 m/s'); self.state = 'AUTO_' + leg.upper()
        if self.fix > 1 or self.fix == 0: return None
        # no fix: dead-reckon along the surveyed lane heading for up to 8 m at 0.25 m/s (compass heading + commanded speed)
        self.ev('GPS no fix -> dead-reckoning (max 8 m)'); self.state = 'DEAD_RECKON'; self.metrics.setdefault('gps_loss_events', 0)
        self.metrics['gps_loss_events'] += 1
        x, y, yaw = self.pose(); s0, _ = self.S.lane.project(np.array([x, y]))
        self.set_mode('MANUAL'); self.dr = [x, y]; dist = 0.0; t_last = self.w.t
        dirn = 1 if math.cos(wrap(yaw - self.S.lane.heading(s0))) > 0 else -1
        dr0 = (x, y, self.w.x, self.w.y)
        while dist < 8.0:
            yield
            dt = self.w.t - t_last; t_last = self.w.t
            s_dr, lat_dr = self.S.lane.project(np.array(self.dr))
            hdg = self.S.lane.heading(s_dr) + (0 if dirn > 0 else math.pi)
            lat_t = kl_lat(self.S.lane.width, dirn) if self.kl_zone(s_dr) else 0.0      # Rev G4: hold the keep-left line
            err = wrap(hdg - self.yaw) - 0.15 * (lat_dr - lat_t) * dirn
            self.drive(float(np.clip(-0.8 * err, -0.3, 0.3)), self.thr_ctl(0.25))
            v = 0.25; self.dr[0] += v * dt * math.cos(self.yaw); self.dr[1] += v * dt * math.sin(self.yaw); dist += v * dt
            if self.fix >= 5:
                err_m = math.hypot(self.dr[0] - dr0[0] - (self.w.x - dr0[2]), self.dr[1] - dr0[1] - (self.w.y - dr0[3]))
                self.metrics.setdefault('dead_reckon', []).append(dict(dist_m=round(dist, 2), end_err_m=round(err_m, 2), recovered=True))
                self.ev('fix back after %.1f m dead-reckoning (DR error %.2f m) -> AUTO' % (dist, err_m))
                self.dr = None; self.stop(); yield from self.wait(1.0)
                self.mav.mission_set_current_send(1, 1, self.next_wp_ahead(dirn)); self.set_mode('AUTO'); self.state = 'AUTO_' + leg.upper()
                return 'resumed'
        self.stop(); self.set_mode('HOLD'); self.state = 'GPS_LOST_HOLD'
        err_m = math.hypot(self.dr[0] - dr0[0] - (self.w.x - dr0[2]), self.dr[1] - dr0[1] - (self.w.y - dr0[3]))
        self.metrics.setdefault('dead_reckon', []).append(dict(dist_m=round(dist, 2), end_err_m=round(err_m, 2), recovered=False))
        self.ev('8 m dead-reckoned, still no fix -> HOLD and wait 60 s')
        t0 = self.w.t
        while self.w.t - t0 < 60:
            yield
            if self.fix >= 5:
                self.dr = None; self.mav.mission_set_current_send(1, 1, self.next_wp_ahead(dirn)); self.set_mode('AUTO'); return 'resumed'
        self.dr = None
        self.alert('GPS lost under trees: holding position (stopped safely, waiting for help)')
        self.outcome_text = 'no fix > 8 m: stopped safely + alert'
        return 'stopped'

    def next_wp_ahead(self, dirn, margin=3.0):
        """Mission index of the first waypoint at least `margin` m ahead along the lane (never one behind the tug)."""
        s_now = self.s_lat()[0]
        for i, p in enumerate(getattr(self, 'cur_pts', [])):
            if dirn * (self.S.lane.project(np.array(p))[0] - s_now) > margin: return i + 1
        return max(1, len(getattr(self, 'cur_pts', [1])))

    # ---------------- MANUAL manoeuvres ----------------
    def goto(self, tx, ty, v=0.35, tol=0.25, reverse=False, tmax=45, avoid=True, settle=True):
        t0 = self.w.t; bumps = 0; was_ok = True
        if reverse: v = min(v, 0.17)          # Rev G3 (F7): never reverse faster than 0.2 m/s (rear centre is lidar-blind)
        while True:
            yield
            if was_ok and not self.w.chain_ok: bumps += 1     # Rev G3: a bump strip opened the hard-wired chain
            was_ok = self.w.chain_ok
            if bumps >= 2:
                self.ev('goto: bump strip contact twice -> give up this leg'); self.stop(); break
            x, y, yaw = self.pose(); dx, dy = tx - x, ty - y; d = math.hypot(dx, dy)
            if d < tol: break
            if self.w.t - t0 > tmax: self.ev('goto timeout'); break
            hd = math.atan2(dy, dx) + (math.pi if reverse else 0)
            e = wrap(hd - yaw)
            if avoid and not reverse:
                ob = self.path_obstacle(0.5)
                if ob is not None and ob[0] < 0.35 and d > 0.8:
                    self.stop(); self._blk = self._blk or self.w.t
                    if self.w.t - self._blk > 5: self.ev('goto blocked by an object -> give up this leg'); self._blk = None; break
                    continue
                self._blk = None
            thr = (v * max(0.0, math.cos(e)) ** 3) * (-1 if reverse else 1)
            if d < 0.6 and settle: thr *= max(0.4, d / 0.6)
            self.drive(float(np.clip(-0.55 * e, -0.3, 0.3)), self.rev_thr(-thr) if reverse else self.thr_ctl(thr))
        if settle: self.stop(); yield from self.wait(0.6)

    def goto_lane(self, s_t, lat_t, v=0.35, via_lat=None, tol=0.3):
        """Follow the surveyed lane centre-line (offset via_lat) to s_t, then to (s_t, lat_t)."""
        s0, l0 = self.s_lat(); via = lat_t if via_lat is None else via_lat
        n = max(1, int(abs(s_t - s0) // 2.5))
        for s in np.linspace(s0, s_t, n + 1)[1:-1]:
            yield from self.goto(*self.S.lane.point(s, via), v=v, tol=0.6, settle=False)
        yield from self.goto(*self.S.lane.point(s_t, lat_t), v=v, tol=tol)

    def goto_safe(self, tx, ty, v=0.35, tol=0.3, clear=1.45):
        """goto with via-points round known bins/obstacles near the straight path (up to 3, nearest first)."""
        B = np.array([tx, ty])
        for it in range(3):
            x, y, _ = self.pose(); A = np.array([x, y]); hit = None
            for o in self.obst_pts:
                o = np.asarray(o, float)
                if np.linalg.norm(B - o) < 0.9 or np.linalg.norm(A - o) < 0.9: continue
                if float(seg_dist(o[None], A[None], B[None])[0]) < clear:
                    along = (o - A) @ (B - A)
                    if hit is None or along < hit[0]: hit = (along, o)
            if hit is None: break
            o = hit[1]; ab = (B - A) / (np.linalg.norm(B - A) + 1e-9); n = np.array([-ab[1], ab[0]]); best = None
            for k in (clear + 0.3, clear + 0.8):
                for sg in (1, -1):
                    V = o + sg * n * k
                    near = min([np.linalg.norm(V - np.asarray(q)) for q in self.obst_pts] + [9])
                    if self.S.in_fence(V, margin=0.2) and self.S.hedge_dist(V) > 0.7 and near > 1.0:
                        L = np.linalg.norm(V - A) + np.linalg.norm(B - V)
                        if best is None or L < best[0]: best = (L, V)
                if best is not None: break
            if best is None: break
            yield from self.goto(*best[1], v=v, tol=0.35, settle=False, avoid=False)
        yield from self.goto(tx, ty, v=v, tol=tol)

    def rev_thr(self, u):
        """Rev G3 (F7): reverse throttle with a speed trim on the measured ground speed so reversing never exceeds 0.2 m/s
        (open-loop feed-forward overshot to 0.22 m/s on the yard slope)."""
        k = getattr(self, '_rev_k', 0.9); v = self.vel
        if v > u + 0.008: k -= 0.08
        elif v < u - 0.02: k += 0.01
        self._rev_k = float(np.clip(k, 0.3, 1.2))
        g = -self.w.grade_here()                       # grade along the reversing direction (surveyed grade map)
        base = max(0.04, u + 0.03 + 0.9 * g * (1.4 if self.w.attached else 1.0))   # feed-forward both ways (downhill too)
        if v > 0.18: return -base * 0.3                # hard limiter on the measured speed
        return -base * self._rev_k

    def thr_ctl(self, v):
        if v == 0: return 0.0
        g = self.w.grade_here() * (1 if v > 0 else -1)      # feed-forward from the surveyed grade map
        return v + math.copysign(0.03 + 0.9 * max(0, g) * (1.4 if self.w.attached else 1.0), v)

    def pivot(self, yaw_t, tol=math.radians(4), tmax=40):
        t0 = self.w.t; open_t = 0.0
        while self.w.t - t0 < tmax:
            yield
            if not self.w.chain_ok:           # Rev G3: a bump strip opened the chain while pivoting -> give up this pivot
                open_t += 0.1
                if open_t > 3.0: self.ev('pivot: bump strip contact -> give up'); break
                continue
            e = wrap(yaw_t - self.pose()[2])
            if abs(e) < tol: break
            self.drive(float(np.clip(-0.5 * e, -0.2, 0.2)) - 0.04 * float(np.sign(e)), 0.0)
        self.stop(); yield from self.wait(0.6)

    def yard_uturn_zone(self, s_slot, l_slot):
        """Rev G6: lane-frame box (s range, lat range) swept by the planned yard U-turn for a home slot: start at s_slot-1 heading
        up-lane at lat l_slot+5.8, 180 deg CCW on R ~2.9-3.2 m (governed), towed bin off-tracking inside; + tug half-length/width."""
        s0 = s_slot + YARD_UTURN['ds']; lt = l_slot + YARD_UTURN['dlat']
        return (s0 - YARD_UTURN['R'] - 0.5 - TUG['front'] - 0.3, s0 + 1.6), (l_slot - 0.7, lt + 0.7)

    def yard_uturn_sweep(self, s_slot, l_slot, step=0.25):
        """Rev G6 (G4 open issue s24a): the ground the planned yard U-turn really sweeps, in x-y. Kinematic tug (start slot s-1 m,
        lat slot+5.8 m, facing up-lane, 180 deg CCW at R, then the 1.5 m line capture) towing the bin on the kingpin (bin yaw rate
        v/L sin(phi), phi clipped at the stop); tug and bin footprints + 0.25 m sampled on a 0.25 m grid. Returns world xy points."""
        R = YARD_UTURN['R'] if HITCH_CAP_DEG < 45 else 2.0
        x, y, yaw = self.S.pose(s_slot + YARD_UTURN['ds'], l_slot + YARD_UTURN['dlat'], math.pi); by = yaw; v = 0.3; dt = 0.2
        pts = set(); turned = 0.0; straight = 0.0; Lb = BIN['L']; cap = math.radians(HITCH_CAP_DEG)
        def add_box(cx, cy, cyaw, fx, rx, hw):
            c, s_ = math.cos(cyaw), math.sin(cyaw)
            for a_ in np.arange(-rx, fx + 1e-6, step):
                for b_ in np.arange(-hw, hw + 1e-6, step):
                    pts.add((round((cx + a_ * c - b_ * s_) / step) * step, round((cy + a_ * s_ + b_ * c) / step) * step))
        it_ = 0
        while straight < 3.0 and it_ < 1500:     # G6 s3: 3 m exit (was 1.5) - s24a ran into the car just after the turn
            it_ += 1
            w_ = v / R if turned < math.pi else 0.0
            if w_: w_ = hitch_gov(w_, v, wrap(yaw - by))     # G6 s3: the executed turn is hitch-governed (R_eff ~3.4 m, not 2.9)
            x += v * dt * math.cos(yaw); y += v * dt * math.sin(yaw); yaw = wrap(yaw + w_ * dt); turned += abs(w_) * dt
            if w_ == 0.0: straight += v * dt
            phi = wrap(yaw - by); by = wrap(by + v / Lb * math.sin(phi) * dt)
            if abs(wrap(yaw - by)) > cap: by = wrap(yaw - math.copysign(cap, wrap(yaw - by)))
            add_box(x, y, yaw, TUG['front'] + 0.25, TUG['rear'] + 0.1, TUG['half_w'] + 0.25)
            bx_, by_ = x - Lb * math.cos(by), y - Lb * math.sin(by)
            add_box(bx_, by_, by, BIN['d'] / 2 + 0.15, BIN['d'] / 2 + 0.15, BIN['w'] / 2 + 0.15)
        return np.array(sorted(pts))

    def points_view(self, Q):
        """Lidar free / occluded / unseen count for world points Q (same rules as zone_view)."""
        r = self.r.scan; x, y, yaw = self.pose()
        ox = x + TUG['lidar_x'] * math.cos(yaw); oy = y + TUG['lidar_x'] * math.sin(yaw); occl = unseen = 0; mp = self._scan_mapped(); hit = []
        for qx, qy in Q:
            d = math.hypot(qx - ox, qy - oy); b = int(round(math.degrees(wrap(math.atan2(qy - oy, qx - ox) - yaw)))) % 360
            rr = [r[(b + k) % 360] for k in (-1, 0, 1)] if r is not None else [np.nan]
            if d < 0.5 or d > 11.5 or any(np.isnan(v_) for v_ in rr): unseen += 1
            elif min(rr) < d - 0.12:
                if all(mp[(b + k) % 360] for k in (-1, 0, 1) if r[(b + k) % 360] < d - 0.12): unseen += 1
                else: occl += 1; hit.append((qx, qy))
        return dict(occl=occl, unseen=unseen, n=max(len(Q), 1), hit=hit[:5])

    def uturn(self, direction, R, name, line_lat=None):
        """180 deg turn on radius R (the bin in tow swings on the turntable); aborts at the geofence.
        Rev G4: with line_lat, the last ~95 deg are closed-loop: capture the line lat = line_lat in the new travel direction
        (open-loop G3 turns ended 0.4-1.1 m off: effective radius 1.07-1.28 x the command)."""
        self.state = 'UTURN'; self.leg = name; x, y, yaw0 = self.pose(); target = wrap(yaw0 + math.pi); v = 0.3; t0 = self.w.t
        s_a, l_a = self.s_lat(); cap_t = None
        while True:
            yield
            e = wrap(target - self.pose()[2])
            if line_lat is not None and abs(e) < math.radians(95):
                cap_t = cap_t or self.w.t
                s_, l_ = self.s_lat(); hl = self.S.lane.heading(s_); fdir = 1 if math.cos(wrap(target - hl)) > 0 else -1
                hdir = hl if fdir > 0 else wrap(hl + math.pi); el = (l_ - line_lat) * fdir
                hd = wrap(hdir - math.atan(0.9 * el)); eh = wrap(hd - self.pose()[2])
                if (abs(eh) < math.radians(6) and abs(el) < 0.2) or self.w.t - cap_t > 30: break
                w = float(np.clip(1.2 * eh, -v / R, v / R))
            else:
                if abs(e) < math.radians(8): break
                w = direction * v / R
            fx, fy = self.ahead(TUG['front'] + 0.3)
            if not self.S.fp_ok((fx, fy), 0.3):          # Rev G3: bumper + 0.3 m must stay >= 0.3 m inside the private boundary
                self.stop(); self.ev('U-turn would leave the geofence -> abort'); raise _Abort('U-turn blocked by geofence')
            if self.sc.get('uturn_stop', True):          # Rev G6 runtime stop: lidar return in the bumper arc on the turning side
                ob = self.turn_obstacle(direction)
                if ob is not None:
                    self.stop(); self.state = 'UTURN_HOLD'; t_h = self.w.t
                    self.ev('U-turn: object %.2f m from the bumper on the turn path -> STOP' % ob)
                    self.metrics.setdefault('uturn_stops', []).append(dict(t=round(self.w.t, 1), name=name, gap_m=round(ob, 2), truth_gap=round(self.truth_gap(), 2)))
                    while self.w.t - t_h < 60.0:
                        yield
                        if self.turn_obstacle(direction) is None and self.w.t - t_h > 3.0: break
                    else:
                        self.set_mode('HOLD'); self.alert('%s: something is in the turning path and has not moved for 60 s - holding with the bin, please clear it' % name)
                        self.outcome_text = 'U-turn path blocked -> holding + alert'; self.finish('alert', self.outcome_text); return
                    self.state = 'UTURN'; continue
            self.drive(-w * 0.43, self.thr_ctl(v))
        self.stop()
        if line_lat is None: yield from self.goto(*self.ahead(1.2), v=0.3, tol=0.3)     # G4: the line capture already straightened the bin
        else: yield from self.wait(0.6)
        self.metrics[name + '_hitch_max'] = round(self.w.hitch_max, 1)
        s_b, l_b = self.s_lat()
        self.metrics.setdefault('uturns', []).append(dict(name=name, start=[round(self.S.L - s_a, 2) if s_a > 300 else round(s_a, 2), round(l_a, 2)],
                                                          end=[round(self.S.L - s_b, 2) if s_b > 300 else round(s_b, 2), round(l_b, 2)], line=line_lat,
                                                          dur_s=round(self.w.t - t0, 1)))

    def reverse_dock(self, D, yawd, use_cam=True, max_extra=0.25, tag=None, dock=False):
        """Reverse onto the handle: the camera (PnP) refines the dock point while it can see tag 0, then the last
        part is blind on the last estimate + EKF/RTK pose; stops on the seat switch."""
        self.state = 'DOCK_REVERSE'; D = np.array(D, float); t0 = self.w.t; last_seen = None; blind_from = None
        if tag is None: tag = min(self.target_ids())          # Rev G3: handle-face tag of this trip's bin
        while True:
            yield
            x, y, yaw = self.pose(); d = np.array([math.cos(yawd), math.sin(yawd)])
            rel = np.array([x, y]) - D; along = rel @ d; e = rel @ np.array([-d[1], d[0]])
            if use_cam:
                img, _ = self.w.render_cam()
                rmin = 1.8 if self.w.night else 1.3     # Rev G: ignore close-in reads (IR saturation / partial tag) - go blind
                dets = [q for q in detect(img) if q[0] == tag and q[1] >= rmin]
                if dets:
                    pw, nyaw, _ = tag_to_world(dets[0], x, y, yaw, self.w.zxy(x, y))
                    Dm = pw[:2] + d * (DOCK_OFF - BIN['d'] / 2)
                    if abs(wrap(nyaw - yawd)) < math.radians(35):
                        D = 0.6 * D + 0.4 * Dm; last_seen = round(dets[0][1], 2)
                        if dets[0][1] < 3.2: yawd = wrap(yawd + 0.3 * wrap(nyaw - yawd))
                        self.last_det_summary = 'id%d @ %.2f m' % (tag, dets[0][1])
                else:
                    self.last_det_summary = 'blind (last tag %.2f m)' % last_seen if last_seen else 'no tag'
                    if last_seen and blind_from is None: blind_from = along
            seated = (self.w.dock_seat or {}).get('seat', False) if dock else self.w.seat
            # Rev G3 (F7): software-qualified crossbeam contact. The crossbeam switch closes on the bin's wheels (or the dock
            # plate) only in the last few cm. Contact while the lidar/tag estimate says the target is still > 0.3 m away means
            # something else is in the centre gap (a child, a foot): stop at once and alert.
            if self.w.crossbeam and not seated and along > 0.3:
                self.stop(); self.set_mode('HOLD')
                ev = dict(t=round(self.w.t, 1), est_dist_m=round(along, 2), v=round(self.w.v, 3), target='dock' if dock else 'bin')
                t_c = self.w.t; p0 = self.w.push_m
                while abs(self.w.v) > 0.003 and self.w.t - t_c < 3: yield
                ev.update(push_m=round(self.w.push_m, 3), stop_s=round(self.w.t - t_c, 2))
                self.metrics.setdefault('crossbeam_stops', []).append(ev)
                self.alert('crossbeam contact %.2f m before the %s (nothing should touch it yet): stopped - something/someone in the centre gap behind the tug'
                           % (along, 'dock' if dock else 'bin'))
                return 'blocked'
            if not self.w.chain_ok and along > 0.6:          # a rear corner bump strip opened the hard-wired chain well before the target
                self.stop()
                self.metrics.setdefault('corner_strip_stops', []).append(dict(t=round(self.w.t, 1), est_dist_m=round(along, 2), reason=self.w.chain_reason))
                self.alert('rear corner bump strip hit %.2f m before the %s: hard-wired stop' % (along, 'dock' if dock else 'bin'))
                return 'blocked'
            if seated:
                self.stop(); self.ev('%s switch closed (lateral err est %.3f m)' % ('dock contact' if dock else 'seat', e))
                self.metrics.setdefault('charge_dock' if dock else 'dock', []).append(dict(ok=True, last_tag_range=last_seen, blind_from_m=None if blind_from is None else round(blind_from, 2)))
                return True
            if along < -max_extra or ((self.w.bumper or not self.w.chain_ok or self.w.crossbeam) and abs(self.w.v) < 0.01 and along < 0.6) or self.w.t - t0 > 120:
                self.stop(); self.ev('dock missed (along %.2f, lateral %.2f, bumper %s)' % (along, e, self.w.bumper))
                self.metrics.setdefault('charge_dock' if dock else 'dock', []).append(dict(ok=False, last_tag_range=last_seen))
                return False
            u = 0.16 if along > 1.2 else 0.11          # Rev G3 (F7): reverse <= 0.2 m/s (was 0.22 commanded)
            eh_t = math.asin(float(np.clip(1.6 * e / max(along, 0.4), -0.45, 0.45))) if along > 0.15 else 0.0
            eh = wrap(yaw - yawd)
            wcmd = 2.0 * (eh_t - eh)                       # desired CCW yaw rate
            self.drive(float(np.clip(-0.43 * wcmd, -0.5, 0.5)), self.rev_thr(u))

    def grab(self):
        self.state = 'GRAB'
        if not (yield from self.pre_motion('tilt')): return False
        self.servo(1900); t0 = self.w.t
        while not self.w.attached and self.w.t - t0 < 8: yield
        if self.w.attached:
            self.ev('hook latched, bin tilted on its wheels')
            # Rev G3 (ported from revG_alt): bin mass from the tilt-actuator holding current (calibrated empty / full)
            I = float(np.mean([self.w.tilt_current() for _ in range(10)])); m_est = (I - 1.4) / 0.095
            self.metrics.setdefault('tilt_current', []).append(dict(leg=self.leg, target=self.target, amps=round(I, 2), mass_est_kg=round(m_est, 1),
                                                                    truth_kg=round(self.w.bin_mass, 1)))
            self.ev('tilt current %.2f A -> bin mass ~%.0f kg' % (I, m_est))
            if self.leg == 'seek' and m_est > 25.0:
                self.alert('%s bin NOT emptied: still ~%.0f kg at pickup (tilt current %.1f A). Bringing it home anyway (21:00 bye-law)' % (self.target, m_est, I))
                self.outcome_text = 'uncollected bin detected -> alert, towed home'; self.metrics['not_emptied'] = True
            return True
        self.servo(1100); return False

    def crossbeam_recover(self, yawd, what):
        """Rev G3 (F7): after a crossbeam stop, pull forward 0.4 m (front lidar covers that way), then wait >= 45 s with the
        crossbeam and both rear bump strips clear before one more reverse. Returns True if clear (retry allowed)."""
        self.state = 'DOCK_HOLD'; self.set_mode('MANUAL'); yield from self.wait(0.5)
        if self.w.chain_ok: yield from self.goto(*self.ahead(0.4), v=0.15, tol=0.12)
        t0 = self.w.t; clear_since = None
        while self.w.t - t0 < 240:
            yield
            ok = (not self.w.crossbeam) and self.w.chain_ok
            clear_since = (clear_since or self.w.t) if ok else None
            if clear_since is not None and self.w.t - t0 >= 45 and self.w.t - clear_since >= 10:
                self.ev('%s: centre gap clear -> one more slow reverse (3 s warning)' % what)
                self.warn = True; yield from self.wait(3.0); self.warn = False; yield from self.pivot(yawd); return True
        return False

    def release(self, name, pull=True):
        """Rev G3 (F4 + F2). Pinch-zone check first: if it is refused, the bin stays hooked, the tug HOLDs and alerts, and
        it never releases on a timeout - only after the zone has been clear again for 10 s (fresh 3 s warning); if it never
        clears it keeps holding (owner alerted). Then the release itself: the latch switch must open; if the pawl sticks,
        mast wiggle (re-tilt 10 deg and lower) up to 2 times; then hold, alert and ask for the manual release lever.
        Returns False if the bin is still hooked."""
        self.state = 'RELEASE'; self.leg = name; self.stop(); yield from self.wait(0.5)
        if not (yield from self.pre_motion('release')):
            self.set_mode('HOLD'); t0 = self.w.t; hold_max = self.sc.get('release_hold_max', 600.0)
            self.release_hold = dict(t=round(t0, 1)); self.state = 'RELEASE_HOLD'
            self.ev('release refused -> HOLD with the bin hooked (no timeout release); waiting for the zone to clear')
            while True:
                ok = yield from self.zone_clear_for(10.0, hold_max - (self.w.t - t0))
                if ok:
                    self.set_mode('MANUAL'); self.state = 'RELEASE'
                    if (yield from self.pre_motion('release')): break
                    continue
                self.release_hold.update(held_s=round(self.w.t - t0, 1), released=False)
                self.metrics['release_hold'] = self.release_hold
                self.alert('bin still hooked at the pad after %.0f min: pinch zone never cleared - holding, please check' % ((self.w.t - t0) / 60))
                self.outcome_text = 'release refused (pinch zone) -> holding bin + alert'; return False
            self.release_hold.update(held_s=round(self.w.t - t0, 1), released=True); self.metrics['release_hold'] = self.release_hold
            self.ev('pinch zone clear again after %.0f s -> release' % (self.w.t - t0))
        tries = 0
        while True:
            self.servo(1100); t0 = self.w.t
            while self.w.attached and self.w.t - t0 < 10: yield
            if not self.w.attached: break
            if tries >= 2:
                self.set_mode('HOLD'); self.state = 'RELEASE_STUCK'
                self.metrics['release_stuck'] = dict(wiggles=tries, released=False)
                self.alert('bin will not release (latch switch still closed after 2 mast wiggles): holding on the pad - use the manual release lever on the cam bar (no tools)')
                self.outcome_text = 'pawl jammed -> holding + alert (manual lever)'; return False
            tries += 1; self.state = 'RELEASE_WIGGLE'
            self.ev('latch switch still closed -> mast wiggle %d (re-tilt ~10 deg, lower again)' % tries)
            self.servo(1900); yield from self.wait(0.9); self.servo(1100); yield from self.wait(0.5)
        if tries: self.metrics['release_stuck'] = dict(wiggles=tries, released=True)
        self.ev('bin released%s' % (' after %d mast wiggle(s)' % tries if tries else '')); yield from self.wait(0.5)
        self.w.bin_mass = M_BIN_EMPTY          # (scenario bookkeeping: the bin is emptied by the crew before pickup)
        if self.w.bin is not None and name in ('release_mouth', 'release_pad', 'release_route', 'teach_drop'):   # G6 s3: + teach_drop (s21a pivoted into its own bin)
            self.placed = getattr(self, 'placed', []) + [np.array([self.w.bin['x'], self.w.bin['y']])]   # known bin on the pad (companion's estimate = behind the hook)
        if self.w.bin is not None: self.log_drop(name)
        if not pull: return True
        # Rev G2: the pull-away point must sit well inside the geofence. Slide it toward the lane centre-line until it is >= 0.3 m in.
        tgt = np.array(self.ahead(1.0)); sp, lp = self.S.lane.project(tgt)
        for k in range(12):
            if self.S.in_fence(tgt, margin=0.3): break
            tgt = np.array(self.S.pose(sp, lp * (1 - (k + 1) / 12.0), 0.0)[:2])
        yield from self.goto(*tgt, v=0.25, tol=0.2)
        return True

    def zone_clear_for(self, need, tmax):
        """Pinch-zone monitor while holding (same 1.5 m lidar rule as pre_motion). True once clear for `need` s."""
        t0 = self.w.t; clear_since = None
        while self.w.t - t0 < max(tmax, 0):
            yield
            busy = self.pinch_busy()
            clear_since = None if busy else (clear_since or self.w.t)
            self.warn = busy
            if clear_since is not None and self.w.t - clear_since >= need: self.warn = False; return True
        self.warn = False; return False

    def pinch_busy(self): return self.pinch_eval()[0]

    def occupied_slots(self):
        """Rev G4: programmed bin slots where one of Brian's OTHER bins should be standing right now (home spots side by side in
        the yard, pad spots A/M/F of the drop layout), plus the measured spots of bins released this evening."""
        out = []; bins = list(getattr(self.w, 'bins', {}) or {})
        if not self.sc.get('multi') or not bins: return [np.asarray(p, float) for p in getattr(self, 'placed', [])]
        pads = getattr(self, 'pad_for', None) or {}
        done = [b for b in self.bins_done if b != self.target]
        for b in bins:
            if b == self.target: continue
            hs = SC.HOME_SPOTS[b]; home = np.asarray(self.S.lane.point(hs['s'], hs['lat']))
            pad = np.asarray(self.layout.bin_pose(self.S, pads[b])[:2]) if b in pads else None
            if self.mission == 'drop': out.append(pad if (b in done and pad is not None) else home)
            else: out.append(home if b in done else (pad if pad is not None else home))
        out += [np.asarray(p, float) for p in getattr(self, 'placed', [])]
        return out

    def pinch_eval(self):
        """Pinch-zone rule (Rev G): anything unmapped within 1.5 m of the tug sides/front (lidar) blocks an actuator motion.
        Rev G4: a cluster is exempt ONLY if it is bin-sized (0.25-1.0 m extent), stationary for >= 1.5 s, and its centre is within
        0.6 m of an occupied programmed bin slot (adjacent bin on its home spot / pad spot). A person or a vehicle in the zone
        is never exempt: a person standing against the bin merges with it (extent > 1.0 m), one standing apart is a separate
        cluster away from the slot, a vehicle is > 1.45 m. Returns (busy, info)."""
        P, _ = self.scan_points(); x, y, yaw = self.pose()
        if not len(P): return False, None
        rel = P - np.array([x, y]); fwd = rel @ np.array([math.cos(yaw), math.sin(yaw)])
        d = np.linalg.norm(rel, axis=1) - TUG['half_w']
        near = (d < 1.5) & (fwd > -0.3)
        for o in self.obst_pts: near &= np.linalg.norm(P - np.asarray(o, float), axis=1) > 0.8
        if not near.any(): return False, None
        if not self.sc.get('slot_exempt', True): return True, 'G3 rule'
        slots = self.occupied_slots()
        Z = (np.linalg.norm(rel, axis=1) < 1.5 + TUG['half_w'] + 1.3)       # look a bit beyond the zone so a cluster is seen whole
        Pz = P[Z]; nz = near[Z]; lab = -np.ones(len(Pz), int); k = 0
        for i in range(len(Pz)):
            if lab[i] >= 0: continue
            st = [i]; lab[i] = k
            while st:
                j = st.pop(); dd = np.linalg.norm(Pz - Pz[j], axis=1)
                for q in np.where((dd < 0.35) & (lab < 0))[0]: lab[q] = k; st.append(q)
            k += 1
        hist = getattr(self, '_slot_hist', []); hist = [h for h in hist if self.w.t - h[0] < 4.0]; now = []; busy = None; ex = []
        for c in range(k):
            m = lab == c
            if not np.any(nz & m): continue
            Q = Pz[m]; ext = float(np.max(np.linalg.norm(Q[:, None] - Q[None], axis=2))) if len(Q) > 1 else 0.0
            ctr = Q.mean(0); away = ctr - np.array([x, y]); away /= np.linalg.norm(away) + 1e-9; ctr = ctr + away * 0.2   # near faces only
            ds = min([np.linalg.norm(ctr - sl) for sl in slots] + [9.0])
            now.append(ctr)
            old = [h for h in hist if self.w.t - h[0] >= 1.5]
            still = any(min([np.linalg.norm(ctr - c2) for c2 in h[1]] + [9]) < 0.15 for h in old)
            if 0.25 <= ext <= 1.0 and ds < 0.6 and still: ex.append(dict(ctr=[round(float(v), 2) for v in ctr], ext=round(ext, 2), slot_d=round(ds, 2))); continue
            busy = dict(ext=round(ext, 2), slot_d=round(ds, 2), n=int(m.sum()), still=still)
        hist.append((self.w.t, now)); self._slot_hist = hist
        if ex and busy is None and (not self.slot_exempt_log or self.w.t - self.slot_exempt_log[-1]['t'] > 5):
            self.slot_exempt_log.append(dict(t=round(self.w.t, 1), state=self.state, target=self.target, exempt=ex))
            self.metrics['slot_exempt'] = self.slot_exempt_log[-6:]
        return busy is not None, busy

    # ---------------- house end ----------------
    def house_grab(self):
        self.leg = 'house_dock'; self.state = 'TO_BIN'; hb = SC.HOME_SPOTS.get(self.target, SC.HOUSE_BIN)
        self.obst_pts = [np.asarray(self.S.lane.point(v['s'], v['lat'])) for k, v in SC.HOME_SPOTS.items() if k != self.target and self.sc.get('multi')]
        if self.home_override: hb = dict(s=self.home_override['s'], lat=self.home_override['lat'])
        yield from self.goto_lane(hb['s'] + DOCK_OFF + 3.8, hb['lat'] + 1.2, via_lat=0.3)
        x, y, yaw = self.S.pose(hb['s'], hb['lat'], 0.0)
        if self.home_override: x, y, yaw = self.home_override['x'], self.home_override['y'], self.home_override['yaw']   # Rev G4: taught home pose
        yield from self.pivot(yaw)
        D = (x + DOCK_OFF * math.cos(yaw), y + DOCK_OFF * math.sin(yaw))
        attempt = 0; blocked = 0
        while attempt < 2:                             # Rev G: re-dock once at the house too
            ok = yield from self.reverse_dock(D, yaw)
            if ok == 'blocked':                        # Rev G3 (F7): someone in the centre gap
                blocked += 1
                if blocked > 1 or not (yield from self.crossbeam_recover(yaw, 'house dock')):
                    self.outcome_text = 'centre-gap contact twice -> drop aborted, alert'
                    self.alert('drop aborted: repeated contact in the centre gap behind the tug at the house'); raise _Abort('centre gap contact at the house')
                continue
            if ok and (yield from self.grab()): return
            attempt += 1
            if attempt == 1:
                self.ev('house dock missed -> pull forward and re-dock once'); self.state = 'REDOCK'
                yield from self.goto(D[0] + 2.4 * math.cos(yaw), D[1] + 2.4 * math.sin(yaw), v=0.3); yield from self.pivot(yaw)
        self.alert('could not dock the bin at the house'); raise _Abort('could not dock the bin at the house')

    def place_house(self):
        """After the yard U-turn the tug faces down-lane with the empty bin trailing: stop with the bin on its home spot."""
        self.leg = 'place_house'; self.state = 'PLACE_BIN'; hb = SC.HOME_SPOTS.get(self.target, SC.HOUSE_BIN)
        if self.home_override: hb = dict(s=self.home_override['s'], lat=self.home_override['lat'])
        if self.home_target: hb = dict(s=self.home_target['s'], lat=self.home_target['lat'])     # Rev G4 g): alternate home slot
        # straight pull along the home-spot line so the trailer lines up before release
        yield from self.goto(*self.S.lane.point(hb['s'] + BIN['L'] - 2.0, hb['lat']), v=0.3, tol=0.35, settle=False)
        yield from self.goto(*self.S.lane.point(hb['s'] + BIN['L'], hb['lat']), v=0.25, tol=0.2)
        r = yield from self.release('place_house')
        if r is False: self.finish('alert', self.outcome_text); yield
        hx, hy, hyaw = self.S.pose(hb['s'], hb['lat'], 0.0); self.placement('home:' + self.target, (hx, hy, hyaw))

    def park(self):
        """Rev G: reverse onto the charging dock exactly like docking a bin - rear camera reads dock tag 20, blind last part,
        dock V-guides line up the free-yawing rear frame, crossbeam contacts close. Rev G3: then the charge-current check:
        dock voltage must be seen on the contacts and (pack >= +3 C) charge current must flow within 5 s; otherwise re-seat once
        (pull out 1.5 m, reverse again), then alert 'not charging'. Below +3 C charging is deferred (temperature gate), not a fault."""
        self.leg = 'park'; self.state = 'PARK'; S = self.S
        x, y, yaw = S.pose(SC.DOCK['s'], SC.DOCK['lat']); h = np.array([math.cos(yaw), math.sin(yaw)])
        spots = SC.HOME_SPOTS.values() if self.sc.get('multi') else [SC.HOUSE_BIN]
        self.obst_pts = [np.asarray(S.lane.point(v['s'], v['lat'])) for v in spots]   # bins we may have placed at home
        attempt = 0; blocked = 0; why = ''
        n_try = 3   # G4 fix: re-seat up to twice (G3 s20a/s10a missed the 1st seat; G4 s20a trip 3 missed 2)
        while attempt < n_try:
            pre = np.asarray(S.lane.point(SC.DOCK['s'] + 2.6 + (0.8 if attempt else 0.0), 0.0))      # G4 fix: longer straight re-approach
            if np.linalg.norm(np.array(self.pose()[:2]) - pre) > 6.0: yield from self.goto_lane(SC.DOCK['s'] + 6.0, 0.6, via_lat=0.5, v=0.35)
            yield from self.goto_safe(*pre, v=0.3, tol=0.3)
            yield from self.pivot(yaw, tol=math.radians(3))
            self.state = 'PARK_DOCK'
            ok = yield from self.reverse_dock((x, y), yaw, tag=20, dock=True, max_extra=0.15)
            if ok == 'blocked':
                blocked += 1
                if blocked > 1 or not (yield from self.crossbeam_recover(yaw, 'charging dock')):
                    self.state = 'DOCKED'; self.set_mode('HOLD'); self.outcome_text = 'centre-gap contact at the dock -> parked short + alert'
                    self.alert('not docked: repeated contact in the centre gap behind the tug at the dock; parked short of it'); yield; return
                continue
            ds = self.w.dock_seat or {}
            yield from self.wait(5.0) if (ok and ds.get('seat')) else iter(())
            ds = self.w.dock_seat or {}; v_ok = bool(self.w.dock_v); amps = self.w.charge_a; cold = (self.w.pack_c if self.w.pack_c is not None else self.w.air_c) < 3.0
            rec = dict(attempt=attempt + 1, ok=bool(ok and ds.get('seat')), lat_mm=round(1000 * ds.get('lat', 0)), yaw_deg=round(math.degrees(ds.get('dyaw', 0)), 1),
                       dock_v=v_ok, charge_a=round(amps, 2), pack_c=self.w.air_c)
            self.metrics.setdefault('charge_contacts', []).append(rec)
            if ok is True and v_ok and (amps > 0.1 or cold):
                self.state = 'DOCKED'; self.set_mode('HOLD')
                if amps > 0.1:
                    self.ev('docked: charge contacts closed (crossbeam lateral %+.0f mm, yaw %+.1f deg), charge current %.1f A -> charging'
                            % (1000 * ds['lat'], math.degrees(ds['dyaw']), amps))
                else:
                    self.ev('docked: contacts closed, dock powers the bus; charging DEFERRED (pack %.1f C < +3 C temperature gate)' % (self.w.pack_c if self.w.pack_c is not None else self.w.air_c))
                    self.metrics['charge_deferred_cold'] = True
                    if self.energy_avail() < TRIP_WH: self.alert('docked but cannot charge below +3 C and only %.0f Wh above reserve' % self.energy_avail())
                yield; return
            why = ('contacts not seated' if ok is not True else ('no dock voltage on the contacts' if not v_ok else 'dock voltage but NO charge current (%.1f A)' % amps))
            attempt += 1
            if attempt >= n_try: break
            self.ev('charge check failed (%s) -> pull forward 1.5 m and re-seat' % why)
            yield from self.goto(*(np.array(self.pose()[:2]) + h * 1.5), v=0.3)
        self.ev('charge check failed (%s) after %d seatings' % (why, attempt))
        self.state = 'DOCKED'; self.set_mode('HOLD')
        self.alert('not charging: %s after %d re-seat(s) (pack %.0f %%) - check the dock contacts / charger' % (why, attempt - 1, 100 * self.w.soc))
        self.outcome_text = 'not charging -> alert'
        yield

    # ---------------- evening: find, identify, recover, dock ----------------
    def seek(self):
        self.leg = 'seek'; self.state = 'SEEK_SCAN'; S = self.S; L = S.L
        pad = getattr(self, '_seek_pad', 'A')
        prior = self._seek_prior if self._seek_prior is not None else self.layout.spot(S, pad); prior_xy = S.lane.point(prior['s'], prior['lat'])
        lookouts = [(L - 16, 0.0), (L - 12.5, 0.0)] if pad == 'A' else [(prior['s'] - 7.0, -0.5), (prior['s'] - 5.0, -0.5)]
        self.ignore_ids = set()
        for li, lo in enumerate(lookouts):
            if li > 0:
                yield from self.goto(*S.lane.point(*lo), v=0.3); self.state = 'SEEK_SCAN'
            yield from self.wait(1.5)
            cands, big = self.lidar_candidates()
            self.ev('lidar scan: %d bin-sized object(s), %d large object(s)' % (len(cands), len(big)))
            cands.sort(key=lambda c: np.linalg.norm(c['c'] - prior_xy))
            self.obst_pts = [c['c'] for c in cands] + [b['c'] for b in big]
            for c in cands:
                if any(np.linalg.norm(c['c'] - np.array(i)) < 0.6 for i in self.ignore_ids): continue
                if S.boundary_dist(c['c']) < 0.45 or not S.in_fence(c['c'], margin=-S.FENCE_IN - 0.2):
                    # Rev G3 legal fence: a bin whose centre is not >= 0.45 m inside the private boundary is on the public verge/road
                    rd = S.road_dist(c['c'])
                    why = 'in the public road' if rd < S.road_half + 0.3 else 'on the public verge, %.1f m from the road centre (private ground starts at %.1f m)' % (rd, S.boundary)
                    self.alert('bin-sized object %s, %.1f m from the drop spot - not entering the road' % (why, np.linalg.norm(c['c'] - prior_xy)))
                    self.outcome_text = 'bin outside geofence -> alert, home'; return 'alert'
                if c['long']:
                    yield from self.view(c)
                    self.alert('bin lying on its side (lidar outline %.2f m long)' % c['dims'][0])
                    self.outcome_text = 'tipped bin -> alert, home'; return 'alert'
                res = yield from self.handle_candidate(c)
                if res in ('grabbed', 'alert'): return res
            if big and li == len(lookouts) - 1:
                self.alert('bin not reachable: vehicle-sized object (%.1f m) blocks the mouth' % max(b['ext'] for b in big))
                self.outcome_text = 'blocked by parked car -> alert, home'; return 'alert'
        self.alert('bin not found near the drop spot (not searching beyond the geofence)'); self.outcome_text = 'bin not found -> alert, home'; return 'alert'

    def lidar_candidates(self):
        P, _ = self.scan_points()
        cands, big = [], []
        if len(P) < 3: return cands, big
        x, y, yaw = self.pose(); o = np.array([x, y])
        lab = -np.ones(len(P), int); k = 0
        for i in range(len(P)):
            if lab[i] >= 0: continue
            st = [i]; lab[i] = k
            while st:
                j = st.pop(); d = np.linalg.norm(P - P[j], axis=1)
                for q in np.where((d < 0.35) & (lab < 0))[0]: lab[q] = k; st.append(q)
            k += 1
        for c in range(k):
            Q = P[lab == c]
            if len(Q) < 3: continue
            ext = float(np.max(np.linalg.norm(Q[:, None] - Q[None], axis=2)))
            if ext > 1.45: big.append(dict(c=Q.mean(0), ext=ext)); continue
            if ext < 0.25: continue
            (cx, cy), (a, b), ang = cv2.minAreaRect(Q.astype(np.float32))
            dims = sorted([a, b], reverse=True); long = dims[0] > 0.95 or ext > 1.05
            if not long and len(Q) >= 6:      # Rev G: L-shape (closeness) fit for the axis - robust to one-and-a-bit faces seen
                ang = l_shape_yaw(Q)
            ctr = np.array([cx, cy]); away = ctr - o; away /= np.linalg.norm(away) + 1e-9
            ctr = ctr + away * max(0.0, 0.33 - dims[1] / 2)          # only the near faces are seen: push centre away
            cands.append(dict(c=ctr, yaw90=math.radians(ang), dims=[round(float(dims[0]), 2), round(float(dims[1]), 2)], long=long, n=len(Q)))
        return cands, big

    def room_ok(self, D, yawd, length=2.6, obstacles=()):
        """The corridor from the dock point out along the handle direction must be clear (hedges, geofence, other objects)."""
        d = np.array([math.cos(yawd), math.sin(yawd)])
        for t in np.arange(0.0, length + 0.01, 0.25):
            p = np.array(D) + d * t
            for sgn in (-1, 1):
                q = p + sgn * np.array([-d[1], d[0]]) * (TUG['half_w'] + 0.05)
                if self.S.hedge_dist(q) < 0.12 or not self.S.in_fence(q, margin=-0.15): return False
                for ob in obstacles:
                    if np.linalg.norm(q - ob) < 0.25: return False
            f = p + d * TUG['front']
            if self.S.hedge_dist(f) < 0.12 or not self.S.in_fence(f, margin=-0.15): return False
        return True

    def view(self, c):
        """Approach a candidate face-on, rear first, until the rear camera reads a tag. None = no room to look."""
        self.state = 'VIEW_ID'; S = self.S; x, y, yaw = self.pose()
        cands_v = []; offs = getattr(self, '_view_offset', 0.0)
        for k in range(4):
            n = wrap(c['yaw90'] + k * math.pi / 2); nv = np.array([math.cos(n + offs), math.sin(n + offs)]); P = None
            others = [np.asarray(o, float) for o in self.obst_pts if np.linalg.norm(np.asarray(o) - c['c']) > 1.1]
            for dist in (3.5, 3.0, 2.6):
                Q = c['c'] + nv * dist
                # line of sight from the view pose to the face must not pass another object (e.g. a neighbour's bin)
                blocked = any(float(seg_dist(o[None], Q[None], c['c'][None])[0]) < 0.75 for o in others)
                if S.in_fence(Q, margin=0.0) and S.hedge_dist(Q) > 0.75 and not blocked: P = Q; break
            if P is None: continue
            score = np.linalg.norm(P - np.array([x, y])) + (1.0 if dist < 3.0 else 0.0)
            if offs == 0.0 and any(abs(wrap(n - sk)) < math.radians(30) for sk in getattr(self, '_view_skip', ())): continue   # Rev G2: face already tried
            cands_v.append((score, k, P, n))
        if not cands_v and getattr(self, '_view_skip', None) and offs == 0.0 and not getattr(self, '_oblique_done', False):
            self._view_offset = math.radians(25); self._oblique_done = True; self.ev('every reachable face tried -> one oblique re-look (25 deg)')
            r = yield from self.view(c); self._view_offset = 0.0; return r
        if not cands_v:
            self._view_last_n = None
            return [] if getattr(self, '_view_skip', None) else None    # Rev G2: all faces tried -> 'no tag', not 'no room'
        cands_v.sort(key=lambda q: q[0])
        self._view_last_n = None
        for i, (_, _, P, n) in enumerate(cands_v[:3]):      # if the path to a view pose is blocked, try the next one
            yield from self.goto_safe(*P, v=0.35, tol=0.3)
            self._view_last_n = n
            if np.linalg.norm(np.array(self.pose()[:2]) - P) < 0.6: break
            self.ev('view pose %d not reached -> try another face' % (i + 1))
        # Rev G: face the bin first and re-measure its outline with the front lidar from ~3 m (two faces visible -> axis to a
        # few deg). While the rear camera looks at the bin the lidar cannot see it (rear arc occluded by the tug body).
        self._view_lc = None
        x, y, _ = self.pose(); yield from self.pivot(math.atan2(c['c'][1] - y, c['c'][0] - x)); yield from self.wait(1.0)
        self._view_all = self.lidar_candidates()[0]          # Rev G2: kept for re-picking the outline once the tag is read
        near = [k for k in self._view_all if np.linalg.norm(k['c'] - np.asarray(c['c'])) < 1.0 and not k['long']]
        if near:
            self._view_lc = min(near, key=lambda k: np.linalg.norm(k['c'] - np.asarray(c['c'])))
            self.ev('close lidar outline: %.2f x %.2f m, axis %.0f deg' % (self._view_lc['dims'][0], self._view_lc['dims'][1], math.degrees(self._view_lc['yaw90'])))
        yield from self.pivot(n)
        dets = []; img = None
        for k in range(15):
            yield
            img, _ = self.w.render_cam(); dets = detect(img)
            if dets: break
        tries = 0
        while not dets and tries < 12:           # creep back toward the face (night range ~3.8 m)
            tries += 1; x, y, yaw = self.pose()
            self.drive(0, self.thr_ctl(-0.15)); yield from self.wait(0.6); self.stop(); yield
            if np.linalg.norm(np.array([x, y]) - c['c']) < 2.2: break
            img, _ = self.w.render_cam(); dets = detect(img)
        self.stop()
        if dets:
            self.last_det_summary = 'ids %s @ %.2f m' % (sorted(set(q[0] for q in dets)), min(q[1] for q in dets))
            self.metrics.setdefault('id_ranges', []).append(round(min(q[1] for q in dets), 2))
            self.r.ev('cam', 'ArUco: ' + self.last_det_summary)
        return dets

    def handle_candidate(self, c):
        self._known = None; self._view_skip = []; self._predock_fail = 0; self._oblique_done = False; self._trims = 0; self._avoid_pts = []
        for attempt in range(6):
            known = getattr(self, '_known', None); self._known = None
            if known is not None:      # Rev G2: after a lidar-confirmed nudge the bin's identity is known and its pose re-measured
                ctr, byaw = known; q = (1,)
                self.ev('after nudge: lidar pose %.0f deg, identity already known -> no re-view' % math.degrees(byaw))
                self.metrics.setdefault('bin_estimates', []).append(dict(face='nudge', est=[round(float(ctr[0]), 2), round(float(ctr[1]), 2), round(math.degrees(byaw), 1)],
                    truth=[round(self.w.bin['x'], 2), round(self.w.bin['y'], 2), round(math.degrees(self.w.bin['yaw']), 1)]))
            else:
                dets = yield from self.view(c)
                if dets is None:
                    self.alert('no room to approach or identify the bin (hedge / geofence)'); self.outcome_text = 'no room -> alert, home'; return 'alert'
                if not dets:
                    # Rev G2: a face can be unreadable (tag dirty, edge-on, glare): look from up to two other faces before alerting
                    self._view_skip = getattr(self, '_view_skip', []) + ([self._view_last_n] if self._view_last_n is not None else [])
                    if len(self._view_skip) <= 2 and self._view_last_n is not None:
                        self.ev('no tag readable from this face -> try another face'); continue
                    self.alert('bin-like object but no tag readable'); self.outcome_text = 'no tag -> alert, home'; return 'alert'
                tid = self.target_ids()
                ours = [q for q in dets if q[0] in tid]          # Rev G3: this trip's bin = its own 4-tag range (black 0-3, green 4-7, brown 30-33)
                if not ours:
                    own = sorted(set(owner_of(q[0]) for q in dets if id0_of(q[0]) in OUR_ID0))
                    if own: self.ev('tag ids %s = our %s bin, not this trip\'s %s bin -> leave it' % (sorted(set(q[0] for q in dets)), '/'.join(own), self.target))
                    else: self.ev('tag ids %s are not ours -> ignore that bin' % sorted(set(q[0] for q in dets)))
                    self.metrics.setdefault('ignored_tags', []).append(sorted(set(q[0] for q in dets)))
                    if not own: self.metrics['ignored_neighbour'] = sorted(set(q[0] for q in dets))
                    self.ignore_ids.add(tuple(c['c'])); return 'next'
                q = min(ours, key=lambda d: abs(d[2])); x, y, yaw = self.pose()      # most central tag in the frame
                pw, nyaw, _ = tag_to_world(q, x, y, yaw, self.w.zxy(x, y))
                byaw = wrap(nyaw - FACE_OFF[q[0]]); ctr = pw[:2] - np.array([math.cos(nyaw), math.sin(nyaw)]) * FACE_HALF[q[0]]
                # fuse with the lidar outline: the camera gives identity + which side is the handle, the lidar rectangle
                # gives the centre and the axis (PnP yaw from a 22 cm tag at 3 m is only good to ~10-25 deg)
                # Rev G fix (HANDOVER s.13 item 1): the lidar OVERRULES the camera. PnP yaw from a 22 cm tag can be 90-180 deg wrong,
                # and at night the PnP position can be ~0.3 m off too. The lidar outline gives the bin axis (mod 90 deg) and a good
                # centre. Physical constraint: a tag can only be read if its face normal points at the camera, so the seen face's
                # normal is the lidar axis pointing from the outline centre toward the camera (within 60 deg). If two axes qualify
                # (diagonal view) the PnP yaw picks between them. The tag ID then says which face it is.
                pnp_yaw = byaw; fused = 'pnp only'
                lcs = ([self._view_lc] if getattr(self, '_view_lc', None) is not None else []) + [c]
                lc = lcs[0]
                if np.linalg.norm(np.asarray(lc['c']) - pw[:2]) >= 1.0:      # Rev G2: outline was another bin (two bins in view) ->
                    alt = [k for k in (getattr(self, '_view_all', None) or []) + self.lidar_candidates()[0]
                           if not k['long'] and np.linalg.norm(np.asarray(k['c']) - pw[:2]) < 0.9]
                    if alt: lc = min(alt, key=lambda k: np.linalg.norm(np.asarray(k['c']) - pw[:2])); self.ev('lidar outline re-picked at the tag position')
                if np.linalg.norm(np.asarray(lc['c']) - pw[:2]) < 1.0:       # the tag sits on a face of this outline
                    camp = np.array([x + TUG['cam_x'] * math.cos(yaw), y + TUG['cam_x'] * math.sin(yaw)])
                    tocam = math.atan2(*(camp - np.asarray(lc['c']))[::-1])
                    axes = [wrap(lc['yaw90'] + k * math.pi / 2) for k in range(4)]
                    ok_ax = [a_ for a_ in axes if abs(wrap(a_ - tocam)) < math.radians(60)] or [min(axes, key=lambda a_: abs(wrap(a_ - tocam)))]
                    pnp_n = wrap(pnp_yaw + FACE_OFF[q[0]])
                    nface = min(ok_ax, key=lambda a_: abs(wrap(a_ - pnp_n)))
                    byaw = wrap(nface - FACE_OFF[q[0]]); ctr = np.asarray(lc['c'], float)
                    fused = 'LIDAR OVERRULE' if abs(wrap(byaw - pnp_yaw)) > math.radians(30) else 'lidar axis'
                self.metrics.setdefault('yaw_fusion', []).append(dict(pnp=round(math.degrees(pnp_yaw)), fused=round(math.degrees(byaw)), how=fused,
                                                                        truth=round(math.degrees(self.w.bin['yaw'])), lidar_c=[round(float(v), 2) for v in lc['c']],
                                                                        lidar_ax=round(math.degrees(lc['yaw90'])), tag_xy=[round(float(v), 2) for v in pw[:2]], n_ax=len(ok_ax) if fused != 'pnp only' else 0,
                                                                        truth_c=[round(self.w.bin['x'], 2), round(self.w.bin['y'], 2)], n_lc=len(lcs)))
                self.ev('bin yaw: PnP %.0f deg -> %s %.0f deg' % (math.degrees(pnp_yaw), fused, math.degrees(byaw)))
            # Rev G6: pickup flip. Handles-out drops leave the handle facing the road; the tug must tow UP-lane with no U-turn
            # (28 deg kingpin stop), so the handle has to face the house within 60 deg before docking: orbit-nudge it round
            # (2 x 90 deg for a handles-out bin, same bumper nudge as s4a); the yard U-turn later does the second reversal.
            if self.sc.get('flip_pickup', True):
                hl = self.S.lane.heading(self.S.lane.project(np.asarray(ctr, float))[0]); dev = wrap(byaw - (hl + math.pi))
                if abs(dev) > math.radians(60):
                    k = int(round(-dev / (math.pi / 2))); k = k if k != 0 else (-1 if dev > 0 else 1)
                    s_b = float(self.S.lane.project(np.asarray(ctr, float))[0])
                    if (abs(dev) > math.radians(120) and s_b < self.S.lane.mouth[0] - 0.5 and self.sc.get('relay_flip', True)
                            and not getattr(self, '_relayed', False)):
                        # G6 s3 RELAY FLIP: a 180 deg orbit-nudge flip inside the 3.6 m hedged lane failed in every run (push poses
                        # beside the bin leave no pivot room: s10b pad M 0 deg turned in 6 pushes, s24d bump-strip trips). Hook the bin
                        # as it stands (handle to the road), tow it the few metres down into the bell-mouth (junction rule applies),
                        # release it there and do the 2 x 90 deg flip in the open mouth (as at spot A, s2).
                        rr = yield from self.relay_flip(np.asarray(ctr, float), byaw)
                        if rr == 'ok': continue
                        self.alert('cannot turn the bin handle-in: relay to the bell-mouth failed (%s) - handle faces %s' % (rr, self.dir_word(byaw)))
                        self.outcome_text = 'relay flip failed -> alert, home'; return 'alert'
                    rots = [k * math.pi / 2] if abs(k) == 1 else [math.pi, -math.pi]
                    self.ev('handle faces %s -> needs to face the house for an up-lane tow: flip %+d deg by orbit-nudge' % (self.dir_word(byaw), round(math.degrees(rots[0]))))
                    rot = self.nudge_plan(ctr, byaw, rots=rots) if self.nudges + abs(k) <= 3 else None
                    seq = None
                    if rot is None and self.nudges < 3:       # G6 s3: mixed-sign sequences also TRANSLATE the bin (~0.55 m per
                        seq = self.nudge_seq_plan(ctr, byaw, 3 - self.nudges)   # 90 deg): s4b sideways at the verge edge needed +90,-90,-90
                    if seq is not None:
                        self.metrics.setdefault('flips', []).append(dict(bin=self.target, dev_deg=round(math.degrees(dev)), seq=list(seq)))
                        c_, y_ = np.array(ctr, float), byaw; seq = list(seq)
                        while seq:
                            sg_ = seq.pop(0)
                            yield from self.do_nudge(c_, y_, sg_ * math.pi / 2)
                            if self._known is not None: c_, y_ = self._known
                            else:
                                y_ = wrap(y_ + sg_ * math.pi / 2); cands, _ = self.lidar_candidates()
                                cands = [q_ for q_ in cands if np.linalg.norm(q_['c'] - c_) < 1.3]
                                if cands: c_ = np.asarray(min(cands, key=lambda q_: np.linalg.norm(q_['c'] - c_))['c'], float)
                            # closed loop: the real bin rolls more/less than the 0.55 m model -> re-plan the rest from the measured pose
                            hl_ = self.S.lane.heading(self.S.lane.project(np.asarray(c_, float))[0])
                            if abs(wrap(y_ - (hl_ + math.pi))) <= math.radians(60) and self.room_ok(np.asarray(c_) + np.array([math.cos(y_), math.sin(y_)]) * DOCK_OFF, y_):
                                break
                            if self.nudges < 3:
                                nw_ = self.nudge_seq_plan(c_, y_, 3 - self.nudges)
                                if nw_ is not None: seq = list(nw_)
                        self._known = (np.array(c_, float), y_); self._view_skip = []
                        continue
                    if rot is None:
                        self.alert('cannot turn the bin handle-in (no room to nudge it round) - handle faces %s' % self.dir_word(byaw))
                        self.outcome_text = 'flip not possible -> alert, home'; return 'alert'
                    self.metrics.setdefault('flips', []).append(dict(bin=self.target, dev_deg=round(math.degrees(dev)), rot_deg=round(math.degrees(rot))))
                    c_, y_ = np.array(ctr, float), byaw
                    for st_ in range(int(round(abs(rot) / (math.pi / 2)))):
                        yield from self.do_nudge(c_, y_, math.copysign(math.pi / 2, rot))
                        if self._known is not None: c_, y_ = self._known
                        else:
                            y_ = wrap(y_ + math.copysign(math.pi / 2, rot)); cands, _ = self.lidar_candidates()
                            cands = [q_ for q_ in cands if np.linalg.norm(q_['c'] - c_) < 1.3]
                            if cands: c_ = np.asarray(min(cands, key=lambda q_: np.linalg.norm(q_['c'] - c_))['c'], float)
                    self._known = (np.array(c_, float), y_); self._view_skip = []
                    continue
            h = np.array([math.cos(byaw), math.sin(byaw)])
            D = ctr + h * DOCK_OFF
            # G6 s4 fix 11 TRIM NUDGE: an orbit-nudge flip can end 15-25 deg off (s24d: -201 deg for a planned -180), and the skewed
            # 2.6 m docking corridor then runs into the hedge end at the lane mouth. If the skewed corridor is blocked but the
            # lane-aligned one is free, push the bin round by the measured skew (partial nudge, max 2 per bin) before docking.
            if self.sc.get('trim_nudge', True) and getattr(self, '_trims', 0) < 2:
                hl_t = self.S.lane.heading(self.S.lane.project(np.asarray(ctr, float))[0]); dev_t = wrap(byaw - (hl_t + math.pi))
                oth_t = [np.array(p) for p in self.obst_pts if np.linalg.norm(np.array(p) - ctr) > 1.2]
                ya = wrap(hl_t + math.pi); ha = np.array([math.cos(ya), math.sin(ya)])
                if (math.radians(6) < abs(dev_t) <= math.radians(60) and not self.room_ok(D, byaw, obstacles=oth_t)
                        and self.room_ok(ctr + ha * DOCK_OFF, ya, obstacles=oth_t) and self.push_pose_ok(ctr, byaw)
                        and self.S.hedge_dist(ctr) >= 0.8):
                    self._trims = getattr(self, '_trims', 0) + 1
                    self.ev('handle %.0f deg off up-lane and the skewed docking corridor is blocked -> trim nudge %+.0f deg' % (math.degrees(dev_t), -math.degrees(dev_t)))
                    self.metrics.setdefault('trims', []).append(dict(bin=self.target, dev_deg=round(math.degrees(dev_t), 1)))
                    yield from self.do_nudge(ctr, byaw, -dev_t, target=abs(dev_t))
                    if self._known is None:
                        cands, _ = self.lidar_candidates(); cands = [q_ for q_ in cands if np.linalg.norm(q_['c'] - ctr) < 1.3]
                        y_ = wrap(byaw - dev_t)
                        if cands:
                            k_ = min(cands, key=lambda q_: np.linalg.norm(q_['c'] - ctr)); c_ = np.asarray(k_['c'], float)
                            y_ = min([wrap(k_['yaw90'] + j * math.pi / 2) for j in range(4)], key=lambda a_: abs(wrap(a_ - y_)))
                        else: c_ = np.array(ctr, float)
                        self._known = (c_, y_)
                    self._view_skip = []; continue
            self.metrics.setdefault('bin_estimates', []).append(dict(face=q[0], est=[round(float(ctr[0]), 2), round(float(ctr[1]), 2), round(math.degrees(byaw), 1)],
                                                                     truth=[round(self.w.bin['x'], 2), round(self.w.bin['y'], 2), round(math.degrees(self.w.bin['yaw']), 1)]))
            others = [np.array(p) for p in self.obst_pts if np.linalg.norm(np.array(p) - ctr) > 1.2]
            self.obst_pts = others + [ctr]
            if self.room_ok(D, byaw, obstacles=others):
                self.state = 'DOCK_APPROACH'
                if face_of(q[0]) != 0:
                    self.ev('room on the handle side -> drive round to it')
                    P = None
                    for k in (2.4, 2.0, 1.6):          # pre-dock pose inside the checked corridor, clear of hedges
                        Q = D + h * k
                        if self.S.in_fence(Q, margin=0.1) and self.S.hedge_dist(Q) > 0.75: P = Q; break
                    if P is None: P = D + h * 1.6
                    yield from self.goto_safe(*P, v=0.35, tol=0.3)
                    if np.linalg.norm(np.array(self.pose()[:2]) - P) > 0.6 and getattr(self, '_predock_fail', 0) < 2:
                        # Rev G2: never start a reverse-dock from the wrong place (it wasted the one re-dock in 4d-mouth)
                        self._predock_fail = getattr(self, '_predock_fail', 0) + 1
                        self.ev('pre-dock pose not reached -> back off, re-measure, re-plan'); self.state = 'REPLAN'
                        away = np.array(self.pose()[:2]) - ctr; away = away / max(np.linalg.norm(away), 1e-3)
                        yield from self.goto_safe(*(ctr + away * 3.0), v=0.3, tol=0.4)
                        c = dict(c, c=ctr, yaw90=byaw); continue
                    yield from self.pivot(byaw)
                ok = yield from self.reverse_dock(D, byaw)
                if ok == 'blocked':
                    if not (yield from self.crossbeam_recover(byaw, 'bin dock')):
                        self.outcome_text = 'centre-gap contact -> alert, home'; return 'alert'
                    ok = yield from self.reverse_dock(D, byaw)
                    if ok == 'blocked': self.outcome_text = 'centre-gap contact twice -> alert, home'; return 'alert'
                if ok and (yield from self.grab()):
                    self.outcome_text = self.outcome_text or 'docked & grabbed'
                    self.metrics['nudges'] = self.nudges; self.metrics['redocks'] = self.docks; return 'grabbed'
                self.docks += 1
                if self.docks >= 2:
                    self.alert('docking failed twice'); self.outcome_text = 'dock failed twice -> alert, home'; return 'alert'
                self.ev('re-dock once: pull forward and retry'); self.state = 'REDOCK'
                yield from self.goto(*(np.array(self.pose()[:2]) + h * 2.0), v=0.3)
                c = dict(c, c=ctr, yaw90=byaw); continue
            self.ev('no room on the handle side (handle faces %s)' % self.dir_word(byaw))
            rot = self.nudge_plan(ctr, byaw) if self.nudges < 2 else None
            if rot is not None:
                yield from self.do_nudge(ctr, byaw, rot); self._view_skip = []
                cands, big = self.lidar_candidates()
                if cands or big: self.obst_pts = [k['c'] for k in cands] + [b['c'] for b in big]    # re-observe after the push
                if cands:
                    cands.sort(key=lambda k: np.linalg.norm(k['c'] - ctr)); c = cands[0]
                else: c = dict(c, c=ctr)
                continue
            if self.docks == 0 and self.room_ok(D, byaw, length=1.4, obstacles=others):
                self.ev('no full approach and no nudge possible -> one short re-dock attempt'); self.docks += 1
                yield from self.goto_safe(*(D + h * 1.6), v=0.25, tol=0.25); yield from self.pivot(byaw)
                ok = yield from self.reverse_dock(D, byaw)
                if ok == 'blocked': self.outcome_text = 'centre-gap contact -> alert, home'; return 'alert'
                if ok and (yield from self.grab()): return 'grabbed'
            else:
                self.ev('re-dock not possible: less than 1.4 m clear in front of the handle')
            why = 'wedged against the hedge' if self.S.hedge_dist(ctr) < 0.8 else 'no room to reach the handle'
            self.alert('cannot recover bin: %s (handle faces %s)' % (why, self.dir_word(byaw)))
            self.outcome_text = 'unrecoverable -> alert, home'; return 'alert'
        self.alert('gave up after 5 recovery cycles'); self.outcome_text = 'gave up -> alert, home'; return 'alert'

    def dir_word(self, yaw):
        s, _ = self.S.lane.project(np.array(self.pose()[:2])); h = self.S.lane.heading(s)
        a = math.degrees(wrap(yaw - h))
        return 'the road' if abs(a) < 45 else ('the house' if abs(a) > 135 else ('the left verge' if a > 0 else 'the right verge'))

    def nudge_plan(self, ctr, byaw, rots=(math.pi / 2, -math.pi / 2, math.pi)):
        """Room, hedge-clearance and geofence check for a bumper orbit-nudge (90 deg per push, ~0.55 m roll per 90 deg)."""
        S = self.S
        if S.hedge_dist(ctr) < 0.8:
            self.ev('nudge rejected: hedge %.2f m from the bin (< 0.8 m, it would wedge)' % S.hedge_dist(ctr)); return None
        push_ok = self.push_pose_ok(ctr, byaw)
        if not push_ok:
            self.ev('nudge rejected: no reachable push position beside the bin'); return None
        for robust in (True, False):     # G6 s3: prefer a rotation whose end pose still has docking room if the bin rolls 0.35 m off the model
          for rot in rots:
            steps = int(round(abs(rot) / (math.pi / 2))); c = np.array(ctr, float); y = byaw; ok = True
            for k in range(steps):
                y = wrap(y + math.copysign(math.pi / 2, rot))
                c = c + 0.55 * np.array([math.cos(y - math.copysign(math.pi / 4, rot)), math.sin(y - math.copysign(math.pi / 4, rot))])
                if not S.in_fence(c, margin=0.0) or S.hedge_dist(c) < 0.8: ok = False; break     # G3: bin centre >= 1.2 m inside the private boundary (fence is 3.7 m stricter than G2)
            if not ok: continue
            hv = np.array([math.cos(y), math.sin(y)]); nv = np.array([-hv[1], hv[0]])
            cs = [c] + ([c + 0.35 * nv, c - 0.35 * nv, c + 0.35 * hv, c - 0.35 * hv] if robust else [])
            if all(self.room_ok(cc + hv * DOCK_OFF, y) for cc in cs):
                self.ev('orbit-nudge plan: rotate %+d deg (bin ends %.2f m from hedge%s)' % (round(math.degrees(rot)), S.hedge_dist(c), ', robust' if robust else ''))
                return rot
        self.ev('nudge rejected: no rotation leaves room to dock inside the geofence'); return None

    def _relay_cands(self, ctr):
        """G6 s4 fix 10/12: relay release poses in the mouth that pass the geometry + flip model, in preference order.
        Keeps 1.8 m from the pad spots of the OTHER bins still out tonight (incl. spot A) and every seen object (s3 used
        _others_for('A'), which leaves spot A out: in s10b the relay pose was chosen beside the black bin at A); push poses keep
        1.3 m from them (_push_clear). Offline check (work_g6/relay_chk.py): with a bin at A only L-10.6 / lat 0.0..-0.4 and
        L-10.1 / lat 0.0..+0.4 qualify (the right half of the mouth fails the geofence / push-pose rules)."""
        S = self.S; ctr = np.asarray(ctr, float)
        own = (self.pad_for or {}).get(self.target, 'A')
        others = [self.layout.bin_pose(S, k) for k in sorted(set((self.pad_for or {}).values())) if k != own]
        others += [tuple(np.asarray(o_, float)[:2]) for o_ in self.obst_pts if np.linalg.norm(np.asarray(o_, float)[:2] - ctr) > 1.2]
        self._avoid_pts = [np.array(o_[:2], float) for o_ in others]
        out = []
        for so in (11.1, 10.6, 11.6, 10.1):
            for la_ in (1.2, 0.8, 0.4, 0.0, -0.4, -0.8, -1.2, -1.6):        # spot-A-like first (the open-mouth flip that works in s2)
                bx, by, byaw_A = S.pose(S.L - so, la_, 0.0); u = np.array([math.cos(byaw_A), math.sin(byaw_A)])
                if S.lane.project(np.array([bx, by]))[0] < S.lane.project(ctr)[0] + 1.5: continue
                ax_ = np.array([bx, by]) + u * 0.985; fr = ax_ + u * (TUG['front'] + 0.2)
                if not (S.in_fence(ax_, margin=0.2) and S.fp_ok(tuple(fr), 0.3) and S.hedge_dist(fr) > 0.45): continue
                if any(math.hypot(bx - o[0], by - o[1]) < 1.8 for o in others): continue
                if not self.flip_model_ok(np.array([bx, by]), byaw_A): continue
                out.append((bx, by, byaw_A))
        return out

    def relay_flip(self, ctr, byaw):
        """G6 s3: dock to the handle as the bin stands (handle facing the road), grab, junction check, tow it down into the
        bell-mouth (spot A, or a clear legal alternate from the adaptive-slot logic), release, pull forward and hand the bin back to
        handle_candidate (known pose) for the open-mouth 2 x 90 deg flip. Returns 'ok' or a reason string."""
        S = self.S; self._relayed = True; self.state = 'RELAY_DOCK'
        h = np.array([math.cos(byaw), math.sin(byaw)]); D = ctr + h * DOCK_OFF
        others = [np.asarray(p, float) for p in self.obst_pts if np.linalg.norm(np.asarray(p) - ctr) > 1.2]
        if not self.room_ok(D, byaw, obstacles=others): return 'no room on the road side of the bin to dock'
        P = None
        for k in (2.4, 2.0, 1.6):
            Q = D + h * k
            if S.in_fence(Q, margin=0.1) and S.hedge_dist(Q) > 0.75: P = Q; break
        if P is None: return 'no pre-dock pose'
        cands = self._relay_cands(ctr)          # G6 s4: model-check the relay poses BEFORE hooking (s4 dev: none -> it towed the bin home reversed)
        if not cands: return 'no relay pose in the mouth with room to flip'
        self.ev('relay flip: hook the bin as it stands (handle to the road), tow it into the bell-mouth, flip it there')
        self.obst_pts = others + [np.array(ctr, float)]
        yield from self.goto_safe(*P, v=0.3, tol=0.3); yield from self.pivot(byaw)
        ok = yield from self.reverse_dock(D, byaw)
        if ok is not True or not (yield from self.grab()): return 'dock/grab failed'
        self.metrics.setdefault('relay_flip', []).append(dict(bin=self.target, t=round(self.w.t, 1), from_s_from_end=round(S.L - float(S.lane.project(ctr)[0]), 2)))
        jw = yield from self.junction_wait()
        if jw == 'stopped':
            yield from self.release('release_relay_abort', pull=True); return 'mouth busy (junction wait)'
        # relay release pose: a mouth pose DOWN-lane of the tug (no reversing with the bin), legal for the tug at release, clear in the
        # lidar, away from other known bins, and one from which the planned 2 x 90 deg flip ends with room to dock (model check)
        s_t = float(self.s_lat()[0]); tgt = None; tried = 0
        for (bx, by, byaw_A) in cands:
            if S.L - float(S.lane.project(np.array([bx, by]))[0]) > S.L - s_t - 0.5: continue    # must be DOWN-lane of the tug
            tried += 1
            if not self.slot_view((bx, by, byaw_A))['clear']: continue
            tgt = (bx, by, byaw_A); break
        self.metrics['relay_flip'][-1].update(slot=None if tgt is None else [round(S.L - float(S.lane.project(np.array(tgt[:2]))[0]), 2), round(float(S.lane.project(np.array(tgt[:2]))[1]), 2)], tried=tried)
        if tgt is None:
            yield from self.release('release_relay_abort', pull=True); return 'no clear relay pose in the mouth'
        bx, by, byaw_A = tgt; u = np.array([math.cos(byaw_A), math.sin(byaw_A)]); axle = np.array([bx, by]) + 0.985 * u
        self.state = 'RELAY_TOW'; self.leg = 'relay_tow'
        yield from self.goto(*axle, v=0.25, tol=0.25)
        r = yield from self.release('release_relay', pull=True)
        if not r: return 'release refused'
        x, y, yaw = self.pose()
        c_est = np.array([bx, by], float)
        cands, _ = self.lidar_candidates()
        cands = [q_ for q_ in cands if np.linalg.norm(np.asarray(q_['c']) - c_est) < 1.3]
        if cands: c_est = np.asarray(min(cands, key=lambda q_: np.linalg.norm(np.asarray(q_['c']) - c_est))['c'], float)
        self._known = (c_est, byaw_A); self._view_skip = []
        self.obst_pts = [o_ for o_ in self.obst_pts if np.linalg.norm(np.asarray(o_, float) - c_est) > 1.2] + [c_est]
        self.ev('relay flip: bin released in the mouth at L-%.1f m -> flip it here' % (S.L - float(S.lane.project(c_est)[0])))
        return 'ok'

    def flip_model_ok(self, ctr, byaw):
        """Model check (no events): a 180 deg orbit-nudge flip (either sense) from this pose keeps the bin in the fence, off the hedges,
        has a push pose at each step and ends with room to dock with the handle facing up-lane."""
        S = self.S
        for rot in (math.pi, -math.pi):
            c = np.array(ctr, float); y = byaw; ok = True
            for k in range(2):
                if not self.push_pose_ok(c, y): ok = False; break
                y = wrap(y + math.copysign(math.pi / 2, rot))
                c = c + 0.55 * np.array([math.cos(y - math.copysign(math.pi / 4, rot)), math.sin(y - math.copysign(math.pi / 4, rot))])
                if not S.in_fence(c, margin=0.0) or S.hedge_dist(c) < 0.8: ok = False; break
            if ok and self.room_ok(c + np.array([math.cos(y), math.sin(y)]) * DOCK_OFF, y): return True
        return False

    def push_pose_ok(self, ctr, byaw):
        """A bumper push pose exists beside the bin (same rule as do_nudge): stand-off 1.0 m (>= 0.8 m off the hedge, 0.8 m inside the
        fence) or 0.7 / 0.4 / 0.25 m (the tug must still pivot there: >= 1.05 m swept radius off the hedge, 0.2 m inside the fence)."""
        S = self.S
        for side in (-1, 1):
            fn = byaw + side * math.pi / 2; nv = np.array([math.cos(fn), math.sin(fn)])
            for so in (1.0, 0.7, 0.4, 0.25):
                Q = np.array(ctr, float) + nv * (BIN['w'] / 2 + TUG['front'] + so)
                if S.in_fence(Q, margin=0.8 if so == 1.0 else 0.2) and S.hedge_dist(Q) > (0.8 if so == 1.0 else 1.05) and self._push_clear(Q, ctr): return True
        return False

    def _push_clear(self, Q, ctr):
        """G6 s4 fix 12: a push pose must keep 1.3 m from every OTHER known object (seen obstacles + the pad spots of the other bins
        still out): s10b's relay flip drove to a push pose beside the black bin at spot A and pushed it instead (0 deg turned)."""
        ctr = np.asarray(ctr, float)[:2]
        for o in list(self.obst_pts or []) + list(getattr(self, '_avoid_pts', []) or []):
            o = np.asarray(o, float)[:2]
            if np.linalg.norm(o - ctr) > 1.2 and np.linalg.norm(o - np.asarray(Q, float)[:2]) < 1.3: return False
        return True

    def nudge_seq_plan(self, ctr, byaw, nmax):
        """G6 s3: shortest sequence of +-90 deg orbit-nudges (incl. mixed signs, which walk the bin sideways) that ends with the handle
        within 60 deg of up-lane, every intermediate bin centre inside the geofence and >= 0.8 m off the hedge, and room to dock."""
        import itertools
        S = self.S
        if S.hedge_dist(ctr) < 0.8: return None
        for n in range(1, nmax + 1):
            for seq in itertools.product((1, -1), repeat=n):
                c = np.array(ctr, float); y = byaw; ok = True
                for sg in seq:
                    if not self.push_pose_ok(c, y): ok = False; break
                    y = wrap(y + sg * math.pi / 2); c = c + 0.55 * np.array([math.cos(y - sg * math.pi / 4), math.sin(y - sg * math.pi / 4)])
                    if not S.in_fence(c, margin=0.0) or S.hedge_dist(c) < 0.8: ok = False; break
                if not ok: continue
                hl = S.lane.heading(S.lane.project(c)[0])
                if abs(wrap(y - (hl + math.pi))) > math.radians(60): continue
                if self.room_ok(c + np.array([math.cos(y), math.sin(y)]) * DOCK_OFF, y):
                    self.ev('orbit-nudge sequence %s (bin walks to %.2f m from the hedge)' % (['%+d' % (90 * q) for q in seq], S.hedge_dist(c)))
                    return seq
        return None

    def do_nudge(self, ctr, byaw, rot, target=None):
        """One 90 deg orbit-nudge. Pushes repeatedly (max 3) until the measured turn reaches the target: bumper-contact
        odometry gives the running turn, the lidar outline after each push re-measures it. A push stops when contact is lost
        (the bin rolled away) or the tug would leave the geofence."""
        sgn = 1 if rot > 0 else -1
        self.state = 'NUDGE_%d' % (self.nudges + 1); self.nudges += 1
        tol = math.radians(8) if target is None else min(math.radians(8), 0.3 * target)    # G6 s4: partial (trim) nudge
        target = math.pi / 2 if target is None else target; turned = 0.0; c = np.array(ctr, float); y = byaw; truth0 = self.w.nudge_rot; pushes = 0
        self._known = None; snapped = False
        while turned < target - tol and pushes < 3 and not self.w.wedged:
            pushes += 1
            hv = np.array([math.cos(y), math.sin(y)]); P = None
            for side in (-sgn, sgn):          # either side face works (push near the front end of one, back end of the other)
                fn = wrap(y + side * math.pi / 2); nv = np.array([math.cos(fn), math.sin(fn)])
                for so in (1.0, 0.7, 0.4, 0.25):    # G6: closer stand-off allowed when the lane is narrow (pad bins in the lane); s3: + 0.25 m
                    Q = c + nv * (BIN['w'] / 2 + TUG['front'] + so) + hv * 0.2 * side * sgn
                    if self.S.in_fence(Q, margin=0.8 if so == 1.0 else 0.2) and self.S.hedge_dist(Q) > (0.8 if so == 1.0 else 1.05) and self._push_clear(Q, c): P = Q; break
                if P is not None: break
            if P is None: self.ev('no push position well inside the geofence'); break
            # G6 s3: the bin being nudged must be a known obstacle for the path to the push pose (it was missing during the pickup
            # flip, so goto_safe drove straight through it: repeated front bump-strip trips in s4b / s24d)
            self.obst_pts = [o_ for o_ in (self.obst_pts or []) if np.linalg.norm(np.asarray(o_, float) - c) > 1.2] + [np.array(c, float)]
            yield from self.goto_safe(*P, v=0.3, tol=0.25)
            yield from self.pivot(wrap(fn + math.pi))
            seg = yield from self._push(sgn, target - turned)
            for back in (1.4, 0.9, 0.5):           # back off only as far as the geofence allows
                if self.S.in_fence(self.ahead(-back - TUG['front']), margin=0.0): break
            yield from self.goto(*self.ahead(-back), v=0.25, reverse=True, tol=0.2)
            est = turned + seg; y_pred = wrap(byaw + sgn * est)
            cands, _ = self.lidar_candidates()
            cands = [k for k in cands if np.linalg.norm(k['c'] - c) < 1.3]
            if cands:                          # re-measure from the lidar outline (axis known mod 90 -> the one nearest the odometry guess)
                k = min(cands, key=lambda k: np.linalg.norm(k['c'] - c)); c = np.asarray(k['c'], float)
                axes = [wrap(k['yaw90'] + q * math.pi / 2) for q in range(4)]
                ax = min(axes, key=lambda a: abs(wrap(a - y_pred)))
                snapped = abs(wrap(ax - y_pred)) < math.radians(35)
                if snapped: y_pred = ax; est = abs(wrap(ax - byaw))
            turned = est; y = y_pred
            self.ev('nudge %d push %d: measured turn %.0f deg' % (self.nudges, pushes, math.degrees(turned)))
        self.w.nudge = 0; self.stop()
        if snapped and not self.w.wedged: self._known = (np.array(c, float), y)    # Rev G2: identity already read, pose re-measured
        deg = math.degrees(self.w.nudge_rot - truth0)
        self.ev('nudge %d: bin turned %.0f deg in %d push(es)%s' % (self.nudges, deg, pushes, ' (WEDGED)' if self.w.wedged else ''))
        self.metrics.setdefault('nudge_log', []).append(dict(deg=round(deg), measured=round(math.degrees(turned)), pushes=pushes, wedged=self.w.wedged))

    def _push(self, sgn, remaining):
        """Drive the bumper into the bin until the contact odometry says `remaining` rad turned. Returns the estimate (rad)."""
        self.w.nudge = sgn; t0 = self.w.t; stuck = 0; ds = 0.0; had = False; lost = 0
        while ds / 0.55 < remaining - 0.03 and self.w.t - t0 < 30:
            yield
            x, y, yaw = self.pose(); Pp, _ = self.scan_points(); st = 0.0      # keep the bumper on the bin's lidar outline
            if len(Pp):
                rel = Pp - np.array([x, y]); f = rel @ np.array([math.cos(yaw), math.sin(yaw)]); l = rel @ np.array([-math.sin(yaw), math.cos(yaw)])
                m = (f > 0) & (f < TUG['front'] + 1.2) & (np.abs(l) < 0.9)
                if m.any(): st = float(np.clip(-0.8 * math.atan2(l[m].mean() - 0.12 * sgn, f[m].mean()), -0.25, 0.25))
            if not self.S.in_fence(self.ahead(TUG['front'] + 0.2), margin=0.0) or not self.S.in_fence(self.pose()[:2], margin=0.3):
                self.ev('nudge push stopped at the geofence'); break
            self.drive(st, self.thr_ctl(0.15))
            if self.w.bumper: ds += abs(self.w.v) * 0.1; had = True; lost = 0
            elif had:
                lost += 1
                if lost > 10: self.ev('nudge push: contact lost (bin rolled away)'); break
            stuck = stuck + 1 if (self.w.v == 0 and self.w.bumper) else 0
            if stuck > 30 or self.w.wedged: break
        self.w.nudge = 0; self.stop(); yield
        return ds / 0.55


    # ================= Rev G4 additions =================
    def placement(self, what, tgt):
        """Evaluation: where the released bin actually stands (truth) vs its programmed / taught pose."""
        b = self.w.bin
        if b is None: return
        e = math.hypot(b['x'] - tgt[0], b['y'] - tgt[1]); ey = math.degrees(wrap(b['yaw'] - tgt[2]))
        self.metrics.setdefault('placement', []).append(dict(spot=what, bin=self.target, err_m=round(e, 2), yaw_err_deg=round(ey, 1)))
        self.ev('placement %s: %.2f m / %+.0f deg from the programmed pose' % (what, e, ey))
        if e > 0.6:     # G4 fix: this is a GROUND-TRUTH evaluation, so it must not drive a robot alert (the tug has no hitch-angle /
                        # post-release bin measurement today). Scored as 'placement out of tolerance' by score_g4 / report_g4 instead.
            self.metrics.setdefault('placement_oot', []).append(dict(spot=what, bin=self.target, err_m=round(e, 2)))
            self.ev('EVAL (truth, not a robot alert): %s bin %.2f m off its programmed spot %s - out of the 0.6 m tolerance' % (self.target, e, what))

    def overnight_charge(self, secs):
        """Rev G4 dock recharge during the RTC sleep (booked analytically like the sleep itself). Charging needs the pack >= +3 C:
        with the dock-powered 15 W pad heater the pack is warmed first; without it a cold pack is not charged. CC 5 A (144 W
        into the pack) + 15 % CV tail. Heater / charger energy comes from the mains."""
        w = self.w; pc0 = w.pack_c if w.pack_c is not None else w.air_c; soc0 = w.soc; air = w.air_c
        usable = PACK_WH_NOM * pack_cold_factor(air); t_warm = 0.0; ok = True
        if w.charge_fault: ok = False
        if pc0 < 3.0:
            if w.pack_heater: t_warm = (3.5 - pc0) * 3300.0 * PACK_WH_NOM / 307.2 / max(15.0 - 0.6 * (pc0 - air), 1.0)
            else: ok = False
        rec = dict(heater=bool(w.pack_heater), pack_c_start=round(pc0, 1), soc_start=round(soc0, 3), warm_h=round(t_warm / 3600.0, 2))
        if ok and t_warm < secs:
            need = (1.0 - soc0) * usable; t_chg = need / 144.0 * 3600.0 * 1.15
            t_c = min(secs - t_warm, t_chg); w.soc = float(min(1.0, soc0 + t_c / 1.15 * 144.0 / 3600.0 / usable))
            w.pack_c = 5.0 if w.pack_heater else max(pc0, air)
            rec.update(charged=True, charge_h=round(t_c / 3600.0, 2), wh_into_pack=round((w.soc - soc0) * usable, 1), soc_end=round(w.soc, 3),
                       mains_wh=round((w.soc - soc0) * usable / 0.9 + (15.0 * secs * 0.25 / 3600.0 if w.pack_heater else 0.0), 1))
        else:
            w.pack_c = air + (pc0 - air) * math.exp(-secs / 5500.0)
            rec.update(charged=False, why='charge fault' if w.charge_fault else 'pack below +3 C and no pack heater', soc_end=round(w.soc, 3))
        rec['pack_c_wake'] = round(w.pack_c, 1)
        self.metrics.setdefault('overnight_charge', []).append(rec)
        self.ev('overnight on the dock: %s' % (('pack heater %.1f h, charged %.1f h -> SOC %.0f %%' % (rec['warm_h'], rec['charge_h'], 100 * w.soc)) if rec.get('charged')
                                               else 'NOT charged (%s), SOC %.0f %%' % (rec['why'], 100 * w.soc)))

    # ---------- audio (two-way, WebRTC over 4G; see audio_api.py) ----------
    def announce(self, clip):
        if self.audio['state'] == 'call': return          # the owner is talking - no canned clip on top
        txt = CLIPS[clip]; dur = 1.0 + 0.07 * len(txt)
        self.audio.update(state='announce', until=self.w.t + dur)
        self.audio['log'].append(dict(t=round(self.w.t, 1), kind='announce', clip=clip, text=txt, dur_s=round(dur, 1)))
        self.r.ev('audio', 'speaker: "%s"' % txt)

    def audio_tick(self):
        a = self.audio; t = self.w.t
        oc = self._owner_call
        if oc and not oc.get('_done') and a['state'] != 'call':
            hit = [al for al in self.alerts if oc['after_alert'] in al['text']]
            if hit and t >= hit[0]['t'] + oc.get('delay_s', 15.0) and not oc.get('_ring'):
                oc['_ring'] = t; a.update(state='ringing', until=t + 4.0)
                import audio_api
                sess = audio_api.MockTug().handle_offer(dict(type='offer', sdp=audio_api.FAKE_OFFER))
                a['call'] = sess['session_id']
                a['log'].append(dict(t=round(t, 1), kind='call_offer', session=sess['session_id'], codec=sess['codec'], path='owner app -> 4G -> TURN relay -> tug'))
                self.r.ev('audio', 'owner app calls the tug (WebRTC offer, session %s) after alert' % sess['session_id'])
        if a['state'] == 'ringing' and t >= a['until']:
            a.update(state='call', until=t + (oc or {}).get('talk_s', 45.0)); a['log'].append(dict(t=round(t, 1), kind='call_connected', session=a['call']))
            self.r.ev('audio', 'two-way audio connected: owner speaks through the tug speaker, tug mic -> owner')
            if oc and oc.get('says'): self.r.ev('audio', 'owner: "%s"' % oc['says'])
        elif a['state'] == 'call' and t >= a['until']:
            a.update(state='idle'); a['log'].append(dict(t=round(t, 1), kind='call_ended', session=a['call']))
            if oc: oc['_done'] = True
            self.r.ev('audio', 'owner hung up')
        elif a['state'] == 'announce' and t >= a['until']: a.update(state='idle')

    def audio_w(self): return AUDIO_W.get(self.audio['state'], 0.0)

    # ---------- vehicle-approach stop (front + rear 24 GHz radar, lidar) ----------
    def radar_view(self):
        x, y, yaw = self.pose(); v = self.vel if self.mode == 'AUTO' or self.speed_cmd > 0 else self.vel
        ego = np.array([math.cos(yaw), math.sin(yaw)]) * (v if self.w.v >= -0.02 else -v)
        out = []
        for q in self.r.radar_tgts:
            look = yaw if q['side'] == 'front' else wrap(yaw + math.pi)
            u = np.array([math.cos(look + math.radians(q['az'])), math.sin(look + math.radians(q['az']))])
            ground = q['vr'] + float(ego @ u)              # target ground speed along the line of sight (+ = moving away)
            out.append(dict(q, ground=round(ground, 2), closing=round(-q['vr'], 2), veh=q['snr'] >= VSTOP['snr_vehicle']))
        return out

    def vehicle_threat(self):
        """Closest qualifying radar target; a vehicle track that was closing and leaves the narrow (+-20 deg) beam at short range
        (a car drawing alongside) is coasted for 2.5 s on its last range rate."""
        best = None; now = self.w.t; tr = getattr(self, '_vtrack', {})
        view = self.radar_view()
        for side in ('front', 'rear'):
            qs = [q for q in view if q['side'] == side and q['veh'] and q['ground'] < -0.3 and q['closing'] >= VSTOP['closing']]
            if qs: q = min(qs, key=lambda q: q['r']); tr[side] = dict(q, t=now)
            elif side in tr and now - tr[side]['t'] < 2.5 and tr[side]['r'] < 9.0:
                q = tr[side]; rp = q['r'] - q['closing'] * (now - q['t'])
                if rp < VSTOP['r_stop']:
                    best = best or dict(q, r=round(max(rp, 0.0), 2), ttc=0.0, crit='coasted track (radar lost it at %.1f m: beam edge or speed gate; predicted %.1f m)' % (q['r'], max(rp, 0.0)))
            else: tr.pop(side, None)
        self._vtrack = tr
        for q in view:
            if not q['veh'] or q['ground'] > -0.3 or q['closing'] < VSTOP['closing']: continue
            ttc = q['r'] / max(q['closing'], 1e-3)
            crit = 'range %.1f m < %.1f m' % (q['r'], VSTOP['r_stop']) if q['r'] < VSTOP['r_stop'] else (
                   'TTC %.1f s < %.1f s' % (ttc, VSTOP['ttc_s']) if (q['r'] < VSTOP['r_ttc'] and ttc < VSTOP['ttc_s']) else None)
            if crit and (best is None or q['r'] < best['r'] or best['crit'].startswith('coasted')): best = dict(q, ttc=round(ttc, 1), crit=crit)
        return best

    def big_lidar_near(self, r=4.0):
        cands, big = self.lidar_candidates(); x, y, _ = self.pose()
        return [b for b in big if np.linalg.norm(np.asarray(b['c']) - np.array([x, y])) < r]

    def truth_vehicle_gap(self):
        g = [v.min_gap for v in self.w.vehicles if v.on]
        from g4_features import poly_gap_fast
        from world import box_segs
        w = self.w; c, s_ = math.cos(w.yaw), math.sin(w.yaw)
        _, tp = box_segs(w.x + c * (TUG['front'] - TUG['rear']) / 2, w.y + s_ * (TUG['front'] - TUG['rear']) / 2, w.yaw, TUG['front'] + TUG['rear'], 2 * TUG['half_w'])
        d = []
        for v in w.vehicles:
            if not v.on: continue
            _, cp = box_segs(v.x, v.y, v.yaw, v.L, v.W); d.append(poly_gap_fast(np.array(cp), np.array(tp)))
        return round(min(d), 2) if d else None

    def vehicle_watch(self, leg):
        """Rev G4 vehicle-approach stop. A radar target that is vehicle-like (SNR >= 18 dB), moving over the ground toward the
        tug (ego-motion compensated: parked cars do not count) and closing, within 5.5 m or with time-to-contact < 3 s (<= 12 m)
        -> HOLD (spring brakes), beacon, speaker clip. Resume when nothing vehicle-like is closing within 8 m and the lidar
        sees no vehicle-sized object within 4 m, for 3 s. A vehicle that stays stopped close by for 10 s (driver waiting behind)
        -> resume at a 0.3 m/s creep. Held > 5 min -> alert, stay stopped. Lane (AUTO) legs only."""
        if getattr(self, '_creep', False):
            near = [q for q in self.radar_view() if q['veh'] and q['r'] < VSTOP['r_clear']]
            if not near:
                self._creep_clear = getattr(self, '_creep_clear', None) or self.w.t
                if self.w.t - self._creep_clear > VSTOP['clear_s']:
                    self._creep = False; self._creep_clear = None; self.change_speed(self.base_speed); self.ev('vehicle gone -> normal speed')
            else: self._creep_clear = None
        th = self.vehicle_threat()
        self._vt_n = (getattr(self, '_vt_n', 0) + 1) if th else 0
        if self._vt_n < 2: return None                      # must persist for 2 radar frames (0.2 s)
        self._vt_n = 0
        self.set_mode('HOLD'); self.vstop_state = 'HOLD'; self.state = 'VEHICLE_HOLD'; t0 = self.w.t; x0 = self.w.odo; v0 = self.w.v
        rec = dict(t=round(t0, 1), leg=leg, side=th['side'], crit=th['crit'], radar_r=th['r'], closing=th['closing'], ground=th['ground'],
                   snr=th['snr'], v_at_trigger=round(v0, 2), truth_gap_at_trigger=self.truth_vehicle_gap())
        self.ev('VEHICLE %s: %s (closing %.1f m/s, ground %.1f m/s) -> HOLD, beacon, speaker' % (th['side'], th['crit'], th['closing'], th['ground']))
        self.announce('vehicle')
        clear_since = None; still_since = None; min_gap = 99.0; stop_t = None; outcome = None
        while True:
            yield
            g = self.truth_vehicle_gap()
            if g is not None: min_gap = min(min_gap, g)
            if stop_t is None and abs(self.w.v) < 0.02: stop_t = round(self.w.t - t0, 2); rec['stop_dist_m'] = round(self.w.odo - x0, 2)
            view = [q for q in self.radar_view() if q['veh']]
            closing = [q for q in view if q['r'] < VSTOP['r_clear'] and q['closing'] > VSTOP['closing'] and q['ground'] < -0.3]
            big = self.big_lidar_near()
            still = [q for q in view if q['r'] < VSTOP['r_clear'] and abs(q['ground']) < 0.3 and q['closing'] < VSTOP['closing']]
            if not closing and not big: clear_since = clear_since or self.w.t
            else: clear_since = None
            if still and not closing and not [b for b in big if (np.asarray(b['c']) - np.array(self.pose()[:2])) @ np.array([math.cos(self.yaw), math.sin(self.yaw)]) > 0]:
                still_since = still_since or self.w.t
            else: still_since = None
            if int((self.w.t - t0) * 10) % 40 == 0: self.announce('vehicle') if self.audio['state'] == 'idle' and self.w.t - t0 > 8 else None
            if clear_since is not None and self.w.t - clear_since >= VSTOP['clear_s']: outcome = 'clear'; break
            if still_since is not None and self.w.t - still_since >= VSTOP['creep_after_s']: outcome = 'creep'; break
            if self.w.t - t0 > VSTOP['max_hold_s']:
                rec.update(hold_s=round(self.w.t - t0, 1), resume='timeout', min_truth_gap_m=round(min_gap, 2), stop_s=stop_t); self.vstops.append(rec)
                self.vstop_state = None
                self.alert('vehicle stop: held 5 min with a vehicle next to the tug - staying stopped'); self.outcome_text = 'vehicle hold timeout -> stopped + alert'
                return 'stopped'
        rec.update(hold_s=round(self.w.t - t0, 1), resume=outcome, min_truth_gap_m=round(min_gap, 2), stop_s=stop_t); self.vstops.append(rec)
        self.ev('vehicle stop: %s after %.1f s -> resume%s' % (outcome, self.w.t - t0, ' at 0.3 m/s (vehicle waiting close by)' if outcome == 'creep' else ''))
        if outcome == 'clear' and [q for q in self.radar_view() if q['veh'] and q['r'] < VSTOP['r_clear']]: outcome = 'clear (vehicle still near: creep)'
        if outcome.startswith(('creep', 'clear (')): self._creep = True; self.change_speed(VSTOP['creep_v'])
        self.vstop_state = None; self.state = 'AUTO_' + leg.upper(); self.set_mode('AUTO'); self._vtrack = {}
        return 'held'

    # ---------- bin calendar ----------
    def calendar_plan(self, evening):
        cal = BinCalendar(self.sc.get('calendar')); c = cal.collection_for_evening(__import__('datetime').date.fromisoformat(evening))
        self.metrics['calendar'] = dict(evening=evening, collection=c, file=os.path.basename(cal.path))
        if c is None or c.get('skipped') or not c['bins']:
            self.ev('calendar: no collection tomorrow (%s) -> nothing to put out tonight' % evening); self.outcome_text = 'calendar: no bins tonight'; return []
        order = sorted(c['bins'], key=lambda b: -SC.HOME_SPOTS[b]['lat'])          # Rev G6: innermost home spot first -> pad A first (handles-out)
        self.pad_for = self.layout.pads_for(order)
        self.ev('calendar: collection %s %s = week %s -> bins %s (drop order %s -> pads %s); drop at %s, pickup by %s %s'
                % (c['weekday'], c['date'], c['week'], '+'.join(c['bins']), '+'.join(order), self.pad_for, c['drop_at'], c['pickup_at'][:3], c['pickup_deadline']))
        self.metrics['calendar'].update(order=order, pads=self.pad_for)
        plan = []
        if self.clock() is not None and self.clock() < parse_clock(c['drop_at']) - 0.5: plan.append(('sleep_until', c['drop_at']))
        plan += SC.drop_plan(self.S, order, self.pad_for)        # starts with 'boot'
        return plan


    # ---------- teach-and-repeat ----------
    def operator_drive(self, lat_fn, s_end, v=0.5, rec=None, step=1.0, tmax=4000):
        """SIMULATED operator on the app joystick (RC override in MANUAL): follows his own line lat_fn(s) along the lane
        using what he sees (truth pose), lookahead 1.6 m. The companion only records its own EKF pose every `step` m."""
        S = self.S; s0 = S.lane.project(np.array([self.w.x, self.w.y]))[0]; sgn = 1 if s_end > s0 else -1; t0 = self.w.t
        last = None
        while True:
            yield
            s, l = S.lane.project(np.array([self.w.x, self.w.y]))
            if sgn * (s_end - s) < 0.3 or self.w.t - t0 > tmax: break
            sa = s + sgn * 1.6; tgt = S.lane.point(sa, lat_fn(sa))
            e = wrap(math.atan2(tgt[1] - self.w.y, tgt[0] - self.w.x) - self.w.yaw)
            vv = v if sgn * (s_end - s) > 2.0 else max(0.15, v * sgn * (s_end - s) / 2.0)
            self.drive(float(np.clip(-0.9 * e, -0.35, 0.35)), self.thr_ctl(vv * max(0.3, math.cos(e))))
            if rec is not None:
                x, y, yaw = self.pose()
                if last is None or math.hypot(x - last[0], y - last[1]) >= step:
                    last = (x, y); rec.append([round(x, 3), round(y, 3), round(yaw, 4), round(self.vel, 2)])
        self.stop(); yield from self.wait(0.8)

    def teach_run(self, bin_name):
        """Rev G4 teach run (app 'Teach' mode, RC). The operator hooks the bin at its home spot, presses MARK HOME, drives the
        lane on his own line, stops at the wait point (MARK WAIT), turns in the bell-mouth, places the bin where he wants it
        (MARK DROP = release), drives back and presses PARK. The companion records the route + exact poses into a route file
        that the repeat mission drives. Joystick input here is a scripted stand-in for a person (truth pose + wobble)."""
        S = self.S; L = S.L; W = S.lane.width; self.mission = 'teach'; self.target = bin_name; self.state = 'TEACH_HOME'; self.leg = 'teach'
        t_start = self.w.t
        while not self.w.seat and self.w.t - t_start < 30:            # operator reverses the last 0.4 m onto the handle
            self.drive(0.0, self.rev_thr(-0.10)); yield
        self.stop(); yield from self.wait(1.0)
        x, y, yaw = self.pose(); hx, hy = x - DOCK_OFF * math.cos(yaw), y - DOCK_OFF * math.sin(yaw); hs, hl = S.lane.project(np.array([hx, hy]))
        home = dict(x=round(hx, 3), y=round(hy, 3), yaw=round(yaw, 4), s=round(float(hs), 3), lat=round(float(hl), 3))
        b = self.w.bin; home_truth = dict(x=round(b['x'], 3), y=round(b['y'], 3), yaw=round(b['yaw'], 4))
        self.ev('TEACH: MARK HOME pressed - bin home pose %.2f, %.2f, %.0f deg (EKF + hook geometry)' % (hx, hy, math.degrees(yaw)))
        if not (yield from self.grab()): raise _Abort('teach: grab failed')
        wob = lambda s_: 0.12 * math.sin(2 * math.pi * s_ / 23.0)
        def down_line(s_):
            if s_ < 22: return float(np.interp(s_, [10, 22], [home['lat'], 0.9]))
            if s_ < L - 26: return 0.9 + wob(s_)
            return float(np.interp(s_, [L - 26, L - 16, L], [0.9, 1.35, 1.35]))       # Rev G6 handles-out: on to spot A's line
        rd = []; self.state = 'TEACH_DRIVE'; self.leg = 'teach_down'
        yield from self.operator_drive(down_line, L - SC.JUNCTION_WAIT, rec=rd)
        self.ev('TEACH: MARK WAIT pressed at L-%.1f m' % (L - self.s_lat()[0])); wait_s = float(self.s_lat()[0]); yield from self.wait(3.0)
        # Rev G6 handles-out: no U-turn with the bin; the operator drives on to spot A and releases there (handle to the road)
        yield from self.operator_drive(down_line, L - 11.1 + 0.985, v=0.3, rec=rd)
        ux, uy, uyaw = self.pose(); us, ul = S.lane.project(np.array([ux, uy]))
        self.state = 'TEACH_PLACE'
        if not (yield from self.release('teach_drop', pull=False)): raise _Abort('teach: release refused')
        b = self.w.bin; x, y, yaw = self.pose()
        dx, dy = x - 0.985 * math.cos(yaw), y - 0.985 * math.sin(yaw); ds, dl = S.lane.project(np.array([dx, dy]))
        drop = dict(x=round(dx, 3), y=round(dy, 3), yaw=round(yaw, 4), s=round(float(ds), 3), lat=round(float(dl), 3))
        drop_truth = dict(x=round(b['x'], 3), y=round(b['y'], 3), yaw=round(b['yaw'], 4))
        self.ev('TEACH: MARK DROP pressed - bin drop pose %.2f, %.2f (L-%.2f m, lat %.2f), handle %.0f deg' % (dx, dy, L - ds, dl, math.degrees(yaw)))
        ok_t = yield from self.solo_turnaround()                 # Rev G6: operator turns the empty tug round (solo pivot)
        if not ok_t or not self.w.chain_ok:      # G6 s3: never wait forever with the chain open (s21a ran to the 4500 s limit)
            raise _Abort('teach: turnaround after the drop failed (%s)' % ('no pivot point' if not ok_t else 'bump strip contact'))
        up_line = lambda s_: (-0.9 + wob(s_)) if s_ > 22 else float(np.interp(s_, [12, 22], [0.0, -0.9]))
        ru = []; self.state = 'TEACH_DRIVE'; self.leg = 'teach_up'
        yield from self.operator_drive(up_line, 12.0, rec=ru)
        self.ev('TEACH: PARK pressed -> automatic docking')
        route = dict(version=1, bin=bin_name, created_clock=clock_str(self.clock()) if self.clock0 is not None else None, source='teach run (RC) %s' % self.r.name,
                     home_pose=home, drop_pose=drop, wait_point=dict(s=round(wait_s, 2)), release_axle=dict(x=round(ux, 3), y=round(uy, 3), yaw=round(uyaw, 4), s=round(float(us), 2), lat=round(float(ul), 2)),
                     handles='out', route_down=rd, route_up=ru,
                     _truth_eval_only=dict(home=home_truth, drop=drop_truth))
        route['validation'] = RouteFile.validate(S, route)
        path = self.sc['route_out']; RouteFile.save(path, route)
        self.metrics['teach'] = dict(file=os.path.relpath(path, G4.ROOT), n_down=len(rd), n_up=len(ru), validation=route['validation'],
                                     home_err_m=round(math.hypot(home['x'] - home_truth['x'], home['y'] - home_truth['y']), 3),
                                     drop_err_m=round(math.hypot(drop['x'] - drop_truth['x'], drop['y'] - drop_truth['y']), 3),
                                     drop_yaw_err_deg=round(math.degrees(wrap(drop['yaw'] - drop_truth['yaw'])), 1))
        self.ev('TEACH: route file written (%d + %d points), validator: %s' % (len(rd), len(ru), 'OK' if route['validation']['ok'] else route['validation']))
        self.mission = 'drop'

    def route_leg(self, which, part):
        """Rev G4 repeat: drive a taught route in AUTO (waypoints resampled every 4 m / 12 deg from the taught EKF track)."""
        S = self.S; R = self.route; pts_all = R['route_down'] if which == 'down' else R['route_up']
        s_here = self.s_lat()[0]
        SL = [S.lane.project(np.array(p[:2]))[0] for p in pts_all]
        if part == 'to_wait': sel = [p for p, sq in zip(pts_all, SL) if s_here + 1.0 < sq <= R['wait_point']['s'] + 0.01]; stop_s = None
        elif part == 'to_drop':          # Rev G6 handles-out: stop 1.5 m short of the taught release axle, release_at_pose drives on
            sel = [p for p, sq in zip(pts_all, SL) if sq > s_here + 1.0 and sq < R['release_axle']['s'] - 1.0]; stop_s = R['release_axle']['s'] - 1.5
        elif part == 'to_uturn':
            sel = [p for p, sq in zip(pts_all, SL) if sq > s_here + 1.0]; stop_s = R['uturn_start']['s'] - 0.2
            if sel:                                         # extend 1.5 m beyond the taught U-turn start (firmware WP radius)
                a = sel[-1]; sel = sel + [[a[0] + 1.5 * math.cos(a[2]), a[1] + 1.5 * math.sin(a[2]), a[2], 0.3]]
        else: sel = [p for p, sq in zip(pts_all, SL) if sq < s_here - 1.0]; stop_s = None
        if not sel: return 'ok'
        wp = RouteFile.resample(sel, 4.0)
        s1 = S.lane.project(np.array(wp[-1]))[0]
        self.route_mode = True
        r = yield from self.auto_leg(s_here, s1, 0.0, 'route_%s_%s' % (which, part), pts=wp, stop_s=stop_s)
        self.route_mode = False
        return r

    def release_at_pose(self, pose, name):
        """Rev G4: place the bin at a taught / programmed pose: drive forward so the released bin centre (0.985 m behind the
        axle) lands on it, then release (pinch-zone rule applies)."""
        u = np.array([math.cos(pose['yaw']), math.sin(pose['yaw'])]); axle = np.array([pose['x'], pose['y']]) + 0.985 * u
        x, y, yaw = self.pose(); ahead_m = (axle - np.array([x, y])) @ np.array([math.cos(yaw), math.sin(yaw)])
        self.state = 'TO_PAD'
        if 0.3 < ahead_m < 5.0: yield from self.goto(*axle, v=0.25, tol=0.2)
        r = yield from self.release(name)
        if r: self.placement('taught drop', (pose['x'], pose['y'], pose['yaw']))
        return r


    # ---------- Rev G4 g) adaptive drop spot ----------
    def notify(self, text):
        """App notification (info, not an alarm): pushed over 4G to the owner's app."""
        self.app_notes.append(dict(t=round(self.w.t, 1), text=text)); self.metrics['app_notifications'] = self.app_notes
        self.r.ev('app', 'notify: ' + text)

    def ko_lat(self, s, l):
        """Shift a lane waypoint sideways (nearest first) until the tug body there stays >= 0.25 m clear of every keep-out."""
        def clear(lq):
            for ds in (-2.5, -1.25, 0.0, 1.25, 2.5):             # shift early enough that the tug + towed bin are already over
                for dl in (-TUG['half_w'], 0.0, TUG['half_w']):
                    if self.S.keepout_depth(self.S.lane.point(s + ds, lq + dl)) > -0.25: return False
            return True
        if clear(l): return l
        for k in range(1, 63):
            for lq in (l - 0.05 * k, l + 0.05 * k):
                if abs(lq) <= 1.55 and clear(lq):
                    self.metrics.setdefault('keepout_shifts', []).append(dict(s=round(float(s), 1), from_lat=round(l, 2), to_lat=round(lq, 2))); return lq
        self.metrics.setdefault('keepout_shifts', []).append(dict(s=round(float(s), 1), from_lat=round(l, 2), to_lat=None)); return l

    def slot_view(self, pose, infl=None):
        """Lidar ray check of a bin slot (footprint + inflate): sample points inside it; a point is FREE if the beam toward it
        returns beyond it, OCCLUDED if something returns in front of it (car, debris, bin, person), UNSEEN if out of range
        (11.5 m) or in the occluded rear arc. Clear = < 2 occluded samples and < 30 % unseen."""
        infl = self.areas.d.get('inflate_m', 0.3) if infl is None else infl
        r = self.r.scan; x, y, yaw = self.pose()
        if r is None: return dict(clear=False, occl=0, unseen=1, n=1)
        ox = x + TUG['lidar_x'] * math.cos(yaw); oy = y + TUG['lidar_x'] * math.sin(yaw)
        poly = self.areas.bin_poly(*pose, infl); g = 0.15; pts = []
        for xx in np.arange(poly[:, 0].min(), poly[:, 0].max() + g, g):
            for yy in np.arange(poly[:, 1].min(), poly[:, 1].max() + g, g):
                if _pip(poly, xx, yy): pts.append((xx, yy))
        occl = unseen = free = 0; mp = self._scan_mapped()
        for qx, qy in pts:
            d = math.hypot(qx - ox, qy - oy); b = int(round(math.degrees(wrap(math.atan2(qy - oy, qx - ox) - yaw)))) % 360
            rr = [r[(b + k) % 360] for k in (-1, 0, 1)]
            if d > 11.5 or any(np.isnan(v) for v in rr): unseen += 1
            elif min(rr) < d - 0.12:
                # G4 fix: a return in front of the slot that lies on the surveyed hedge map hides the slot (UNSEEN), it does not block it
                if all(mp[(b + k) % 360] for k in (-1, 0, 1) if r[(b + k) % 360] < d - 0.12): unseen += 1
                else: occl += 1
            else: free += 1
        n = max(len(pts), 1)
        return dict(clear=occl < 2 and unseen < 0.3 * n, occl=occl, unseen=unseen, n=n)

    def zone_view(self, s_rng, l_rng, g=0.3):
        r = self.r.scan; x, y, yaw = self.pose()
        ox = x + TUG['lidar_x'] * math.cos(yaw); oy = y + TUG['lidar_x'] * math.sin(yaw); occl = unseen = n = 0; mp = self._scan_mapped()
        for sq in np.arange(s_rng[0], s_rng[1] + 1e-6, g):
            for lq in np.arange(l_rng[0], l_rng[1] + 1e-6, g):
                qx, qy = self.S.lane.point(sq, lq); n += 1
                d = math.hypot(qx - ox, qy - oy); b = int(round(math.degrees(wrap(math.atan2(qy - oy, qx - ox) - yaw)))) % 360
                rr = [r[(b + k) % 360] for k in (-1, 0, 1)] if r is not None else [np.nan]
                if d > 11.5 or any(np.isnan(v) for v in rr): unseen += 1
                elif min(rr) < d - 0.12:
                    if all(mp[(b + k) % 360] for k in (-1, 0, 1) if r[(b + k) % 360] < d - 0.12): unseen += 1   # G4 fix: hedge-map return = unseen
                    else: occl += 1
        return dict(occl=occl, unseen=unseen, n=max(n, 1))

    def _scan_mapped(self):
        """G4 fix: per-bearing flag 'this lidar return lies on the surveyed hedge map' (cached per scan)."""
        r = self.r.scan
        if r is None: return np.zeros(360, bool)
        if getattr(self, '_mapped_for', None) is r: return self._mapped
        x, y, yaw = self.pose(); ox = x + TUG['lidar_x'] * math.cos(yaw); oy = y + TUG['lidar_x'] * math.sin(yaw)
        ang = yaw + np.radians(np.arange(360)); ok = np.isfinite(r); m = np.zeros(360, bool)
        H = self.S.hedges_near((x, y), 16.0)
        if ok.any() and len(H):
            P = np.c_[ox + r[ok] * np.cos(ang[ok]), oy + r[ok] * np.sin(ang[ok])]
            d = np.min(seg_dist(P[:, None, :], H[None, :, :2], H[None, :, 2:]), axis=1)
            m[np.where(ok)[0]] = d < (0.3 if self.fix >= 6 else 0.6)
        self._mapped_for = r; self._mapped = m; return m

    def slot_check(self, pose, scans=6):
        res = None
        for k in range(scans):
            yield
            v = self.slot_view(pose)
            if res is None or v['occl'] > res['occl'] or v['unseen'] > res['unseen']: res = v
        return res

    def pts_in_box(self, s_rng, l_rng):
        P, _ = self.scan_points()
        for p in P:
            sq, lq = self.S.lane.project(p)
            if s_rng[0] <= sq <= s_rng[1] and l_rng[0] <= lq <= l_rng[1]: return True
        return False

    def _choose(self, slot, primary, alts_fn, extra_ok=None):
        rec = dict(t=round(self.w.t, 1), slot=slot, bin=self.target, primary=[round(v, 2) for v in primary])
        v = yield from self.slot_check(primary); rec['primary_check'] = v
        if v['clear'] or (v['occl'] < 2 and v['unseen'] >= 0.3 * v['n']):     # not seen (range / rear arc): keep the primary, as before G4
            if not v['clear']: self.ev('slot %s not visible from here (%d/%d unseen) -> keep the programmed slot' % (slot, v['unseen'], v['n']))
            self.metrics.setdefault('adaptive_slot', []).append(dict(rec, chosen='primary', n_alts=0)); return primary
        alts = alts_fn(); rec['n_alts'] = len(alts); tried = []
        self.ev('slot %s for the %s bin NOT clear (%d occluded / %d unseen of %d samples) -> %d legal alternates' % (slot, self.target, v['occl'], v['unseen'], v['n'], len(alts)))
        for a in alts:
            va = self.slot_view(a); ok = va['clear'] and (extra_ok is None or extra_ok(a))
            sa, la = self.S.lane.project(np.array(a[:2])); tried.append(dict(s=round(float(sa), 2), lat=round(float(la), 2), clear=va['clear'], ok=bool(ok)))
            if ok:
                rec.update(chosen=dict(s=round(float(sa), 2), s_from_end=round(self.S.L - float(sa), 2), lat=round(float(la), 2), yaw_deg=round(math.degrees(a[2]), 1),
                                       moved_m=round(math.hypot(a[0] - primary[0], a[1] - primary[1]), 2)), tried=tried)
                self.metrics.setdefault('adaptive_slot', []).append(rec)
                self.notify('%s bin: slot %s blocked - using alternate %.1f m away (%s)' % (self.target, slot, rec['chosen']['moved_m'],
                            'L-%.1f m, lat %+.2f' % (self.S.L - sa, la) if sa > 300 else 's=%.1f m, lat %+.2f' % (sa, la)))
                return a
        rec.update(chosen=None, tried=tried); self.metrics.setdefault('adaptive_slot', []).append(rec)
        return None

    def _others_for(self, exclude):
        """Programmed slots (other bins' home spots and pad spots) + bins placed tonight: an alternate keeps the spacing to all."""
        out = []
        for b, hs in SC.HOME_SPOTS.items():
            if not (exclude == 'home' and b == self.target): out.append(self.S.pose(hs['s'], hs['lat'], 0.0))
        for k in self.layout.d['spots']:
            if k != exclude: out.append(self.layout.bin_pose(self.S, k))
        return out

    def choose_pad_slot(self, pad, primary):
        sp = self.layout.spot(self.S, pad)
        room = lambda x, y, yaw: self.room_ok(np.array([x, y]) + np.array([math.cos(yaw), math.sin(yaw)]) * DOCK_OFF, yaw)
        def corridor_ok(a):          # the pickup approach corridor (3.5 m up-lane of the slot) must be empty of observed objects too
            sa, la = self.S.lane.project(np.array(a[:2])); v = self.zone_view((sa - 3.6, sa - 0.45), (la - 0.45, la + 0.45), g=0.2)
            return v['occl'] <= 1 and v['unseen'] <= 0.3 * v['n']
        return (yield from self._choose(pad, primary, lambda: self.areas.alternates(pad, primary, sp['hedge_clear_m'], self._others_for(pad), sp['spacing_m'], room), corridor_ok))

    def choose_home_slot(self, final=True):
        hc = self._home_check; hp = hc['primary']; x, y, yaw = self.S.pose(hp['s'], hp['lat'], 0.0)
        if not final:                # G4 fix: not visible yet (hedge / range / rear arc) -> defer instead of deciding on a hidden slot
            v = yield from self.slot_check((x, y, yaw), scans=3)
            if not v['clear'] and v['occl'] < 2: return 'defer'
        room = lambda xx, yy, yw: self.room_ok(np.array([xx, yy]) + np.array([math.cos(yw), math.sin(yw)]) * DOCK_OFF, yw)
        def uturn_zone_ok(a):        # Rev G6: the SWEPT AREA of the planned yard U-turn for this slot (tug body + towed bin) must be SEEN free
            sa, la = self.S.lane.project(np.array(a[:2])); v = self.points_view(self.yard_uturn_sweep(sa, la))    # x-y swept area (G4 used a lane box)
            ok = v['occl'] <= 1 and v['unseen'] <= 0.3 * v['n']
            self.metrics.setdefault('uturn_zone_checks', []).append(dict(s=round(float(sa), 2), lat=round(float(la), 2), occl=v['occl'], unseen=v['unseen'], n=v['n'], ok=bool(ok)))
            return ok
        a = yield from self._choose('home:' + self.target, (x, y, yaw), lambda: self.areas.alternates('home', (x, y, yaw), 0.3, self._others_for('home'), 1.0, room), uturn_zone_ok)
        if a is None:
            self.set_mode('HOLD'); self.stop()
            self.alert('home slot of the %s bin blocked and no clear alternate in the yard - holding with the bin, please clear it' % self.target)
            self.outcome_text = 'home slot + alternates blocked -> holding bin + alert'; return None
        if a == (x, y, yaw): return hp
        sa, la = self.S.lane.project(np.array(a[:2])); self.home_target = dict(s=float(sa), lat=float(la)); return self.home_target

    def log_drop(self, name):
        """Where the bin was actually left (companion estimate: 0.985 m behind the axle along the tug heading), for the pickup."""
        x, y, yaw = self.pose(); bx, by = x - 0.985 * math.cos(yaw), y - 0.985 * math.sin(yaw); sb, lb = self.S.lane.project(np.array([bx, by]))
        e = dict(x=round(bx, 3), y=round(by, 3), yaw=round(yaw, 4), s=round(float(sb), 3), lat=round(float(lb), 3), how=name, t=round(self.w.t, 1),
                 slot=(self.metrics.get('adaptive_slot') or [{}])[-1].get('slot') if name != 'place_house' else 'home')
        self.drop_log[self.target] = e; self.metrics['drop_log'] = self.drop_log
        try:
            os.makedirs(os.path.join(G4.ROOT, 'out', os.environ.get('BT_OUTDIR', 'G6'), 'droplog'), exist_ok=True)
            json.dump(self.drop_log, open(os.path.join(G4.ROOT, 'out', os.environ.get('BT_OUTDIR', 'G6'), 'droplog', self.r.name + '.json'), 'w'), indent=1)
        except Exception: pass

    # ---------------- alerts / home ----------------
    def alert(self, text):
        x, y, _ = self.pose(); lat, lon = xy2ll(x, y)
        img, _ = self.w.render_cam()
        n = len(self.alerts) + 1; fn = os.path.join(self.r.out, 'alert_%d.png' % n)
        big = cv2.resize(img, (640, 480), interpolation=cv2.INTER_NEAREST)
        cv2.putText(big, '4G ALERT: ' + text[:62], (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)
        cv2.imwrite(fn, big)
        self.alerts.append(dict(t=round(self.w.t, 1), text=text, lat=round(lat, 6), lon=round(lon, 6), photo=os.path.basename(fn)))
        self.alert_flag = text; self.r.ev('ALERT', '4G alert + photo: ' + text)
        if self.result == 'running': self.result = 'alert'

    def go_home(self):
        self.ev('heading home empty')
        L = self.S.L
        s, _ = self.s_lat()
        if s > L - 14: yield from self.goto_safe(*self.S.lane.point(min(s, L - 13), 0.0), v=0.3)
        s, _ = self.s_lat()
        yield from self.pivot(wrap(self.S.lane.heading(s) + math.pi))
        plan = self.sc['plan']
        tgt = 7.0 if 'park' in plan else [p for p in plan if not isinstance(p, str) and p[0] == 'auto'][-1][2]
        r = yield from self.auto_leg(None, tgt, 0.0, 'home_empty')
        if r == 'stopped': self.finish(self.result if self.result != 'running' else 'stopped', self.outcome_text); return
        if 'park' in plan: yield from self.park()
        self.finish(self.result if self.result != 'running' else 'alert', self.outcome_text or 'alert, returned')
