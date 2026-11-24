#!/usr/bin/env python3
"""B2-F lane physics scenarios on the lane world (lane_world.py), chunked foreground runner with checkpoint/resume.
usage: lanerun.py <run_id> [budget_s=95]      run_id in RUNS below; re-call until it prints DONE.
Each run dir runs/<run_id>/: ckpt.pkl (state), rec_NNN.npz (25 fps body poses + HUD channels), snaps/ (P1 carried-state
snapshots every 2 m), result.json (metrics + verdict). simB2h.py is imported unchanged; its grab()/set_down() firmware is used."""
import os, sys, json, math, time, pickle, glob, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import importlib
LW = importlib.import_module(os.environ.get('X_LANE_WORLD', 'lane_world'))   # [22 Nov] X_LANE_WORLD=lane_world_real: the EU-DEM profile without the assumed 12 % pitch
import mujoco
B = importlib.import_module(os.environ.get('X_SIM', 'simB2h'))
from bins_g5 import BINS
T_WALL0 = time.time()
RUNS_DIR = os.environ.get('X_RUNS_DIR', os.path.join(HERE, 'runs'))
VSLOPE = sorted(tuple(float(v) for v in t.split(':')) for t in os.environ.get('X_VSLOPE', '').split(',') if t)   # [X] 'g:v_bin:v_empty,...'
VDEF = float(os.environ.get('X_VDEF', '0.5')); LDK = float(os.environ.get('X_LDK', '0'))   # [revision 6] cruise cap of a transit (0.5 as B2-F); look-ahead grows by LDK m per m/s above 0.45
VLOOK = float(os.environ.get('X_VLOOK', '0'))   # [revision 5] the slope rule looks this far ahead (m), so the robot is already slow at the brow of a pitch
VREV = float(os.environ.get('X_VREV', '0.2'))    # [revision 5] speed cap when backing down a pitch tail first
BODIES = ['tug', 'wheelL', 'wheelR', 'cforkL', 'cforkR', 'cwheelL', 'cwheelR', 'lift', 'comb', 'keeper', 'padbase', 'pad', 'bin', 'bwL', 'bwR', 'lid']
HUD = ['s', 'lat', 'grade', 'v', 'liftF', 'clear', 'hedge', 'tip', 'Wh', 'leaf', 'roll', 'pitch', 'binkg', 'carry', 'gap']
ETA_W, ETA_L, HOTEL_W, LIGHTS_W = 0.60, 0.30, 9.0, 17.0
PRE = (('yard', 0.0, 25.0), ('mouth', LW.LEN - 15, LW.LEN + 50))
LAT_OUT = [(0, LW.HOME['lat']), (12.0, LW.HOME['lat']), (24.0, 0.0), (610.0, 0.0), (619.5, LW.PAD_A['lat']), (700, LW.PAD_A['lat'])]

def S_(s, **k): d = dict(s); d.update(k); return d
BASE = dict(binkey='ESE240SL', kg=110.0, with_bin=True, variant=dict(step='ramp', trench='covered'), act_N=3000.0, pert={}, night=False, obstacles=[])
TRANSIT_OUT = [('grab',), ('drive', dict(to=LW.PAD_A['s'], ref='bin', dirn=1, knots=LAT_OUT, snaps=True)), ('setdown',)]
RUNS = {
 'P1': S_(BASE, title='P1 full 240 L (ESE 240 SL, 110 kg): home -> pad A', start='home', steps=TRANSIT_OUT),
 'P3': S_(BASE, binkey='WEB140', kg=None, title='P3 full 140 L (Weber 140, 66 kg): home -> pad A', start='home', steps=TRANSIT_OUT),
 'P7': S_(BASE, title='P7 night: P1 with bin CG +60 mm, mass x1.1, mu x0.8', start='home', night=True, pert=dict(mass=1.1, mu=0.8, cg_dz=0.06), steps=TRANSIT_OUT),
 'P2a': S_(BASE, with_bin=False, kg=0.0, title='P2a return empty: pad A -> home', start=('from', 'P1'),
           steps=[('forward', 0.45), ('pivot', 180.0), ('drive', dict(to=12.0, ref='tug', dirn=-1, knots=LAT_OUT))]),
 'P2c': S_(BASE, kg=13.0, title='P2c collect empty 240 L at pad A -> home', start=('padA_bin', 'P1'),
           steps=[('grab',), ('pivot', 180.0), ('drive', dict(to=LW.HOME['s'], ref='bin', dirn=-1, knots=LAT_OUT, snaps=True)), ('setdown',)]),
 'P4a': S_(BASE, title='P4a 12 % pitch DOWN, 110 kg, wet leaves mu 0.35, stop + hold', start=('snap', 'P1', 124.0),
           steps=[('drive', dict(to=145.0, ref='tug', dirn=1, knots=LAT_OUT)), ('hold', 10.0), ('drive', dict(to=166.0, ref='tug', dirn=1, knots=LAT_OUT))]),
 'P4b': S_(BASE, title='P4b 12 % pitch UP, 110 kg, wet leaves mu 0.35, stop + hold', start=('snap', 'P1', 170.0),
           steps=[('softstop',), ('pivot', 180.0), ('drive', dict(to=145.0, ref='tug', dirn=-1, knots=LAT_OUT)), ('hold', 10.0), ('drive', dict(to=127.0, ref='tug', dirn=-1, knots=LAT_OUT))]),
}
PF = dict(step='ramp', trench='covered', pothole='filled')
RUNS['P2a_pf'] = S_(RUNS['P2a'], variant=PF, title='P2a-pf return empty, pothole filled (supplementary)',
                    steps=[('forward', 0.45), ('pivot', 180.0), ('drive', dict(to=12.0, ref='tug', dirn=-1, knots=LAT_OUT, snaps=True))])
RUNS['P2c_pf'] = S_(RUNS['P2c'], variant=PF, title='P2c-pf collect empty 240 L, pothole filled (supplementary)', start=('snap', 'P2c', 556.0),
                    steps=[('drive', dict(to=LW.HOME['s'], ref='bin', dirn=-1, knots=LAT_OUT)), ('setdown',)])
