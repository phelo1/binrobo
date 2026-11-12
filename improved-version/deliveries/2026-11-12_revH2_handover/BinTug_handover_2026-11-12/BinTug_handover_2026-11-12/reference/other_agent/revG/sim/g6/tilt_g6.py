#!/usr/bin/env python3
"""G6 task 5: full grab -> tip to 48 deg -> hold -> stand -> release cycle with a REAL actuator model: new clevis pin position
(rear-frame RF-13 pin = ACT_BASE), the actuator's rated push force as the force cap, and its load-dependent speed
(linear speed-vs-load line from the data sheet) limiting the mast rate. Grabber GH-B6 (H3). Nominal data-sheet bin, flat, mu 0.6.
usage: PYTHONPATH=/workspace/work/pylib python3 tilt_g6.py <BIN> <act_id> -> ../results_G6_tilt_<BIN>_<act_id>.json"""
import json, math, os, sys, time
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import sim_g5, scen_g5
from sim_g5 import Sim, TXm
from scen_g5 import Runner, grab_GH, tip_more, release_GH
from tow_g5 import nominal, CAD
from bins_g5 import BINS
ACTS={  # base pin (mm), rated push N, speed (mm/s) at 0 load and at Fv, current (A) at 0 and at Fv
 'XTL450_G5': dict(base=(600.0,340.0),F=2500.0,v0=None,Fv=None,i0=None,i1=None,desc='G5 model: 2,500 N cap, mast rate fixed 1.5 deg/s (no speed model)'),
 'LA34L12':   dict(base=(558.0,340.0),F=10000.0,v0=8.2,v1=4.8,Fv=10000.0,i0=1.5,i1=7.0,desc='LINAK LA34 L 400 mm, 12 mm pitch std motor (surplus hoist), pin moved to x=558'),
 'LA34L20F':  dict(base=(558.0,340.0),F=5000.0,v0=18.0,v1=13.2,Fv=5000.0,i0=2.0,i1=10.0,desc='LINAK LA34 L 400 mm, 20 mm pitch fast motor, pin x=558'),
 'LA36_16H':  dict(base=(580.0,340.0),F=5600.0,v0=22.0,v1=17.0,Fv=5600.0,i0=2.5,i1=10.2,desc='LINAK LA36 24 V 16 mm pitch H-gear, 398 mm stroke, pin x=580 (speed/current read off the data-sheet curves)'),
 'LA36_12H':  dict(base=(580.0,340.0),F=6800.0,v0=17.0,v1=13.0,Fv=6800.0,i0=2.4,i1=10.3,desc='LINAK LA36 24 V 12 mm pitch H-gear 1:46, 400 mm stroke (BID 650), pin x=580; data-sheet 24 V unregulated table: 17 mm/s no load, 13 mm/s at 6,800 N, 10.3 A'),
 'LA36_12H_cold': dict(base=(580.0,340.0),F=3400.0,v0=12.75,v1=9.75,Fv=3400.0,i0=2.4,i1=10.3,desc='LA36 12H at -30 C: data-sheet 50 % load (3,400 N); speed x0.75 is an ASSUMPTION (cold grease), not a data-sheet value'),
}
def dLdphi(phi_rad):
    a,L1=sim_g5.act_lever(phi_rad+math.radians(0.5)); b,L0=sim_g5.act_lever(phi_rad-math.radians(0.5)); return abs(L1-L0)*1000.0   # mm per deg
