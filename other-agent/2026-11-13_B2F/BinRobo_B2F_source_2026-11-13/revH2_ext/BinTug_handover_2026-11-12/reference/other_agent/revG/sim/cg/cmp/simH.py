#!/usr/bin/env python3
"""REV H MuJoCo model for the B1-vs-Rev H comparison, generated from it1/simB_it1.py by cmp/make_simH.py (simB_it1.py untouched).
Geometry and masses from revH_ext/revH/sim/params.py (ROBOT, MASS_ITEMS); common physics terms, drive/brake model, bins and the
B1 grab/set-down firmware sequence (F1, F2, F6, F9, SD2, F5) reused unchanged. Rev H specifics: open U (legs, funnel), drive track
0.97 m, 318 mm drive wheels, 260 mm nose casters, tail anti-tip wheels 75 mm up, mast at x 0.45, 600 mm comb on a 300 mm-stroke
carriage, FIXED lower rest pad 0.45 m below the comb, NO handle-bar keeper, bin carried by its FRONT-wall lip (face opposite the
handle) exactly as params.py/make_iso.py define it. The front lip is modelled with the same section as the gate comb-lip model
(30 x 8 mm ledge, 25 mm rim) at the data-sheet comb height and EN 840 receiver width: this is Rev H's premise, not a real feature.
Env REVH_FIX: comma list of firmware fixes (see grab/set_down).
ITER1 copy of simB_cg.py (frozen file untouched). Changes are tagged [D#] design / [F#] firmware; see ITER1_conceptB.md.
Concept gate, concept B: rigid straddle CARRIER. The tug straddles the bin (drive wheels beside the bin, axle under the full
bin's CG), lifts it ~75 mm by its EN 840 comb lip (inverted-L lip below the handle bar) with a vertical lifter, a sprung lower
back pad reacts the hanging moment, a small keeper presses on the handle bar. No kingpin, no hitch, no tilting mast.
Same physics terms as the G6 model (sim_g5): contact solref/solimp, cone, noslip, dt, bin model (hull, two-box inertia, lid,
wheels with crr frictionloss), 330 mm drive wheels (velocity servo kv 150, cap 60 N m), 200 mm castors, drive/brake model.
Tug frame: origin on the ground under the drive-axle centre, +x toward the castors (front), bin straddled at x ~ 0.
ASSUMPTION (to verify on Brian's bins, F-3): comb lip = horizontal ledge 30 mm deep x 8 mm with a 25 mm down-turned rim,
width = 2*handle_half - 20 mm, ledge underside at min(data-sheet comb height, bar bottom - 15 mm)."""
import os, sys, json, math, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); G6=os.path.join(HERE,'..','..','g6'); sys.path.insert(0,G6)
import mujoco
from sim_g5 import box_I, composite, inert
from bins_g5 import BINS
DT=float(os.environ.get('SIM_DT','0.0005'))
GEO=dict(track=0.485, rw=0.159, ww=0.035, cx=0.79, cy=0.30, cr=0.13, guard_y=0.33, guard_x0=-0.23, guard_x1=0.42, tail_x=-0.40, tail_y=0.405, tail_r=0.05, tail_gap=0.075, leg_tip=-0.43, mouth=0.78,
         face_x=0.425, tooth_len=0.051, nib_l=0.012, nib_h=0.020, tooth_hw=0.12, approach_nib_z=0.865, lift_range=0.26,
         pad_x=0.235, pad_z=0.45, pad_k=300000.0, pad_pre=0.0, pad_stroke=0.003, lift_extra=0.075, act_N=3000.0,
         tcap=60.0, kvs=1.0, car_zero=0.840, pad_in=0.0, pad_dz=0.45, pad_ret=0.0, rim_off=0.025, creep_v=0.03, creep_gap=0.06, lift_extra1=0.10,
         nib_l1=0.008, tooth_hw1=0.30, keep_l=0.080, yaw_sigma=1.0, yaw_ok=1.5)
# [D7] keeper arm 68 -> 80 mm (reach the bar on small-cb bins with the pad extended); [D6] nib 12 -> 8 mm long, tooth 240 -> 160 mm wide (more room in the 22 mm lip channel at a docking yaw); [F6] dual-ToF yaw alignment in the creep, rim-catch and tilt abort in the lift
# [D1] sprung pad on the LIFT CARRIAGE, pad face pad_in inboard of the nib front - tof, pad_dz below the nib top; [D2] optional pad retract (pad_ret m, 0 = fixed pad)
# [D3] lift stroke 250 mm, carriage zero at nib top car_zero; [F1] approach height = measured lip-rim bottom - rim_off; [F2] contact-sensing creep; [F3] lift_extra1
PADCAR=True     # B2 (post-gate design change): sprung pad on the LIFT CARRIAGE, unloads when the comb lowers
GEO.update(json.loads(os.environ.get('CGB_GEO','{}'))); GEO['lift_range']=0.30
FIX=set(x for x in os.environ.get('REVH_FIX','').split(',') if x)
CORNERS=[(0.88,0.40),(0.88,-0.40),(0.0,0.52),(0.0,-0.52),(-0.43,0.52),(-0.43,-0.52)]   # params/mission.turning(): nose tip 0.88 (half 0.40), drive wheels and leg tips half 1.04/2
EN840_RW={'WEB140':0.480,'ESE140CL':0.480,'ESE240SL':0.580,'ESE240SL250':0.580,'ESE240CL':0.580,'SULO240':0.580,'CRA240':0.580}
def xlip(P): return P['xlip']
GEO['nib_l']=GEO['nib_l1']; GEO['tooth_hw']=GEO['tooth_hw1']
RW=GEO['rw']   # drive wheel radius used by the speed controllers (0.165 m unless a sensitivity run changes rw)
MASSF=os.environ.get('CGB_MASSF',os.path.join(HERE,'mass_revH.json'))
def make_mass():
    # revH_ext/revH/sim/params.py MASS_ITEMS (kg, x, z) unchanged; y from params.ROBOT (paired items split L/R). Total 85.5 kg.
    sys.path.insert(0,os.path.join(HERE,'..','..','..','..','revH_ext','revH','sim')); import params as PH
    R=PH.ROBOT; rows=[]
    for n,k,x,z in PH.MASS_ITEMS:
        if n.startswith('Carriage'): continue
        if n.startswith('Donor drive'):
            for s in (1,-1): rows.append(dict(name=n+(' L' if s>0 else ' R'),kg=k/2,p=[x,s*R['drive_track']/2,z],d=[0.3,0.12,0.3],g='wheel'))
        elif n.startswith('Nose casters'):
            for s in (1,-1): rows.append(dict(name=n+(' L' if s>0 else ' R'),kg=k/2,p=[x,s*R['nose_track']/2,z],d=[0.2,0.08,0.2],g='cast'))
        elif n.startswith('Side rails'):
            for s in (1,-1): rows.append(dict(name=n+(' L' if s>0 else ' R'),kg=k/2,p=[x,s*(R['leg_inner_gap']/2+0.025),z],d=[1.31,0.05,0.05],g='chassis'))
        elif n.startswith('Batteries'):
            for s in (1,-1): rows.append(dict(name=n+(' L' if s>0 else ' R'),kg=k/2,p=[x,s*0.42,z],d=[0.18,0.08,0.17],g='chassis'))
        elif n.startswith('Mast uprights'):
            for s in (1,-1): rows.append(dict(name=n+(' L' if s>0 else ' R'),kg=k/2,p=[x,s*R['mast_half_span'],z],d=[0.05,0.05,1.05],g='chassis'))
        else: rows.append(dict(name=n,kg=k,p=[x,0.0,z],d=[0.2,0.4,0.2],g='chassis'))
    car=[dict(name='Carriage, comb blade, pads (params)',kg=4.5,p=[0.40,0,0.90],d=[0.1,0.6,0.5],g='lift')]
    json.dump(dict(label='revH',total=round(sum(r['kg'] for r in rows+car),2),rows=rows,carriage=car),open(MASSF,'w'),indent=1)
