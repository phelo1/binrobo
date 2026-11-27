#!/usr/bin/env python3
"""Video 4: one grab of a full 240 L bin by the improved version, filmed close up.
This one is a fresh run of the other agent's gate simulation (their grab routine, unchanged) with the improved-version
switches, started 60 mm and 4 degrees off line (inside the frozen test range of 80 mm and 6 degrees). The joint positions are
recorded 50 times a second while it runs and then drawn. usage: grab_film.py [dy_m] [dyaw_deg]"""
import os, sys, math, json, subprocess
os.environ.update(CGB_F9='1', CMP_SIM='simB2hx', X_LIFT_RANGE='0.35', X_ROCKER='1', B2F_PAD_IN='-0.005', CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}', B2_DOCK='front')
os.environ.setdefault('MUJOCO_GL', 'egl')
import numpy as np, mujoco
from PIL import Image, ImageDraw, ImageFont
CG = '/home/claude/b2f_run/revG/sim/cg'
for p in (os.path.join(CG, '..', 'it1'), os.path.join(CG, '..', '..', 'g6'), CG, os.path.join(CG, 'b2'), os.path.join(CG, 'h2')): sys.path.insert(0, p)
os.chdir(CG)
REC = []; CTX = dict(R=None, next=0.0); _step = mujoco.mj_step
def step_rec(m, d, *a):
    _step(m, d, *a)
    if d.time >= CTX['next']:
        R = CTX['R']; REC.append((float(d.time), d.qpos.copy(), str(getattr(R, 'phase', '')) if R is not None else '')); CTX['next'] = d.time + 0.02
mujoco.mj_step = step_rec
import importlib; B = importlib.import_module('simB2hx')
from bins_g5 import BINS
sys.path.insert(0, '/home/claude/s0/video');
OUT = '/home/claude/s0/video/out'; os.makedirs(OUT, exist_ok=True)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F = lambda n, b=False: ImageFont.truetype(FB if b else FR, n)
STEEL = (0.30, 0.36, 0.44, 1); BLACK = (0.07, 0.07, 0.08, 1); ORANGE = (0.95, 0.52, 0.10, 1); RED = (0.90, 0.16, 0.10, 1)
COLOURS = dict(tray=(0.22, 0.27, 0.34, 1), bumper=(0.95, 0.80, 0.15, 1), rearface=(0.6, 0.65, 0.7, 0.0), guard0=(0.85, 0.88, 0.92, 0.22), guard1=(0.85, 0.88, 0.92, 0.22),
               flare0=(0.85, 0.88, 0.92, 0.22), flare1=(0.85, 0.88, 0.92, 0.22), antitip0=BLACK, antitip1=BLACK, driveL=BLACK, driveR=BLACK, casterL=BLACK, casterR=BLACK,
               faceplate=ORANGE, tooth=ORANGE, nib=ORANGE, padg=(0.98, 0.85, 0.20, 1), keeparm=(0.5, 0.5, 0.5, 0.0), keeptip=(0.5, 0.5, 0.5, 0.0), keeptip2=(0.5, 0.5, 0.5, 0.0),
               binwheelL=RED, binwheelR=RED, lid=(0.07, 0.25, 0.50, 1), ground=(0.56, 0.55, 0.50, 1))
FRAME = [(-0.37, 0.98, 0.405, 0.455, 0.36, 0.41), (-0.37, 0.98, -0.455, -0.405, 0.36, 0.41), (0.465, 0.515, -0.405, 0.405, 0.36, 0.41), (0.93, 0.98, -0.405, 0.405, 0.36, 0.41),
         (0.47, 0.52, 0.175, 0.225, 0.41, 1.37), (0.47, 0.52, -0.225, -0.175, 0.41, 1.37), (0.47, 0.52, -0.23, 0.23, 1.37, 1.42), (0.98, 1.02, -0.02, 0.02, 0.27, 1.06),
         (0.93, 0.98, 0.405, 0.455, 0.20, 0.36), (0.93, 0.98, -0.455, -0.405, 0.20, 0.36)]

dy = float(sys.argv[1]) if len(sys.argv) > 1 else 0.06; dyaw = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
binkey = 'ESE240SL'; p = B.bin_params(binkey); p['fill'] = BINS[binkey]['fill_full']
S = B.SimB(binkey, p, tug_pose=B.start_pose(p, dy, dyaw)); R = B.RunnerB(S); CTX['R'] = R
RECF = os.path.join(OUT, 'grab_film_rec_%+.0f_%+.0f.npz' % (dy * 1000, dyaw))
if os.environ.get('REUSE') == '1' and os.path.exists(RECF):     # redraw from the saved recording of the same run (no new simulation)
    z = np.load(RECF, allow_pickle=True); REC[:] = [(float(t), q, str(s_)) for t, q, s_ in zip(z['t'], z['q'], z['ph'])]; g = json.load(open(os.path.join(OUT, 'grab_film_run.json')))
    class _C:  # captured flag from the saved result
        pass
    S.captured = lambda: g.get('result') == 'success'
