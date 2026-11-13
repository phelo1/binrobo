#!/usr/bin/env python3
"""Renderer for the drawing set: draws the model pieces (triangle meshes) in true isometric (parallel) projection with MuJoCo's
offscreen renderer, then adds outlines from the part map and the depth map so the result reads as a line-and-tone drawing.
Nothing here is simulated; MuJoCo is used only to draw."""
import os, sys, math, pickle, struct, tempfile
os.environ.setdefault('MUJOCO_GL', 'egl')
import numpy as np, mujoco
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = pickle.load(open(os.path.join(HERE, 'model.pkl'), 'rb'))
ISO_EL = -35.264
VIEWS = dict(FL=(-135.0, ISO_EL, 'Front-left'), FR=(135.0, ISO_EL, 'Front-right'), RL=(-45.0, ISO_EL, 'Rear-left'), RR=(45.0, ISO_EL, 'Rear-right'),
             UFL=(-135.0, 28.0, 'Underside, from front-left'), URR=(45.0, 28.0, 'Underside, from rear-right'))

def write_stl(path, V, T):
    V = np.asarray(V, np.float32); T = np.asarray(T, np.int32); a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]; n = np.cross(b - a, c - a); ln = np.linalg.norm(n, axis=1, keepdims=True); n = n / np.maximum(ln, 1e-12)
    rec = np.zeros(len(T), dtype=[('n', '<f4', 3), ('a', '<f4', 3), ('b', '<f4', 3), ('c', '<f4', 3), ('att', '<u2')]); rec['n'] = n; rec['a'] = a; rec['b'] = b; rec['c'] = c
    with open(path, 'wb') as f: f.write(b'\0' * 80); f.write(struct.pack('<I', len(T))); f.write(rec.tobytes())