if not os.path.exists(MASSF): make_mass()
def bin_params(binkey,p=None):
    """nominal (or sampled p from mc_g5.sample) bin parameters + comb lip"""
    B=BINS[binkey]
    if p is None:
        sh,r,_=B['sections'][1] if len(B['sections'])>1 else B['sections'][0]
        kn=B['knuckles'] if B['knuckles']!='maybe' else [(0.045,0.005)]
        p=dict(bar_r=r,bar_shape=sh,bar_x=B['bar_x'][0],cb=B['cb'][0],bar_habs=B['bar_abs'][0],wheel_r=B['wheel']/2,handle_half=B['web'][0],knuckles=kn,
               wy=(B['track']-0.05)/2,W=B['W'],D=B['D'],empty=B['empty'],fill=0.0,lid=['closed',0.0],dy=0.0,dyaw=0.0,mu=0.6,mu_hook=0.35,comb_d=0.0)
    p=dict(p); p['bar_h']=p['bar_habs']-p['wheel_r']
    comb=B['comb'] if B['comb'] else p['bar_habs']-0.02
    p['zL_abs']=min(comb+p.get('comb_d',0.0),p['bar_habs']-p['bar_r']-0.015)      # ledge underside above ground (bin standing)
    p['lip_w']=EN840_RW[binkey]                      # Rev H premise: full EN 840 receiver width on the front wall
    p['xlip']=-(p['bar_x']+p['bar_r']-p['D']+0.02)    # front wall at rim height, bin frame mirrored (front -> +x)
    return p
