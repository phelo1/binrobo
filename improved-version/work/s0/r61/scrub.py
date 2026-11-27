#!/usr/bin/env python3
"""Cleans a directory tree for a PUBLIC repository: the place where the robot runs must not be findable from the files.

usage: scrub.py <tree> [--owner mine|other] [--report <json>]      (changes the tree in place)
       scrub.py --verify <tree> [<tree> ...]                         (changes nothing; exit code 1 if anything is left)

What it does
  1. Coordinates. Every latitude / longitude of the site is moved to a made-up origin (53.000000 N, 8.000000 W). The move keeps
     every distance in metres exactly as it was, so the lane keeps its shape and every test runs the same:
         lat' = LAT0N + (lat - LAT0)            lon' = LON0N + (lon - LON0) * MX / MXN
     The real origin is read at run time from the private working copy (PRIVATE_WORLD); it is not in this file.
  2. OpenStreetMap way numbers of the lane are replaced by 0, and raw OpenStreetMap extracts are removed.
  3. Place names (village, county, council, road number, nearby towns, postcodes) are replaced by neutral words. The list of names
     is read at run time from PRIVATE_NAMES; it is not in this file either.
  4. Files that cannot be cleaned or checked are removed and listed: flight logs, firmware binaries, and - for material that is not
     this agent's own - pictures, videos and PDFs (a PDF is replaced by its text, cleaned).
Every removal and every changed file is written to the report."""
import sys, os, re, json, math, gzip, subprocess, io

PRIVATE_WORLD = '/home/claude/b2f_run/sitl/b2f/scripts_base/world.py'
PRIVATE_ROUTE = '/home/claude/b2f_run/sitl/b2f/data/route.json'
PRIVATE_NAMES = '/home/claude/s0/r61/private_names.json'
LAT0N, LON0N = 53.0, -8.0


def private():
    src = open(PRIVATE_WORLD).read(); m = re.search(r'LAT0,\s*LON0\s*=\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)', src)
    lat0, lon0 = float(m.group(1)), float(m.group(2)); rt = json.load(open(PRIVATE_ROUTE))
    la = [p[0] for p in rt['ll']] + [p[0] for p in rt['vertices_ll']]; lo = [p[1] for p in rt['ll']] + [p[1] for p in rt['vertices_ll']]
    names = json.load(open(PRIVATE_NAMES))
    return dict(lat0=lat0, lon0=lon0, lat=(min(la + [lat0]) - 0.03, max(la + [lat0]) + 0.03), lon=(min(lo + [lon0]) - 0.04, max(lo + [lon0]) + 0.04),
                ways=[str(w) for w in rt.get('osm_ways', [])], names=names)


P = private()
MX = 111320 * math.cos(math.radians(P['lat0'])); MXN = 111320 * math.cos(math.radians(LAT0N))
NUM = re.compile(r'(?<![\d.])(-?\d{1,3}\.\d{4,})(?![\d])')
NAME_RULES = [(re.compile(pat, 0 if cs else re.I), rep) for pat, rep, cs in P['names']['rules']]
NAME_CHECK = re.compile(P['names']['check'], re.I); NAME_CHECK_CS = re.compile(P['names']['check_cs'])
WAYS = re.compile(r'(?<!\d)(' + '|'.join(re.escape(w) for w in P['ways']) + r')(?!\d)') if P['ways'] else None
E7 = re.compile(r'(?<![\d.])(-?\d{9,10})(?![\d.])')
DROP_NAME = re.compile(r'(^osm_.*\.(xml|json)$|\.osm$|\.BIN$|\.tlog(\.raw)?$|^eeprom\.bin$|^ardu(rover|copter|plane).*|\.elf$|\.pid$)')
BIN_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm', '.pdf', '.bin', '.npz', '.pkl', '.step', '.stp', '.stl', '.xlsx', '.docx', '.zip')


def is_lat(v): return P['lat'][0] <= v <= P['lat'][1]
def is_lon(v): return P['lon'][0] <= v <= P['lon'][1]


def e7_hits(text):
    out = []
    for m in E7.finditer(text):
        v = int(m.group(1)) / 1e7
        if is_lat(v) or is_lon(v): out.append(m.group(1))
    return out


