# MuJoCo model of Rev F: tug (free) + drive wheels + casters + tilting mast (hinge, position servo with
# actuator-geometry torque limit) + floating hook carriage (slide + return spring) + bin (free) with wheels.
# Hooks = two connect equalities, inactive until latch. Wheel-stop crossbeam, channel arms, anti-tip rollers are tug geoms.
import json, math, numpy as np, mujoco
from model_revF import TX, PX, PZ, KZ, EH, S_TOP, S_BOT, ACT_BASE, ACT_S, ACT_E, HX, HZ, mast_pose
M = json.load(open('mass_revF.json'))
TXm, PXm, PZm, EHm, KZm = TX/1000, PX/1000, PZ/1000, EH/1000, KZ/1000
def box_I(m,dx,dy,dz): return np.diag([m*(dy*dy+dz*dz)/12,m*(dx*dx+dz*dz)/12,m*(dx*dx+dy*dy)/12])
MAST=('Mast rail','Mast pivot lug','Carriage float stop','Mast top plate','Mast lower cross','Actuator bracket','Rear docking camera','Carriage return spring','Tilt actuator rod')
def grp(r):
    n=r['name']
    if n.startswith(('Drive wheel','Wheel hub')): return 'wheel'
    if n.startswith('Caster 200'): return 'castw'
    if n.startswith('Caster fork'): return 'castf'
    if r['mod']=='Grabber': return 'carr'
    if n.startswith(MAST): return 'mast'
    if r['mod']=='Rear frame' or n.startswith('Tilt actuator IP66'): return 'rear'
    return 'chassis'
def composite(rows,origin):
    m=sum(r['kg'] for r in rows)
    if m==0: return 1e-3,np.zeros(3),np.eye(3)*1e-6
    c=sum(r['kg']*np.array(r['p']) for r in rows)/m; I=np.zeros((3,3))
    for r in rows:
        d=np.array(r['p'])-c; I+=box_I(r['kg'],*r['d'])+r['kg']*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    return m,c-origin,I+np.eye(3)*1e-5
def inert(m,c,I): return f'<inertial mass="{m:.4f}" pos="{c[0]:.4f} {c[1]:.4f} {c[2]:.4f}" fullinertia="{I[0,0]:.5f} {I[1,1]:.5f} {I[2,2]:.5f} {I[0,1]:.5f} {I[0,2]:.5f} {I[1,2]:.5f}"/>'
def act_lever(phi):
    """moment arm (m) of the tilt actuator about the mast pin at mast angle phi (rad)"""
    c,s=math.cos(phi),math.sin(phi)
    A=np.array([PXm+ACT_E/1000*c+ACT_S/1000*s, PZm-ACT_E/1000*s+ACT_S/1000*c]); B=np.array(ACT_BASE)/1000
    d=A-B; u=d/np.linalg.norm(d); r=A-np.array([PXm,PZm]); return abs(r[0]*u[1]-r[1]*u[0]), float(np.linalg.norm(d))