def build_xml(binkey, p, terrain='flat', bump=None, mu=0.6, crr=0.06, crr_bin=None, tug_pose=(0,0,0), with_bin=True):
    G=GEO; M=json.load(open(MASSF)); rows=M['rows']
    ch=composite([r for r in rows if r['g']=='chassis'],np.zeros(3))
    wm=sum(r['kg'] for r in rows if r['g']=='wheel')/2; cm=sum(r['kg'] for r in rows if r['g']=='cast')/2
    car=M['carriage'][0]; z0=G['car_zero']-G['nib_h']
    ca=composite([dict(kg=car['kg'],p=[car['p'][0]-G['face_x'],0,0.0],d=car['d'])],np.zeros(3))
    fr=f'{mu} 0.005 0.0001'; wq='euler="90 0 0"'
    if terrain=='flat': ground=f'<geom name="ground" type="plane" size="80 80 0.1" friction="{fr}" condim="3"/>'
    else:
        bx,bh,by,bw=bump[:4]
        ground=f'<geom name="ground" type="plane" size="80 80 0.1" friction="{fr}" condim="3"/><geom name="bump" type="box" pos="{bx} {by} {bh/2}" size="0.15 {bw} {bh/2}" friction="{fr}" condim="3"/>'
        if len(bump)>4:   # [lane prep] kerb ramp of length Lr in front of the step (top surface from the ground to the step top)
            Lr=bump[4]; th=math.atan(bh/Lr); xm=bx-0.15-Lr/2
            ground+=f'<geom name="ramp" type="box" pos="{xm+0.02*math.sin(th):.4f} {by} {bh/2-0.02*math.cos(th):.4f}" size="{Lr/2/math.cos(th)+0.005:.4f} {bw} 0.02" euler="0 {-math.degrees(th):.3f} 0" friction="{fr}" condim="3"/>'
    def drive(side,s):
        return f'''<body name="wheel{side}" pos="0 {s*G['track']} {G['rw']}"><joint name="axle{side}" type="hinge" axis="0 1 0" damping="0.05" frictionloss="{crr*300*0.165:.3f}"/>
<inertial mass="{wm:.3f}" pos="0 0 0" diaginertia="{max(0.035*wm/3.65,0.3*wm*G['rw']**2+0.001):.4f} {0.6*wm*G['rw']**2:.4f} {max(0.035*wm/3.65,0.3*wm*G['rw']**2+0.001):.4f}"/>
<geom name="drive{side}" type="cylinder" size="{G['rw']} {G['ww']}" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body>'''
    def caster(side,s):
        return f'''<body name="cfork{side}" pos="{G['cx']} {s*G['cy']} {G['cr']}"><joint name="swivel{side}" type="hinge" axis="0 0 1" damping="0.05"/>
<inertial mass="1.0" pos="-0.02 0 0.08" diaginertia="0.004 0.004 0.002"/>
<body name="cwheel{side}" pos="-0.05 0 0"><joint name="cax{side}" type="hinge" axis="0 1 0" damping="0.005" frictionloss="{crr*200*G['cr']:.3f}"/>
<inertial mass="{max(cm-1.0,0.2):.3f}" pos="0 0 0" diaginertia="{0.35*max(cm-1.0,0.2)*G['cr']**2+0.002:.4f} {0.6*max(cm-1.0,0.2)*G['cr']**2:.4f} {0.35*max(cm-1.0,0.2)*G['cr']**2+0.002:.4f}"/>
<geom name="caster{side}" type="cylinder" size="{G['cr']} 0.03" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body></body>'''
    gx0,gx1=G['guard_x0'],G['guard_x1']; gy=G['guard_y']
    lt=G['leg_tip']; mh_=G['mouth']/2; fl=math.hypot(gx0-lt,mh_-gy); fa=math.degrees(math.atan2(mh_-gy,gx0-lt))
    guards=''.join(f'''<geom name="guard{k}" type="box" pos="{(gx0+gx1)/2:.3f} {sg*(gy+0.025):.3f} 0.285" size="{(gx1-gx0)/2:.3f} 0.025 0.025" friction="0.25" contype="1" conaffinity="0" mass="0" rgba="0.6 0.75 0.95 1"/>
<geom name="flare{k}" type="box" pos="{(gx0+lt)/2:.3f} {sg*((gy+mh_)/2+0.025):.3f} 0.285" size="{fl/2:.3f} 0.025 0.025" euler="0 0 {sg*fa:.2f}" friction="0.25" contype="1" conaffinity="0" mass="0"/>
<geom name="antitip{k}" type="sphere" pos="{G['tail_x']:.3f} {sg*G['tail_y']:.3f} {G['tail_r']+G['tail_gap']:.3f}" size="{G['tail_r']}" friction="0.6" contype="0" conaffinity="1" mass="0"/>''' for k,sg in enumerate((1,-1)))
    body=f'''<geom name="tray" type="box" pos="0.72 0 0.285" size="0.025 0.355 0.025" contype="0" conaffinity="1" mass="0"/>
<geom name="bumper" type="box" pos="0.865 0 0.25" size="0.015 0.40 0.04" contype="0" conaffinity="1" mass="0"/>
<geom name="rearface" type="box" pos="0.45 0 0.80" size="0.025 0.245 0.50" contype="2" conaffinity="0" mass="0" rgba="0.4 0.4 0.45 0.4"/>'''
    # lifter carriage: origin = tooth-plate top at the face plate (x face_x)
    Lt=G['tooth_len']; nl=G['nib_l']; nh=G['nib_h']; hw=G['tooth_hw']
    qref=-G['pad_pre']/G['pad_k']
    # pad on the carriage: face x (tug frame) = nib front (face_x-tooth_len) - tof_nom(0.004) - pad_in ; z = nib top - pad_dz (centre)
    nibfront=G['face_x']-G['tooth_len']; pfx=nibfront-0.004-G['pad_in']-G['face_x']; pz=G['nib_h']-G['pad_dz']
    padb=f'''<body name="padbase" pos="{pfx:.4f} 0 {pz:.4f}"><joint name="padext" type="slide" axis="1 0 0" range="0 {max(G['pad_ret'],0.0005)}" damping="2000" solreflimit="0.004 1"/>
<inertial mass="0.3" pos="0.02 0 0" diaginertia="0.001 0.001 0.001"/>
<body name="pad" pos="0 0 0"><joint name="pad" type="slide" axis="1 0 0" range="0 {G['pad_stroke']}" stiffness="{G['pad_k']}" springref="{qref:.5f}" damping="300" solreflimit="0.004 1"/>
<inertial mass="0.4" pos="0.01 0 0" diaginertia="0.001 0.001 0.001"/><geom name="padg" type="box" pos="0.01 0 0" size="0.01 0.15 0.05" contype="2" conaffinity="0" friction="0.3" mass="0" rgba="0.1 0.1 0.1 1"/></body></body>'''
    lift=f'''<body name="lift" pos="{G['face_x']} 0 {z0:.4f}"><joint name="lift" type="slide" axis="0 0 1" range="0 {G['lift_range']}" damping="200" solreflimit="0.01 1"/>{inert(*ca)}
<geom name="faceplate" type="box" pos="0.005 0 0.05" size="0.005 0.20 0.10" contype="6" conaffinity="0" friction="0.3" mass="0" rgba="0.3 0.3 0.35 1"/>
<geom name="tooth" type="box" pos="{-(Lt-nl)/2:.4f} 0 -0.005" size="{(Lt-nl)/2:.4f} {hw} 0.005" contype="6" conaffinity="0" friction="{p.get('mu_hook',0.35)}" mass="0" rgba="0.2 0.2 0.25 1"/>
<geom name="nib" type="box" pos="{-Lt+nl/2:.4f} 0 {nh/2-0.005:.4f}" size="{nl/2:.4f} {hw} {nh/2+0.005:.4f}" contype="6" conaffinity="0" friction="{p.get('mu_hook',0.35)}" mass="0" rgba="1 0.45 0.1 1"/>
<body name="keeper" pos="0 0 0.10"><joint name="keeper" type="hinge" axis="0 1 0" range="-70 83" damping="0.5"/>
<inertial mass="0.2" pos="-0.035 0 0" diaginertia="0.0003 0.0003 0.0001"/><geom name="keeparm" type="box" pos="{-G['keep_l']/2+0.004:.4f} 0 0.02" size="{G['keep_l']/2-0.004:.4f} 0.12 0.004" contype="0" conaffinity="0" mass="0"/>
<geom name="keeptip" type="cylinder" pos="{-G['keep_l']:.4f} 0.10 0" size="0.012 0.025" euler="90 0 0" contype="0" conaffinity="0" friction="0.2" mass="0" rgba="0.9 0.9 0.2 1"/>
<geom name="keeptip2" type="cylinder" pos="{-G['keep_l']:.4f} -0.10 0" size="0.012 0.025" euler="90 0 0" contype="0" conaffinity="0" friction="0.2" mass="0" rgba="0.9 0.9 0.2 1"/></body>{padb if PADCAR else ''}</body>'''
    binb=''; bm=0.0
    if with_bin:
        bh=p['bar_h']; bx=p['bar_x']; r=p['bar_r']; xbt=bx-p['cb']; D=p['D']; W=p['W']; xfront=bx+r-D+0.02; sc=D/0.74; lidm=1.8; fill=p['fill']
        me,ce=p['empty']-1.4-lidm,np.array([xbt-0.32*sc,0,0.42*bh/0.93]); mf,cf=fill,np.array([xbt-0.33*sc,0,0.38*bh/0.93])
        MX=np.array([-1.0,1,1]); ce=ce*MX; cf=cf*MX          # mirror x: front wall -> +x
        mb=me+mf; cbg=(me*ce+mf*cf)/mb; Ib=box_I(me,0.6,0.55,1.0)+box_I(mf,0.5,0.45,0.7)
        for mm,cc in ((me,ce),(mf,cf)): d=cc-cbg; Ib+=mm*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
        hw_=W/2*1000; hb=hw_-50; zt=bh*1000; xb=xbt*1000; xf=xfront*1000; xfb=xf+170*sc; xbb=min(-25.0,xb-110)
        hull=[(xbb,-hb,-60),(xbb,hb,-60),(xfb,-hb,-100),(xfb,hb,-100),(xb,-hw_,zt),(xb,hw_,zt),(xf,-hw_,zt),(xf,hw_,zt)]
        hv=' '.join(f'{-x/1000} {y/1000} {z/1000}' for x,y,z in hull)
        hh=p['handle_half']; wr=p['wheel_r']; mh=p.get('mu_hook',0.35)
        bar=(f'<geom name="bar" type="capsule" fromto="{-bx:.4f} {-hh:.4f} {bh:.4f} {-bx:.4f} {hh:.4f} {bh:.4f}" size="{r:.4f}" contype="0" conaffinity="4" friction="{mh}" mass="0"/>' if p['bar_shape']=='tube'
             else f'<geom name="bar" type="box" pos="{-bx:.4f} 0 {bh:.4f}" size="{r*0.8:.4f} {hh:.4f} {r:.4f}" contype="0" conaffinity="4" friction="{mh}" mass="0"/>')
        wx0=xbt-0.01; wx1=bx+0.01
        webs=''.join(f'<geom name="web{k}" type="box" pos="{-(wx0+wx1)/2:.4f} {sg*(hh+0.01):.4f} {bh-0.012:.4f}" size="{(wx1-wx0)/2:.4f} 0.01 0.035" contype="0" conaffinity="4" mass="0"/>' for k,sg in enumerate((1,-1)))
        xff=p['xlip']; zL=p['zL_abs']-wr; lw=p['lip_w']
        lip=(f'<geom name="ledge" type="box" pos="{xff+0.015:.4f} 0 {zL+0.004:.4f}" size="0.015 {lw/2:.4f} 0.004" contype="0" conaffinity="4" friction="{mh}" mass="0" rgba="0.1 0.5 0.2 1"/>'
             f'<geom name="rim" type="box" pos="{xff+0.026:.4f} 0 {zL-0.0125:.4f}" size="0.004 {lw/2:.4f} 0.0125" contype="0" conaffinity="4" friction="{mh}" mass="0" rgba="0.1 0.5 0.2 1"/>')
        lstate,lang=p['lid']; lo={'closed':0.0,'ajar':lang,'open':lang,'hanging':4.55}[lstate]
        lid_x=xbt+0.005; lid_hl=(lid_x-xfront)/2; lid_hw=W/2
        cb_=crr_bin if crr_bin is not None else crr
        bw=lambda side,s: f'''<body name="bw{side}" pos="0 {s*p['wy']:.4f} 0"><joint name="bax{side}" type="hinge" axis="0 1 0" damping="0.01" frictionloss="{cb_*(fill+12)*9.81*0.45*0.1:.3f}"/>
<inertial mass="0.7" pos="0 0 0" diaginertia="0.002 0.0035 0.002"/><geom name="binwheel{side}" type="cylinder" size="{wr} 0.025" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body>'''
        binb=f'''<body name="bin" pos="0 0 {wr}" euler="0 0 0"><freejoint name="binfree"/>{inert(mb,cbg,Ib)}
<geom name="binhull" type="mesh" mesh="hull" contype="0" conaffinity="3" mass="0" friction="{mu}"/>{bar}{webs}{lip}
{bw('L',1)}{bw('R',-1)}
<body name="lid" pos="{-lid_x:.4f} 0 {bh:.4f}"><joint name="lid" type="hinge" axis="0 -1 0" range="{lo:.3f} 4.6" damping="0.3"/>
<inertial mass="{lidm}" pos="{lid_hl:.3f} 0 0.02" diaginertia="0.05 0.09 0.13"/>
<geom name="lid" type="box" pos="{lid_hl:.4f} 0 0.015" size="{lid_hl:.4f} {lid_hw:.4f} 0.015" contype="0" conaffinity="12" friction="0.4" mass="0"/></body></body>'''
        bm=mb+1.4+lidm; asset=f'<asset><mesh name="hull" vertex="{hv}"/></asset>'
    else: asset=''
    tp=tug_pose
    xml=f'''<mujoco model="bin_carrier_cgB"><compiler angle="degree"/>
<option timestep="{DT}" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic" noslip_iterations="3"/>
<default><geom solref="0.008 1" solimp="0.9 0.99 0.002"/></default>{asset}
<worldbody>{ground}
<body name="tug" pos="{tp[0]:.4f} {tp[1]:.4f} 0" euler="0 0 {tp[2]}"><freejoint name="tugfree"/>{inert(*ch)}{body}{guards}
{drive('L',1)}{drive('R',-1)}{caster('L',1)}{caster('R',-1)}{'' if PADCAR else padb}{lift}</body>
{binb}</worldbody>
<contact><exclude body1="tug" body2="cwheelL"/><exclude body1="tug" body2="cwheelR"/><exclude body1="tug" body2="cforkL"/><exclude body1="tug" body2="cforkR"/></contact>
<actuator><velocity name="mL" joint="axleL" kv="{150*G['kvs']}" forcerange="-{G['tcap']} {G['tcap']}"/><velocity name="mR" joint="axleR" kv="{150*G['kvs']}" forcerange="-{G['tcap']} {G['tcap']}"/>
<position name="liftact" joint="lift" kp="200000" kv="8000" forcerange="-{G['act_N']} {G['act_N']}"/>
<motor name="keepm" joint="keeper" gear="1" ctrllimited="true" ctrlrange="-8 8"/>
<position name="padact" joint="padext" kp="100000" kv="3000" forcerange="-1500 1500"/></actuator></mujoco>'''
    tm=sum(r['kg'] for r in rows)+car['kg']
    return xml,tm,bm
