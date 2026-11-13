#!/usr/bin/env python3
"""Rev G4 SITL report: revG/RESULTS_G4_sitl.md (ASCII) + .pdf (pandoc, pdflatex) from out/G4/*/result.json, out/G4/robust/<tag>/,
out/G4/report/*.png.  Usage: report_g4.py [robust_tag]"""
import json, os, sys, glob, math, collections, subprocess, shutil, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); G4 = os.path.join(ROOT, 'out', 'G4'); PROJ = os.path.join(ROOT, '..')
REVG = os.path.join(PROJ, 'revG'); FIG = os.path.join(REVG, 'fig_g4'); os.makedirs(FIG, exist_ok=True)
sys.path.insert(0, HERE)
import scenarios as SC
from companion import clock_str, parse_clock, VSTOP, UTURN_G4
from g4_features import DropLayout, BinCalendar, CFG, DropAreas, KL_GAP, RADAR
TAG = sys.argv[1] if len(sys.argv) > 1 else 'G4'

def load(p):
    try: return json.load(open(p))
    except Exception: return None
R = {sc: load(os.path.join(G4, sc, 'result.json')) for sc in SC.ALL_G4}; R = {k: v for k, v in R.items() if v}
G3 = {x['scenario']: x for x in (load(os.path.join(ROOT, 'out', 'regress_G3.json')) or [])}
ROB = collections.defaultdict(list)
for p in sorted(glob.glob(os.path.join(G4, 'robust', TAG, '*', 'result.json'))):
    r = load(p)
    if r: ROB[os.path.basename(os.path.dirname(p)).rsplit('_seed', 1)[0]].append(r)
def cls(r):
    exp = r.get('expect', 'pass'); ok = r['result'] == exp
    if r['result'] == 'pass' and (r.get('metrics') or {}).get('placement_oot'): return False, 'PASS but PLACEMENT >0.6 m'   # G4: truth placement tolerance
    if r['result'] == 'pass': return ok, 'PASS'
    if r['result'] in ('alert', 'stopped'): return ok, 'EXPECTED ALERT' if ok else 'ALERT (unexpected)'
    return ok, 'FAIL (expected)' if ok else 'FAIL'
def f(v, fmt='%.2f', none='-'):
    return none if v is None else (fmt % v)
def esc(t): return str(t).replace('|', '/').replace('\n', ' ')
def ascii_(t):
    rep = {'\u2013': '-', '\u2014': '-', '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"', '\u00b0': ' deg', '\u2192': '->', '\u00b1': '+-', '\u2264': '<=', '\u2265': '>=', '\u00d7': 'x'}
    for a, b in rep.items(): t = t.replace(a, b)
    return t.encode('ascii', 'replace').decode('ascii')
md = []; W = md.append

# ---------------- integrity of the frozen G3 code ----------------
chk = subprocess.run(['md5sum', '-c', 'out/final_g3_code.md5'], cwd=ROOT, capture_output=True, text=True).stdout.strip().splitlines()
g3_ok = all(l.endswith(': OK') for l in chk) and len(chk) > 0

# ---------------- headline numbers ----------------
n_ok = sum(cls(r)[0] for r in R.values()); n_all = len(R); missing = [s for s in SC.ALL_G4 if s not in R]
rob_n = sum(len(v) for v in ROB.values()); rob_ok = sum(cls(r)[0] for v in ROB.values() for r in v)
legal = [(r.get('legal_min_inside_m'), s) for s, r in R.items() if r.get('legal_min_inside_m') is not None]
legal += [(r.get('legal_min_inside_m'), '%s seed %s' % (s, r.get('seed'))) for s, v in ROB.items() for r in v if r.get('legal_min_inside_m') is not None]
lmin = min(legal) if legal else (None, '')
breaches = [s for s, r in R.items() if r['fence_breach']] + ['%s seed %s' % (s, r.get('seed')) for s, v in ROB.items() for r in v if r['fence_breach']]
hed = [(r.get('hedge_overlap_m') or 0.0, s) for s, r in R.items()] + [(r.get('hedge_overlap_m') or 0.0, '%s seed %s' % (s, r.get('seed'))) for s, v in ROB.items() for r in v]
hmax = max(hed) if hed else (0, '')
# keep-left aggregate over all regression runs
agg = {'down': [], 'up': []}
for s, r in R.items():
    for k in ('down', 'up'):
        q = (r.get('keep_left') or {}).get(k)
        if q and q['dist_m'] >= 30: agg[k].append((s, q))
