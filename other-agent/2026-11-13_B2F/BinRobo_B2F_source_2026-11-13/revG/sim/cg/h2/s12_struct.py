#!/usr/bin/env python3
"""[H2] S12 structure hand calcs for Rev H2 and B2-F from the simulated peak wheel, comb (nib/lip-rim), pad and lift forces in h2/res.
Writes h2/res/s12_structure.json and h2/rep/s12_table.md. Every geometric value that is not in DESIGN_RevH2.md / DESIGN_B2.md /
work/revB2/assumptions_B2.md / revH2 cut and plate lists is marked ASSUMED in the output. Yield SF = yield / stress (or allowable / load).
Load levels: STATIC (G8 statics, 110 kg + CG), CARRY (max over smooth-ground runs: G2 climb, G4 e-stop, G5 towstab, G6 release, S7, perturbations),
EDGE (max over pothole runs and compliant-tyre kerb runs), COMB_ALL (max comb over every run incl. stalled trench and S10 contact variants).
Rigid-wheel impulses at sharp steps (14.7-22.1 kN) and wheel forces in the stalled trench runs (0.25-1.06 MN) are single-sample
rigid-contact artefacts and are reported, not used."""
import json, math, os, glob
H = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(H, 'res'); REP = os.path.join(H, 'rep'); os.makedirs(REP, exist_ok=True)
G = 9.81

def rhs(b, h, t):
    I = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12.0
    return dict(I=I, Z=I / (h / 2.0), Wt=2 * (b - t) * (h - t) * t)

def J(f): return json.load(open(os.path.join(RES, f)))

def cat(f, d):
    if 'trench' in f: return 'trench'
    if '_S5_' in f and 'step' in f: return 'step_rigid'
    if '_S5_' in f: return 'pothole'
    if '_S6_' in f: return 'ramp' if d.get('ramp') else ('kerb_compliant' if d.get('tyre', '').startswith('0.') else 'kerb_rigid')
    if 'step40' in f: return 'step_rigid'
    if 'static' in f: return 'static'
    return 'carry'

def peaks(pfx):
    P = {}
    for f in glob.glob(os.path.join(RES, pfx + '*.json')):
        b = os.path.basename(f)
        if 'grab_' in b or 'tipcalc' in b or 'tyrecal' in b: continue
        d = json.load(open(f))
        if 'peak' in d:
            pk = d['peak']; r = dict(wheel=pk.get('drive_tyre_N', [0])[0], comb=pk.get('nib_rim_N', [0])[0], pad=pk.get('pad_N', [0])[0], lift=pk.get('lift_N', [0])[0])
        elif 'lipF' in d: r = dict(wheel=d['drive_tyre'], comb=d['lipF'], pad=d['padF'], lift=d['liftF'])
        elif 'driveL' in d: r = dict(wheel=max(d['driveL'], d['driveR']), comb=0.0, pad=d.get('pad_N', 0), lift=d.get('lift_N', 0), castor=d['caster_sum'])
        else: continue
        c = cat(b, d)
        for k, v in r.items():
            key = (c, k)
            if key not in P or v > P[key][0]: P[key] = (v, b)
    return P

DES = {
 'H2': dict(name='Rev H2', rail=(50, 50, 3), rail_mat=235, mast=(50, 50, 3), x_mast=0.53, e_mast=0.3454 + 0.08, foot_lever=0.10, wall=3.0,
            comb=dict(t=6, h=75, teeth_cut=20, fy=355, src='640 x 75 x 6 S355, teeth to EN 840-1 Annex B (cut depth 20 mm ASSUMED)'),
            guide='rollers', roll_sp=0.30, rw=0.159, castor_h=0.32, castor_lever_plate=0.030, t_cap=80.0,
            castor_static_max_sum=None),
 'B2F': dict(name='B2-F', rail=(50, 50, 2), rail_mat=235, mast=(50, 50, 2), x_mast=0.49, e_mast=0.3454 + 0.08, foot_lever=0.06, wall=2.0,
            comb=dict(t=6, h=130, teeth_cut=0, fy=355, src='640 x 130 x 6 S355 with an 8 x 20 mm nib (full depth)'),
            guide='hgr15', block_pitch=0.20, rw=0.165, castor_h=0.245, castor_span=0.15, t_cap=80.0),
}
BOLT = {'M8': 36.6, 'M10': 58.0, 'M12': 84.3}; FYB88 = 640.0
E_STAR = 210000 / (2 * (1 - 0.3 ** 2)); P0_LIM_S235 = 1.67 * 235   # line-contact first yield (Tresca, p0 = 3.3 k)
C0_6202 = 3750.0; C0_HGH15 = 23470.0; ROLL_R, ROLL_L = 17.5, 11.0

