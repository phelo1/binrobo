#!/usr/bin/env python3
"""Concept gate, concept A' (evolved tow). Imports the G6 MuJoCo model (revG/sim/g6/sim_g5.py) and patches it IN-PROCESS ONLY
(no G6 file is modified). A' design changes vs G6 (M110 + fixes R7):
  A1 spine contact removed (contype 0); replaced by a SPRUNG load-transfer pad on the rear frame: slide joint along the bin
     back-face normal, roller face (mu 0.1), stroke 25 mm, k 5600 N/m, nominal force set by calibration so the static flat
     tow pose (ESE 240 SL full) keeps castors >= ~80 N; line of action through (or near) the drive axle.
  A2 kingpin centring spring-damper: 859 N m/rad (150 N m at 10 deg) + damping (zeta ~0.7 on the full-bin yaw inertia).
  A3 kingpin = tapered-roller hub (structure only; hand calc), +1.5 kg.
  A4 release: upper wheel-stop roller at 150 mm (G6_SB2=0.15), R7 firmware (ratchet lifted after claim, straighten + pivot,
     tapered pin, pin before descent, stand-up to ground-upright, IMU/float interlock) + float free in stand-up (R8) +
     wheel-on-ground interlock + 'chase' stand-up on slopes (tug creeps toward the bin while standing it up so the wheels
     stay on the stop bar; closed loop on wheel-stop contact force).
Mass file: cg/mass_cgA.json = G6 M110 + A' rows.  Env: CGA_PAD (json overrides), CGA_NOPAD=1, CGA_BUMPW=1 (full-width step)."""
import os, sys, json, math, re, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); G6=os.path.join(HERE,'..','g6'); sys.path.insert(0,G6)
import mujoco, sim_g5
_orig=sim_g5.build_xml
PADF=os.path.join(HERE,'padA.json')
def pad_cfg():
    P=dict(k=5600.0,F_nom=300.0,stroke=0.025,c=300.0,mu=0.1,hx=0.04,hy=0.16,hz=0.006,on=True)
    if os.path.exists(PADF): P.update(json.load(open(PADF)))
    P.update(json.loads(os.environ.get('CGA_PAD','{}')))
    if os.environ.get('CGA_NOPAD')=='1': P['on']=False
    return P
YAW_K=float(os.environ.get('CGA_YAWK',859.0)); YAW_C=float(os.environ.get('CGA_YAWC',280.0))
def build_xml_A(**kw):
    xml,tm,bm=_orig(**kw)
    xml=re.sub(r'(<geom name="spine"[^>]*?)contype="2"',r'\1contype="0"',xml)                       # A1: no rigid spine contact
    xml=re.sub(r'(<joint name="yaw" type="hinge" axis="0 0 1" range="[^"]*") damping="5"',
               r'\1 stiffness="%.1f" damping="%.1f"'%(YAW_K,YAW_C),xml)                              # A2: centring spring-damper
    P=pad_cfg()
    if P['on'] and 'pos' in P:
        px,py,pz=P['pos']; nx,nz=P['n']          # pad centre (free/extended) in the rear-frame, unit normal (x,z) pointing tug->bin
        ang=math.degrees(math.atan2(nx,nz))       # rotate body z-axis onto n about y
        qref=P['F_nom']/P['k']-P['stroke']/2      # spring force at the extended stop = F_nom - k*stroke/2
        pad=(f'<body name="padA" pos="{px:.4f} {py:.4f} {pz:.4f}" euler="0 {ang:.3f} 0">'
             f'<joint name="padA" type="slide" axis="0 0 1" range="{-P["stroke"]:.4f} 0" stiffness="{P["k"]}" springref="{qref:.5f}" damping="{P["c"]}" solreflimit="0.004 1"/>'
             f'<inertial mass="0.6" pos="0 0 0" diaginertia="0.002 0.002 0.002"/>'
             f'<geom name="padAg" type="box" size="{P["hx"]} {P["hy"]} {P["hz"]}" contype="2" conaffinity="0" friction="{P["mu"]}" rgba="0.9 0.6 0.1 1" mass="0"/></body>')
        xml=xml.replace('<body name="mast"',pad+'\n<body name="mast"',1)
    if os.environ.get('CGA_BUMPW')=='1':
        xml=re.sub(r'(<geom name="bump" type="box" pos="[-0-9.e]+ )([-0-9.e]+)( [-0-9.e]+" size="0.15 )0.25',r'\g<1>0\g<3>2.0',xml)
    if os.environ.get('CGA_BUMPYAW'):
        xml=re.sub(r'(<geom name="bump" type="box" pos="[^"]*" size="[^"]*")',r'\1 euler="0 0 %s"'%os.environ['CGA_BUMPYAW'],xml)
    return xml,tm,bm
sim_g5.build_xml=build_xml_A
MASSF=os.path.join(HERE,'mass_cgA.json')
def make_mass():
    M=json.load(open(os.path.join(G6,'mass_g6_M110.json')))
    add=[dict(name="A' sprung load-transfer pad: 2 rollers, slide, 2 die springs, bracket",mod='Rear frame',kg=1.6,cx=500.0,cy=0,cz=330.0,dx=120,dy=320,dz=60),
         dict(name="A' kingpin centring spring-damper (torsion bar + gas damper)",mod='Rear frame',kg=1.5,cx=700.0,cy=0,cz=300.0,dx=200,dy=80,dz=60),
         dict(name="A' kingpin tapered-roller hub (replaces bolt/bush, net)",mod='Rear frame',kg=1.5,cx=670.0,cy=0,cz=280.0,dx=120,dy=120,dz=60),
         dict(name="A' upper wheel-stop roller 150 mm + brackets",mod='Rear frame',kg=1.0,cx=120.0,cy=0,cz=150.0,dx=40,dy=660,dz=40),
         dict(name="A' wheel-on-ground load sensor + pawl sensor",mod='Rear frame',kg=0.2,cx=120.0,cy=0,cz=110.0,dx=40,dy=100,dz=40)]
    M['rows']+=add; M['label']="cgA"; M['total']=round(sum(r['kg'] for r in M['rows']),2)
    json.dump(M,open(MASSF,'w'),indent=0); return M['total']
