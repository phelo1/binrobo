# NOT USED. Tried on 27 Nov and withdrawn: on a ragged hedge (depth scatter 0.15 m, 20 % dropouts) this test gave two false free-standing runs in every scan.
# patch 2 (revision 6.1): free-standing things in front of the hedge. Run when no test is running.
import sys
p='/home/claude/b2f_run/sitl/b2f/scripts/b2f_r6.py'; s=open(p).read()
def rep(old,new,n=1):
    global s
    assert s.count(old)==n, (s.count(old), old[:80]); s=s.replace(old,new)

rep("""def rect_dist(bx, by):""",
"""FG = os.environ.get('X_R6_FG', '1') == '1'      # [revision 6.1] free-standing things in front of the hedge are told from it by the range jump on both sides


def fg_runs(r, seen=None, circ=False, jump=0.25, wmin=0.12, wmax=1.2, step=math.radians(1.0)):
    \"\"\"[revision 6.1] which returns of one lidar scan belong to a thing that stands FREE in front of whatever is behind it.
    r = ranges in angular order, one step apart (inf = no return). A run of three or more returns whose ranges follow on from each other,
    between 0.12 and 1.2 m wide, is free-standing if on BOTH sides the next return (within four rays) is more than `jump` farther off,
    or there is none. A person 0.3 m in front of a hedge shows such a run; a bulge of the hedge does not, and neither does a hedge end
    (one side only). seen = rays the lidar can use at all (outside it nothing is known, so a run that touches it does not count).\"\"\"
    r = np.asarray(r, float); n = len(r); out = np.zeros(n, bool)
    if n < 5: return out
    fin = np.isfinite(r); seen = np.ones(n, bool) if seen is None else np.asarray(seen, bool)
    idx = np.where(fin)[0]
    if len(idx) < 3: return out
    # runs: consecutive finite returns at most 3 rays apart whose ranges differ by less than jump
    runs = []; cur = [int(idx[0])]
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a <= 3 and abs(r[b] - r[a]) < jump: cur.append(int(b))
        else: runs.append(cur); cur = [int(b)]
    runs.append(cur)
    if circ and len(runs) > 1 and (idx[0] + n - idx[-1]) <= 3 and abs(r[idx[0]] - r[idx[-1]]) < jump: runs[0] = runs.pop() + runs[0]
    def side(i0, d, r_edge):
        \"\"\"True = open or farther on this side; False = something as near or nearer; None = not known (edge of what the lidar sees)\"\"\"
        for k in range(1, 5):
            j = i0 + d * k
            if circ: j %= n
            elif j < 0 or j >= n: return None
            if not seen[j]: return None
            if fin[j]: return bool(r[j] - r_edge > jump)
        return True
    for run in runs:
        if len(run) < 3: continue
        a, b = run[0], run[-1]; span = ((b - a) % n) * step
        wdt = math.hypot(r[b] * math.cos(span) - r[a], r[b] * math.sin(span))
        if not (wmin <= wdt <= wmax): continue
        if side(a, -1, r[a]) is True and side(b, +1, r[b]) is True: out[run] = True
    return out


def rect_dist(bx, by):""")

# rear lidars: keep the free-standing flags of each scan
rep("""        segs = [q for q in segs if len(q)]; Sg = np.concatenate(segs) if segs else np.zeros((0, 4)); movers = w.movers_now(); out = []""",
"""        segs = [q for q in segs if len(q)]; Sg = np.concatenate(segs) if segs else np.zeros((0, 4)); movers = w.movers_now(); out = []; self._rear_fg = []""")
rep("""            ok = np.isfinite(r); r = r[ok] + self._r6rng.normal(0, 0.01, int(ok.sum())); a = np.radians(rel[ok])
            out.append(np.c_[lx + r * np.cos(a), ly + r * np.sin(a)])
        return np.concatenate(out) if out else np.zeros((0, 2))""",
"""            ok = np.isfinite(r); r[ok] = r[ok] + self._r6rng.normal(0, 0.01, int(ok.sum()))
            self._rear_fg.append(fg_runs(r)[ok] if FG else np.zeros(int(ok.sum()), bool))
            r = r[ok]; a = np.radians(rel[ok])
            out.append(np.c_[lx + r * np.cos(a), ly + r * np.sin(a)])
        return np.concatenate(out) if out else np.zeros((0, 2))""")

