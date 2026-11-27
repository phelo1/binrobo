#!/usr/bin/env python3
"""Assemble the revision 5 reply note from its parts and fill the placeholders. usage: assemble_r5.py <out.md>"""
import json, re, sys, os
D = os.path.dirname(os.path.abspath(__file__)); rd = lambda n: open(os.path.join(D, n)).read().rstrip() + '\n'
C = rd('C_static.md'); i4 = C.index('## 4. What changed in the design')
parts = [rd('0_head.md'), rd('A_directions.md'), rd('B_findings.md'), rd('D_results.md'), C[:i4].rstrip() + '\n', rd('E_results2.md'), rd('F_driving.md'), C[i4:].rstrip() + '\n', rd('G_tail.md')]
s = '\n'.join(parts)
fill = json.load(open(os.path.join(D, 'fill_r5.json')))
for k, v in fill.items(): s = s.replace('«%s»' % k, v)
left = sorted(set(re.findall(r'«[A-Z0-9_]+»', s)))
if left: print('PLACEHOLDERS LEFT:', left)
s = re.sub(r'\n{3,}', '\n\n', s)
open(sys.argv[1], 'w').write(s); print('written', sys.argv[1], len(s), 'chars', len(s.split()), 'words')
