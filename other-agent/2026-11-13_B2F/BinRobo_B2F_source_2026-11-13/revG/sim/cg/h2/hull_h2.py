#!/usr/bin/env python3
"""S1 corrected bin hull (H2 campaign). Used by h2/simH2.py and h2/simB2h.py when H2_HULL=new (default); H2_HULL=old keeps
each sim's original gate hull block unchanged (cmp/simH.py l.132 / b2/simB2.py l.170).

What changes against the gate hull (bins_g5 + simH/simB2 block), and nothing else:
  * FRONT wall (opposite handle, hinge, wheels) tapers TF mm from rim to base (drawn), not 170*sc mm.
  * REAR wall: drawn draft TR mm from the rim to the top of the wheel recess, then a vertical wheel-recess wall at XREC
    (relative to the axle, + towards the rear) down to the base. Two convex meshes (MuJoCo collides convex hulls only):
    'binhull' (rim to recess top) and 'binhull_lo' (recess top to base).
  * EN 840 frontal comb receiver on the FRONT wall at the data-sheet comb height (ledge underside = comb + comb_d) and the
    EN 840 width (580 mm 240 L, 480 mm 140 L); same section as the gate lip model (30 x 8 mm ledge, 25 mm down-turned rim).
  * HANDLE side: handle bar on brackets (bar + brackets exactly as cmp/simH.py models them) and a PLAIN rim: 20 mm x 8 mm
    horizontal flange at the height the B1/B2 model put its lip (min(comb, bar - r - 15 mm)), width W - 60 mm, no down-turned
    edge, no receiver ribs (assumption: no data sheet dimensions the rear rim; flagged in the report).
  * Mass, CG and inertia of the bin: the gate two-box model unchanged (bins_g5 + simB2 formulas).
Drawing scales used for TF/TR/XREC (S1 note in docs/reviews/GATE_H2_vs_B2F.md):
  Craemer MGBneo 240 side (1.25 mm/px; 200 mm wheel = 160 px): front 34 mm, rear draft 30 mm, recess wall 97 mm ahead of the
  axle, recess top 96 mm above the axle. SULO Citybac 240 ds p.3 (3.06 mm/px): front 37 mm, rear draft 31 mm.
  Weber 140 side (1.11 mm/px): front 42 mm, rear draft 39 mm, recess wall 68 mm ahead of the axle, top 100 mm above it.
  ESE bins: no side elevation in the project files -> family values (240 L: Craemer/SULO mean; 140 L: Weber)."""
import os, math, numpy as np
FAM={'240':dict(TF=0.035,TR=0.030,XREC=-0.097,ZRT=0.096),'140':dict(TF=0.040,TR=0.038,XREC=-0.068,ZRT=0.100)}
EN840_RW={'WEB140':0.480,'ESE140CL':0.480,'ESE240SL':0.580,'ESE240SL250':0.580,'ESE240CL':0.580,'SULO240':0.580,'CRA240':0.580}
ZB=-0.100          # body base relative to the axle (gate value at the front; base on the ground for 200 mm wheels)
def fam(binkey): return FAM['140' if '140' in binkey else '240']
def HULL(): return os.environ.get('H2_HULL','new')
def geom_params(binkey,p):
    """all hull numbers in the bin frame, UNMIRRORED (rear/handle +x, front -x, z from the axle). Returns dict."""
    F=fam(binkey); bh=p['bar_h']; bx=p['bar_x']; r=p['bar_r']; xb=bx-p['cb']; D=p['D']; W=p['W']; wr=p['wheel_r']
    xf=bx+r-D+0.02                                         # front wall at rim height (gate definition)
    zL_front=p['comb_abs']+p.get('comb_d',0.0)-wr          # receiver ledge underside (data sheet comb height)
    zL_rear=min(p['comb_abs']+p.get('comb_d',0.0),p['bar_habs']-r-0.015)-wr   # plain rim underside (B1/B2 lip height)
    zt=max(bh,zL_front+0.010)
    hw=W/2; hb=hw-0.050
    return dict(bh=bh,bx=bx,r=r,xb=xb,xf=xf,zt=zt,zb=ZB,zrt=F['ZRT'],xrec=F['XREC'],tf=F['TF'],tr=F['TR'],hw=hw,hb=hb,wr=wr,
                zL_front=zL_front,zL_rear=zL_rear,lw=EN840_RW[binkey],W=W,D=D)
