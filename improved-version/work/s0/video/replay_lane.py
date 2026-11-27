#!/usr/bin/env python3
"""Replays saved lane-physics recordings (25 fps world poses of the 16 robot / bin bodies) in the same MuJoCo model
and world the run used, and writes an MP4. Nothing is re-simulated: every frame shows the poses the test recorded.
The model is the simulation's own (boxes, cylinders, the bin hull), not the CAD drawing.

usage:  replay_lane.py step      -> video 1: improved version, full 240 L bin, over the sharp 40 mm step
        replay_lane.py return    -> video 2: empty return at the step, sharp (stalls) beside 1:4 ramp (passes)
Environment for the improved version must be set by the caller (X_SIM, X_ROCKER, X_LIFT_RANGE, B2F_PAD_IN, CGB_GEO).
"""
import os, sys, json, glob, math, subprocess
os.environ.setdefault('MUJOCO_GL', 'egl')
import numpy as np, mujoco
from PIL import Image, ImageDraw, ImageFont
LANE = '/home/claude/b2f_run/work/b2f_lanephys'
sys.path.insert(0, LANE)
import lanerun_x as LR
import lane_world as LW
# Display speed-up: the lane model's height map covers the whole 633 m lane (2.1 million cells), which the software renderer
# redraws for every frame. Nothing is simulated here, so only the part within CROP metres of the step is loaded for drawing.
CROP = 20.0; _hf = LW.hfield_grid
def _hf_crop(*a, **k):
    H, (x0, x1, y0, y1, nr, nc) = _hf(*a, **k); nr, nc = int(nr), int(nc); xs = np.linspace(x0, x1, nc); ys = np.linspace(y0, y1, nr)
    c = LW.point(LW.FEAT['step']['s'], 0.0); jx = np.where(np.abs(xs - c[0]) <= CROP)[0]; iy = np.where(np.abs(ys - c[1]) <= CROP)[0]
    return H[iy[0]:iy[-1] + 1, jx[0]:jx[-1] + 1].copy(), (float(xs[jx[0]]), float(xs[jx[-1]]), float(ys[iy[0]]), float(ys[iy[-1]]), len(iy), len(jx))
LW.hfield_grid = _hf_crop
OUT = '/home/claude/s0/video/out'; os.makedirs(OUT, exist_ok=True)
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F = lambda n, b=False: ImageFont.truetype(FB if b else FR, n)
FOOT = 'Simulation replay (MuJoCo 4.0.1), not field footage. The lane and the bins are assumed, not surveyed.'
FOOT2 = 'Yellow line: step edge. Red: the bin\'s own wheels. Near-side hedge not drawn. Mast and frame are drawn from the CAD for clarity; the other shapes are the physics model.'


STEEL = (0.30, 0.36, 0.44, 1); BLACK = (0.07, 0.07, 0.08, 1); ORANGE = (0.95, 0.52, 0.10, 1); RED = (0.90, 0.16, 0.10, 1)
COLOURS = dict(tray=(0.22, 0.27, 0.34, 1), bumper=(0.95, 0.80, 0.15, 1), rearface=(0.6, 0.65, 0.7, 0.0), guard0=(0.85, 0.88, 0.92, 0.22), guard1=(0.85, 0.88, 0.92, 0.22),
               flare0=(0.85, 0.88, 0.92, 0.22), flare1=(0.85, 0.88, 0.92, 0.22), antitip0=BLACK, antitip1=BLACK, driveL=BLACK, driveR=BLACK, casterL=BLACK, casterR=BLACK,
               faceplate=ORANGE, tooth=ORANGE, nib=ORANGE, padg=(0.98, 0.85, 0.20, 1), keeparm=(0.5, 0.5, 0.5, 0.0), keeptip=(0.5, 0.5, 0.5, 0.0), keeptip2=(0.5, 0.5, 0.5, 0.0),
               binwheelL=RED, binwheelR=RED, lid=(0.07, 0.25, 0.50, 1))
# frame members from the CAD drawing, in the robot frame (x forward from the drive axle, z up from the ground), metres: (x0,x1,y0,y1,z0,z1)
# They are not physics shapes; they are drawn so the lifting carriage does not appear to float. Mast 60 mm taller than B2-F (350 mm travel).
FRAME = [(-0.37, 0.98, 0.405, 0.455, 0.36, 0.41), (-0.37, 0.98, -0.455, -0.405, 0.36, 0.41), (0.465, 0.515, -0.405, 0.405, 0.36, 0.41), (0.93, 0.98, -0.405, 0.405, 0.36, 0.41),
         (0.47, 0.52, 0.175, 0.225, 0.41, 1.37), (0.47, 0.52, -0.225, -0.175, 0.41, 1.37), (0.47, 0.52, -0.23, 0.23, 1.37, 1.42), (0.98, 1.02, -0.02, 0.02, 0.27, 1.06),
         (0.93, 0.98, 0.405, 0.455, 0.20, 0.36), (0.93, 0.98, -0.455, -0.405, 0.20, 0.36)]


