"""Vehicle builders for the Rev H test bench: the Rev H straddle carrier and a Rev G tug + tilted bin (calibration reference)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dyn import Body, Wheel, Sim, Ground, settle, G
import params as P


def make_revh(binkey='ESE240SL', fill=1.0, mu=0.6, t_lim=None, x0=0.0):
    """Rev H: one rigid body (robot + lifted bin), 2 driven wheels, 2 nose casters, 2 tail anti-tip wheels."""
    R, D = P.ROBOT, P.DRIVE
    c = P.combined(binkey, fill) if binkey else P.combined(None)
    b = Body('revH', c['m'], c['iyy'], c['ixx'])
    cgx, cgz = c['x'], c['z']
    t_lim = D['t_lim'] if t_lim is None else t_lim
    for s, sg in (('L', 1.0), ('R', -1.0)):
        b.wheels.append(Wheel('drive' + s, R['drive_x'] - cgx, sg * R['drive_track'] / 2, R['drive_r'] - cgz, R['drive_r'], 1.2e5, 1500.0, mu,
                              driven=True, crr=D['crr'], t_lim=t_lim, kv=D['kv'], brake=D['brake'], i_w=D['i_wheel']))
        b.wheels.append(Wheel('nose' + s, R['nose_x'] - cgx, sg * R['nose_track'] / 2, R['nose_r'] - cgz, R['nose_r'], 3.0e5, 1000.0, mu, crr=0.03))
        b.wheels.append(Wheel('tail' + s, R['tail_x'] - cgx, sg * R['tail_track'] / 2, R['tail_r'] + R['tail_gap'] - cgz, R['tail_r'], 4.0e5, 800.0, mu, crr=0.03))
    b.x = x0 + cgx; b.z = cgz
    b.meta = dict(c, cgx=cgx, cgz=cgz, binkey=binkey, fill=fill)
    return b


def make_revg(bin_m=108.3, tug_m=None, mu=0.6, x0=0.0, t_lim=60.0, tx=0.67):
    """Rev G reference: 95 kg tug (drive axle at x0) towing a bin tilted 48 deg on its own wheels, pinned at the hook.
    Geometry from the project files (see params.REVG). The hook is a pin: the bin can pitch about it (hook float)."""
    V = P.REVG; tug_m = V['tug_m'] if tug_m is None else tug_m
    # --- tug
    cgx, cgz = V['tug_cg']                                      # from revG/cad/mass_g3_sim_L95.json: 98 mm ahead of the axle, 303 mm up
    tug = Body('tug', tug_m, tug_m * 0.42 ** 2, tug_m * 0.25 ** 2)
    for s, sg in (('L', 1.0), ('R', -1.0)):
        tug.wheels.append(Wheel('tdrive' + s, 0.0 - cgx, sg * 0.345, V['drive_r'] - cgz, V['drive_r'], 1.2e5, 1500.0, mu, driven=True,
                                crr=0.03, t_lim=t_lim, kv=150.0, brake=150.0, i_w=0.06))
        tug.wheels.append(Wheel('tcaster' + s, V['caster_x'] - cgx, sg * 0.20, V['caster_r'] - cgz, V['caster_r'], 3.0e5, 1000.0, mu, crr=0.03))
    tug.x = x0 + cgx; tug.z = cgz
    # --- bin, tilted back 48 deg about its axle towards the tug
    a = math.radians(V['bin_tilt_deg']); r = V['bin_wheel_r']
    rot = lambda xf, z: (xf * math.cos(a) - z * math.sin(a), xf * math.sin(a) + z * math.cos(a))   # bin frame (axle origin) -> world offsets
    cg_dx, cg_dz = rot(0.30, 0.50)                              # upright CG: 0.30 m ahead of the axle (away from the handle), 0.50 m up
    hk_dx, hk_dz = rot(-0.15, 0.90)                             # handle bar: 0.15 m behind the axle, 0.90 m above it
    ax_x = x0 - tx                                              # bin axle behind the kingpin (drive axle)
    binb = Body('bin', bin_m, bin_m * (0.74 ** 2 + 1.07 ** 2) / 12, bin_m * (0.58 ** 2 + 1.07 ** 2) / 12)
    # in this model +x is forward (towards the tug), so "towards the handle/tug" = +x: mirror the bin-frame x
    cgbx, cgbz = ax_x - cg_dx, r + cg_dz
    hkx, hkz = ax_x - hk_dx, r + hk_dz
    binb.x, binb.z = cgbx, cgbz
    for s, sg in (('L', 1.0), ('R', -1.0)):
        binb.wheels.append(Wheel('bin' + s, ax_x - cgbx, sg * V['bin_track'] / 2, r - cgbz, r, 6.0e5, 1000.0, mu, crr=0.03))
    joint = (tug, (hkx - tug.x, hkz - tug.z), binb, (hkx - binb.x, hkz - binb.z), 4.0e5, 4.0e3)
    meta = dict(hook=(hkx - x0, hkz), bin_cg=(cgbx - x0, cgbz), axle=ax_x - x0,
                hook_static_share=(cgbx - ax_x) / (hkx - ax_x))
    return tug, binb, joint, meta


def drive_test(sim, v, t_end, x_goal, on_log=None):
    """Drive at v until x_goal or t_end. Returns the log and a pass flag."""
    sim.v_cmd = v
    b0 = sim.b[0]
    def hook(s):
        if b0.x >= x_goal: s.t = 1e9
    t0 = sim.t
    n_log = int(round(0.004 / sim.dt)); i = 0
    while sim.t < t_end:
        if b0.x >= x_goal: break
        sim.step()
        if i % n_log == 0: sim.log.append(sim.snapshot())
        i += 1
    return sim.log, b0.x >= x_goal