def front_x(g,z):  # front wall x at height z (unmirrored)
    return g['xf']+g['tf']*(g['zt']-z)/(g['zt']-g['zb'])
def rear_x(g,z):
    if z>=g['zrt']: return g['xb']-g['tr']*(g['zt']-z)/(g['zt']-g['zrt'])
    return g['xrec']
def half_w(g,z): return g['hw']-(g['hw']-g['hb'])*(g['zt']-z)/(g['zt']-g['zb'])
def meshes(g):
    zt,zrt,zb=g['zt'],g['zrt'],g['zb']
    up=[];lo=[]
    for z in (zt,zrt):
        for x in (front_x(g,z),rear_x(g,z)):
            for s in (-1,1): up.append((x,s*half_w(g,z),z))
    for z in (zrt,zb):
        for x in (front_x(g,z),g['xrec']):
            for s in (-1,1): lo.append((x,s*half_w(g,z),z))
    return up,lo
def old_mesh(p):
    """gate hull vertices (unmirrored), as cmp/simH.py l.132 / b2/simB2.py, for the overlay plot only"""
    bh=p['bar_h']; bx=p['bar_x']; r=p['bar_r']; xbt=bx-p['cb']; D=p['D']; W=p['W']; xfront=bx+r-D+0.02; sc=D/0.74
    hw_=W/2*1000; hb=hw_-50; zt=bh*1000; xb=xbt*1000; xf=xfront*1000; xfb=xf+170*sc; xbb=min(-25.0,xb-110)
    return [(x/1000,y/1000,z/1000) for x,y,z in [(xbb,-hb,-60),(xbb,hb,-60),(xfb,-hb,-100),(xfb,hb,-100),(xb,-hw_,zt),(xb,hw_,zt),(xf,-hw_,zt),(xf,hw_,zt)]]
