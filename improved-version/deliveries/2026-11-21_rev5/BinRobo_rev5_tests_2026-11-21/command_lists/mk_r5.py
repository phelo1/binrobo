#!/usr/bin/env python3
"""Revision 5, list A: person stops (empty nose first and tail first, full bin), lowering with the ground-looking sensors and the load guard,
edges from a standstill and with a run-up, kerb shocks, sideways tyre force. Results in h2/res_r5x. Built from the revision 4 command lines."""
import re
src = [l for l in open('/home/claude/s0/r4/q_r4_c.txt') if l.strip()]
def conv(l):
    return l.replace('X_NOSE_DX=0.34', 'X_NOSE_DX=0.245').replace('mass_cgB2_r4.json', 'mass_cgB2_r5.json').replace('res_r4x', 'res_r5x').replace('IT1_TAG=_r4', 'IT1_TAG=_r5')
base = conv([l for l in src if 'runY.py pstop' in l and 'IT1_TAG=_r4 ' in l and 'PERT_M' not in l and 'X_CBRAKE' not in l][0]); pre = base.split('python3')[0]; Y = 'python3 /home/claude/s0/r4/runY.py '
def line(cmd, tag='_r5', **env):
    p = pre.replace('IT1_TAG=_r5', 'IT1_TAG=' + tag)
    if env: p = p.replace('env ', 'env ' + ' '.join('%s=%s' % kv for kv in env.items()) + ' ', 1)
    return p + Y + cmd + '\n'
a = []
for gr in (0, -0.03, -0.06, -0.08, -0.10, -0.12):
    for v in (0.2, 0.3, 0.4): a.append(line('pstop %g %g 0.3 0 0.15' % (v, gr)))
for gr in (-0.06, -0.08, -0.10, -0.12): a.append(line('pstop 0.2 %g 0.22 0 0.15' % gr))
a.append(line('pstop 0.4 0 0.22 0 0.15'))
for gr in (-0.06, -0.08, -0.10, -0.12):
    for v in (0.2, 0.3): a.append(line('pstop %g %g 0.3 0 0.15 rev' % (v, gr)))
    a.append(line('pstop 0.2 %g 0.22 0 0.15 rev' % gr))
a.append(line('pstop 0.3 -0.12 0.22 0 0.15 rev'))
for gr in (0, -0.03, -0.06, -0.09, -0.12):
    for v in (0.2, 0.3, 0.4): a.append(line('pstop %g %g 0.3 110 0.15' % (v, gr)))
a.append(line('pstop 0.5 0 0.3 110 0.15'))
for gr in (-0.06, -0.09, -0.12): a.append(line('pstop 0.2 %g 0.22 110 0.15' % gr))
a += [line('pstop 0.4 0 0.3 0 0.2'), line('pstop 0.3 -0.09 0.3 110 0.2')]
for c in ('0.4 0 0.3 0 0.15', '0.2 -0.12 0.3 0 0.15 rev', '0.2 -0.12 0.3 110 0.15', '0.2 -0.12 0.3 0 0.15'): a.append(line('pstop ' + c, tag='_r5pm110', PERT_M=1.1))
b = []
for c in ('0 L 110', '0 L 60', '0 L 25', '10 L 110', '15 L 110', '20 L 110', '25 L 110', '40 L 110', '60 L 110', '20 L 25', '15 L 25', '20 both 110', '60 both 110'): b.append(line('lower %s 8' % c))
for c in ('0 L 110', '0 L 25', '15 L 110', '20 L 110', '25 L 110', '60 L 110'): b.append(line('lower %s 8' % c, X_LOWER_V='0.013'))
for c in ('0 L 110', '0 L 25', '20 L 110', '25 L 25'): b.append(line('lower %s 8' % c, X_TRIP_N='50'))
b.append(line('lower 60 L 110 8 nocheck')); b.append(line('lower 20 L 110 8', tag='_r5pm110', PERT_M=1.1))
c = []
for h in ('0.008', '0.010', '0.012', '0.015', '0.020'): c.append(line('stepempty both 0.3', X_STEP_AT='1.12', X_STEP_H=h))
for h in ('0.020', '0.025'): c.append(line('stepempty both 0.3', X_STEP_AT='3.0', X_STEP_H=h))
for h in ('0.020', '0.025', '0.030'):
    for v in ('0.3', '0.4'): c.append(line('liftpeak step both ' + v, X_STEP_AT='3.0', X_STEP_H=h))
c.append(line('liftpeak step both 0.4', X_STEP_AT='3.0', X_STEP_YAW='20')); c.append(line('liftpeak step both 0.3', X_STEP_AT='3.0', X_STEP_YAW='20')); c.append(line('stepempty one 0.4', X_STEP_AT='3.0'))
c.append(line('stepempty both 0.3', X_STEP_AT='3.0', X_STEP_H='0.030', X_STEP_YAW='20')); c.append(line('lat 110')); c.append(line('lat 0'))
k = [conv(l) for l in src if 'liftpeak kerb' in l and ('_r4cap12 ' in l or '_r4cap12t20 ' in l)]
open('q_r5_a.txt', 'w').writelines(a + c + k + b); print('pstop', len(a), 'steps', len(c), 'kerb', len(k), 'lower', len(b))