class Scene:
    """pieces drawn in one state. style(piece) -> rgba or None (None = not drawn)."""
    def __init__(self, state, exploded=False, style=None, with_bin=None, max_px=(7000, 5000)):
        self.state = state; with_bin = (state == 'carry') if with_bin is None else with_bin
        self.tmp = tempfile.mkdtemp(prefix='binrobo_draw_'); assets = []; geoms = []; self.pieces = []
        for e in MODEL['parts']:
            if e['with_bin_only'] and not with_bin: continue
            rgba = style(e) if style else ((*e['col'], 1.0) if e['render'] or exploded else None)
            if rgba is None: continue
            V = e['V_' + state] + (np.array(e['explode'], np.float32) if exploded else 0.0); k = len(self.pieces)
            write_stl(os.path.join(self.tmp, 'm%d.stl' % k), V, e['T'])
            assets.append('<mesh name="m%d" file="m%d.stl" inertia="shell"/>' % (k, k))
            geoms.append('<geom name="g%d" type="mesh" mesh="m%d" rgba="%.3f %.3f %.3f %.3f" contype="0" conaffinity="0"/>' % (k, k, *rgba))
            self.pieces.append(dict(e=e, V=V, rgba=rgba))
        xml = ('<mujoco><compiler meshdir="%s"/><visual><global offwidth="%d" offheight="%d" orthographic="true"/><quality offsamples="4"/>'
               '<headlight ambient="0.50 0.50 0.50" diffuse="0.42 0.42 0.42" specular="0 0 0"/><map znear="0.001" zfar="60"/></visual>'
               '<asset>%s</asset><worldbody><light directional="true" pos="-2 3 6" dir="0.35 -0.5 -1" diffuse="0.30 0.30 0.30" specular="0 0 0" castshadow="false"/>%s</worldbody></mujoco>'
               % (self.tmp, max_px[0], max_px[1], ''.join(assets), ''.join(geoms)))
        self.m = mujoco.MjModel.from_xml_string(xml); self.d = mujoco.MjData(self.m); mujoco.mj_forward(self.m, self.d); self.m.stat.extent = 1.0
        self.gid = {mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_GEOM, 'g%d' % k): k for k in range(len(self.pieces))}
        A = np.vstack([p['V'] for p in self.pieces]); self.lo = A.min(0); self.hi = A.max(0)

    @staticmethod
    def axes(az, el):
        a, e = math.radians(az), math.radians(el); f = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r); u = np.cross(r, f); return f, r, u

    def fit(self, az, el, margin=1.04):
        """look-at point and (width, height) in metres that just contain every drawn piece in this view"""
        f, r, u = self.axes(az, el); A = np.vstack([p['V'] for p in self.pieces]); x = A @ r; y = A @ u; c = np.array([(x.min() + x.max()) / 2, (y.min() + y.max()) / 2])
        look = c[0] * r + c[1] * u + f * float((A @ f).mean()); return look, (float(np.ptp(x)) * margin, float(np.ptp(y)) * margin)

    def project(self, P, az, el, look, mpp, W, H):
        """robot-frame points (m) -> pixel coordinates of the final image (mpp = metres per pixel)"""
        f, r, u = self.axes(az, el); P = np.atleast_2d(np.asarray(P, float)) - look; return np.c_[W / 2 + (P @ r) / mpp, H / 2 - (P @ u) / mpp]

    def render(self, az, el, look, mpp, W, H, ss=2, edges=True, edge_col=(38, 42, 50)):
        """returns (rgb image HxWx3 uint8 with white background and outlines, part map HxW of piece indices or -1)"""
        w, h = W * ss, H * ss; ren = mujoco.Renderer(self.m, height=h, width=w); cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        cam.lookat[:] = look; cam.distance = 12.0; cam.azimuth = az; cam.elevation = el; cam.orthographic = 1; self.m.vis.global_.fovy = mpp * H
        ren.update_scene(self.d, cam); rgb = ren.render().astype(np.float32)
        ren.enable_segmentation_rendering(); ren.update_scene(self.d, cam); seg = ren.render()[:, :, 0].copy(); ren.disable_segmentation_rendering()
        ren.enable_depth_rendering(); ren.update_scene(self.d, cam); dep = ren.render().copy(); ren.disable_depth_rendering(); ren.close()
        pm = np.full(seg.shape, -1, np.int32)
        for g_, k in self.gid.items(): pm[seg == g_] = k
        rgb[pm < 0] = 255.0
        if edges:
            E = np.zeros(pm.shape, bool); E[:, 1:] |= pm[:, 1:] != pm[:, :-1]; E[1:, :] |= pm[1:, :] != pm[:-1, :]
            dz = dep.astype(np.float64); dz[pm < 0] = 0.0
            d2x = np.abs(dz[:, 2:] - 2 * dz[:, 1:-1] + dz[:, :-2]); d2y = np.abs(dz[2:, :] - 2 * dz[1:-1, :] + dz[:-2, :]); thr = 0.45 * mpp / ss   # crease: slope change across neighbouring pixels
            C = np.zeros(pm.shape, bool); C[:, 1:-1] |= d2x > thr; C[1:-1, :] |= d2y > thr; C &= pm >= 0
            E2 = E.copy(); E2[1:, :] |= E[:-1, :]; E2[:, 1:] |= E[:, :-1]            # outlines 2 px (at the supersampled size), creases 1 px
            rgb[C] = rgb[C] * 0.35 + np.array(edge_col) * 0.65; rgb[E2] = edge_col
        img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
        return np.asarray(img), pm[ss // 2::ss, ss // 2::ss]

if __name__ == '__main__':
    st = sys.argv[1] if len(sys.argv) > 1 else 'nobin'; view = sys.argv[2] if len(sys.argv) > 2 else 'RL'; ex = len(sys.argv) > 3 and sys.argv[3] == 'ex'
    S = Scene(st, exploded=ex); az, el, _ = VIEWS[view]; look, (wm, hm) = S.fit(az, el); mpp = max(wm / 1500, hm / 1500); W, H = int(wm / mpp) + 2, int(hm / mpp) + 2
    img, pm = S.render(az, el, look, mpp, W, H); out = os.path.join(HERE, 'test_%s_%s%s.png' % (st, view, '_ex' if ex else '')); Image.fromarray(img).save(out)
    print(out, img.shape, 'pieces', len(S.pieces), 'visible pieces', len(np.unique(pm)) - 1, 'mm per px %.2f' % (mpp * 1000))
