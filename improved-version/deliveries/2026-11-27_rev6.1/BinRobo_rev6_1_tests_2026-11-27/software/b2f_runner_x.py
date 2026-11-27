#!/usr/bin/env python3
"""B2-F lane SITL runner: real ArduPilot Rover 4.6.2 SITL binary (--model JSON, lock-step) + b2f_world physics +
b2f_companion (Pi) over MAVLink. Chunked: each call runs the scenario queue for a wall budget; at the budget the Pi brings
the robot to rest at a safe point, the whole state (world, Pi state, trace) is pickled, SITL is stopped. The next call
relaunches SITL with --home at the checkpoint pose (firmware boot + EKF init + fence upload + arm) and continues.
Usage: b2f_runner.py <queue.txt> [--budget 100]     queue lines: <scenario> <seed>
"""
import json, math, os, socket, struct, subprocess, sys, time, pickle, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'scripts_base'))
os.environ['MAVLINK20'] = '1'
from pymavlink import mavutil
from pymavlink.rotmat import Matrix3, Vector3
from world import xy2ll, wrap
import b2f_world as BW
# revision 2 switches (unset = B2-F): longer nose and robot mass, applied before the scenarios and the companion read them
BW.ROB['x1'] += float(os.environ.get('X_NOSE_DX', '0')); BW.ROB['mass'] = float(os.environ.get('X_ROB_MASS', BW.ROB['mass']))
BW.ROB['vmax'] = float(os.environ.get('X_ROB_VMAX', BW.ROB['vmax']))   # [revision 6] wheel speed at full throttle (0.80 as B2-F; 1.24 with the 2:1 chain stage)
import b2f_scen as SCN
import importlib; CP = importlib.import_module(os.environ.get('X_COMP', 'b2f_companion'))
import b2f_r6 as R6M; ROB = BW.ROB

# [revision 6 test] walkers that follow the lane (the scenario's own movers only walk a straight line): a mover with a 'poly' key walks that polyline
_mp0 = BW.World.mover_pos
def _mover_pos(self, m):
    if 'poly' not in m: return _mp0(self, m)
    if m['t0'] is None:
        if math.hypot(self.x - m['mid'][0], self.y - m['mid'][1]) < m['trigger_d']: m['t0'] = self.t + m.get('delay', 0.0)
        else: return None
    if self.t < m['t0']: return None
    P = np.array(m['poly']); cum = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]; d = (self.t - m['t0']) * m['speed']; pd = cum[-1] * m.get('pause_at', 0.5)
    if d > pd: d = pd + max(0.0, d - pd - m.get('pause', 0.0) * m['speed'])
    if d >= cum[-1]: return None
    i = int(np.searchsorted(cum, d, side='right')) - 1; f = (d - cum[i]) / max(cum[i + 1] - cum[i], 1e-9); q = P[i] + (P[i + 1] - P[i]) * f
    return (float(q[0]), float(q[1]))
BW.World.mover_pos = _mover_pos
INST = int(os.environ.get('X_INST', '0'))   # second SITL instance on shifted ports, so two campaigns can run side by side

OUT = os.environ.get('B2F_OUT', '/workspace/work/out/b2f_lane/sitl/runs')
CK = os.path.join(ROOT, 'ckpt' + os.environ.get('X_CK', ''))
BINARY = os.path.join(ROOT, 'bin', 'ardurover_aarch64' if os.uname().machine == 'aarch64' else 'ardurover')
PARM = os.path.join(ROOT, 'params', 'bintug_b2f.parm')
GPS_EPOCH_OFFSET = 315964800; LEAP = 18
def _jd(o): return o.item() if hasattr(o, 'item') else (o.tolist() if hasattr(o, 'tolist') else str(o))


