"""Scenario definitions. Lane coordinates: s = metres from the house end along the OSM lane, lat = metres left of
the house->road direction. L = lane length (633 m). rel_yaw 0 = facing the road (down-lane), pi = facing the house."""
import math, numpy as np
from world import wrap, BIN, TUG
TUG_HOOK_X = TUG['hook_x']
from scene import Site, ExtWorld, M_BIN_FULL, M_BIN_EMPTY, BIN_ID0
import os, json
from g4_features import Car, DropLayout, kl_lat, CFG, ROUTES
OUT_G4 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', os.environ.get('BT_OUTDIR', 'G6'))   # G6 outputs

_SITE = {}
def site(variant='real'):
    if variant not in _SITE: _SITE[variant] = Site(variant)
    return _SITE[variant]

DOCK = dict(s=4.0, lat=0.0)                       # charging dock in the yard, tug parked facing down-lane
HOUSE_BIN = dict(s=10.0, lat=-1.4)                # bin's home spot at the yard edge, handle facing down-lane
# Rev G3 multi-bin: home spots side by side in the open yard (handles facing down-lane); placed back in the order brown, green, black
HOME_SPOTS = {'black': dict(s=10.0, lat=-1.4), 'green': dict(s=10.0, lat=-3.0), 'brown': dict(s=10.0, lat=-4.6)}
# G6 s4 STUDY ONLY (default 0 = unchanged): env BT_HOME_DS moves every home spot that many m down-lane (away from the dock)
_HDS = float(os.environ.get('BT_HOME_DS', '0'))
if _HDS:
    HOUSE_BIN['s'] += _HDS
    for _v in HOME_SPOTS.values(): _v['s'] += _HDS
UTURN_S = 12.0                                    # Rev G3: the mouth U-turn starts at L-12.0 (was L-10.5) to stay on private ground
JUNCTION_WAIT = 23.0                              # Rev G3: junction wait point L-23 m: 15.7 m from the carriageway edge, 12.7 m inside the
                                                  # assumed private boundary, 11 m before the bell-mouth (LD06 12 m range reaches the mouth entrance)
YARD_DS, YARD_DLAT = -1.0, 5.8                    # Rev G6: yard U-turn start = home slot s-1 m, lat slot+5.8 m (28 deg kingpin stop)
def drop_nominal(S):                              # where the drop run leaves the bin = drop pad spot A (G6: handle faces the road)
    return dict(s=S.L - 11.1, lat=1.35)
def DROP_SPOTS(S):
    """Rev G3 drop pad (all on private ground): spot A at the bell-mouth (U-turn, release), spots M and F in the lane just
    up-lane of the mouth, on the left verge strip (U-turn in the mouth, then tow back up and release). Handles face up-lane."""
    return {'A': drop_nominal(S), 'M': dict(s=S.L - 14.6, lat=0.85), 'F': dict(s=S.L - 20.0, lat=0.85)}   # M-F 5.4 m (M's dock corridor); 1.2 m off the hedge line
# Pad spot per bin. Drop order = pickup order = brown, green, black (home spots must be refilled lat -4.6 -> -1.4, and A (the mouth)
# is always dropped last / picked last so the mouth is free for every U-turn and the lane is clear when the mouth bin comes home).
PAD_FOR = {1: {'black': 'A'}, 2: {'green': 'M', 'black': 'A'}, 3: {'brown': 'F', 'green': 'M', 'black': 'A'}}
CLOCK = {}                                        # filled per scenario: start clock, minutes from 00:00 on collection day (D-1 18:00 = -360)
def hhmm(t): return int(t[:2]) * 60 + int(t[3:5])


def bin_at(S, s, lat, rel_yaw, state='up'):
    x, y, yaw = S.pose(s, lat, rel_yaw); return dict(x=x, y=y, yaw=yaw, state=state)


def base(name, title, start, night=False, variant='real', tmax=4000, plan=(), bin_=None, others=(), obst=(), zones=(), movers=(),
         attached=False, bin_mass=M_BIN_EMPTY, bins=None, air_c=8.0, gust=5.0, soc0=0.90, contact_fault=0, charge_fault=False,
         pawl_stuck=0, vehicles=(), pack_heater=False, pack_c0=None, **kw):
    S = site(variant)
    x, y, yaw = S.pose(*start)
    w = ExtWorld(S, (x, y), yaw, night=night)
    w.air_c = air_c; w.wind_gust = gust; w.soc = w.soc0 = soc0; w.contact_fault = contact_fault; w.charge_fault = charge_fault
    w.pawl_stuck = pawl_stuck
    w.vehicles = list(vehicles); w.pack_heater = pack_heater; w.pack_c = pack_c0      # Rev G4
    dx, dy, dyaw = S.pose(DOCK['s'], DOCK['lat'], 0.0); off = TUG_HOOK_X - 0.30          # Rev G charging dock (fake-bin geometry)
    w.dock = dict(x=dx + off * math.cos(dyaw), y=dy + off * math.sin(dyaw), yaw=dyaw, state='up')
    w.bin = bin_; w.others = list(others); w.obst = list(obst); w.gps_zones = list(zones); w.bin_mass = bin_mass
    if bins:                                       # Rev G3: several of Brian's bins (multi-bin evenings), tag set per bin
        w.bins = bins; w.neighbours = list(others); first = kw.get('first', 'black')
        w.bin = bins[first]; w.bin_mass = bins[first]['mass']; w.others = [b for k, b in bins.items() if k != first] + list(others)
    for m in movers: w.movers.append(m(w))
    if attached:
        w.attached = True; w.hook_tilt = BIN['tilt_deg']
        w.bin = dict(x=x - BIN['L'] * math.cos(yaw), y=y - BIN['L'] * math.sin(yaw), yaw=yaw, state='up')
    d = dict(name=name, title=title, world=w, site=S, plan=list(plan), tmax=tmax, night=night, expect=EXPECT.get(name, 'pass'))
    d.update(kw); return d


def stander(kind, xy, r, leave_after_contact=None, leave_at=None, appear_d=None):
    """Rev G3: a person/child standing still at xy (off-scene until the tug is within appear_d m, if given). Walks off
    leave_after_contact s after the tug first touches them (crossbeam/bumper), or at absolute time leave_at."""
    def make(w):
        st = dict(on=appear_d is None, t_on=0.0)
        def pos(t):
            if not st['on']:
                if math.hypot(w.x - xy[0], w.y - xy[1]) < appear_d: st['on'] = True; st['t_on'] = t
                else: return (xy[0] + 60.0, xy[1] + 60.0)
            if leave_at is not None and t > st['t_on'] + leave_at: return (xy[0] + 60.0, xy[1] + 60.0)
            if leave_after_contact is not None:
                ev = [e for e in w.crossbeam_events if e['kind'] == 'mover'] + [e for e in w.chain_trips if 'mover' in e['reason']]
                if ev and t > min(e['t'] for e in ev) + leave_after_contact: return (xy[0] + 60.0, xy[1] + 60.0)
            return (float(xy[0]), float(xy[1]))
        return dict(kind=kind, r=r, pos=pos)
    return make


