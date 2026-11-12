#!/usr/bin/env python3
"""B1 with the 640 mm self-aligning comb (tag _f9_fwp32): build a merged result set res/fwmerge/B1_*_fwm.json = the fwp32 run where
one exists (cmp/res), otherwise the B1 final run (it1/res *_f9) as an INHERITED result, then score it with summarize_cmp.py.
Provenance -> res/gate_fw_provenance.json. Inherited items are those the comb width cannot change much (drive-limited or static)."""
import os, json, glob, shutil, subprocess
H = os.path.dirname(os.path.abspath(__file__)); IT1 = os.path.join(H, '..', 'it1', 'res'); RES = os.path.join(H, 'res'); M = os.path.join(RES, 'fwmerge')
os.makedirs(M, exist_ok=True); prov = {}
for f in glob.glob(os.path.join(IT1, 'B1_*_f9.json')):
    n = os.path.basename(f)[3:-8]; fw = os.path.join(RES, 'B1_%s_f9_fwp32.json' % n)
    src = fw if os.path.exists(fw) else f; prov[n] = 'fwp32 run' if src == fw else 'inherited from B1 final (it1/res)'
    shutil.copy(src, os.path.join(M, 'B1_%s_fwm.json' % n))
json.dump(prov, open(os.path.join(RES, 'gate_fw_provenance.json'), 'w'), indent=1)
r = subprocess.run(['python3', os.path.join(H, 'summarize_cmp.py'), 'B1_', '_fwm', M, 'B1'], capture_output=True, text=True); print(r.stdout[-3000:], r.stderr[-2000:])
print({k: v for k, v in prov.items() if v == 'fwp32 run'})