def move(text):
    """returns (new text, n moved, lone tokens left alone)"""
    toks = [(m, float(m.group(1))) for m in NUM.finditer(text)]
    has_lat = any(is_lat(v) for _, v in toks); has_lon = any(is_lon(v) for _, v in toks)
    if not (has_lat or has_lon): return text, 0, []
    if not (has_lat and has_lon):      # only one kind in the whole file: not taken for a position. Reported, and looked at by hand.
        return text, 0, [m.group(1) for m, v in toks if is_lat(v) or is_lon(v)][:5]
    n = [0]
    def sub(m):
        s = m.group(1); v = float(s); dec = len(s.split('.')[1])
        if is_lat(v): n[0] += 1; return '%.*f' % (dec, LAT0N + (v - P['lat0']))
        if is_lon(v): n[0] += 1; return '%.*f' % (dec, LON0N + (v - P['lon0']) * MX / MXN)
        return s
    return NUM.sub(sub, text), n[0], []


def clean_text(text):
    """-> (text, dict of counts, lone)"""
    c = {}
    t2, n, lone = move(text)
    if n: c['coords'] = n
    if WAYS is not None:
        t2, k = WAYS.subn('0', t2)
        if k: c['ways'] = k
    for rx, rep in NAME_RULES:
        t2, k = rx.subn(rep, t2)
        if k: c['names'] = c.get('names', 0) + k
    return t2, c, lone


def looks_text(b): return b'\x00' not in b[:65536]


def leftovers(text):
    """independent check, used by --verify: anything that still points at the place"""
    bad = []
    toks = [(m.group(1), float(m.group(1))) for m in re.finditer(r'(?<![\d.])(-?\d{1,3}\.\d{3,})(?![\d])', text)]
    la = [s for s, v in toks if is_lat(v)]; lo = [s for s, v in toks if is_lon(v)]
    la4 = [s for s in la if len(s.split('.')[1]) >= 4]; lo4 = [s for s in lo if len(s.split('.')[1]) >= 4]
    if la4 and lo4: bad.append('lat and lon in range (%d, %d)' % (len(la4), len(lo4)))
    elif la or lo: bad.append('LONE or 3-decimal numbers in range: lat-like x%d, lon-like x%d (%d, %d with 4+ decimals)' % (len(la), len(lo), len(la4), len(lo4)))
    if WAYS is not None and WAYS.search(text): bad.append('way number')
    m = NAME_CHECK.search(text) or NAME_CHECK_CS.search(text)
    if m: bad.append('name: ' + m.group(0)[:1] + '***')
    if e7_hits(text): bad.append('scaled coordinate')
    return bad


def pdf_text(path):
    try: return subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
    except Exception: return ''


def scrub(tree, owner, report):
    for dp, dn, fn in os.walk(tree, topdown=False):
        for f in fn:
            p = os.path.join(dp, f); rel = os.path.relpath(p, tree); low = f.lower()
            if os.path.islink(p): os.remove(p); report['removed'].append((rel, 'link')); continue
            if DROP_NAME.search(f): sz = os.path.getsize(p); os.remove(p); report['removed'].append((rel, 'map extract, flight log or firmware file', sz)); continue
            ext = os.path.splitext(low)[1]
            if low.endswith('.gz'):
                try: raw = gzip.open(p, 'rb').read()
                except Exception: os.remove(p); report['removed'].append((rel, 'unreadable gz')); continue
                if not looks_text(raw): os.remove(p); report['removed'].append((rel, 'binary inside gz')); continue
                t = raw.decode('utf-8', 'surrogateescape'); t2, c, lone = clean_text(t)
                if lone: report['lone'].append((rel, lone))
                if c:
                    with open(p, 'wb') as fh:
                        with gzip.GzipFile(fileobj=fh, mode='wb', mtime=0) as g: g.write(t2.encode('utf-8', 'surrogateescape'))
                    report['changed'].append((rel, c))
                continue
            if ext in BIN_EXT:
                other = owner == 'other' or '/reference/other_agent/' in '/' + rel or rel.startswith('reference/other_agent/')
                if ext == '.pdf' and other:      # a PDF of the other agent: keep its text, cleaned; the PDF itself cannot be cleaned
                    t = pdf_text(p); t2, c, lone = clean_text(t); sz = os.path.getsize(p); os.remove(p)
                    open(p + '.txt', 'w').write('[text of %s, taken out of the PDF for the public repository; pictures and layout are not kept]\n\n' % f + t2)
                    report['removed'].append((rel, 'PDF replaced by its text', sz)); continue
                if other:
                    sz = os.path.getsize(p); os.remove(p); report['removed'].append((rel, 'picture, video or binary of the other agent: not checked', sz)); continue
                if ext == '.pdf':      # own PDF: must be clean as it is
                    bad = leftovers(pdf_text(p))
                    if bad: sz = os.path.getsize(p); os.remove(p); report['removed'].append((rel, 'own PDF with ' + '; '.join(bad), sz))
                    continue
                if ext in ('.xlsx', '.docx', '.zip', '.pkl', '.npz', '.bin'):
                    raw = open(p, 'rb').read(); t = raw.decode('latin-1')
                    if ext in ('.xlsx', '.docx', '.zip'):
                        try:
                            import zipfile; z = zipfile.ZipFile(io.BytesIO(raw)); t = '\n'.join(z.read(n).decode('utf-8', 'replace') for n in z.namelist() if z.getinfo(n).file_size < 20e6)
                        except Exception: pass
                    bad = leftovers(t)
                    if bad: sz = os.path.getsize(p); os.remove(p); report['removed'].append((rel, 'binary with ' + '; '.join(bad), sz))
                continue      # own pictures and videos: drawings, renders of the model and plots; kept
            raw = open(p, 'rb').read()
            if not looks_text(raw):
                bad = leftovers(raw.decode('latin-1'))
                if bad or owner == 'other': sz = len(raw); os.remove(p); report['removed'].append((rel, 'binary: ' + ('; '.join(bad) or 'not checked'), sz))
                continue
            t = raw.decode('utf-8', 'surrogateescape'); t2, c, lone = clean_text(t)
            if lone: report['lone'].append((rel, lone))
            e7 = e7_hits(t2)
            if e7: os.remove(p); report['removed'].append((rel, 'scaled coordinates in a text file', len(raw))); continue
            if c: open(p, 'wb').write(t2.encode('utf-8', 'surrogateescape')); report['changed'].append((rel, c))
        # names in file and folder names
        for name in list(fn) + list(dn):
            p = os.path.join(dp, name)
            if not os.path.lexists(p): continue
            n2 = name
            for rx, rep in NAME_RULES: n2 = rx.sub(re.sub(r'[\[\] ]', '', rep) or 'x', n2)
            if n2 != name: os.rename(p, os.path.join(dp, n2)); report['renamed'].append((os.path.relpath(p, tree), n2))
        if not os.listdir(dp) and dp != tree: os.rmdir(dp)


