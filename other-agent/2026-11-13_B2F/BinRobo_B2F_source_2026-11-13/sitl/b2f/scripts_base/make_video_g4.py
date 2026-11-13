#!/usr/bin/env python3
"""Rev G4 video of the NEW scenarios (target 2-3 min): chapters with title cards -> out/G4/Bin_Tug_G4_SITL.mp4
Usage: make_video_g4.py render <worker 0|1>   |   make_video_g4.py concat"""
import json, os, subprocess, sys, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); G4 = os.path.join(ROOT, 'out', 'G4'); CL = os.path.join(G4, 'clips')
os.makedirs(CL, exist_ok=True)
CHAPTERS = [
    ('1  Vehicle-approach stop (24 GHz radar front + rear, lidar)', ['Vehicle-like target closing within ~5 m (or time-to-contact < 3 s): HOLD + beacon + speaker',
      'Resume when nothing is closing and no vehicle-sized object within 4 m for 3 s'],
     [('s23a_vehicle_oncoming', 13), ('s23c_vehicle_passing', 12), ('s23b_vehicle_behind', 10), ('s23d_no_false_stop', 7)]),
    ('2  Pinch-zone fix: adjacent bins exempt, people are not', ['Our bin on an occupied programmed slot is exempt (bin-sized, still, on the slot)',
      'A person against that bin is still refused; owner talks through the tug (2-way audio)'], [('s16c_release_person_by_bin', 14), ('s10a_two_bin_drop', 12)]),
    ('3  Teach and repeat', ['Teach (RC/app): route + exact home and drop poses -> route file', 'Repeat at night from the route file'],
     [('s21a_teach_route', 13), ('s21b_repeat_drop', 11)]),
    ('4  Bin calendar + programmable drop layout', ['Alternate weeks from an anchor date: week A black+brown, week B green+brown',
      'Week B uses a custom layout (spot M moved, 0.75 m hedge clearance, handle +8 deg)'], [('s22b_calendar_week_b', 14)]),
    ('5  Three-bin evening, real pickup', ['Drop from 18:00, overnight dock recharge (pack heater), pickup must end by 21:00'], [('s20b_three_bin_pickup', 14)]),
    ('6  Adaptive drop spot + keep-out zones', ['Slot checked by lidar before release; blocked -> nearest clear legal alternate, else hold + alert',
      'Pickup goes to where the bin was really left (drop log + tag search); routes avoid user keep-outs'],
     [('s24b_all_slots_blocked', 8), ('s24d_pickup_logged_pose', 9), ('s24c_keepout_route', 7), ('s24a_home_slot_car', 9)]),
]
FONT = cv2.FONT_HERSHEY_SIMPLEX

def card(path, lines, secs=3.0):
    img = np.zeros((540, 960, 3), np.uint8); img[:] = (40, 30, 22); y = 150
    for t, sc, col in lines:
        cv2.putText(img, t, (50, y), FONT, sc, col, 2 if sc > 0.75 else 1, cv2.LINE_AA); y += int(60 * sc) + 14
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '960x540', '-r', '10', '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '26', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for k in range(int(secs * 10)): p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()

CLIPS = [c for ch in CHAPTERS for c in ch[2]]
if sys.argv[1] == 'render':
    k = int(sys.argv[2])
    for i, (name, tgt) in enumerate(CLIPS):
        if i % 2 != k or not os.path.exists(os.path.join(G4, name, 'trace.json')): continue
        subprocess.run([sys.executable, os.path.join(HERE, 'render.py'), name, str(tgt), os.path.join(CL, name + '.mp4')])
else:
    S = json.load(open(os.path.join(G4, 'report', 'g4_summary.json')))
    W, Y, G = (255, 255, 255), (0, 255, 255), (210, 210, 210)
    card(os.path.join(CL, '_intro.mp4'), [('Bin Tug - work package G4 (SIMULATION)', 1.0, W),
        ('Real ArduPilot Rover 4.6.2 firmware (JSON SITL) + Pi companion state machine', 0.6, G),
        ('New: vehicle-approach stop, keep-left, teach & repeat, bin calendar,', 0.6, G),
        ('drop layout, two-way audio, pinch-zone fix for side-by-side bins', 0.6, G),
        ('Long drives are time-lapsed (factor top right). Nothing here is built yet.', 0.55, Y)], 4)
    files = ['_intro.mp4']
    for ci, (title, sub, clips) in enumerate(CHAPTERS):
        have = [n for n, _ in clips if os.path.exists(os.path.join(CL, n + '.mp4'))]
        if not have: continue
        cp = os.path.join(CL, '_ch%d.mp4' % ci)
        card(cp, [(title, 0.8, W)] + [(s, 0.55, G) for s in sub], 2.5); files.append(os.path.basename(cp)); files += [n + '.mp4' for n in have]
    lines = [('G4 results (SIMULATION)', 1.0, W),
             ('Regression: %d / %d as expected; robustness (4 seeds): %d / %d' % (S['regress_ok'], S['regress_n'], S['robust_ok'], S['robust_n']), 0.6, G)]
    if S.get('kl'): lines.append(('Keep-left gap to the left lane edge: mean %.2f m, min %.2f m (target 0.3-0.5)' % (S['kl']['mean'], S['kl']['min']), 0.6, G))
    if S.get('margin') is not None: lines.append(('3-bin evening: pickup done %s, margin %.0f min to 21:00' % (S['pick_end'], S['margin']), 0.6, G))
    lines.append(('Report: RESULTS_G4_sitl.pdf', 0.6, Y))
    card(os.path.join(CL, '_outro.mp4'), lines, 4); files.append('_outro.mp4')
    open(os.path.join(CL, 'list.txt'), 'w').write(''.join("file '%s'\n" % f for f in files))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(CL, 'list.txt'), '-c:v', 'libx264', '-preset', 'veryfast',
                    '-crf', '26', '-pix_fmt', 'yuv420p', os.path.join(G4, 'Bin_Tug_G4_SITL.mp4')], check=True)
    print('video ok', files)