def build_xml(fill=96, ballast=4, mu=0.5, terrain='flat', crr=0.06, hole_x=None, bump=None, ballast_x=None, caster_x=0.74,
              tug_x0=None, phi0=8.0, act_force=2500, kv=150, rear_scale=1.0, drive4=False, hook_tc=0.004,
              tug_pose=None, bin_pose=None, bumper_hits_bin=False, walls=(), yaw_range=70, bumper_mu=0.5, antitip_clear=0.07, multiccd=False, bin_solref=None):
    # Rev F.1 additions: rear_scale (lighter rear frame), drive4 (chain-coupled front wheels, swivel locked),
    # hook_tc (hook compliance: latch constraint time-constant), tug_pose/bin_pose (x,y,yaw_deg), walls (static boxes),
    # bumper_hits_bin (front bumper collides with the bin, for nudging an empty bin).
    rows=[]
    for r in M['rows']:
        if r['name'].startswith('Ballast') and r['cz']>124+ballast*10.5: continue
        px=(r['cx']-TX)/1000
        if ballast_x is not None and r['name'].startswith('Ballast'): px=ballast_x
        rows.append(dict(name=r['name'],mod=r['mod'],kg=r['kg'],p=[px,r['cy']/1000,r['cz']/1000],d=[r['dx']/1000,r['dy']/1000,r['dz']/1000]))
    for r in rows: r['g']=grp(r)
    for r in rows:
        if r['g']=='rear' and not r['name'].startswith(('Tilt actuator','Yaw turntable','Anti-tip roller 100','Stop roller','Wheel-contact')): r['kg']*=rear_scale
    tug_mass=sum(r['kg'] for r in rows)
    piv=np.array([PXm-TXm,0,PZm]); kp=np.array([0,0,KZm])
    ch=composite([r for r in rows if r['g']=='chassis'],np.zeros(3))
    re=composite([r for r in rows if r['g']=='rear'],kp)
    ma=composite([r for r in rows if r['g']=='mast'],piv)
    ca=composite([r for r in rows if r['g']=='carr'],piv+np.array([0,0,S_TOP/1000]))
    wm=sum(r['kg'] for r in rows if r['g']=='wheel')/2; cwm=sum(r['kg'] for r in rows if r['g']=='castw')/2; cfm=sum(r['kg'] for r in rows if r['g']=='castf')/2
    fr=f'{mu} 0.005 0.0001'
    me,ce=12.3-1.4,np.array([-0.32,0,0.42]); mf,cf=fill,np.array([-0.33,0,0.38])   # 1.4 kg = the two bin wheels, modelled as their own bodies
    mb=me+mf; cb=(me*ce+mf*cf)/mb
    Ib=box_I(me,0.6,0.55,1.0)+box_I(mf,0.5,0.45,0.7)
    for mm,cc in ((me,ce),(mf,cf)):
        d=cc-cb; Ib+=mm*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    hull=[(-40,-240,-60),(-40,240,-60),(-590,-240,-100),(-590,240,-100),(0,-290,930),(0,290,930),(-760,-290,930),(-760,290,930)]
    hv=' '.join(f'{x/1000} {y/1000} {z/1000}' for x,y,z in hull)
    if terrain=='flat': ground=f'<geom name="ground" type="plane" size="80 80 0.1" friction="{fr}" condim="3"/>'
    elif terrain=='hole':
        x0,x1=hole_x,hole_x+0.40; y0,y1=0.345-0.22,0.345+0.22
        ground=f'''<geom name="floor" type="plane" pos="0 0 -0.10" size="80 80 0.1" friction="{fr}" condim="3"/>
<geom name="gA" type="box" pos="{(x0-40)/2} 0 -0.05" size="{(x0+40)/2} 40 0.05" friction="{fr}" condim="3"/>
<geom name="gB" type="box" pos="{(x1+40)/2} 0 -0.05" size="{(40-x1)/2} 40 0.05" friction="{fr}" condim="3"/>
<geom name="gC" type="box" pos="{(x0+x1)/2} {(y0-40)/2} -0.05" size="0.2 {(y0+40)/2} 0.05" friction="{fr}" condim="3"/>
<geom name="gD" type="box" pos="{(x0+x1)/2} {(y1+40)/2} -0.05" size="0.2 {(40-y1)/2} 0.05" friction="{fr}" condim="3"/>'''
    elif terrain=='bump':
        bx,bh,by=bump
        ground=f'''<geom name="ground" type="plane" size="80 80 0.1" friction="{fr}" condim="3"/>
<geom name="bump" type="box" pos="{bx} {by} {bh/2}" size="0.15 0.25 {bh/2}" friction="{fr}" condim="3"/>'''
    for k,(cx,cy,cz,hx,hy,hz) in enumerate(walls):
        ground+=f'<geom name="wall{k}" type="box" pos="{cx} {cy} {cz}" size="{hx} {hy} {hz}" friction="0.6" condim="3" rgba="0.2 0.5 0.2 1"/>'
    wq='euler="90 0 0"'
    def drive(side,s):
        return f'''<body name="wheel{side}" pos="0 {s*0.345} 0.165"><joint name="axle{side}" type="hinge" axis="0 1 0" damping="0.05" frictionloss="{crr*300*0.165:.3f}"/>
<inertial mass="{wm:.3f}" pos="0 0 0" diaginertia="{0.035*wm/3.65:.4f} {0.6*wm*0.165**2:.4f} {0.035*wm/3.65:.4f}"/>
<geom name="drive{side}" type="cylinder" size="0.165 0.035" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body>'''
    def caster(side,s):
        return f'''<body name="cfork{side}" pos="{caster_x} {s*0.2} 0.1"><joint name="swivel{side}" type="hinge" axis="0 0 1" damping="0.05" {'limited="true" range="-0.5 0.5"' if drive4 else ''}/>
<inertial mass="{cfm:.3f}" pos="-0.02 0 0.08" diaginertia="0.004 0.004 0.002"/>
<body name="cwheel{side}" pos="-0.05 0 0"><joint name="cax{side}" type="hinge" axis="0 1 0" damping="0.005" frictionloss="{crr*200*0.1:.3f}"/>
<inertial mass="{cwm:.3f}" pos="0 0 0" diaginertia="0.004 {0.6*cwm*0.01:.4f} 0.004"/>
<geom name="caster{side}" type="cylinder" size="0.1 0.025" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body></body>'''
    def binwheel(side,s):
        return f'''<body name="bw{side}" pos="0 {s*0.27} 0"><joint name="bax{side}" type="hinge" axis="0 1 0" damping="0.01" frictionloss="{crr*(fill+12)*9.81*0.45*0.1:.3f}"/>
<inertial mass="0.7" pos="0 0 0" diaginertia="0.002 0.0035 0.002"/>
<geom name="binwheel{side}" type="cylinder" size="0.1 0.025" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1" {f'solref="{bin_solref} 1" solimp="0.9 0.95 0.005"' if bin_solref else ''}/></body>'''
    if tug_x0 is None: tug_x0=TXm
    tp=tug_pose if tug_pose is not None else (tug_x0,0.0,0.0); bp=bin_pose if bin_pose is not None else (0.0,0.0,0.0)
    ph0=math.radians(phi0)
    # tug-frame geoms (tug origin = ground under drive axle)
    tg=f'''<geom name="tray" type="box" pos="0.28 0 0.194" size="0.35 0.26 0.074" contype="0" conaffinity="1" mass="0"/>
<geom name="bumper" type="box" pos="0.7625 0 0.18" size="0.0175 0.33 0.05" contype="{1 if bumper_hits_bin else 0}" conaffinity="1" friction="{bumper_mu}" mass="0"/>
<geom name="pod" type="box" pos="0.11 0 0.32" size="0.092 0.112 0.052" contype="2" conaffinity="0" mass="0"/>
<geom name="deckrear" type="box" pos="0.0 0 0.268" size="0.07 0.26 0.004" contype="2" conaffinity="0" mass="0"/>'''
    rg=f'''<geom name="spine" type="box" pos="{(PXm-TXm+0.10)/2:.3f} 0 0.009" size="{(0.10-(PXm-TXm))/2+0.03:.3f} 0.03 0.02" contype="2" conaffinity="0" mass="0"/>
<geom name="stopbar" type="capsule" fromto="{0.12-TXm:.3f} -0.33 {0.10-KZm:.3f} {0.12-TXm:.3f} 0.33 {0.10-KZm:.3f}" size="0.022" friction="0.3" contype="1" conaffinity="0" mass="0"/>
<geom name="armL" type="box" pos="{0.005-TXm:.3f} 0.325 {0.10-KZm:.3f}" size="0.115 0.01 0.02" friction="0.3" contype="1" conaffinity="0" mass="0"/>
<geom name="armR" type="box" pos="{0.005-TXm:.3f} -0.325 {0.10-KZm:.3f}" size="0.115 0.01 0.02" friction="0.3" contype="1" conaffinity="0" mass="0"/>
<geom name="antitipL" type="sphere" pos="{-0.21-TXm:.3f} 0.36 {antitip_clear+0.05-KZm:.3f}" size="0.05" friction="0.05" contype="1" conaffinity="0" mass="0"/>
<geom name="antitipR" type="sphere" pos="{-0.21-TXm:.3f} -0.36 {antitip_clear+0.05-KZm:.3f}" size="0.05" friction="0.05" contype="1" conaffinity="0" mass="0"/>'''
    lim=act_force*0.22
    xml=f'''<mujoco model="bin_tug_revF"><compiler angle="degree"/>
<option timestep="0.0005" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic" noslip_iterations="3">{'<flag multiccd="enable"/>' if multiccd else ''}</option>
<default><geom solref="0.008 1" solimp="0.9 0.99 0.002"/></default>
<asset><mesh name="hull" vertex="{hv}"/></asset>
<worldbody>{ground}
<body name="tug" pos="{tp[0]:.4f} {tp[1]:.4f} 0" euler="0 0 {tp[2]}"><freejoint name="tugfree"/>{inert(*ch)}{tg}
{drive('L',1)}{drive('R',-1)}{caster('L',1)}{caster('R',-1)}
<body name="rear" pos="0 0 {KZm:.4f}"><joint name="yaw" type="hinge" axis="0 0 1" range="-{yaw_range} {yaw_range}" damping="5"/>{inert(*re)}{rg}
<body name="mast" pos="{piv[0]:.4f} 0 {piv[2]-KZm:.4f}"><joint name="tilt" type="hinge" axis="0 1 0" range="-12 80" damping="400" ref="0"/>{inert(*ma)}
<body name="carriage" pos="0 0 {S_TOP/1000:.4f}"><joint name="float" type="slide" axis="0 0 1" range="{(S_BOT-S_TOP)/1000:.3f} 0" stiffness="200" springref="0.3" damping="150" frictionloss="15"/>{inert(*ca)}
<site name="hookL" pos="{EHm:.4f} 0.19 0"/><site name="hookR" pos="{EHm:.4f} -0.19 0"/></body></body></body></body>
<body name="bin" pos="{bp[0]:.4f} {bp[1]:.4f} 0.1" euler="0 0 {bp[2]}"><freejoint name="binfree"/>{inert(mb,cb,Ib)}
<geom name="binhull" type="mesh" mesh="hull" contype="0" conaffinity="3" mass="0" friction="{mu}" {f'solref="{bin_solref} 1" solimp="0.9 0.95 0.005"' if bin_solref else ''}/>
<site name="handleL" pos="{HX/1000} 0.19 {HZ/1000}"/><site name="handleR" pos="{HX/1000} -0.19 {HZ/1000}"/>
{binwheel('L',1)}{binwheel('R',-1)}</body></worldbody>
<equality><connect name="latchL" active="false" body1="carriage" body2="bin" anchor="{EHm:.4f} 0.19 0" solref="0.004 1"/>
<connect name="latchR" active="false" body1="carriage" body2="bin" anchor="{EHm:.4f} -0.19 0" solref="0.004 1"/>
{'<joint joint1="caxL" joint2="axleL" polycoef="0 1.65 0 0 0"/><joint joint1="caxR" joint2="axleR" polycoef="0 1.65 0 0 0"/>' if drive4 else ''}</equality>
<contact><exclude body1="tug" body2="cwheelL"/><exclude body1="tug" body2="cwheelR"/><exclude body1="tug" body2="cforkL"/><exclude body1="tug" body2="cforkR"/></contact>
<actuator><velocity name="mL" joint="axleL" kv="{kv}" forcerange="-60 60"/><velocity name="mR" joint="axleR" kv="{kv}" forcerange="-60 60"/>
<position name="act" joint="tilt" kp="60000" kv="3000" forcerange="-{lim:.0f} {lim:.0f}"/>
<position name="yawlock" joint="yaw" kp="20000" kv="800" forcerange="-600 600"/></actuator></mujoco>'''
    return xml,tug_mass,mb+1.4