def run(binkey,aid):
    A=ACTS[aid]; sim_g5.ACT_BASE=A['base']
    C=json.load(open(os.path.join(HERE,'combos_g6.json')))[os.environ.get('G6_COMBO','H3')]; ghp=dict(C)
    kw=nominal(binkey); B=BINS[binkey]
    for k_,n_ in (('_claim_and','claim_and'),('_guard','square_guard'),('_reapp','reapp')):
        if k_ in ghp: kw[n_]=ghp.pop(k_)
    S=Sim(grabber='GH',gh='B2',ghp=ghp,fill=B['fill_full'],mu=0.6,massfile=os.path.join(CAD,'mass_g3_sim_L95.json'),ballast=99,act_force=A['F'],
          tug_pose=(TXm+0.60+(kw['wheel_r']-0.10),0.0,0.0),**kw)
    R=Runner(S,rec_hz=2); R.recording=False
    st=dict(E_J=0.0,mech_J=0.0,phase_t={},Lmin=1e9,Lmax=0)
    orig=Runner.ramp_phi
    def ramp(self,target_deg,rate_deg=1.5,cond=None,Tmax=90,check_every=20):
        if A['v0'] is None: return orig(self,target_deg,rate_deg,cond,Tmax,check_every)
        tgt=math.radians(target_deg)
        for k in range(int(Tmax/self.dt)):
            if cond and k%check_every==0 and cond(): return True
            dlt=tgt-self.phi_cmd
            if abs(dlt)<1e-6 and abs(self.s.d.qpos[self.s.jq('tilt')]-tgt)<math.radians(0.3): return True
            F=min(self.act_f,A['Fv']); v=A['v0']-(A['v0']-A['v1'])*F/A['Fv']          # actuator speed at the present load (mm/s)
            r=min(math.radians(rate_deg), math.radians(v/max(dLdphi(self.s.d.qpos[self.s.jq('tilt')]),0.5)))*self.dt
            self.phi_cmd+=max(-r,min(r,dlt)); self.step()
        return False
    Runner.ramp_phi=ramp
    prev=R.step; last=[None,R.t]
    def step():
        L0=sim_g5.act_lever(S.d.qpos[S.jq('tilt')])[1]; prev(); L1=sim_g5.act_lever(S.d.qpos[S.jq('tilt')])[1]
        dL=abs(L1-L0)*1000; st['mech_J']+=R.act_f*dL/1000
        st['Lmin']=min(st['Lmin'],L1*1000); st['Lmax']=max(st['Lmax'],L1*1000)
        if A['i0'] is not None and dL>1e-6:
            I=A['i0']+(A['i1']-A['i0'])*min(R.act_f,A['Fv'])/A['Fv']; st['E_J']+=24*I*R.dt
        if R.phase!=last[0]:
            if last[0] is not None: st['phase_t'][last[0][:40]]=round(st['phase_t'].get(last[0][:40],0)+R.t-last[1],1)
            last[0]=R.phase; last[1]=R.t
    R.step=step
    out=dict(bin=binkey,act=aid,desc=A['desc'],base=A['base'],F_cap=A['F'])
    t0=R.t; g=grab_GH(R,tip_to=25.0); out['grab']={k:g.get(k) for k in ('result','claim','captured','float_mm')}; t_grab=R.t-t0
    if g.get('result')!='success': out['ok']=False; Runner.ramp_phi=orig; return out
    t1=R.t; tip_more(R,48.0); t_tip=R.t-t1
    out['tilt_reached']=round(S.bin_tilt_rel(),1); out['mast_deg']=round(S.tilt(),1)
    R.phase='8 hold at tow pose'; R.run_for(2.0)
    out['held']=bool(S.captured())
    t2=R.t; o=release_GH(R); t_rel=R.t-t2
    out['release']=o; out['events']=R.events[-12:]; out['combo']=os.environ.get('G6_COMBO','H3'); Runner.ramp_phi=orig
    out.update(peak_act_N=round(R.peak_act),peak_act_at=R.peak_act_at,peak_act_filt_N=round(R.peak_act_f),time_grab_s=round(t_grab,1),time_tip_s=round(t_tip,1),
               time_release_s=round(t_rel,1),mech_energy_J=round(st['mech_J']),elec_energy_Wh=round(st['E_J']/3600,2) if A['i0'] else None,
               pin_pin_mm=[round(st['Lmin'],1),round(st['Lmax'],1)],phase_t=st['phase_t'])
    out['ok']=bool(out['held'] and o.get('released'))
    return out
if __name__=='__main__':
    b,a=sys.argv[1],sys.argv[2]; t=time.time(); o=run(b,a); o['cpu_s']=round(time.time()-t)
    json.dump(o,open(os.path.join(HERE,'..','results_G6_tilt_%s_%s%s.json'%(b,a,('_'+os.environ['G6_COMBO']) if os.environ.get('G6_COMBO') else '')),'w'),indent=1,default=str)
    print(json.dumps({k:v for k,v in o.items() if k!='phase_t'},default=str),flush=True)
