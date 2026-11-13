import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mc_g5 import make_sim
from scen_g5 import Runner, approach
j=json.load(open('../results_G6_mc_CRA240_B2_H3.json')); p0=j['runs'][19]['params']; h3=dict(j['ghp'])
k3={k:h3[k] for k in ('hy','lip_chamfer','ease','_reapp','_guard','_claim_and')}
which=sys.argv[1]; G=h3 if which=='H3' else k3
for dy in [float(x) for x in sys.argv[2].split(',')]:
    p=dict(p0); p['dy']=dy
    S=make_sim(p,'B2',dict(G)); R=Runner(S,rec_hz=2); R.recording=False
    ok=approach(R,0.10); print(which,dy,'docked',ok,round(R.t,1),flush=True)