class Scene:
    def __init__(self, runs_dir, rid, w, h, hide=None):
        d = os.path.join(LANE, runs_dir, rid); self.res = json.load(open(os.path.join(d, 'result.json'))); cfg = self.res['cfg']
        T, Q, H, P = [], [], [], []
        for f in sorted(glob.glob(os.path.join(d, 'rec_*.npz'))):
            r = np.load(f); T.append(r['t']); Q.append(r['q']); H.append(r['hud']); P += list(r['ph'])
        self.t = np.concatenate(T); self.q = np.concatenate(Q); self.hud = np.concatenate(H); self.ph = P
        self.S, self.R, self.L = LR.build(cfg); m = self.S.m; self.m = m; self.d = self.S.d
        m.vis.global_.offwidth = max(w, m.vis.global_.offwidth); m.vis.global_.offheight = max(h, m.vis.global_.offheight)
        m.vis.quality.shadowsize = 4096; m.vis.headlight.ambient[:] = 0.38; m.vis.headlight.diffuse[:] = 0.30
        m.vis.map.zfar = 200.0 / max(m.stat.extent, 1e-6); m.vis.map.znear = 0.02 / max(m.stat.extent, 1e-6)
        self.bid = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n) for n in LR.BODIES}
        self.geoms = {b: [g for g in range(m.ngeom) if m.geom_bodyid[g] == b] for b in self.bid.values() if b >= 0}
        rec = set(self.geoms)
        self.other = [b for b in range(1, m.nbody) if b not in rec and any(m.geom_bodyid[g] == b for g in range(m.ngeom)) and m.body_mocapid[b] < 0]
        # painted line along the top edge of the step (a marker only): from the two step tiles of the lane model
        self.marks = []; gid = lambda nm: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, nm); gu, gl = gid('t_stepU'), gid('t_stepL')
        if gu >= 0 and gl >= 0:
            R9 = np.zeros(9); mujoco.mju_quat2Mat(R9, m.geom_quat[gu]); Ru = R9.reshape(3, 3); hs = m.geom_size[gu]
            sg = 1.0 if float((m.geom_pos[gl] - m.geom_pos[gu]) @ Ru[:, 0]) > 0 else -1.0
            self.marks.append((m.geom_pos[gu] + Ru @ np.array([sg * (hs[0] - 0.015), 0.0, hs[2] + 0.002]), Ru, (0.015, hs[1], 0.002), (1.0, 0.85, 0.10, 1)))
        gr = gid('t_stepRamp')
        if gr >= 0: m.geom_rgba[gr] = (0.86, 0.52, 0.20, 1)   # the ramp, coloured so it shows
        self.ren = mujoco.Renderer(m, height=h, width=w); self.cam = mujoco.MjvCamera(); self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.opt = mujoco.MjvOption()
        # ground a little lighter and hedges darker than the model defaults, so the robot reads against them
        for g in range(m.ngeom):
            nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ''
            if nm == 'ground': m.geom_rgba[g] = (0.56, 0.55, 0.50, 1)
            elif nm == 't_stepRamp': m.geom_rgba[g] = (0.86, 0.52, 0.20, 1)   # the ramp, coloured so it shows
            elif nm.startswith('t_'): m.geom_rgba[g] = (0.56, 0.55, 0.50, 1)   # same colour as the rest of the lane surface
            elif nm.startswith('hedge'): m.geom_rgba[g] = (0.16, 0.38, 0.17, 0.0 if (hide and nm.startswith(hide)) else 1)   # hedge on the camera side is not drawn
            elif nm in COLOURS: m.geom_rgba[g] = COLOURS[nm]
            elif m.geom_bodyid[g] == self.bid.get('bin', -9): m.geom_rgba[g] = (0.10, 0.33, 0.62, 1)

    def idx(self, t): return int(np.clip(np.searchsorted(self.t, t), 0, len(self.t) - 1))

    def pose(self, i):
        m, d = self.m, self.d; q = self.q[i]; s_now = float(self.hud[i, 0])
        self.L.pool.update(s_now); mujoco.mj_kinematics(m, d)
        for k, n in enumerate(LR.BODIES):
            b = self.bid[n]
            if b < 0 or not np.isfinite(q[k, 0]): continue
            R9 = np.zeros(9); mujoco.mju_quat2Mat(R9, q[k, 3:].astype(np.float64)); Rm = R9.reshape(3, 3)
            d.xpos[b] = q[k, :3]; d.xmat[b] = R9; d.xquat[b] = q[k, 3:]
            for g in self.geoms[b]:
                d.geom_xpos[g] = q[k, :3] + Rm @ m.geom_pos[g]
                G9 = np.zeros(9); mujoco.mju_quat2Mat(G9, m.geom_quat[g]); d.geom_xmat[g] = (Rm @ G9.reshape(3, 3)).ravel()
        for b in self.other:   # bodies that were not recorded but carry shapes: keep them rigid on their parent
            p = m.body_parentid[b]; Rp = d.xmat[p].reshape(3, 3); B9 = np.zeros(9); mujoco.mju_quat2Mat(B9, m.body_quat[b]); Rb = Rp @ B9.reshape(3, 3)
            d.xpos[b] = d.xpos[p] + Rp @ m.body_pos[b]; d.xmat[b] = Rb.ravel()
            for g in range(m.ngeom):
                if m.geom_bodyid[g] == b:
                    d.geom_xpos[g] = d.xpos[b] + Rb @ m.geom_pos[g]; G9 = np.zeros(9); mujoco.mju_quat2Mat(G9, m.geom_quat[g]); d.geom_xmat[g] = (Rb @ G9.reshape(3, 3)).ravel()

    def frame(self, i, look_dx=0.0, dist=3.4, az_off=90.0, elev=-14.0, look_z=0.55):
        """camera follows the robot: looks at a point look_dx ahead of the drive axle, from az_off degrees round from its heading"""
        self.pose(i); d = self.d; b = self.bid['tug']; Rm = d.xmat[b].reshape(3, 3); yaw = math.degrees(math.atan2(Rm[1, 0], Rm[0, 0]))
        p = d.xpos[b] + Rm @ np.array([look_dx, 0.0, 0.0])
        self.cam.lookat[:] = (p[0], p[1], p[2] + look_z)
        self.cam.distance = dist; self.cam.azimuth = yaw + az_off; self.cam.elevation = elev
        self.ren.update_scene(d, self.cam, self.opt)
        scn = self.ren.scene; pt = d.xpos[b].copy(); eye3 = np.eye(3)
        for (x0, x1, y0, y1, z0, z1) in FRAME:
            c = pt + Rm @ np.array([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]); g = scn.geoms[scn.ngeom]
            mujoco.mjv_initGeom(g, mujoco.mjtGeom.mjGEOM_BOX, np.array([(x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2]), c, Rm.ravel().copy(), np.array(STEEL, np.float32)); scn.ngeom += 1
        for (c, Rk, hs, col) in self.marks:
            g = scn.geoms[scn.ngeom]; mujoco.mjv_initGeom(g, mujoco.mjtGeom.mjGEOM_BOX, np.array(hs, float), np.array(c, float), Rk.ravel().copy(), np.array(col, np.float32)); scn.ngeom += 1
        if scn.nlight < scn.lights.shape[0] if hasattr(scn.lights, 'shape') else scn.nlight < len(scn.lights):   # one sun-like light with shadows, so shapes and the step read clearly
            L = scn.lights[scn.nlight]; dv = np.array([0.35, -0.25, -1.0]); dv /= np.linalg.norm(dv)
            L.pos[:] = np.array(self.cam.lookat) - 12.0 * dv; L.dir[:] = dv
            for nm, val in (('directional', 1), ('type', 1), ('castshadow', 1), ('headlight', 0)):
                try: setattr(L, nm, val)
                except Exception: pass
            L.ambient[:] = 0.0; L.diffuse[:] = 0.55; L.specular[:] = 0.1; L.cutoff = 90.0; L.exponent = 1.0; L.attenuation[:] = (1, 0, 0)
            scn.nlight += 1
        img = self.ren.render().copy(); sky = (img.sum(axis=2) == 0)
        if sky.any():
            grad = np.linspace(0, 1, img.shape[0])[:, None]; col = (np.array([150, 185, 225])[None, :] * (1 - grad) + np.array([222, 232, 240])[None, :] * grad).astype(np.uint8)
            img[sky] = np.repeat(col[:, None, :], img.shape[1], axis=1)[sky]
        return img


def writer(path, w, h, fps=25):
    return subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (w, h), '-r', str(fps), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)