class Sim:
    def __init__(s,**kw):
        xml,s.tug_mass,s.bin_mass=build_xml(**kw); s.m=mujoco.MjModel.from_xml_string(xml); s.d=mujoco.MjData(s.m)
        s.kw=kw; s.act_force=kw.get('act_force',2500)
        G=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_GEOM,n)
        s.gid={n:G(n) for n in ('driveL','driveR','casterL','casterR','binwheelL','binwheelR','binhull','stopbar','armL','armR','antitipL','antitipR','pod','deckrear','spine','bumper')}
        B=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_BODY,n)
        s.bid={n:B(n) for n in ('tug','rear','bin','mast','carriage','wheelL','wheelR','cwheelL','cwheelR','cforkL','cforkR','bwL','bwR')}
        S=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_SITE,n)
        s.sid={n:S(n) for n in ('hookL','hookR','handleL','handleR')}
        s.jq=lambda n:s.m.jnt_qposadr[mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_JOINT,n)]
        s.jv=lambda n:s.m.jnt_dofadr[mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_JOINT,n)]
        s.d.qpos[s.jq('tilt')]=math.radians(kw.get('phi0',8.0)); s.d.ctrl[2]=math.radians(kw.get('phi0',8.0))
        for k,(n,sy) in enumerate((('latchL',0.19),('latchR',-0.19))):
            s.m.eq_data[k][3:6]=[HX/1000,sy,HZ/1000]
        s.kv=kw.get('kv',150)
        mujoco.mj_forward(s.m,s.d); s.grav=np.array([0,0,-9.81])
    def set_grade(s,gx=0.0,gy=0.0):
        a=math.atan(gx); b=math.atan(gy)
        s.m.opt.gravity[:]=9.81*np.array([-math.sin(a)*math.cos(b),-math.cos(a)*math.sin(b),-math.cos(a)*math.cos(b)])
    def latch(s,on=True,capture=True):
        if on and capture:   # handle seats where the hook throat actually is (float/ramp take-up)
            Rb=s.d.xmat[s.bid['bin']].reshape(3,3); xb=s.d.xpos[s.bid['bin']]
            for k,n in enumerate(('hookL','hookR')):
                s.m.eq_data[k][3:6]=Rb.T@(s.d.site_xpos[s.sid[n]]-xb)
        s.d.eq_active[0]=on; s.d.eq_active[1]=on
    def yaw_lock(s,on):
        kp,kv=(20000,800) if on else (0,0)
        s.m.actuator_gainprm[3][0]=kp; s.m.actuator_biasprm[3][1]=-kp; s.m.actuator_biasprm[3][2]=-kv; s.d.ctrl[3]=0
    def yaw_rel(s): return math.degrees(s.d.qpos[s.jq('yaw')])
    def latch_soft(s,soft):
        for k in (0,1): s.m.eq_solref[k]=[0.06 if soft else s.kw.get('hook_tc',0.004),1]
    def gap_vec(s):
        Rt=s.d.xmat[s.bid['tug']].reshape(3,3); return Rt.T@(s.d.site_xpos[s.sid['hookL']]-s.d.site_xpos[s.sid['handleL']])
    def set_brake(s,on):
        kv=20000 if on else s.kv
        for a in (0,1): s.m.actuator_gainprm[a][0]=kv; s.m.actuator_biasprm[a][2]=-kv
    def hook_gap(s):
        return max(np.linalg.norm(s.d.site_xpos[s.sid['hookL']]-s.d.site_xpos[s.sid['handleL']]),np.linalg.norm(s.d.site_xpos[s.sid['hookR']]-s.d.site_xpos[s.sid['handleR']]))
    def update_act_limit(s):
        lev,L=act_lever(s.d.qpos[s.jq('tilt')]); lim=s.act_force*lev
        s.m.actuator_forcerange[2]=[-lim,lim]; return lev,L
    def normals(s):
        out={k:0.0 for k in s.gid}; f=np.zeros(6)
        for i in range(s.d.ncon):
            c=s.d.contact[i]; mujoco.mj_contactForce(s.m,s.d,i,f)
            for k,g in s.gid.items():
                if c.geom1==g or c.geom2==g: out[k]+=f[0]
        return out
    def hook(s):
        F=np.zeros(2)
        for i in range(s.d.nefc):
            if s.d.efc_type[i]==mujoco.mjtConstraint.mjCNSTR_EQUALITY and s.d.efc_id[i]<2: F[s.d.efc_id[i]]+=s.d.efc_force[i]**2
        return np.sqrt(F)
    def rpy(s,b='tug'):
        R=s.d.xmat[s.bid[b]].reshape(3,3); return math.degrees(math.atan2(R[2,1],R[2,2])),math.degrees(math.asin(-R[2,0])),math.degrees(math.atan2(R[1,0],R[0,0]))
    def bin_tilt(s):
        R=s.d.xmat[s.bid['bin']].reshape(3,3); return math.degrees(math.atan2(R[0,2],R[2,2]))
    def bin_tilt_rel(s):
        Rb=s.d.xmat[s.bid['bin']].reshape(3,3); Rt=s.d.xmat[s.bid['tug']].reshape(3,3); R=Rt.T@Rb; return math.degrees(math.atan2(R[0,2],R[2,2]))
    def bin_yaw_rel(s):
        Rb=s.d.xmat[s.bid['bin']].reshape(3,3); Rt=s.d.xmat[s.bid['tug']].reshape(3,3); R=Rt.T@Rb; return math.degrees(math.atan2(R[1,0],R[0,0]))
    def fwd_speed(s):
        R=s.d.xmat[s.bid['tug']].reshape(3,3); a=s.jv('tugfree'); return float(R[:,0]@s.d.qvel[a:a+3])
    def tilt(s): return math.degrees(s.d.qpos[s.jq('tilt')])
    def floatpos(s): return S_TOP/1000+float(s.d.qpos[s.jq('float')])
    def snapshot(s):
        P={k:(s.d.xpos[b].tolist(),s.d.xmat[b].tolist()) for k,b in s.bid.items()}
        return P
