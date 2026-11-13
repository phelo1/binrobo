"""B2-F lane SITL scenarios (S9 set + ArduPilot-specific failsafe / fence cases). Lane coordinates as G6: s = m from the
house end, lat + = left of house->road. Pads A/M/F as G6 except pad A, set 0.25 m further off the hedge (lat 1.10, G6 1.35)
as the H2-vs-B2F gate recommended (B2-F rails came within 3 mm of the truth hedge at G6's pad A in the S9 Python model).
Handles face the road at the pads (G6 handles-out layout); at home they face down-lane. Dock at s 4 (nose-in, facing the house)."""
import math, os, numpy as np
import b2f_world as BW
from b2f_world import ROB, BIN_T, wrap

S = BW.site(); L = S.L
PADS = {'A': dict(s=L - 11.1, lat=1.10), 'M': dict(s=L - 14.6, lat=0.85), 'F': dict(s=L - 20.0, lat=0.85)}
HOME = {'black': dict(s=10.0, lat=-1.4), 'green': dict(s=10.0, lat=-3.0), 'brown': dict(s=10.0, lat=-4.6)}
DOCK = dict(s=4.0, lat=0.0)
SIZE = {'black': '240', 'green': '240', 'brown': '140'}
STAGE_DROP, STAGE_PICK = 4.0, 4.5
EXPECT = dict(tune='pass', s1a='pass', s1b='pass', s3a='pass', s3b='pass', s4a='pass', s4b='pass', s4c='alert', s5a='pass', s5b='pass',
              s6a='alert', s6b='alert', s7='alert', s8='alert', s9='alert', s10a='alert', s10b='alert', s11a='alert', s11b='alert',
              s12a='alert', s12b='alert')
TITLES = dict(tune='tuning segment s 200-290 loaded', s1a='One-bin night drop (240 L black -> pad A)', s1b='One-bin night pickup (pad A -> home)',
              s3a='Three-bin night drop (140 L -> A, 240 L -> M, 240 L -> F)', s3b='Three-bin night pickup (F, M, A -> home)',
              s4a='RTK float under the hedge (40 m, loaded)', s4b='RTK loss under the hedge (20 m, bridged by odometry + lidar)',
              s4c='RTK long loss under the hedge (70 m)', s5a='Lidar: person + dog crossing (loaded)', s5b='Car in the bell-mouth at the drop',
              s6a='Companion freeze, loaded transit (firmware failsafe)', s6b='Companion freeze while reversing onto the bin',
              s7='E-stop, loaded transit at 0.5 m/s', s8='Low battery at the energy guard', s9='Bin missing at pickup',
              s10a='Bin tipped at pickup', s10b='Bin blocked at pickup (garden-waste sack in the approach)', s11a='Wind no-go',
              s11b='Frost no-go', s12a='Geofence: pad drawn on the road verge (Pi refuses)', s12b='Geofence: Pi check bypassed, firmware fence HOLD at the road edge')


def lane_pose(s, lat, facing):
    x, y, h = S.pose(s, lat, 0.0); return x, y, (h if facing == 'down' else wrap(h + math.pi))

def docked_pose():
    dx, dy, dh = S.pose(DOCK['s'], DOCK['lat'], 0.0); ryaw = wrap(dh + math.pi)
    return dx - (ROB['x1'] + 0.02) * math.cos(ryaw), dy - (ROB['x1'] + 0.02) * math.sin(ryaw), ryaw

def mk_bin(where, key, size, mass, state='up', jit=None, rng=None):
    d = PADS[key] if where == 'pad' else HOME[key]; s0, lat = d['s'], d['lat']; dyaw = 0.0
    if jit and rng is not None: s0 += rng.uniform(-jit[0], jit[0]); lat += rng.uniform(-jit[0], jit[0]); dyaw = math.radians(rng.uniform(-jit[1], jit[1]))
    x, y, h = S.pose(s0, lat, 0.0)
    return dict(x=float(x), y=float(y), yaw=wrap(h + dyaw), size=size, mass=mass, state=state)

def nominal(where, key, size):
    d = PADS[key] if where == 'pad' else HOME[key]; x, y, h = S.pose(d['s'], d['lat'], 0.0)
    return dict(x=float(x), y=float(y), yaw=float(h), size=size)