def bar(dr, xy, wh, frac, col):
    x, y = xy; w, h = wh; dr.rectangle([x, y, x + w, y + h], outline=(255, 255, 255), width=1); dr.rectangle([x + 1, y + 1, x + 1 + int((w - 2) * max(0.0, min(1.0, frac))), y + h - 1], fill=col)


def video_step():
    W, H = 1280, 720; sc = Scene('runs_lean', 'P1', W, 600, hide='hedgeR')
    t0, t1 = 603.0, 627.0; i0, i1 = sc.idx(t0), sc.idx(t1); out = os.path.join(OUT, '1_improved_full_240L_over_sharp_step.mp4'); ff = writer(out, W, H)
    step_s = 290.0; cmin = 9.0
    for n, i in enumerate(range(i0, i1 + 1)):
        s = float(sc.hud[i, 0]); v = float(sc.hud[i, 3]); clr = float(sc.hud[i, 5]); cmin = min(cmin, clr)
        img = Image.new('RGB', (W, H), (18, 20, 24)); img.paste(Image.fromarray(sc.frame(i, look_dx=0.2, dist=3.0, az_off=118.0, elev=-9.0, look_z=0.4)), (0, 56))
        dr = ImageDraw.Draw(img)
        dr.text((20, 12), 'Improved version carrying a full 240 L bin (110 kg) down over the sharp 40 mm step', font=F(25, True), fill=(255, 255, 255))
        dr.rectangle([0, 656, W, H], fill=(18, 20, 24))
        dr.text((20, 661), 'Distance along lane %5.1f m    Speed %.2f m/s    Real time' % (s, abs(v)), font=F(18), fill=(230, 230, 230))
        dr.text((600, 661), 'Bin wheels above the ground: %3.0f mm now, %3.0f mm lowest so far' % (1000 * clr, 1000 * cmin), font=F(18, True), fill=(255, 220, 90))
        dr.text((20, 688), FOOT, font=F(12), fill=(170, 170, 170)); dr.text((20, 703), FOOT2, font=F(12), fill=(170, 170, 170))
        ff.stdin.write(np.asarray(img).tobytes())
        if n % 100 == 0: print('step frame', n, 'of', i1 - i0, 's %.1f clr %.3f' % (s, clr), flush=True)
    ff.stdin.close(); ff.wait(); print('WROTE', out, 'lowest clearance in the clip %.0f mm' % (1000 * cmin))