def kl_sum(lst):
    if not lst: return None
    d = sum(q['dist_m'] for _, q in lst); mean = sum(q['mean'] * q['dist_m'] for _, q in lst) / d
    pct = sum(q['pct_in_0p3_0p5'] * q['dist_m'] for _, q in lst) / d; mn = min((q['min'], s) for s, q in lst)
    sd = math.sqrt(sum((q['sd'] ** 2 + (q['mean'] - mean) ** 2) * q['dist_m'] for _, q in lst) / d)
    return dict(dist=d, mean=mean, min=mn[0], min_at=mn[1], pct=pct, sd=sd, n=len(lst))
KL = {k: kl_sum(v) for k, v in agg.items()}
# 3-bin evening
a20, b20, c20 = R.get('s20a_three_bin_drop'), R.get('s20b_three_bin_pickup'), R.get('s20c_three_bin_pickup_noheat')
margin = (b20 or {}).get('metrics', {}).get('deadline_margin_min'); pick_end = (b20 or {}).get('metrics', {}).get('finish_clock')
VS = [(s, v) for s in ('s23a_vehicle_oncoming', 's23b_vehicle_behind', 's23c_vehicle_passing', 's23d_no_false_stop') if s in R for v in [R[s]]]

json.dump(dict(regress_ok=n_ok, regress_n=n_all, robust_ok=rob_ok, robust_n=rob_n, margin=margin, pick_end=pick_end,
               kl=None if not KL['down'] else dict(mean=(KL['down']['mean'] + (KL['up'] or KL['down'])['mean']) / 2, min=min(KL['down']['min'], (KL['up'] or KL['down'])['min']))),
          open(os.path.join(G4, 'report', 'g4_summary.json'), 'w'), indent=1)

W('---\ntitle: "Bin Tug - work package G4: SITL results (simulation only)"\ndate: "%s"\ngeometry: margin=1.5cm\nfontsize: 9pt\n'
  'header-includes:\n  - \\usepackage{longtable}\n  - \\renewcommand{\\arraystretch}{1.05}\n---\n' % dt.date.today().isoformat())
W('**Everything below is a software-in-the-loop simulation** (real ArduPilot Rover 4.6.2 firmware in JSON SITL, Python 2.5D world of Brian\'s 633 m lane, Pi companion state machine). Nothing has been built or tested on hardware. Numbers marked ASSUMED are model inputs, not measurements.\n')
W('G4 code is a copy: `sitl/scripts_g4/` + `sitl/params/bintug_g4.parm` + `sitl/config_g4/`; outputs in `sitl/out/G4/`. The frozen G3 code and results in `sitl/scripts/`, `sitl/out/` were not changed: md5 check of `out/final_g3_code.md5` = **%s** (%s).\n'
  % ('OK' if g3_ok else 'FAILED', '; '.join(l.split('/')[-1] for l in chk)))

W('# 1. Summary\n')
W('| Item | Result |\n|---|---|')
W('| Full regression (%d scenarios) | **%d / %d as expected**%s |' % (len(SC.ALL_G4), n_ok, n_all, (' - MISSING: ' + ', '.join(missing)) if missing else ''))
W('| Robustness, %d scenarios x seeds 7/11/23/42 | **%d / %d as expected** |' % (len(SC.ROBUST_G4), rob_ok, rob_n))
if b20: W('| 3-bin evening, real pickup (s20a drop -> overnight dock recharge -> s20b pickup) | %s, pickup finished **%s**, margin to 21:00 **%s min** |' % (b20['result'].upper(), pick_end, f(margin, '%.1f')))
for k in ('down', 'up'):
    q = KL.get(k)
    if q: W('| Keep-left gap, tug left side to left lane edge, %s (%.0f m over %d runs) | mean **%.3f m**, SD %.3f, min **%.3f m** (%s), %.0f %% of distance inside 0.3-0.5 m |' % (k, q['dist'], q['n'], q['mean'], q['sd'], q['min'], q['min_at'], q['pct']))
