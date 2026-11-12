"""Bin Tug Rev H ("straddle carrier") - single source of geometry, mass and bin data for the concept test bench.

Units: m, kg, N, s. Robot frame: origin on the ground under the drive-axle centre, +x towards the nose
(direction of travel on the lane), +y left, +z up. The bin sits behind the mast, between the legs.

CONCEPT STAGE: every number here is a design intent or an estimate, not a measurement. Bin data are the
project's own G5 data-sheet values (revG/sim/g5/bins_g5.py), copied unchanged.
"""
import math

G = 9.81

# ----------------------------------------------------------------------------------------------- robot geometry
ROBOT = dict(
    # Layout "A4" chosen by the layout study in tests_mech.py (see RESULTS section 3): batteries on the legs beside the
    # drive wheels, motors pointing aft, electronics on the mast, 260 mm flat-free nose casters, pad 0.37 m ahead of the axle.
    drive_x=0.0, drive_track=0.97, drive_r=0.159,            # donor powerchair 12.5 in drive wheels; motors lie under the rails, inboard face flush at y = 0.33
    nose_x=0.74, nose_track=0.60, nose_r=0.130,              # 260 mm flat-free swivel casters
    tail_x=-0.40, tail_track=0.81, tail_r=0.050, tail_gap=0.075,   # anti-tip wheels under the flared rail tips (clear of the bin wheels), 75 mm off the ground
    leg_inner_gap=0.66,                                       # clear width between the legs
    funnel_mouth=0.78, funnel_len=0.20,                       # flared leg tips
    leg_tip_x=-0.43, nose_tip_x=0.88,                         # overall length 1.31 m
    width=1.04, height=1.30,
    pad_x=0.37,                                               # carriage pad face = bin front wall when docked
    comb_width=0.60,
    comb_z_min=0.84, comb_z_max=1.14,                         # carriage travel (300 mm stroke)
    lift=0.100,                                               # carry height of the bin above the ground
    pad_drop=0.45,                                            # lower pad below the comb
    mast_x=0.45, mast_half_span=0.22,
    lidar=(0.88, 0.0, 0.35), cam=(0.45, 0.0, 1.33),
)

# mass roll-up (kg, x, z) - estimate; steel from section tables, donor drive from the project's G3 figure (19 kg pair)
MASS_ITEMS = [
    ('Side rails (legs) 2 x 1.31 m 50x50x3 RHS',    11.6,  0.20, 0.285),
    ('Nose cross-member 50x50x3 + caster outriggers', 5.5,  0.72, 0.285),
    ('Mast uprights 2 x 1.05 m 50x50x3',             9.3,  0.45, 0.80),
    ('Mast ties and braces',                         3.0,  0.52, 0.60),
    ('Carriage, comb blade, pads',                   4.5,  0.40, 0.90),
    ('Lift actuator 3000 N / 300 mm',                2.0,  0.47, 0.65),
    ('Donor drive units x2 (motor, gearbox, brake, wheel), motors aft', 19.0, -0.08, 0.16),
    ('Nose casters 260 mm flat-free + forks x2',     5.0,  0.74, 0.15),
    ('Tail anti-tip wheels x2',                      0.8, -0.40, 0.10),
    ('Batteries 2 x 12 V 18 Ah AGM, one on each leg behind the wheel', 10.8, -0.24, 0.36),
    ('Electronics box, driver, contactor, harness (on the mast)', 5.0, 0.51, 0.55),
    ('Sensors, lights, bumpers, deck, covers',       5.0,  0.55, 0.50),
    ('Motor plates, brackets, fasteners',            4.0,  0.15, 0.22),
]


def robot_mass():
    m = sum(i[1] for i in MASS_ITEMS)
    x = sum(i[1] * i[2] for i in MASS_ITEMS) / m
    z = sum(i[1] * i[3] for i in MASS_ITEMS) / m
    # pitch and roll inertia about the CG (point masses + a spread allowance of 15 %)
    iyy = 1.15 * sum(i[1] * ((i[2] - x) ** 2 + (i[3] - z) ** 2) for i in MASS_ITEMS)
    ixx = 1.15 * sum(i[1] * ((i[3] - z) ** 2 + 0.30 ** 2) for i in MASS_ITEMS)
    return dict(m=m, x=x, z=z, iyy=iyy, ixx=ixx)


# ----------------------------------------------------------------------------------------------- drive (donor powerchair)
DRIVE = dict(
    t_lim=60.0,         # N.m per wheel usable at the driver current limit (same value the Rev G MuJoCo study used)
    t_lim_hi=80.0,      # sensitivity: MDDS30 80 A peak / chair controller class
    kv=150.0,           # N.m.s/rad velocity-loop gain (as Rev G sim)
    v_noload=1.67,      # m/s at 24 V (6 km/h chair)
    brake=150.0,        # N.m spring-brake hold per wheel (Rev G assumption)
    i_wheel=0.06,       # kg.m^2 wheel + reflected rotor inertia (low because the gearbox is not back-driven hard at these speeds)
    crr=0.03,           # rolling resistance, pneumatic tyre on rough tarmac / gravel
    eta=0.60,           # battery -> wheel efficiency at light load
)