for tag, var, act in (('P5a_drop_sharp_3kN', 'sharp', 3000.0), ('P5b_drop_sharp_4kN', 'sharp', 4000.0), ('P5c_drop_ramp14', 'ramp', 3000.0)):
    RUNS[tag] = S_(BASE, variant=dict(step=var, trench='covered'), act_N=act, title='P5 40 mm step DOWN (%s), 110 kg, lift cap %.0f N' % (var if var == 'sharp' else '1:4 ramp', act),
                   start=('snap', 'P1', 282.0), steps=[('drive', dict(to=297.0, ref='tug', dirn=1, knots=LAT_OUT, feature='step')), ('hold', 3.0)])
for tag, var, act in (('P5d_up_sharp_3kN', 'sharp', 3000.0), ('P5e_up_sharp_4kN', 'sharp', 4000.0), ('P5f_up_ramp14', 'ramp', 3000.0)):
    RUNS[tag] = S_(BASE, variant=dict(step=var, trench='covered'), act_N=act, title='P5 40 mm step UP (%s), 110 kg, lift cap %.0f N' % (var if var == 'sharp' else '1:4 ramp', act),
                   start=('snap', 'P1', 298.0), steps=[('softstop',), ('pivot', 180.0), ('drive', dict(to=283.0, ref='tug', dirn=-1, knots=LAT_OUT, feature='step')), ('hold', 3.0)])
RUNS['P5g_trench_open'] = S_(BASE, variant=dict(step='ramp', trench='open'), title='P5 trench 40 x 200 mm as-is, 110 kg', start=('snap', 'P1', 446.0),
                             steps=[('drive', dict(to=462.0, ref='tug', dirn=1, knots=LAT_OUT, feature='trench')), ('hold', 3.0)])
RUNS['P5i_trench_open_4kN'] = S_(BASE, variant=dict(step='ramp', trench='open'), act_N=4000.0, title='P5 trench 40 x 200 mm as-is, 110 kg, lift cap 4000 N', start=('snap', 'P1', 446.0),
                             steps=[('drive', dict(to=462.0, ref='tug', dirn=1, knots=LAT_OUT, feature='trench')), ('hold', 3.0)])
RUNS['P5h_pothole'] = S_(BASE, title='P5 pothole 60 mm under the left wheel, 110 kg', start=('snap', 'P1', 542.0),
                         steps=[('drive', dict(to=557.0, ref='tug', dirn=1, knots=LAT_OUT, feature='pothole')), ('hold', 3.0)])
PERSON = dict(name='person', kind='person', r=0.22, h=1.75, s=146.0, lat0=-2.3, lat1=0.0, lat2=2.4, wait=5.0, v=1.4, trig=2.2)
DOG = dict(name='dog', kind='dog', r=0.17, h=0.55, s=236.0, lat0=-2.3, lat1=2.6, v=2.5, trig=2.4)
# [revision 5] the empty robot DOWN the 12 % pitch (never run before): nose first against tail first, with a person stepping out, and a stop-and-hold.
# Start: the empty robot on its way up (snapshot of P2a_pf at s 126, facing the house). Grip on the pitch = 0.35 x X_MU_SCALE (leaf zone).
RUNS['X8n'] = S_(BASE, with_bin=False, kg=0.0, obstacles=[PERSON], title='X8n empty robot NOSE first down the 12 % pitch, person steps in', start=('snap', 'P2a_pf', 126.0),
                 steps=[('pivot', 180.0), ('drive', dict(to=156.0, ref='tug', dirn=1, knots=LAT_OUT, obstacle=True))])
RUNS['X8t'] = S_(BASE, with_bin=False, kg=0.0, obstacles=[PERSON], title='X8t empty robot TAIL first down the 12 % pitch, person steps in', start=('snap', 'P2a_pf', 126.0),
                 steps=[('drive', dict(to=156.0, ref='tug', dirn=1, rev=True, knots=LAT_OUT, obstacle=True))])
RUNS['X9n'] = S_(BASE, with_bin=False, kg=0.0, title='X9n empty robot NOSE first: stop and hold on the 12 % pitch', start=('snap', 'P2a_pf', 126.0),
                 steps=[('pivot', 180.0), ('drive', dict(to=146.0, ref='tug', dirn=1, knots=LAT_OUT)), ('hold', 5.0), ('drive', dict(to=156.0, ref='tug', dirn=1, knots=LAT_OUT))])
RUNS['X9t'] = S_(BASE, with_bin=False, kg=0.0, title='X9t empty robot TAIL first: stop and hold on the 12 % pitch', start=('snap', 'P2a_pf', 126.0),
                 steps=[('drive', dict(to=146.0, ref='tug', dirn=1, rev=True, knots=LAT_OUT)), ('hold', 5.0), ('drive', dict(to=156.0, ref='tug', dirn=1, rev=True, knots=LAT_OUT)), ('pivot', 180.0)])
RUNS['P6a_person_estop'] = S_(BASE, obstacles=[PERSON], title='P6a person steps in on the 12 % wet descent: e-stop', start=('snap', 'P1', 128.0),
                              steps=[('drive', dict(to=152.0, ref='tug', dirn=1, knots=LAT_OUT, obstacle=True))])
RUNS['P6b_dog_crossing'] = S_(BASE, obstacles=[DOG], title='P6b dog runs across: stop, wait, resume', start=('snap', 'P1', 222.0),
                              steps=[('drive', dict(to=246.0, ref='tug', dirn=1, knots=LAT_OUT, obstacle=True))])

# ------------------------------------------------------------------------------------------------ helpers
def qyaw(yaw, pitch=0.0):
    qz = np.array([math.cos(yaw / 2), 0, 0, math.sin(yaw / 2)]); qy = np.array([math.cos(pitch / 2), 0, math.sin(pitch / 2), 0]); q = np.zeros(4)
    mujoco.mju_mulQuat(q, qz, qy); return q
def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi
def hull_pts_local(S):
    """bin plan outline points in the bin body frame (both hull meshes)"""
    pts = []
    for n in ('binhull', 'binhull_lo'):
        g = mujoco.mj_name2id(S.m, mujoco.mjtObj.mjOBJ_GEOM, n)
        if g < 0: continue
        did = S.m.geom_dataid[g]; a = S.m.mesh_vertadr[did]; nv = S.m.mesh_vertnum[did]
        V = S.m.mesh_vert[a:a + nv].astype(float)
        Rg = np.zeros(9); mujoco.mju_quat2Mat(Rg, S.m.geom_quat[g]); pts.append(V @ Rg.reshape(3, 3).T + S.m.geom_pos[g])
    return np.vstack(pts) if pts else np.zeros((0, 3))

