import pickle, sys
d = pickle.load(open('../ckpt/%s.pkl' % sys.argv[1], 'rb')); w = d['w']; c = d['cst']
print('hedge', w.hedge_min, w.hedge_min_at, 'contact', w.contact_min, w.contact_with, w.collisions[:3], w.chain_trips[:3])
print('op', c['i'], c['plan'][c['i']] if c['i'] < len(c['plan']) else None, c['op'], c['state'])
T = d['trace']; a = int(sys.argv[2]) if len(sys.argv) > 2 else -400; st = int(sys.argv[3]) if len(sys.argv) > 3 else 20
for x in T[a::st]: print(x['t'], x['state'], x['op'], x['s'], x['lat'], round(x['yaw'], 2), x['v'], x['spd'], round(x['w'], 2), x['mode'], x['fix'], x['dLR'])