W('| Vehicle-approach stop (s23a-c) | %s |' % '; '.join('%s: %s' % (s[4:], ', '.join('%s %s -> hold %.0f s, min gap %.2f m' % (v_['side'], v_['crit'].split(' (')[0], v_['hold_s'], v_['min_truth_gap_m']) for v_ in r['vehicle_stops']) or 'no stop') for s, r in VS))
W('| Geofence breaches (tug axle corridor), all runs | %d %s |' % (len(breaches), ('(' + ', '.join(breaches) + ')') if breaches else ''))
W('| Closest footprint to the assumed private boundary | %s m inside (%s) |' % (f(lmin[0]), lmin[1]))
W('| Max footprint overlap with a modelled hedge line, all runs | %.2f m (%s) |' % hmax)
W('')

W('# 2. Corrections to the G3 report\n')
W('* **The G3 "3-bin margin 79 min" was invalid.** It was computed in `finish()` whenever an s20b run ended, and G3 s20b ended at 19:40 because the pinch-zone check refused the 2nd release and the tug held on the pad - 2 of 3 bins were not home. A margin is only reported in G4 when all bins of the evening are back and the tug has docked (`bins_left` empty, result pass).')
W('* **"1 geofence breach" vs "0.37 m inside" are two different fences.** `fence_breach` flags the tug AXLE leaving the lane corridor (half-width 1.9 m + 0.6 m slack) or coming within 6.6 m of the road centre-line; `legal_min_inside_m` is the closest FOOTPRINT point to the assumed private boundary (6.0 m from the road centre-line). The G3 breach (s10a) was sideways: the axle reached lat -2.51 m at L-14.1 m, i.e. **into the right-hand hedge line before the bell-mouth**, while 0.93 m inside the legal boundary. G4 checked all G3 mouth drops: every one put the tug body 0.65-0.85 m past the modelled right hedge line at L-13 to L-15 (approach waypoints at lat -2.3 m start 15 m before the leg end; the world has no hedge collision, so nothing stopped it).')
W('* **G4 fix:** approach waypoints are clamped to |lat| <= 1.55 m before the mouth, and the mouth U-turn now starts inside the bell-mouth (L-%.1f m, lat %.1f m, commanded R %.2f m) with a closed-loop line capture onto lat +%.2f m for the last 95 deg (an offline kinematic sweep `sitl/work_uturn_study2.py` found no hedge overlap for this start). New metric `hedge_overlap_m` on every run (summary above).' % (UTURN_G4['start_from_end'], UTURN_G4['lat'], UTURN_G4['R'], UTURN_G4['line']))
W('* G3 yard U-turns were open-loop and ended 0.4-1.1 m off the home line, which is why s10b/s20c placed the 2nd bin next to the first and the pinch check then refused. G4 adds the same line capture to the yard U-turn.\n')

W('# 3. Task 1 - pinch zone and the three-bin evening\n')
W('Rule (companion `pinch_eval`): anything unmapped within 1.5 m of the tug sides/front still blocks a release. G4 exempts a lidar cluster only if it is **bin-sized (0.25-1.0 m), stationary for >= 1.5 s and centred within 0.6 m of an occupied programmed slot** (another of Brian\'s bins on its home/pad spot or one released tonight). A person touching that bin merges with it (> 1.0 m), a person apart from it is a separate cluster off the slot, and a vehicle is > 1.45 m, so none of them is exempt.\n')
W('| Scenario | G3 | G4 result | Outcome | Slot exemptions used |\n|---|---|---|---|---|')
for s in ('s10a_two_bin_drop', 's10b_two_bin_pickup', 's20a_three_bin_drop', 's20b_three_bin_pickup', 's20c_three_bin_pickup_noheat', 's16b_release_blocked', 's16c_release_person_by_bin'):
    r = R.get(s); g = G3.get(s if s != 's20c_three_bin_pickup_noheat' else 's20c_three_bin_pickup_heated')
    if not r: W('| %s | %s | NOT RUN | | |' % (s, g['cls'] if g else '-')); continue
    W('| %s | %s | %s | %s | %d |' % (s, g['cls'] if g else 'new', cls(r)[1], esc(r['outcome'])[:70], len(r['metrics'].get('slot_exempt', []))))