class Lane:
    """per-run world bookkeeping: hedge pool, leaf friction, obstacles, metrics, energy, recording"""
    def __init__(L, S, R, cfg):
        L.S, L.R, L.cfg = S, R, cfg; m = S.m
        L.pool = LW.HedgePool(m)
        L.gground = [g for g in range(m.ngeom) if m.geom_bodyid[g] == 0 and (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or '').startswith(('ground', 't_'))]
        L.mu_scale = cfg['pert'].get('mu', 1.0); L.leaf_state = None
        L.bid = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n) for n in BODIES}
        L.binbodies = {L.bid[n] for n in ('bin', 'bwL', 'bwR', 'lid') if L.bid[n] >= 0}
        L.with_bin = S.with_bin; L.hull = hull_pts_local(S) if S.with_bin else None
        L.corners = np.array(B.CORNERS); L.wr = S.p['wheel_r']
        L.obs = [dict(o, mid=m.body_mocapid[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, o['name'])], t0=None) for o in cfg['obstacles']]
        L.carry = False; L.M = L.new_metrics(); L.Mseg = L.new_metrics(); L.E = 0.0; L.rec = []; L.recph = []; L.tick = 0; L.s = 0.0; L.lat = 0.0; L.inst = {}
        L.binkg = float(S.bin_mass) if S.with_bin else 0.0; L.dirn = 1
        L.dax = (S.jv('axleL'), S.jv('axleR')); L.dlift = S.jv('lift')
        R.mon = L.mon
    def new_metrics(L):
        return dict(clear_min=9.0, clear_at=None, seated_all=True, bin_ground_N=0.0, roll_max=0.0, pitch_max=0.0, hedge_min=9.0, hedge_at=None,
                    tip_min=99.0, tip_at=None, liftF_max=0.0, liftF_at=None, gap_min=9.0, v_max=0.0, n_lost=0)
    def tug_xy_yaw(L):
        d = L.S.d; b = L.bid['tug']; Rm = d.xmat[b].reshape(3, 3); return d.xpos[b][:2].copy(), math.atan2(Rm[1, 0], Rm[0, 0])
    def set_leaf(L, leaf):
        if leaf == L.leaf_state: return
        L.leaf_state = leaf; mu = (LW.MU_LEAF if leaf else LW.MU_GROUND) * L.mu_scale
        for g in L.gground: L.S.m.geom_friction[g][0] = mu
    def obstacles(L):
        for o in L.obs:
            if o['t0'] is None:
                bumper_s = L.s + (1.09 + float(os.environ.get('X_NOSE_DX', '0'))) * L.dirn
                if L.dirn * (o['s'] - bumper_s) <= o['trig']: o['t0'] = L.R.t; L.R.ev('%s starts moving into the lane (bumper %.2f m from its line)' % (o['kind'], o['s'] - bumper_s))
            if o['t0'] is None: lat = o['lat0']
            else:
                dl = o['lat1'] - o['lat0']; tt = L.R.t - o['t0']; lat = o['lat0'] + math.copysign(min(abs(dl), o['v'] * tt), dl)
                t1 = abs(dl) / o['v']
                if 'lat2' in o and tt > t1 + o['wait']:     # person: stands in the lane for 'wait' s, then walks on to the far verge
                    d2 = o['lat2'] - o['lat1']; lat = o['lat1'] + math.copysign(min(abs(d2), o['v'] * (tt - t1 - o['wait'])), d2)
                    if tt > t1 + o['wait'] + abs(d2) / o['v'] + 0.3: lat = 9.0
                if o['kind'] == 'dog' and tt > t1 + 0.5: lat = 9.0     # gone through the far hedge gap
            p = LW.point(o['s'], min(lat, 2.8) if lat < 9 else 6.0); z = float(LW.zprof(o['s']))
            L.S.d.mocap_pos[o['mid']] = (p[0], p[1], z if lat < 9 else -400); o['lat'] = lat
    def footprint(L):
        d = L.S.d; b = L.bid['tug']; Rm = d.xmat[b].reshape(3, 3); p = d.xpos[b]
        pts = [L.corners @ Rm[:2, :2].T + p[:2]]
        if L.with_bin and L.hull is not None:
            bb = L.bid['bin']; Rb = d.xmat[bb].reshape(3, 3); pts.append((L.hull @ Rb.T + d.xpos[bb])[:, :2])
        return np.vstack(pts)
    def hedge_clear(L):
        F = L.footprint(); s, lat = LW.project(F); best = (9.0, None)
        for si, li in zip(s, lat):
            side = 1 if li > 0 else -1; f = LW.hedge_face(si, side)
            if f is None: continue
            c = f - abs(li)
            if c < best[0]: best = (c, si)
        return best
    def tip_margin(L):
        d = L.S.d; S = L.S
        sup = []
        for w, r in (('wheelL', B.GEO['rw']), ('cwheelL', B.GEO['cr']), ('cwheelR', B.GEO['cr']), ('wheelR', B.GEO['rw'])):
            sup.append(d.xpos[L.bid[w]] - np.array([0, 0, r]))
        sup = np.array(sup); mt = S.m.body_subtreemass[L.bid['tug']]; c = d.subtree_com[L.bid['tug']] * mt; M = mt
        if L.carry and L.with_bin:
            mb = S.m.body_subtreemass[L.bid['bin']]; c = c + d.subtree_com[L.bid['bin']] * mb; M += mb
        c = c / M; h = c[2] - sup[:, 2].mean(); P2 = sup[:, :2]
        ctr = P2.mean(0); dmin = 9.0
        for k in range(4):
            a, b = P2[k], P2[(k + 1) % 4]; e = b - a; n = np.array([-e[1], e[0]]); n /= np.linalg.norm(n)
            if (ctr - a) @ n < 0: n = -n
            dmin = min(dmin, (c[:2] - a) @ n)
        return math.degrees(math.atan2(dmin, h))
    def bin_ground(L):
        d = L.S.d; m = L.S.m; f = np.zeros(6); tot = 0.0
        for i in range(d.ncon):
            c = d.contact[i]; b1 = m.geom_bodyid[c.geom1]; b2 = m.geom_bodyid[c.geom2]
            if (b1 == 0 and b2 in L.binbodies) or (b2 == 0 and b1 in L.binbodies):
                mujoco.mj_contactForce(m, d, i, f); tot += f[0]
        return tot
    def wheel_clear(L):
        d = L.S.d; zc = [d.xpos[L.bid[w]] for w in ('bwL', 'bwR')]
        zs = LW.surface_z(np.array([p[0] for p in zc]), np.array([p[1] for p in zc]), L.cfg['variant'])
        return float(min(zc[0][2] - L.wr - zs[0], zc[1][2] - L.wr - zs[1]))
    def mon(L):
        S, R, d = L.S, L.R, L.S.d; L.tick += 1
        xy, yaw = L.tug_xy_yaw(); s, lat = LW.project(xy[None]); L.s, L.lat = float(s[0]), float(lat[0])
        L.set_leaf(LW.leaf_at(L.s)); L.pool.update(L.s, back=8 if getattr(L, 'dirn', 1) > 0 else 17)
        if L.obs: L.obstacles()
        dtk = 20 * R.dt
        pw = max(0.0, float(d.actuator_force[0]) * float(d.qvel[L.dax[0]])) + max(0.0, float(d.actuator_force[1]) * float(d.qvel[L.dax[1]]))
        pl = max(0.0, S.lift_force() * float(d.qvel[L.dlift]))
        L.E += (pw / ETA_W + pl / ETA_L + HOTEL_W + (LIGHTS_W if L.cfg['night'] else 0.0)) * dtk / 3600.0
        if L.tick % 2: return
        r, p, _ = S.rpy(); v = S.fwd_speed(); F = abs(S.lift_force()); hc, hs = L.hedge_clear(); tm = L.tip_margin()
        clr = L.wheel_clear() if L.with_bin else float('nan')
        if L.carry: st = S.seated(); bg = L.bin_ground()
        gap = 9.0
        for o in L.obs:
            if o.get('lat', 9) < 9:
                po = LW.point(o['s'], o['lat']); gap = min(gap, float(np.min(np.linalg.norm(L.footprint() - po, axis=1))) - o['r'])
        for M in (L.M, L.Mseg):
            M['roll_max'] = max(M['roll_max'], abs(r)); M['pitch_max'] = max(M['pitch_max'], abs(p)); M['v_max'] = max(M['v_max'], abs(v))
            if F > M['liftF_max']: M['liftF_max'] = F; M['liftF_at'] = round(L.s, 1)
            if hc < M['hedge_min']: M['hedge_min'] = hc; M['hedge_at'] = round(hs, 1)
            if tm < M['tip_min']: M['tip_min'] = tm; M['tip_at'] = round(L.s, 1)
            if L.carry:
                if clr < M['clear_min']: M['clear_min'] = clr; M['clear_at'] = round(L.s, 1)
                M['seated_all'] = M['seated_all'] and st
                if not (st and clr > 0.030): M['n_lost'] += 1
                M['bin_ground_N'] = max(M['bin_ground_N'], bg)
            M['gap_min'] = min(M['gap_min'], gap)
        L.inst = dict(clear=clr, hedge=hc, tip=tm, gap=gap)
        if L.tick % 4 == 0:   # 0.04 s -> 25 fps recording
            q = np.full((len(BODIES), 7), np.nan, np.float32)
            for k, n in enumerate(BODIES):
                b = L.bid[n]
                if b >= 0: q[k, :3] = d.xpos[b]; q[k, 3:] = d.xquat[b]
            ob = np.full((2, 3), np.nan, np.float32)
            for k, o in enumerate(L.obs[:2]):
                if o.get('lat', 9) < 9: ob[k] = (*LW.point(o['s'], o['lat']), LW.zprof(o['s']))
            hud = np.array([L.s, L.lat, 100 * LW.grade(L.s), v, F, clr, hc, tm, L.E, float(L.leaf_state or 0), r, p, L.binkg, float(L.carry), gap], np.float32)
            L.rec.append((np.float32(R.t), q, hud, ob)); L.recph.append(R.phase)