def video_return():
    W, H = 1280, 720; PW, PH = 640, 560
    A = Scene('runs_lean', 'P2a', PW, PH, hide='hedgeL'); Bc = Scene('runs_lean_ramp', 'P2a', PW, PH, hide='hedgeL')
    t0, t1 = 693.0, 716.0; out = os.path.join(OUT, '2_empty_return_sharp_step_vs_ramp.mp4'); ff = writer(out, W, H)
    n = 0; t = t0
    while t <= t1 + 1e-6:
        img = Image.new('RGB', (W, H), (18, 20, 24)); dr = ImageDraw.Draw(img)
        for k, (sc, lab) in enumerate(((A, 'Sharp 40 mm step'), (Bc, '1:4 ramp at the step'))):
            i = sc.idx(min(t, float(sc.t[-1]))); s = float(sc.hud[i, 0]); v = float(sc.hud[i, 3])
            fr = sc.frame(i, look_dx=0.45, dist=4.4, az_off=70.0, elev=-9.0, look_z=0.5)
            img.paste(Image.fromarray(fr), (k * PW, 92))
            x0 = k * PW + 18
            dr.text((x0, 62), lab, font=F(22, True), fill=(255, 255, 255))
            stalled = (k == 0 and s < 291.3 and abs(v) < 0.03)
            st = 'STALLED: castors cannot climb the edge' if stalled else ('approaching the step' if s > 291.3 else ('at the step' if s > 289.6 else 'over, continuing home'))
            col = (255, 110, 90) if stalled else ((120, 230, 140) if (k == 1 and s <= 289.6) else (230, 230, 230))
            dr.rectangle([k * PW, 652, (k + 1) * PW, 684], fill=(18, 20, 24))
            dr.text((x0, 658), 'Speed %.2f m/s' % abs(v), font=F(17), fill=(230, 230, 230))
            dr.text((x0 + 150, 658), st, font=F(17, True), fill=col)
        dr.line([(PW, 56), (PW, 684)], fill=(90, 90, 90), width=2)
        dr.text((20, 12), 'Empty return up the lane (no bin), castors leading: the same robot at the same 40 mm step', font=F(24, True), fill=(255, 255, 255))
        dr.text((20, 688), FOOT, font=F(12), fill=(170, 170, 170)); dr.text((20, 703), FOOT2.replace(" Red: the bin\'s own wheels.", ' Orange-brown wedge: the ramp.'), font=F(12), fill=(170, 170, 170))
        ff.stdin.write(np.asarray(img).tobytes())
        if n % 100 == 0: print('return frame', n, 't %.1f' % t, flush=True)
        n += 1; t = t0 + n / 25.0
    ff.stdin.close(); ff.wait(); print('WROTE', out)


if __name__ == '__main__':
    {'step': video_step, 'return': video_return}[sys.argv[1]]()