else:
    g = B.grab(R); R.phase = 'Holding the bin'; R.hold(); R.run_for(2.0)
    np.savez_compressed(RECF, t=np.array([r[0] for r in REC]), q=np.array([r[1] for r in REC]), ph=np.array([r[2] for r in REC]))
print('grab result:', g.get('result'), '| captured', S.captured(), '| docked offset %s mm' % g.get('dock_dy_mm'), '| wheel clearance %s mm' % g.get('wheel_clear_mm'), '| frames', len(REC), '| sim time %.1f s' % REC[-1][0])
ph = [];
for t, q, s_ in REC:
    if not ph or ph[-1][1] != s_: ph.append((round(t, 1), s_))
print('phases:', ph)
jl = S.m.jnt_qposadr[mujoco.mj_name2id(S.m, mujoco.mjtObj.mjOBJ_JOINT, 'lift')]; ql = np.array([r[1][jl] for r in REC]); tl_ = np.array([r[0] for r in REC])
print('lift joint: at load-on %.3f m, at the end %.3f m, rise after load-on %.0f mm' % (ql[np.searchsorted(tl_, 32.0)], ql[-1], 1000 * (ql[-1] - ql[np.searchsorted(tl_, 32.0)])))
# plain captions for the phases of their grab routine. Their labels for the pad toggle, the +100 mm lift and the keeper do not
# describe the improved version (fixed pad, 150 mm carry lift, no keeper on the front wall), so those are reworded here.
CAP = [('0 Comb', 'Comb moves to its approach height'), ('1 Approach', 'Reversing toward the bin, steering by the rear camera'), ('1b', 'Final approach at 0.06 m/s'),
       ('1c-a', 'Stops and turns on the spot to square up to the bin'), ('1c ', 'Creeps in at 0.03 m/s until the comb is under the lip'), ('2 Lift', 'Comb rises under the lip until it takes the load'),
       ('2b', 'Bin settles against the fixed pad'), ('2c', 'Lifts the bin about 150 mm to its carrying height'), ('3 ', 'Bin held at carrying height'), ('Holding', 'Bin held at carrying height')]
def caption(s_):
    for k, v in CAP:
        if s_.startswith(k): return v
    return 'Starting 1.2 m from the bin'
json.dump(dict(result=g.get('result'), dy=dy, dyaw=dyaw, dock_dy_mm=g.get('dock_dy_mm'), wheel_clear_mm=g.get('wheel_clear_mm'), phases=ph), open(os.path.join(OUT, 'grab_film_run.json'), 'w'), indent=1, default=str)

# ---------------------------------------------------------------- drawing
m, d = S.m, S.d; W, H = 1280, 720; VW, VH = 1280, 600; IW, IH = 400, 300
m.vis.global_.offwidth = max(VW, m.vis.global_.offwidth); m.vis.global_.offheight = max(VH, m.vis.global_.offheight)
m.vis.quality.shadowsize = 4096; m.vis.headlight.ambient[:] = 0.38; m.vis.headlight.diffuse[:] = 0.30
m.stat.extent = 4.0; m.vis.map.shadowclip = float(os.environ.get('SHCLIP', '10')); m.vis.map.shadowscale = 0.9   # drawing only: shadow map sized to the scene (the default gave speckles on the ground plane)
bid = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n); b_tug, b_bin, b_bw, b_lift = bid('tug'), bid('bin'), bid('bwL'), bid('lift')
for gi in range(m.ngeom):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, gi) or ''
    if nm in COLOURS: m.geom_rgba[gi] = COLOURS[nm]
    elif m.geom_bodyid[gi] == b_bin: m.geom_rgba[gi] = (0.10, 0.33, 0.62, 1)
    elif nm.startswith('ground') or m.geom_type[gi] == mujoco.mjtGeom.mjGEOM_PLANE: m.geom_rgba[gi] = COLOURS['ground']
ren = mujoco.Renderer(m, height=VH, width=VW); ren2 = mujoco.Renderer(m, height=IH, width=IW); opt = mujoco.MjvOption()
cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE; cam2 = mujoco.MjvCamera(); cam2.type = mujoco.mjtCamera.mjCAMERA_FREE
wr = float(p['wheel_r'])