class SimB:
    def __init__(s,binkey='ESE240SL',p=None,**kw):
        s.binkey=binkey; s.p=bin_params(binkey,p); s.kw=kw
        xml,s.tug_mass,s.bin_mass=build_xml(binkey,s.p,**kw); s.xml=xml; s.m=mujoco.MjModel.from_xml_string(xml); s.d=mujoco.MjData(s.m)
        s.with_bin=kw.get('with_bin',True); s.grabber='CB'
        B=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_BODY,n); Gd=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_GEOM,n)
        s.bid={n:B(n) for n in ('tug','lift','pad','keeper','wheelL','wheelR')+(('bin','bwL','bwR','lid') if s.with_bin else ())}
        names=['driveL','driveR','casterL','casterR','ground','bump','nib','tooth','faceplate','padg','keeptip','guard0','guard1','flare0','flare1','antitip0','antitip1','rearface','keeparm','keeptip2']
        if s.with_bin: names+=['binwheelL','binwheelR','binhull','bar','ledge','rim','lid']
        s.gid={n:Gd(n) for n in names}
        s.jq=lambda n:s.m.jnt_qposadr[mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_JOINT,n)]
        s.jv=lambda n:s.m.jnt_dofadr[mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_JOINT,n)]
        s.aid=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_ACTUATOR,n)
        s.keeper_cmd=6.0; s.d.qpos[s.jq('keeper')]=1.4
        mujoco.mj_forward(s.m,s.d)
        s.lift_mass=float(s.m.body_subtreemass[s.bid['lift']])
    def set_grade(s,gx=0.0,gy=0.0):
        a=math.atan(gx); b=math.atan(gy)
        s.m.opt.gravity[:]=9.81*np.array([-math.sin(a)*math.cos(b),-math.cos(a)*math.sin(b),-math.cos(a)*math.cos(b)])
    def set_brake(s,on):
        kv=(20000 if on else 150)*GEO['kvs']   # kvs: servo gain re-tuned for a different wheel radius (sensitivity only; 1.0 = frozen)
        for a in (0,1): s.m.actuator_gainprm[a][0]=kv; s.m.actuator_biasprm[a][2]=-kv
    def pre_step(s): s.d.ctrl[s.aid('keepm')]=s.keeper_cmd
    def rpy(s,b='tug'):
        R=s.d.xmat[s.bid[b]].reshape(3,3); return math.degrees(math.atan2(R[2,1],R[2,2])),math.degrees(math.asin(max(-1,min(1,-R[2,0])))),math.degrees(math.atan2(R[1,0],R[0,0]))
    def fwd_speed(s):
        R=s.d.xmat[s.bid['tug']].reshape(3,3); a=s.jv('tugfree'); return float(R[:,0]@s.d.qvel[a:a+3])
    def bin_tilt_abs(s):
        R=s.d.xmat[s.bid['bin']].reshape(3,3); return math.degrees(math.acos(max(-1,min(1,R[2,2]))))
    def bin_in_tug(s):
        Rt=s.d.xmat[s.bid['tug']].reshape(3,3); return Rt.T@(s.d.xpos[s.bid['bin']]-s.d.xpos[s.bid['tug']])
    def lift_q(s): return float(s.d.qpos[s.jq('lift')])
    def lift_force(s): return float(s.d.actuator_force[s.aid('liftact')])
    def contacts(s):
        out={k:0.0 for k in s.gid}; f=np.zeros(6); pairs={}
        for i in range(s.d.ncon):
            c=s.d.contact[i]; mujoco.mj_contactForce(s.m,s.d,i,f)
            for k,g in s.gid.items():
                if c.geom1==g or c.geom2==g: out[k]+=f[0]
            pairs[(min(c.geom1,c.geom2),max(c.geom1,c.geom2))]=pairs.get((min(c.geom1,c.geom2),max(c.geom1,c.geom2)),0.0)+f[0]
        s._pairs=pairs; return out
    def pair(s,a,b):
        ga,gb=s.gid.get(a,-9),s.gid.get(b,-9); return s._pairs.get((min(ga,gb),max(ga,gb)),0.0)
    def bin_ground(s):
        """bin (wheels + hull) normal force from ground/bump (call after contacts())"""
        return sum(s.pair(a,b) for a in ('binwheelL','binwheelR','binhull') for b in ('ground','bump'))
    def wheel_clear(s):
        """min bin-wheel bottom height above the plane z=0 (m)"""
        wr=s.p['wheel_r']; return min(float(s.d.xpos[s.bid[w]][2])-wr for w in ('bwL','bwR'))
    def nib_in_bin(s):
        """nib centre in the bin frame (m)"""
        g=s.gid['nib']; Rb=s.d.xmat[s.bid['bin']].reshape(3,3); return Rb.T@(s.d.geom_xpos[g]-s.d.xpos[s.bid['bin']])
    def seated(s):
        """truth: nib engaged in the lip channel (between body face and rim inner face, nib top >= 10 mm above the rim bottom),
        laterally on the lip; the load may sit on the nib (ledge) or on the plate (rim) - either way the lip cannot leave without lowering"""
        q=s.nib_in_bin(); P=s.p; xbt=xlip(P); zL=P['zL_abs']-P['wheel_r']; nh=GEO['nib_h']; nl=GEO['nib_l']
        top=q[2]+nh/2+0.005
        inx=(xbt-0.004<q[0]-nl/2) and (q[0]+nl/2<xbt+0.022+0.004); inz=(top>zL-0.025+0.010) and (top<zL+0.006); iny=abs(q[1])<=abs(GEO['tooth_hw']-P['lip_w']/2)+0.02   # wide comb: lip on the comb
        return bool(inx and inz and iny)
    def captured(s): return bool(s.seated() and s.wheel_clear()>0.030)