def bin_xml(binkey,p,dock,mu,fr,crr_bin,mh,box_I,inert,wq='euler="90 0 0"'):
    """bin body XML for the NEW hull. dock='front' -> bin frame mirrored (front wall at +x, as cmp/simH.py) and the front
    receiver is named ledge/rim (the robot's seat switches look for those); the plain handle-side rim is 'hrim'.
    dock='handle' -> unmirrored (handle at +x, as b2/simB2.py); the plain rim is named 'ledge' (what B2's comb meets) and
    the front receiver 'fledge'/'frim'. Returns (asset, body_xml, bin_mass_total, info)."""
    g=geom_params(binkey,p); M=-1.0 if dock=='front' else 1.0
    X=lambda x: M*x
    bh=g['bh']; bx=g['bx']; r=g['r']; xbt=g['xb']; xfront=g['xf']; D=g['D']; W=g['W']; sc=D/0.74; lidm=1.8; fill=p['fill']; wr=g['wr']
    me,ce=p['empty']-1.4-lidm,np.array([xbt-0.32*sc,0,0.42*bh/0.93]); mf,cf=fill,np.array([xbt-0.33*sc,0,0.38*bh/0.93])
    MX=np.array([M,1,1]); ce=ce*MX; cf=cf*MX
    dz_=float(os.environ.get('H2_BINCG_DZ','0'))   # [S7] bin CG raised (both boxes moved up together)
    ce=ce+np.array([0,0,dz_]); cf=cf+np.array([0,0,dz_])
    mb=me+mf; cbg=(me*ce+mf*cf)/mb; Ib=box_I(me,0.6,0.55,1.0)+box_I(mf,0.5,0.45,0.7)
    for mm,cc in ((me,ce),(mf,cf)): d=cc-cbg; Ib+=mm*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    up,lo=meshes(g)
    hv=' '.join(f'{X(x):.5f} {y:.5f} {z:.5f}' for x,y,z in up); hl=' '.join(f'{X(x):.5f} {y:.5f} {z:.5f}' for x,y,z in lo)
    hh=p['handle_half']
    bar=(f'<geom name="bar" type="capsule" fromto="{X(bx):.4f} {-hh:.4f} {bh:.4f} {X(bx):.4f} {hh:.4f} {bh:.4f}" size="{r:.4f}" contype="0" conaffinity="4" friction="{mh}" mass="0"/>' if p['bar_shape']=='tube'
         else f'<geom name="bar" type="box" pos="{X(bx):.4f} 0 {bh:.4f}" size="{r*0.8:.4f} {hh:.4f} {r:.4f}" contype="0" conaffinity="4" friction="{mh}" mass="0"/>')
    wx0=xbt-0.01; wx1=bx+0.01   # handle brackets: as cmp/simH.py (the gate's own model of the handle side)
    webs=''.join(f'<geom name="web{k}" type="box" pos="{X((wx0+wx1)/2):.4f} {sg*(hh+0.01):.4f} {bh-0.012:.4f}" size="{(wx1-wx0)/2:.4f} 0.01 0.035" contype="0" conaffinity="4" mass="0"/>' for k,sg in enumerate((1,-1)))
    for k,(yc,ht) in enumerate(p['knuckles']):
        for j,sg in enumerate((1,-1)):
            webs+=f'<geom name="knk{k}{j}" type="box" pos="{X((wx0+wx1)/2):.4f} {sg*yc:.4f} {bh-0.004:.4f}" size="{(wx1-wx0)/2:.4f} {ht:.4f} {r+0.006:.4f}" contype="0" conaffinity="4" mass="0"/>'
    # front receiver (outward = -x unmirrored)
    zF=g['zL_front']; lw=g['lw']; nF=('ledge','rim') if dock=='front' else ('fledge','frim')
    rec=(f'<geom name="{nF[0]}" type="box" pos="{X(xfront-0.015):.4f} 0 {zF+0.004:.4f}" size="0.015 {lw/2:.4f} 0.004" contype="0" conaffinity="4" friction="{mh}" mass="0" rgba="0.1 0.5 0.2 1"/>'
         f'<geom name="{nF[1]}" type="box" pos="{X(xfront-0.026):.4f} 0 {zF-0.0125:.4f}" size="0.004 {lw/2:.4f} 0.0125" contype="0" conaffinity="4" friction="{mh}" mass="0" rgba="0.1 0.5 0.2 1"/>')
    # plain handle-side rim (outward = +x unmirrored)
    zR=g['zL_rear']; nR='hrim' if dock=='front' else 'ledge'
    prim=f'<geom name="{nR}" type="box" pos="{X(xbt+0.010):.4f} 0 {zR+0.004:.4f}" size="0.010 {W/2-0.030:.4f} 0.004" contype="0" conaffinity="4" friction="{mh}" mass="0" rgba="0.5 0.5 0.1 1"/>'
    lstate,lang=p['lid']; lo_={'closed':0.0,'ajar':lang,'open':lang,'hanging':4.55}[lstate]
    lid_x=xbt+0.005; lid_hl=(lid_x-xfront)/2; lid_hw=W/2
    cb_=crr_bin
    bw=lambda side,s: f'''<body name="bw{side}" pos="0 {s*p['wy']:.4f} 0"><joint name="bax{side}" type="hinge" axis="0 1 0" damping="0.01" frictionloss="{cb_*(fill+12)*9.81*0.45*0.1:.3f}"/>
<inertial mass="0.7" pos="0 0 0" diaginertia="0.002 0.0035 0.002"/><geom name="binwheel{side}" type="cylinder" size="{wr} 0.025" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body>'''
    if dock=='front':
        lid=(f'<body name="lid" pos="{-lid_x:.4f} 0 {bh:.4f}"><joint name="lid" type="hinge" axis="0 -1 0" range="{lo_:.3f} 4.6" damping="0.3"/>'
             f'<inertial mass="{lidm}" pos="{lid_hl:.3f} 0 0.02" diaginertia="0.05 0.09 0.13"/>'
             f'<geom name="lid" type="box" pos="{lid_hl:.4f} 0 0.015" size="{lid_hl:.4f} {lid_hw:.4f} 0.015" contype="0" conaffinity="12" friction="0.4" mass="0"/></body>')
    else:
        lid=(f'<body name="lid" pos="{lid_x:.4f} 0 {bh:.4f}"><joint name="lid" type="hinge" axis="0 1 0" range="{lo_:.3f} 4.6" damping="0.3"/>'
             f'<inertial mass="{lidm}" pos="{-lid_hl:.3f} 0 0.02" diaginertia="0.05 0.09 0.13"/>'
             f'<geom name="lid" type="box" pos="{-lid_hl:.4f} 0 0.015" size="{lid_hl:.4f} {lid_hw:.4f} 0.015" contype="0" conaffinity="12" friction="0.4" mass="0"/></body>')
    body=f'''<body name="bin" pos="0 0 {wr}" euler="0 0 0"><freejoint name="binfree"/>{inert(mb,cbg,Ib)}
<geom name="binhull" type="mesh" mesh="hull" contype="0" conaffinity="3" mass="0" friction="{mu}"/><geom name="binhull_lo" type="mesh" mesh="hull_lo" contype="0" conaffinity="3" mass="0" friction="{mu}"/>{bar}{webs}{rec}{prim}
{bw('L',1)}{bw('R',-1)}
{lid}</body>'''
    asset=f'<asset><mesh name="hull" vertex="{hv}"/><mesh name="hull_lo" vertex="{hl}"/></asset>'
    info=dict(g=g,xlip=(-xfront if dock=='front' else xbt),zL=(zF if dock=='front' else zR),lip_w=(lw if dock=='front' else W-0.06))
    return asset,body,mb+1.4+lidm,info