# ------------------------------------------------------------------------------------------------ build / state
def build(cfg):
    B.GEO['act_N'] = float(os.environ.get('X_ACT_N', cfg['act_N'])); os.environ['H2_BINCG_DZ'] = str(cfg['pert'].get('cg_dz', 0.0))
    post = LW.install(B, cfg['variant'], cfg['obstacles'])
    p = B.bin_params(cfg['binkey']); Bn = BINS[cfg['binkey']]
    kg = cfg['kg'] if cfg['kg'] is not None else Bn['empty'] + Bn['fill_full']
    p['fill'] = max(0.0, kg - Bn['empty'])
    S = B.SimB(cfg['binkey'], p, tug_pose=(0, 0, 0), with_bin=cfg['with_bin'], mu=LW.MU_GROUND); post(S.m)
    PM = cfg['pert'].get('mass', 1.0)
    if PM != 1.0:
        S.m.body_mass[:] *= PM; S.m.body_inertia[:] *= PM; mujoco.mj_setConst(S.m, S.d); S.lift_mass *= PM
    if cfg['pert'].get('mu', 1.0) != 1.0: S.m.geom_friction[:, 0] *= cfg['pert']['mu']
    mujoco.mj_forward(S.m, S.d)
    R = B.RunnerB(S); L = Lane(S, R, cfg)
    S.wheel_clear = L.wheel_clear                       # terrain-aware clearance (captured() uses it)
    if S.with_bin: L.binkg = float(S.m.body_subtreemass[L.bid['bin']])
    return S, R, L
def place(S, body, x, y, yaw, dz):
    j = S.jq(body + 'free'); s, _ = LW.project(np.array([[x, y]])); h = LW.heading(float(s[0]))
    gx = LW.grade(float(s[0])) * math.cos(yaw - h); z = float(LW.surface_z(x, y)[0]) + dz
    S.d.qpos[j:j + 3] = (x, y, z); S.d.qpos[j + 3:j + 7] = qyaw(yaw, -math.atan(gx)); S.d.qvel[S.jv(body + 'free'):S.jv(body + 'free') + 6] = 0
def get_state(S): d = S.d; return dict(qpos=d.qpos.copy(), qvel=d.qvel.copy(), act=d.act.copy(), ctrl=d.ctrl.copy(), qacc_warmstart=d.qacc_warmstart.copy(), time=d.time)
def set_state(S, st):
    d = S.d
    for k in ('qpos', 'qvel', 'act', 'ctrl', 'qacc_warmstart'): getattr(d, k)[:] = st[k]
    d.time = st['time']; mujoco.mj_forward(S.m, d)