def shot(rn, cm):
    rn.update_scene(d, cm, opt); scn = rn.scene; Rm = d.xmat[b_tug].reshape(3, 3); pt = d.xpos[b_tug]
    for (x0, x1, y0, y1, z0, z1) in FRAME:
        c = pt + Rm @ np.array([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); gg = scn.geoms[scn.ngeom]
        mujoco.mjv_initGeom(gg, mujoco.mjtGeom.mjGEOM_BOX, np.array([(x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2]), c, Rm.ravel().copy(), np.array(STEEL, np.float32)); scn.ngeom += 1
    if scn.nlight < len(scn.lights):
        L = scn.lights[scn.nlight]; dv = np.array([0.35, -0.25, -1.0]); dv /= np.linalg.norm(dv); L.pos[:] = np.array(cm.lookat) - 12.0 * dv; L.dir[:] = dv
        for nm, val in (('directional', 1), ('type', 1), ('castshadow', 1), ('headlight', 0)):
            try: setattr(L, nm, val)
            except Exception: pass
        L.ambient[:] = 0.0; L.diffuse[:] = 0.55; L.specular[:] = 0.1; L.cutoff = 90.0; L.exponent = 1.0; L.attenuation[:] = (1, 0, 0); scn.nlight += 1
    img = rn.render().copy(); sky = (img.sum(axis=2) == 0)
    if sky.any():
        grad = np.linspace(0, 1, img.shape[0])[:, None]; col = (np.array([150, 185, 225])[None, :] * (1 - grad) + np.array([222, 232, 240])[None, :] * grad).astype(np.uint8)
        img[sky] = np.repeat(col[:, None, :], img.shape[1], axis=1)[sky]
    return img

# camera: fixed, side-on to the approach, centred between the bin and the robot's start; inset follows the comb
d.qpos[:] = REC[0][1]; mujoco.mj_forward(m, d); m.stat.center[:] = d.xpos[b_bin]; pb0 = d.xpos[b_bin].copy(); pt0 = d.xpos[b_tug].copy(); ax = pt0[:2] - pb0[:2]; yaw_ax = math.degrees(math.atan2(ax[1], ax[0]))
SPEED = 2.0; FPS = 25; out = os.path.join(OUT, '4_grab_full_240L_close_up.mp4')
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                       '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out if not os.environ.get('ONLYFRAMES') else '/tmp/_unused.mp4'], stdin=subprocess.PIPE)
T = np.array([r[0] for r in REC]); n = 0; tend = T[-1]; ONLY = [float(x) for x in os.environ.get('ONLYFRAMES', '').split(',') if x]
while True:
    ts = T[0] + n / FPS * SPEED
    if ONLY:
        if n >= len(ONLY): break
        ts = ONLY[n]
    if ts > tend: break
    i = int(np.clip(np.searchsorted(T, ts), 0, len(T) - 1)); d.qpos[:] = REC[i][1]; mujoco.mj_forward(m, d)
    pb = d.xpos[b_bin]; ptg = d.xpos[b_tug]
    cam.lookat[:] = (pb0[0] + 0.75 * math.cos(math.radians(yaw_ax)), pb0[1] + 0.75 * math.sin(math.radians(yaw_ax)), 0.66); cam.distance = 3.5; cam.azimuth = yaw_ax + 105.0; cam.elevation = -8.0
    pl = d.xpos[b_lift]; cam2.lookat[:] = (pl[0] - 0.10 * math.cos(math.radians(yaw_ax)), pl[1] - 0.10 * math.sin(math.radians(yaw_ax)), pl[2] + 0.02); cam2.distance = 1.15; cam2.azimuth = yaw_ax + 100.0; cam2.elevation = -4.0
    img = Image.new('RGB', (W, H), (18, 20, 24)); img.paste(Image.fromarray(shot(ren, cam)), (0, 56)); ins = Image.fromarray(shot(ren2, cam2)); img.paste(ins, (W - IW - 14, 70))
    dr = ImageDraw.Draw(img); dr.rectangle([W - IW - 15, 69, W - 14, 70 + IH], outline=(255, 255, 255), width=2)
    dr.rectangle([W - IW - 14, 70, W - IW + 196, 94], fill=(18, 20, 24)); dr.text((W - IW - 8, 73), 'Close-up: comb and bin lip', font=F(14, True), fill=(255, 255, 255))
    clr = float(min(d.xpos[bid('bwL')][2], d.xpos[bid('bwR')][2]) - wr)
    lat = float(S.bin_in_tug()[1]) * 1000.0
    dr.text((20, 12), 'Improved version picking up a full 240 L bin, starting %.0f mm and %.0f degrees off line' % (abs(dy) * 1000, abs(dyaw)), font=F(25, True), fill=(255, 255, 255))
    dr.rectangle([0, 656, W, H], fill=(18, 20, 24))
    dr.text((20, 661), caption(REC[i][2]), font=F(18, True), fill=(255, 220, 90))
    dr.text((640, 662), 'Bin off the robot\'s centre line: %3.0f mm     Bin wheels above ground: %3.0f mm' % (abs(lat), max(clr, 0.0) * 1000), font=F(16), fill=(230, 230, 230))
    dr.text((20, 688), 'Simulation (MuJoCo 4.0.1, the gate test\'s own grab routine), 2x speed, not field footage. The bin is a catalogue model, not Brian\'s measured bin.', font=F(12), fill=(170, 170, 170))
    dr.text((20, 703), 'Orange: lifting comb. Yellow block: pad. Red: the bin\'s own wheels. Mast and frame are drawn from the CAD for clarity; the other shapes are the physics model.', font=F(12), fill=(170, 170, 170))
    if ONLY: img.save('/home/claude/s0/video/chk/v4_test_%d.png' % n)
    else: ff.stdin.write(np.asarray(img).tobytes())
    n += 1
    if n % 100 == 0: print('frame', n, 'sim t %.1f' % ts, REC[i][2][:50], 'clr %.3f lat %.0f' % (clr, lat), flush=True)
ff.stdin.close(); ff.wait(); print('WROTE', out, 'frames', n)
