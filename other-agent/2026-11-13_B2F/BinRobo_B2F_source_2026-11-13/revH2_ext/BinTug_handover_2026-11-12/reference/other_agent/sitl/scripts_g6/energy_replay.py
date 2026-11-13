#!/usr/bin/env python3
"""Rev G6 energy replay: the measured (SITL) bus-power traces of s20a (3-bin drop evening) and s20b (3-bin pickup evening)
replayed through three 8S LFP packs (12 / 20 / 25 Ah = 307 / 512 / 640 Wh nominal) under:
  A  'as designed'  : pack at the s20 air temperature (+0.5 C, cold factor from scene.pack_cold_factor), dock pack heater ->
                      overnight recharge (CC 5 A, 144 W) between the evenings; no charge between trips (pack < +3 C off the dock).
  B  '0 C, no charge': usable = nominal x 0.88 (0 C derate), NO charge at all between the start of s20a and the end of s20b
                      (no mid-evening charge, no overnight charge: heater failed / no mains at the dock).
Trip guard as in the companion: a trip only starts if (SOC - 10 %) x usable >= TRIP_WH (47 Wh); a refused trip leaves that bin
(and every later one that evening). Reports bins moved, finish clock vs the 21:00 bye-law, end SOC, minimum SOC.
usage: energy_replay.py <s20a dir> <s20b dir> <label> [out.json]"""
import json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
TRIP_WH = 47.0; RESERVE = 0.10; V_NOM = 25.6
def cold(t_c):
    import numpy as np
    return float(np.interp(t_c, [-20, -10, 0, 10, 25], [0.60, 0.75, 0.88, 0.95, 1.0]))


def drains(d):
    """Per-trip pack drain (Wh) from a run: bus energy while NOT on dock voltage (the dock carries the bus when seated), split at
    the 'trip N:' events; + the RTC-sleep energy booked by the run. Returns dict(trips=[(n, start_clock, wh)], pre_wh, sleep_wh, res)."""
    res = json.load(open(os.path.join(d, 'result.json'))); T = json.load(open(os.path.join(d, 'trace.json')))['trace']
    starts = [(e['t'], e['text']) for e in res['events'] if re.match(r'trip \d+:', e['text'])]
    st_t = [t for t, _ in starts]
    seg = [0.0] * (len(st_t) + 1); prev = None
    for r in T:
        if prev is not None:
            dwh = r['wh'] - prev['wh']
            if dwh > 0 and not prev.get('dkv'):
                k = sum(1 for t in st_t if r['t'] >= t); seg[k] += dwh
        prev = r
    trips = []
    for i, (t, txt) in enumerate(starts):
        m = re.search(r'clock (\S+ \S+|\S+)', txt); trips.append(dict(n=i + 1, t=t, text=txt[:90], clock=m.group(1) if m else None, wh=round(seg[i + 1], 1)))
    return dict(trips=trips, pre_wh=round(seg[0], 1), sleep_wh=res.get('sleep_wh') or 0.0, res=res)


def replay(A, B, ah, case):
    nom = V_NOM * ah; usable = nom * (cold(A['res'].get('air_c', 0.5)) if case == 'A' else 0.88)
    soc = 1.0; out = dict(pack_ah=ah, pack_wh=round(nom), usable_wh=round(usable), case=case, evenings=[])
    smin = soc
    for name, D in (('s20a drop', A), ('s20b pickup', B)):
        if name.startswith('s20b'):
            soc -= D['sleep_wh'] / usable           # RTC sleep before the pickup evening
            if case == 'A': soc = 1.0               # overnight dock recharge (heater keeps the pack >= +3 C); 144 W CC: <= 4.5 h even for 640 Wh
        soc -= D['pre_wh'] / usable; moved = 0; refused = []
        for tr in D['trips']:
            avail = (soc - RESERVE) * usable
            if avail < TRIP_WH: refused.append(dict(trip=tr['n'], avail_wh=round(avail, 1))); break
            soc -= tr['wh'] / usable; moved += 1; smin = min(smin, soc)
        if name.startswith('s20a'): soc -= D['sleep_wh'] / usable
        m = D['res'].get('metrics') or {}
        out['evenings'].append(dict(evening=name, trips=len(D['trips']), moved=moved, refused=refused, soc_end=round(soc, 3),
                                    finish_clock=m.get('finish_clock'), deadline_margin_min=m.get('deadline_margin_min') if moved == len(D['trips']) else None,
                                    trip_wh=[t['wh'] for t in D['trips']]))
    out['soc_min'] = round(smin, 3); out['soc_end'] = round(soc, 3)
    out['complete'] = all(e['moved'] == e['trips'] for e in out['evenings'])
    return out


if __name__ == '__main__':
    A = drains(sys.argv[1]); B = drains(sys.argv[2]); label = sys.argv[3]
    rows = [replay(A, B, ah, case) for case in ('A', 'B') for ah in (12, 20, 25)]
    summ = dict(label=label, s20a=dict(result=A['res']['result'], trips=A['trips'], pre_wh=A['pre_wh'], sleep_wh=A['sleep_wh'], energy_wh=A['res']['energy_wh'],
                                         mass=A['res'].get('mass_kg'), finish=(A['res'].get('metrics') or {}).get('finish_clock')),
                s20b=dict(result=B['res']['result'], trips=B['trips'], pre_wh=B['pre_wh'], sleep_wh=B['sleep_wh'], energy_wh=B['res']['energy_wh'],
                          mass=B['res'].get('mass_kg'), finish=(B['res'].get('metrics') or {}).get('finish_clock'),
                          margin_min=(B['res'].get('metrics') or {}).get('deadline_margin_min')), replay=rows)
    for r in rows:
        print('%s case %s %2d Ah (%3d Wh, usable %3d): %s | %s | SOC min %.0f %% end %.0f %%' % (label, r['case'], r['pack_ah'], r['pack_wh'], r['usable_wh'],
              'COMPLETE' if r['complete'] else 'INCOMPLETE', '; '.join('%s %d/%d%s' % (e['evening'], e['moved'], e['trips'], (' refused %s' % e['refused']) if e['refused'] else '') for e in r['evenings']),
              100 * r['soc_min'], 100 * r['soc_end']))
    if len(sys.argv) > 4: json.dump(summ, open(sys.argv[4], 'w'), indent=1)
