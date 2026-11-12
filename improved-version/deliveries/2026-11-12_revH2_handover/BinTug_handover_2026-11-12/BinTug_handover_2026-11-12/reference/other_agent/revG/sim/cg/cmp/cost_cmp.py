#!/usr/bin/env python3
"""Cost comparison B1 vs Rev H on one basis (COSTDOWN_G8 function/safety lines). Output res/cost_cmp.json.
Rev H as claimed = revH_ext/revH/results/bom_revH.json summary. Rev H re-based = Rev H mover lines (Structure, Drive, Bin handling,
Power) + the G8 Lean-D (donor) lines for every function Rev H shares with the project (Safety, Navigation, Sensing, Comms,
Enclosure & wiring, Lights, Dock) + donor chair at the G8 excerpt price (EUR 400) instead of Rev H's EUR 160; G8 donor logistics;
contingency at the G8 donor overall rate. B1 = it1/res/cost_it1.json (Lean G8 concept B + iteration 1)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(H, '..', '..', '..', '..')
RH = json.load(open(os.path.join(P, 'revH_ext/revH/results/bom_revH.json')))['summary']
G8 = json.load(open(os.path.join(P, 'revG/bom_revG8.json'))); B1 = json.load(open(os.path.join(H, '..', 'it1', 'res', 'cost_it1.json')))
ha = RH['rev_h_by_area']; da = G8['by_area_donor']; la = G8['by_area_lean']
shared = ['Safety & power dist.', 'Navigation', 'Sensing', 'Comms', 'Enclosure & wiring', 'Lights', 'Dock']
own = ['Structure', 'Drive', 'Bin handling', 'Power']
t = G8['totals']['lean_donor']; crate = t['contingency'] / t['subtotal']
parts = sum(ha[a] for a in own) + sum(da[a] for a in shared) + (400 - 160)
reb = dict(parts=round(parts, 2), logistics=t['logistics'], contingency=round(crate * (parts + t['logistics']), 2))
reb['all_in'] = round(reb['parts'] + reb['logistics'] + reb['contingency'], 2)
# B1 on a donor drive (indicative hybrid; geometry not designed): swap lean Structure/Drive/Power for the donor lines
b1p = B1['basis']['parts'] + B1['delta']['parts'] - sum(la[a] for a in ('Structure', 'Drive', 'Power')) + sum(da[a] for a in ('Structure', 'Drive', 'Power'))
b1d = dict(parts=round(b1p, 2), logistics=t['logistics'] + 19.99); b1d['contingency'] = round(crate * (b1d['parts'] + b1d['logistics']), 2)
b1d['all_in'] = round(b1d['parts'] + b1d['logistics'] + b1d['contingency'], 2)
R = dict(revH_claim=RH['rev_h'], revH_by_area=ha, g8_donor_by_area={a: da.get(a, 0) for a in shared + own}, g8_lean_by_area={a: la.get(a, 0) for a in shared + own},
         shared_gap={a: round(da[a] - ha[a], 2) for a in shared}, revH_rebased=reb, contingency_rate=round(crate, 4),
         B1=dict(all_in=B1['new_all_in'], basis=B1['basis'], delta=B1['delta']), B1_donor_indicative=b1d,
         fw_comb_delta=dict(item='640 mm comb plate (6 mm S355, laser) + yaw/roll pivot (2 bushes, 2 springs, end stops) in place of the 160 mm tooth',
                            eur_est=45.0, status='est', note='replaces a same-plate 160 mm tooth; +~1.6 kg on the carriage'))
json.dump(R, open(os.path.join(H, 'res', 'cost_cmp.json'), 'w'), indent=1); print(json.dumps(R, indent=1))
