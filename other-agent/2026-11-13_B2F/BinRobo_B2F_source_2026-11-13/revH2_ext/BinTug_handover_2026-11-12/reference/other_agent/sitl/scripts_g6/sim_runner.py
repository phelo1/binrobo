#!/usr/bin/env python3
"""ArduPilot JSON-SITL physics backend for the bin-tug (lock-step, UDP 9002).
 - Launches the real ArduPilot Rover 4.6.2 SITL binary with --model JSON and params/bintug.parm
 - Steps scene.ExtWorld on every servo packet and replies with IMU/attitude/position/velocity JSON
 - Feeds the firmware: GPS via MAVLink GPS_INPUT (fix 6 RTK / 5 float / 1 none, by zone, GPS1_TYPE 14)
                       LD06 lidar via MAVLink OBSTACLE_DISTANCE (72 x 5 deg sectors, 10 Hz, hedge-map filtered)
 - Runs the companion state machine (companion.py) on its own MAVLink link (SERIAL0, tcp 5760)
 - Logs a 10 Hz telemetry trace + events to out/<scenario>/trace.json and result.json
Usage: sim_runner.py <scenario_name> [--instance N] [--tmax S]
"""
import json, math, os, socket, struct, subprocess, sys, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
OUT_G4 = os.path.join(ROOT, 'out', os.environ.get('BT_OUTDIR', 'G6'))   # G6: all outputs under out/G6 (G3/G4 results untouched)
sys.path.insert(0, HERE)
os.environ['MAVLINK20'] = '1'
from pymavlink import mavutil
from pymavlink.rotmat import Matrix3, Vector3
from world import TUG, BIN, xy2ll, LAT0, LON0, wrap
from scene import ExtWorld, power_w, seg_dist
import scenarios, companion
from g4_features import Radar24, left_gap, kl_lat
import g6_features as G6

GPS_EPOCH_OFFSET = 315964800; LEAP = 18
def _jd(o): return o.item() if hasattr(o, 'item') else (o.tolist() if hasattr(o, 'tolist') else str(o))
BINARY = os.environ.get('ARDUROVER', os.path.join(ROOT, 'bin', 'ardurover_aarch64'))