W('')
if a20 and b20:
    oc = (b20['metrics'].get('overnight_charge') or [{}])[0]
    W('**Three-bin evening (brown + green + black, +0.5 C, 12 Ah pack, dock pack heater ASSUMED 15 W):**\n')
    W('| Step | Value |\n|---|---|')
    W('| s20a drop: first motion / finished | %s / %s, %s |' % (a20['metrics'].get('first_motion_clock'), a20['metrics'].get('finish_clock'), a20['result'].upper()))
    W('| s20a energy from the pack / SOC end | %.1f Wh / %.0f %% (pack %.1f C at the end) |' % (a20['pack_wh_out'], 100 * a20['soc_end'], a20.get('pack_c_end') or 0))
    W('| Overnight on the dock (RTC sleep) | heater warm-up %s h, charge %s h, %s Wh into the pack, SOC %s -> %s; mains ~%s Wh |' % (oc.get('warm_h'), oc.get('charge_h'), oc.get('wh_into_pack'), oc.get('soc_start'), oc.get('soc_end'), oc.get('mains_wh')))
    W('| s20b pickup: wake / finished | %s / **%s**, %s |' % (b20['clock_start'], pick_end, b20['result'].upper()))
    W('| s20b energy / SOC end | %.1f Wh / %.0f %% |' % (b20['pack_wh_out'], 100 * b20['soc_end']))
    W('| **Margin to the 21:00 bye-law deadline** | **%s min** (trip time measured %s min) |' % (f(margin, '%.1f'), b20['metrics'].get('trip_min_meas')))
    if c20: W('| s20c: same start, NO pack heater (pack +0.5 C cannot charge) | %s - %s |' % (c20['result'].upper(), esc(c20['outcome'])))
    W('')
    W('Placement of each bin (truth vs programmed pose):\n')
    W('| Run | Spot | Bin | Error m | Yaw error deg |\n|---|---|---|---|---|')
    for s in ('s10a_two_bin_drop', 's10b_two_bin_pickup', 's20a_three_bin_drop', 's20b_three_bin_pickup', 's22a_calendar_week_a', 's22b_calendar_week_b'):
        for p in (R.get(s) or {}).get('metrics', {}).get('placement', []): W('| %s | %s | %s | %.2f | %+.0f |' % (s, p['spot'], p['bin'], p['err_m'], p['yaw_err_deg']))
    W('')

W('# 4. New features\n')
W('## a) Teach and repeat\n')
t21, r21 = R.get('s21a_teach_route'), R.get('s21b_repeat_drop')
W('Teach mode (app/RC): the operator hooks the bin, presses MARK HOME, drives the lane, MARK WAIT at the junction wait point, turns in the mouth, places the bin and presses MARK DROP (= release), drives back, PARK. The companion records its EKF track every 1 m plus the exact home / drop poses into `out/G4/routes/route_black.json`; a validator checks fence, hedge clearance and private ground before the route may be used. Repeat: house grab at the taught home pose, AUTO legs on the taught track (resampled every 4 m), junction wait, U-turn, release at the taught drop pose. In the SITL the operator\'s joystick is a scripted stand-in (truth pose + 0.12 m wobble).\n')
if t21:
    m = t21['metrics'].get('teach', {})
    W('| Teach (s21a) | %s; %s down + %s up points; recorded home pose error %s m, drop pose error %s m / %s deg (vs truth); validator %s |' % (
        t21['result'].upper(), m.get('n_down'), m.get('n_up'), m.get('home_err_m'), m.get('drop_err_m'), m.get('drop_yaw_err_deg'), 'OK' if (m.get('validation') or {}).get('ok') else esc(m.get('validation'))))
if r21:
    pl = [p for p in r21['metrics'].get('placement', []) if p['spot'] == 'taught drop']
    W('| Repeat at night (s21b) | %s - %s; placed %s from the taught drop pose |' % (r21['result'].upper(), esc(r21['outcome']), ('%.2f m / %+.0f deg' % (pl[0]['err_m'], pl[0]['yaw_err_deg'])) if pl else '-'))
