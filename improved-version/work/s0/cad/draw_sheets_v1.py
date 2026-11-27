#!/usr/bin/env python3
"""Drawing set for the improved version (B2-F with three tested changes): A3 landscape sheets at 200 dpi.
  1-4    isometric views from four corners, robot without the bin, every visible item named
  5-8    the same four views carrying a full 240 L bin
  9      the underside, seen from below
  10     the bin drawn see-through, to show the comb under its lip and the pad on its front wall
  11-12  exploded views without and with the bin, every item numbered
  13     parts list keyed to the numbers
  14     wiring looms (proposed routing)
usage: draw_sheets.py [sheet numbers ...]   (no arguments = all)"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import render as RN
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'sheets'); os.makedirs(OUT, exist_ok=True)
MODEL = RN.MODEL; ITEMS = {it['item']: it for it in MODEL['items']}
W, H = 3307, 2339; NSHEETS = 14; SH_EX = 11; SH_PARTS = 13; DATE = '2026-11-13'
RN.VIEWS['UFL'] = (-135.0, -RN.ISO_EL, 'Underside')
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
_fc = {}
def F(n, b=False):
    if (n, b) not in _fc: _fc[(n, b)] = ImageFont.truetype(FB if b else FR, n)
    return _fc[(n, b)]
INK = (22, 26, 34); GREY = (95, 102, 112); RED = (176, 32, 32); BLUE = (22, 92, 170); LINE = (50, 56, 66); LOOMC = (150, 60, 0)
SRC_COL = dict(CAD=INK, changed=RED, new=BLUE)

# ------------------------------------------------------------------ sheet frame and title block
def new_sheet(n, title, sub):
    img = Image.new('RGB', (W, H), (255, 255, 255)); dr = ImageDraw.Draw(img); dr.rectangle([28, 28, W - 29, H - 29], outline=INK, width=4)
    dr.text((60, 48), title, font=F(46, True), fill=INK); dr.text((62, 108), sub, font=F(23), fill=GREY)
    x0, y0, x1, y1 = W - 880, H - 262, W - 48, H - 48; dr.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=INK, width=3)
    dr.line([(x0, y0 + 74), (x1, y0 + 74)], fill=INK, width=2); dr.line([(x0, y0 + 142), (x1, y0 + 142)], fill=INK, width=2); dr.line([(x0 + 470, y0 + 142), (x0 + 470, y1)], fill=INK, width=2)
    dr.text((x0 + 18, y0 + 14), 'BinRobo, improved version', font=F(34, True), fill=INK); dr.text((x1 - 200, y0 + 24), 'Sheet %d of %d' % (n, NSHEETS), font=F(22), fill=GREY)
    t = title
    while dr.textlength(t, font=F(25, True)) > 800: t = t[:-1]
    dr.text((x0 + 18, y0 + 90), t, font=F(25, True), fill=INK)
    dr.text((x0 + 18, y0 + 154), 'CONCEPT, NOT FOR MANUFACTURE', font=F(21, True), fill=RED); dr.text((x0 + 18, y0 + 186), 'B2-F with three tested changes', font=F(18), fill=GREY)
    dr.text((x0 + 484, y0 + 154), 'Date %s    Units mm' % DATE, font=F(19), fill=INK); dr.text((x0 + 484, y0 + 182), 'Isometric (parallel) projection', font=F(17), fill=GREY)
    return img, dr
N_SRC = 'Drawn from the other agent\'s CAD model of B2-F with the three tested changes applied: fixed pad, 350 mm lift travel on a 60 mm taller mast, castor cross-beam on a centre pivot.'
N_BLK = 'Block-level model: fasteners, brackets, cable glands and the inside of the electronics pod are not modelled.'
N_NEW = 'Wiring looms and the items in blue boxes are at positions proposed in this drawing; there is no B2-F wiring table or mounting drawing for them yet.'
N_COV = 'The removable front cover (item 44) is left off to show the battery; the electronics pod and power box sit under the fixed rear cover and show best on the exploded sheets.'
N_OPEN = 'OPEN ISSUE (sheet 9): with the castors swivelled forward, as when reversing, their wheels overlap the front bumper by about 45 mm. The nose layout is not final.'
N_BIN = 'The bin is the catalogue 240 L model used in the simulations, not Brian\'s measured bin. It hangs on the comb with its wheels about 100 mm off the ground.'
def wrap(dr, text, font, w):
    out = []; cur = ''
    for wd in text.split():
        t = (cur + ' ' + wd).strip()
        if dr.textlength(t, font=font) > w and cur: out.append(cur); cur = wd
        else: cur = t
    return out + [cur]
def notes(dr, x, y, lines, w=2280, head='Notes'):
    dr.text((x, y), head, font=F(22, True), fill=INK); yy = y + 32; f = F(18)
    for ln in lines:
        for k, t in enumerate(wrap(dr, ln, f, w - 22)): dr.text((x + (0 if k == 0 else 16), yy), ('- ' if k == 0 else '') + t, font=f, fill=RED if ln.startswith('OPEN ISSUE') else INK); yy += 25
        yy += 2
    return yy
def legend_src(dr, x, y):
    f = F(18)
    for txt, c in (('as in their CAD', INK), ('changed in this version', RED), ('new: position proposed here', BLUE)):
        dr.rounded_rectangle([x, y, x + 34, y + 22], 5, fill=(255, 255, 255), outline=c, width=3); dr.text((x + 44, y), txt, font=f, fill=INK); x += 64 + int(dr.textlength(txt, font=f))
    return x

# ------------------------------------------------------------------ anchors: a visible point on each item
def anchors(S, pm):
    """item -> (x, y, visible pixels) for the piece of that item with the largest visible area"""
    out = {}
    ids, counts = np.unique(pm[pm >= 0], return_counts=True)
    for k, c in zip(ids, counts):
        it = S.pieces[k]['e']['item']
        if it in out and out[it][2] >= c: continue
        ys, xs = np.nonzero(pm == k); cx, cy = xs.mean(), ys.mean(); j = int(np.argmin((xs - cx) ** 2 + (ys - cy) ** 2)); out[it] = (int(xs[j]), int(ys[j]), int(c))
    return out
def dilate(mask, r):
    m = mask.copy()
    for _ in range(r):
        n = m.copy(); n[1:, :] |= m[:-1, :]; n[:-1, :] |= m[1:, :]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]; m = n
    return m

# ------------------------------------------------------------------ named callouts in two columns beside a view
SHORT = {1: 'Side rail', 2: 'Mast-base cross-member', 3: 'Nose cross-member, raised', 4: 'Motor plate', 5: 'Gearmotor with brake', 6: 'Chain case', 7: 'Axle stub', 8: 'Wheel encoder, speed sensor',
         9: 'Drive wheel 330 mm', 10: 'Castor beam on centre pivot', 11: 'Pivot pin and hangers', 12: 'Bump stop', 13: 'Castor 200 mm', 14: 'Side guard', 15: 'Mouth flare', 16: 'Leg-tip gap sensor',
         17: 'Anti-tip roller', 18: 'Rear bumper', 19: 'Rear red marker', 20: 'Front bumper', 21: 'Charge contact', 22: 'Headlight', 23: 'Mast upright, 60 mm taller', 24: 'Mast gusset', 25: 'Mast top tie',
         26: 'Linear rail', 27: 'Lift actuator', 28: 'Carriage plate', 29: 'Rail carriage block', 30: 'Comb face plate', 31: 'Comb pivot block', 32: 'Comb with lifting nib', 33: 'Nib seat switch',
         34: 'Comb contact switch', 35: 'Comb distance sensor', 36: 'Keeper (may be deleted)', 37: 'Pad arm, fixed', 38: 'Pad rods and springs', 39: 'Pad face', 40: 'Pad contact switch', 41: 'Bay floor',
         42: 'Bay side wall', 43: 'Rear cover', 44: 'Front cover', 45: 'Battery 24 V', 46: 'Ballast plate', 47: 'Electronics pod', 48: 'Power box', 49: 'Isolator key', 50: 'E-stop', 51: 'Reset button',
         52: 'Sensor post', 53: 'Lidar', 54: 'Front camera', 55: 'GNSS antenna', 56: 'LTE antenna', 57: 'Front radar', 58: 'Horn', 59: 'Rear camera', 60: 'Beacon', 61: 'Work lamp', 62: 'Mast-top marker',
         63: 'Rear radar', 64: 'Microphone', 101: '240 L bin', 102: 'Bin lid', 103: 'Bin handle', 104: 'Bin wheels, off the ground', 201: 'Battery power trunk', 202: 'Left drive loom', 203: 'Right drive loom',
         204: 'Rear loom', 205: 'Lift actuator loom', 206: 'Mast-top loom', 207: 'Carriage loom', 208: 'Sensor-post loom', 209: 'Nose loom', 210: 'Operator-controls loom'}
def tag(it): return ('L%d' % (it - 200)) if it > 200 else str(it)
def _cross(p1, p2, p3, p4):
    d = lambda a, b, c: (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return d(p1, p2, p3) * d(p1, p2, p4) < 0 and d(p3, p4, p1) * d(p3, p4, p2) < 0
def callouts(dr, img_xy, pm, anc, want, area, font=21, minpx=45):
    """item number and name for every wanted, visible item, in a column each side of the view; leaders do not cross within a column"""
    ox, oy = img_xy; h, w = pm.shape; x0, y0, x1, y1 = area; f = F(font); fb = F(font, True); th = font + 13; pitch = th + 5; drawn = pm >= 0
    rl = np.where(drawn.any(1), drawn.argmax(1), w); rr = np.where(drawn.any(1), w - 1 - drawn[:, ::-1].argmax(1), 0); labs = []
    for it in want:
        if it not in anc or anc[it][2] < minpx: continue
        ax, ay, n = anc[it]; t = tag(it); labs.append(dict(it=it, ax=ax + ox, ay=ay + oy, pref=(ax - rl[ay]) - (rr[ay] - ax), t=t, name=SHORT[it], tw=int(dr.textlength(t, font=fb)), nw=int(dr.textlength(SHORT[it], font=f))))
    cap = int((y1 - y0) // pitch); L = sorted([q for q in labs if q['pref'] < 0], key=lambda q: q['pref']); R = sorted([q for q in labs if q['pref'] >= 0], key=lambda q: -q['pref'])
    while len(L) > len(R) + 8: R.append(L.pop())
    while len(R) > len(L) + 8: L.append(R.pop())
    for side, col in (('L', L), ('R', R)):
        if not col: continue
        col.sort(key=lambda q: q['ay']); ys = [q['ay'] - th / 2 for q in col]; n = len(ys)
        for _ in range(600):
            mv = False
            for i in range(n - 1):
                d = ys[i] + pitch - ys[i + 1]
                if d > 0.01: ys[i] -= d / 2; ys[i + 1] += d / 2; mv = True
            if ys[0] < y0: ys[0] = y0; mv = True
            if ys[-1] > y1 - th: ys[-1] = y1 - th; mv = True
            if not mv: break
        for i in range(1, n): ys[i] = max(ys[i], ys[i - 1] + pitch)
        for i in range(n - 2, -1, -1): ys[i] = min(ys[i], ys[i + 1] - pitch)
        bw = [q['tw'] + q['nw'] + 34 for q in col]; edge = max(x0 + max(bw) + 4, ox - 44) if side == 'L' else min(x1 - max(bw) - 4, ox + w + 44)
        for q, y in zip(col, ys): q['y'] = int(y)
        for _ in range(60):   # un-cross leaders by swapping the two labels
            sw = False
            for i in range(n):
                for j in range(i + 1, n):
                    a, b = col[i], col[j]
                    if _cross((edge, a['y'] + th / 2), (a['ax'], a['ay']), (edge, b['y'] + th / 2), (b['ax'], b['ay'])): a['y'], b['y'] = b['y'], a['y']; sw = True
            if not sw: break
        for q in col:
            ym = q['y'] + th // 2; dr.line([(edge, ym), (q['ax'], q['ay'])], fill=(255, 255, 255), width=5);
        for q in col:
            ym = q['y'] + th // 2; dr.line([(edge, ym), (q['ax'], q['ay'])], fill=LINE, width=2); dr.ellipse([q['ax'] - 5, q['ay'] - 5, q['ax'] + 5, q['ay'] + 5], fill=(255, 255, 255), outline=INK, width=2)
            dr.ellipse([q['ax'] - 2, q['ay'] - 2, q['ax'] + 2, q['ay'] + 2], fill=INK)
        for q, b in zip(col, bw):
            bx = edge - b if side == 'L' else edge; c = SRC_COL[ITEMS[q['it']]['src']]
            dr.rounded_rectangle([bx, q['y'], bx + b, q['y'] + th], 6, fill=(255, 255, 255), outline=c, width=2)
            dr.text((bx + 9, q['y'] + 5), q['t'], font=fb, fill=LOOMC if q['it'] > 200 else INK); dr.text((bx + 9 + q['tw'] + 14, q['y'] + 5), q['name'], font=f, fill=INK)
    return [q['it'] for q in labs]

# ------------------------------------------------------------------ small aids: where the view is taken from, and a scale triad
def keyplan(dr, x, y, view, cap=True):
    """plan outline of the robot (front to the right) with an arrow from the corner the view is taken from"""
    s = 0.105; X = lambda xm: x + (xm + 401) * s; Y = lambda ym: y + (465 - ym) * s
    dr.rectangle([X(-401), Y(465), X(1106), Y(-465)], outline=INK, width=2); dr.rectangle([X(-401), Y(358), X(400), Y(-358)], outline=GREY, width=1); dr.rectangle([X(470), Y(225), X(520), Y(-225)], fill=GREY)
    dr.text((X(-330), Y(60)), 'bin bay', font=F(15), fill=GREY); dr.text((X(1106) + 8, Y(60)), 'front', font=F(15, True), fill=INK)
    az = RN.VIEWS[view][0]; ex, ey = -math.cos(math.radians(az)), -math.sin(math.radians(az)); cx, cy = X(352), Y(0); px, py = cx + ex * 1250 * s, cy - ey * 1250 * s; qx, qy = cx + ex * 780 * s, cy - ey * 780 * s
    dr.line([(px, py), (qx, qy)], fill=RED, width=4); ang = math.atan2(qy - py, qx - px)
    dr.polygon([(qx + 14 * math.cos(ang), qy + 14 * math.sin(ang)), (qx + 12 * math.cos(ang + 2.5), qy + 12 * math.sin(ang + 2.5)), (qx + 12 * math.cos(ang - 2.5), qy + 12 * math.sin(ang - 2.5))], fill=RED)
    if cap: dr.text((x - 6, y + 930 * s + 34), 'Plan: the red arrow is the viewing direction', font=F(15), fill=GREY)
def triad(dr, S, view, mpp, x, y):
    """the three main directions with 500 mm marked on each (in isometric all three are drawn to the same scale)"""
    az, el, _ = RN.VIEWS[view]; f, r, u = S.axes(az, el)
    for v, name in (((1, 0, 0), 'to the front'), ((0, 1, 0), 'to the left'), ((0, 0, 1), 'up')):
        v = np.array(v, float) * 0.5; ex, ey = x + (v @ r) / mpp, y - (v @ u) / mpp; dr.line([(x, y), (ex, ey)], fill=INK, width=3); dr.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=INK)
        tx = ex + (10 if ex >= x else -10 - dr.textlength(name, font=F(16))); dr.text((tx, ey - 22 if ey < y else ey + 4), name, font=F(16), fill=INK)
    dr.text((x - 120, y + 300), 'Each leg is 500 mm long', font=F(16), fill=GREY)

# ------------------------------------------------------------------ sheets 1-8: one isometric view each
ISO_AREA = (60, 176, W - 60, 2050)
_mpp = {}
def iso_mpp():
    if 'v' not in _mpp:
        m = 0
        for st in ('nobin', 'carry'):
            S = RN.Scene(st)
            for v in ('FL', 'FR', 'RL', 'RR'): _, (wm, hm) = S.fit(*RN.VIEWS[v][:2]); m = max(m, wm / 1960.0, hm / 1840.0)
        _mpp['v'] = m
    return _mpp['v']
ALL = [i for i in sorted(SHORT)]
def view_sheet(n, state, view, title, sub, note_lines, ghost=False, overlay=None):
    """one large view with every visible item named. ghost: the bin body and lid are drawn see-through and the parts behind them are still labelled"""
    img, dr = new_sheet(n, title, sub); az, el, _ = RN.VIEWS[view]
    S = RN.Scene(state); look, (wm, hm) = S.fit(az, el); x0, y0, x1, y1 = ISO_AREA; mpp = max(iso_mpp(), wm / 1960.0, hm / (y1 - y0 - 10.0)); w, h = int(wm / mpp) + 4, int(hm / mpp) + 4
    vi, pm = S.render(az, el, look, mpp, w, h); ox = (x0 + x1 - w) // 2; oy = (y0 + y1 - h) // 2; anc = anchors(S, pm)
    if ghost:   # the same view drawn again without the bin body and lid, then the bin laid over it faintly; label points for the parts behind the bin come from the second drawing
        S2 = RN.Scene(state, style=lambda e: None if e['item'] in (101, 102) or not e['render'] else (*e['col'], 1.0)); va, pm2 = S2.render(az, el, look, mpp, w, h)
        binmask = np.isin(pm, [k for k, p in enumerate(S.pieces) if p['e']['item'] in (101, 102)]); A = va.astype(np.float32); B = vi.astype(np.float32); out = A.copy()
        edge = binmask & (np.abs(B - np.array((38, 42, 50), np.float32)).sum(2) < 70); out[binmask] = 0.74 * A[binmask] + 0.26 * B[binmask]; out[edge] = 0.45 * A[edge] + 0.55 * B[edge]; vi = out.astype(np.uint8)
        anc = {**anchors(S2, pm2), **{k: v for k, v in anc.items() if k in (101, 102)}}
    img.paste(Image.fromarray(vi), (ox, oy))
    if overlay: overlay(dr, lambda P: S.project(P, az, el, look, mpp, w, h) + np.array([ox, oy]))
    shown = callouts(dr, (ox, oy), pm, anc, ALL, (x0, 252, x1, y1)); keyplan(dr, W - 400, 96, view, cap=False)
    if view == 'UFL': dr.text((W - 414, 212), 'seen from below', font=F(16, True), fill=RED)
    lx = legend_src(dr, 60, 2064) + 30; dr.text((lx, 2064), 'Scale: 100 mm along the length, width or height = %.0f px here (about 1 : %.1f on A3).' % (0.1 * 0.8165 / mpp, mpp / 0.8165 / 0.000127), font=F(18), fill=GREY)
    notes(dr, 60, 2104, note_lines); img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, state, view, 'labels', len(shown), 'mm/px %.3f' % (mpp * 1000), flush=True)
def iso_sheet(n, state, view):
    vname = RN.VIEWS[view][2]; bin_ = state == 'carry'
    view_sheet(n, state, view, '%s isometric, %s' % (vname, 'carrying a full 240 L bin' if bin_ else 'without the bin'),
               ('Bin on the comb at carrying height, as at the end of a simulated pick-up. ' if bin_ else 'Robot alone, comb at its lowest position. ') + 'Every visible item is named; the number is its line on the parts list (sheet %d).' % SH_PARTS,
               [N_SRC + ' ' + N_BLK, N_NEW + ' ' + N_COV] + ([N_BIN] if bin_ else ['Overall size: 1,507 mm long, 930 mm wide, 1,510 mm high (1,552 mm long with a 240 L bin on board).']) + [N_OPEN])
def sheet_under(n=9):
    def castor_room(dr, proj):   # the circle each castor needs to swivel (50 mm trail + 100 mm wheel + half the wheel width), drawn at the height of the bumper's lower edge
        for sgn in (1, -1):
            pts = proj([(0.95 + 0.152 * math.cos(t), sgn * 0.28 + 0.152 * math.sin(t), 0.13) for t in np.linspace(0, 2 * math.pi, 73)])
            for k in range(0, 72, 2): dr.line([tuple(pts[k]), tuple(pts[k + 1])], fill=RED, width=4)
    view_sheet(n, 'nobin', 'UFL', 'Underside, without the bin', 'Isometric view from below the front-left corner, as if the robot stood on a glass floor. The number is the item\'s line on the parts list (sheet %d).' % SH_PARTS,
               ['The castor cross-beam (item 10) hangs from the raised nose cross-member (item 3) on one pin (item 11), 200 mm above the ground as in the tests, so the two castors can rise and fall against each other by about 25 mm each way; the bump stops (item 12) limit the swing.',
                'Red dashed circles: the room each castor needs to swivel (304 mm across, drawn at the height of the bumper\'s lower edge). Bay floor, bay walls and ballast (items 41, 42, 46) are cut back to clear it; in the B2-F CAD they pass through the castors.',
                'OPEN ISSUE: with the castors swivelled forward, as when reversing, their wheels overlap the front bumper (item 20) by about 45 mm. Either the bumper moves about 65 mm forward or the castors about 65 mm back; neither is tested yet.'], overlay=castor_room)
def sheet_ghost(n=10):
    view_sheet(n, 'carry', 'RL', 'Rear-left isometric, bin drawn see-through', 'The same view as sheet 7 with the bin body and lid see-through, so the comb under the front lip, the pad on the front wall and the lift carriage can be seen.',
               ['The comb (item 32) sits under the lip along the front of the bin and its nib hooks behind the lip; the bin hangs from it. The fixed pad (item 39) presses on the front wall lower down and stops the bin swinging.',
                N_BIN, N_BLK + ' ' + N_NEW], ghost=True)

# ------------------------------------------------------------------ exploded sheets with numbered balloons
def balloons(dr, img_xy, pm, anc, items, rect, r=21):
    """a numbered balloon in clear space near each item, short leader; returns the items that got one"""
    ox, oy = img_xy; x0, y0, x1, y1 = rect; occ = np.ones((H, W), bool); occ[y0:y1, x0:x1] = False; occ[oy:oy + pm.shape[0], ox:ox + pm.shape[1]] |= dilate(pm >= 0, 3)
    yy, xx = np.ogrid[-r - 3:r + 4, -r - 3:r + 4]; disc = (xx * xx + yy * yy) <= (r + 3) ** 2; done = []; placed = []   # placed: (bx, by, ax, ay)
    def seg_d(px, py, x1_, y1_, x2_, y2_):
        vx, vy = x2_ - x1_, y2_ - y1_; t = max(0.0, min(1.0, ((px - x1_) * vx + (py - y1_) * vy) / max(vx * vx + vy * vy, 1e-9))); return math.hypot(px - x1_ - t * vx, py - y1_ - t * vy)
    order = sorted([it for it in items if it in anc], key=lambda it: -anc[it][2])
    for it in order:
        ax, ay, _ = anc[it]; ax += ox; ay += oy; best = None
        for rad in (48, 64, 82, 104, 130, 160, 196, 240, 300, 380, 480):
            for k in range(24):
                a = 2 * math.pi * k / 24; bx = int(ax + rad * math.cos(a)); by = int(ay + rad * math.sin(a))
                if bx - r - 4 < x0 or bx + r + 4 > x1 or by - r - 4 < y0 or by + r + 4 > y1: continue
                if (occ[by - r - 3:by + r + 4, bx - r - 3:bx + r + 4] & disc).any(): continue
                if any(seg_d(qx, qy, bx, by, ax, ay) < r + 5 or seg_d(bx, by, qx, qy, qax, qay) < r + 5 for qx, qy, qax, qay in placed): continue
                best = (bx, by); break
            if best: break
        if not best: continue
        bx, by = best; occ[by - r - 3:by + r + 4, bx - r - 3:bx + r + 4] |= disc; placed.append((bx, by, ax, ay))
        loom = it > 200; label = tag(it); col = LOOMC if loom else INK
        d = math.hypot(ax - bx, ay - by); sx = bx + (ax - bx) * r / d; sy = by + (ay - by) * r / d
        dr.line([(sx, sy), (ax, ay)], fill=(255, 255, 255), width=5); dr.line([(sx, sy), (ax, ay)], fill=col, width=2); dr.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=col)
        dr.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 255, 255), outline=col, width=3); f = F(19 if len(label) < 3 else 16, True); tw = dr.textlength(label, font=f)
        dr.text((bx - tw / 2, by - (12 if len(label) < 3 else 10)), label, font=f, fill=col); done.append(it)
    return done

def parts_column(dr, x, y, items, shown, w=840):
    dr.text((x, y), 'Item', font=F(19, True), fill=INK); dr.text((x + 62, y), 'Qty', font=F(19, True), fill=INK); dr.text((x + 116, y), 'Description', font=F(19, True), fill=INK); yy = y + 30
    dr.line([(x, yy - 4), (x + w, yy - 4)], fill=INK, width=2); pitch = min(26, (H - 336 - yy) / max(len(items), 1)); f = F(17)
    for it in items:
        d = ITEMS[it]; loom = it > 200; nm = d['name'] if not loom else d['name'].split('  ', 1)[1]
        while dr.textlength(nm, font=f) > w - 150 and len(nm) > 10: nm = nm[:-2]
        col = INK if it in shown else (150, 150, 150)
        dr.text((x + 4, yy), tag(it), font=F(17, True), fill=LOOMC if loom else col); dr.text((x + 70, yy), str(d['qty']), font=f, fill=col); dr.text((x + 116, yy), nm, font=f, fill=col)
        if d['src'] != 'CAD': dr.text((x + w - 16, yy), '*' if d['src'] == 'changed' else '+', font=F(17, True), fill=RED if d['src'] == 'changed' else BLUE)
        yy += pitch
    return yy

def exploded_sheet(n, state):
    bin_ = state == 'carry'
    img, dr = new_sheet(n, 'Exploded view, ' + ('with a 240 L bin' if bin_ else 'without the bin'),
                        ('As sheet %d, with the lift carriage at carrying height and the bin, lid, handle and wheels pulled away to the rear. ' % SH_EX if bin_ else 'Every item of the robot pulled apart along its assembly direction and numbered. ')
                        + 'Wiring looms L1 to L10 are drawn in colour.')
    S = RN.Scene(state, exploded=True); az, el, _ = RN.VIEWS['RL']; look, (wm, hm) = S.fit(az, el)
    rect = (48, 160, 2400, H - 110); aw, ah = rect[2] - rect[0] - 150, rect[3] - rect[1] - 130; mpp = max(wm / aw, hm / ah); w, h = int(wm / mpp) + 4, int(hm / mpp) + 4
    vi, pm = S.render(az, el, look, mpp, w, h); ox = (rect[0] + rect[2] - w) // 2; oy = (rect[1] + rect[3] - h) // 2
    # explode lines: from each exploded group's centre back to where it sits, drawn only on empty paper so they pass behind the parts
    lay = Image.new('L', (W, H), 0); ld = ImageDraw.Draw(lay); groups = {}
    for p in S.pieces:
        e = p['e']
        if tuple(e['explode']) != (0, 0, 0) and e['kind'] == 'part': groups.setdefault((e['exgroup'], tuple(e['explode'])), []).append(p['V'])
    for (gname, ex), Vs in groups.items():
        c = np.vstack(Vs).mean(0); a = S.project(c, az, el, look, mpp, w, h)[0]; b = S.project(c - np.array(ex), az, el, look, mpp, w, h)[0]; L = math.hypot(*(b - a)); nseg = max(int(L / 22), 1)
        for k in range(nseg):
            t0, t1 = k / nseg, (k + 0.55) / nseg; ld.line([(ox + a[0] + (b[0] - a[0]) * t0, oy + a[1] + (b[1] - a[1]) * t0), (ox + a[0] + (b[0] - a[0]) * t1, oy + a[1] + (b[1] - a[1]) * t1)], fill=255, width=2)
    img.paste(Image.fromarray(vi), (ox, oy)); la = np.asarray(lay) > 0; bg = np.ones((H, W), bool); bg[oy:oy + h, ox:ox + w] = pm < 0; A = np.asarray(img).copy(); A[la & bg] = (150, 156, 166); img = Image.fromarray(A); dr = ImageDraw.Draw(img)
    anc = anchors(S, pm); order = [it['item'] for it in MODEL['items'] if (bin_ or it['item'] < 100 or it['item'] > 200)]
    shown = balloons(dr, (ox, oy), pm, anc, order, rect)
    yy = parts_column(dr, 2430, 168, order, set(shown)); dr.text((2430, yy + 4), '* changed from the B2-F CAD', font=F(16), fill=RED); dr.text((2700, yy + 4), '+ new, position proposed here', font=F(16), fill=BLUE)
    dr.text((2430, yy + 26), 'L1 to L10 are wiring looms; each travels with the part it is tied to.', font=F(16), fill=LOOMC)
    missing = [i for i in order if i not in shown]; keyplan(dr, 2180, 190, 'RL', cap=False)
    dr.text((60, H - 96), 'Pulled apart along the dashed lines. Seen from the rear-left; the bin side is nearest. Full details of every item are on sheet %d.' % SH_PARTS + ('' if not missing else '   Hidden in this view: item %s.' % ', '.join(tag(i) for i in missing)), font=F(18), fill=GREY)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, 'balloons', len(shown), 'of', len(order), 'missing', missing, flush=True)

# ------------------------------------------------------------------ parts list
POD = ['Motor controller, 2 x 30 A (CTL-L8)', 'Flight controller F405 running ArduPilot Rover (G18)', 'Companion computer (G23) with SD card and shutdown supply (S11)', 'RTK satellite receiver (RTK-L8)',
       '4G modem (G25)', 'Safety relay (SR-L8) and two watchdogs (S7)', 'Speed and standstill monitors (SLS-L8)', 'Fuse box (S2) and 24 V to 5 V converter (G27)',
       'Lights switching board (L6), audio amplifier (AU-L8)', 'Tilt switch (S13), temperature sensors (S12), tamper siren (S10)']
def sheet_parts(n=13):
    img, dr = new_sheet(n, 'Parts list', 'Item numbers match the labels on sheets 1 to 10 and the balloons on sheets %d and %d. "Their line" is the line in the other agent\'s parts list (BinRobo_B2F_BOM_2026-11-12).' % (SH_EX, SH_EX + 1))
    its = [it for it in MODEL['items']]; cols = [its[:29], its[29:58], its[58:]]; xw = 1040; f = F(20); fb = F(20, True); fn = F(16)
    def cut(s, wpx, fnt=None):
        fnt = fnt or f
        while dr.textlength(s, font=fnt) > wpx and len(s) > 6: s = s[:-2]
        return s
    for c, col in enumerate(cols):
        x = 60 + c * (xw + 34); y = 172; dr.text((x, y), 'Item', font=fb, fill=INK); dr.text((x + 62, y), 'Qty', font=fb, fill=INK); dr.text((x + 116, y), 'Description', font=fb, fill=INK)
        dr.text((x + 690, y), 'Their line', font=fb, fill=INK); dr.text((x + 930, y), 'Status', font=fb, fill=INK); dr.line([(x, y + 30), (x + xw, y + 30)], fill=INK, width=2); yy = y + 40
        for d in col:
            loom = d['item'] > 200; nm = d['name'].split('  ', 1)[1] if loom else d['name']; st = {'CAD': 'their CAD', 'changed': 'CHANGED', 'new': 'NEW'}[d['src']]
            dr.text((x + 4, yy), tag(d['item']), font=fb, fill=LOOMC if loom else INK); dr.text((x + 72, yy), str(d['qty']), font=f, fill=INK); dr.text((x + 116, yy), cut(nm, 576), font=f, fill=INK)
            dr.text((x + 690, yy), cut(d['ref'] or '-', 236), font=F(19), fill=GREY); dr.text((x + 930, yy), st, font=fb if d['src'] != 'CAD' else f, fill=SRC_COL[d['src']] if d['src'] != 'CAD' else GREY)
            note = 'contents listed on this sheet; not drawn individually' if d['item'] == 47 else d['note']; yy += 27
            if note:
                for t in wrap(dr, note, fn, xw - 130): dr.text((x + 116, yy), t, font=fn, fill=RED if note.startswith('OPEN ISSUE') else GREY); yy += 21
            yy += 9
        if c == 2:
            yy += 16; dr.text((x, yy), 'Inside the electronics pod (item 47), not drawn', font=fb, fill=INK); yy += 32
            for p in POD: dr.text((x + 12, yy), '- ' + p, font=F(18), fill=INK); yy += 26
            yy += 14; dr.text((x, yy), 'Deleted from B2-F in this version', font=fb, fill=INK); yy += 32
            for p in ('Pad toggle actuator, knee toggle links and toggle-lock switch (the pad is fixed)', 'Rail drop plates and fixed castor plates (replaced by the pivoting castor beam)'): dr.text((x + 12, yy), '- ' + p, font=F(18), fill=INK); yy += 26
        print('  parts column', c, 'ends at y', int(yy))
    rb = [d for d in its if not 100 < d['item'] < 200]
    notes(dr, 60, 2104, ['Status: "their CAD" = as in the other agent\'s CAD model; CHANGED = altered for this version; NEW = added in this drawing at a proposed position. %d robot items: %d their CAD, %d changed, %d new (10 of the new ones are looms). Items 101 to 104 are the bin.'
                         % (len(rb), sum(1 for d in rb if d['src'] == 'CAD'), sum(1 for d in rb if d['src'] == 'changed'), sum(1 for d in rb if d['src'] == 'new')),
                         'Item 36 (keeper) is still drawn because the other agent has not yet confirmed it can go. Item 54 (front camera) is in their CAD, but I found no line for it in their parts list.',
                         'Loom contents are grouped from the device list in their parts list and their earlier harness (Rev G6); wire sizes, fuses and connectors still have to be set out in a wiring table.'])
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

# ------------------------------------------------------------------ wiring looms
def sheet_looms(n=14):
    img, dr = new_sheet(n, 'Wiring looms (proposed routing)', 'The robot is drawn faint and the ten looms in colour, as if seen through the bodywork. The routing is proposed in this drawing; no B2-F wiring table exists yet.')
    cells = [(48, 176, 1500, 1690), (1528, 176, 2980, 1690)]; looms = [d for d in MODEL['items'] if d['item'] > 200]
    grey = lambda e: None if e['kind'] == 'loom' or not e['render'] else (0.80, 0.82, 0.85, 1.0)
    only = lambda e: (*e['col'], 1.0) if e['kind'] == 'loom' else None
    SP = RN.Scene('nobin', style=grey); SL = RN.Scene('nobin', style=only); fits = [SP.fit(*RN.VIEWS[v][:2]) for v in ('RL', 'FR')]; mpp = max(max(wm / 1340.0, hm / 1400.0) for _, (wm, hm) in fits)
    for v, cell, (look, (wm, hm)) in zip(('RL', 'FR'), cells, fits):
        az, el, vname = RN.VIEWS[v]; w, h = int(wm / mpp) + 4, int(hm / mpp) + 4; a, pmA = SP.render(az, el, look, mpp, w, h, edge_col=(120, 126, 136)); b, pmB = SL.render(az, el, look, mpp, w, h)
        a = (255 - (255 - a.astype(np.float32)) * 0.45).astype(np.uint8); m = dilate(pmB >= 0, 1); a[m] = b[m]; ox = (cell[0] + cell[2] - w) // 2; oy = (cell[1] + cell[3] - h) // 2 + 14
        img.paste(Image.fromarray(a), (ox, oy)); dr.rectangle(cell, outline=(190, 195, 202), width=2); dr.text((cell[0] + 14, cell[1] + 10), vname + ' isometric', font=F(28, True), fill=INK)
        balloons(dr, (ox, oy), np.where((pmA >= 0) | (pmB >= 0), 0, -1), anchors(SL, pmB), [d['item'] for d in looms], cell, r=24)
    keyplan(dr, 3050, 300, 'RL', cap=False); dr.text((3034, 420), 'left-hand view', font=F(17, True), fill=INK); keyplan(dr, 3050, 620, 'FR', cap=False); dr.text((3034, 780), 'right-hand view', font=F(17, True), fill=INK)
    x, y = 60, 1712; cw = (80, 330, 1130, 780); heads = ('Loom', 'Name', 'Route', 'Cables carried (proposed)'); xx = x
    for hd, wd in zip(heads, cw): dr.text((xx, y), hd, font=F(18, True), fill=INK); xx += wd
    dr.line([(x, y + 28), (x + sum(cw), y + 28)], fill=INK, width=2); yy = y + 36; f = F(18)
    for d in looms:
        e = [p for p in MODEL['parts'] if p['item'] == d['item']][0]; col = tuple(int(255 * c) for c in e['col']); route, cores = d['note'].split('. ', 1)
        dr.rectangle([x, yy + 3, x + 16, yy + 19], fill=col, outline=INK); dr.text((x + 24, yy), tag(d['item']), font=F(18, True), fill=INK); dr.text((x + cw[0], yy), d['name'].split('  ', 1)[1], font=f, fill=INK)
        r_ = route[0].upper() + route[1:]
        while dr.textlength(r_, font=f) > cw[2] - 16: r_ = r_[:-2]
        dr.text((x + cw[0] + cw[1], yy), r_, font=f, fill=INK)
        while dr.textlength(cores, font=f) > cw[3] - 10: cores = cores[:-2]
        dr.text((x + cw[0] + cw[1] + cw[2], yy), cores, font=f, fill=GREY); yy += 28
    notes(dr, 60, yy + 10, ['Loom contents follow the device list in the other agent\'s parts list and the wire groups of their earlier harness (Rev G6), regrouped for one rigid frame. Wire sizes, fuses and connectors are not worked out here.',
                              'L7 crosses to the moving carriage in a hanging loop; it needs a cable chain or a strain-relieved loop sized for 350 mm of travel. All looms start at the electronics pod except L1, which joins battery, isolator key, power box and pod.'], w=2300)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

JOBS = {}
for k, (st, v) in enumerate([(s, v) for s in ('nobin', 'carry') for v in ('FL', 'FR', 'RL', 'RR')]): JOBS[k + 1] = (lambda st=st, v=v, k=k: iso_sheet(k + 1, st, v))
JOBS.update({9: sheet_under, 10: sheet_ghost, 11: lambda: exploded_sheet(11, 'nobin'), 12: lambda: exploded_sheet(12, 'carry'), 13: sheet_parts, 14: sheet_looms})
if __name__ == '__main__':
    for n in ([int(a) for a in sys.argv[1:]] or sorted(JOBS)): JOBS[n]()