def sec_for(Zreq, fy=235):
    cands = [(50, 50, 3), (50, 50, 4), (60, 60, 3), (60, 60, 4), (80, 40, 3), (80, 40, 4), (60, 60, 5), (80, 80, 4), (100, 50, 4), (80, 80, 5), (100, 50, 5), (100, 60, 5), (120, 60, 5), (100, 100, 5)]
    for c in cands:
        if rhs(c[1], c[0], c[2])['Z'] >= Zreq: return '%dx%dx%d' % c
    return '>120x60x5'

out = {}; md = []
for pfx, D in DES.items():
    P = peaks(pfx + '_')
    g = lambda c, k: P.get((c, k), (0.0, '-'))
    W = {'static': g('static', 'wheel'), 'carry': g('carry', 'wheel'),
         'edge': max(g('pothole', 'wheel'), g('kerb_compliant', 'wheel')), 'rigid_step(info)': g('step_rigid', 'wheel'), 'trench(info)': g('trench', 'wheel')}
    combs = {c: g(c, 'comb') for c in ('carry', 'pothole', 'step_rigid', 'kerb_compliant', 'kerb_rigid', 'trench')}
    Cc = {'static': (110 * G, 'W bin 110 kg'), 'carry': g('carry', 'comb'), 'comb_all': max(combs.values())}
    pads = {'carry': g('carry', 'pad'), 'all': max(g(c, 'pad') for c in ('carry', 'pothole', 'step_rigid', 'kerb_compliant', 'kerb_rigid', 'trench'))}
    lift = max(g(c, 'lift') for c in ('carry', 'pothole', 'step_rigid', 'kerb_compliant', 'kerb_rigid', 'trench'))
    R = dict(loads=dict(wheel={k: [round(v[0]), v[1]] for k, v in W.items()}, comb={k: [round(v[0]), v[1]] for k, v in Cc.items()},
                        comb_by_case={k: [round(v[0]), v[1]] for k, v in combs.items()}, pad={k: [round(v[0]), v[1]] for k, v in pads.items()}, lift=[round(lift[0]), lift[1]]))
    rows = []
    # 1 side rail: simply supported drive axle -> castor, load at the mast foot; M = F_wheel * x_mast (statics.py model), per rail
    s = rhs(*D['rail'])
    for lev in ('static', 'carry', 'edge', 'rigid_step(info)'):
        F = W[lev][0]; M = F * D['x_mast']; sig = M * 1e3 / s['Z']; sf = D['rail_mat'] / sig
        rows.append(dict(item='side rail %dx%dx%d S235' % D['rail'], level=lev, load_N=round(F), M_Nm=round(M), stress_MPa=round(sig, 1), SF=round(sf, 2),
                         fix=None if sf >= 2 or 'info' in lev else 'S235 %s (Z >= %d mm3)' % (sec_for(2 * M * 1e3 / 235), 2 * M * 1e3 / 235)))
    # 2 mast foot: M = F_comb * e, two uprights; upright bending at the foot and foot bolts (2 per tension row, lever foot_lever) through the RHS wall
    sm = rhs(*D['mast'])
    for lev in ('static', 'carry', 'comb_all'):
        F = Cc[lev][0]; M = F * D['e_mast']; Mu = M / 2; sig = Mu * 1e3 / sm['Z']; sf = 235 / sig
        rows.append(dict(item='mast upright at foot %dx%dx%d S235' % D['mast'], level=lev, load_N=round(F), M_Nm=round(Mu), stress_MPa=round(sig, 1), SF=round(sf, 2),
                         fix=None if sf >= 2 else 'S235 %s' % sec_for(2 * Mu * 1e3 / 235)))
        Tb = Mu / D['foot_lever'] / 2
        sfb = BOLT['M10'] * FYB88 / Tb
        pull = math.pi * 20 * D['wall'] * 0.577 * 235          # washer 20 mm punching through the RHS wall
        rows.append(dict(item='mast-foot bolts M10 8.8 (ASSUMED 2 per row, lever %.0f mm)' % (1000 * D['foot_lever']), level=lev, load_N=round(Tb), M_Nm=round(Mu), stress_MPa=round(Tb / BOLT['M10'], 1), SF=round(sfb, 2),
                         fix=None if sfb >= 2 else 'M12 8.8 or a longer gusset'))
        rows.append(dict(item='  bolt pull-through %.0f mm RHS wall' % D['wall'], level=lev, load_N=round(Tb), M_Nm=None, stress_MPa=None, SF=round(pull / Tb, 2),
                         fix=None if pull / Tb >= 2 else 'through-plates / crush tubes, or 5 mm foot plates welded to the upright'))
    # 3 comb plate (in-plane bending about the pivot block, 100 mm wide; load uniform on 580 mm receiver) and pivot pin
    cb = D['comb']; hn = cb['h'] - cb['teeth_cut']; Zc = cb['t'] * hn ** 2 / 6.0
    for lev in ('carry', 'comb_all'):
        F = Cc[lev][0]
        for case, arm in (('symmetric', 240 ** 2 / 2 / 580.0), ('one half at the roll stop', 120.0)):
            M = F * arm / 1000; sig = M * 1e3 / Zc; sf = cb['fy'] / sig
            rows.append(dict(item='comb plate (%s)' % case, level=lev, load_N=round(F), M_Nm=round(M), stress_MPa=round(sig, 1), SF=round(sf, 2),
                             fix=None if sf >= 2 else 'plate 8 mm or net depth >= %.0f mm' % math.sqrt(6 * 2 * M * 1e3 / (cb['fy'] * cb['t']))))
        for d in (16, 20):
            sig = F * 20 / (math.pi * d ** 3 / 32); sf = FYB88 / sig       # pin cantilever 20 mm from the bush face (ASSUMED)
            rows.append(dict(item='comb pivot pin D%d 8.8 (ASSUMED, 20 mm cantilever)' % d, level=lev, load_N=round(F), M_Nm=round(F * 0.02), stress_MPa=round(sig, 1), SF=round(sf, 2), fix=None if sf >= 2 else 'pin D20 8.8 or double shear'))
    # 4 lift guide
    for lev in ('static', 'carry', 'comb_all'):
        F = Cc[lev][0]; M = F * D['e_mast']
        if D['guide'] == 'rollers':
            Pb = M / D['roll_sp'] / 2
            rows.append(dict(item='carriage roller 6202-2RS, C0 3.75 kN', level=lev, load_N=round(Pb), M_Nm=round(M), stress_MPa=None, SF=round(C0_6202 / Pb, 2),
                             fix=None if C0_6202 / Pb >= 2 else 'two rollers per station or C0 >= %.1f kN; roller rows 0.45 m apart' % (2 * Pb / 1000)))
            p0 = math.sqrt(Pb * E_STAR / (math.pi * ROLL_R * ROLL_L)); sfc = (P0_LIM_S235 / p0) ** 2
            rows.append(dict(item='  roller line contact on S235 tube face', level=lev, load_N=round(Pb), M_Nm=None, stress_MPa=round(p0), SF=round(sfc, 2),
                             fix=None if sfc >= 2 else 'hardened track strip (>= 50 HRC) on each upright face'))
        else:
            Pb = M / D['block_pitch'] / 2
            rows.append(dict(item='HGH15CA block, C0 23.47 kN (pitch 0.20 m ASSUMED)', level=lev, load_N=round(Pb), M_Nm=round(M), stress_MPa=None, SF=round(C0_HGH15 / Pb, 2),
                             fix=None if C0_HGH15 / Pb >= 2 else 'block pitch 0.30 m or HGH20'))
            Tb = Pb / 2; sfr = 8.78 * FYB88 / Tb   # 2 rail screws M4 8.8 per block length carry the pull-off half
            rows.append(dict(item='  HGR15 rail screws M4 8.8 (2 per block)', level=lev, load_N=round(Tb), M_Nm=None, stress_MPa=round(Tb / 8.78), SF=round(sfr, 2),
                             fix=None if sfr >= 2 else 'M4 12.9 into a 10 mm backing flat (not the 2 mm wall), 60 mm pitch'))
    # 5 castor outriggers: vertical 3 g on the worst static castor share; kerb strike = full drive torque cap into both castors
    cst = max(J(f)['caster_sum'] for f in glob.glob(os.path.join(RES, pfx + '_static_*.json')))
    Fv = 3 * cst / 2; Fh = 2 * D['t_cap'] / D['rw'] / 2; Mk = Fh * D['castor_h']
    if pfx == 'H2':
        Zp = 150 * 8 ** 2 / 6.0
        rows.append(dict(item='castor outrigger plate 8 mm S355 (vertical 3 g)', level='static x3', load_N=round(Fv), M_Nm=round(Fv * D['castor_lever_plate']), stress_MPa=round(Fv * D['castor_lever_plate'] * 1e3 / Zp, 1), SF=round(355 / (Fv * D['castor_lever_plate'] * 1e3 / Zp), 2), fix=None))
        rows.append(dict(item='castor outrigger plate 8 mm S355 (kerb strike, 80 N m)', level='kerb', load_N=round(Fh), M_Nm=round(Mk), stress_MPa=round(Mk * 1e3 / Zp, 1), SF=round(355 / (Mk * 1e3 / Zp), 2), fix=None if 355 / (Mk * 1e3 / Zp) >= 2 else '10 mm plate'))
        wt = rhs(50, 50, 3)['Wt']
        rows.append(dict(item='nose cross-member 50x50x3 torsion (kerb strike)', level='kerb', load_N=round(Fh), M_Nm=round(Mk), stress_MPa=round(Mk * 1e3 / wt, 1), SF=round(0.577 * 235 / (Mk * 1e3 / wt), 2), fix=None))
    else:
        s2 = rhs(50, 50, 2)
        rows.append(dict(item='nose cross-member 50x50x2 bending (vertical 3 g, castor 0.15 m from the drop plate)', level='static x3', load_N=round(Fv), M_Nm=round(Fv * D['castor_span']), stress_MPa=round(Fv * D['castor_span'] * 1e3 / s2['Z'], 1), SF=round(235 / (Fv * D['castor_span'] * 1e3 / s2['Z']), 2), fix=None))
        tau = Mk * 1e3 / s2['Wt']
        rows.append(dict(item='nose cross-member 50x50x2 torsion (kerb strike, 80 N m)', level='kerb', load_N=round(Fh), M_Nm=round(Mk), stress_MPa=round(tau, 1), SF=round(0.577 * 235 / tau, 2), fix=None))
        Zd = 100 * 6 ** 2 / 6.0; Md = Fh * 0.12
        rows.append(dict(item='rail drop plate 6 x 100 S355 (ASSUMED size; kerb strike, 0.12 m drop)', level='kerb', load_N=round(Fh), M_Nm=round(Md), stress_MPa=round(Md * 1e3 / Zd, 1), SF=round(355 / (Md * 1e3 / Zd), 2), fix=None if 355 / (Md * 1e3 / Zd) >= 2 else '8 mm plate'))
    # bin side, for information: receiver ledge (gate-model 30 x 8 HDPE, load at 26 mm, DESIGN_B2 s.9 formula), HDPE yield 22.5 MPa
    for lev in ('carry', 'comb_all'):
        F = Cc[lev][0]; w = F / 580.0; sig = 6 * w * 26 / 8 ** 2
        rows.append(dict(item='(bin) receiver ledge, HDPE, gate-model section', level=lev, load_N=round(F), M_Nm=None, stress_MPa=round(sig, 1), SF=round(22.5 / sig, 2), fix=None if 22.5 / sig >= 2 else 'comb buffer to cut the peak; measure real receivers (B0b/B1)'))
    R['rows'] = rows; R['castor_static_max_sum_N'] = cst; out[pfx] = R
    md.append('\n### %s\n\nLoads used: wheel static %d N, carry %d N (%s), edge %d N (%s); rigid-step impulse %d N and stalled-trench %d N not used. Comb static %d N, carry %d N, all runs %d N (%s). Pad max %d N; lift max %d N (actuator cap).\n'
              % (D['name'], W['static'][0], W['carry'][0], W['carry'][1], W['edge'][0], W['edge'][1], W['rigid_step(info)'][0], W['trench(info)'][0],
                 Cc['static'][0], Cc['carry'][0], Cc['comb_all'][0], Cc['comb_all'][1], pads['all'][0], lift[0]))
    md.append('| element | load level | force (N) | M (N m) | stress (MPa) | SF | meets 2? / fix |\n|---|---|---|---|---|---|---|')
    for r in rows:
        md.append('| %s | %s | %s | %s | %s | %.2f | %s |' % (r['item'], r['level'], r['load_N'], '-' if r['M_Nm'] is None else r['M_Nm'], '-' if r['stress_MPa'] is None else r['stress_MPa'], r['SF'],
                                                          'yes' if r['SF'] >= 2 else ('info' if 'info' in str(r['level']) else 'NO: ' + str(r['fix']))))
json.dump(out, open(os.path.join(RES, 's12_structure.json'), 'w'), indent=1)
open(os.path.join(REP, 's12_table.md'), 'w').write('\n'.join(md) + '\n')
print('\n'.join(md))