W('')
W('## b) Bin calendar (alternate weeks)\n')
cal = BinCalendar()
W('`config_g4/bin_calendar.json` (EXAMPLE - fill from the collector): anchor %s = week %s, collection on %s, week A %s, week B %s, drop from %s (earliest %s) on the eve, pickup from %s, deadline %s, skip dates %s. The companion resolves the evening -> bins, orders them (outermost home spot first), assigns pads from the layout and sleeps until the drop time.\n'
  % (cal.d['anchor_date'], cal.d['anchor_week'], cal.d['collection_weekday'], '+'.join(cal.d['weeks']['A']), '+'.join(cal.d['weeks']['B']), cal.d['drop']['time'], cal.d['drop']['earliest'], cal.d['pickup']['time'], cal.d['pickup']['deadline'], ', '.join(cal.d.get('skip_dates', []))))
W('| Collection | Week | Bins | Drop | Pickup |\n|---|---|---|---|---|')
for c in cal.table(dt.date(2026, 11, 9), 8):
    W('| %s %s | %s | %s | %s | %s |' % (c.get('weekday', ''), c['date'], c.get('week', '-'), '+'.join(c['bins']) if c['bins'] else 'SKIPPED', c.get('drop_at', '-'), c.get('pickup_at', '-')))
W('')
for s in ('s22a_calendar_week_a', 's22b_calendar_week_b'):
    r = R.get(s)
    if r: c = r['metrics'].get('calendar', {}); W('* **%s**: %s - %s; evening %s -> week %s, bins %s, pads %s, first motion %s.' % (s, r['result'].upper(), esc(r['outcome']), c.get('evening'), (c.get('collection') or {}).get('week'), c.get('order'), c.get('pads'), r['metrics'].get('first_motion_clock')))
W('')
W('## c) Programmable drop layout per spot\n')
W('Per spot: position (s from the lane end, lat or `auto` from the hedge clearance), handle heading, minimum spacing to every other bin, minimum hedge clearance. The validator also checks private ground (>= 0.45 m), geofence, a 2.6 m dock corridor (only against spots still occupied when this one is picked up) and a >= 1.36 m pass corridor beside lane spots.\n')
import scenarios as _S
S = _S.site('real')
from world import TUG as _T
import numpy as _np
def _room(D, yaw, others):
    d = _np.array([math.cos(yaw), math.sin(yaw)])
    for t in _np.arange(0, 2.61, 0.25):
        p = _np.array(D) + d * t
        for sg in (-1, 1):
            q = p + sg * _np.array([-d[1], d[0]]) * (_T['half_w'] + 0.05)
            if S.hedge_dist(q) < 0.12 or not S.in_fence(q, margin=-0.15, ko=False): return False
            if any(_np.linalg.norm(q - o) < 0.65 for o in others): return False
    return True
for fn in ('drop_layout_default.json', 'drop_layout_custom.json', 'drop_layout_bad.json'):
    ok, rows = DropLayout(os.path.join(CFG, fn)).validate(S, _room)
    W('**%s** - %s\n' % (fn, 'VALID' if ok else 'REJECTED'))
    W('| Spot | L-s m | lat m | hdg deg | legal m | hedge m (req) | min gap m (req) | pass corr. m | dock corr. | OK / why |\n|---|---|---|---|---|---|---|---|---|---|')
    for r_ in rows: W('| %s | %.1f | %.2f | %+.0f | %.2f | %.2f (%.2f) | %s (%.1f) | %s | %s | %s |' % (r_['spot'], r_['s_from_end'], r_['lat'], r_['heading_deg'], r_['legal_m'], r_['hedge_m'], r_['hedge_req'], f(r_['min_gap_m']), r_['spacing_req'], f(r_['pass_corridor_m']), 'yes' if r_['dock_corridor'] else 'NO', 'OK' if r_['ok'] else esc(r_['why'])))
    W('')
