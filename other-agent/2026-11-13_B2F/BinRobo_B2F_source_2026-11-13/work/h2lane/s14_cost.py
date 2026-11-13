#!/usr/bin/env python3
"""S14 cost on one basis. Reads the regenerated BOMs (Rev H2: revH2/results/bom_revH2.json via bom_revH2.py; B2: revG/sim/cg/b2/res/
bom_b2.json via bom_b2.py with ACT-L8 removed) and applies the 12 Nov price spot-checks (work/h2lane/price_checks.json) to Rev H2.
One basis = the same contingency rule (checked 5 %, excerpt 8 %, estimate 12 %, local/used/donor 15 %, logistics 10 %) and the
same 'verified' definition: a line counts as verified when its status starts with 'checked' (page fetched), share by parts value.
Output res/s14_cost.json."""
import json, os, csv
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.abspath(os.path.join(H, '..', '..'))
HB = os.path.join(P, 'revH2_ext', 'BinTug_handover_2026-11-12', 'revH2', 'results')
B2 = json.load(open(os.path.join(P, 'revG', 'sim', 'cg', 'b2', 'res', 'bom_b2.json')))
B2pre = json.load(open(os.path.join(P, 'revG', 'sim', 'cg', 'b2', 'res', 'bom_b2.pre_S14.json')))
PC = {l['id']: l for l in json.load(open(os.path.join(H, 'price_checks.json')))['lines']}
def rate(st, origin, eur, idd=''):
    s = st.split('+')[-1] if st else 'est'
    if (origin == 'LOCAL' and eur) or idd == 'SR-L8': return 0.15
    return 0.05 if s.startswith('checked') else 0.08 if s.startswith('excerpt') else 0.12
def h2(variant, apply_checks):
    rows = [r for r in csv.DictReader(open(os.path.join(HB, 'bom_revH2_%s.csv' % variant))) if r['id'] not in ('TOTAL', 'GAP') and r['eur']]
    parts = [dict(id=r['id'], eur=float(r['eur']), status=r['price_status'], origin=r['origin'], cr=float(r['contingency_rate'] or 0)) for r in rows if r['area'] != 'Logistics']
    logi = sum(float(r['eur']) for r in rows if r['area'] == 'Logistics')
    if apply_checks:
        for p in parts:
            if p['id'] in PC:
                c = PC[p['id']]; p['eur'] = c['eur_after']; p['status'] = c['status_after']; p['cr'] = rate(p['status'], p['origin'], p['eur'], p['id'])
    tot = sum(p['eur'] for p in parts); cont = sum(p['eur'] * p['cr'] for p in parts) + 0.10 * logi
    ver = sum(p['eur'] for p in parts if p['status'].startswith('checked'))
    return dict(parts=round(tot, 2), logistics=round(logi, 2), contingency=round(cont, 2), all_in=round(tot + logi + cont, 2),
                verified_share=round(ver / tot, 3), lines=len(parts))
out = dict(rev_h2=dict(), b2=dict())
for v in ('donor', 'new'):
    out['rev_h2'][v + '_as_regenerated'] = h2(v, False)
    out['rev_h2'][v + '_after_12nov_checks'] = h2(v, True)
for v in ('new', 'donor'):
    out['b2'][v + '_published'] = B2pre[v]['totals']; out['b2'][v + '_corrected_no_ACT-L8'] = B2[v]['totals']
out['price_checks'] = PC
json.dump(out, open(os.path.join(H, 'res', 's14_cost.json'), 'w'), indent=1)
for k, v in out['rev_h2'].items(): print('RevH2', k, v)
for k, v in out['b2'].items(): print('B2', k, {a: v[a] for a in ('parts', 'logistics', 'contingency', 'all_in', 'verified_share')})