class RunnerB:
    """drive/brake model identical to scen_g5.Runner (0.6 m/s^2 ramp, kv 150 / brake kv 20000, cap 60 / 150 N m)"""
    def __init__(s,S):
        s.s=S; s.t=0.0; s.dt=S.m.opt.timestep; s.i=0; s.phase=''; s.events=[]; s.brake=True; s.w=0.0; s.wd=0.0; s.wc=0.0; s.wdc=0.0; s._bk=None
        s.ctrl_fn=None; s.grade=(0,0); s.lift_cmd=0.0; s.peak={}; s.mon=None
    def set_drive(s,v,dv=0.0): s.w=v/RW; s.wd=dv/RW; s.brake=False
    def hold(s): s.w=0; s.wd=0; s.brake=True
    def pk(s,k,v):
        if v>s.peak.get(k,(0,0,''))[0]: s.peak[k]=(round(v,2),round(s.t,3),s.phase)
    def step(s):
        S=s.s; d=S.d
        if s.ctrl_fn is not None and s.i%20==0: s.ctrl_fn()
        a=0.6/RW*s.dt
        if s.brake: s.wc=0.0; s.wdc=0.0
        else: s.wc+=max(-a,min(a,s.w-s.wc)); s.wdc+=max(-a,min(a,s.wd-s.wdc))
        d.ctrl[0]=s.wc-s.wdc/2; d.ctrl[1]=s.wc+s.wdc/2; d.ctrl[S.aid('liftact')]=s.lift_cmd
        lim=150*GEO['tcap']/60.0 if s.brake else GEO['tcap']   # [D5 option] wheel torque cap scales with the drive reduction (60 N m = frozen common term)
        S.m.actuator_forcerange[0]=[-lim,lim]; S.m.actuator_forcerange[1]=[-lim,lim]
        if s.brake!=s._bk: S.set_brake(s.brake); s._bk=s.brake
        S.pre_step(); mujoco.mj_step(S.m,d); s.t+=s.dt; s.i+=1
        if s.mon and s.i%20==0: s.mon()
    def run_for(s,T,fn=None):
        for _ in range(int(T/s.dt)):
            if fn and fn(): return True
            s.step()
        return False
    def until(s,cond,Tmax):
        for _ in range(int(Tmax/s.dt)):
            if cond(): return True
            s.step()
        return False
    def ramp_lift(s,target,rate=0.03,cond=None,Tmax=20):
        r=rate*s.dt
        for k in range(int(Tmax/s.dt)):
            if cond and k%20==0 and cond(): return True
            dl=target-s.lift_cmd
            if abs(dl)<1e-7 and abs(s.s.lift_q()-target)<0.002: return True
            s.lift_cmd+=max(-r,min(r,dl)); s.step()
        return False
    def ramp_grade(s,gx,gy,T=2.0):
        g0=s.grade; n=int(T/s.dt)
        for k in range(n):
            f=(k+1)/n; s.grade=(g0[0]+(gx-g0[0])*f,g0[1]+(gy-g0[1])*f); s.s.set_grade(*s.grade); s.step()
    def ev(s,msg): s.events.append((round(s.t,2),msg))
def soft_stop(R,Tmax=3.0):
    S=R.s; R.w=0.0; R.wd=0.0; R.brake=False; R.until(lambda: abs(S.fwd_speed())<0.02 and abs(R.wc)<0.05,Tmax); R.hold()
def heading_hold(R,v,psi_ref_deg,K=2.0):
    S=R.s
    def ctl():
        e=math.radians((psi_ref_deg-S.rpy()[2]+180)%360-180); R.w=v/RW; R.wd=max(-0.3,min(0.3,0.69*K*e))/RW; R.brake=False
    return ctl
def steer_hold(R,v,k=5.0,maxdeg=15.0,bias=0.0):
    """as scen_g5.steer_hold (G5c C2 camera-guided reversing onto the bin centre line), same gains"""
    S=R.s
    def ctl():
        pb=S.d.xpos[S.bid['bin']]; Rb=S.d.xmat[S.bid['bin']].reshape(3,3); psib=math.degrees(math.atan2(Rb[1,0],Rb[0,0]))
        e=float((S.d.xpos[S.bid['tug']]-pb)@Rb[:,1])+bias
        ref=psib+max(-maxdeg,min(maxdeg,math.degrees(math.atan(k*e))))
        er=math.radians((ref-S.rpy()[2]+180)%360-180); R.w=v/RW; R.wd=max(-0.3,min(0.3,0.69*2.0*er))/RW; R.brake=False
    return ctl
def steer_hold_f9(R,v,k,maxdeg_fn,bias=0.0):
    """[F9] steer_hold with a heading-offset limit that is a function of the nib gap (callable)"""
    S=R.s
    def ctl():
        pb=S.d.xpos[S.bid['bin']]; Rb=S.d.xmat[S.bid['bin']].reshape(3,3); psib=math.degrees(math.atan2(Rb[1,0],Rb[0,0]))
        e=float((S.d.xpos[S.bid['tug']]-pb)@Rb[:,1])+bias; md=maxdeg_fn()
        ref=psib+max(-md,min(md,math.degrees(math.atan(k*e))))
        er=math.radians((ref-S.rpy()[2]+180)%360-180); R.w=v/RW; R.wd=max(-0.3,min(0.3,0.69*2.0*er))/RW; R.brake=False
    return ctl
def start_pose(p,dy=0.0,dyaw=0.0,out=1.2):
    """tug pose (world) so that the nib front is 'out' m ahead of the bin body face; bin at the origin"""
    xbt=xlip(p); nibx=GEO['face_x']-GEO['tooth_len']
    return (xbt-nibx+out,dy,dyaw)