def named_state(S):
    out = {}
    for j in range(S.m.njnt):
        n = mujoco.mj_id2name(S.m, mujoco.mjtObj.mjOBJ_JOINT, j); a = S.m.jnt_qposadr[j]; v = S.m.jnt_dofadr[j]
        nq = {0: 7, 1: 4, 2: 1, 3: 1}[S.m.jnt_type[j]]; nv = {0: 6, 1: 3, 2: 1, 3: 1}[S.m.jnt_type[j]]
        out[n] = (S.d.qpos[a:a + nq].copy(), S.d.qvel[v:v + nv].copy())
    return out
def set_named(S, ns):
    for n, (qp, qv) in ns.items():
        j = mujoco.mj_name2id(S.m, mujoco.mjtObj.mjOBJ_JOINT, n)
        if j < 0: continue
        a = S.m.jnt_qposadr[j]; v = S.m.jnt_dofadr[j]; S.d.qpos[a:a + len(qp)] = qp; S.d.qvel[v:v + len(qv)] = qv
    mujoco.mj_forward(S.m, S.d)
SKIP_R = ('s', 'ctrl_fn', 'mon')
def r_attrs(R): return {k: v for k, v in R.__dict__.items() if k not in SKIP_R}
def s_attrs(S): return dict(keeper_cmd=S.keeper_cmd, pad_cmd=S.pad_cmd, pad_tgt=S.pad_tgt)
def restore_attrs(S, R, ra, sa):
    for k, v in ra.items(): setattr(R, k, v)
    for k, v in sa.items(): setattr(S, k, v)
    R._bk = None; R.ctrl_fn = None

# ------------------------------------------------------------------------------------------------ manoeuvres
def lat_target(knots, s):
    ks = [k[0] for k in knots]; ls = [k[1] for k in knots]; lt = float(np.interp(s, ks, ls))
    fl, fr = LW.hedge_face(s, 1), LW.hedge_face(s, -1)       # 0.4 m hedge guard on the body edge
    hi = (fl - LW.BODY_HALF - 0.4) if fl is not None else 9.0; lo = -((fr - LW.BODY_HALF - 0.4) if fr is not None else 9.0)
    if hi < lo: return 0.5 * (hi + lo)
    return float(np.clip(lt, lo, hi))
