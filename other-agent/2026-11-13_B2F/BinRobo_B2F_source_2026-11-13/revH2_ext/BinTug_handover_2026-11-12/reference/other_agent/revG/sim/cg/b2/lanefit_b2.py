#!/usr/bin/env python3
"""B2 lane fit: cmp/lanefit.py (unchanged, imported) with three B2 additions, all strict (any footprint point past a truth hedge
face = FAIL, bin gap < 0.05 m = FAIL):
 (1) footprint may carry true castor swivel circles ('circles': [cx, cy, r]) instead of covering rectangles;
 (2) route rule 'kl_gap' (m): keep-left gap from the 3.6 m lane edge to the body side (SITL rule 0.40 m for B1); B2 keeps B1's
     centre line, i.e. kl_gap = 0.40 + (0.485 - half_w);
 (3) pivot strategy 'srun': every empty pivot after a withdraw is made after a run-on of 0.3-3.0 m with a lateral S-shift
     |e| <= 0.6 x run (<= 1.6 m) (swept along a smooth S with the heading following the path), instead of on the axis line only.
(4) corridor guard 'guard' (m): min clearance the lane target keeps to the mapped hedge faces (SITL 0.25; B2 0.40)
usage: lanefit_b2.py <design.json> -> b2/res/lanefit_<name>.json"""
import os, sys, json, math, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','cmp'))
import lanefit as LF
_D0=LF.Design.__init__
def _init(s,D):
    _D0(s,D)
    if D.get('circles'):
        pts=[[cx+r*math.cos(a),cy+r*math.sin(a)] for cx,cy,r in D['circles'] for a in np.linspace(0,2*math.pi,36,endpoint=False)]
        s.outline=np.vstack([s.outline,np.array(pts)]); s.r_empty=float(np.max(np.linalg.norm(s.outline,axis=1)))
        s.r_load=float(max(s.r_empty,np.max(np.linalg.norm(s.binp,axis=1)) if len(s.binp) else 0))
        if D.get('pivot_D_sim'): s.r_load=max(s.r_load,D['pivot_D_sim']/2)
LF.Design.__init__=_init
KL=None
_lt=LF.lane_target
GUARD=0.25
def lane_target(s,sgn,hw):
    """SITL keep-left rule with the keep-left gap KL (B2: B1's centre line kept, KL = 0.40 + (0.485 - hw)) and the corridor guard GUARD
    (min clearance target to the mapped hedge face, SITL 0.25 m; B2 route rule 0.40 m)"""
    hw_eff=hw+((KL-0.40) if KL is not None else 0.0)
    if GUARD==0.25: return _lt(s,sgn,hw_eff)
    kl=sgn*(LF.LANE.width/2-0.40-hw_eff)
    fl=LF.HLN-(0.0 if LF.G6.in_gap(s,1) else LF.G6.hedge_offset(s,1)); fr=LF.HLN-(0.0 if LF.G6.in_gap(s,-1) else LF.G6.hedge_offset(s,-1))
    wff=fl+fr; mid=(fl-fr)/2; a=float(np.clip((3.2-wff)/0.3,0,1)); tgt=(1-a)*kl+a*mid
    return float(np.clip(tgt,-fr+hw+GUARD,fl-hw-GUARD)) if wff>2*hw+2*GUARD else mid
