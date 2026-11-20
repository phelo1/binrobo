#!/usr/bin/env python3
"""Volume and bounding box of every drawn solid of a model script (runs the script, reads its PARTS list).
usage: solids_list.py <model script> <out.json>"""
import sys, json, runpy, os
script, out = sys.argv[1], sys.argv[2]
sys.argv = [script]; g = runpy.run_path(script, run_name='solids')
rows = []
for p in g['PARTS']:
    s = p[3]; bb = s.BoundingBox()
    rows.append(dict(name=p[0], grp=p[1], col=p[2], src=p[5], vol_cm3=round(s.Volume() / 1000.0, 1), bb=[round(v, 1) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)]))
json.dump(rows, open(out, 'w'), indent=0); print(len(rows), 'solids ->', out)