if not os.path.exists(MASSF): make_mass()
R7ENV=dict(G6_YAWRANGE='40',G6_RATCHET_TIP='1',G6_STANDFIX='1',G6_STANDWORLD='1',G6_STRAIGHTEN='1',G6_PIVOT='1',G6_PINLOCK='1',G6_PINTOL='3.0',
           G6_DNLOCK='1',G6_SB2='0.15',G6_RATCHET_STAND='1',G6_MASSFILE=MASSF)
def set_env():
    for k,v in R7ENV.items(): os.environ.setdefault(k,v)
def pad_state(S):
    """pad compression (m) and normal force on the bin (N)"""
    try: j=S.m.joint('padA')
    except Exception: return 0.0,0.0
    g=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_GEOM,'padAg'); f=np.zeros(6); F=0.0
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if g in (c.geom1,c.geom2): mujoco.mj_contactForce(S.m,S.d,i,f); F+=f[0]
    return -float(S.d.qpos[S.m.jnt_qposadr[j.id]]),F
def binwheel_ground(S):
    """bin-wheel normal force from the GROUND only (wheel-on-ground sensor truth), N"""
    gs=set(mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_GEOM,n) for n in ('ground','bump','floor','gA','gB','gC','gD'))
    bw=(S.gid['binwheelL'],S.gid['binwheelR']); f=np.zeros(6); F=0.0
    for i in range(S.d.ncon):
        c=S.d.contact[i]
        if (c.geom1 in bw and c.geom2 in gs) or (c.geom2 in bw and c.geom1 in gs): mujoco.mj_contactForce(S.m,S.d,i,f); F+=f[0]
    return F
# ---------------------------------------------------------------- A' procedures (tow pose, stand-up/release)
import scen_g5, tow_g5
SBRET=float(os.environ.get('CGA_SBRET','0.06'))
_tip_more=scen_g5.tip_more; _stand_up=scen_g5.stand_up
def _sb_shift(S,dx):
    for n in ('stopbar','stopbar2'):
        gi=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_GEOM,n)
        if gi>=0: S.m.geom_pos[gi][0]+=dx
def tow_pose_A(R):
    """A' tow pose: wheel-stop bar retracts 60 mm (cam), ratchet lifted, float settles on its bottom stop and is clamped there."""
    S=R.s
    if getattr(S,'_cga_tow',False): return
    _sb_shift(S,SBRET); S._cga_tow=True
    S.ratchet_on=False; jf=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); lo=-S.GHV['float_down']; S.m.jnt_range[jf]=[lo,S.GHV['float_up']]
    S.float_pull=200.0; R.run_for(1.5); S.float_pull=0.0; S.m.jnt_range[jf]=[lo,lo+0.0005]
    R.ev("A' tow pose: stop bar retracted %.0f mm, float clamped at bottom stop"%(SBRET*1000))
def tip_more_A(R,target=48.0):
    _tip_more(R,target); tow_pose_A(R)
def stand_up_A(R):
    """A' stand-up: float unclamped + ratchet lifted (free float), stop bar redeployed (1.5 s), then R7 stand-up with 'chase'
    (on a grade the tug creeps toward the bin whenever the wheel-stop force drops below 30 N) and a wheel-on-ground interlock."""
    S=R.s
    if getattr(S,'_cga_tow',False):
        jf=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'float'); S.m.jnt_range[jf]=[-S.GHV['float_down'],S.GHV['float_up']]; S.ratchet_on=False
        R.phase="8a A' stop bar redeploys (cam), float unclamped"; n=30
        for k in range(n): _sb_shift(S,-SBRET/n); R.run_for(0.05)
        S._cga_tow=False; R.run_for(0.5)
    if os.environ.get('CGA_CHASE','1')=='1' and abs(R.grade[0])>0.01:
        prev=R.step; st=dict(on=True)
        def step_chase():
            if st['on'] and R.i%20==0 and R.phase.startswith('9 '):
                C=S.contacts(); f=C.get('stopL',0)+C.get('stopR',0)
                if f<30.0: R.w=-0.04/0.165; R.wd=0.0; R.brake=False
                else: R.hold()
            prev()
        R.step=step_chase
        _stand_up(R); st['on']=False; R.step=prev; R.hold(); R.run_for(0.5)
    else: _stand_up(R)
    if getattr(R,'pin_fail',False): return
    Fg=binwheel_ground(S); Wb=S.bin_mass*9.81
    R.ev("A' wheel-on-ground interlock: bin wheels on ground %.0f N of %.0f N"%(Fg,Wb))
    if Fg<0.35*Wb:
        R.phase="9x A' interlock: wheels not on ground -> creep toward bin 50 mm, mast eases 1 deg, re-check"
        x0=S.d.xpos[S.bid['tug']].copy(); R.set_drive(-0.04); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>0.05,3.0); R.hold()
        R.phi_cmd+=math.radians(1.0); R.run_for(1.0); Fg=binwheel_ground(S)
        if Fg<0.35*Wb: R.pin_fail=True; R.ev("A' interlock HOLD: wheels on ground %.0f N"%Fg)
for mod in (scen_g5,tow_g5): mod.tip_more=tip_more_A
scen_g5.stand_up=stand_up_A