def verify(trees):
    bad = []; n = 0
    for tree in trees:
        for dp, dn, fn in os.walk(tree):
            if '.git' in dn: dn.remove('.git')
            for name in list(fn) + list(dn):
                if NAME_CHECK.search(name) or NAME_CHECK_CS.search(name): bad.append((os.path.join(dp, name), ['name in a file or folder name']))
            for f in fn:
                p = os.path.join(dp, f); low = f.lower(); n += 1
                if DROP_NAME.search(f): bad.append((p, ['file kind that should have been removed'])); continue
                try:
                    if low.endswith('.gz'): t = gzip.open(p, 'rb').read().decode('latin-1')
                    elif low.endswith('.pdf'): t = pdf_text(p)
                    elif low.endswith(('.xlsx', '.docx', '.zip')):
                        import zipfile; z = zipfile.ZipFile(p); t = '\n'.join(z.read(k).decode('utf-8', 'replace') for k in z.namelist() if z.getinfo(k).file_size < 20e6)
                    elif low.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm')): continue      # pictures: by rule (own ones only), not by content
                    else: t = open(p, 'rb').read().decode('latin-1')
                except Exception as e: bad.append((p, ['unreadable: %s' % e])); continue
                b = leftovers(t)
                if b: bad.append((p, b))
    return n, bad


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--verify':
        n, bad = verify(a[1:]); hard = [b for b in bad if not all(x.startswith('LONE') for x in b[1])]; lone = [b for b in bad if b not in hard]
        print('checked %d files: %d with something left, %d with a lone number in range' % (n, len(hard), len(lone)))
        for p, b in hard[:60]: print('  LEFT ', p[-150:], b)
        for p, b in lone[:40]: print('  lone ', p[-150:], b)
        sys.exit(1 if hard else 0)
    tree = a[0]; owner = a[a.index('--owner') + 1] if '--owner' in a else 'mine'
    rep = dict(removed=[], changed=[], renamed=[], lone=[]); scrub(tree, owner, rep)
    if '--report' in a:
        rp = a[a.index('--report') + 1]; old = json.load(open(rp)) if os.path.exists(rp) else dict(removed=[], changed=[], renamed=[], lone=[])
        for k in rep: old[k] += [[tree] + list(x) for x in rep[k]]
        json.dump(old, open(rp, 'w'), indent=0)
    print('%s: removed %d, changed %d, renamed %d, lone %d' % (tree[-70:], len(rep['removed']), len(rep['changed']), len(rep['renamed']), len(rep['lone'])))
