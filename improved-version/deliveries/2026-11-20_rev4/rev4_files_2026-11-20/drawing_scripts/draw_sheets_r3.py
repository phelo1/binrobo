#!/usr/bin/env python3
"""Drawing set for the improved version (B2-F with three tested changes): A3 landscape sheets at 200 dpi.
  1-4    isometric views from four corners, robot without the bin, every visible item named
  5-8    the same four views carrying a full 240 L bin
  9      the underside, seen from below
  10     the bin drawn see-through, to show the comb under its lip and the pad on its front wall
  11-12  exploded views without and with the bin, every item numbered
  13     parts list keyed to the numbers
  14     wiring looms (proposed routing)
  15     safety functions, stop chain, power path, fusing (proposal)
  16     main dimensions, side and plan views
usage: draw_sheets.py [sheet numbers ...]   (no arguments = all)"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import render as RN
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'sheets'); os.makedirs(OUT, exist_ok=True)
MODEL = RN.MODEL; ITEMS = {it['item']: it for it in MODEL['items']}
W, H = 3307, 2339; NSHEETS = 16; SH_EX = 11; SH_PARTS = 13; SH_SAFE = 15; DATE = '2026-11-14'
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
    dr.text((x0 + 18, y0 + 14), 'BinRobo improved version, rev 3', font=F(33, True), fill=INK); dr.text((x1 - 200, y0 + 24), 'Sheet %d of %d' % (n, NSHEETS), font=F(22), fill=GREY)
    t = title
    while dr.textlength(t, font=F(25, True)) > 800: t = t[:-1]
    dr.text((x0 + 18, y0 + 90), t, font=F(25, True), fill=INK)
    dr.text((x0 + 18, y0 + 154), 'CONCEPT, NOT FOR MANUFACTURE', font=F(21, True), fill=RED); dr.text((x0 + 18, y0 + 186), 'Revision 3, after the review of 14 Nov', font=F(18), fill=GREY)
    dr.text((x0 + 484, y0 + 154), 'Date %s    Units mm' % DATE, font=F(19), fill=INK); dr.text((x0 + 484, y0 + 182), 'Isometric (parallel) projection', font=F(17), fill=GREY)
    return img, dr
N_SRC = 'Drawn from the other agent\'s CAD model of B2-F with the changes of revisions 1 to 3: fixed sprung pad, castor beam on a centre pivot, 700 mm comb, bumper 65 mm forward on a sprung carrier, bolted lift stops, frame drawn with its real wall thicknesses.'
N_BLK = 'Fasteners, weld seams, cable glands and the inside of the electronics pod are not drawn. Bought-in units (drive units, castors, actuator, sensors) are drawn as blocks.'
N_NEW = 'Wiring looms and the items in blue boxes are at positions proposed in this drawing; there is no B2-F wiring table or mounting drawing for them yet.'
N_COV = 'The removable front cover (item 44) is left off to show the battery; the electronics pod and power box sit under the fixed rear cover and show best on the exploded sheets.'
N_OPEN = 'Revision 3 of 14 November 2026. Concept only: what it has passed in simulation and what is still open are in the revision 3 reply note. Weight by this model: 152 kg.'
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
SHORT = {1: 'Side rail', 2: 'Mast-base cross-member', 3: 'Nose cross-member', 4: 'Motor plate', 5: 'Gearmotor with brake', 6: 'Chain case', 7: 'Axle stub', 8: 'Wheel encoder, speed sensor',
         9: 'Drive wheel 330 mm', 10: 'Castor beam on centre pivot', 11: 'Pivot pin D20, hanger plates', 12: 'Bump stop', 13: 'Castor 200 mm', 14: 'Side guard', 15: 'Mouth flare', 16: 'Leg-tip gap sensor',
         17: 'Anti-tip roller', 18: 'Rear bumper', 19: 'Rear red marker', 20: 'Front bumper bar', 21: 'Charge contact', 22: 'Headlight', 23: 'Mast upright 80 x 40 x 4', 25: 'Mast top tie',
         26: 'Linear rail', 27: 'Lift actuator, 400 mm unit', 28: 'Carriage plate, aluminium', 29: 'Rail carriage block', 30: 'Comb face plate', 31: 'Comb pivot block', 32: 'Comb 700 mm with lifting nib', 33: 'Nib seat switch',
         34: 'Comb contact switch', 35: 'Comb distance sensor', 37: 'Pad arm, fixed', 38: 'Pad rods, long springs', 39: 'Pad face, 10 mm behind nib', 40: 'Pad contact switch', 41: 'Bay floor',
         42: 'Bay side wall', 43: 'Rear cover', 44: 'Front cover', 45: 'Battery 24 V', 47: 'Electronics pod', 48: 'Power box', 49: 'Isolator key', 50: 'E-stop', 51: 'Reset button',
         52: 'Sensor post', 53: 'Lidar', 54: 'Front camera', 55: 'GNSS antenna', 56: 'LTE antenna', 57: 'Front radar', 58: 'Horn', 59: 'Rear camera', 60: 'Beacon', 61: 'Work lamp', 62: 'Mast-top marker',
         63: 'Rear radar', 64: 'Microphone', 65: 'Main fuse 50 A', 66: 'Bumper carrier', 67: 'Lift stop, bolted', 68: 'Lift limit switch', 72: 'Bumper switch', 73: 'Cable chain bracket', 74: 'Corner plate', 69: 'Rail backing flat', 70: 'Mast foot shoe', 71: 'Actuator base bracket', 101: '240 L bin', 102: 'Bin lid', 103: 'Bin handle', 104: 'Bin wheels, off the ground', 201: 'Battery power trunk', 202: 'Left drive loom', 203: 'Right drive loom',
         204: 'Rear loom', 205: 'Lift actuator loom', 206: 'Mast-top loom', 207: 'Carriage loom', 208: 'Sensor-post loom', 209: 'Nose loom', 210: 'Operator-controls loom', 211: 'Safety and control loom', 212: 'Charge loom'}
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
    dr.rectangle([X(-401), Y(465), X(1171), Y(-465)], outline=INK, width=2); dr.rectangle([X(-401), Y(358), X(400), Y(-358)], outline=GREY, width=1); dr.rectangle([X(470), Y(225), X(520), Y(-225)], fill=GREY)
    dr.text((X(-330), Y(60)), 'bin bay', font=F(15), fill=GREY); dr.text((X(1171) + 8, Y(60)), 'front', font=F(15, True), fill=INK)
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
               [N_SRC + ' ' + N_BLK, N_NEW + ' ' + N_COV] + ([N_BIN] if bin_ else ['Overall size: 1,572 mm long, 930 mm wide, 1,510 mm high (1,617 mm long with a 240 L bin on board).']) + [N_OPEN])
def sheet_under(n=9):
    def castor_room(dr, proj):   # the circle each castor needs to swivel (50 mm trail + 100 mm wheel + half the wheel width), drawn at the height of the bumper's lower edge
        for sgn in (1, -1):
            pts = proj([(0.95 + 0.152 * math.cos(t), sgn * 0.28 + 0.152 * math.sin(t), 0.13) for t in np.linspace(0, 2 * math.pi, 73)])
            for k in range(0, 72, 2): dr.line([tuple(pts[k]), tuple(pts[k + 1])], fill=RED, width=4)
    view_sheet(n, 'nobin', 'UFL', 'Underside, without the bin', 'Isometric view from below the front-left corner, as if the robot stood on a glass floor. The number is the item\'s line on the parts list (sheet %d).' % SH_PARTS,
               ['The castor cross-beam (item 10) hangs from the raised nose cross-member (item 3) on one pin (item 11), 200 mm above the ground, so the two castors can rise and fall against each other; the bump stops (item 12) limit that to 2 degrees, about 10 mm at each castor.',
                'Red dashed circles: the room each castor needs to swivel (drawn at the height of the bumper\'s lower edge). The bumper bar sits 65 mm further forward than on B2-F, on a carrier (item 66) whose two arms and drop legs pass between the castors; the fixed beam behind the bar ends 200 mm from the centre line, 9 mm outside the nearest swivel circle.',
                'Bay floor and bay walls (items 41, 42) are cut back to clear the castors. The 5 kg ballast plate is deleted. ' + N_BLK], overlay=castor_room)
def sheet_ghost(n=10):
    view_sheet(n, 'carry', 'RL', 'Rear-left isometric, bin drawn see-through', 'The same view as sheet 7 with the bin body and lid see-through, so the comb under the front lip, the pad on the front wall and the lift carriage can be seen.',
               ['The comb (item 32), now 700 mm wide, sits under the lip along the front of the bin and its nib hooks behind the lip; the bin hangs from it. The fixed pad (item 39) sits 10 mm behind the nib tip. Its two rods slide in the guide block and two 134 mm springs push against a fixed cup plate behind the arm, so the pad really can move 45 mm; it presses on the front wall lower down and stops the bin swinging.',
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
                        + 'Wiring looms L1 to L12 are drawn in colour.')
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
    dr.text((2430, yy + 26), 'L1 to L12 are wiring looms; each travels with the part it is tied to.', font=F(16), fill=LOOMC)
    missing = [i for i in order if i not in shown]; keyplan(dr, 2180, 190, 'RL', cap=False)
    dr.text((60, H - 96), 'Pulled apart along the dashed lines. Seen from the rear-left; the bin side is nearest. Full details of every item are on sheet %d.' % SH_PARTS + ('' if not missing else '   Hidden in this view: item %s.' % ', '.join(tag(i) for i in missing)), font=F(18), fill=GREY)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, 'balloons', len(shown), 'of', len(order), 'missing', missing, flush=True)

# ------------------------------------------------------------------ parts list
POD = ['Motor controller, 2 x 30 A (CTL-L8)', 'Flight controller F405 running ArduPilot Rover (G18)', 'Companion computer (G23) with SD card and shutdown supply (S11)', 'RTK satellite receiver (RTK-L8)',
       '4G modem (G25)', 'Safety relay (SR-L8) and two watchdogs (S7)', 'Speed and standstill monitors (SLS-L8)', 'Fuse box (S2) and 24 V to 5 V converter (G27)',
       'Lights switching board (L6), audio amplifier (AU-L8)', 'Tilt switch (S13), temperature sensors (S12), tamper siren (S10)']
def sheet_parts(n=13):
    img, dr = new_sheet(n, 'Parts list', 'Item numbers match the labels on sheets 1 to 10 and the balloons on sheets %d and %d. "Their line" is the line in the other agent\'s parts list (BinRobo_B2F_BOM_2026-11-12).' % (SH_EX, SH_EX + 1))
    its = [it for it in MODEL['items']]; cols = [its[:31], its[31:62], its[62:]]; xw = 1040; f = F(19); fb = F(19, True); fn = F(15)
    def cut(s, wpx, fnt=None):
        fnt = fnt or f
        while dr.textlength(s, font=fnt) > wpx and len(s) > 6: s = s[:-2]
        return s
    for c, col in enumerate(cols):
        x = 60 + c * (xw + 34); y = 172; dr.text((x, y), 'Item', font=fb, fill=INK); dr.text((x + 62, y), 'Qty', font=fb, fill=INK); dr.text((x + 116, y), 'Description', font=fb, fill=INK)
        dr.text((x + 690, y), 'Their line', font=fb, fill=INK); dr.text((x + 930, y), 'Status', font=fb, fill=INK); dr.line([(x, y + 30), (x + xw, y + 30)], fill=INK, width=2); yy = y + 38
        for d_ in col:
            loom = d_['item'] > 200; nm = d_['name'].split('  ', 1)[1] if loom else d_['name']; st = {'CAD': 'their CAD', 'changed': 'CHANGED', 'new': 'NEW'}[d_['src']]
            dr.text((x + 4, yy), tag(d_['item']), font=fb, fill=LOOMC if loom else INK); dr.text((x + 72, yy), str(d_['qty']), font=f, fill=INK); dr.text((x + 116, yy), cut(nm, 566), font=f, fill=INK)
            dr.text((x + 690, yy), cut(d_['ref'] or '-', 236, F(18)), font=F(18), fill=GREY); dr.text((x + 930, yy), st, font=fb if d_['src'] != 'CAD' else f, fill=SRC_COL[d_['src']] if d_['src'] != 'CAD' else GREY)
            note = ('contents listed on sheet %d; not drawn individually' % SH_SAFE) if d_['item'] == 47 else d_['note']; yy += 25
            if note:
                for t in wrap(dr, note, fn, xw - 130): dr.text((x + 116, yy), t, font=fn, fill=GREY); yy += 19
            yy += 7
        if c == 2:
            yy += 14; dr.text((x, yy), 'Deleted from B2-F', font=fb, fill=INK); yy += 30
            for p in ('Keeper with its motor and switch (old item 36)', 'Pad toggle actuator, links and toggle-lock switch', 'Rail drop plates and fixed castor plates', 'Mast gussets (old item 24) and loose foot plates: now the welded foot shoe', 'Ballast plate 5 kg (old item 46): not needed at this weight'):
                dr.text((x + 12, yy), '- ' + p, font=F(17), fill=INK); yy += 24
        print('  parts column', c, 'ends at y', int(yy))
    rb = [d_ for d_ in its if not 100 < d_['item'] < 200]
    notes(dr, 60, 2104, ['Status: "their CAD" = as in the other agent\'s CAD model; CHANGED = altered; NEW = added in these drawings at a proposed position. %d robot items: %d their CAD, %d changed, %d new (12 of the new ones are looms). Items 101 to 104 are the bin.'
                         % (len(rb), sum(1 for d_ in rb if d_['src'] == 'CAD'), sum(1 for d_ in rb if d_['src'] == 'changed'), sum(1 for d_ in rb if d_['src'] == 'new')),
                         '"new line needed": the BOM has no line for it yet. "to change": the BOM line exists but describes the B2-F part. Still without a line: castor beam parts (10, 12), front camera (54), lift driver. To come out of the BOM: B2-PADACT, B2-TOGGLE, B1-PADLS, GR-07 and the ballast lines. Not placed in the drawing: pack heater HTR-L8.',
                         'Loom contents are grouped from the device list in their parts list and their earlier harness (Rev G6); wire sizes and connectors still have to be set out in a wiring table. Sheet %d gives the proposed safety chain and fusing.' % SH_SAFE])
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

# ------------------------------------------------------------------ wiring looms
def sheet_looms(n=14):
    img, dr = new_sheet(n, 'Wiring looms (proposed routing)', 'The robot is drawn faint and the twelve looms in colour, as if seen through the bodywork. The routing is proposed in these drawings; no B2-F wiring table exists yet.')
    cells = [(48, 176, 1500, 1500), (1528, 176, 2980, 1500)]; looms = [d_ for d_ in MODEL['items'] if d_['item'] > 200]
    grey = lambda e: None if e['kind'] == 'loom' or not e['render'] else (0.80, 0.82, 0.85, 1.0)
    only = lambda e: (*e['col'], 1.0) if e['kind'] == 'loom' else None
    SP = RN.Scene('nobin', style=grey); SL = RN.Scene('nobin', style=only); fits = [SP.fit(*RN.VIEWS[v][:2]) for v in ('RL', 'FR')]; mpp = max(max(wm / 1340.0, hm / 1230.0) for _, (wm, hm) in fits)
    for v, cell, (look, (wm, hm)) in zip(('RL', 'FR'), cells, fits):
        az, el, vname = RN.VIEWS[v]; w, h = int(wm / mpp) + 4, int(hm / mpp) + 4; a, pmA = SP.render(az, el, look, mpp, w, h, edge_col=(120, 126, 136)); b, pmB = SL.render(az, el, look, mpp, w, h)
        a = (255 - (255 - a.astype(np.float32)) * 0.45).astype(np.uint8); m = dilate(pmB >= 0, 1); a[m] = b[m]; ox = (cell[0] + cell[2] - w) // 2; oy = (cell[1] + cell[3] - h) // 2 + 14
        img.paste(Image.fromarray(a), (ox, oy)); dr.rectangle(cell, outline=(190, 195, 202), width=2); dr.text((cell[0] + 14, cell[1] + 10), vname + ' isometric', font=F(28, True), fill=INK)
        balloons(dr, (ox, oy), np.where((pmA >= 0) | (pmB >= 0), 0, -1), anchors(SL, pmB), [d_['item'] for d_ in looms], cell, r=24)
    keyplan(dr, 3050, 300, 'RL', cap=False); dr.text((3034, 420), 'left-hand view', font=F(17, True), fill=INK); keyplan(dr, 3050, 620, 'FR', cap=False); dr.text((3034, 780), 'right-hand view', font=F(17, True), fill=INK)
    x, y = 60, 1520; cw = (80, 300, 1230, 700); heads = ('Loom', 'Name', 'Route', 'Cables carried (proposed)'); xx = x; f = F(17)
    for hd, wd in zip(heads, cw): dr.text((xx, y), hd, font=F(18, True), fill=INK); xx += wd
    dr.line([(x, y + 28), (x + sum(cw), y + 28)], fill=INK, width=2); yy = y + 35
    for d_ in looms:
        e = [p for p in MODEL['parts'] if p['item'] == d_['item']][0]; col = tuple(int(255 * c) for c in e['col']); route, cores = d_['note'].rsplit('. ', 1); route = route[0].upper() + route[1:]
        rl = wrap(dr, route, f, cw[2] - 20); cl = wrap(dr, cores, f, cw[3] - 10)
        dr.rectangle([x, yy + 3, x + 16, yy + 19], fill=col, outline=INK); dr.text((x + 24, yy), tag(d_['item']), font=F(17, True), fill=INK); dr.text((x + cw[0], yy), d_['name'].split('  ', 1)[1], font=f, fill=INK)
        for k, t in enumerate(rl): dr.text((x + cw[0] + cw[1], yy + 21 * k), t, font=f, fill=INK)
        for k, t in enumerate(cl): dr.text((x + cw[0] + cw[1] + cw[2], yy + 21 * k), t, font=f, fill=GREY)
        yy += 21 * max(len(rl), len(cl)) + 7
    print('  loom table ends at y', int(yy))
    notes(dr, 60, yy + 6, ['L7 crosses to the moving carriage in a cable chain anchored on the mast, with one hand-off point on the carriage; the chain is sized for the full 335 mm of travel and has a bracket at each end (item 73). The two top limit switches are on different looms (L7 and L6), one per stop channel.',
                           'Changed in revision 3: L2, L3 and L4 run along the inner face of the side rails behind the side guards; every loom leaves the bay through a grommet in a cover; L6 runs on the front and top faces of the top tie; L9 runs over the nose cross-member and down a bumper leg; the charge pair is a loom of its own (L12), apart from the stop-loop cables.'], w=2300)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

# ------------------------------------------------------------------ safety functions, stop chain, power path and fusing (proposal, revision 3)
def sheet_safety(n=15):
    img, dr = new_sheet(n, 'Safety functions, stop chain, power path and fusing (proposed)', 'A proposal for the safety design, built from the devices in the B2-F parts list. Item numbers are those of sheet %d. The performance levels are targets; no calculation has been done.' % SH_PARTS)
    f = F(18); fb = F(18, True)
    def box(x, y, w, h, lines, col=INK, fill=(255, 255, 255), bold_first=True):
        dr.rounded_rectangle([x, y, x + w, y + h], 8, fill=fill, outline=col, width=3); th = 23 * len(lines); yy = y + (h - th) // 2
        for k, t in enumerate(lines):
            ft = fb if (k == 0 and bold_first) else f; tw = dr.textlength(t, font=ft); dr.text((x + (w - tw) / 2, yy), t, font=ft, fill=INK); yy += 23
    def line(pts, col=INK, width=4, dash=False, arrow=True):
        for a_, b_ in zip(pts[:-1], pts[1:]):
            if dash:
                L = math.hypot(b_[0] - a_[0], b_[1] - a_[1]); nseg = max(int(L / 18), 1)
                for k in range(nseg): dr.line([(a_[0] + (b_[0] - a_[0]) * k / nseg, a_[1] + (b_[1] - a_[1]) * k / nseg), (a_[0] + (b_[0] - a_[0]) * (k + 0.55) / nseg, a_[1] + (b_[1] - a_[1]) * (k + 0.55) / nseg)], fill=col, width=width)
            else: dr.line([a_, b_], fill=col, width=width)
        if arrow:
            (x1_, y1_), (x2_, y2_) = pts[-2], pts[-1]; ang = math.atan2(y2_ - y1_, x2_ - x1_)
            dr.polygon([(x2_, y2_), (x2_ - 18 * math.cos(ang - 0.42), y2_ - 18 * math.sin(ang - 0.42)), (x2_ - 18 * math.cos(ang + 0.42), y2_ - 18 * math.sin(ang + 0.42))], fill=col)
    PW = (170, 30, 30); SG = (22, 92, 170); LB = (252, 244, 240); LS = (240, 246, 252)
    # ---------------- power path
    dr.text((80, 176), 'Power path', font=F(26, True), fill=PW)
    box(80, 226, 210, 96, ['Battery', '24 V 20 Ah (45)'], PW, LB); box(330, 226, 210, 96, ['Main fuse 50 A', 'at the battery (65)'], PW, LB); box(580, 226, 190, 96, ['Isolator key', '(49)'], PW, LB)
    box(900, 226, 160, 96, ['Contactor', 'KM1'], PW, LB); box(1100, 226, 160, 96, ['Contactor', 'KM2'], PW, LB)
    for a_, b_ in ((290, 330), (540, 580), (770, 900), (1060, 1100)): line([(a_, 274), (b_, 274)], PW)
    line([(1260, 274), (1380, 274), (1380, 470)], PW, arrow=False); line([(1380, 274), (1450, 274)], PW); line([(1380, 470), (1450, 470)], PW)
    dr.text((1272, 236), 'switched', font=F(16, True), fill=PW); dr.text((1272, 284), 'feed', font=F(16, True), fill=PW)
    box(1450, 216, 500, 116, ['Drive controller (in the pod)', '2 gearmotors with spring brakes (5)', 'motor pairs 6 mm2, 30 A limit each'], PW, LB)
    box(1450, 380, 500, 180, ['Lift driver (in the power box, 48)', 'fuse 7.5 A, pair 2.5 mm2, current limit 4 A', 'runs only at standstill; "up" needs both', 'top switches (68) closed; actuator (27)'], PW, LB)
    # pre-charge and regeneration paths round the contactor pair
    line([(840, 274), (840, 412), (1320, 412), (1320, 274)], PW, width=3, dash=True, arrow=False); box(925, 388, 310, 48, ['pre-charge relay K3 + 1 kohm'], PW, (255, 255, 255), bold_first=False)
    line([(1340, 274), (1340, 354), (860, 354), (860, 274)], PW, width=3, dash=True); box(940, 332, 280, 44, ['diode: braking energy back'], PW, (255, 255, 255), bold_first=False)
    line([(810, 274), (810, 470)], PW); box(640, 470, 340, 76, ['Fuse box S2 (in the pod)', '15 A feed, 1.5 mm2'], PW, LB); line([(810, 546), (810, 590)], PW)
    box(640, 590, 340, 140, ['Stays on after a stop:', 'flight controller, companion,', 'satellite receiver, 4G modem,', 'lights, safety controller'], PW, LB)
    dr.text((652, 430), 'unswitched feed', font=F(16, True), fill=PW)
    box(80, 470, 210, 96, ['Dock charge', 'contacts (21)'], PW, LB); box(330, 470, 210, 96, ['10 A fuse +', 'ideal diode (48)'], PW, LB); line([(290, 518), (330, 518)], PW); line([(540, 518), (560, 518), (560, 274)], PW)
    dr.text((84, 574), 'loom L12, 2.5 mm2', font=F(16), fill=PW)
    # ---------------- stop chain
    dr.text((80, 770), 'Stop chain: every device on its own input pair', font=F(26, True), fill=SG)
    ins = [['E-stop button (50)', 'two contacts'], ['Front bumper switch, left (72)', 'two contacts'], ['Front bumper switch, right (72)', 'two contacts'], ['Rear bumper switch, left (18)', 'two contacts'], ['Rear bumper switch, right (18)', 'two contacts'],
           ['Two tilt switches (in the pod)', 'one per channel, mounted apart'], ['Speed and standstill monitor', 'two wheel sensors (8), two outputs'], ['Lift top switches (68)', 'channel A on L7, channel B on L6'], ['Watchdogs: flight controller, companion', 'one signal each']]
    y0 = 826; ycs = []
    for k, t in enumerate(ins): box(80, y0 + 76 * k, 520, 64, t, SG, LS); ycs.append(y0 + 76 * k + 32)
    for yc in ycs: line([(600, yc - 7), (700, yc - 7)], SG, width=3); line([(600, yc + 7), (700, yc + 7)], SG, width=3)
    box(700, 826, 380, 76 * 8 + 64, ['Safety controller', '(in the pod; replaces the', 'safety relay SR-L8)', '', '9 two-channel inputs,', 'each watched for a broken', 'wire and for a short', 'between its two channels', '', '2 safe outputs', '+ pre-charge and', 'lift-enable outputs'], SG, LS)
    box(700, 1560, 380, 70, ['Reset button (51), monitored'], SG, LS); line([(890, 1560), (890, 1498)], SG)
    line([(1020, 826), (1020, 322)], SG, arrow=True); line([(1080, 1040), (1180, 1040), (1180, 322)], SG)
    dr.text((1030, 600), 'coil KM1', font=F(16, True), fill=SG); dr.text((1190, 700), 'coil KM2', font=F(16, True), fill=SG); dr.text((1030, 622), '(loom L11)', font=F(16), fill=SG)
    line([(1240, 322), (1240, 1595), (1080, 1595)], SG, dash=True); dr.text((1250, 1180), 'feedback: the mirror contacts of', font=F(16), fill=SG); dr.text((1250, 1202), 'BOTH contactors, in series; a reset', font=F(16), fill=SG); dr.text((1250, 1224), 'is accepted only if both are closed', font=F(16), fill=SG)
    line([(1080, 1300), (1982, 1300), (1982, 470), (1950, 470)], SG, width=3); dr.text((1340, 1268), 'lift enable: standstill + both top switches', font=F(16), fill=SG)
    box(925, 388, 310, 48, ['pre-charge relay K3 + 1 kohm'], PW, (255, 255, 255), bold_first=False); box(940, 332, 280, 44, ['diode: braking energy back'], PW, (255, 255, 255), bold_first=False)   # labels drawn again, over the coil lines
    box(1450, 640, 500, 250, ['On any stop', 'both contactors open;', 'drive and lift lose power;', 'the spring brakes apply;', 'the screw actuator holds the bin (to be', 'confirmed by its supplier, or a brake added);', 'computers, lights and alerts stay on'], INK, (246, 246, 246))
    # ---------------- right-hand panel
    x = 2020; y = 176; dr.text((x, y), 'Safety functions and target levels', font=F(24, True), fill=INK); y += 36
    cw = (430, 520, 110); hd = ('What triggers it', 'What happens', 'Target'); xx = x
    for h_, w_ in zip(hd, cw): dr.text((xx, y), h_, font=F(19, True), fill=INK); xx += w_
    dr.line([(x, y + 24), (x + sum(cw) + 140, y + 24)], fill=INK, width=2); y += 30
    SFN = [('E-stop pressed', 'both contactors open, brakes apply', 'PL d'), ('Front or rear bumper pressed', 'both contactors open, brakes apply', 'PL d'), ('Speed above the limit, or motion when a standstill is commanded', 'both contactors open, brakes apply', 'PL d'),
           ('Tilt beyond the limit (two switches)', 'both contactors open, brakes apply', 'PL c'), ('Lift above 327 mm (two switches)', 'lift "up" blocked; above them, bolted stops at 335 mm', 'PL c'),
           ('Lift commanded while moving', 'lift driver not enabled', 'PL c'), ('Flight controller or companion stops answering', 'both contactors open, brakes apply', 'PL b'), ('A contactor fails to open', 'no reset; the other contactor still opens the circuit', 'part of the above')]
    for a_, b_, c_ in SFN:
        la = wrap(dr, a_, F(18), cw[0] - 14); lb = wrap(dr, b_, F(18), cw[1] - 14)
        for k, t in enumerate(la): dr.text((x, y + 23 * k), t, font=F(18), fill=INK)
        for k, t in enumerate(lb): dr.text((x + cw[0], y + 23 * k), t, font=F(18), fill=INK)
        dr.text((x + cw[0] + cw[1], y), c_, font=F(16, True), fill=INK); y += 23 * max(len(la), len(lb)) + 8
    for t in wrap(dr, 'Targets are my proposal from the risk graph of ISO 13849-1 (serious injury possible, slow machine, private lane). They are not a calculation: the component data (failure rates, diagnostic coverage, common-cause measures) still have to be collected and the levels verified.', F(18), 1190):
        dr.text((x, y), t, font=F(18), fill=RED); y += 23
    y += 16; dr.text((x, y), 'Fuses and wire sizes', font=F(24, True), fill=INK); y += 36
    for hd_, tx in (('Battery trunk (L1)', 'main fuse 50 A at the battery positive; 10 mm2 to the isolator, the contactors and the drive controller.'), ('Motor pairs (L2, L3)', '6 mm2; current limit 30 A per channel in the drive controller.'),
                    ('Lift (L5)', 'fuse 7.5 A; 2.5 mm2. The supplier lists 3 A maximum for the actuator; the driver limit is set to 4 A so a stalled lift is cut off by current, not by the fuse.'),
                    ('Charge (L12)', 'fuse 10 A and ideal diode in the power box; 2.5 mm2; joins the battery side of the isolator.'), ('Electronics (unswitched)', 'fuse box S2: 15 A feed in 1.5 mm2; branch fuses 2 to 5 A in 0.5 to 0.75 mm2.'),
                    ('Stop-loop and limit-switch pairs', '0.5 mm2, on a 2 A fuse; the two channels of a device never share a cable with motor or charge wires (L9 and L12 are separate for this reason).'),
                    ('Pre-charge and braking energy', 'a 1 kohm 2 W resistor through relay K3 charges the drive controller before the contactors close; a power diode across the contactor pair lets braking energy return to the battery when they are open. Both follow the drive-controller maker\'s manual.')):
        dr.text((x, y), hd_, font=fb, fill=INK); y += 23
        for t in wrap(dr, tx, F(18), 1176): dr.text((x + 14, y), t, font=F(18), fill=GREY); y += 23
        y += 5
    y += 12; dr.text((x, y), 'Open points', font=F(24, True), fill=RED); y += 34
    for tx in ('The lift driver is described here by what it must do (24 V, 10 A or more, adjustable current limit, fault output, enable input). No part is chosen or priced.',
               'The safety controller replaces the safety relay in the parts list because nine devices need their own monitored inputs. No part is chosen or priced.',
               'That the actuator holds its load without power is not on the supplier\'s page. Ask the supplier in writing, or add a brake or a latch.',
               'The supplier lists no position signal on this actuator: lift height comes from the load-on event and time, bounded by the switches and stops.',
               'The pack heater (BOM HTR-L8) is not placed. Connectors are not chosen.'):
        for k, t in enumerate(wrap(dr, tx, F(18), 1176)): dr.text((x + (0 if k == 0 else 16), y), ('- ' if k == 0 else '') + t, font=F(18), fill=INK); y += 23
        y += 5
    print('  safety sheet right panel ends at y', int(y))
    notes(dr, 60, 1700, ['Red: power. Blue: the stop chain. Solid lines are wires; dashed lines are the pre-charge path, the braking-energy diode and the contactor feedback loop.',
                         'Changed from revision 2: each stop device has its own two-channel input instead of being chained in series; two tilt switches; feedback from both contactors; the lift is interlocked with standstill and with two top switches; pre-charge and a path for braking energy are added.',
                         'Inside the electronics pod (item 47), not drawn: ' + '; '.join(p.split(' (')[0] for p in POD) + '.',
                         'A stop removes motion power only. The computers stay up so the robot can report where it stopped and why. This sheet is a proposal to be checked, not a wiring table.'], w=1880)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

# ------------------------------------------------------------------ dimension sheet: side and plan views, to scale
def sheet_dims(n=16):
    img, dr = new_sheet(n, 'Main dimensions', 'Side view from the right and plan view from above, robot without the bin, comb at its lowest position. Parallel projection: both views are to the same scale. Dimensions in mm, taken from the model.')
    S = RN.Scene('nobin', style=lambda e: None if e['kind'] == 'loom' or not e['render'] else (*e['col'], 1.0)); fd = F(20, True)
    views = [('side', 90.0, 0.0, (60, 190, 1820, 1990)), ('plan', 90.0, -89.99, (1850, 190, 3250, 1990))]; fits = [S.fit(az, el) for _, az, el, _ in views]
    mpp = max(max(wm / (c[2] - c[0] - 430.0), hm / (c[3] - c[1] - 430.0)) for (_, _, _, c), (_, (wm, hm)) in zip(views, fits))
    def hdim(P, xa, xb, yy, txt, up=True):
        (ax, ay), (bx, by) = P(xa), P(xb); dr.line([(ax, ay), (ax, yy)], fill=GREY, width=1); dr.line([(bx, by), (bx, yy)], fill=GREY, width=1); dr.line([(ax, yy), (bx, yy)], fill=BLUE, width=3)
        for x_, sg in ((ax, 1), (bx, -1)): dr.polygon([(x_, yy), (x_ + sg * 16, yy - 6), (x_ + sg * 16, yy + 6)], fill=BLUE)
        tw = dr.textlength(txt, font=fd); dr.text(((ax + bx - tw) / 2, yy - 30 if up else yy + 6), txt, font=fd, fill=BLUE)
    def vdim(P, pa, pb, xx, txt, side=None):
        """vertical dimension at pixel column xx; text turned 90 degrees beside the line, or (side='r') written level to the right for short spans"""
        (ax, ay), (bx, by) = P(pa), P(pb); dr.line([(ax, ay), (xx, ay)], fill=GREY, width=1); dr.line([(bx, by), (xx, by)], fill=GREY, width=1); dr.line([(xx, ay), (xx, by)], fill=BLUE, width=3)
        lo, hi = max(ay, by), min(ay, by)
        dr.polygon([(xx, lo), (xx - 6, lo - 16), (xx + 6, lo - 16)], fill=BLUE); dr.polygon([(xx, hi), (xx - 6, hi + 16), (xx + 6, hi + 16)], fill=BLUE)
        tw = int(dr.textlength(txt, font=fd)) + 8
        if side == 'r': dr.text((xx + 12, (lo + hi) / 2 - 12), txt, font=fd, fill=BLUE); return
        t = Image.new('RGBA', (tw, 30), (255, 255, 255, 0)); ImageDraw.Draw(t).text((4, 2), txt, font=fd, fill=BLUE + (255,)); t = t.rotate(90, expand=True); img.paste(t, (int(xx - 36), int(min((lo + hi) / 2 - tw / 2, lo - tw - 2))), t)
    for (name, az, el, c), (look, (wm, hm)) in zip(views, fits):
        w, h = int(wm / mpp) + 4, int(hm / mpp) + 4; vi, pm = S.render(az, el, look, mpp, w, h); ox = (c[0] + c[2] - w) // 2; oy = (c[1] + c[3] - h) // 2 + (30 if name == 'side' else 0)
        img.paste(Image.fromarray(vi), (ox, oy)); dr.rectangle(c, outline=(190, 195, 202), width=2); dr.text((c[0] + 14, c[1] + 10), 'Side view (nose to the right)' if name == 'side' else 'Plan view (nose to the right, left side up)', font=F(26, True), fill=INK)
        P = lambda p: tuple(S.project([p], az, el, look, mpp, w, h)[0] + np.array([ox, oy])); top = oy - 10; bot = oy + h + 10; lft = ox - 10; rgt = ox + w + 10
        if name == 'side':
            gy = P((0, 0, 0))[1]; dr.line([(ox - 40, gy), (ox + w + 40, gy)], fill=INK, width=3)
            hdim(P, (-0.401, 0, 0), (1.171, 0, 0), bot + 150, 'overall 1,572', up=False); hdim(P, (0, 0, 0), (0.95, 0, 0), bot + 80, 'drive axle to castor swivel axis 950', up=False); hdim(P, (-0.401, 0, 0), (0, 0, 0), bot + 80, '401', up=False)
            hdim(P, (0, 0, 1.42), (0.415, 0, 1.42), top - 40, 'axle to comb face 415'); hdim(P, (0.95, 0, 1.42), (1.155, 0, 1.42), top - 40, 'to bumper face 205')
            vdim(P, (1.171, 0, 0.13), (1.171, 0, 0.23), rgt + 40, 'bumper 130 to 230', side='r'); vdim(P, (1.171, 0, 0.36), (1.171, 0, 0.41), rgt + 40, 'rails 360 to 410', side='r')
            vdim(P, (1.171, 0, 0), (1.171, 0, 1.42), rgt + 270, 'top of the mast 1,420'); vdim(P, (1.171, 0, 0), (1.171, 0, 1.51), rgt + 330, 'top of the beacon 1,510')
            vdim(P, (-0.401, 0, 0), (-0.401, 0, 0.275), lft - 40, 'pad centre 275'); vdim(P, (-0.401, 0, 0), (-0.401, 0, 0.855), lft - 110, 'top of the nib, comb down 855'); vdim(P, (-0.401, 0, 0), (-0.401, 0, 1.19), lft - 180, 'top of the nib at the bolted stops 1,190')
        else:
            hdim(P, (-0.401, 0.465, 0), (1.171, 0.465, 0), top - 40, 'overall 1,572'); vdim(P, (1.171, -0.33, 0), (1.171, 0.33, 0), rgt + 50, 'bumper bar 660'); vdim(P, (1.171, -0.465, 0), (1.171, 0.465, 0), rgt + 120, 'overall width 930')
            vdim(P, (-0.401, -0.358, 0), (-0.401, 0.358, 0), lft - 40, 'between the side guards 716'); vdim(P, (-0.401, -0.35, 0), (-0.401, 0.35, 0), lft - 110, 'comb 700'); vdim(P, (-0.401, -0.4, 0), (-0.401, 0.4, 0), lft - 180, 'drive wheel track 800')
            hdim(P, (-0.37, -0.465, 0), (0.98, -0.465, 0), bot + 80, 'side rails 1,350', up=False); hdim(P, (0.49, -0.465, 0), (0.955, -0.465, 0), bot + 150, 'mast-base to nose cross-member 465', up=False)
    notes(dr, 60, 2010, ['Heights: castor pivot pin 200; drive wheels 330 diameter; castors 200 diameter, 280 either side of the centre line; lowest fixed part 120 (bay floor). Lift: firmware stop at 320 of travel, limit switches at 327, bolted stops at 335; at the stops the carriage plate is 35 below the top tie.',
                         'With a 240 L bin on board the overall length is 1,617. The pivot-turn circle measured in simulation is 2.46 m across. Dimensions are of this concept model, not of a built machine.'], w=2300)
    img.save(os.path.join(OUT, 'sheet%02d.png' % n)); print('sheet', n, flush=True)

JOBS = {}
for k, (st, v) in enumerate([(s, v) for s in ('nobin', 'carry') for v in ('FL', 'FR', 'RL', 'RR')]): JOBS[k + 1] = (lambda st=st, v=v, k=k: iso_sheet(k + 1, st, v))
JOBS.update({9: sheet_under, 10: sheet_ghost, 11: lambda: exploded_sheet(11, 'nobin'), 12: lambda: exploded_sheet(12, 'carry'), 13: sheet_parts, 14: sheet_looms, 15: sheet_safety, 16: sheet_dims})
if __name__ == '__main__':
    for n in ([int(a) for a in sys.argv[1:]] or sorted(JOBS)): JOBS[n]()