W('## d) Keep-left edge following\n')
W('Ireland drives on the left: on lane legs (s = 25 m to L-24 m) the waypoints run at the keep-left offset for the travel direction (target gap %.2f m between the tug\'s left side and the surveyed left lane edge, 1.80 m from the centre-line; the hedge is 0.25 m beyond), one every 2 m. Rover 4.6 path following goes through AR_PosControl (the NAVL1_* params do not exist in this firmware); with defaults the tracking SD was 0.21 m with a 0.13 m bias, so `bintug_g4.parm` sets PSC_POS_P 1.0, PSC_VEL_P 3.0, PSC_VEL_I 0.3 (3 short dev runs, `out/G4/t_kl*`). Gap measured from the truth pose, AUTO lane legs moving > 0.1 m/s, excluding the first/last 8 m of a leg, detours, holds and keep-out shifts. The lane edge is the surveyed one; real hedge irregularity is NOT modelled.\n' % KL_GAP)
W('| Scenario | dir | distance m | mean m | SD m | min m | max m | %% in 0.3-0.5 | towed bin mean / min m |\n|---|---|---|---|---|---|---|---|---|')
for k in ('down', 'up'):
    for s, q in sorted(agg[k], key=lambda x: x[0]):
        W('| %s | %s | %.0f | %.3f | %.3f | %.3f | %.3f | %.0f | %s / %s |' % (s, k, q['dist_m'], q['mean'], q['sd'], q['min'], q['max'], q['pct_in_0p3_0p5'], f(q.get('bin_mean'), '%.2f'), f(q.get('bin_min'), '%.2f')))
for k in ('down', 'up'):
    q = KL.get(k)
    if q: W('| **ALL (%s)** | %s | %.0f | **%.3f** | %.3f | **%.3f** | | %.0f | |' % (q['n'], k, q['dist'], q['mean'], q['sd'], q['min'], q['pct']))
W('\n![Keep-left gap along the lane (s10b, both directions)](fig_g4/g4_keepleft.png){width=95%}\n')
W('## e) Vehicle-approach stop (front + rear 24 GHz radar + lidar)\n')
W('Model of an HLK-LD2451-class module (+-%.0f deg, %.0f m, min radial speed %.2f m/s, 10 Hz; noise ASSUMED). Trigger: vehicle-like target moving over the ground toward the tug (ego-motion compensated), closing > %.1f m/s and range < %.1f m or TTC < %.0f s within %.0f m; a closing track lost at short range is coasted for 2.5 s. Action: HOLD (spring brakes), beacon, speaker clip. Resume: nothing closing within %.0f m and no vehicle-sized lidar object within 4 m for %.0f s (0.3 m/s creep if a vehicle is still near). Lane legs only.\n'
  % (RADAR['fov_deg'], RADAR['rmax_vehicle'], RADAR['v_min'], VSTOP['closing'], VSTOP['r_stop'], VSTOP['ttc_s'], VSTOP['r_ttc'], VSTOP['r_clear'], VSTOP['clear_s']))
W('| Scenario | Result | Vehicle | Trigger side / criterion | Radar range m | Closing m/s | Stop time s / dist m | Hold s | Resume | Min gap vehicle-tug m (bin) |\n|---|---|---|---|---|---|---|---|---|---|')
for s, r in VS:
    vv = r.get('vehicles') or [{}]
    if not r['vehicle_stops']: W('| %s | %s | %s | no vehicle stop | | | | | | %s |' % (s, cls(r)[1], vv[0].get('name', 'parked car + jogger') if vv else 'parked car + jogger', f(vv[0].get('min_gap_tug_m')) if vv else '-'))
    for v_ in r['vehicle_stops']:
        W('| %s | %s | %s (%s) | %s / %s | %.1f | %.1f | %s / %s | %.1f | %s | %.2f (%s) |' % (s, cls(r)[1], vv[0].get('name'), vv[0].get('mode'), v_['side'], esc(v_['crit']), v_['radar_r'], v_['closing'], v_.get('stop_s'), v_.get('stop_dist_m'), v_['hold_s'], v_['resume'], v_['min_truth_gap_m'], f(vv[0].get('min_gap_bin_m'))))
for s in ('s23a_vehicle_oncoming', 's23b_vehicle_behind', 's23c_vehicle_passing', 's23d_no_false_stop'):
    v = ROB.get(s)
    if v: W('| %s robustness | %d/%d as expected | | %s | | | | | | min gap %s |' % (s, sum(cls(r)[0] for r in v), len(v), '; '.join('seed %s: %d stop(s)' % (r.get('seed'), len(r['vehicle_stops'])) for r in v), f(min([(r.get('vehicles') or [{}])[0].get('min_gap_tug_m', 99) for r in v] or [None]))))