LF.lane_target=lane_target
def s_pivot(d,x,y,yaw,r,obst,runs=np.arange(0.3,3.01,0.1),es=np.arange(-1.6,1.61,0.1)):
    """run on along +x (robot heading yaw) by L with a lateral S-shift e (|e|<=0.5 L), then a 180 deg empty pivot. Swept."""
    best=(-9.0,None); c,s_=math.cos(yaw),math.sin(yaw)
    for L in runs:
        for e in es:
            if abs(e)>0.6*L+1e-9: continue
            px,py=x+L*c-e*s_,y+L*s_+e*c; m=LF.disc_ok(np.array([px,py]),r,obst)
            if m<=best[0]: continue
            mv=9.0
            for t in np.linspace(0,1,max(3,int(L/0.1)+1)):
                lat=e*(1-math.cos(math.pi*t))/2; dlat=e*math.pi*math.sin(math.pi*t)/(2*L); h=yaw+math.atan(dlat)
                P=d.fp(x+t*L*c-lat*s_,y+t*L*s_+lat*c,h,False)
                for p in P[::2]: mv=min(mv,LF.region_margin(p)[0])
                for (bx,by,byaw) in obst: mv=min(mv,float(np.min(LF.pt_box_dist(P,bx,by,byaw)))-LF.BINGAP)
                if mv<=best[0]: break
            m=min(m,mv)
            if m>best[0]: best=(round(m,3),(round(float(L),2),round(float(e),2)))
    return best
SRUN=False
_lp=LF.line_pivot
def line_pivot(d,x,y,yaw,r,dlist,loaded,obst,skip_last=False):
    if not SRUN or loaded: return _lp(d,x,y,yaw,r,dlist,loaded,obst,skip_last)
    sg=1.0 if (dlist and dlist[-1]>=0) else -1.0
    return s_pivot(d,x,y,yaw if sg>0 else yaw+math.pi,r,obst)
LF.line_pivot=line_pivot
if __name__=='__main__':
    D=json.load(open(sys.argv[1])); KL=D.get('kl_gap'); SRUN=D.get('pivot_strategy')=='srun'; GUARD=D.get('guard',0.25)
    d=LF.Design(D); R=dict(design=d.name,r_empty=round(d.r_empty,3),r_load=round(d.r_load,3),pivot_D_empty=round(2*d.r_empty,2),pivot_D_load=round(2*d.r_load,2),half_w=d.half_w,kl_gap=KL,guard=GUARD,pivot_strategy=D.get('pivot_strategy'))
    R['sweep']={('%s %s'%('down' if sg>0 else 'up','loaded' if ld else 'empty')):LF.lane_sweep(d,ld,sg) for sg in (1,-1) for ld in (True,False)}
    mins=[v['min_clear_m'] for v in R['sweep'].values()]; R['sweep_min']=min(mins); R['sweep_PASS_strict']=R['sweep_min']>0; R['sweep_margin_vs_p95']=round(R['sweep_min']-LF.EST_P95,3)
    R['lane_pivot']=LF.lane_pivot_profile(d.r_empty); R['lane_pivot_loaded']=LF.lane_pivot_profile(d.r_load)
    R['lane_pivot_frac_empty']=round(np.mean([m>0 for _,m in R['lane_pivot']]),3); R['lane_pivot_frac_loaded']=round(np.mean([m>0 for _,m in R['lane_pivot_loaded']]),3)
    nar=[m for s_,m in R['lane_pivot_loaded'] if 500<=s_<=516]; R['narrowing_pivot_margin_loaded']=min(nar) if nar else None
    R['yard_dock']=LF.yard_dock(d); R['mouth']=LF.mouth(d)
    R['sequences']={'%s n%d handle-to-%s'%(ms,n,ht):LF.sequence(d,n,ht,ms) for ms in ('drop','pickup') for n in (1,2,3) for ht in ('lane','road')}
    allm=[st[1] for v in R['sequences'].values() for st in v['steps'] if st[1] is not None]; R['sequence_min_margin']=min(allm); R['sequences_all_ok']=all(v['ok'] for v in R['sequences'].values())
    json.dump(R,open(os.path.join(H,'res','lanefit_%s.json'%d.name),'w'),indent=1,default=float)
    print(d.name,'pivot D',R['pivot_D_empty'],R['pivot_D_load'],'sweep min',R['sweep_min'],{k:(v['min_clear_m'],v['at_s']) for k,v in R['sweep'].items()},'seq min',R['sequence_min_margin'],'all ok',R['sequences_all_ok'])
