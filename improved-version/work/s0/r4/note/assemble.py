#!/usr/bin/env python3
"""Put the note together from its parts, in section order, and fill the placeholders."""
import re, sys, json
parts = ''.join(open(f).read().rstrip() + '\n\n' for f in ('A_findings.md', 'B1_results.md', 'B2_results.md', 'L_lane.md', 'C_rest.md', 'D_end.md'))
chunks = re.split(r'(?m)^(?=(?:## |### 3\.\d ))', parts); sec = {}
for c in chunks:
    if not c.strip(): continue
    h = c.splitlines()[0]; m = re.match(r'### (3\.\d)', h) or re.match(r'## (\d+)\.', h) or re.match(r'## (Files|Sources)', h); assert m, h; sec[m.group(1)] = c.rstrip() + '\n\n'
order = ['1', '2', 'R', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '4', '5', '6', '7', '8', '9', 'Files', 'Sources']
sec['R'] = '## 3. Results\n\n'
out = open('E_head.md').read().rstrip() + '\n\n' + ''.join(sec[k] for k in order)
F = json.load(open('fill.json'))
for k, v in F.items(): out = out.replace('«%s»' % k, v)
left = re.findall(r'«[^»]*»', out); assert not left, left
assert set(sec) == set(order), set(sec) ^ set(order)
open(sys.argv[1], 'w').write(out.rstrip() + '\n'); print('wrote', sys.argv[1], len(out), 'chars', len(out.split()), 'words')