W('\n![Vehicle stops: distance, tug speed and hold](fig_g4/g4_vehicle.png){width=100%}\n')
W('## f) Two-way audio\n')
W('Companion audio state (idle / announce / ringing / call; owner call has priority), canned clips on vehicle stop, pinch refusal and centre-gap contact, and a WebRTC-over-4G API stub `sitl/scripts_g4/audio_api.py` (aiohttp REST signalling; TURN relay because of 4G CGNAT; Opus 24 kbit/s). Parts and wiring: `revG/docs_G4/AUDIO_RADAR_G4.md` (Appendix). The stub returns a canned SDP answer - no audio flows.\n')
r16 = R.get('s16c_release_person_by_bin')
if r16:
    W('s16c audio log: ' + '; '.join('t=%.0f s %s%s' % (a['t'], a['kind'], (' "%s"' % a['text']) if a.get('text') else '') for a in r16.get('audio_log', [])) + '\n')
st = os.path.join(G4, 'audio_api_selftest.txt')
if os.path.exists(st): W('API self-test (`audio_api.py selftest`):\n\n```\n' + '\n'.join(l[:118] for l in open(st).read().splitlines()) + '\n```\n')
W('## g) Adaptive drop spot, allowed areas and keep-out zones\n')
W('Each programmed slot (pads A/M/F, home spots) gets an ordered list of alternates: taught, or auto-generated on a 0.4 m grid inside the user-drawn allowed drop area, same handle heading (handles toward the lane), each one legal: footprint inside the allowed area, >= 0.1 m outside every keep-out, >= 0.45 m inside private ground, hedge clearance and spacing to all programmed slots as the layout requires, plus a 2.6 m dock corridor; sorted by distance from the primary (max 30, >= 0.8 m apart). Before a release the companion checks the slot with lidar ray-casting over the slot footprint + 0.3 m (FREE / OCCLUDED / UNSEEN); if the primary is blocked it takes the nearest alternate that is clear and whose approach is clear (pads: the 3.5 m pickup corridor; home: the yard U-turn ground), logs it, notifies the app, and records where the bin was actually left in a drop log; pickup searches from the logged pose with the existing lidar + ArUco procedure. None clear -> hold with the bin + alert. Pad A is only checked before the mouth U-turn: if A is blocked the U-turn is not attempted (hold + alert) - the U-turn geometry leaves no room for an A alternate.\n')
W('**Camera:** in this SITL the slot decision is lidar-only. The rear ArUco camera cannot see a slot ahead of the tug; it only identifies a blocking bin (tag ID) once it is behind. A camera classifier for debris / people was not modelled.\n')
W('Keep-outs are added to the inclusion fence (`Site.in_fence` rejects axle points within 0.5 m of a keep-out, used by every planner), lane waypoints shift sideways around them, and every run logs the deepest footprint penetration.\n')
W('![Inclusion fence, private boundary, allowed drop areas, keep-outs, programmed slots and auto alternates](fig_g4/g4_fences.png){width=100%}\n')
da = DropAreas(S)
W('| Zone | Type | Polygon (lane coords) |\n|---|---|---|')
for k, v in da.d['allowed_areas'].items(): W('| %s | allowed drop area | %s frame: %s |' % (k, v['frame'], ' '.join('(%.1f,%.2f)' % tuple(q) for q in v['poly'])))
for v in da.d['keepouts']: W('| %s | KEEP-OUT | %s frame: %s |' % (esc(v['name']), v['frame'], ' '.join('(%.1f,%.2f)' % tuple(q) for q in v['poly'])))
W('| s24c only: soft verge over a septic tank | KEEP-OUT | house frame: (300,0.5) (312,0.5) (312,2.2) (300,2.2) |\n')
W('| Scenario | Result | Outcome | Adaptive slot decision | Keep-out depth m (- = outside) |\n|---|---|---|---|---|')
for s in ('s24a_home_slot_car', 's24b_all_slots_blocked', 's24c_keepout_route', 's24d_pickup_logged_pose'):
    r = R.get(s)
    if not r: W('| %s | NOT RUN | | | |' % s); continue
    ad = [a for a in r['metrics'].get('adaptive_slot', []) if a.get('chosen') != 'primary']
    dec = '; '.join('%s: primary %d/%d occluded -> %s' % (a['slot'], a['primary_check']['occl'], a['primary_check']['n'], ('alternate %.1f m away (%s)' % (a['chosen']['moved_m'], 'L-%.1f/lat %+.2f' % (a['chosen']['s_from_end'], a['chosen']['lat']) if a['chosen']['s'] > 300 else 's %.1f/lat %+.2f' % (a['chosen']['s'], a['chosen']['lat']))) if a.get('chosen') else 'none of %d clear' % a.get('n_alts', 0)) for a in ad) or ('keep-out shifts %d waypoints' % len(r['metrics'].get('keepout_shifts', [])) if r['metrics'].get('keepout_shifts') else '-')
    W('| %s | %s | %s | %s | %s |' % (s, cls(r)[1], esc(r['outcome'])[:60], esc(dec), f(r.get('keepout_max_depth_m'))))