def carried_world(w, name, size, mass):
    w.bins[name] = dict(x=w.x, y=w.y, yaw=wrap(w.yaw + math.pi), size=size, mass=mass, state='carried'); w.carry = name
    bx, by, byaw = w.carried_xy(); w.bins[name].update(x=bx, y=by, yaw=byaw); w.lift_q = 0.239; w.pad_on = True

def drop_trip(col, pad):
    sp = PADS[pad]['s']
    return [('preflight', 'drop %s->%s' % (col, pad)), ('pad_check', pad), ('undock',), ('grab', col, 'home'), ('pivot_safe', 'down'),
            ('lane', sp - STAGE_DROP, 0.0, 12.0), ('wait_clear', pad), ('pivot_safe', 'up'), ('setdown', 'pad', pad),
            ('lane', 8.0, 0.0), ('dock',), ('trip_end',)]

def pickup_trip(col, pad):
    sp = PADS[pad]['s']
    return [('preflight', 'pickup %s<-%s' % (col, pad)), ('undock',), ('pivot_safe', 'down'), ('lane', sp - STAGE_PICK, 0.0, 12.0),
            ('verify_bin', col, pad), ('pivot_safe', 'up'), ('grab', col, pad), ('lane', 13.0, HOME[col]['lat']),
            ('setdown', 'home', col), ('dock',), ('trip_end',)]