def visitor(kind, xy, r, appear_s, dwell):
    """Rev G3: a vehicle/lorry turning in the bell-mouth: appears when the tug passes lane station appear_s, stays dwell s."""
    def make(w):
        st = dict(t0=None)
        def pos(t):
            if st['t0'] is None:
                if w.site.lane.project(np.array([w.x, w.y]))[0] > appear_s: st['t0'] = t
                else: return (xy[0] + 80.0, xy[1] + 80.0)
            if t - st['t0'] > dwell: return (xy[0] + 80.0, xy[1] + 80.0)
            return (float(xy[0]), float(xy[1]))
        return dict(kind=kind, r=r, pos=pos)
    return make


def home_bins(S, mass, colours):
    out = {}
    for c in colours:
        hs = HOME_SPOTS[c]; b = bin_at(S, hs['s'], hs['lat'], 0.0); b.update(id0=BIN_ID0[c], mass=mass, colour=c); out[c] = b
    return out


def drop_plan(S, order, pad_for):
    """Rev G3 drop plan: per bin: house grab -> tow to the junction wait point -> look at the mouth -> mouth U-turn ->
    release at its pad spot (A at the mouth, M/F towed back up the lane) -> return -> dock. Ends docked."""
    L = S.L; plan = ['boot']
    for c in order:
        plan += [('select', c), 'house_grab', ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_tow'), 'junction_wait',
                 ('drop_out', pad_for[c]), ('auto', None, 7.0, 0.0, 'up_empty'), 'park']          # Rev G6 handles-out (no mouth U-turn)
    return plan


def pickup_plan(S, order, pad_for):
    L = S.L; plan = ['boot']
    for c in order:
        plan += [('select', c), ('to_seek', pad_for[c]), 'seek', 'up_tow_home', 'uturn_yard', 'place_house', 'park']
    return plan


def crosser(kind, s_cross, r, speed, trigger_d, lat0=-3.2, lat1=3.2, pause=4.0):
    """Person/dog crossing the lane at s_cross; starts when the tug is trigger_d m away, pauses mid-lane."""
    def make(w):
        S = w.site; st = dict(t0=None)
        a = S.lane.point(s_cross, lat0); b = S.lane.point(s_cross, lat1); Lab = np.linalg.norm(b - a)
        def pos(t):
            if st['t0'] is None:
                if math.hypot(w.x - a[0] / 2 - b[0] / 2, w.y - a[1] / 2 - b[1] / 2) < trigger_d: st['t0'] = t
                else: return (float(a[0]) + 50, float(a[1]) + 50)          # off-scene until triggered
            d = (t - st['t0']) * speed; mid = Lab * 0.45
            if d > mid: d = mid + max(0.0, d - mid - pause * speed)
            d = min(d, Lab)
            if d >= Lab and (t - st['t0']) > Lab / speed + pause + 6: return (float(b[0]) + 50, float(b[1]) + 50)
            p = a + (b - a) * d / Lab; return (float(p[0]), float(p[1]))
        return dict(kind=kind, r=r, pos=pos)
    return make


def walker(kind, s_start, lat, speed, appear_s, r=0.25):
    """Rev G4: a person walking / jogging along the lane at a fixed lat (speed < 0 = toward the house); appears when the tug
    passes lane station appear_s."""
    def make(w):
        st = dict(t0=None)
        def pos(t):
            if st['t0'] is None:
                if w.site.lane.project(np.array([w.x, w.y]))[0] > appear_s: st['t0'] = t
                else: return (1e4, 1e4)
            sq = s_start + speed * (t - st['t0'])
            if sq < 0 or sq > w.site.L: return (1e4, 1e4)
            p = w.site.lane.point(sq, lat); return (float(p[0]), float(p[1]))
        return dict(kind=kind, r=r, pos=pos)
    return make


