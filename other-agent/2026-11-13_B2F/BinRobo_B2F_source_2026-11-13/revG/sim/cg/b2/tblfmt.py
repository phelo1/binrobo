"""formatters copied from cmp/tables_cmp.py"""
import os, json
def g1s(S, key='G1'):
    if not S: return 'not run'
    g = S[key]; b = g['bins']
    return '%s; pooled %d/%d; FH %d; knocked %d' % (' / '.join('%s %s' % (k.replace('ESE240', '').replace('WEB140', 'WEB'), ('%d/%d' % (v['captured'], v['n'])) if isinstance(v, dict) else v) for k, v in b.items()),
                                                  g['pooled'], g['n'], g['false_holds'], g['knocked'])
def g2s(S):
    if not S: return 'not run'
    r = S['G2']['runs']; ok = sum(1 for v in r.values() if v and v['ok'])
    ts = [v['t'] for v in r.values() if v]; cr = [v['creep'] for v in r.values() if v]
    bad = [k for k, v in r.items() if not (v and v['ok'])]
    return '%d/6; %s-%s s; creep <= %.3f m%s' % (ok, min(ts) if ts else '-', max(ts) if ts else '-', max(cr) if cr else 0, ('; fail: ' + ', '.join('%s (grab %s, %.2f m)' % (k, r[k]['grab'], r[k]['dist']) for k in bad if r[k])) if bad else '')
def g3s(S):
    if not S: return 'not run'
    o, b = S['G3']['one'], S['G3']['both']
    f = lambda x: ('PASS (%.2f m, clear %.0f mm)' % (x['dist'], 1000 * x['clear_min']) if x['ok'] else 'FAIL (%.2f m, grab %s, bin-ground %.0f N, seated %s)' % (x['dist'], x['grab'], x['bin_ground'], x['seated'])) if x else 'not run'
    return 'one side %s; full width %s' % (f(o), f(b))
def g4s(S):
    if not S: return 'not run'
    r = S['G4']['runs']; return ' / '.join('%s %s %.2f m, slide %.3f' % (k, 'PASS' if v['ok'] else 'FAIL', v['stop'], v['slide']) if v else k + ' not run' for k, v in r.items())
def g5s(S):
    if not S or not S['G5']['run']: return 'not run'
    v = S['G5']['run']; return '%s; roll %.2f deg; pivot swept %.2f m' % ('PASS' if v['ok'] else 'FAIL', v['roll'], v['swept'])
def g6s(S):
    if not S: return 'not run'
    g = S['G6']; c = g['cases']; bad = ['%s %s' % (k.replace('ESE240', ''), v) for k, v in c.items() if v != 'PASS']
    return '%d/18, %d TIPS%s' % (g['passed'], g['tips'], ('; ' + ', '.join(bad)) if bad else '')
def g7s(S):
    if not S: return 'not run'
    r = S['G7']['runs']; return '; '.join('%s %s' % (k, ('base %s / dt025 %s%s' % (v['base'], v['dt025'], (' t %s/%s s' % tuple(v['t'])) if v['t'][0] else '')) if isinstance(v, dict) else v) for k, v in r.items())
def g8s(S):
    if not S: return 'not run'
    p = S['G8']['poses']; okn = sum(1 for v in p.values() if v and v['ok'])
    dmin = min(min(v['dL'], v['dR']) for v in p.values() if v); cmin = min(v['castors'] for v in p.values() if v)
    bad = [k for k, v in p.items() if not (v and v['ok'])]
    return '%d/8 poses; drive >= %.0f N, castors >= %.0f N; hand-calc min tip %.1f deg%s' % (okn, dmin, cmin, S['G8']['handcalc_min_tip_deg'], ('; fail: ' + ', '.join(bad)) if bad else '')
def g9s(S): return ('%.1f kg' % S['G9']['kg']) if S else 'not run'