# ---------------------------------------------------------------- S5 rim keeper (clamp bar over the receiver ledge)
# A 400 mm bar on the comb plate that closes down onto the TOP of the seated receiver ledge after the claim (2 mm clear when
# the lip sits on the teeth), toggle-locked (position servo, +/-1500 N). Open = 60 mm up. Collides with the ledge/rim only
# (contype 4). Modelled the same way for Rev H2 and B2-F.
KB_OPEN=0.060
def keeper_xml(G,cx0=0.0):
    Lt=G['tooth_len']; nh=G['nib_h']
    x=-Lt+0.013-cx0; z=nh+0.010+0.004
    return (f'<body name="kbody" pos="0 0 0"><joint name="kslide" type="slide" axis="0 0 1" range="0 {KB_OPEN}" damping="200" solreflimit="0.004 1"/>'
            f'<inertial mass="0.3" pos="{x:.4f} 0 {z:.4f}" diaginertia="0.004 0.0001 0.004"/>'
            f'<geom name="kbar" type="box" pos="{x:.4f} 0 {z:.4f}" size="0.011 0.20 0.004" contype="4" conaffinity="0" friction="0.3" mass="0" rgba="0.9 0.2 0.9 1"/></body>')
def keeper_act(): return '<position name="kact" joint="kslide" kp="200000" kv="3000" forcerange="-1500 1500"/>'
def _kid(S):
    import mujoco
    return mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_ACTUATOR,'kact')
def keeper_init(S):
    import mujoco
    j=mujoco.mj_name2id(S.m,mujoco.mjtObj.mjOBJ_JOINT,'kslide'); S.d.qpos[S.m.jnt_qposadr[j]]=KB_OPEN; S.d.ctrl[_kid(S)]=KB_OPEN
def keeper_close(S,R):
    S.d.ctrl[_kid(S)]=0.0; R.run_for(1.0)
def keeper_open(S): S.d.ctrl[_kid(S)]=KB_OPEN
# ---------------------------------------------------------------- env hooks for S6 / S7 / S10 (none active by default)
def apply_overrides(S):
    """H2_LIP_SOLREF='t,z' / H2_LIP_SOLIMP='a,b,w' / H2_LIP_MU=m : comb-lip contact (nib, tooth, ledge, rim) [S10]
    H2_TYRE='t,z' : compliant drive tyre, solref on the drive-wheel geoms with priority 1 (wins over the ground) [S6]"""
    import numpy as np
    lip=[S.gid.get(n,-1) for n in ('nib','tooth','ledge','rim')]; lip=[g for g in lip if g>=0]
    if os.environ.get('H2_LIP_SOLREF'):
        v=[float(x) for x in os.environ['H2_LIP_SOLREF'].split(',')]
        for g in lip: S.m.geom_solref[g]=v; S.m.geom_priority[g]=2
    if os.environ.get('H2_LIP_SOLIMP'):
        v=[float(x) for x in os.environ['H2_LIP_SOLIMP'].split(',')]
        for g in lip: S.m.geom_solimp[g][:3]=v; S.m.geom_priority[g]=2
    if os.environ.get('H2_LIP_MU'):
        for g in lip: S.m.geom_friction[g][0]=float(os.environ['H2_LIP_MU'])
    if os.environ.get('H2_TYRE'):
        v=[float(x) for x in os.environ['H2_TYRE'].split(',')]
        for n in ('driveL','driveR'):
            g=S.gid.get(n,-1)
            if g>=0: S.m.geom_solref[g]=v; S.m.geom_priority[g]=1