def build(name, seed):
    rng = np.random.default_rng(seed * 1000 + 17)
    sc = dict(name=name, title=TITLES[name], expect=EXPECT[name], pads=PADS, home=HOME, dock=DOCK, expect_bins={}, tmax=4000,
              clock_min=None, carry_size='240', soc0=0.90)
    full = lambda c: BIN_T[SIZE[c]]['full']; empty = lambda c: BIN_T[SIZE[c]]['empty']
    def world_at(x, y, yaw):
        w = BW.World(x, y, yaw, seed=seed, night=True); w.soc = sc['soc0']; return w
    if name in ('s1a', 's3a', 's8', 's11a', 's11b'):
        cols = ['black'] if name != 's3a' else ['brown', 'black', 'green']
        pads = {'black': 'A'} if name != 's3a' else {'brown': 'A', 'black': 'M', 'green': 'F'}
        w = world_at(*docked_pose())
        for c in (['black', 'green', 'brown'] if name == 's3a' else ['black']):
            w.bins[c] = mk_bin('home', c, SIZE[c], full(c)); sc['expect_bins'][c] = nominal('home', c, SIZE[c])
        plan = []
        for c in cols: plan += drop_trip(c, pads[c])
        sc['clock_min'] = -360.0; sc['tmax'] = 3600 * 4.5 if name == 's3a' else 5400
        if name == 's8': w.soc = sc['soc0'] = 0.17; sc['tmax'] = 200
        if name == 's11a': sc['weather'] = dict(gust=18.0, air_c=6.0); sc['tmax'] = 200
        if name == 's11b': sc['weather'] = dict(gust=4.0, air_c=-3.0, frost=True); w.air_c = -3.0; sc['tmax'] = 200
        if name == 's3a': w.air_c = 0.0
    elif name in ('s1b', 's3b'):
        cols = ['black'] if name == 's1b' else ['green', 'black', 'brown']
        pads = {'black': 'A'} if name == 's1b' else {'brown': 'A', 'black': 'M', 'green': 'F'}
        w = world_at(*docked_pose())
        for c in cols:
            w.bins[c] = mk_bin('pad', pads[c], SIZE[c], empty(c), jit=(0.05, 3.0), rng=rng); sc['expect_bins'][c] = nominal('pad', pads[c], SIZE[c])
        plan = []
        for c in cols: plan += pickup_trip(c, pads[c])
        # pickups start at the earliest legal time (dev s3b__s5_d1: 3 trips x ~55 min from 18:30 -> 3rd trip refused by the 21:00 guard)
        sc['clock_min'] = 18 * 60 + 0.0; sc['tmax'] = 3600 * 4.5 if name == 's3b' else 5400
        if name == 's3b': w.air_c = 0.0
    elif name in ('s4a', 's4b', 's4c', 's6a', 's7', 's5a', 'tune'):
        s0, s1 = dict(s4a=(35, 125), s4b=(35, 125), s4c=(35, 160), s6a=(200, 320), s7=(200, 320), s5a=(295, 380), tune=tuple(float(q) for q in os.environ.get('B2F_SEG', '200,290').split(',')))[name]
        w = world_at(*lane_pose(s0, 1.165, 'down')); carried_world(w, 'black', '240', 55.0)
        plan = [('lane', float(s1), None)]
        if name == 's4a': w.zones = [(60.0, 100.0, 'float')]
        if name == 's4b': w.zones = [(60.0, 80.0, 'none')]
        if name == 's4c': w.zones = [(60.0, 130.0, 'none')]
        if name == 's6a': sc['crash'] = ('lane', 230.0); sc['allow_hold'] = True
        if name == 's7': sc['estop'] = 230.0
        if name == 's5a':
            def crosser(kind, s_c, r, speed, trig, pause, pause_at, delay=0.0):
                a = S.lane.point(s_c, -1.95); b = S.lane.point(s_c, 1.95); m = 0.5 * (a + b)
                return dict(kind=kind, r=r, a=a.tolist(), b=b.tolist(), mid=m.tolist(), speed=speed, trigger_d=trig, pause=pause, pause_at=pause_at, t0=None, delay=delay)
            jit = rng.uniform(-0.5, 0.5)
            w.movers = [crosser('person', 320.0, 0.25, 1.0, 10.0 + jit, 15.0, 0.80), crosser('dog', 350.0, 0.20, 1.5, 5.5 + jit, 4.0, 0.80)]   # both stop IN the keep-left path
        sc['tmax'] = 900
    elif name in ('s5b', 's12a', 's12b'):
        s0 = 585.0 if name != 's12b' else 600.0
        w = world_at(*lane_pose(s0, 1.165, 'down')); carried_world(w, 'black', '240', 55.0)
        if name == 's5b':
            x, y, h = S.pose(L - 9.5, 0.3, 0.0); jit = rng.uniform(-3, 3)
            w.cars = [dict(x=float(x), y=float(y), yaw=float(h), L=4.4, W=1.8, appear_s=598.0 + jit, dwell=75.0, t0=None)]
            plan = [('lane', PADS['A']['s'] - STAGE_DROP, 0.0), ('wait_clear', 'A'), ('pivot_safe', 'up'), ('setdown', 'pad', 'A'), ('lane_short', -1, 6.0)]
        elif name == 's12a':
            sc['pads'] = dict(PADS, A=dict(s=L - 2.5, lat=0.0))
            plan = [('pad_check', 'A'), ('lane', sc['pads']['A']['s'] - STAGE_DROP, 0.0), ('pivot_safe', 'up'), ('setdown', 'pad', 'A')]
        else:
            sc['pi_fence_bypass'] = True; plan = [('bypass_drive', L + 4.0), ('end', 'fail', 'fence did not stop the robot')]
        sc['tmax'] = 900
    elif name in ('s9', 's10a', 's10b', 's6b'):
        w = world_at(*lane_pose(565.0 if name != 's6b' else PADS['A']['s'] - STAGE_PICK, 1.165 if name != 's6b' else 0.0, 'down' if name != 's6b' else 'up'))
        b = mk_bin('pad', 'A', '240', 13.0, jit=None if name == 's6b' else (0.05, 3.0), rng=rng)
        if name == 's9': b['state'] = 'gone'
        if name == 's10a': b['state'] = 'tipped'; b['yaw'] = wrap(b['yaw'] + math.pi / 2)
        w.bins['black'] = b; sc['expect_bins']['black'] = nominal('pad', 'A', '240')
        if name == 's10b':
            x, y, h = S.pose(PADS['A']['s'] - 1.9, 1.05, 0.0); w.obst = [dict(x=float(x), y=float(y), yaw=float(h) + 0.3, L=0.55, W=0.45, kind='sack')]
        if name == 's6b':
            plan = [('grab', 'black', 'A')]; sc['crash'] = ('grab', 0.0); sc['allow_hold'] = True
        else:
            plan = [('lane', PADS['A']['s'] - STAGE_PICK, 0.0), ('verify_bin', 'black', 'A'), ('pivot_safe', 'up'), ('grab', 'black', 'A'), ('lane_short', -1, 10.0)]
        sc['tmax'] = 900
    else:
        raise KeyError(name)
    sc['plan'] = plan; sc['world'] = w; sc['soc0'] = w.soc
    if name in ('s1a', 's1b', 's3a', 's3b'): sc['full_mission'] = True
    return sc