# all points + flags
rep("""        P = []
        if self.scan is not None:
            r = self.scan; ok = np.isfinite(r)
            if ok.any():
                a = np.radians(np.arange(360))[ok]; P.append(np.c_[ROB['lidar_x'] + r[ok] * np.cos(a), r[ok] * np.sin(a)])
        if REAR: P.append(self.rear_scan())
        P = [q for q in P if len(q)]
        return np.concatenate(P) if P else np.zeros((0, 2))""",
"""        P = []; F = []
        if self.scan is not None:
            r = self.scan; ok = np.isfinite(r)
            if ok.any():
                a = np.radians(np.arange(360))[ok]; P.append(np.c_[ROB['lidar_x'] + r[ok] * np.cos(a), r[ok] * np.sin(a)])
                rel_ = np.arange(360); F.append(fg_runs(r, seen=~((rel_ > 105) & (rel_ < 255)), circ=True)[ok] if FG else np.zeros(int(ok.sum()), bool))
        if REAR:
            Pr = self.rear_scan(); P.append(Pr); F.append(np.concatenate(self._rear_fg) if len(self._rear_fg) else np.zeros(0, bool))
        keep_ = [i for i, q in enumerate(P) if len(q)]
        self._r6_fg = np.concatenate([F[i] for i in keep_]) if keep_ else np.zeros(0, bool)
        return np.concatenate([P[i] for i in keep_]) if keep_ else np.zeros((0, 2))""")

rep("""        B = B[(np.hypot(B[:, 0], B[:, 1]) < rng + 1.5) & (rect_dist(B[:, 0], B[:, 1]) > 0.03)]
        if len(B) == 0: return self._r6_objs""",
"""        sel_ = (np.hypot(B[:, 0], B[:, 1]) < rng + 1.5) & (rect_dist(B[:, 0], B[:, 1]) > 0.03)
        fg = self._r6_fg[sel_] if len(getattr(self, '_r6_fg', [])) == len(B) else np.zeros(int(sel_.sum()), bool); B = B[sel_]
        if len(B) == 0: return self._r6_objs""")

rep("""        self._r6_hedge = B[hedge]      # for the gateway look-ahead (r6_gap_ahead)""",
"""        # [revision 6.1] a free-standing run (range jump on both sides, fg_runs) is not hedge, however close to the hedge it stands: someone
        # walking 0.3 to 0.45 m from the hedge was only told from it at 2 to 3 m (turn tests b and c). Outside the house yard only: by
        # the house, pipes and corners of walls would pass for free-standing things and block the turns there.
        fg_on = FG and float(self.w.s_lat()[0]) > 30.0
        if fg_on: hedge &= ~fg
        else: fg = np.zeros(N, bool)
        self._r6_hedge = B[hedge]      # for the gateway look-ahead (r6_gap_ahead)""")

rep("""        prev = getattr(self, '_r6_prev', []) if now - getattr(self, '_r6_prev_t', -9.0) < 0.35 else []; hist = self.st.setdefault('r6_hist', []); objs = []
        for q in range(nl):
            Bq = Bm[lab == q]; Wq = Wm[lab == q]""",
"""        prev = getattr(self, '_r6_prev', []) if now - getattr(self, '_r6_prev_t', -9.0) < 0.35 else []; hist = self.st.setdefault('r6_hist', []); objs = []
        fgm = fg[m]
        for q in range(nl):
            Bq = Bm[lab == q]; Wq = Wm[lab == q]; fgq = fgm[lab == q]""")
rep("""                if dh < 0.20 + 0.05 * rq: continue""",
"""                if dh < 0.20 + 0.05 * rq and not (len(fgq) and fgq.mean() >= 0.5): continue""")
open(p,'w').write(s)
import ast; ast.parse(s); print('patch 2 applied')
