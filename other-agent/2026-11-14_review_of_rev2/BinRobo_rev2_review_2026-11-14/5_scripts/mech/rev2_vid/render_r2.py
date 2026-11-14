#!/usr/bin/env python3
"""[independent tester 2026-11-14] Revision 2 lane videos: the B2-F lane video tooling (work/b2f_lanephys/render_lane.py, software
rasteriser, no OpenGL) re-used unchanged, pointed at the rev2 recordings (runs/ symlinks -> b2f_lanephys/runs_r2b_*), own shot lists
and captions. Chunked: render_r2.py <video> [budget_s]; then render_r2.py <video> --final.  --count prints frames/length."""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); P = '/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c'
sys.path.insert(0, P + '/work/b2f_lanephys')
import render_lane as RL
from PIL import Image, ImageDraw
RL.HERE = HERE
RL.OUT = '/workspace/work/out/rev2/videos'; os.makedirs(RL.OUT, exist_ok=True)
RL.CAPTION = 'Digital twin simulation - not field footage. Revision 2 independent re-test (MuJoCo 4.0.1)'
F = RL.F; W, H, FPS = RL.W, RL.H, RL.FPS
def title_card(vid, sub=None, secs=4.0):
    im = Image.new('RGB', (W, H), (14, 20, 30)); dr = ImageDraw.Draw(im)
    dr.text((80, 200), RL.CAPTION, font=F(28, True), fill=(255, 210, 80))
    dr.text((80, 270), vid['title'], font=F(34, True), fill=(255, 255, 255)); y = 340
    for ln in (sub or vid.get('sub', [])): dr.text((80, y), ln, font=F(22), fill=(200, 210, 225)); y += 36
    dr.text((80, H - 70), 'BinRobo revision 2 (simB2hx_r2, 119.39 kg in sim)  |  MuJoCo 4.0.1, dt 0.5 ms  |  B2-F CAD meshes posed from the sim  |  software rasteriser', font=F(16), fill=(140, 150, 165))
    return [im] * int(secs * FPS)
RL.title_card = title_card
def vid_def(name):
    V = {
     'P1_filled': dict(title='P1 - full 240 L (110 kg), home -> pad A, pothole FILLED', runs=['pf_P1'], sub=['Grab at home (x6), transit 610 m (time-lapse x40), set-down at pad A (x6).',
                'Revision 2, 119.39 kg. Lane: 1:4 ramp on the 40 mm step, trench covered, pothole filled.', 'Result: PASS, 1308 s, 15.2 Wh, bin-wheel clearance min 50 mm.']),
     'P1_pothole_open': dict(title='P1 - pothole OPEN: stuck 1140 s, scored PASS', runs=['po_P1'], sub=['Same mission, 60 mm pothole as-is at s 550. Transit x60, trapped section x20 then x100.',
                'The robot circles in the pothole for 1140 s (lat 0 -> 0.8 m limit cycle) and escapes at t 2285 s.', 'Lane verdict PASS (no time limit). With a 120 s stuck limit: FAIL. 50.6 Wh vs 15.2 Wh.']),
     'P5g_trench_open': dict(title='P5g - open 200 mm trench, 110 kg: stall', runs=['pf_P5g'], sub=['Real time x1.5. Trench 40 x 200 mm as-is (not covered).', 'Result: FAIL - drive stalls at s 455.1 (no progress 12 s).']),
     'step_sharp_up_down': dict(title='Sharp 40 mm step, down and up, 110 kg (3 kN lift cap)', runs=['pf_P5a', 'pf_P5d'], sub=['P5a: step DOWN (outbound). P5d: pivot, then step UP carrying the bin back. Real time x1.5.',
                'Revision 2 with rocker: both PASS in MuJoCo 4.0.1 (MuJoCo 3.17 stalls on box edges - artefact).']),
     'P4a_wet_descent_stop': dict(title='P4a - 12 % wet-leaf descent, 110 kg: stop and hold', runs=['pf_P4a'], sub=['Downhill on the 12 % pitch, mu 0.35 (wet leaves), stop and hold 10 s on the spring brakes. x4.',
                'The 12 % pitch is an ASSUMED overlay on the EU-DEM profile. Result: PASS.']),
    }
    v = V[name]; v['name'] = name; sh = []
    if name == 'P1_filled':
        sh = [dict(run='pf_P1', t0=0.04, t1=39.8, speed=6.0, cam='orbit'), dict(run='pf_P1', t0=39.8, t1=1288.9, speed=40.0, cam='chase'), dict(run='pf_P1', t0=1286.9, t1=1308.1, speed=6.0, cam='orbit')]
    elif name == 'P1_pothole_open':
        sh = [dict(run='po_P1', t0=39.8, t1=1105.0, speed=60.0, cam='chase'), dict(run='po_P1', t0=1105.0, t1=1300.0, speed=20.0, cam='chase'),
              dict(run='po_P1', t0=1300.0, t1=2300.0, speed=100.0, cam='chase'), dict(run='po_P1', t0=2300.0, t1=2443.3, speed=40.0, cam='chase')]
    elif name == 'P5g_trench_open': sh = [dict(run='pf_P5g', t0=927.6, t1=968.6, speed=1.5, cam='side', label='P5g open trench - FAIL (stall s 455.1)')]
    elif name == 'step_sharp_up_down':
        sh = [dict(run='pf_P5a', t0=601.0, t1=628.6, speed=1.5, cam='side', label='P5a sharp 40 mm step DOWN, 110 kg - PASS'),
              dict(run='pf_P5d', t0=654.0, t1=682.3, speed=1.5, cam='side', label='P5d sharp 40 mm step UP, 110 kg - PASS')]
    elif name == 'P4a_wet_descent_stop': sh = [dict(run='pf_P4a', t0=281.4, t1=376.7, speed=4.0, cam='chase', label='P4a 12 % wet descent, stop and hold - PASS')]
    v['shots'] = sh; return v
RL.vid_def = vid_def
_end0 = RL.end_card
def end_card(vid):
    ims = _end0(vid)
    if vid['name'] == 'P1_pothole_open':
        im = ims[0].copy(); dr = ImageDraw.Draw(im)
        dr.text((80, 330), 'Tester re-score with a 120 s stuck limit: FAIL (stuck in the pothole s 549-552 for 1140 s)', font=F(22, True), fill=(255, 120, 100))
        ims = [im] * len(ims)
    return ims
RL.end_card = end_card
if __name__ == '__main__':
    n = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == '--final':
        RL.finalize(n); src = os.path.join(RL.OUT, 'B2F_lane_%s.mp4' % n); dst = os.path.join(RL.OUT, 'rev2_%s.mp4' % n); os.replace(src, dst); print('->', dst)
    elif len(sys.argv) > 2 and sys.argv[2] == '--count':
        v = vid_def(n); L = RL.frame_list(v); print(n, len(L), 'frames', len(L) / FPS, 's')
    else: RL.render_video(n, float(sys.argv[2]) if len(sys.argv) > 2 else 95.0)