class Runner:
    def __init__(self, name, instance=0, tmax=None):
        self.sc = scenarios.get(name); self.name = name; self.inst = instance
        self.out = os.path.join(OUT_G4, name + os.environ.get('BT_OUT_SUFFIX', '')); os.makedirs(self.out, exist_ok=True)
        self.w = self.sc['world']; self.site = self.sc['site']
        self.tmax = tmax or self.sc.get('tmax', 4000)
        self.z0 = self.site.ter.z(0.0, 0.0)
        self.trace = []; self.events = []; self.energy_wh = 0.0; self.leg_energy = {}
        self.gps_hz = 5; self.lidar_hz = 10; self.last_gps = -1; self.last_lidar = -1; self.last_log = -1
        self.scan = None; self.gps_fix = 6; self.prev_vel = np.zeros(3); self.acc_f = np.zeros(3)
        self.gps_err = np.zeros(2); self.gps_sent_pos = (0, 0); self.pwm = [1500] * 16
        self.gps_hold = []; self.sleep_wh = 0.0; self.sleep_s = 0.0; self.batt_sent = 0.0     # Rev G3
        self.radar = Radar24(self.w.rng) if self.sc.get('radar', True) else None; self.radar_tgts = []; self.last_radar = -1   # Rev G4
        # Rev G6: RTK multipath under canopy, wheel odometry (scale error ASSUMED ~N(0, 1 %)), corridor fit, lane fusion
        sd = int(os.environ.get('BT_SEED', '7'))
        self.mp = G6.RtkMultipath(sd) if self.site.variant == 'real' and self.sc.get('multipath', True) else None
        self.odo_k = 1.0 + float(np.random.default_rng(sd + 77).normal(0, 0.01)); self.cfit = G6.CorridorFit(sd)
        self.fus = G6.LaneFusion(self.site); self.corridor_on = self.sc.get('corridor', os.environ.get('BT_CORRIDOR', '1') != '0')
        self.raw_fix = 6; self.raw_xy = (0.0, 0.0); self.gps_q = 'rtk'; self.walls = {}

    def _clear_instance(self):
        """Rev G3: kill a stale ardurover left on THIS instance (by PID, read from /proc) and wait for the UDP port."""
        me = '-I%d' % self.inst
        for pid in os.listdir('/proc'):
            if not pid.isdigit(): continue
            try: cmd = open('/proc/%s/cmdline' % pid, 'rb').read().split(b'\0')
            except Exception: continue
            if cmd and cmd[0].endswith(b'ardurover_aarch64') or (cmd and cmd[0].endswith(b'ardurover')):
                if me.encode() in cmd:
                    try: os.kill(int(pid), 9); print('killed stale ardurover pid', pid, flush=True)
                    except Exception: pass

    def launch(self):
        self._clear_instance()
        rd = os.path.join(self.out, 'sitlrun'); os.makedirs(rd, exist_ok=True)
        hdg = (90 - math.degrees(self.w.yaw)) % 360
        port = 9002 + 10 * self.inst
        parm = os.path.join(ROOT, 'params', 'bintug_g6.parm')     # G6 param file (G3/G4 files untouched)
        extra = list(self.sc.get('params') or []) + [q.strip().replace('=', ' ') for q in os.environ.get('BT_PARAMS', '').split(';') if q.strip()]   # G6: env overrides (tuning)
        if extra:
            parm = os.path.join(rd, 'bintug_scenario.parm')
            open(parm, 'w').write(open(os.path.join(ROOT, 'params', 'bintug_g6.parm')).read() + '\n# scenario overrides\n' + '\n'.join(extra) + '\n')
        args = [BINARY, '-w', '--model', 'JSON:127.0.0.1', '--speedup', '200', '--rate', '50',
                '--defaults', parm, '--home', '%.7f,%.7f,%.2f,%.1f' % (LAT0, LON0, self.z0, hdg),
                '-I%d' % self.inst, '--sim-port-out', str(port), '--sim-port-in', str(port + 1)]
        self.sitl_log = open(os.path.join(rd, 'sitl_stdout.txt'), 'w')
        self.proc = subprocess.Popen(args, cwd=rd, stdout=self.sitl_log, stderr=subprocess.STDOUT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for k in range(40):          # Rev G3: the previous run's socket may still be closing
            try: self.sock.bind(('127.0.0.1', port)); break
            except OSError: time.sleep(1.0)
        self.sock.settimeout(10)
        base = 5760 + 10 * self.inst
        for k in range(60):
            try:
                self.gcs = mavutil.mavlink_connection('tcp:127.0.0.1:%d' % base, source_system=255, source_component=191, autoreconnect=False); break
            except Exception: time.sleep(0.5)
        self.sens = None; self.sens_port = base + 2

    def stop(self):
        try: self.proc.terminate(); self.proc.wait(5)
        except Exception:
            try: self.proc.kill()
            except Exception: pass

    def fdm_json(self, dt):
        w = self.w; roll, pitch = w.attitude(); yaw_ned = wrap(math.pi / 2 - w.yaw)
        z = w.zxy(w.x, w.y) - self.z0
        vx, vy = w.v * math.cos(w.yaw), w.v * math.sin(w.yaw)
        gx, gy = w.ter.grad(w.x, w.y); vz = gx * vx + gy * vy
        vel = np.array([vy, vx, -vz])
        acc = (vel - self.prev_vel) / dt; self.prev_vel = vel
        self.acc_f = 0.7 * self.acc_f + 0.3 * acc
        R = Matrix3(); R.from_euler(roll, pitch, yaw_ned)
        f = R.transposed() * Vector3(self.acc_f[0], self.acc_f[1], self.acc_f[2] - 9.80665)
        d = dict(timestamp=w.t, imu=dict(gyro=[0.0, 0.0, -w.w], accel_body=[f.x, f.y, f.z]), position=[w.y, w.x, -z],
                 attitude=[roll, pitch, yaw_ned], velocity=vel.tolist())
        return (json.dumps(d, separators=(',', ':')) + '\n').encode()     # SITL's JSON parser needs no spaces after ':'

    def raw_gnss(self):
        """Rev G6: what the RTK receiver outputs (truth + receiver noise + canopy multipath model; scenario zones override)."""
        w = self.w; q = w.gps_quality(); t = w.t
        bias = np.zeros(2)
        if q == 'rtk' and self.mp is not None:
            sl = self.site.lane.project(np.array([w.x, w.y]))[0]
            q, bias = self.mp.step(t, sl, 1.0 / self.gps_hz)
        for a, b, k in self.gps_hold:          # Rev G3: RTK receiver re-converging after an RTC wake
            if a <= t < b: q = 'float' if (k == 'float' and q in ('rtk', 'wrongfix')) else ('none' if k == 'none' else q)
        fix = {'rtk': 6, 'wrongfix': 6, 'float': 5, 'none': 1}[q]
        sig = {6: 0.012, 5: 0.25, 1: 3.0}[fix]
        self.gps_err = 0.9 * self.gps_err + w.rng.normal(0, sig * 0.45, 2)
        if fix == 6 and q == 'rtk': bias = np.zeros(2)
        return fix, (w.x + self.gps_err[0] + bias[0], w.y + self.gps_err[1] + bias[1]), q

    def send_gps(self):
        if self.sens is None: return
        w = self.w; t = w.t
        fix, (x, y), q = self.raw_gnss(); self.raw_fix = fix; self.raw_xy = (x, y); self.gps_q = q
        c = self.comp; fused = None
        if self.corridor_on:
            self.fus.rtk(fix, (x, y), t)
            if c.yaw is not None: fused = self.fus.output(1.0 / self.gps_hz)
        if fused is not None:
            fq = self.fus.quality()
            if fix == 1 and fq == 'lost': fused = None
            else:
                x, y = float(fused[0]), float(fused[1])
                fix = 6 if fq == 'good' else (5 if fq == 'degraded' else 1)
        if fix == 1: x, y = self.raw_xy
        self.gps_fix = fix
        sig = {6: 0.012, 5: 0.25, 1: 3.0}[fix]
        lat, lon = xy2ll(x, y); alt = w.zxy(w.x, w.y)
        tow_s = 1_700_000_000 + t - GPS_EPOCH_OFFSET + LEAP
        week = int(tow_s // 604800); ms = int((tow_s % 604800) * 1000)
        vx, vy = w.v * math.cos(w.yaw), w.v * math.sin(w.yaw)
        if fix == 1:
            self.sens.mav.gps_input_send(int(t * 1e6), 0, 0, ms, week, 1, 0, 0, 0, 99.0, 99.0, 0, 0, 0, 9, 99, 99, 3, 0)
        else:
            self.sens.mav.gps_input_send(int(t * 1e6), 0, 0, ms, week, fix, int(lat * 1e7), int(lon * 1e7), alt,
                                         0.6 if fix == 6 else 1.2, 0.9, vy, vx, 0.0, 0.05 if fix == 6 else 0.3, sig * 1.5, sig * 2.5,
                                         22 if fix == 6 else 13, 0)
        self.gps_sent_pos = (x, y)

    def send_lidar(self):
        r = self.w.lidar()
        self.scan = r
        if self.corridor_on and self.site.variant == 'real':          # Rev G6: hedge-face fit (tug frame) -> lateral update
            self.walls = self.cfit.fit(r); c = self.comp
            klt = c.kl_target() if hasattr(c, 'kl_target') else None
            faces = None
            if klt is not None and self.sc.get('face_clamp', os.environ.get('BT_FACE_CLAMP', '1') != '0') and self.fus.p is not None:
                # faces in the frame of the RATE-LIMITED estimate (fus.out): an RTK re-fix step in fus.p must not step the clamp target
                # (it did: the offset jumped 0.4 m in 1.5 s while the forwarded position eased -> AUTO swerve, s10b s=505)
                fz = G6.lane_faces(self.site.lane, self.fus.out if self.fus.out is not None else self.fus.p, c.yaw_now(), r, getattr(c, '_leg_sgn', 1))
                if fz is not None: faces = fz[0]; self.faces_log = faces
            self.fus.corridor(self.walls, c.yaw, klt, ahead=getattr(self.cfit, 'last_ahead', None), faces=faces)
        # Pi-side map filter: returns on the surveyed hedge lines are dropped before the scan is sent to the firmware,
        # so the proximity library only sees unmapped objects (people, branches, bins, cars). Uses the EKF pose.
        c = self.comp
        if c.ekf_xy is not None and c.yaw is not None:
            x, y = c.ekf_xy; yaw = c.yaw
            ox = x + TUG['lidar_x'] * math.cos(yaw); oy = y + TUG['lidar_x'] * math.sin(yaw)
            ang = yaw + np.radians(np.arange(360)); ok = np.isfinite(r)
            if ok.any():
                P = np.c_[ox + r[ok] * np.cos(ang[ok]), oy + r[ok] * np.sin(ang[ok])]
                H = self.site.hedges_near((x, y), 16.0)
                if len(H):
                    d = np.min(seg_dist(P[:, None, :], H[None, :, :2], H[None, :, 2:]), axis=1)
                    rr = r.copy(); idx = np.where(ok)[0]; rr[idx[d < 0.3]] = np.inf; r = rr
        cw = np.array([r[(-k) % 360] for k in range(360)])          # CCW bearings -> clockwise (body FRD)
        dist = np.full(72, 65535, np.int64)
        for i in range(72):
            seg = cw[5 * i - 2: 5 * i + 3] if i > 0 else np.r_[cw[-2:], cw[:3]]
            seg = seg[~np.isnan(seg)]
            if len(seg) == 0: continue
            m = np.min(seg)
            dist[i] = 1201 if not np.isfinite(m) else int(max(5, m * 100))
        self.sector = dist
        if self.sens is not None:
            self.sens.mav.obstacle_distance_send(int(self.w.t * 1e6), mavutil.mavlink.MAV_DISTANCE_SENSOR_LASER, dist.tolist(), 5, 5, 1200, 0, 0,
                                                 mavutil.mavlink.MAV_FRAME_BODY_FRD)

    def run(self):
        self.launch()
        self.comp = companion.Companion(self, self.sc)
        frame_last = -1; reply = None; t_wall = time.time(); n = 0
        try:
            while True:
                try: data, addr = self.sock.recvfrom(256)
                except socket.timeout:
                    self.ev('sim', 'SITL stopped sending servo packets'); break
                if len(data) < 40: continue
                magic, rate, fc = struct.unpack('<HHI', data[:8])
                if magic != 18458: continue
                pwm = list(struct.unpack('<16H', data[8:40]))
                if fc == frame_last and reply is not None:
                    self.sock.sendto(reply, addr); continue
                if fc < frame_last: self.ev('sim', 'SITL frame counter reset')
                frame_last = fc; dt = 1.0 / max(rate, 1)
                pwm = [p if p > 900 else 1500 for p in pwm]
                self.w.step(dt, pwm); self.pwm = pwm
                if self.corridor_on and self.comp.yaw is not None:     # Rev G6: wheel odometry (encoders) into the Pi's lane fusion
                    self.fus.predict(self.w.v * self.odo_k + float(self.w.rng.normal(0, 0.01)), self.comp.yaw_now(), dt)
                reply = self.fdm_json(dt); self.sock.sendto(reply, addr); n += 1
                t = self.w.t
                if self.sens is None and t > 1.0:
                    try: self.sens = mavutil.mavlink_connection('tcp:127.0.0.1:%d' % self.sens_port, source_system=255, source_component=192)
                    except Exception: self.sens = None
                if t - self.last_gps >= 1.0 / self.gps_hz: self.last_gps = t; self.send_gps()
                # the LD06 is read by the Pi: a crashed companion also stops feeding OBSTACLE_DISTANCE
                if t - self.last_lidar >= 1.0 / self.lidar_hz and not self.comp.crashed and not self.comp.sleeping: self.last_lidar = t; self.send_lidar()
                if self.radar is not None and t - self.last_radar >= 0.1 and not self.comp.crashed and not self.comp.sleeping:   # Rev G4: 24 GHz radars, 10 Hz
                    self.last_radar = t; self.radar_tgts = self.radar.scan(self.w)
                if abs(self.w.pack_v - self.batt_sent) > 0.04 and self.gcs is not None:
                    self.batt_sent = self.w.pack_v       # SITL battery = SIM_BATT_VOLTAGE (the JSON backend has no battery field in 4.6.2)
                    self.gcs.mav.param_set_send(1, 1, b'SIM_BATT_VOLTAGE', float(self.w.pack_v), mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
                self.pump()
                self.integrate_energy(dt)
                if t - self.last_log >= 0.1:
                    self.last_log = t
                    if not self.comp.crashed: self.comp.tick(t)
                    else: self.comp.crash_monitor(t)
                    self.log()
                if self.comp.done or t > self.tmax:
                    if t > self.tmax: self.ev('sim', 'time limit %.0f s reached' % self.tmax)
                    break
        finally:
            self.stop()
            self.save(time.time() - t_wall, n)

    def pump(self):
        for conn in (self.gcs, self.sens):
            if conn is None: continue
            while True:
                m = conn.recv_match(blocking=False)
                if m is None: break
                if conn is self.gcs: self.comp.on_msg(m)
                if m.get_type() == 'STATUSTEXT' and conn is self.gcs: self.ev('fw', m.text)

    def integrate_energy(self, dt):
        w = self.w; c = self.comp
        g_dir = w.grade_here() * (1 if w.v >= 0 else -1)
        p = power_w(w.v, w.w, g_dir, w.attached, w.bin_mass, abs(w.v) > 0.02, w.night and c.state.startswith(('DOCK', 'VIEW', 'SEEK', 'NUDGE')),
                    abs(w.hook_tilt - (BIN['tilt_deg'] if self.pwm[4] > 1700 else 0)) > 0.5, lights_w=c.lights_w())
        p += companion.RADAR_W + c.audio_w()             # Rev G4: two 24 GHz radar modules + audio amplifier
        if c.sleeping: p = companion.SLEEP_W            # Rev G3: RTC sleep (Pi, 4G, RTK off)
        w.pack_step(p, dt)                               # Rev G3: pack model (dock supply carries the bus when docked)
        e = p * dt / 3600.0; self.energy_wh += e
        self.leg_energy[c.leg] = self.leg_energy.get(c.leg, 0.0) + e

    def keep_left_stats(self):
        """Rev G4: keep-left evaluation from the TRUTH pose: gap between the tug's left side and the left lane edge (lane edge =
        surveyed lane half-width 1.8 m; the hedge line is 0.25 m beyond it), per direction, over lane-leg samples flagged
        keep-left by the companion (AUTO, moving > 0.1 m/s). Also the towed bin's left side."""
        S = self.site; out = {}
        for sgn, key in ((1, 'down'), (-1, 'up')):
            g = []; gb = []; dist = 0.0
            for r in self.trace:
                if not r.get('kl') or abs(r['v']) < 0.1: continue
                h = S.lane.heading(S.lane.project(np.array([r['x'], r['y']]))[0])
                if math.cos(wrap(r['yaw'] - h)) * sgn < 0.5: continue
                s, lat = S.lane.project(np.array([r['x'], r['y']])); g.append(left_gap(S.lane.width, lat, sgn)); dist += abs(r['v']) * 0.1
                if r['att'] and r['bin'] is not None:
                    sb, lb = S.lane.project(np.array(r['bin'][:2])); gb.append(left_gap(S.lane.width, lb, sgn, half=BIN['w'] / 2))
            if g:
                g = np.array(g); out[key] = dict(n=len(g), dist_m=round(dist, 0), mean=round(float(g.mean()), 3), min=round(float(g.min()), 3),
                                                 max=round(float(g.max()), 3), sd=round(float(g.std()), 3), pct_in_0p3_0p5=round(100.0 * float(np.mean((g >= 0.3) & (g <= 0.5))), 1))
                if gb: gb = np.array(gb); out[key].update(bin_mean=round(float(gb.mean()), 3), bin_min=round(float(gb.min()), 3))
        return out

    def book_sleep(self, wh, secs, on_dock):
        """Rev G3: RTC sleep time skipped by the simulation, booked analytically."""
        self.sleep_wh += wh; self.sleep_s += secs
        if not on_dock: self.w.pack_step(wh * 3600.0 / max(secs, 1.0), secs)

    def ev(self, kind, text, **kw):
        d = dict(t=round(self.w.t, 2), kind=kind, text=text); d.update(kw); self.events.append(d)
        print('[%7.1f] %-5s %s' % (self.w.t, kind, text), flush=True)

    def log(self):
        w = self.w; c = self.comp
        sec = getattr(self, 'sector', None)
        front = None
        if self.scan is not None:
            r = self.scan; fr = r[np.r_[0:60, 300:360]]; fr = fr[np.isfinite(fr)]
            front = float(fr.min()) if len(fr) else None
        b = w.bin
        self.trace.append(dict(t=round(w.t, 2), x=round(w.x, 3), y=round(w.y, 3), yaw=round(w.yaw, 4), v=round(w.v, 3), w=round(w.w, 3),
                               mode=c.mode, state=c.state, leg=c.leg, fix=self.gps_fix, lidar=None if front is None else round(front, 2),
                               bin=None if b is None else [round(b['x'], 3), round(b['y'], 3), round(b['yaw'], 4), b['state']],
                               others=[[round(o['x'], 2), round(o['y'], 2), round(o['yaw'], 3)] for o in w.others],
                               att=bool(w.attached), hook=round(float(w.hook_tilt), 1), hitch=round(w.hitch, 1), seat=bool(w.seat), bump=bool(w.bumper),
                               ekf=c.ekf_xy, eyaw=None if c.yaw is None else round(c.yaw, 4), wh=round(self.energy_wh, 3), det=c.last_det_summary, alert=c.alert_flag,
                               movers=[list(map(lambda q: round(q, 2), m['pos'](w.t))) + [m['r'], m['kind']] for m in w.movers],
                               sec=None if sec is None else [int(min(s, 1201)) for s in sec[::2]], spd=round(c.speed_cmd, 2),
                               pwm=[self.pwm[i] for i in (0, 2, 4)], lights=c.lights_str(), crashed=c.crashed,
                               chain=bool(w.chain_ok), xb=bool(w.crossbeam), soc=round(w.soc, 4), pv=round(w.pack_v, 2), dkv=bool(w.dock_v),
                               chg=round(w.charge_a, 1), tgt=c.target, clk=None if c.clock0 is None else round(c.clock(), 2), slp=bool(c.sleeping),
                               others_id=[o.get('id0', 10) for o in w.others], bin_id=None if b is None else b.get('id0', 0),
                               veh=[[round(v.x, 2), round(v.y, 2), round(v.yaw, 3), v.L, v.W, v.name] for v in w.vehicles if v.on],
                               rad=[[q['side'][0], q['r'], q['vr'], q['snr']] for q in self.radar_tgts if q['snr'] > 18][:4],
                               vstop=c.vstop_state, kl=c.kl_active, aud=c.audio['state'], pc=None if w.pack_c is None else round(w.pack_c, 1),
                               **self.g6_log()))

    def g6_log(self):
        """Rev G6 lateral-control trace fields (truth lateral, Pi fused lateral, raw GNSS lateral, corridor state, target)."""
        w = self.w; L = self.site.lane
        s_t, l_t = L.project(np.array([w.x, w.y]))
        d = dict(tl=round(float(l_t), 3), ts=round(float(s_t), 2), rq=self.gps_q, rf=self.raw_fix)
        gs, gl = L.project(np.array(self.raw_xy)); d['gl'] = round(float(gl), 3); d['gs'] = round(float(gs), 2)
        if self.fus.p is not None:
            fs, fl = L.project(self.fus.p); d['fl'] = round(float(fl), 3); d['fs'] = round(float(fs), 2)
        d['cv'] = bool(self.fus.corr_valid); d['nw'] = bool(self.fus.narrow); d['nwalls'] = len(self.walls)
        d['ltg'] = getattr(self.comp, 'lat_target_now', None); d['fq'] = self.fus.quality() if self.corridor_on else None
        return d

    def lateral_stats(self):
        """Rev G6: cross-track (truth lateral - commanded lateral) on keep-left lane legs, the Pi's lateral estimate error, the raw GNSS
        lateral error, split by RTK quality, plus truth closest approach to the hedge faces and the geofence."""
        rows = [r for r in self.trace if r.get('kl') and r.get('ltg') is not None and abs(r['v']) > 0.1]
        out = dict(n=len(rows))
        if rows:
            xte = np.array([r['tl'] - r['ltg'] for r in rows]); ee = np.array([r['fl'] - r['tl'] for r in rows if 'fl' in r])
            ge = np.array([r['gl'] - r['tl'] for r in rows if r['rf'] > 1])
            def st(a):
                if len(a) == 0: return None
                return dict(mean=round(float(a.mean()), 3), sd=round(float(a.std()), 3), p95_abs=round(float(np.percentile(np.abs(a), 95)), 3), max_abs=round(float(np.abs(a).max()), 3))
            out['xte'] = st(xte); out['est_err'] = st(ee); out['gnss_lat_err'] = st(ge)
            for qn in ('rtk', 'float', 'none', 'wrongfix'):
                sub = np.array([r['tl'] - r['ltg'] for r in rows if r['rq'] == qn])
                if len(sub): out['xte_' + qn] = st(sub); out['n_' + qn] = len(sub)
            sub = np.array([r['tl'] - r['ltg'] for r in rows if not r['cv']])
            if len(sub): out['xte_no_corridor'] = st(sub); out['n_no_corridor'] = len(sub)
            out['corridor_valid_pct'] = round(100.0 * np.mean([r['cv'] for r in rows]), 1)
        out['hedge_clear_min_m'] = round(self.w.hedge_clear_min, 3) if self.w.hedge_clear_min < 8 else None
        out['hedge_clear_at'] = self.w.hedge_clear_at; out['fence_clear_min_m'] = round(self.w.fence_clear_min, 3) if self.w.fence_clear_min < 8 else None
        out['fusion'] = dict(self.fus.stats); out['multipath_events'] = None if self.mp is None else len(self.mp.events)
        if self.mp is not None:
            ev = {}
            for e in self.mp.events: ev[e['kind']] = ev.get(e['kind'], 0) + 1
            out['multipath_by_kind'] = ev
        return out

    def save(self, wall, n):
        w = self.w
        res = dict(scenario=self.name, title=self.sc['title'], night=w.night, sim_time_s=round(w.t, 1), wall_s=round(wall, 1), frames=n,
                   result=self.comp.result, outcome=self.comp.outcome_text, energy_wh=round(self.energy_wh, 2),
                   leg_energy_wh={k: round(v, 2) for k, v in self.leg_energy.items()}, leg_time_s=self.comp.leg_time,
                   hitch_max_deg=round(w.hitch_max, 1), hitch_limit_hits=w.hitch_limit_hits, odo_m=round(w.odo, 1), fence_breach=w.fence_breach,
                   stops=self.comp.stops, alerts=self.comp.alerts, metrics=self.comp.metrics, events=self.events,
                   expect=self.sc.get('expect', 'pass'), seed=int(os.environ.get('BT_SEED', '7')),
                   legal_min_inside_m=round(w.legal_min, 2) if w.legal_min < 1e8 else None, legal_min_xy=w.legal_min_xy,
                   rev_speed_max=round(w.rev_v_max, 3), chain_trips=w.chain_trips, crossbeam_events=w.crossbeam_events, push_m=round(w.push_m, 3),
                   soc_start=w.soc0, soc_end=round(w.soc, 4), pack_wh_out=round(w.pack_wh_out, 2), air_c=w.air_c,
                   sleep_wh=round(self.sleep_wh, 2), sleep_h=round(self.sleep_s / 3600.0, 2), clock_start=self.sc.get('clock'),
                   release_tries=w.rel_tries, still_hooked=bool(w.attached),
                   hedge_overlap_m=round(w.hedge_overlap, 2), hedge_overlap_at=w.hedge_overlap_xy,
                   keep_left=self.keep_left_stats(), vehicles=[dict(name=v.name, mode=v.mode, dirn=v.dirn, appeared=bool(getattr(v, 't0', None) is not None),
                                                                    passed=v.passed, min_gap_tug_m=round(v.min_gap, 2), min_gap_bin_m=round(v.min_gap_bin, 2) if v.min_gap_bin < 90 else None)
                                                               for v in w.vehicles],
                   keepout_max_depth_m=None if not self.site.keepouts else round(w.ko_max, 2), keepouts=[k['name'] for k in self.site.keepouts],
                   vehicle_stops=self.comp.vstops, audio_log=self.comp.audio['log'], pack_c_end=None if w.pack_c is None else round(w.pack_c, 1),
                   lateral=self.lateral_stats(), hitch_cap_deg=G6.HITCH_CAP_DEG, mass_kg=G6.M_TUG_KG(), corridor_on=self.corridor_on,
                   hitch_guard=getattr(self.comp, 'hitch_events', []), pack=getattr(w, 'pack_name', None))
        json.dump(res, open(os.path.join(self.out, 'result.json'), 'w'), indent=1, default=_jd)
        json.dump(dict(meta=dict(scenario=self.name, title=self.sc['title'], night=w.night, variant=self.site.variant,
                                 static=[dict(o) for o in w.obst], zones=w.gps_zones), trace=self.trace),
                  open(os.path.join(self.out, 'trace.json'), 'w'), default=_jd)
        print('saved', self.name, 'sim %.0f s in %.0f s wall, %d frames, result=%s' % (w.t, wall, n, self.comp.result), flush=True)


if __name__ == '__main__':
    import signal
    def _term(*a): raise KeyboardInterrupt('SIGTERM')      # Rev G3: a killed run still saves its trace/result (finally:)
    signal.signal(signal.SIGTERM, _term)
    name = sys.argv[1]; inst = int(sys.argv[sys.argv.index('--instance') + 1]) if '--instance' in sys.argv else 0
    tmax = float(sys.argv[sys.argv.index('--tmax') + 1]) if '--tmax' in sys.argv else None
    Runner(name, inst, tmax).run()