def approach(R,cam_sigma=0.008,thr=0.025,seed=0,retry=True):
    S=R.s; rng=np.random.default_rng(seed); bias=float(rng.normal(0,cam_sigma)); R.cam_bias=bias
    xbt=xlip(S.p); b0=S.d.xpos[S.bid['bin']].copy()
    def nib_gap():   # nib front to body face distance along the tug x axis (camera/ToF would give this), m
        return float(S.nib_in_bin()[0]-GEO['nib_l']/2-xbt)
    R.phase='1 Approach: camera-guided reversing, arms straddle the bin, comb low'; R.ctrl_fn=steer_hold(R,-0.15,5.0,15.0,bias)
    R.until(lambda: nib_gap()<0.20 or np.linalg.norm(S.d.xpos[S.bid['bin']][:2]-b0[:2])>0.08,20.0)
    R.phase='1b Final approach 0.06 m/s until the comb ToF sees the lip root 4 mm ahead of the nib (or a tip switch closes)'; R.ctrl_fn=steer_hold(R,-0.06,5.0,15.0,bias)
    st={}; tof=0.004+float(rng.uniform(-0.003,0.003))
    def stop():
        C=S.contacts()
        if nib_gap()<=tof: st['why']='tip'; return True
        if S.pair('nib','binhull')>30 or S.pair('faceplate','bar')>30 or S.pair('tooth','binhull')>30: st['why']='tip'; return True
        if np.linalg.norm(S.d.xpos[S.bid['bin']][:2]-b0[:2])>0.08: st['why']='pushed'; return True
        return nib_gap()<-0.03
    ok=R.until(stop,12.0); R.ctrl_fn=None; R.hold(); R.run_for(0.5)
    pushed=st.get('why')=='pushed' or S.bin_tilt_abs()>6
    dy=float(S.bin_in_tug()[1])+bias; R.dock_dy=round(float(S.bin_in_tug()[1])*1000,1)
    R.ev('docked: %s, bin dy %.0f mm (camera %.0f), nib gap %.0f mm, bin moved %.0f mm'%(st.get('why'),R.dock_dy,dy*1000,nib_gap()*1000,1000*np.linalg.norm(S.d.xpos[S.bid['bin']][:2]-b0[:2])))
    if retry and not pushed and (abs(dy)>thr or st.get('why')!='tip'):
        R.ev('re-approach: pull forward 0.5 m'); R.phase='1r Re-approach'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy()[2]
        R.ctrl_fn=heading_hold(R,0.15,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.5,8.0); R.ctrl_fn=None; R.hold(); R.run_for(0.4)
        R.reapp=True; return approach(R,cam_sigma,thr,seed+1000,retry=False)
    return bool(ok and st.get('why')=='tip' and not pushed)
def grab(R,seed=0):
    """approach, lift by the comb, keeper closed. Claim = lift-force rise >= 60 N AND nib seat switch AND keeper on the bar."""
    S=R.s; out={}
    S.keeper_cmd=6.0
    ok=approach(R,seed=seed); out['docked']=ok; out['reapp']=bool(getattr(R,'reapp',False)); out['dock_dy_mm']=getattr(R,'dock_dy',None)
    if not ok:
        out.update(result='bin_pushed' if S.bin_tilt_abs()>6 else 'no_dock',claim=False,captured=False); return out
    R.phase='2 Lift: comb rises until the load comes on, then +%.0f mm'%(GEO['lift_extra']*1000); R.run_for(0.3)
    f0=S.lift_force(); st={'fs':[]}
    def loaded():
        if PADCAR:   # B2 firmware: tare the lift load cell while moving (first 12 mm of travel), then a 60 N rise = load on
            q=S.lift_q(); F=S.lift_force()
            if q<0.012: st['fs'].append(F); return False
            if F-(float(np.mean(st['fs'][-20:])) if st['fs'] else f0)>60.0: st['zc']=q; return True
            return False
        if S.lift_force()-f0>40.0: st['zc']=S.lift_q(); return True
        return False
    R.ramp_lift(GEO['lift_range']-0.01,0.03,cond=loaded,Tmax=12)
    if 'zc' not in st: out.update(result='safe_miss',claim=False,captured=S.captured(),why='no load pick-up'); return out
    R.ramp_lift(min(st['zc']+GEO['lift_extra'],GEO['lift_range']-0.002),0.03); R.run_for(0.8)
    R.phase='3 Keeper closes on the handle bar'; S.keeper_cmd=-6.0; R.run_for(1.0)
    S.contacts(); kq=float(S.d.qpos[S.jq('keeper')]); rise=S.lift_force()-f0
    seat_sw=(S.pair('nib','ledge')+S.pair('tooth','rim')+S.pair('nib','rim'))>20; keep_ok=S.pair('keeptip','bar')>5 or S.pair('keeptip2','bar')>5
    claim=bool(rise>60 and seat_sw and keep_ok)
    out.update(lift_rise_N=round(rise),seat_switch=bool(seat_sw),keeper_on_bar=bool(keep_ok),keeper_deg=round(math.degrees(kq),1),claim=claim,
               captured=S.captured(),wheel_clear_mm=round(S.wheel_clear()*1000,1),bin_tilt_abs=round(S.bin_tilt_abs(),1),seated=S.seated())
    if not claim:
        R.phase='3x No claim: keeper open, comb down, back off'; S.keeper_cmd=6.0; R.run_for(0.5); R.ramp_lift(0.0,0.04); R.run_for(0.5)
        out['result']='safe_miss' if not S.captured() else 'missed_claim'; return out
    out['result']='success' if out['captured'] else 'false_positive'
    R.ev('grab: claim %s captured %s clear %.0f mm rise %.0f N'%(claim,out['captured'],out['wheel_clear_mm'],rise))
    return out
def set_down(R):
    """lower until the bin carries itself (lift force < 15 % of the carry load), keeper opens, comb a further 35 mm down,
    then drive forward 0.6 m (teeth slide out under the lip). Interlock: bin upright (tilt <= 4 deg) before the comb withdraws."""
    S=R.s; out={}
    S.contacts(); Fc=S.lift_force(); R.phase='10 Set-down: comb lowers'; st={}
    def light():
        if S.lift_force()<0.15*Fc+0.15*(S.lift_mass*9.81): st['z']=S.lift_q(); return True
        return False
    R.ramp_lift(0.0,0.02,cond=light,Tmax=15)
    R.phase='11 Keeper opens, comb a further 35 mm down'; S.keeper_cmd=6.0; R.run_for(0.6)
    zt=max(0.0,S.lift_q()-0.035); R.ramp_lift(zt,0.02); R.run_for(0.5)
    out['tilt_before_withdraw']=round(S.bin_tilt_abs(),1)
    if S.bin_tilt_abs()>4.0:
        out.update(released=False,hold=True,why='bin not upright before withdraw'); R.ev('set-down interlock HOLD'); return out
    R.phase='12 Drive forward 0.6 m: comb withdraws'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy()[2]
    R.ctrl_fn=heading_hold(R,0.15,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.6,10.0); R.ctrl_fn=None; R.hold()
    R.phase='13 Bin standing alone'; R.run_for(3.0)
    q=S.nib_in_bin(); xbt=xlip(S.p)
    out.update(released=bool(q[0]-xbt>0.10),nib_clear_m=round(float(q[0]-xbt),3))
    return out

