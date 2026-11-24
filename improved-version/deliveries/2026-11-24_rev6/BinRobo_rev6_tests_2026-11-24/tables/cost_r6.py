#!/usr/bin/env python3
"""Revision 6 cost (24 Nov): revision 5.1 plus the changes after the re-test of 23 Nov (third lidar, companion able to run the person detector,
lift relays, watchdog relays, second diode; the 2:1 sprocket costs the same as the 3.5:1 one).
Changes against the B2-F parts list (new-drive variant, 3,417.26 parts / 4,112.32 all-in), low and high. Prints a Markdown table and totals."""
import json
BASE_PARTS, BASE_ALLIN = 3417.26, 4112.32; K = BASE_ALLIN / BASE_PARTS
R = [('Frame: box section from a steel stockholder\'s offcut rack or a scrap yard, laser-cut plates, bolts (line FAB-B2 was 354)', -70, 125, 'ASSUMED: 55 kg of section at EUR 1.2 to 2.0 a kg (was 2.2 to 3.0 new), 25 kg of cut plate at EUR 6 to 10 a kg, bolts 50 to 80', 'changed'),
     ('Lift actuator, bought used (line B-0 was 164)', 86, 236, 'used unit EUR 250 to 400 (revision 5 sources). Now the only option priced', 'same'),
     ('Lift rails and carriages, bought used (line B-1 was 90)', -45, -20, 'ASSUMED: used pair with four carriages EUR 45 to 70', 'new'),
     ('Lift stop blocks and four limit switches', 40, 80, 'ASSUMED', 'same'),
     ('Soft nose with switch strips on the front, the corners and the sides; rear bumpers kept (lines BMP-L8 and G22 were 170)', 20, 160, 'ASSUMED: foam and cover 45 to 80, ribbon switches 60 to 150, aluminium 25 to 40', 'same'),
     ('Second and third lidar, one on each leg tip', 100, 100, 'two at the price of line G21', 'one more: +50'),
     ('Front camera with infra-red light', 30, 45, 'ASSUMED, as the rear camera', 'same'),
     ('Two ToF sensors under the bin', 12, 12, 'price of line B2-GAP', 'same'),
     ('Ground-speed source for the watchdog', 10, 35, 'ASSUMED', 'same'),
     ('Stop relay: keep the used relay already on the B2-F list (line SR-L8, EUR 61)', 0, 0, 'as revision 5.1', 'same'),
     ('Lift relays K4 and K5, three watchdog relays with linked contacts, second diode', 50, 110, 'ASSUMED: five small relays at EUR 9 to 20, diode 5 to 10', 'new'),
     ('Companion computer able to run the person detector on two cameras (line G23 was 101)', 60, 130, 'the reviewers\' figure: an RK3588-class board, or a Pi 5 with an accelerator', 'new'),
     ('Chain stage 2:1: 24-tooth wheel sprocket in place of 42 teeth (line DRV-W8)', -5, 0, 'ASSUMED: a smaller plate sprocket costs the same or a little less', 'new'),
     ('Contactors: keep the pair already on the B2-F list (line KM-L8, EUR 57)', 0, 0, 'no auxiliary contacts needed: feedback is by the controller-side voltage', 'same'),
     ('Castor beam pivot parts, longer pad springs', 20, 40, 'ASSUMED', 'same'),
     ('B2-F lines not needed: pad actuator and switch, hitch motor and switch, ballast', -121, -121, 'their prices', 'same'),
     ('Sourcing: simpler 4G board, plain multicore harness', -80, -80, 'my cost review of 13 November', 'same')]
lo = sum(r[1] for r in R); hi = sum(r[2] for r in R)
print('| Change against the B2-F parts list | Low, EUR | High, EUR | Basis | Since revision 5.1 |\n|---|---:|---:|---|---|')
for n, a, b, w, c in R: print('| %s | %+d | %+d | %s | %s |' % (n, a, b, w, c))
print('| **Sum of changes** | **%+d** | **%+d** | | |' % (lo, hi))
p = (BASE_PARTS + lo, BASE_PARTS + hi); a = (p[0] * K, p[1] * K)
r5p = (3369.26, 3979.26); r5a = (r5p[0] * K, r5p[1] * K)   # revision 5.1
print('\nparts %.0f to %.0f; all-in (same mark-up as the B2-F list, x%.4f) %.0f to %.0f' % (p[0], p[1], K, a[0], a[1]))
print('revision 5.1 was parts %.0f to %.0f, all-in %.0f to %.0f; revision 6 adds all-in %.0f to %.0f' % (r5p[0], r5p[1], r5a[0], r5a[1], a[0] - r5a[0], a[1] - r5a[1]))
print('B2-F list all-in %.0f; difference %+.0f to %+.0f' % (BASE_ALLIN, a[0] - BASE_ALLIN, a[1] - BASE_ALLIN))
# further used-part options, NOT counted above (each needs a part to be found first)
OPT = [('Used gearmotor pair from a mobility scooter or powerchair breaker (line DRV-M8 is 315 new)', -200, -150, 'ASSUMED: EUR 115 to 165 for a matched pair; gear ratio and shaft must suit the chain stage'),
       ('Used motor controller (line CTL-L8 is 148 new)', -70, -40, 'ASSUMED'),
       ('Used lidars or cameras', -60, -20, 'ASSUMED; small sums'),
       ('Used battery cells', 0, 0, 'not advised: capacity unknown; the new cells are only EUR 140')]
ol = sum(o[1] for o in OPT); oh = sum(o[2] for o in OPT)
print('\n| Further used-part options, not counted | Low, EUR | High, EUR | Note |\n|---|---:|---:|---|')
for n, x, y, w in OPT: print('| %s | %+d | %+d | %s |' % (n, x, y, w))
print('\nall options taken: parts %.0f to %.0f, all-in %.0f to %.0f' % (p[0] + ol, p[1] + oh, (p[0] + ol) * K, (p[1] + oh) * K))
json.dump(dict(rows=R, parts=p, all_in=a, base_parts=BASE_PARTS, base_all_in=BASE_ALLIN, r5_parts=r5p, r5_all_in=r5a, options=OPT,
               all_options_parts=(p[0] + ol, p[1] + oh), all_options_all_in=((p[0] + ol) * K, (p[1] + oh) * K)), open('/home/claude/s0/r6/tables/cost_r6.json', 'w'), indent=1)
