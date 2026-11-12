#!/usr/bin/env python3
"""Rev H2: how a bin hangs from the comb, and how much lift it needs. Static geometry, no dynamics. Writes ../results/hang.json.

The bin hangs from the comb seat line under its frontal receiver. Its centre of gravity is behind that line, so the base swings
towards the mast until the front wall meets the rest pad. If the pad face is exactly where the wall is, the bin hangs plumb. If the
pad sits back by e, the bin rotates by atan(e / pad_drop) and its wheels drop. The lift must cover that drop plus the wanted
clearance. Wall positions are scaled from manufacturer drawings (params.WALL_SETBACK): measure the real bins.

Also reproduces the other agent's 11-12 deg hang for Rev H: their bin hull puts a 170 mm taper on the FRONT wall (simH.py line 132,
xfb = xf + 170 mm), which the manufacturer drawings show on the REAR (wheel) wall; the front wall tapers about 35 mm."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import params as P
R = P.ROBOT; G = P.G


def hang(binkey, pad_setback, pad_drop=None, wall=None, clear=None):
    b = P.BINS[binkey]; pad_drop = R['pad_drop'] if pad_drop is None else pad_drop
    s_wall = P.WALL_SETBACK[binkey][0] if wall is None else wall
    e = max(s_wall - pad_setback, 0.0)                               # gap between wall and pad when the bin stands plumb on the comb
    th = math.atan(e / pad_drop)
    zc = b['comb'] if b['comb'] else sum(P.COMB_UNKNOWN_BAND) / 2    # comb seat height, bin standing
    Lw = P.AXLE_TO_FRONT[binkey] + P.COMB_SEAT_OFFSET; r = b['wheel'] / 2
    drop = Lw * math.sin(th) - (zc - r) * (1 - math.cos(th))         # bin-wheel drop when the bin swings by th about the comb line
    clear = R['wheel_clear_min'] if clear is None else clear
    lift_needed = clear + drop; comb_top = zc + lift_needed
    m = b['empty'] + b['fill_full']; cg = P.bin_cg(b, 1.0)
    d_cg = cg['xf'] + P.COMB_SEAT_OFFSET
    return dict(bin=b['name'], wall_setback_mm=round(s_wall * 1000), pad_setback_mm=round(pad_setback * 1000), blocked_mm=round(max(pad_setback - s_wall, 0) * 1000),
                hang_deg=round(math.degrees(th), 1), wheel_drop_mm=round(drop * 1000), lift_for_clearance_mm=round(lift_needed * 1000),
                comb_height_needed_m=round(comb_top, 3), within_travel=bool(comb_top <= R['comb_z_max'] and zc - 0.105 >= R['comb_z_min']),
                clearance_at_100mm_lift_mm=round((0.100 - drop) * 1000), pad_force_full_N=round(m * G * d_cg / pad_drop), gross_kg=round(m, 1))


def main():
    out = dict(pad_setback_default_mm=round(R['pad_setback'] * 1000), pad_drop_mm=round(R['pad_drop'] * 1000), wheel_clear_target_mm=round(R['wheel_clear_min'] * 1000),
               comb_travel_m=[R['comb_z_min'], R['comb_z_max']])
    out['as_designed'] = [hang(k, R['pad_setback']) for k in P.BINS]
    # sensitivity: pad set wrong or wall not as drawn (the two only matter as their difference)
    sens = []
    for k in ('ESE240SL', 'ESE240SL250', 'ESE240CL', 'WEB140'):
        for wall in (0.015, 0.030, 0.045, 0.060, 0.080):
            sens.append(dict(hang(k, R['pad_setback'], wall=wall), case='wall setback %d mm' % round(wall * 1000)))
    out['sensitivity'] = sens
    # what the lift travel can absorb: largest wall-to-pad gap that still gives the target clearance, per bin
    lim = []
    for k in P.BINS:
        e = 0.0
        while e < 0.20 and hang(k, 0.0, wall=e + 0.001)['within_travel']: e += 0.001
        lim.append(dict(bin=P.BINS[k]['name'], largest_gap_mm=round(e * 1000), hang_deg=round(math.degrees(math.atan(e / R['pad_drop'])), 1)))
    out['travel_limit'] = lim
    # the other agent's Rev H result, reproduced: flush pad 0.45 m below the comb, hull with 170 mm front-wall taper over the body height
    b = P.BINS['ESE240SL']; body_h = 1.017 - 0.10 + 0.10                       # their hull: rim at the bar height, base 100 mm below the axle
    swing = 0.170 * (0.45 / body_h) + 0.004                                    # wall behind the nib at pad height (+ their 4 mm ToF stand-off)
    th = math.atan(swing / 0.45); Lw = P.AXLE_TO_FRONT['ESE240SL']
    out['other_agent_revH_model'] = dict(front_wall_taper_mm=170, pad='flush, 0.45 m below the comb', swing_at_pad_mm=round(swing * 1000),
                                         hang_deg=round(math.degrees(th), 1), wheel_drop_mm=round((Lw * math.sin(th) - 0.905 * (1 - math.cos(th))) * 1000),
                                         their_mujoco_result='11.2-12.5 deg hang, about 75 mm of swing (COMPARE_B1_vs_RevH.md s.4 and s.5.1)',
                                         drawings_show='front wall taper about 35 mm over the body height (Craemer 240 side elevation, scaled); the large taper is on the rear wall')
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'hang.json'), 'w'), indent=1)
    for r in out['as_designed']: print(r)
    print(out['travel_limit']); print(out['other_agent_revH_model'])


if __name__ == '__main__':
    main()