# ======================= ITER1 firmware (overrides the frozen approach / grab / set_down above) =======================
def rim_bottom_world(S):
    """lip rim bottom height above the ground plane, as the comb ToF / rear camera measure it (truth from the bin pose)"""
    P=S.p; xbt=xlip(P); zL=P['zL_abs']-P['wheel_r']
    Rb=S.d.xmat[S.bid['bin']].reshape(3,3); w=S.d.xpos[S.bid['bin']]+Rb@np.array([xbt+0.026,0,zL-0.025])
    Rt=S.d.xmat[S.bid['tug']].reshape(3,3); return float((Rt.T@(w-S.d.xpos[S.bid['tug']]))[2])
def set_pad(S,ret): S.d.ctrl[S.aid('padact')]=ret
def comb_contact(S):
    return max(S.pair(a,b) for a in ('nib','tooth','faceplate') for b in ('binhull','bar','ledge','rim','lid'))
def approach(R,cam_sigma=0.008,thr=0.025,seed=0,retry=True):
    """[F1] comb pre-set to the measured lip-rim height, [F2] force-limited contact-sensing creep, abort+back-off on bin motion"""
    S=R.s; G=GEO; rng=np.random.default_rng(seed); bias=float(rng.normal(0,cam_sigma)); R.cam_bias=bias
    xbt=xlip(S.p)
    def nib_gap(): return float(S.nib_in_bin()[0]-G['nib_l']/2-xbt)
    set_pad(S,G['pad_ret'])
    # model start-up only: the bin is spawned upright; let it settle on its own wheels/feet before the camera reference is taken
    jb=S.jv('binfree'); R.until(lambda: float(np.linalg.norm(S.d.qvel[jb:jb+6]))<0.002 and R.t>0.3,3.0)
    b0=S.d.xpos[S.bid['bin']].copy(); t0=S.bin_tilt_abs()
    if not hasattr(R,'tilt0'): R.tilt0=t0   # [F5] bin's own standing tilt (rear camera), reference for the set-down upright interlock
    moved=lambda: float(np.linalg.norm(S.d.xpos[S.bid['bin']][:2]-b0[:2]))
    rim=rim_bottom_world(S)+float(rng.normal(0,0.003)); R.rim_meas=rim
    qa=min(max(rim-G['rim_off']-G['car_zero'],0.0),G['lift_range']-0.12); R.q_app=qa
    R.phase='0 Comb to approach height (lip rim - %.0f mm)'%(G['rim_off']*1000); R.ramp_lift(qa,0.05,Tmax=8); R.run_for(0.2)
    F9=os.environ.get('CGB_F9')=='1'   # [F9 candidate] heading limit 10 deg far out, tapered to 2 deg over the last 0.5 m; faster pivot (see below)
    if F9:
        taper=lambda: max(2.0,min(10.0,2.0+8.0*(nib_gap()-0.10)/0.40))
        R.phase='1 Approach: camera-guided reversing'; R.ctrl_fn=steer_hold_f9(R,-0.15,5.0,taper,bias)
    else:
        R.phase='1 Approach: camera-guided reversing'; R.ctrl_fn=steer_hold(R,-0.15,5.0,15.0,bias)
    R.until(lambda: nib_gap()<0.20 or moved()>0.08,20.0)          # funnel/flare contact allowed here (as G6), 80 mm abort
    R.phase='1b Final approach 0.06 m/s'; R.ctrl_fn=steer_hold_f9(R,-0.06,5.0,taper,bias) if F9 else steer_hold(R,-0.06,5.0,15.0,bias)
    F8=os.environ.get('CGB_F8')=='1'   # [F8 candidate, default OFF] distance-based 1b (no 10 s timeout); no pivot/creep unless the gap is < 0.10 m
    R.until(lambda: nib_gap()<G['creep_gap'] or moved()>0.08,25.0 if F8 else 10.0)
    if F8 and nib_gap()>0.10:
        R.ctrl_fn=None; R.hold(); R.run_for(0.3); why='funnel'; R.dock_dy=round(float(S.bin_in_tug()[1])*1000,1)
        R.ev('docked: funnel stall at nib gap %.0f mm, bin dy %.0f mm'%(nib_gap()*1000,R.dock_dy))
        if retry:
            R.ev('back off 0.6 m and re-approach'); R.phase='1r Back off and re-approach'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy('bin')[2]
            R.ctrl_fn=heading_hold(R,0.10,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.6,10.0); R.ctrl_fn=None; R.hold(); R.run_for(0.4)
            R.reapp=True; return approach(R,cam_sigma,thr,seed+1000,retry=False)
        R.dock_why=why; return False
    # [F6] creep with dual-ToF yaw alignment (two comb-end ToFs on the body face; yaw error sigma yaw_sigma deg)
    ybias=float(rng.normal(0,G['yaw_sigma'])); R.yaw_bias=ybias
    def relyaw(): return (S.rpy()[2]-S.rpy('bin')[2]+180)%360-180+ybias
    def creep_ctl():
        e=math.radians(-relyaw()); R.w=-G['creep_v']/RW; R.wd=max(-0.04,min(0.04,0.69*3.0*e))/RW; R.brake=False
    R.phase='1c-a Stop and pivot in place until the dual-ToF yaw is within 0.5 deg'; R.ctrl_fn=None; R.hold(); R.run_for(0.3)
    pl,pT=(0.10,12.0) if F9 else (0.04,6.0)   # [F9] pivot wheel-speed limit 0.04 -> 0.10 m/s, timeout 6 -> 12 s
    def piv_ctl():
        e=math.radians(-relyaw()); R.w=0.0; R.wd=max(-pl,min(pl,0.69*3.0*e))/RW; R.brake=False
    R.ctrl_fn=piv_ctl; R.until(lambda: abs(relyaw())<=0.5,pT); R.ctrl_fn=None; R.hold(); R.run_for(0.3)
    b0=S.d.xpos[S.bid['bin']].copy(); t0=S.bin_tilt_abs()
    R.phase='1c Creep %.2f m/s, yaw-aligned, stop on ToF / comb contact / pad contact / bin motion'%G['creep_v']; R.ctrl_fn=creep_ctl
    st={}; tof=0.004+float(rng.uniform(-0.003,0.003))
    def stop():
        S.contacts()
        if nib_gap()<=tof: st['why']='tof'; return True
        if comb_contact(S)>30: st['why']='contact'; return True
        if S.pair('padg','binhull')>30: st['why']='pad'; return True
        if moved()>0.010 or S.bin_tilt_abs()-t0>2.0: st['why']='moved'; return True
        if nib_gap()<-0.03: st['why']='overrun'; return True
        return False
    ok=R.until(stop,12.0); R.ctrl_fn=None; R.hold(); R.run_for(0.5)
    why=st.get('why','timeout'); gap=nib_gap()
    dy=float(S.bin_in_tug()[1])+bias; R.dock_dy=round(float(S.bin_in_tug()[1])*1000,1)
    R.ev('docked: %s, bin dy %.0f mm (camera %.0f), nib gap %.0f mm, bin moved %.0f mm, rim %.3f q_app %.3f, yaw meas %.1f true %.1f deg'%(why,R.dock_dy,dy*1000,gap*1000,1000*moved(),rim,qa,relyaw(),relyaw()-ybias))
    R.dock_relyaw=round(relyaw(),2)
    good=why in ('tof','contact') and gap<=0.010 and S.bin_tilt_abs()-t0<3.0 and abs(relyaw())<=G['yaw_ok']
    if retry and (not good or abs(dy)>thr):
        R.ev('back off 0.4 m and re-approach'); R.phase='1r Back off and re-approach'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy()[2]
        R.ctrl_fn=heading_hold(R,0.10,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.4,8.0); R.ctrl_fn=None; R.hold(); R.run_for(0.4)
        R.reapp=True; return approach(R,cam_sigma,thr,seed+1000,retry=False)
    R.dock_why=why
    return bool(good)
