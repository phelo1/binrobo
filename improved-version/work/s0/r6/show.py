#!/usr/bin/env python3
# one line per run of a mission-simulation output folder. usage: show.py <sitl_out name> [...]
import json, glob, sys
for name in sys.argv[1:]:
    for f in sorted(glob.glob('/home/claude/sitl_out/%s/runs/*/result.json' % name)):
        r = json.load(open(f)); m = r['metrics']
        print('%-22s %s s%-3s %-5s %-16s | nearest %s %s | contacts %d | hedge %.3f | %.1f min %.1f Wh | alerts %s' % (name, r['scenario'], r['seed'], r['result'], r['outcome'][:16], r['contact_min_m'], r['contact_with'], len(r['collisions']), r['hedge_min_m'], r['sim_time_s'] / 60, r['energy_wh'], [a[:60] for a in r['alerts']]))
        pp = m.get('ppl_pauses', [])
        if pp: print('      pauses: ' + '; '.join('%s %.1f m at s %.0f, %s s%s%s' % (p.get('by', 'cam'), p['range'], p['s'], p.get('wait_s'), ' person' if p.get('person') else '', ' passed-static' if p.get('passed_static') else '') for p in pp[:12]) + (' ... %d in all' % len(pp) if len(pp) > 12 else ''))
        if m.get('stops') or m.get('prot_stops'): print('      obstacle stops %d, protective-field stops %d %s' % (len(m.get('stops', [])), len(m.get('prot_stops', [])), [(q['s'], q['gap']) for q in m.get('prot_stops', [])][:6]))
        for t in m.get('trips', []): print('      trip %s %s -> %s  %.1f min  %.1f Wh' % (t['kind'], t['clk0'], t['clk1'], t['min'], t['wh']))