class Drive:
    def __init__(D, L, a):
        D.L, D.a = L, a; D.dirn = a['dirn']; L.dirn = D.dirn; D.Ld = 1.5; D.estop = False; D.stopped_for = None; D.clear_since = L.R.t - 2.5; D._v = a.get('vmax', VDEF)
    def ref_s(D):
        L = D.L
        if D.a['ref'] == 'bin' and L.with_bin:
            p = L.S.d.xpos[L.bid['bin']][:2]; return float(LW.project(p[None])[0][0])
        return L.s
    def remaining(D): return D.dirn * (D.a['to'] - D.ref_s())
    def ctl(D):
        L = D.L; S, R = L.S, L.R; xy, yaw = L.tug_xy_yaw(); s, lat = LW.project(xy[None]); s = float(s[0])
        rev = bool(D.a.get('rev'))   # [revision 5] tail first: the robot faces up the lane and backs down it (drive wheels leading)
        hd = yaw + (math.pi if rev else 0.0)
        Ld_ = D.Ld + LDK * max(0.0, abs(S.fwd_speed()) - 0.45); sl = s + D.dirn * Ld_; tgt = LW.point(sl, lat_target(D.a['knots'], sl))
        al = wrap(math.atan2(tgt[1] - xy[1], tgt[0] - xy[0]) - hd)
        v = min(D.a.get('vmax', VDEF), float(os.environ.get('X_VMAX', '9')))
        for thr_, vb_, ve_ in VSLOPE:   # [X] person-stop rule: slower on a downhill slope steeper than thr_ (with a bin / empty)
            if max(-LW.grade(s + D.dirn * 0.5 * k_) * D.dirn for k_ in range(int(VLOOK / 0.5) + 1)) >= thr_: v = min(v, vb_ if (L.with_bin and L.binkg >= 40.0) else ve_)   # an empty bin does not load the braked wheels: empty-robot speed
        if rev: v = min(v, VREV)
        if s < 25.0 or s > LW.LEN - 15.0: v = min(v, 0.3)
        if VDEF > 0.5 and (s < 30.0 or s > LW.LEN - 20.0): v = min(v, 0.4)   # [revision 6] fast cruise only in the lane proper, as the mission software
        if abs(al) > math.radians(25): v = min(v, 0.25)
        rem = D.remaining(); v = min(v, math.sqrt(2 * 0.25 * max(rem - 0.02, 0.0)) + 0.06)
        if D.a.get('obstacle'): v = D.obstacle_rule(v)
        if D.estop: R.hold(); return
        if rem <= 0.02 or v <= 0.0: R.w = 0.0; R.wd = 0.0; R.brake = False; return
        om = 2 * v * math.sin(al) / Ld_
        R.w = (-v if rev else v) / B.RW; R.wd = max(-0.3, min(0.3, om * 2 * B.GEO['track'])) / B.RW; R.brake = False
    def obstacle_rule(D, v):
        """LD06 front sector: obstacle in the swept corridor (|lat - robot lat| < 0.49 + 0.30): gap <= 1.5 m -> E-STOP (spring brakes);
        gap <= 3.0 m -> controlled stop; resume when the corridor has been clear for 2 s. Sensor period 0.1 s."""
        L = D.L; R = L.R
        if (R.i // 20) % 10: return getattr(D, '_v', v)
        bumper = L.s + (0.40 if D.a.get('rev') else 1.09 + float(os.environ.get('X_NOSE_DX', '0'))) * D.dirn; worst = None   # leading end: the tail when backing down
        for o in L.obs:
            if o.get('lat', 9) > 8: continue
            g = D.dirn * (o['s'] - bumper) - o['r']
            if abs(o['lat'] - L.lat) < LW.BODY_HALF + 0.30 + o['r'] and g > -0.5: worst = g if worst is None else min(worst, g)
        if worst is not None and worst <= 1.5 and not D.estop and abs(L.S.fwd_speed()) > 0.05:
            D.estop = True; L.estop = dict(t=R.t, x=L.S.d.xpos[L.bid['tug']][:2].copy(), gap=worst, v=L.S.fwd_speed()); R.ev('E-STOP: %s %.2f m ahead in the corridor' % ('obstacle', worst))
        if worst is not None and worst <= 3.0:
            if getattr(D, '_v', v) > 0 and not D.estop: R.ev('controlled stop: obstacle %.2f m ahead in the corridor' % worst); L.n_stops = getattr(L, 'n_stops', 0) + 1
            D.clear_since = None; D._v = 0.0
        else:
            if D.clear_since is None: D.clear_since = R.t
            vn = v if R.t - D.clear_since >= 2.0 else 0.0
            if vn > 0 and getattr(D, '_v', v) == 0.0: R.ev('corridor clear 2 s: resume')
            D._v = vn
            if D._v > 0 and D.estop and R.t - L.estop['t'] > 3.5: D.estop = False
        return D._v
def softstop(R): B.soft_stop(R, 4.0)
def forward(L, dist, v=0.15):
    S, R = L.S, L.R; x0 = S.d.xpos[L.bid['tug']].copy(); psi = S.rpy()[2]; R.phase = 'Pull forward %.2f m (comb clear of the bin)' % dist
    R.ctrl_fn = B.heading_hold(R, v, psi); R.until(lambda: np.linalg.norm(S.d.xpos[L.bid['tug']][:2] - x0[:2]) >= dist, 10.0); R.ctrl_fn = None; softstop(R); R.hold(); R.run_for(0.3)
def pivot(L, deg):
    S, R = L.S, L.R; psi0 = S.rpy()[2]; ref = psi0 + deg; R.phase = 'Pivot %.0f deg on the spot' % deg; L.pivot_x0 = S.d.xpos[L.bid['tug']][:2].copy()
    def ctl():
        e = math.radians((ref - S.rpy()[2] + 180) % 360 - 180); R.w = 0.0; R.wd = max(-0.10, min(0.10, 0.6 * e)) * 2 / B.RW; R.brake = False
    R.ctrl_fn = ctl; ok = R.until(lambda: abs((ref - S.rpy()[2] + 180) % 360 - 180) < 1.0, 40.0); R.ctrl_fn = None; R.hold(); R.run_for(0.5)
    R.ev('pivot %+.0f deg %s, axle moved %.3f m' % (deg, 'done' if ok else 'TIMEOUT', float(np.linalg.norm(S.d.xpos[L.bid['tug']][:2] - L.pivot_x0))))
    return ok
def hold(L, T):
    S, R = L.S, L.R; s_cmd = L.s; softstop(R); R.hold(); R.phase = 'Stop and hold on the spring brakes (%.0f s)' % T
    R.run_for(0.2); x0 = S.d.xpos[L.bid['tug']].copy(); out = {'overrun_m': round(abs(L.s - s_cmd), 2)}   # [revision 6, reviewers' caveat] distance from the stop command to where the robot came to rest
    R.run_for(3.0); out['creep3_m'] = float(np.linalg.norm(S.d.xpos[L.bid['tug']][:2] - x0[:2]))
    if T > 3: R.run_for(T - 3.0)
    out['creepT_m'] = float(np.linalg.norm(S.d.xpos[L.bid['tug']][:2] - x0[:2])); out['T'] = T; out['s'] = round(L.s, 2); out['grade_pct'] = round(100 * LW.grade(L.s), 1)
    out['leaf'] = bool(LW.leaf_at(L.s)); R.ev('hold at s %.1f (%.1f %%): creep %.4f m in 3 s, %.4f m in %.0f s' % (L.s, out['grade_pct'], out['creep3_m'], out['creepT_m'], T))
    return out

# ------------------------------------------------------------------------------------------------ run
def rundir(rid): d = os.path.join(RUNS_DIR, rid); os.makedirs(os.path.join(d, 'snaps'), exist_ok=True); return d
def save_rec(L, d, ck):
    if not L.rec: return
    n = ck['nrec']; t = np.array([r[0] for r in L.rec]); q = np.stack([r[1] for r in L.rec]); h = np.stack([r[2] for r in L.rec]); ob = np.stack([r[3] for r in L.rec])
    np.savez_compressed(os.path.join(d, 'rec_%03d.npz' % n), t=t, q=q, hud=h, ob=ob, ph=np.array(L.recph)); ck['nrec'] = n + 1; L.rec = []; L.recph = []
def checkpoint(S, R, L, ck, d):
    save_rec(L, d, ck)
    ck.update(state=get_state(S), R=r_attrs(R), S=s_attrs(S), M=L.M, Mseg_cur=L.Mseg, E=L.E, carry=L.carry, tick=L.tick, estop=getattr(L, 'estop', None),
              obs=[{k: v for k, v in o.items()} for o in L.obs])
    pickle.dump(ck, open(os.path.join(d, 'ckpt.pkl.tmp'), 'wb')); os.replace(os.path.join(d, 'ckpt.pkl.tmp'), os.path.join(d, 'ckpt.pkl'))
def init_run(rid, cfg, S, R, L):
    st = cfg['start']; ck = dict(step=0, nrec=0, results={}, t_wall=0.0, snaps_done=[])
    if st == 'home':
        p = S.p; bx = LW.point(LW.HOME['s'], LW.HOME['lat']); byaw = LW.heading(LW.HOME['s'])
        place(S, 'bin', bx[0], bx[1], byaw, p['wheel_r'] + 0.003)
        sp = B.start_pose(p); c, s_ = math.cos(byaw), math.sin(byaw)
        place(S, 'tug', bx[0] + c * sp[0] - s_ * sp[1], bx[1] + s_ * sp[0] + c * sp[1], byaw + sp[2], 0.004); mujoco.mj_forward(S.m, S.d)
    elif st[0] == 'from':
        src = pickle.load(open(os.path.join(RUNS_DIR, st[1], 'ckpt.pkl'), 'rb')); set_named(S, src['named'])
        S.d.qvel[:] = 0; mujoco.mj_forward(S.m, S.d); ck['src'] = st[1]
    elif st[0] == 'padA_bin':
        src = pickle.load(open(os.path.join(RUNS_DIR, st[1], 'ckpt.pkl'), 'rb')); qb = src['named']['binfree'][0]
        byaw = math.atan2(2 * (qb[3] * qb[6] + qb[4] * qb[5]), 1 - 2 * (qb[5] ** 2 + qb[6] ** 2)); p = S.p
        place(S, 'bin', qb[0], qb[1], byaw, p['wheel_r'] + 0.003); sp = B.start_pose(p); c, s_ = math.cos(byaw), math.sin(byaw)
        place(S, 'tug', qb[0] + c * sp[0] - s_ * sp[1], qb[1] + s_ * sp[0] + c * sp[1], byaw + sp[2], 0.004); mujoco.mj_forward(S.m, S.d)
        R.ev('emptied bin left by P1 at pad A; tug placed at the docking start pose 1.2 m out (outbound empty leg not simulated: trim 1)')
    elif st[0] == 'snap':
        sn = sorted(glob.glob(os.path.join(RUNS_DIR, st[1], 'snaps', 's*.pkl')), key=lambda f: abs(float(os.path.basename(f)[1:-4]) - st[2]))[0]
        sp = pickle.load(open(sn, 'rb')); set_state(S, sp['state']); restore_attrs(S, R, sp['R'], sp['S']); L.carry = sp['carry']
        R.events = []; R.peak = {}; ck['snap'] = os.path.basename(sn); ck['t_start'] = R.t; R.ev('start from %s snapshot %s (carried state)' % (st[1], ck['snap']))
    return ck
def verdict(rid, cfg, ck, L, R):
    M = L.M; res = ck['results']; fails = []
    g = res.get('grab')
    if g is not None and g.get('result') != 'success': fails.append('grab %s' % g.get('result'))
    carried = any(k.startswith('drive') for k in res) and (cfg['with_bin'])
    if carried and M['clear_min'] < 9:
        if not M['seated_all']: fails.append('comb lip unseated')
        if M['bin_ground_N'] > 1.0: fails.append('bin touched the ground (%.0f N)' % M['bin_ground_N'])
    if M['roll_max'] >= 15 or M['pitch_max'] >= 15: fails.append('tug roll/pitch >= 15 deg')
    if M['hedge_min'] < 0: fails.append('hedge contact (clearance %.3f m at s %s)' % (M['hedge_min'], M['hedge_at']))
    if M['tip_min'] < 0: fails.append('static tip margin < 0')
    for k, v in res.items():
        if k.startswith('drive') and not v.get('reached'): fails.append('%s stalled at s %.1f (%s)' % (k, v.get('s_end', -1), v.get('why')))
        if k.startswith('drive') and v.get('captured_end') is False: fails.append('%s: bin not captured at the end (wheels < 30 mm or unseated)' % k)
        if k.startswith('hold') and v.get('creep3_m', 0) >= 0.05: fails.append('%s creep %.3f m >= 0.05 m in 3 s' % (k, v['creep3_m']))
        if k.startswith('hold') and v.get('overrun_m', 0) > 1.0: fails.append('%s: the robot ran %.1f m past the stop command before it held' % (k, v['overrun_m']))
        if k.startswith('pivot') and not v.get('ok'): fails.append('%s timeout' % k)
    sd = res.get('setdown')
    if sd is not None:
        if not (sd.get('released') and sd.get('standing')): fails.append('set-down %s' % ('HOLD' if sd.get('hold') else 'fail'))
    es = getattr(L, 'estop', None)
    if cfg['obstacles']:
        if M['gap_min'] <= 0: fails.append('contact with the %s' % cfg['obstacles'][0]['kind'])
        e = res.get('estop')
        if e:
            if e['stop_m'] > 0.5: fails.append('e-stop distance %.2f m > 0.5' % e['stop_m'])
            if e['slide_m'] >= 0.05: fails.append('slide after stop %.3f m' % e['slide_m'])
    return fails
def run(rid, budget):
    cfg = dict(RUNS[rid])
    if os.environ.get('X_MU_SCALE'): cfg['pert'] = dict(cfg['pert'], mu=float(os.environ['X_MU_SCALE']))   # [revision 5] grip scale from the environment
    cfg['variant'] = json.loads(os.environ['X_VARIANT']) if os.environ.get('X_VARIANT') else cfg['variant']; d = rundir(rid); ckf = os.path.join(d, 'ckpt.pkl')
    S, R, L = build(cfg); t_b = time.time() - T_WALL0
    if os.path.exists(ckf):
        ck = pickle.load(open(ckf, 'rb'))
        if ck.get('done'): print('DONE (already)', rid); return
        set_state(S, ck['state']); restore_attrs(S, R, ck['R'], ck['S']); L.M = ck['M']; L.Mseg = ck.get('Mseg_cur', L.new_metrics()); L.E = ck['E']; L.carry = ck['carry']; L.tick = ck['tick']
        if ck.get('estop'): L.estop = ck['estop']
        for o, so in zip(L.obs, ck.get('obs', [])): o.update({k: v for k, v in so.items() if k != 'mid'})
    else:
        ck = init_run(rid, cfg, S, R, L)
    print('build %.1f s, step %d/%d, t %.1f' % (t_b, ck['step'], len(cfg['steps']), R.t), flush=True)
    deadline = T_WALL0 + budget
    while ck['step'] < len(cfg['steps']):
        st = cfg['steps'][ck['step']]; kind = st[0]; key = '%s%d' % (kind, ck['step'])
        if ck.get('seg_step') != ck['step']: L.Mseg = L.new_metrics(); ck['seg_step'] = ck['step']
        step0 = ck['step']
        left = deadline - time.time()
        if kind in ('grab', 'setdown', 'pivot') and left < 30: break
        if kind == 'grab':
            g = B.grab(R, seed=7); L.carry = g['result'] == 'success'; ck['results']['grab'] = {k: v for k, v in g.items() if k != 'events'}
            R.ev('grab result %s' % g['result']); ck['step'] += 1
            if not L.carry: ck['abort'] = 'grab failed'; break
        elif kind == 'setdown':
            L.carry = False; o = B.set_down(R)
            bt = L.S.bin_tilt_abs(); jb = S.jv('binfree'); bv = float(np.linalg.norm(S.d.qvel[jb:jb + 3]))
            o.update(tilt_end=round(bt, 2), bin_speed=round(bv, 4), standing=bool(abs(bt - getattr(R, 'tilt0', 0)) < 8 and bv < 0.05 and bt < 30))
            bp = S.d.xpos[L.bid['bin']][:2]; sb, lb = LW.project(bp[None]); o['bin_s'] = round(float(sb[0]), 2); o['bin_lat'] = round(float(lb[0]), 3)
            ck['results']['setdown'] = o; R.ev('set-down: released %s standing %s tilt %.1f' % (o.get('released'), o['standing'], bt)); ck['step'] += 1
        elif kind == 'forward': forward(L, st[1]); ck['step'] += 1
        elif kind == 'softstop': softstop(R); R.hold(); R.run_for(0.3); ck['step'] += 1
        elif kind == 'pivot':
            ok = pivot(L, st[1]); ck['results'][key] = dict(ok=ok); ck['step'] += 1
        elif kind == 'hold':
            ck['results'][key] = hold(L, st[1]); ck['step'] += 1
        elif kind == 'drive':
            a = st[1]; D = Drive(L, a); R.ctrl_fn = D.ctl; R.phase = 'Transit %s, pure pursuit %.1f m/s cap' % ('house -> road' if a['dirn'] > 0 else 'road -> house', a.get('vmax', 0.5))
            if 'feature' in a: R.phase = 'Crossing the %s (%s)' % (a['feature'], cfg['title'].split(',')[0])
            prog = ck.get('prog') or (R.t, D.ref_s()); why = None; fin = False
            ck.setdefault('drive_t0', R.t)   # 01:40 fix: the 2400 s drive timeout was dead code (drive_t0 never stored)
            while True:
                for _ in range(400): R.step()
                if D.a.get('obstacle') and getattr(L, 'estop', None) and 'estop' not in ck['results'] and abs(S.fwd_speed()) < 0.005:
                    e = L.estop; x1 = S.d.xpos[L.bid['tug']][:2].copy(); R.run_for(3.0); x2 = S.d.xpos[L.bid['tug']][:2].copy()
                    ck['results']['estop'] = dict(stop_m=round(float(np.linalg.norm(x1 - e['x'])), 3), slide_m=round(float(np.linalg.norm(x2 - x1)), 4), v0=round(e['v'], 3),
                                                  gap_at_trigger=round(e['gap'], 2), s=round(L.s, 1), grade_pct=round(100 * LW.grade(L.s), 1), leaf=bool(LW.leaf_at(L.s)))
                    R.ev('e-stop: stopped in %.3f m, slide %.4f m in 3 s' % (ck['results']['estop']['stop_m'], ck['results']['estop']['slide_m']))
                if a.get('snaps') and (L.carry or not L.with_bin):
                    sk = 2 * int(L.s // 2)
                    if sk not in ck['snaps_done'] and abs(L.s - sk) < 0.3:
                        pickle.dump(dict(state=get_state(S), R=r_attrs(R), S=s_attrs(S), carry=L.carry), open(os.path.join(d, 'snaps', 's%05.1f.pkl' % sk), 'wb')); ck['snaps_done'].append(sk)
                rem = D.remaining()
                if rem <= 0.03 and abs(S.fwd_speed()) < 0.03: fin = True; break
                if R.t - prog[0] > 12.0:
                    if abs(D.ref_s() - prog[1]) < 0.05 and not (D.a.get('obstacle') and (D.estop or D.clear_since is None or R.t - D.clear_since < 2.0)): why = 'no progress 12 s (stall)'; break
                    prog = (R.t, D.ref_s())
                if R.t - ck.get('drive_t0', R.t) > 2400: why = 'timeout'; break
                if time.time() > deadline: break
            ck['prog'] = prog
            if fin or why:
                R.ctrl_fn = None; softstop(R); R.hold(); R.run_for(0.5)
                ck['results'][key] = dict(reached=bool(fin), why=why, s_end=round(L.s, 2), ref_end=round(D.ref_s(), 2), t=round(R.t, 1))
                if L.carry: ck['results'][key]['captured_end'] = bool(S.captured()); ck['results'][key]['clear_end_mm'] = round(1000 * L.wheel_clear(), 1)
                if a.get('feature'):
                    f = LW.FEAT[a['feature']]; fs = f['s']; far = fs + (f.get('w', 0.0) if a['feature'] == 'trench' else f.get('L', 0.0) if a['feature'] == 'pothole' else 0.0)
                    bw = [float(LW.project(S.d.xpos[L.bid[w]][:2][None])[0][0]) for w in ('bwL', 'bwR')]
                    ck['results'][key]['binwheels_past_far_edge'] = bool(min(bw) > far + 0.05 if a['dirn'] > 0 else max(bw) < fs - 0.05)
                ck['step'] += 1; ck.pop('prog', None); ck.pop('drive_t0', None); R.ev('%s: %s at s %.1f' % (key, 'reached' if fin else why, L.s))
            else:
                R.ctrl_fn = None; break
        if ck['step'] > step0: ck.setdefault('Mseg', {})[key] = {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in L.Mseg.items()}
        checkpoint(S, R, L, ck, d)
        if time.time() > deadline: break
    ck['t_wall'] = ck.get('t_wall', 0) + time.time() - T_WALL0
    done = ck['step'] >= len(cfg['steps']) or ck.get('abort')
    if done:
        fails = verdict(rid, cfg, ck, L, R); M = L.M
        if ck.get('abort'): fails.append(ck['abort'])
        ck['done'] = True; ck['named'] = named_state(S)
        res = dict(run=rid, title=cfg['title'], verdict='PASS' if not fails else 'FAIL', fails=fails, sim_time_s=round(R.t - ck.get('t_start', 0.0), 1), t_start=ck.get('t_start', 0.0), energy_Wh=round(L.E, 2),
                   wall_s=round(ck['t_wall']), metrics={k: (round(v, 4) if isinstance(v, float) else v) for k, v in M.items()}, results=ck['results'], seg_metrics=ck.get('Mseg', {}),
                   events=R.events[-40:], cfg={k: v for k, v in cfg.items() if k != 'steps'}, steps=[list(map(str, s_)) for s_ in cfg['steps']], peak=R.peak)
        json.dump(res, open(os.path.join(d, 'result.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
        print('DONE', rid, res['verdict'], fails, 'sim %.0f s' % R.t, 'E %.1f Wh' % L.E, json.dumps(res['metrics']), flush=True)
    checkpoint(S, R, L, ck, d)
    if not done: print('CHUNK', rid, 'step', ck['step'], 't %.1f' % R.t, 's %.1f' % L.s, 'E %.2f' % L.E, 'wall %.0f' % (time.time() - T_WALL0), flush=True)

if __name__ == '__main__':
    run(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 95.0)