def grab(R,seed=0):
    """approach, lift (load on = lift-force rise >= 60 N AND nib seat switch), +lift_extra1, keeper closes, pad extends (D2).
    Claim = lift-force rise >= 60 N AND nib seat switch AND keeper on the bar."""
    S=R.s; G=GEO; out={}
    S.keeper_cmd=6.0
    ok=approach(R,seed=seed); out['docked']=ok; out['reapp']=bool(getattr(R,'reapp',False)); out['dock_dy_mm']=getattr(R,'dock_dy',None)
    if not ok:
        out.update(result='bin_pushed' if S.bin_tilt_abs()>6 else 'no_dock',claim=False,captured=False); return out
    R.phase='2 Lift: comb rises until the load comes on'; R.run_for(0.3)
    q0=S.lift_q(); f0=S.lift_force(); st={'fs':[]}
    def seat_sw(): return (S.pair('nib','ledge')+S.pair('tooth','rim')+S.pair('nib','rim'))>20
    q_ledge=R.rim_meas+0.025-G['car_zero']; tref=getattr(R,'tilt0',S.bin_tilt_abs())
    def loaded():
        q=S.lift_q(); F=S.lift_force()
        if S.bin_tilt_abs()-tref>3.0: st['abort']='bin tilting during lift'; return True     # [F6] camera tilt abort
        if q-q0<0.012: st['fs'].append(F); return False
        S.contacts()
        if F-(float(np.mean(st['fs'][-20:])) if st['fs'] else f0)>60.0 and seat_sw():
            if q<q_ledge-0.012: st['abort']='load on %.0f mm below the expected ledge (rim catch)'%(1000*(q_ledge-q)); return True   # [F6] rim catch
            st['zc']=q; return True
        return False
    R.ramp_lift(G['lift_range']-0.002,0.03,cond=loaded,Tmax=12)
    if 'zc' not in st:
        R.phase='2x Lift abort: comb back to the approach height'; R.ramp_lift(q0,0.04); R.run_for(0.3)
        out.update(result='safe_miss',claim=False,captured=S.captured(),why=st.get('abort','no load pick-up')); R.ev('lift abort: '+out['why']); return out
    R.zc=st['zc']; f_tare=float(np.mean(st['fs'][-20:])) if st['fs'] else f0
    R.phase='2b Pad extends during the +100 mm lift (bin hangs against it before the keeper closes)'; set_pad(S,0.0)   # [F7] pad first, then keeper
    tgt=G['lift_range']-0.002 if 'liftmax' in FIX else min(st['zc']+G['lift_extra1'],G['lift_range']-0.002)   # [FH1] lift to the stroke end
    R.ramp_lift(tgt,0.03); R.run_for(0.8)
    R.phase='3 Keeper closes on the handle bar'; S.keeper_cmd=-6.0; R.run_for(1.2)
    S.contacts(); kq=float(S.d.qpos[S.jq('keeper')]); rise=S.lift_force()-f_tare
    ss=seat_sw(); keep_ok=True   # Rev H: no handle-bar keeper; claim = load + comb switches
    claim=bool(rise>60 and ss and keep_ok)
    if 'wheelchk' in FIX:   # [FH2] rear camera checks both bin wheels >= 30 mm clear (sigma 5 mm) before the claim; else lower + report
        wc=S.wheel_clear()+float(np.random.default_rng(seed+77).normal(0,0.005)); out['wheel_cam_mm']=round(wc*1000,1)
        claim=claim and wc>0.030
    out.update(lift_rise_N=round(rise),seat_switch=bool(ss),keeper_on_bar=bool(keep_ok),keeper_deg=round(math.degrees(kq),1),claim=claim,zc=round(st['zc'],3),q_app=round(R.q_app,3),
               captured=S.captured(),wheel_clear_mm=round(S.wheel_clear()*1000,1),bin_tilt_abs=round(S.bin_tilt_abs(),1),seated=S.seated(),dock=getattr(R,'dock_why',None))
    if not claim:
        R.phase='3x No claim: keeper open, pad retract, comb down, back off'; S.keeper_cmd=6.0; set_pad(S,G['pad_ret']); R.run_for(0.5); R.ramp_lift(R.q_app,0.04); R.run_for(0.5)
        out['result']='safe_miss' if not S.captured() else 'missed_claim'; return out
    out['result']='success' if out['captured'] else 'false_positive'
    R.ev('grab: claim %s captured %s clear %.0f mm rise %.0f N tilt %.1f'%(claim,out['captured'],out['wheel_clear_mm'],rise,S.bin_tilt_abs()))
    return out
def set_down(R):
    """[F4] SD2 position-based set-down: comb to the recorded pick-up height zc, keeper opens + pad retracts (D2), comb to zc-0.050
    (25 mm under the rim bottom), interlock bin upright (<= 4 deg), drive forward 0.6 m."""
    S=R.s; G=GEO; out={}
    zc=getattr(R,'zc',max(0.0,S.lift_q()-G['lift_extra1']))
    R.phase='10 SD2: comb lowers by position to the pick-up height'; R.ramp_lift(zc,0.02,Tmax=15); R.run_for(0.5)
    out['wheel_clear_at_zc_mm']=round(S.wheel_clear()*1000,1)
    R.phase='11 SD2: keeper opens, pad retracts, comb to 25 mm under the rim'; S.keeper_cmd=6.0; set_pad(S,G['pad_ret']); R.run_for(0.6)
    R.ramp_lift(max(0.0,zc-0.050),0.02,Tmax=10); R.run_for(0.8)
    out['tilt_before_withdraw']=round(S.bin_tilt_abs(),1); out['wheel_clear_before_withdraw_mm']=round(S.wheel_clear()*1000,1)
    if abs(S.bin_tilt_abs()-getattr(R,'tilt0',0.0))>3.0:   # [F5] upright interlock relative to the bin's own standing tilt
        out.update(released=False,hold=True,why='bin not upright before withdraw'); R.ev('set-down interlock HOLD'); return out
    R.phase='12 Drive forward 0.6 m: comb withdraws'; x0=S.d.xpos[S.bid['tug']].copy(); psi=S.rpy()[2]
    R.ctrl_fn=heading_hold(R,0.15,psi); R.until(lambda: np.linalg.norm(S.d.xpos[S.bid['tug']][:2]-x0[:2])>=0.6,10.0); R.ctrl_fn=None; R.hold()
    R.phase='13 Bin standing alone'; R.run_for(3.0)
    q=S.nib_in_bin(); xbt=xlip(S.p)
    out.update(released=bool(q[0]-xbt>0.10),nib_clear_m=round(float(q[0]-xbt),3),sd='SD2it1')
    return out