def get(name):
    S = site('generic' if name.startswith('opt_') else 'real'); L = S.L
    dn = drop_nominal(S)
    evening_plan = ['boot', ('auto', 6.0, L - JUNCTION_WAIT, 0.0, 'down_empty'), 'junction_wait', ('auto', None, L - 16, 0.0, 'down_empty_mouth'),
                    'seek', ('auto', None, HOUSE_BIN['s'] + YARD_DS, HOUSE_BIN['lat'] + YARD_DLAT, 'up_tow'), 'uturn_yard', 'place_house', 'park']
    short_plan = ['boot', ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_empty'), 'junction_wait', ('auto', None, L - 16, 0.0, 'down_empty_mouth'),
                  'seek', ('auto', None, L - 45, 0.0, 'up_tow')]
    st = (L - 40, 0.0, 0.0)
    if name == 's1_morning':
        return base(name, '1  Morning drop-off (day): full bin down, empty return', (DOCK['s'], DOCK['lat'], 0.0),
                    bin_=bin_at(S, HOUSE_BIN['s'], HOUSE_BIN['lat'], 0.0), bin_mass=M_BIN_FULL, tmax=4200,
                    plan=['boot', 'house_grab', ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_tow'), 'junction_wait',
                          ('drop_out', 'A'), ('auto', None, 7.0, 0.0, 'up_empty'), 'park'], clock='08:00')
    if name == 's1n_night_drop':      # Rev G: the real operating case under the [county] bye-laws (full bin, after 18:00, dark)
        return base(name, '1n Night drop-off: full bin down in the dark, empty return', (DOCK['s'], DOCK['lat'], 0.0),
                    bin_=bin_at(S, HOUSE_BIN['s'], HOUSE_BIN['lat'], 0.0), bin_mass=M_BIN_FULL, tmax=4200, night=True,
                    plan=['boot', 'house_grab', ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_tow'), 'junction_wait',
                          ('drop_out', 'A'), ('auto', None, 7.0, 0.0, 'up_empty'), 'park'], clock='D-1 18:30', air_c=4.0)
    if name in ('s8a_crash_tow_nofs', 's8b_crash_tow_fs'):   # Rev G safety: the Pi hangs mid-tow (full bin, downhill)
        s0 = 300.0; nofs = name.endswith('nofs')
        return base(name, '8%s Companion crash mid-tow, full bin downhill (%s)' % ('a' if nofs else 'b', 'old params: FS_GCS off' if nofs else 'Rev G: FS_GCS on'),
                    (s0, 0.0, 0.0), attached=True, bin_mass=M_BIN_FULL, tmax=600, crash=('AUTO_DOWN_TOW', 25.0),
                    params=['FS_GCS_ENABLE 0'] if nofs else [], fs_label='FS_GCS_ENABLE 0' if nofs else 'FS_GCS_ENABLE 1',
                    plan=['boot', ('auto', None, s0 + 120, 0.0, 'down_tow')])
    if name == 's8c_crash_dock':     # Rev G safety: the Pi hangs while reversing onto the bin under RC override (MANUAL)
        return base(name, '8c Companion crash while reversing onto the bin (MANUAL + RC override)', (DOCK['s'], DOCK['lat'], 0.0),
                    bin_=bin_at(S, HOUSE_BIN['s'], HOUSE_BIN['lat'], 0.0), bin_mass=M_BIN_FULL, tmax=900, crash=('DOCK_REVERSE', 2.0),
                    plan=['boot', 'house_grab'])
    if name == 's9_dock_charge':     # Rev G: return to the charging dock from the lane, offset start
        return base(name, '9  Return onto the charging dock (contacts must close)', (40.0, 0.6, math.pi + math.radians(10)), tmax=900,
                    plan=['boot', ('auto', None, 12.0, 0.0, 'home_empty'), 'park'])
    if name == 's2_evening_day':
        b = bin_at(S, dn['s'] + 0.3, dn['lat'] - 0.2, math.radians(8))      # G6: left handles-out by the drop -> flipped at pickup
        return base(name, '2  Evening pickup (day): bin upright near the drop spot, handle to the road (G6 flip)', (DOCK['s'], DOCK['lat'], 0.0), bin_=b, tmax=4200, plan=evening_plan, clock='16:30')
    if name == 's3_night_pickup':
        b = bin_at(S, dn['s'] - 0.8, dn['lat'] - 0.6, math.pi + math.radians(30))
        return base(name, '3  Night pickup: bin offset ~1 m and rotated 30 deg', (DOCK['s'], DOCK['lat'], 0.0), bin_=b, night=True, tmax=4200, plan=evening_plan, clock='18:30')
    # ---------------- Rev G3 scenarios (ported from revG_alt + new) ----------------
    DK = (DOCK['s'], DOCK['lat'], 0.0)
    if name in ('s9a_dock_fault', 's9b_dock_cold', 's9c_no_charge'):
        k = name[2]
        ttl = {'a': 'missed contact (no dock voltage): retry, then alert', 'b': 'dock at -2 C: contacts made, charging inhibited',
               'c': 'contacts made but NO charge current: re-seat once, then alert'}[k]
        return base(name, '9%s Auto-charge: %s' % (k, ttl), (40.0, 0.6, math.pi + math.radians(10)), tmax=900, night=(k == 'b'),
                    plan=['boot', ('auto', None, 12.0, 0.0, 'home_empty'), 'park'], contact_fault=99 if k == 'a' else 0,
                    charge_fault=(k == 'c'), air_c=-2.0 if k == 'b' else 6.0, weather=dict(temp_c=4.0) if k == 'b' else None)
    if name in ('s10a_two_bin_drop', 's10b_two_bin_pickup', 's20a_three_bin_drop', 's20b_three_bin_pickup', 's20c_three_bin_pickup_noheat'):
        n = 2 if name.startswith('s10') else 3; cols = ['black', 'green'] if n == 2 else ['black', 'green', 'brown']
        pads = PAD_FOR[n]
        if name.endswith('drop'):
            bins = home_bins(S, M_BIN_FULL, cols); order = ['black', 'green'] if n == 2 else ['black', 'green', 'brown']   # G6: A -> M -> F
            plan = drop_plan(S, order, pads)
            if n == 3: plan = plan + [('sleep_until', 'D0 06:00')]     # starts 17:40 -> the boot bye-law guard sleeps it to 18:00
            return base(name, '%s %d bins out (%s), collection eve from 18:00, night, ~0 C%s' % (name[1:4], n, ' + '.join(order), ' (dock pack heater)' if n == 3 else ''), DK,
                        bins=bins, first=order[0], night=True, tmax=3000 * n + 2000, plan=plan, multi=n, mission='drop', pad_for=pads,
                        clock='D-1 17:40' if n == 3 else 'D-1 18:00', air_c=0.5 if n == 3 else 5.0, soc0=1.0 if n == 3 else 0.95,
                        pack_heater=(n == 3), pack_c0=5.0 if n == 3 else None)
        spots = DROP_SPOTS(S); bins = {}
        jit = {'black': (0.2, 0.1, 6), 'green': (-0.3, -0.15, -9), 'brown': (0.25, -0.1, 12)}
        for c in cols:
            sp = spots[pads[c]]; ds, dl, dy = jit[c]
            b = bin_at(S, sp['s'] + ds, sp['lat'] + dl, math.radians(dy)); b.update(id0=BIN_ID0[c], mass=M_BIN_EMPTY, colour=c); bins[c] = b   # G6: handles-out
        order = ['green', 'black'] if n == 2 else ['brown', 'green', 'black']
        plan = pickup_plan(S, order, pads)
        if n == 3: plan = [('sleep_until', 'D0 18:00')] + plan
        soc0 = 0.9; pc0 = None; heater = False
        if n == 3:
            # G4: s20b = the real evening: SOC + pack temperature carried over from s20a, overnight dock recharge (pack heater)
            # during the RTC sleep. s20c (renamed meaning in G4) = same start but NO heater: a +0.5 C pack cannot be charged.
            try:
                r20 = json.load(open(os.path.join(OUT_G4, 's20a_three_bin_drop' + os.environ.get('BT_OUT_SUFFIX', ''), 'result.json'))); soc0 = r20['soc_end']; pc0 = r20.get('pack_c_end')
            except Exception: soc0 = 0.55     # estimate if s20a has not been run yet
            heater = name == 's20b_three_bin_pickup'
            if not heater: pc0 = 0.5
        return base(name, '%s %d bins back after collection, %s, night, ~0 C%s' % (name[1:4], n, 'RTC wake 18:00' if n == 3 else '18:30',
                    (' (dock pack heater: overnight recharge)' if heater else ' (NO pack heater: no overnight charge)') if n == 3 else ''), DK,
                    bins=bins, first=order[0], night=True, tmax=3000 * n + 2000, plan=plan, multi=n, mission='pickup', pad_for=pads,
                    clock='D0 07:30' if n == 3 else 'D0 18:30', air_c=0.5 if n == 3 else 5.0, soc0=soc0, pack_heater=heater, pack_c0=pc0)
    if name == 's11b_estop':
        s0 = 300.0
        return base(name, '11b E-stop pressed mid-tow (full bin, downhill)', (s0, 0.0, 0.0), attached=True, bin_mass=M_BIN_FULL, tmax=700,
                    plan=['boot', ('auto', None, s0 + 90, 0.0, 'down_tow')], estop=('down_tow', s0 + 20))
    if name == 's12_bumper_low_object':
        s0 = 250.0; x, y, yaw = S.pose(s0 - 25, kl_lat(S.lane.width, -1) + 0.15, 0.4)   # G6 s3: on the up-lane keep-left line (was lat 0.15: missed since G4 keep-left)
        low = dict(kind='low object', x=x, y=y, yaw=yaw, L=0.55, W=0.45, H=0.18)
        return base(name, '12 Low object under the lidar beam (front bump strip, hard-wired chain)', (s0, 0.0, math.pi), obst=[low], tmax=700,
                    plan=['boot', ('auto', None, s0 - 80, 0.0, 'up_empty')])
    if name == 's13_low_battery':
        s0 = 300.0
        return base(name, '13 Pack nearly flat mid-tow (firmware battery failsafe)', (s0, 0.0, 0.0), attached=True, bin_mass=M_BIN_FULL, tmax=900,
                    soc0=0.06, plan=['boot', ('auto', None, s0 + 150, 0.0, 'down_tow')], params=['BATT_ARM_VOLT 0', 'BATT_LOW_VOLT 0'], skip_soc_gate=True)
    if name in ('s14a_weather_frost', 's14b_weather_wind'):
        fr = name == 's14a_weather_frost'
        wx = dict(temp_c=-1.5, gust_ms=4.0, frost=True) if fr else dict(temp_c=7.0, gust_ms=22.0, warning='yellow')
        return base(name, '14%s Weather no-go: %s' % ('a' if fr else 'b', 'frost (-1.5 C)' if fr else 'wind gusts 22 m/s'), DK,
                    bin_=bin_at(S, HOUSE_BIN['s'], HOUSE_BIN['lat'], 0.0), bin_mass=M_BIN_FULL, night=True, tmax=600,
                    plan=['boot', 'house_grab', ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_tow')], weather=wx, clock='D-1 18:30')
    if name == 's15_not_emptied':
        b = bin_at(S, dn['s'] + 0.3, dn['lat'] - 0.2, math.pi + math.radians(8))
        return base(name, '15 Bin NOT emptied by the crew (still full at pickup)', DK, bin_=b, bin_mass=M_BIN_FULL, night=True, tmax=4600,
                    plan=evening_plan, clock='D0 18:30', mission='pickup')
    sm = (L - 40, 0.0, 0.0)
    mouth_drop = ['boot', ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_tow'), 'junction_wait', ('drop_out', 'A'), ('auto', None, L - 45, 0.0, 'up_empty')]   # G6 handles-out
    AX = dn['s'] + 0.985; FR = AX + 0.957          # G6 release pose at A: drive axle / front bumper station (tug faces the road)
    if name in ('s16a_release_person', 's16b_release_blocked'):
        # F4: a person stands beside the tug at the drop pad (lingers 70 s) / an object is left within 1.5 m (never cleared)
        p = S.lane.point(FR + 0.55, dn['lat'] + 0.75)    # G6: 0.55 m beyond the front bumper, front-left, as the tug stops at A facing the road
        if name == 's16a_release_person':
            return base(name, '16a Release refused: person beside the tug at the pad (F4: hold + alert, never time out)', sm, attached=True,
                        bin_mass=M_BIN_FULL, tmax=1500, plan=mouth_drop, movers=[stander('person', p, 0.25, appear_d=2.6, leave_at=70.0)], expect='alert')
        x, y, yaw = S.pose(FR + 0.64, dn['lat'] + 0.9, 0.3)      # G6: same offset from the (now road-facing) front bumper as in G3/G4
        box = dict(kind='wheelbarrow', x=x, y=y, yaw=yaw, L=0.9, W=0.6, H=0.6)
        return base(name, '16b Release refused: object left within 1.5 m (F4: hold bin, alert, wait for owner)', sm, attached=True,
                    bin_mass=M_BIN_FULL, tmax=1500, plan=mouth_drop, obst=[box], expect='alert', release_hold_max=240.0)
    if name in ('s17a_release_sticky', 's17b_release_jammed'):
        jam = name.endswith('jammed')
        return base(name, '17%s Pawl %s at release (F2: mast wiggle x2, then hold + manual lever)' % ('b' if jam else 'a', 'jammed (ice)' if jam else 'sticks once'),
                    sm, attached=True, bin_mass=M_BIN_FULL, tmax=1200, plan=mouth_drop, pawl_stuck=99 if jam else 1, expect='alert' if jam else 'pass')
    if name == 's18a_child_centre_gap':
        hb = HOUSE_BIN; bx, by, byaw = S.pose(hb['s'], hb['lat'], 0.0)
        cx, cy = bx + 1.05 * math.cos(byaw), by + 1.05 * math.sin(byaw)       # 0.68 m in front of the handle face, on the dock axis
        return base(name, '18a Child standing in the centre gap behind the reversing tug (F7 crossbeam check)', DK,
                    bin_=bin_at(S, hb['s'], hb['lat'], 0.0), bin_mass=M_BIN_FULL, tmax=900, plan=['boot', 'house_grab'],
                    movers=[stander('child', (cx, cy), 0.13, leave_after_contact=25.0)], expect='alert')
    if name == 's18b_person_behind_dock':
        dx, dy, dyaw = S.pose(DOCK['s'] + 1.0, DOCK['lat'] + 0.05, 0.0)     # between the dock face and the tug's rear frame
        return base(name, '18b Person standing behind the tug as it reverses onto the charging dock (F7)', (40.0, 0.6, math.pi + math.radians(10)),
                    tmax=900, plan=['boot', ('auto', None, 12.0, 0.0, 'home_empty'), 'park'],
                    movers=[stander('person', (dx, dy), 0.22, leave_after_contact=30.0, appear_d=4.5)], expect='alert')
    if name == 's19_junction_wait':
        p = S.lane.point(L - 10.4, 0.5)                 # G6: car nosing into the lane end ON the approach to spot A (seen from the wait point)
        return base(name, '19 Car turning in the bell-mouth: tug waits at the junction wait point (L-27 m), never in the mouth', sm,
                    attached=True, bin_mass=M_BIN_FULL, tmax=1200, plan=mouth_drop, movers=[visitor('car', p, 1.3, L - 30, 75.0)])
    # ---------------- Rev G4 scenarios ----------------
    if name == 's16c_release_person_by_bin':
        # G4 pinch fix check: multi-bin drop at pad A with our green bin already on pad M (adjacent programmed slot -> exempt),
        # but a person stands against that bin inside the pinch zone -> must still refuse; owner calls through the tug speaker.
        # G6 handles-out: drop order A -> M, so the black bin is already on A and the GREEN bin is being dropped at M; the person
        # stands against the black bin's up-lane face, 0.8 m beyond the tug's front bumper (inside the 1.5 m pinch zone).
        lay = DropLayout(); gx, gy, gyaw = lay.bin_pose(S, 'A')
        green = dict(x=gx, y=gy, yaw=gyaw, state='up', id0=BIN_ID0['black'], mass=M_BIN_FULL, colour='black')
        p = S.lane.point(dn['s'] - 0.37 - 0.3, dn['lat'] - 0.3)
        w_ = base(name, '16c Release refused: person against our adjacent bin on pad M (slot exemption must NOT hide a person)', sm, attached=True,
                  bin_mass=M_BIN_FULL, tmax=1500, plan=mouth_drop[:1] + [('select', 'green')] + mouth_drop[1:3] + [('drop_out', 'M')] + mouth_drop[4:], multi=2, mission='drop',
                  pad_for={'green': 'M', 'black': 'A'}, pre_done=['black'], others=[green],
                  movers=[stander('person', p, 0.25, appear_d=4.5, leave_at=75.0)], expect='alert',
                  owner_call=dict(after_alert='release refused', delay_s=8.0, talk_s=40.0, says='Hello - could you step back from the bins? The robot is waiting to put one down.'))
        w_['world'].bin.update(id0=BIN_ID0['green'], mass=M_BIN_FULL, colour='green'); w_['world'].bins = {'green': w_['world'].bin, 'black': green}
        w_['placed0'] = [(gx, gy)]; return w_
    if name in ('s23a_vehicle_oncoming', 's23b_vehicle_behind', 's23c_vehicle_passing', 's23d_no_false_stop'):
        s0 = 300.0; st0 = (s0, kl_lat(S.lane.width, 1), 0.0)
        if name == 's23a_vehicle_oncoming':
            veh = [Car('car', s0 + 75, -1, v_cruise=4.5, mode='pass', appear_s=s0 + 12)]; ttl = 'oncoming car squeezes past (tug keeps left)'
        elif name == 's23b_vehicle_behind':
            veh = [Car('car', s0 - 18, +1, v_cruise=4.0, mode='follow', appear_s=s0 + 10, s_off=s0 + 62)]; ttl = 'car closes from behind, waits, then turns off at a gate'
        elif name == 's23c_vehicle_passing':
            veh = [Car('van', s0 - 20, +1, v_cruise=4.0, mode='pass', appear_s=s0 + 10, L=4.9, W=1.9, H=1.9)]; ttl = 'van from behind overtakes the stopped tug'
        else:
            veh = []; ttl = 'parked car + jogger: NO vehicle stop expected'
        obst = []; movers = []
        if name == 's23d_no_false_stop':
            x, y, yaw = S.pose(s0 + 45, -1.15, 0.02); obst = [dict(kind='car', x=x, y=y, yaw=yaw, L=4.3, W=1.8, H=1.45)]
            movers = [walker('jogger', s0 + 95, -1.35, -2.6, s0 + 20)]
        return base(name, '23%s Vehicle-approach stop: %s' % (name[3], ttl), st0, attached=True, bin_mass=M_BIN_FULL, tmax=900, vehicles=veh,
                    obst=obst, movers=movers, plan=['boot', ('auto', None, s0 + 120, 0.0, 'down_tow')])
    if name == 's21a_teach_route':
        hb = HOME_SPOTS['black']; b = bin_at(S, hb['s'], hb['lat'], 0.0); b.update(id0=0)
        return base(name, '21a Teach run (RC/app): record route + exact home and drop poses -> route file', (hb['s'] + 0.915 + 0.4, hb['lat'], 0.0),
                    bin_=b, bin_mass=M_BIN_FULL, tmax=4500, plan=['boot', ('teach', 'black'), 'park'], clock='16:00',
                    route_out=os.path.join(ROUTES, 'route_black.json'), mission='teach')
    if name == 's21b_repeat_drop':
        rf = os.path.join(ROUTES, 'route_black.json'); hp = {'s': HOME_SPOTS['black']['s'], 'lat': HOME_SPOTS['black']['lat'], 'yaw': None}
        try: R = json.load(open(rf)); hp = R['home_pose']
        except Exception: R = None
        b = bin_at(S, HOME_SPOTS['black']['s'], HOME_SPOTS['black']['lat'], 0.0); b.update(id0=0)
        return base(name, '21b Repeat the taught route at night: grab at the taught home pose, drop at the taught drop pose', DK,
                    bin_=b, bin_mass=M_BIN_FULL, night=True, tmax=4500, route_file=rf, clock='D-1 18:30', air_c=4.0,
                    plan=['boot', 'route_check', 'house_grab', ('route_leg', 'down', 'to_wait'), 'junction_wait', ('route_leg', 'down', 'to_drop'),
                          'release_route', 'turn_solo', ('route_leg', 'up', 'home'), 'park'])          # G6 handles-out
    if name in ('s22a_calendar_week_a', 's22b_calendar_week_b'):
        wk_b = name.endswith('b'); evening = '2026-11-24' if wk_b else '2026-11-17'
        bins = home_bins(S, M_BIN_FULL, ['black', 'green', 'brown'])
        lay = os.path.join(CFG, 'drop_layout_custom.json' if wk_b else 'drop_layout_default.json')
        return base(name, '22%s Bin calendar: evening %s -> week %s bins%s' % ('b' if wk_b else 'a', evening, 'B' if wk_b else 'A', ', custom drop layout' if wk_b else ''), DK,
                    bins=bins, first='black', night=True, tmax=7000, plan=[('calendar', evening)], multi=2, mission='drop', clock='D-1 18:00',
                    calendar=os.path.join(CFG, 'bin_calendar.json'), layout=lay, air_c=5.0, soc0=0.95)
    if name in ('s24a_home_slot_car', 's24b_all_slots_blocked', 's24c_keepout_route', 's24d_pickup_logged_pose'):
        # Rev G4 g) adaptive drop spot / keep-outs
        if name == 's24a_home_slot_car':
            x, y, yaw = S.pose(9.0, -1.6, 0.03); car = dict(kind='car', x=x, y=y, yaw=yaw, L=4.3, W=1.8, H=1.45)
            return base(name, '24a Home slot blocked by a parked car -> nearest clear legal alternate in the yard (night)', (60.0, kl_lat(S.lane.width, -1), math.pi),
                        attached=True, bin_mass=M_BIN_EMPTY, obst=[car], night=True, tmax=1500, clock='D0 19:00', mission='pickup',
                        plan=['boot', ('auto', None, HOUSE_BIN['s'] + YARD_DS, HOUSE_BIN['lat'] + YARD_DLAT, 'up_tow'), 'uturn_yard', 'place_house', 'park'])
        if name == 's24b_all_slots_blocked':
            obst = []
            for so, la, Lx, Wx, H, k in ((14.6, 0.95, 1.3, 1.0, 0.6, 'debris'), (18.0, 1.0, 0.74, 0.58, 1.07, 'bin (not ours)')):
                x, y, yaw = S.pose(L - so, la, 0.1); obst.append(dict(kind=k, x=x, y=y, yaw=yaw, L=Lx, W=Wx, H=H))
            w_ = base(name, '24b Pad M and every alternate blocked (debris, a stranger\'s bin) -> hold with the bin + alert', sm, attached=True,
                      bin_mass=M_BIN_FULL, obst=obst, tmax=1200, multi=1, mission='drop', pad_for={'green': 'M'}, expect='alert',
                      plan=['boot', ('select', 'green'), ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_tow'), 'junction_wait',
                            ('drop_out', 'M'), ('auto', None, L - 45, 0.0, 'up_empty')])
            w_['world'].bin.update(id0=4, colour='green', mass=M_BIN_FULL); w_['world'].bins = {'green': w_['world'].bin}; return w_
        if name == 's24c_keepout_route':
            ko = [dict(name='soft verge over a septic tank (user keep-out)', frame='house', poly=[[300.0, 0.5], [312.0, 0.5], [312.0, 2.2], [300.0, 2.2]])]
            return base(name, '24c Keep-out zone on the keep-left line: the route must go round it', (280.0, kl_lat(S.lane.width, 1), 0.0), attached=True,
                        bin_mass=M_BIN_FULL, tmax=700, keepouts_extra=ko, plan=['boot', ('auto', None, 340.0, 0.0, 'down_tow')])
        # s24d: the drop log says the black bin was left on an alternate (L-18.0, lat 0.95); the crew moved it another ~0.5 m
        lx, ly, lyaw = S.pose(L - 18.0, 0.95, 0.0)        # G6: logged handles-out
        log = {'black': dict(x=lx, y=ly, yaw=lyaw, s=L - 18.0, lat=0.95, slot="M'", how='release_pad')}
        b = bin_at(S, L - 18.45, 0.75, math.radians(9)); b.update(id0=0, mass=M_BIN_EMPTY, colour='black')   # G6: handles-out
        return base(name, '24d Pickup from where the bin was actually left (drop log + lidar/tag search), not the programmed pad', (L - 45, 0.0, 0.0),
                    bins={'black': b}, first='black', night=True, tmax=1200, multi=1, mission='pickup', pad_for={'black': 'A'}, drop_log=log,
                    plan=['boot', ('select', 'black'), ('to_seek', 'LOG'), 'seek', ('auto', None, L - 60, 0.0, 'up_tow')])
    if name.startswith('t_kl'):       # dev test: keep-left tracking. t_kl_<navl1period>_<spacing>[_<damping>]
        parts = name.split('_'); per = parts[2]; sp = float(parts[3]); dmp = parts[4] if len(parts) > 4 else None
        prm = ['NAVL1_PERIOD %s' % per] + (['NAVL1_DAMPING %s' % dmp] if dmp else [])
        if parts[1] == 'klp': prm = ['PSC_POS_P %s' % per] + (['PSC_VEL_P %s' % dmp] if dmp else []) + (['PSC_VEL_I %s' % parts[5]] if len(parts) > 5 else []); sp = float(parts[3])
        return base(name, 'dev: keep-left tracking test', (290.0, kl_lat(S.lane.width, 1), 0.0), attached=True, bin_mass=M_BIN_FULL, tmax=600,
                    params=prm, kl_spacing=sp, plan=['boot', ('auto', None, 410.0, 0.0, 'down_tow')])
    if name == 't_pad_drop':          # dev test (not in the regression): tow-back release at pad M
        b0 = home_bins(S, M_BIN_FULL, ['green'])
        w_ = base(name, 'test: release at pad M', sm, attached=True, bin_mass=M_BIN_FULL, tmax=900, multi=2, mission='drop',
                  plan=['boot', ('select', 'green'), ('auto', None, L - JUNCTION_WAIT, 0.0, 'down_tow'), 'junction_wait',
                        ('auto', None, L - UTURN_S, -2.3, 'down_tow_mouth'), 'uturn_mouth', ('release_pad', 'M'), ('auto', None, L - 45, 0.0, 'up_empty')])
        w_['world'].bin.update(id0=4); w_['world'].bins = {'green': w_['world'].bin}; return w_
    if name == 't_pad_pick':          # dev test: pick the green bin at pad M with our black bin at pad F
        spots = DROP_SPOTS(S); bins = {}
        for c, pd, j in (('green', 'M', (-0.3, -0.15, -9)), ('black', 'F', (0.2, 0.1, 6))):
            sp = spots[pd]; b = bin_at(S, sp['s'] + j[0], sp['lat'] + j[1], math.radians(j[2])); b.update(id0=BIN_ID0[c], mass=M_BIN_EMPTY, colour=c); bins[c] = b   # G6 handles-out
        return base(name, 'test: pickup at pad M', (L - 45, 0.0, 0.0), bins=bins, first='green', night=True, tmax=900, multi=2, mission='pickup',
                    plan=['boot', ('select', 'green'), ('to_seek', 'M'), 'seek', ('auto', None, L - 60, 0.0, 'up_tow')])
    if name == 'test_seek':
        return base(name, 'test: nominal bin, short', st, bin_=bin_at(S, dn['s'] + 0.3, dn['lat'] - 0.2, math.pi + math.radians(8)), tmax=900, plan=short_plan)
    if name in ('s4a_backwards_day', 's4a_backwards_night'):
        b = bin_at(S, L - 9.5, 0.3, 0.0) if 'day' in name else bin_at(S, L - 8.8, 0.2, math.radians(10))   # G3: shifted 1.5-2.5 m inland (legal fence)
        return base(name, '4a Bin backwards, handle to the road (%s)' % ('night, closer to road' if 'night' in name else 'day'), st, bin_=b,
                    night='night' in name, tmax=1500, plan=short_plan)
    if name == 's4b_sideways':
        b = bin_at(S, L - 10.5, 2.6, -math.pi / 2)     # G3: shifted 1.5 m inland with the pad
        return base(name, '4b Bin sideways across the verge', st, bin_=b, tmax=1500, plan=short_plan)
    if name == 's4c_in_hedge':
        b = bin_at(S, L - 15.0, -1.65, -math.pi / 2 - math.radians(25))
        return base(name, '4c Bin shoved into the hedge, little room', st, bin_=b, tmax=1500, plan=short_plan)
    if name == 's4d1_moved_mouth':
        b = bin_at(S, L - 10.8, -3.0, math.pi + math.radians(20))    # G3: moved 3.3 m inland (old spot is now s4i: public verge)
        return base(name, '4d Bin moved ~5 m across the junction mouth', st, bin_=b, tmax=1500, plan=short_plan)
    if name == 's4i_on_verge':        # Rev G3 legal fence: the old 4d spot is on the road verge (a public place) -> must not go there
        b = bin_at(S, L - 7.5, -3.6, math.pi + math.radians(20))
        return base(name, '4i Bin left on the public road verge (outside private ground)', st, bin_=b, tmax=1500, plan=short_plan)
    if name == 's4d2_moved_road':
        R = S.road; e = S.lane.P[-1]; d = R[-1] - R[0]; d = d / np.linalg.norm(d); n = np.array([-d[1], d[0]])
        if (n @ (S.lane.point(L - 10, 0) - e)) < 0: n = -n
        p = e + d * 12.0 + n * 3.6
        b = dict(x=float(p[0]), y=float(p[1]), yaw=math.atan2(n[1], n[0]), state='up')
        return base(name, '4d Bin moved 12 m along the road verge (outside geofence)', st, bin_=b, tmax=1500, plan=short_plan)
    if name == 's4e_tipped_night':
        b = bin_at(S, dn['s'], dn['lat'], math.pi / 2, state='tipped')
        return base(name, '4e Bin tipped over on its side (night)', st, bin_=b, night=True, tmax=1500, plan=short_plan)
    if name == 's4f_in_road':
        p = S.lane.point(L - 3.0, -0.6)
        b = dict(x=float(p[0]), y=float(p[1]), yaw=S.lane.heading(L) + math.radians(150), state='up', lid_open=True)
        return base(name, '4f Bin partly in the public road, lid open', st, bin_=b, tmax=1500, plan=short_plan)
    if name == 's4g_neighbour_night':
        nb = bin_at(S, dn['s'], dn['lat'], math.pi + math.radians(5))              # neighbour's bin on our usual spot
        b = bin_at(S, dn['s'] + 0.3, dn['lat'] - 1.6, math.pi - math.radians(10))   # ours, 1.6 m beside it
        return base(name, '4g Neighbour\'s bin beside ours (night)', st, bin_=b, others=[nb], night=True, tmax=1500, plan=short_plan)
    if name == 's4h_car_block':
        b = bin_at(S, dn['s'] + 2.0, dn['lat'], math.pi)
        x, y, yaw = S.pose(L - 10.5, 0.0, math.pi / 2 + math.radians(10))
        car = dict(kind='car', x=x, y=y, yaw=yaw, L=4.3, W=1.8, H=1.45)
        return base(name, '4h Parked car blocks the bin', st, bin_=b, obst=[car], tmax=1500, plan=short_plan)
    if name == 's5_person_dog':
        s0 = 300.0
        return base(name, '5  Person, then dog, cross mid-tow (full bin, downhill)', (s0, 0.0, 0.0), attached=True, bin_mass=M_BIN_FULL, tmax=900,
                    movers=[crosser('person', s0 + 25, 0.25, 0.9, 4.2), crosser('dog', s0 + 60, 0.2, 2.0, 4.0, lat0=3.0, lat1=-3.2)],
                    plan=['boot', ('auto', None, s0 + 90, 0.0, 'down_tow')])
    if name == 's6_branch':
        s0 = 420.0
        x, y, yaw = S.pose(s0 + 22, -0.85, 0.25)
        br = dict(kind='branch', x=x, y=y, yaw=yaw, L=2.2, W=0.5, H=0.5)
        return base(name, '6  Fallen branch partly blocks the lane', (s0, 0.0, 0.0), attached=True, bin_mass=M_BIN_FULL, obst=[br], tmax=900,
                    plan=['boot', ('auto', None, s0 + 50, 0.0, 'down_tow')])
    if name == 's7_rtk_dropout':
        s0 = 120.0
        return base(name, '7  RTK dropout under trees: float, short loss, long loss', (s0, 0.0, math.pi), attached=True, tmax=1200,
                    zones=[(60, 110, 'float'), (84, 90, 'none'), (20, 58, 'float'), (28, 52, 'none')],
                    plan=['boot', ('auto', None, 10.0, 0.0, 'up_tow')])
    # ---------------- Rev G6 scenarios ----------------
    if name in ('s25a_corridor_down', 's25b_rtk_only_down', 's25c_corridor_up'):
        up = name == 's25c_corridor_up'; rtk_only = name == 's25b_rtk_only_down'
        sa = float(os.environ.get('BT_S25_S0', 'nan')); sb = float(os.environ.get('BT_S25_S1', 'nan'))   # G6 tuning: lane segment only
        if up: sa, sb = (L - 30.0 if sa != sa else sa), (30.0 if sb != sb else sb)
        else: sa, sb = (30.0 if sa != sa else sa), (L - 30.0 if sb != sb else sb)
        st0 = (sa, kl_lat(S.lane.width, -1 if up else 1), math.pi if up else 0.0)
        return base(name, '25%s %s, full lane %s with tree-canopy RTK multipath, hedge gaps and narrowings%s' % (name[3], 'Corridor-primary lateral (lidar hedge fit)' if not rtk_only else 'BASELINE RTK-primary lateral (corridor OFF)',
                    'up (empty bin)' if up else 'down (full bin)', ''), st0, attached=True, bin_mass=M_BIN_EMPTY if up else M_BIN_FULL, tmax=2400,
                    corridor=not rtk_only, plan=['boot', ('auto', None, sb, 0.0, 'up_tow' if up else 'down_tow')])
    if name == 's7b_rtk_long_loss':
        s0 = 330.0
        return base(name, '7b RTK lost for 160 m under trees (no fix at all): corridor + odometry until along-lane uncertainty > 2.5 m -> hold + alert', (s0, 0.0, math.pi), attached=True, tmax=1500,
                    zones=[(100, 300, 'none')], plan=['boot', ('auto', None, 30.0, 0.0, 'up_tow')], expect='alert')
    if name in ('dev_narrow_solo', 'dev_narrow_tow', 'dev_narrow_towup', 'dev_bends_solo'):          # G6 session 3 dev tests (not in the regression)
        if name == 'dev_bends_solo':
            return base(name, 'dev: dog-leg bends s=30-130 down and back up (solo)', (28.0, 0.0, 0.0), tmax=900,
                        plan=['boot', ('auto', None, 130.0, 0.0, 'down_empty'), ('auto', None, 26.0, 0.0, 'up_empty')])
        if name == 'dev_narrow_solo':
            return base(name, 'dev: narrowing s=500-516 down and back up (solo)', (470.0, kl_lat(S.lane.width, 1), 0.0), tmax=900,
                        plan=['boot', ('auto', None, 545.0, 0.0, 'down_empty'), ('auto', None, 380.0, 0.0, 'up_empty')])
        up = name.endswith('up')
        return base(name, 'dev: narrowing towing %s' % ('up' if up else 'down'), (545.0, kl_lat(S.lane.width, -1), math.pi) if up else (470.0, kl_lat(S.lane.width, 1), 0.0),
                    attached=True, bin_mass=M_BIN_EMPTY if up else M_BIN_FULL, tmax=600,
                    plan=['boot', ('auto', None, 380.0 if up else 545.0, 0.0, 'up_tow' if up else 'down_tow')])
    if name == 'dev_yard_uturn':          # G6 s4 dev: s24a without the car (yard U-turn + place_house accuracy study)
        return base(name, 'dev: tow the empty black bin up into the yard, U-turn, place on the home slot (no car)', (60.0, kl_lat(S.lane.width, -1), math.pi),
                    attached=True, bin_mass=M_BIN_EMPTY, night=True, tmax=1500, clock='D0 19:00', mission='pickup',
                    plan=['boot', ('auto', None, HOUSE_BIN['s'] + YARD_DS, HOUSE_BIN['lat'] + YARD_DLAT, 'up_tow'), 'uturn_yard', 'place_house', 'park'])
    if name == 'opt_generic_12pct':
        return base(name, 'Optional: generic 12 % / 2.8 m lane, full bin', (4.0, 0.0, 0.0), variant='generic', attached=True, bin_mass=M_BIN_FULL, tmax=1500,
                    plan=['boot', ('auto', None, S.L - 12, 0.0, 'down_tow'), ('auto', None, 10.0, 0.0, 'up_tow')])
    raise KeyError(name)


EXPECT = {'s4d1_moved_mouth': 'alert',    # G3: with the verge excluded, a bin moved into the private corner of the bell-mouth has no legal
                                         # approach corridor and no nudge room -> alert (G2 picked it up by using the verge). Set after
                                         # two re-positioning attempts (L-11.5/-3.4 wedged, L-10.8/-3.0 no room); not tuned further.
          's4c_in_hedge': 'alert', 's4d2_moved_road': 'alert', 's4e_tipped_night': 'alert', 's4f_in_road': 'alert', 's4h_car_block': 'alert',
          's4i_on_verge': 'alert', 's7_rtk_dropout': 'alert', 's8a_crash_tow_nofs': 'fail', 's9a_dock_fault': 'alert', 's9c_no_charge': 'alert',
          's11b_estop': 'alert', 's12_bumper_low_object': 'alert', 's13_low_battery': 'alert', 's14a_weather_frost': 'alert',
          's14b_weather_wind': 'alert', 's15_not_emptied': 'alert', 's16a_release_person': 'alert', 's16b_release_blocked': 'alert',
          's17b_release_jammed': 'alert', 's18a_child_centre_gap': 'alert', 's18b_person_behind_dock': 'alert',
          # s20b: predicted BEFORE the run from the G3 trip energy (~43 Wh/trip): 12 Ah at +0.5 C with charging inhibited cannot do
          # 3 drops + 3 pickups above the 10 % reserve -> the energy guard must leave the last bin and alert (requirement NOT met)
          's20c_three_bin_pickup_noheat': 'alert',      # G4: no pack heater at +0.5 C -> no overnight charge -> energy guard must leave bin(s) + alert
          's16c_release_person_by_bin': 'alert', 's24b_all_slots_blocked': 'alert'}
# G6 session 3: s25b (RTK-only baseline) stays expected=pass - it is judged on its driving metrics (hedge clearance, holds), not re-classified.
# G4: s20b is now expected to PASS (overnight dock recharge with the pack heater, all 3 bins back by 21:00)
NEW_G3 = ['s4i_on_verge', 's9a_dock_fault', 's9b_dock_cold', 's9c_no_charge', 's10a_two_bin_drop', 's10b_two_bin_pickup', 's11b_estop',
          's12_bumper_low_object', 's13_low_battery', 's14a_weather_frost', 's14b_weather_wind', 's15_not_emptied', 's16a_release_person',
          's16b_release_blocked', 's17a_release_sticky', 's17b_release_jammed', 's18a_child_centre_gap', 's18b_person_behind_dock',
          's19_junction_wait', 's20a_three_bin_drop', 's20b_three_bin_pickup', 's20c_three_bin_pickup_noheat']
ALL = ['s1_morning', 's2_evening_day', 's3_night_pickup', 's4a_backwards_day', 's4a_backwards_night', 's4b_sideways', 's4c_in_hedge',
       's4d1_moved_mouth', 's4d2_moved_road', 's4e_tipped_night', 's4f_in_road', 's4g_neighbour_night', 's4h_car_block',
       's5_person_dog', 's6_branch', 's7_rtk_dropout',
       's1n_night_drop', 's8a_crash_tow_nofs', 's8b_crash_tow_fs', 's8c_crash_dock', 's9_dock_charge']    # last five: Rev G
ALL_G3 = ALL + NEW_G3
ROBUST_G3 = ['s4a_backwards_day', 's4a_backwards_night', 's4b_sideways', 's4c_in_hedge', 's4d1_moved_mouth', 's4g_neighbour_night',
             's5_person_dog', 's8c_crash_dock', 's9_dock_charge',                       # the G2 robustness set
             's16a_release_person', 's17b_release_jammed', 's18a_child_centre_gap', 's19_junction_wait']   # + new G3 safety cases

NEW_G4 = ['s16c_release_person_by_bin', 's21a_teach_route', 's21b_repeat_drop', 's22a_calendar_week_a', 's22b_calendar_week_b',
          's23a_vehicle_oncoming', 's23b_vehicle_behind', 's23c_vehicle_passing', 's23d_no_false_stop',
          's24a_home_slot_car', 's24b_all_slots_blocked', 's24c_keepout_route', 's24d_pickup_logged_pose']
ALL_G4 = ALL_G3 + NEW_G4
ROBUST_G4 = ROBUST_G3 + ['s16c_release_person_by_bin', 's23a_vehicle_oncoming', 's23b_vehicle_behind', 's23c_vehicle_passing', 's23d_no_false_stop',
                         's24a_home_slot_car', 's24b_all_slots_blocked', 's24c_keepout_route', 's24d_pickup_logged_pose']

NEW_G6 = ['s25a_corridor_down', 's25b_rtk_only_down', 's25c_corridor_up', 's7b_rtk_long_loss']
ALL_G6 = ALL_G4 + NEW_G6
ROBUST_G6 = ROBUST_G4 + ['s25a_corridor_down', 's2_evening_day', 's10b_two_bin_pickup']
