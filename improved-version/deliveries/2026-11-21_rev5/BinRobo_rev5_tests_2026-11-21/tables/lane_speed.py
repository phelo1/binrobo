import numpy as np,glob,json,sys
RULE=[(-1,0.4,0.4),(0.005,0.4,0.3),(0.03,0.3,0.3),(0.06,0.3,0.2),(0.09,0.2,0.2)]
def load(d,r):
    out={}
    for f in sorted(glob.glob('%s/%s/rec_*.npz'%(d,r))):
        z=np.load(f,allow_pickle=True)
        for k in ('t','hud','ph'): out.setdefault(k,[]).append(z[k])
    return {k:np.concatenate(v) for k,v in out.items()}
def lim(g,carry):
    v=9
    for thr,vb,ve in RULE:
        if g>=thr: v=min(v, vb if carry else ve)
    return v
res={}
for d,r in [('runs_r5_pf','P1'),('runs_r5_pf','P3'),('runs_r5_pf','P7'),('runs_r5_pf','P2c'),('runs_r5_pf','P2a_pf'),('runs_r5_pf','P5a_drop_sharp_3kN'),('runs_r5_pf','P5h_pothole')]:
    z=load(d,r); h=z['hud']; s=h[:,0]; g=h[:,2]/100.0; v=h[:,3]; carry=h[:,13]>0.5; kg=h[:,12]
    ds=np.gradient(s); dirn=np.sign(ds); dirn[dirn==0]=1
    gd=-g*dirn                      # downhill grade in the direction of travel
    loaded=carry&(kg>=40)
    L=np.array([lim(gd[i],loaded[i]) for i in range(len(s))])
    mv=np.abs(v)>0.05
    ex=np.where(mv, np.abs(v)-L, -9)
    i=int(np.argmax(ex)); j=int(np.argmax(np.abs(v)))
    # brow: speed when the local downhill grade first exceeds 9 % 
    k=np.where((gd>=0.09)&mv)[0]
    brow=None
    if len(k): brow=dict(s=float(s[k[0]]), v=float(abs(v[k[0]])), vmax_on_pitch=float(np.abs(v[k]).max()))
    k6=np.where((gd>=0.06)&(gd<0.09)&mv)[0]
    res[r]=dict(v_max=float(abs(v[j])), v_max_s=float(s[j]), v_max_grade_pct=float(100*gd[j]), worst_over_rule=float(ex[i]), at_s=float(s[i]), at_grade_pct=float(100*gd[i]), at_v=float(abs(v[i])), loaded=bool(loaded[i]), brow=brow, vmax_6to9=float(np.abs(v[k6]).max()) if len(k6) else None, hedge_min=float(h[mv,6].min()))
    print(r, json.dumps(res[r]))
json.dump(res, open('/home/claude/s0/r5/pack_tables/lane_speed_r5.json','w'), indent=1)