ko_all = [(r.get('keepout_max_depth_m'), s) for s, r in R.items() if r.get('keepout_max_depth_m') is not None]
if ko_all: W('\nDeepest keep-out penetration over all regression runs: %.2f m (%s) - negative means the footprint never entered a keep-out.\n' % max(ko_all))

W('# 5. Full regression\n')
W('| Scenario | G3 | G4 | exp | sim s | Wh | legal m | hedge m | Outcome |\n|---|---|---|---|---|---|---|---|---|')
for s in SC.ALL_G4:
    r = R.get(s); g = G3.get(s)
    if not r: W('| %s | %s | MISSING | | | | | | |' % (s, g['cls'] if g else 'new')); continue
    W('| %s | %s | %s%s | %s | %.0f | %.0f | %s | %s | %s |' % (s, g['cls'] if g else 'new', cls(r)[1], '' if cls(r)[0] else ' **BAD**', r['expect'], r['sim_time_s'], r['energy_wh'], f(r.get('legal_min_inside_m')), f(r.get('hedge_overlap_m')), esc(r['outcome'])[:62]))
W('\n# 6. Robustness (seeds 7, 11, 23, 42)\n')
W('| Scenario | as expected | Not as expected (seed: outcome) |\n|---|---|---|')
for s in SC.ROBUST_G4:
    v = ROB.get(s, [])
    W('| %s | %d/%d | %s |' % (s, sum(cls(r)[0] for r in v), len(v), esc('; '.join('seed %s: %s' % (r.get('seed'), r['outcome']) for r in v if not cls(r)[0]))[:150]))
W('')
W('# 7. Failures, limits and open issues (honest list)\n')
bad = [s for s, r in R.items() if not cls(r)[0]]
W('* Regression scenarios NOT as expected: %s.' % (', '.join(bad) if bad else 'none'))
rb = ['%s seed %s' % (s, r.get('seed')) for s, v in ROB.items() for r in v if not cls(r)[0]]
W('* Robustness runs NOT as expected: %s.' % (', '.join(rb) if rb else 'none'))
OPEN = os.path.join(G4, 'report', 'open_issues.md')
if os.path.exists(OPEN): W(open(OPEN).read())
W('\n# Appendix - audio and radar parts and wiring\n')
doc = os.path.join(REVG, 'docs_G4', 'AUDIO_RADAR_G4.md')
if os.path.exists(doc): W('\n'.join(('#' + l) if l.startswith('#') else l for l in open(doc).read().splitlines()[1:]))
txt = ascii_('\n'.join(md))
open(os.path.join(REVG, 'RESULTS_G4_sitl.md'), 'w').write(txt)
for fn in ('g4_fences.png', 'g4_keepleft.png', 'g4_vehicle.png'):
    if os.path.exists(os.path.join(G4, 'report', fn)): shutil.copy(os.path.join(G4, 'report', fn), os.path.join(FIG, fn))
r = subprocess.run(['pandoc', 'RESULTS_G4_sitl.md', '-o', 'RESULTS_G4_sitl.pdf', '--pdf-engine=pdflatex', '-V', 'colorlinks=true'], cwd=REVG, capture_output=True, text=True)
print('pandoc rc', r.returncode, r.stderr[-1500:])
print('regress %d/%d robust %d/%d margin %s' % (n_ok, n_all, rob_ok, rob_n, margin))
