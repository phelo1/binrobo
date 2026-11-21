#!/usr/bin/env python3
"""Revision 5 cost: changes against the B2-F parts list (new-drive variant), low and high. Prints a Markdown table and the totals."""
import json
BASE_PARTS, BASE_ALLIN = 3417.26, 4112.32; K = BASE_ALLIN / BASE_PARTS
R = [('Frame: box section, laser-cut plates, bolts (line FAB-B2 was 354)', -14, 181, 'ASSUMED: 55 kg of section at EUR 2.2 to 3.0 a kg, 25 kg of cut plate at EUR 6 to 10 a kg, bolts 50 to 80'),
     ('Lift actuator, bought used (line B-0 was 164)', 86, 236, 'used unit EUR 250 to 400: one used listing at about USD 294 (Sources). New: EUR 940 to 1,060'),
     ('Lift stop blocks and four limit switches', 40, 80, 'ASSUMED'),
     ('Soft nose with three switch strips; rear bumpers kept (lines BMP-L8 and G22 were 170)', 20, 160, 'ASSUMED: foam and cover 45 to 80, ribbon switches 60 to 150, aluminium 25 to 40'),
     ('Second lidar, for the rear', 50, 50, 'price of line G21'),
     ('Front camera with infra-red light', 30, 45, 'ASSUMED, as the rear camera'),
     ('Two ToF sensors under the bin', 12, 12, 'price of line B2-GAP'),
     ('Ground-speed source for the watchdog', 10, 35, 'ASSUMED'),
     ('Safety controller, bought used (line SR-L8 was 61)', 39, 189, 'ASSUMED: EUR 100 to 250 used'),
     ('Contactors with mirror contacts, used (line KM-L8 was 57)', 0, 80, 'ASSUMED'),
     ('Castor beam pivot parts, longer pad springs', 20, 40, 'ASSUMED'),
     ('B2-F lines not needed: pad actuator and switch, hitch motor and switch, ballast', -121, -121, 'their prices'),
     ('Sourcing: simpler 4G board, plain multicore harness', -80, -80, 'my cost review of 13 November')]
lo = sum(r[1] for r in R); hi = sum(r[2] for r in R)
print('| Change against the B2-F parts list | Low, EUR | High, EUR | Basis |\n|---|---:|---:|---|')
for n, a, b, w in R: print('| %s | %+d | %+d | %s |' % (n, a, b, w))
print('| **Sum of changes** | **%+d** | **%+d** | |' % (lo, hi))
p = (BASE_PARTS + lo, BASE_PARTS + hi); a = (p[0] * K, p[1] * K); new = ((p[0] + 690) * K, (p[1] + 660) * K)
print('\nparts %.0f to %.0f; all-in (same mark-up as the B2-F list, x%.3f) %.0f to %.0f; with a new actuator %.0f to %.0f' % (p[0], p[1], K, a[0], a[1], new[0], new[1]))
json.dump(dict(rows=R, parts=p, all_in=a, all_in_new_actuator=new, base_parts=BASE_PARTS, base_all_in=BASE_ALLIN), open('/home/claude/s0/r5/pack_tables/cost_r5.json', 'w'), indent=1)