# ----------------------------------------------------------------------------------------------- bins (project G5 data)
# H, W, D overall; comb = height of the frontal receiver; track = overall width over the wheels; empty / fill_full masses
BINS = {
    'WEB140':      dict(name='Weber 140 L',                 H=1.050, W=0.475, D=0.545, comb=1.001, wheel=0.20, track=0.479, empty=10.0, fill_full=56.0),
    'ESE140CL':    dict(name='ESE 140 CL',                  H=1.030, W=0.480, D=0.553, comb=0.969, wheel=0.20, track=0.478, empty=9.0,  fill_full=61.0),
    'ESE240SL':    dict(name='ESE 240 SL (200 mm wheels)',  H=1.079, W=0.583, D=0.737, comb=1.005, wheel=0.20, track=0.569, empty=13.0, fill_full=97.0),
    'ESE240SL250': dict(name='ESE 240 SL (250 mm wheels)',  H=1.104, W=0.583, D=0.737, comb=1.030, wheel=0.25, track=0.580, empty=13.6, fill_full=96.4),
    'SULO240':     dict(name='SULO Citybac 240',            H=1.075, W=0.582, D=0.728, comb=0.991, wheel=0.20, track=0.575, empty=10.2, fill_full=99.8),
    'ESE240CL':    dict(name='ESE 240 CL (lowest)',         H=1.003, W=0.580, D=0.738, comb=0.938, wheel=0.20, track=0.569, empty=11.0, fill_full=99.0),
    'CRA240':      dict(name='Craemer MGBneo 240 (tallest)', H=1.100, W=0.580, D=0.740, comb=None,  wheel=0.20, track=0.590, empty=12.0, fill_full=96.0),
}
COMB_UNKNOWN_BAND = (1.000, 1.030)   # Craemer comb height is not published: sampled in this band (H 1100 max)
EN840_COMB_BAND = (0.860, 1.030)     # EN 840-1 Tables 2/3 dimension 5 as extracted from the 2004 text - verify on the bins


def bin_cg(b, fill_frac):
    """Bin CG relative to the bin's front wall at rim height (xf = distance behind the front wall) and height above its base.
    Body: mid-depth of the body shell (handle and wheels excluded), 45 % of height. Contents: bins taper towards the base at the
    front, so the contents' centroid sits a little behind mid-depth and above mid-height."""
    body_depth = b['D'] - 0.105                      # shell depth without the handle overhang (~105 mm)
    m_e, m_c = b['empty'], b['fill_full'] * fill_frac
    xf_e, z_e = 0.52 * body_depth, 0.45 * b['H']
    xf_c, z_c = 0.55 * body_depth, (0.10 + 0.47 * fill_frac) * b['H']
    m = m_e + m_c
    return dict(m=m, xf=(m_e * xf_e + m_c * xf_c) / m, z=(m_e * z_e + m_c * z_c) / m)


def combined(binkey=None, fill_frac=1.0, lift=None):
    """Robot (+ carried bin) mass, CG and inertias in the robot frame."""
    r = robot_mass()
    if binkey is None:
        return dict(r, m_bin=0.0)
    b = BINS[binkey]; c = bin_cg(b, fill_frac); lift = ROBOT['lift'] if lift is None else lift
    xb = ROBOT['pad_x'] - c['xf']; zb = c['z'] + lift
    m = r['m'] + c['m']
    x = (r['m'] * r['x'] + c['m'] * xb) / m; z = (r['m'] * r['z'] + c['m'] * zb) / m
    ib_yy = c['m'] * (b['D'] ** 2 + b['H'] ** 2) / 12.0
    ib_xx = c['m'] * (b['W'] ** 2 + b['H'] ** 2) / 12.0
    iyy = r['iyy'] + r['m'] * ((r['x'] - x) ** 2 + (r['z'] - z) ** 2) + ib_yy + c['m'] * ((xb - x) ** 2 + (zb - z) ** 2)
    ixx = r['ixx'] + r['m'] * (r['z'] - z) ** 2 + ib_xx + c['m'] * (zb - z) ** 2
    return dict(m=m, x=x, z=z, iyy=iyy, ixx=ixx, m_bin=c['m'], x_bin=xb, z_bin=zb, m_robot=r['m'])


# ----------------------------------------------------------------------------------------------- Rev G reference (for calibration only)
# Lean 95 kg tug + tilted bin, values from the project: world.py (track 0.69, wheel r 0.165), HANDOVER (95 kg, 48 deg),
# sim_g3.py (drive forcerange +/-60 N.m, kv 150, caster at +0.84 m, mu 0.6 for the step tows), bins_g5.py.
REVG = dict(
    tug_m=95.0, tug_cg=(0.098, 0.303),               # CG from revG/cad/mass_g3_sim_L95.json (sum of 141 rows)
    drive_r=0.165, drive_track=0.69, caster_x=0.84, caster_r=0.10, caster_track=0.50,
    hitch_L=1.35,                                    # drive axle -> bin axle when hooked and tilted (world.py BIN['L'])
    bin_tilt_deg=48.0, bin_wheel_r=0.10, bin_track=0.54,
)

if __name__ == '__main__':
    r = robot_mass(); print('robot', {k: round(v, 3) for k, v in r.items()})
    for k in BINS:
        for f in (0.0, 1.0):
            c = combined(k, f); print(k, f, {kk: round(vv, 3) for kk, vv in c.items()})