class Runner:
    def __init__(self, name, seed, budget):
        self.name = name; self.seed = seed; self.key = '%s__s%d%s' % (name, seed, os.environ.get('B2F_SUFFIX', '')); self.budget = budget
        self.ckf = os.path.join(CK, self.key + '.pkl'); self.out = os.path.join(OUT, self.key); os.makedirs(self.out, exist_ok=True)
        if os.path.exists(self.ckf):
            d = pickle.load(open(self.ckf, 'rb'))
            self.w = d['w']; self.sc = d['sc']; self.trace = d['trace']; self.events = d['events']; self.cst = d['cst']; self.chunks = d['chunks']
            self.dr = d.get('dr')
        else:
            self.sc = SCN.build(name, seed); self.w = self.sc.pop('world')
            for q_ in [k for k in os.environ.get('X_MOVER', '').split(',') if k]:   # [revision 5 test] 'person:pause:60,person:trigger_d:3.0': change a mover of the scenario
                kind_, key_, val_ = q_.split(':')
                for m_ in self.w.movers:
                    if m_['kind'] == kind_: m_[key_] = float(val_)
            if os.environ.get('X_MOVERS_SET'):   # [revision 6 test] replace the scenario's movers. JSON list of dicts: kind, r, speed, a=[s, lat], b=[s, lat], trig=[s, lat] (trigger point),
                # trigger_d, pause, pause_at, delay. Stations are metres from the house; lat is metres left of the lane centre line.
                S_ = self.w.S; mv_ = []
                for q_ in json.loads(os.environ['X_MOVERS_SET']):
                    a_ = S_.lane.point(q_['a'][0], q_['a'][1]); b_ = S_.lane.point(q_['b'][0], q_['b'][1]); g_ = S_.lane.point(*q_['trig']) if 'trig' in q_ else 0.5 * (a_ + b_)
                    poly_ = [S_.lane.point(float(ss_), q_['a'][1] + (q_['b'][1] - q_['a'][1]) * k_ / max(1, int(abs(q_['b'][0] - q_['a'][0])))).tolist() for k_, ss_ in enumerate(np.linspace(q_['a'][0], q_['b'][0], max(2, int(abs(q_['b'][0] - q_['a'][0])) + 1)))] if q_.get('along') else None
                    mv_.append(dict(kind=q_.get('kind', 'person'), r=q_.get('r', 0.25), a=a_.tolist(), b=b_.tolist(), mid=g_.tolist(), speed=q_.get('speed', 1.0), trigger_d=q_.get('trigger_d', 5.0),
                                    pause=q_.get('pause', 0.0), pause_at=q_.get('pause_at', 0.5), t0=None, delay=q_.get('delay', 0.0)))
                    if poly_: mv_[-1]['poly'] = poly_
                self.w.movers = mv_
            if os.environ.get('X_HEDGE_GAP'):   # [revision 6 test] 's0:s1:side' (side +1 = left of house->road, -1 = right): a gateway - the hedge is cut out of the truth and of the map between the two stations
                g0_, g1_, gs_ = [float(v_) for v_ in os.environ['X_HEDGE_GAP'].split(':')]; S_ = self.w.S
                for nm_ in ('hedge_truth', 'hedge'):
                    H_ = getattr(S_, nm_); mid_ = 0.5 * (H_[:, :2] + H_[:, 2:]); sl_ = np.array([S_.lane.project(q2_) for q2_ in mid_])
                    setattr(S_, nm_, H_[~((sl_[:, 0] > g0_) & (sl_[:, 0] < g1_) & (sl_[:, 1] * gs_ > 0))])
            for q_ in json.loads(os.environ.get('X_OBST_ADD', '[]')):   # [revision 6 test] unmapped standing things: s, lat, L, W (m)
                c_ = self.w.S.lane.point(q_['s'], q_['lat']); self.w.obst.append(dict(x=float(c_[0]), y=float(c_[1]), yaw=float(self.w.S.lane.heading(q_['s'])), L=q_.get('L', 0.4), W=q_.get('W', 0.4), kind=q_.get('kind', 'box')))
            self.trace = []; self.events = []; self.cst = None; self.chunks = []; self.dr = None
        self.pwm = [1500] * 16; self.prev_vel = np.zeros(3); self.acc_f = np.zeros(3); self.gps_err = np.zeros(2)
        self.last_gps = -1; self.last_lidar = -1; self.last_log = -1; self.scan = None; self.sector = None; self.batt_sent = 0
        self.gps_fix = 6; self.raw_fix = 6; self.gps_q = 'rtk'; self.sens = None; self.gcs = None

    # ------------------------------------------------------------ SITL process
    def launch(self):
        rd = os.path.join(self.out, 'sitlrun'); os.makedirs(rd, exist_ok=True)
        w = self.w; hdg = (90 - math.degrees(w.yaw)) % 360; z = w.S.ter.z(w.x, w.y); lat, lon = xy2ll(w.x, w.y)
        self.z0 = z; self.x0, self.y0 = w.x, w.y
        parm = PARM
        extra = list(self.sc.get('params') or []) + [q.strip() for q in os.environ.get('B2F_PARAMS', '').split(';') if q.strip()]
        if extra:
            parm = os.path.join(rd, 'scenario.parm'); open(parm, 'w').write(open(PARM).read() + '\n# scenario overrides\n' + '\n'.join(extra) + '\n')
        port = 9002 + 10 * INST
        # infrastructure (post-freeze deviation D1, no robot behaviour change): SITL binds its TCP serial ports without
        # SO_REUSEADDR; a port still in TIME_WAIT from the previous chunk made SERIAL0 fail ('bind failed on port 5760') and
        # the chunk ran without its GCS link (scored s1a__s7 chunk 1). Wait until 5760 / 5762 are bindable (max 80 s).
        for k in range(160):
            busy = False
            for p_ in (5760 + 10 * INST, 5762 + 10 * INST, 5763 + 10 * INST):
                t_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try: t_.bind(('0.0.0.0', p_))
                except OSError: busy = True
                finally: t_.close()
            if not busy: break
            time.sleep(0.5)
        args = [BINARY, '-w', '--model', 'JSON:127.0.0.1', '--speedup', '200', '--rate', '50', '--defaults', parm,
                '--home', '%.8f,%.8f,%.2f,%.1f' % (lat, lon, z, hdg), '-I%d' % INST, '--sim-port-out', str(port), '--sim-port-in', str(port + 1)]
        self.sitl_log = open(os.path.join(rd, 'sitl_stdout_c%d.txt' % len(self.chunks)), 'w')
        self.proc = subprocess.Popen(args, cwd=rd, stdout=self.sitl_log, stderr=subprocess.STDOUT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        for k in range(40):
            try: self.sock.bind(('127.0.0.1', port)); break
            except OSError: time.sleep(0.5)
        self.sock.settimeout(10)
        for k in range(60):
            try: self.gcs = mavutil.mavlink_connection('tcp:127.0.0.1:%d' % (5760 + 10 * INST), source_system=255, source_component=191, autoreconnect=False); break
            except Exception: time.sleep(0.3)

    def stop(self):
        for c_ in (self.gcs, self.sens):      # D1: client side closes first, so TIME_WAIT lands on its ephemeral port, not on 5760
            try: c_.close()
            except Exception: pass
        time.sleep(0.3)
        try: self.proc.terminate(); self.proc.wait(5)
        except Exception:
            try: self.proc.kill()
            except Exception: pass
        try: self.sock.close()
        except Exception: pass
        try: self.gcs.close()
        except Exception: pass
        try: self.sens.close()
        except Exception: pass

    # ------------------------------------------------------------ physics reply
    def fdm_json(self, dt):
        """physics reply. Attitude from the DEM slope, low-passed (tau 0.3 s); body rates are the kinematic rates of THAT attitude
        (G6 sent gyro = [0, 0, yaw rate] with a sign-flipped roll: on the lane's cross-slopes the EKF tilt drifted a few deg and,
        through the 67 deg magnetic dip, the compass heading 10-15 deg - found in the B2-F dev runs)."""
        w = self.w; yaw_ned = wrap(math.pi / 2 - w.yaw)
        gx, gy = w.S.ter.grad(w.x, w.y); c, s = math.cos(w.yaw), math.sin(w.yaw)
        pitch_t = math.atan(gx * c + gy * s); roll_t = math.atan(-gx * s + gy * c)      # ground rising to the left -> right side down -> +roll
        if not hasattr(self, 'rp'): self.rp = [roll_t, pitch_t]
        k = min(1.0, dt / 0.3); r0, p0 = self.rp
        roll = r0 + (roll_t - r0) * k; pitch = p0 + (pitch_t - p0) * k; self.rp = [roll, pitch]
        dr = (roll - r0) / dt; dp = (pitch - p0) / dt; dy = -w.w
        gyro = [dr - math.sin(pitch) * dy, math.cos(roll) * dp + math.sin(roll) * math.cos(pitch) * dy,
                -math.sin(roll) * dp + math.cos(roll) * math.cos(pitch) * dy]
        z = w.S.ter.z(w.x, w.y) - self.z0
        vx, vy = w.v * c, w.v * s; vz = (gx * vx + gy * vy)
        vel = np.array([vy, vx, -vz]); acc = (vel - self.prev_vel) / dt; self.prev_vel = vel; self.acc_f = 0.7 * self.acc_f + 0.3 * acc
        R = Matrix3(); R.from_euler(roll, pitch, yaw_ned)
        f = R.transposed() * Vector3(self.acc_f[0], self.acc_f[1], self.acc_f[2] - 9.80665)
        d = dict(timestamp=w.t - self.t_chunk0, imu=dict(gyro=gyro, accel_body=[f.x, f.y, f.z]),
                 position=[w.y - self.y0, w.x - self.x0, -z], attitude=[roll, pitch, yaw_ned], velocity=vel.tolist())
        return (json.dumps(d, separators=(',', ':')) + '\n').encode()

    # ------------------------------------------------------------ sensors to the firmware
    def send_gps(self):
        w = self.w; q, bias = w.gps_quality()
        gf_ = os.environ.get('X_GPS_FAULT')   # [revision 5 test] '<s0>:<s1>:<direction deg from the lane heading, + = left>:<metres>': Float quality with this bias between the two stations
        if gf_:
            a_, b_, d_, m_ = [float(k) for k in gf_.split(':')]; s_ = float(w.s_lat()[0])
            if a_ <= s_ <= b_:
                h_ = w.S.lane.heading(s_) + math.radians(d_); q = 'float'; bias = np.array([m_ * math.cos(h_), m_ * math.sin(h_)])
        self.gps_q = q
        fix = {'rtk': 6, 'wrongfix': 6, 'float': 5, 'none': 1}[q]; self.raw_fix = fix
        sig = {6: 0.012, 5: 0.25, 1: 3.0}[fix]
        self.gps_err = 0.9 * self.gps_err + w.rng.normal(0, sig * 0.45, 2)
        x, y = w.x + self.gps_err[0] + bias[0], w.y + self.gps_err[1] + bias[1]
        out = self.comp.gnss_fuse(fix, x, y)
        if out is None: fix = 1
        else: x, y, fix, sig = out
        self.gps_fix = fix
        if fix == 1:
            self.sens.mav.gps_input_send(int(w.t * 1e6), 0, 0, 0, 0, 1, 0, 0, 0, 99.0, 99.0, 0, 0, 0, 9, 99, 99, 3, 0); return
        lat, lon = xy2ll(x, y); alt = w.S.ter.z(w.x, w.y)
        tow_s = 1_700_000_000 + w.t - GPS_EPOCH_OFFSET + LEAP; week = int(tow_s // 604800); ms = int((tow_s % 604800) * 1000)
        self.sens.mav.gps_input_send(int(w.t * 1e6), 0, 0, ms, week, fix, int(lat * 1e7), int(lon * 1e7), alt,
                                     0.6 if fix == 6 else 1.2, 0.9, w.v * w.odo_k * math.sin(w.yaw) + self.comp.corr_v[1], w.v * w.odo_k * math.cos(w.yaw) + self.comp.corr_v[0], 0.0,
                                     0.05 if fix == 6 else 0.3, sig * 1.5, sig * 2.5, 22 if fix == 6 else 13, 0)

    def send_lidar(self):
        """LD06 scan -> Pi (companion keeps it) -> OBSTACLE_DISTANCE (72 x 5 deg) to the firmware proximity library."""
        r = self.w.lidar()
        if R6M.LID_BAD:      # test hook: a worse lidar and a real hedge (b2f_r6.lid_degrade)
            w_ = self.w; ox_ = w_.x + ROB['lidar_x'] * math.cos(w_.yaw); oy_ = w_.y + ROB['lidar_x'] * math.sin(w_.yaw)
            if not hasattr(self, '_lidbad_rng'): self._lidbad_rng = np.random.default_rng(7070 + int(self.seed)); self._lidbad_st = {}
            r = R6M.lid_degrade(w_, ox_, oy_, w_.yaw + np.radians(np.arange(360)), r, self._lidbad_rng, self._lidbad_st)
        self.scan = r; self.comp.on_scan(r)
        cw = np.array([r[(-k) % 360] for k in range(360)]); dist = np.full(72, 65535, np.int64)
        for i in range(72):
            seg = cw[5 * i - 2: 5 * i + 3] if i > 0 else np.r_[cw[-2:], cw[:3]]
            m = np.min(seg); dist[i] = 1201 if not np.isfinite(m) else int(max(5, m * 100))
        self.sector = dist
        self.sens.mav.obstacle_distance_send(int(self.w.t * 1e6), mavutil.mavlink.MAV_DISTANCE_SENSOR_LASER, dist.tolist(), 5, 5, 1200, 0, 0,
                                             mavutil.mavlink.MAV_FRAME_BODY_FRD)

    # ------------------------------------------------------------ main loop (one chunk)
    def run_chunk(self):
        t_wall0 = time.time(); self.t_chunk0 = self.w.t
        self.launch()
        self.comp = CP.Companion(self, self.sc, self.cst)
        self.ev('sim', 'chunk %d start: SITL launched, home = checkpoint pose s=%.1f' % (len(self.chunks), float(self.w.s_lat()[0])))
        frame_last = -1; reply = None; n = 0; status = 'running'
        try:
            while True:
                try: data, addr = self.sock.recvfrom(256)
                except socket.timeout:
                    self.ev('sim', 'SITL stopped sending servo packets'); status = 'sitl_timeout'; break
                if len(data) < 40: continue
                magic, rate, fc = struct.unpack('<HHI', data[:8])
                if magic != 18458: continue
                pwm = list(struct.unpack('<16H', data[8:40]))
                if fc == frame_last and reply is not None: self.sock.sendto(reply, addr); continue
                frame_last = fc; dt = 1.0 / max(rate, 1)
                pwm = [p if p > 900 else 1500 for p in pwm]; self.pwm = pwm
                self.w.step(dt, pwm); self.comp.odometry(dt)
                reply = self.fdm_json(dt); self.sock.sendto(reply, addr); n += 1
                t = self.w.t
                if self.sens is None and t - self.t_chunk0 > 1.0:
                    try: self.sens = mavutil.mavlink_connection('tcp:127.0.0.1:%d' % (5762 + 10 * INST), source_system=255, source_component=192)
                    except Exception: self.sens = None
                if self.sens is not None:
                    if t - self.last_gps >= 0.2: self.last_gps = t; self.send_gps()
                    if t - self.last_lidar >= 0.1 and not self.comp.st['crashed']: self.last_lidar = t; self.send_lidar()
                    if abs(self.w.pack_v() - self.batt_sent) > 0.05:
                        self.batt_sent = self.w.pack_v(); self.gcs.mav.param_set_send(1, 1, b'SIM_BATT_VOLTAGE', float(self.batt_sent), mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
                self.pump()
                if t - self.last_log >= 0.1:
                    self.last_log = t; self.comp.tick(t); self.log()
                if self.comp.st['result'] != 'running': status = 'done'; break
                if t > self.sc['tmax']: self.ev('sim', 'time limit %.0f s' % self.sc['tmax']); self.comp.finish('timeout', 'time limit'); status = 'done'; break
                if time.time() - t_wall0 > self.budget and not self.comp.pause_req:
                    self.comp.pause_req = True
                if self.comp.paused: status = 'paused'; break
                if time.time() - t_wall0 > self.budget + 12:      # could not reach a safe pause point: force (logged)
                    self.ev("sim", "forced pause (no safe point within 12 s)"); status = "paused"; break
        finally:
            self.stop()
        self.chunks.append(dict(t0=round(self.t_chunk0, 1), t1=round(self.w.t, 1), wall=round(time.time() - t_wall0, 1), frames=n, status=status))
        self.cst = self.comp.state_for_ckpt()
        if status in ('paused', 'sitl_timeout') and self.comp.st['result'] == 'running':
            pickle.dump(dict(w=self.w, sc=self.sc, trace=self.trace, events=self.events, cst=self.cst, chunks=self.chunks), open(self.ckf, 'wb'))
            print('checkpoint', self.key, 't=%.0f' % self.w.t, 'wall %.0f' % (time.time() - t_wall0), flush=True); return False
        self.save(); 
        if os.path.exists(self.ckf): os.remove(self.ckf)
        return True

    def pump(self):
        for conn in (self.gcs, self.sens):
            if conn is None: continue
            while True:
                try: m = conn.recv_match(blocking=False)
                except Exception: m = None
                if m is None: break
                if conn is self.gcs:
                    self.comp.on_msg(m)
                    if m.get_type() == 'STATUSTEXT': self.ev('fw', m.text)

    def ev(self, kind, text, **kw):
        d = dict(t=round(self.w.t, 2), kind=kind, text=text); d.update(kw); self.events.append(d)
        print('[%7.1f] %-4s %s' % (self.w.t, kind, text), flush=True)

    def log(self):
        w = self.w; c = self.comp; st = c.st; s, lat = w.s_lat()
        cb = None
        if w.carry: bx, by, byaw = w.carried_xy(); cb = [round(bx, 3), round(by, 3), round(byaw, 4)]
        self.trace.append(dict(t=round(w.t, 2), x=round(w.x, 3), y=round(w.y, 3), yaw=round(w.yaw, 4), v=round(w.v, 3), w=round(w.w, 3),
                               s=round(float(s), 2), lat=round(float(lat), 3), mode=c.mode, state=st['state'], op=st['opname'],
                               fix=self.gps_fix, rq=self.gps_q, ekf=c.ekf_xy, carry=w.carry, cb=cb, lift=round(w.lift_q, 3),
                               bins={k: [round(b['x'], 2), round(b['y'], 2), round(b['yaw'], 3), b['state'], b['size']] for k, b in w.bins.items()},
                               mv=[[round(a, 2), round(b, 2), r, k] for a, b, r, k in w.movers_now()],
                               cars=[[o['x'], o['y'], o['yaw'], o['L'], o['W']] for o in w.standing() if o['kind'] == 'car'],
                               obst=[[o['x'], o['y'], o['yaw'], o['L'], o['W'], o['kind']] for o in w.obst],
                               hc=round(min(w.hedge_min, 9.9), 3), hcl=round(c.hc_now, 3) if c.hc_now is not None else None,
                               wh=round(w.energy_wh, 3), soc=round(w.soc, 4), clk=c.clock_str(), spd=round(c.speed_cmd, 2),
                               alert=st['alerts'][-1] if st['alerts'] else None, chain=w.chain_ok, ltg=c.lat_tgt,
                               sec=None if self.sector is None else [int(min(q, 1201)) for q in self.sector],
                               lid=None if self.scan is None else [round(float(q), 2) if np.isfinite(q) else None for q in self.scan[::3]],
                               crashed=st['crashed'], gs=c.ap_gs, thr=c.ap_thr, dLR=[None if q is None else round(q, 3) for q in c.dLR], ev=c.ekf_v, cv=[round(c.corr_v[0], 3), round(c.corr_v[1], 3)], gdr=None if st['dr'] is None else round(math.hypot(st['dr'][0] - w.x, st['dr'][1] - w.y), 3), eyaw=None if c.yaw is None else round(c.yaw, 4), pwm=[self.pwm[0], self.pwm[2]]))

    def save(self):
        w = self.w; st = self.comp.st
        res = dict(scenario=self.name, seed=self.seed, title=self.sc['title'], expect=self.sc['expect'], result=st['result'], outcome=st['outcome'],
                   alerts=st['alerts'], sim_time_s=round(w.t, 1), chunks=self.chunks, energy_wh=round(w.energy_wh, 2), soc_start=self.sc.get('soc0'),
                   soc_end=round(w.soc, 4), odo_m=round(w.odo, 1), hedge_min_m=round(w.hedge_min, 3) if w.hedge_min < 90 else None,
                   hedge_min_at=w.hedge_min_at, legal_min_m=round(w.legal_min, 3) if w.legal_min < 90 else None, legal_min_at=w.legal_min_at,
                   contact_min_m=round(w.contact_min, 3) if w.contact_min < 90 else None, contact_with=w.contact_with,
                   person_rest_min_m=round(w.person_rest_min, 3) if w.person_rest_min < 90 else None,
                   car_rest_min_m=round(w.car_rest_min, 3) if w.car_rest_min < 90 else None,
                   collisions=w.collisions, chain_trips=w.chain_trips, metrics=st['metrics'], events=self.events)
        json.dump(res, open(os.path.join(self.out, 'result.json'), 'w'), indent=1, default=_jd)
        meta = dict(scenario=self.name, seed=self.seed, title=self.sc['title'], night=w.night, zones=w.zones, clock0=self.sc.get('clock'))
        json.dump(dict(meta=meta, trace=self.trace), open(os.path.join(self.out, 'trace.json'), 'w'), default=_jd)
        print('SAVED', self.key, 'result=%s outcome=%s sim %.0f s' % (st['result'], st['outcome'], w.t), flush=True)


def main():
    qf = sys.argv[1]; budget = float(sys.argv[sys.argv.index('--budget') + 1]) if '--budget' in sys.argv else 95.0
    t0 = time.time(); os.makedirs(CK, exist_ok=True)
    lines = [l.split() for l in open(qf) if l.strip() and not l.startswith('#')]
    for name, seed in lines:
        key = '%s__s%s%s' % (name, seed, os.environ.get('B2F_SUFFIX', ''))
        if os.path.exists(os.path.join(OUT, key, 'result.json')): continue
        left = budget - (time.time() - t0)
        if left < 15: break
        r = Runner(name, int(seed), left)
        done = r.run_chunk()
        if not done: break
    left = [l for l in lines if not os.path.exists(os.path.join(OUT, '%s__s%s%s' % (l[0], l[1], os.environ.get('B2F_SUFFIX', '')), 'result.json'))]
    print('QUEUE left %d / %d, wall %.0f s' % (len(left), len(lines), time.time() - t0), flush=True)


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGTERM, lambda *a: (_ for _ in ()).throw(KeyboardInterrupt()))
    main()
