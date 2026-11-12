# G5 bin-range variant of sim_g3.py: adds binm= (explicit bin body: width, depth, wheel track, empty mass, hand gap, inner hinge knuckles).
# Rev G MuJoCo model. Built on the Rev F.1 model (sim_revF.py) with:
#  * a PHYSICAL grabber: hook pieces are collision boxes on a cradle (elastomer-mounted on a floating carriage); the bin handle is a
#    real bar (capsule = tube handle, box = moulded handle) between side webs; latch tongue = spring slide joint; lid = hinged body.
#    grabber='G' (Rev G cradle hook), 'F1' (Rev F.1 hook as drawn, physical), 'F1eq' (F.1 sim's idealised equality latch).
#  * variable bin geometry (bar height/diameter/offset/width, 200 or 250 mm wheels, lid state);
#  * an optional charging dock (posts, sprung contact shoes, V-guide rails) and no bin.
# Units: m, kg, N. Model frame: bin axle at x=0; tug drive axle at TX (= kingpin).
import json, math, os, numpy as np, mujoco
import sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','cad','revF1'))
import geo_g3 as GG
from model_revF import TX, PX, PZ, KZ, EH, S_TOP, S_BOT, ACT_BASE, ACT_S, ACT_E, HX as HX0, HZ as HZ0
HERE=os.path.dirname(os.path.abspath(__file__))
TXm, PXm, PZm, EHm, KZm = TX/1000, PX/1000, PZ/1000, EH/1000, KZ/1000
def box_I(m,dx,dy,dz): return np.diag([m*(dy*dy+dz*dz)/12,m*(dx*dx+dz*dz)/12,m*(dx*dx+dy*dy)/12])
MAST=('Mast rail','Mast pivot lug','Carriage float stop','Mast top plate','Mast lower cross','Actuator bracket','Rear docking camera','Carriage return spring','Tilt actuator rod')
def grp_f1(r):
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
    c,s=math.cos(phi),math.sin(phi)
    A=np.array([PXm+ACT_E/1000*c+ACT_S/1000*s, PZm-ACT_E/1000*s+ACT_S/1000*c]); B=np.array(ACT_BASE)/1000
    d=A-B; u=d/np.linalg.norm(d); r=A-np.array([PXm,PZm]); return abs(r[0]*u[1]-r[1]*u[0]), float(np.linalg.norm(d))
def load_rows(massfile, ballast, ballast_x, extra_kg=0.0):
    M=json.load(open(os.path.join(HERE,massfile))); rows=[]
    if 'tx' in M: tx=M['tx']
    else: tx=TX
    for r in M['rows']:
        if r['name'].startswith('Ballast'):
            k=r.get('k',int(round((r['cz']-129)/10.5)))
            if k>=ballast: continue
        px=(r['cx']-tx)/1000
        if ballast_x is not None and r['name'].startswith('Ballast'): px=ballast_x
        g=r.get('body') or grp_f1(r)
        rows.append(dict(name=r['name'],kg=r['kg'],p=[px,r['cy']/1000,r['cz']/1000],d=[max(r['dx'],1)/1000,max(r['dy'],1)/1000,max(r['dz'],1)/1000],g=g))
    if extra_kg: rows.append(dict(name='extra',kg=extra_kg,p=[0.35,0,0.2],d=[0.2,0.2,0.1],g='chassis'))
    return rows
def hook_geoms(pieces, pref, rgba='0.35 0.37 0.42 1', fr=0.35):
    out=[]
    for i,(pid,cx,cz,hx,hz,ang,y0,y1) in enumerate(pieces):
        out.append(f'<geom name="{pref}{i}" type="box" pos="{cx/1000:.4f} {(y0+y1)/2000:.4f} {cz/1000:.4f}" size="{hx/1000:.4f} {(y1-y0)/2000:.4f} {hz/1000:.4f}" euler="0 {ang:.3f} 0" contype="6" conaffinity="4" friction="{fr}" rgba="{rgba}" mass="0"/>')
    return '\n'.join(out)
def gh_carriage(V,variant,ca,mu_hook,pawl_jam,lat=None):
    Mo=GG.GH_MOUNT; L=dict(GG.GH_LAT); L.update(lat or {}); P=GG.pawl_params(V)
    P['mass']=round(GG.GH_PAWL['mass']*GG.pawl_length(P)/GG.pawl_length(GG.GH_PAWL),4)
    hg=hook_geoms(GG.gh_cup(V['hy'],variant=('A' if V['mode']=='passive' else 'B'),lip_chamfer=V.get('lip_chamfer',False),V=V),'hk',fr=mu_hook)
    if V.get('ice',0)>0:   # G6 task 2: debris / ice layer on each cup floor (top at -26+ice), own friction (ice 0.1, grit 0.6)
        th=float(V.get('throat',-24.0)); ice=float(V['ice'])
        for k,sg in enumerate((1,-1)):
            y0,y1=sorted((sg*(V['hy']-5),sg*(V['hy']+5)))
            hg+=f'\n<geom name="hkice{k}" type="box" pos="{(th+24)/2000:.4f} {(y0+y1)/2000:.4f} {(-26+ice/2)/1000:.4f}" size="{(24-th)/2000-0.0005:.4f} {(y1-y0)/2000:.4f} {ice/2000:.4f}" contype="6" conaffinity="4" friction="{V.get("ice_mu",0.1)}" rgba="0.8 0.9 1 1" mass="0"/>'
    pw=[]
    for side,sg in (('L',1),('R',-1)):
        gs=''.join(f'<geom name="pw{side}{i}" type="box" pos="{cx/1000:.4f} 0 {cz/1000:.4f}" size="{hx/1000:.4f} {P["w"]/2000:.4f} {hz/1000:.4f}" euler="0 {ang:.3f} 0" contype="6" conaffinity="4" friction="{mu_hook}" rgba="1 0.45 0.1 1" mass="0"/>'
                   for i,(n,cx,cz,hx,hz,ang) in enumerate(GG.gh_pawl_geoms_v(P)))
        cg=GG.gh_pawl_cg(P)
        pw.append(f'''<body name="pawl{side}" pos="{P['P'][0]/1000:.4f} {sg*(V['hy']+P['yoff'])/1000:.4f} {P['P'][1]/1000:.4f}"><joint name="pawl{side}" type="hinge" axis="0 1 0" range="0 {P['open_deg']}" stiffness="{P['k']}" springref="{-P['pre']/P['k']:.4f}" damping="0.002" frictionloss="{3.0 if pawl_jam else 0.004}" solreflimit="0.004 1"/>
<inertial mass="{P['mass']}" pos="{cg[0]/1000:.4f} 0 {cg[1]/1000:.4f}" diaginertia="6e-5 6e-5 2e-5"/>{gs}</body>''')
    if V['mode']=='passive':
        fj=f'<joint name="float" type="slide" axis="0 0 1" range="{-V["float_down"]} {V["float_up"]}" damping="60" frictionloss="5" solreflimit="0.01 1"/>'
    else:
        fj=f'<joint name="float" type="slide" axis="0 0 1" range="{-V["float_down"]} {V["float_up"]}" damping="40" frictionloss="3" solreflimit="0.01 1"/>'
    return f'''<body name="carriage" pos="0 0 {V['ref']:.4f}">{fj}{inert(*ca)}
<body name="lat" pos="0 0 0"><joint name="lat" type="slide" axis="0 1 0" range="{-L['travel']} {L['travel']}" stiffness="{L['k']}" damping="{L['c']}" frictionloss="{L['friction']}" solreflimit="0.01 1"/>
<inertial mass="0.6" pos="0 0 0" diaginertia="0.01 0.002 0.01"/>
<body name="cradle" pos="{EHm:.4f} 0 0"><joint name="mx" type="slide" axis="1 0 0" range="{-Mo['travel']} {Mo['travel']}" stiffness="{Mo['k']}" damping="{Mo['c']}"/>
<joint name="mz" type="slide" axis="0 0 1" range="{-Mo['travel']} {Mo['travel']}" stiffness="{Mo['k']}" damping="{Mo['c']}"/>
<inertial mass="1.6" pos="0.02 0 0" diaginertia="0.03 0.004 0.03"/>
{hg}
<site name="hookc" pos="0 0 0"/>{''.join(pw)}</body></body></body>'''
def mast_lidfinger():
    """K4 lid hold-down finger on the mast top: sprung (torsion) stainless arm with UHMW roller tip; only touches the lid"""
    return '''<body name="lidfinger" pos="0.010 0 0.990"><joint name="lidfinger" type="hinge" axis="0 1 0" range="-0.5 0.7" stiffness="3.0" springref="-0.35" damping="0.3"/>
<inertial mass="0.25" pos="-0.13 0 0.03" diaginertia="0.002 0.002 0.0001"/>
<geom name="lidf" type="capsule" fromto="0 0 0 -0.27 0 0.07" size="0.008" contype="8" conaffinity="0" friction="0.2" mass="0"/>
<geom name="lidftip" type="cylinder" pos="-0.275 0 0.07" size="0.014 0.06" euler="90 0 0" contype="8" conaffinity="0" friction="0.1" mass="0"/></body>'''
FPADS=[None]
def funnel_pairs(mu=0.25):
    """G3: funnel arms/flares are faced with UHMW strip (mu ~0.25 on the bin tyre); MuJoCo would otherwise take the larger
    (ground) friction of the two geoms and the tyre self-locks on a 30 deg flare."""
    out=''
    for w in ('binwheelL','binwheelR'):
        for g in ('flareL','flareR','armL','armR')+(('fpadgL','fpadgR','fpadlL','fpadlR') if FPADS[0] else ()):
            m_=FPADS[0].get('mu',mu) if (FPADS[0] and g.startswith('fpad')) else mu
            out+=f'<pair geom1="{w}" geom2="{g}" condim="3" friction="{m_} {m_} 0.005 0.0001 0.0001"/>'
    return out
def build_xml(fill=96, ballast=4, mu=0.5, terrain='flat', crr=0.06, hole_x=None, bump=None, ballast_x=0.70, caster_x=0.84,
              tug_x0=None, phi0=8.0, act_force=2500, kv=150, tug_pose=None, bin_pose=None, antitip_clear=0.10, yaw_range=70,
              grabber='G', massfile='mass_revF.json', extra_kg=0.0, with_bin=True, dock=None,
              bar_r=0.016, bar_shape='tube', bar_h=None, bar_x=None, handle_half=0.27, wheel_r=0.10, lid=('closed',0.0),
              mu_hook=0.35, mu_feet=None, flare_mu=None, tongue_jam=False, cam_fail=False, hook_tc=0.004, act_kp=60000, wind=False, gh='B1', pawl_jam=False, lidfinger=True, rest_stop=None, ghp=None, antitip_y=0.46, binm=None, fpads=None, claim_and=False, square_guard=False, lat=None, asym=None, reapp=None):
    if os.path.basename(str(massfile)).startswith('mass_g6_') and os.environ.get('G6_LEGACY_BALLASTX')!='1': ballast_x=None   # G6 fix: keep the mass file's ballast position
    yaw_range=float(os.environ.get('G6_YAWRANGE',yaw_range))   # G6: kingpin hard stop (design +/-40); legacy default 70
    rows=load_rows(massfile,ballast,ballast_x,extra_kg); FPADS[0]=fpads
    tug_mass=sum(r['kg'] for r in rows)
    piv=np.array([PXm-TXm,0,PZm]); kp=np.array([0,0,KZm])
    GHV=dict(GG.GH[gh]); GHV.update(ghp or {})
    FL=GG.G_FLOAT if grabber=='G' else GG.F_FLOAT
    s_rest=(FL['ref'] if grabber=='G' else FL['rest']) if grabber not in ('F1eq','GH') else (S_TOP/1000 if grabber=='F1eq' else GHV['ref'])
    ch=composite([r for r in rows if r['g']=='chassis'],np.zeros(3))
    re=composite([r for r in rows if r['g']=='rear'],kp)
    ma=composite([r for r in rows if r['g']=='mast'],piv)
    ca=composite([r for r in rows if r['g']=='carr'],piv+np.array([0,0,s_rest]))
    wm=sum(r['kg'] for r in rows if r['g']=='wheel')/2; cwm=sum(r['kg'] for r in rows if r['g']=='castw')/2; cfm=sum(r['kg'] for r in rows if r['g']=='castf')/2
    fr=f'{mu} 0.005 0.0001'
    lidm=1.8
    BM=binm or {}
    bh_=bar_h if bar_h is not None else HZ0/1000; bx_=bar_x if bar_x is not None else HX0/1000
    if binm:
        xbt=bx_-BM['gap']-bar_r                     # body back face at rim height (x, bin frame)
        D=BM['D']; W=BM['W']; xfront=bx_+bar_r-D+0.02; sc=D/0.74
        me,ce=BM['empty']-1.4-lidm,np.array([xbt-0.32*sc-0.0,0,0.42*bh_/0.93]); mf,cf=fill,np.array([xbt-0.33*sc,0,0.38*bh_/0.93])
        wy=BM['wy']; lid_x=xbt+0.005; lid_z=bh_; lid_hl=(lid_x-xfront)/2; lid_hw=W/2
    else:
        xbt=0.0; wy=0.27; lid_x=0.005; lid_z=0.93; lid_hl=0.385; lid_hw=0.29
        me,ce=12.3-1.4-lidm,np.array([-0.32,0,0.42]); mf,cf=fill,np.array([-0.33,0,0.38])
    mb=me+mf; cb=(me*ce+mf*cf)/mb
    Ib=box_I(me,0.6,0.55,1.0)+box_I(mf,0.5,0.45,0.7)
    for mm,cc in ((me,ce),(mf,cf)):
        d=cc-cb; Ib+=mm*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    hull=[(-40,-240,-60),(-40,240,-60),(-590,-240,-100),(-590,240,-100),(0,-290,930),(0,290,930),(-760,-290,930),(-760,290,930)]
    if binm:
        hw=W/2*1000; hb=hw-50; zt=bh_*1000; xb=xbt*1000; xf=xfront*1000; xfb=xf+170*sc; xbb=min(-25.0,xb-110)
        hull=[(xbb,-hb,-60),(xbb,hb,-60),(xfb,-hb,-100),(xfb,hb,-100),(xb,-hw,zt),(xb,hw,zt),(xf,-hw,zt),(xf,hw,zt)]
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
    if dock is not None: ground+=dock_xml(**dock)
    wq='euler="90 0 0"'
    def drive(side,s):
        return f'''<body name="wheel{side}" pos="0 {s*0.345} 0.165"><joint name="axle{side}" type="hinge" axis="0 1 0" damping="0.05" frictionloss="{crr*300*0.165:.3f}"/>
<inertial mass="{wm:.3f}" pos="0 0 0" diaginertia="{0.035*wm/3.65:.4f} {0.6*wm*0.165**2:.4f} {0.035*wm/3.65:.4f}"/>
<geom name="drive{side}" type="cylinder" size="0.165 0.035" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body>'''
    def caster(side,s):
        return f'''<body name="cfork{side}" pos="{caster_x} {s*0.2} 0.1"><joint name="swivel{side}" type="hinge" axis="0 0 1" damping="0.05"/>
<inertial mass="{max(cfm,0.2):.3f}" pos="-0.02 0 0.08" diaginertia="0.004 0.004 0.002"/>
<body name="cwheel{side}" pos="-0.05 0 0"><joint name="cax{side}" type="hinge" axis="0 1 0" damping="0.005" frictionloss="{crr*200*0.1:.3f}"/>
<inertial mass="{max(cwm,0.2):.3f}" pos="0 0 0" diaginertia="0.004 {0.6*max(cwm,0.2)*0.01:.4f} 0.004"/>
<geom name="caster{side}" type="cylinder" size="0.1 0.025" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body></body>'''
    mf_feet=mu_feet if mu_feet is not None else mu
    def binwheel(side,s):
        return f'''<body name="bw{side}" pos="0 {s*wy:.4f} 0"><joint name="bax{side}" type="hinge" axis="0 1 0" damping="0.01" frictionloss="{crr*(fill+12)*9.81*0.45*0.1:.3f}"/>
<inertial mass="0.7" pos="0 0 0" diaginertia="0.002 0.0035 0.002"/>
<geom name="binwheel{side}" type="cylinder" size="{wheel_r} 0.025" {wq} friction="{fr}" condim="3" contype="0" conaffinity="1"/></body>'''
    if tug_x0 is None: tug_x0=TXm
    tp=tug_pose if tug_pose is not None else (tug_x0,0.0,0.0); bp=bin_pose if bin_pose is not None else (0.0,0.0,0.0)
    tg=f'''<geom name="tray" type="box" pos="0.28 0 0.194" size="0.35 0.26 0.074" contype="0" conaffinity="1" mass="0"/>
<geom name="bumper" type="box" pos="0.7625 0 0.18" size="0.0175 0.33 0.05" contype="0" conaffinity="1" mass="0"/>
<geom name="pod" type="box" pos="0.11 0 0.32" size="0.092 0.112 0.052" contype="2" conaffinity="0" mass="0"/>
<geom name="deckrear" type="box" pos="0.0 0 0.268" size="0.07 0.26 0.004" contype="2" conaffinity="0" mass="0"/>'''
    flare=0.20 if grabber=='G' else 0.07; fang=30 if grabber=='G' else 25
    sb_x=0.12-TXm
    rg=f'''<geom name="spine" type="box" pos="{(PXm-TXm+0.10)/2:.3f} 0 0.009" size="{(0.10-(PXm-TXm))/2+0.03:.3f} 0.03 0.02" contype="2" conaffinity="0" mass="0"/>
<geom name="stopbar" type="capsule" fromto="{sb_x:.3f} -0.33 {0.10-KZm:.3f} {sb_x:.3f} 0.33 {0.10-KZm:.3f}" size="0.022" friction="0.3" contype="1" conaffinity="0" mass="0"/>
{('<geom name="stopbar2" type="capsule" fromto="%.3f -0.33 %.3f %.3f 0.33 %.3f" size="0.022" friction="0.3" contype="1" conaffinity="0" mass="0"/>'%(sb_x,float(os.environ['G6_SB2'])-KZm,sb_x,float(os.environ['G6_SB2'])-KZm)) if os.environ.get('G6_SB2') else ''}
<geom name="armL" type="box" pos="{0.005-TXm:.3f} 0.325 {0.10-KZm:.3f}" size="0.115 0.01 0.02" friction="0.3" contype="1" conaffinity="0" mass="0"/>
<geom name="armR" type="box" pos="{0.005-TXm:.3f} -0.325 {0.10-KZm:.3f}" size="0.115 0.01 0.02" friction="0.3" contype="1" conaffinity="0" mass="0"/>
<geom name="flareL" type="box" pos="{-0.11-TXm-flare/2*math.cos(math.radians(fang)):.3f} {0.325+flare/2*math.sin(math.radians(fang)):.3f} {0.10-KZm:.3f}" size="{flare/2:.3f} 0.008 0.02" euler="0 0 {-fang}" friction="0.3" contype="1" conaffinity="0" mass="0"/>
<geom name="flareR" type="box" pos="{-0.11-TXm-flare/2*math.cos(math.radians(fang)):.3f} {-0.325-flare/2*math.sin(math.radians(fang)):.3f} {0.10-KZm:.3f}" size="{flare/2:.3f} 0.008 0.02" euler="0 0 {fang}" friction="0.3" contype="1" conaffinity="0" mass="0"/>
<geom name="antitipL" type="sphere" pos="{-0.21-TXm:.3f} {antitip_y:.3f} {antitip_clear+0.05-KZm:.3f}" size="0.05" friction="0.05" contype="1" conaffinity="0" mass="0"/>
<geom name="antitipR" type="sphere" pos="{-0.21-TXm:.3f} {-antitip_y:.3f} {antitip_clear+0.05-KZm:.3f}" size="0.05" friction="0.05" contype="1" conaffinity="0" mass="0"/>'''
    if fpads:   # G5 fix candidate FC: sprung UHMW centring pads on the inner faces of the funnel arms (y slide, spring to free_y)
        FP=dict(free_y=0.245,k=1000.0,pre=10.0,len=0.23,lead=0.08,ang=20.0); FP.update(fpads)
        for side,sg in (('L',1),('R',-1)):
            yb=0.315; tr=yb-FP['free_y']-0.012
            rg+=f'''<body name="fpad{side}" pos="{0.005-TXm:.3f} {sg*FP['free_y']:.4f} {0.10-KZm:.3f}"><joint name="fpad{side}" type="slide" axis="0 {sg} 0" range="0 {tr:.4f}" stiffness="{FP['k']}" springref="{-FP['pre']/FP['k']:.4f}" damping="{FP.get('c',30.0)}" solreflimit="0.01 1"/>
<inertial mass="0.3" pos="0 0 0" diaginertia="0.001 0.001 0.001"/>
<geom name="fpadg{side}" type="box" pos="{-0.0:.3f} {sg*0.006:.4f} 0" size="{FP['len']/2:.3f} 0.006 0.025" friction="0.25" contype="1" conaffinity="0" mass="0" rgba="0.95 0.95 0.9 1"/>
<geom name="fpadl{side}" type="box" pos="{-FP['len']/2-FP['lead']/2*math.cos(math.radians(FP['ang'])):.3f} {sg*(0.006+FP['lead']/2*math.sin(math.radians(FP['ang']))):.4f} 0" size="{FP['lead']/2:.3f} 0.006 0.025" euler="0 0 {-sg*FP['ang']}" friction="0.25" contype="1" conaffinity="0" mass="0" rgba="0.95 0.95 0.9 1"/></body>'''
    lim=act_force*0.22
    # ---- grabber
    if grabber=='G':
        F=GG.G_FLOAT; Mo=GG.G_MOUNT; T=GG.G_TONGUE; LF=GG.G_LIDFINGER
        hg=hook_geoms(GG.G_PIECES,'hk',fr=mu_hook)
        tl=(T['x1']-T['x0'])/2000; tcx=(T['x0']+T['x1'])/2000; tcz=(T['z0']+T['z1'])/2000
        tongue=f'''<body name="tongue" pos="0 0 0"><joint name="tongue" type="slide" axis="1 0 0" range="0 {T['retract']/1000}" solreflimit="0.004 1" stiffness="{T['k']}" springref="{-T['pre']/T['k']:.4f}" damping="20" {'frictionloss="4000"' if tongue_jam else 'frictionloss="1"'}/>
<inertial mass="0.25" pos="{tcx} 0 {tcz}" diaginertia="0.001 0.0002 0.001"/>
<geom name="tongue" type="box" pos="{tcx:.4f} 0 {tcz:.4f}" size="{tl:.4f} {T['y']/1000} {(T['z1']-T['z0'])/2000:.4f}" contype="6" conaffinity="4" friction="0.2" rgba="1 0.45 0.1 1" mass="0"/></body>'''
        (px_,pz_)=LF['pivot']; Lf=LF['length']/1000; a0=math.radians(LF['down_deg']); tx_,tz_=-Lf*math.cos(a0),-Lf*math.sin(a0)
        lidf=f'''<body name="lidfinger" pos="{px_/1000} 0 {pz_/1000}"><joint name="lidfinger" type="hinge" axis="0 1 0" range="0 2.6" stiffness="{LF['k']}" springref="{-LF['pre']/LF['k']:.3f}" damping="2.0"/>
<inertial mass="0.15" pos="{tx_/2:.3f} 0 {tz_/2:.3f}" diaginertia="0.002 0.002 0.0001"/>
<geom name="lidfL" type="capsule" fromto="0 {LF['y'][1]/1000} 0 {tx_:.4f} {LF['y'][1]/1000} {tz_:.4f}" size="0.004" contype="6" conaffinity="4" friction="0.3" mass="0"/>
<geom name="lidfR" type="capsule" fromto="0 {LF['y'][0]/1000} 0 {tx_:.4f} {LF['y'][0]/1000} {tz_:.4f}" size="0.004" contype="6" conaffinity="4" friction="0.3" mass="0"/></body>'''
        carriage=f'''<body name="carriage" pos="0 0 {F['ref']:.4f}"><joint name="float" type="slide" axis="0 0 1" range="{-F['down']} {F['up']}" damping="40" frictionloss="3" solreflimit="0.01 1"/>{inert(*ca) if ca[0]>0.01 else '<inertial mass="2.0" pos="0 0 0" diaginertia="0.02 0.02 0.02"/>'}
<body name="cradle" pos="{EHm:.4f} 0 0"><joint name="mx" type="slide" axis="1 0 0" range="{-Mo['travel']} {Mo['travel']}" stiffness="{Mo['k']}" damping="{Mo['c']}" solreflimit="0.01 1"/>
<joint name="mz" type="slide" axis="0 0 1" range="{-Mo['travel']} {Mo['travel']}" stiffness="{Mo['k']}" damping="{Mo['c']}" solreflimit="0.01 1"/>
<inertial mass="2.6" pos="0.01 0 0.0" diaginertia="0.02 0.004 0.02"/>
{hg}
<site name="hookc" pos="0 0 0"/>{tongue}{lidf}</body></body>'''
    elif grabber=='F1':
        F=GG.F_FLOAT; Mo=GG.F_MOUNT; T=GG.F_TONGUE
        hg=hook_geoms(GG.F_PIECES,'hk',fr=mu_hook)
        tl=(T['x1']-T['x0'])/2000; tcx=(T['x0']+T['x1'])/2000; tcz=(T['z0']+T['z1'])/2000
        tg_=''.join(f'<geom name="tongue{k}" type="box" pos="{tcx:.4f} {sg*(T["y"][0]+T["y"][1])/2000:.4f} {tcz:.4f}" size="{tl:.4f} {(T["y"][1]-T["y"][0])/2000:.4f} {(T["z1"]-T["z0"])/2000:.4f}" contype="6" conaffinity="4" friction="0.2" rgba="1 0.45 0.1 1" mass="0"/>' for k,sg in enumerate((1,-1)))
        tongue=f'''<body name="tongue" pos="0 0 0"><joint name="tongue" type="slide" axis="1 0 0" range="0 {T['retract']/1000}" solreflimit="0.004 1" stiffness="{T['k']}" springref="{-T['pre']/T['k']:.4f}" damping="20" {'frictionloss="4000"' if tongue_jam else 'frictionloss="1"'}/>
<inertial mass="0.1" pos="{tcx} 0 {tcz}" diaginertia="0.0005 0.0001 0.0005"/>{tg_}</body>'''
        carriage=f'''<body name="carriage" pos="0 0 {F['rest']:.4f}"><joint name="float" type="slide" axis="0 0 1" range="{-F['down']} 0" stiffness="{F['k']}" springref="{F['springref']}" damping="150" frictionloss="15"/>{inert(*ca)}
<body name="cradle" pos="{EHm:.4f} 0 0"><joint name="mx" type="slide" axis="1 0 0" range="{-Mo['travel']} {Mo['travel']}" stiffness="{Mo['k']}" damping="{Mo['c']}"/>
<joint name="mz" type="slide" axis="0 0 1" range="{-Mo['travel']} {Mo['travel']}" stiffness="{Mo['k']}" damping="{Mo['c']}"/>
<inertial mass="0.8" pos="0 0 0" diaginertia="0.005 0.002 0.005"/>
{hg}
<site name="hookc" pos="0 0 0"/>{tongue}</body></body>'''
    elif grabber=='GH':
        carriage=gh_carriage(GHV,gh,ca,mu_hook,pawl_jam,lat=lat)
    else:   # F1eq: Rev F.1 idealised latch (equality connect), used for traction/mass tests
        carriage=f'''<body name="carriage" pos="0 0 {S_TOP/1000:.4f}"><joint name="float" type="slide" axis="0 0 1" range="{(S_BOT-S_TOP)/1000:.3f} 0" stiffness="200" springref="0.3" damping="150" frictionloss="15"/>{inert(*ca)}
<site name="hookL" pos="{EHm:.4f} 0.19 0"/><site name="hookR" pos="{EHm:.4f} -0.19 0"/><site name="hookc" pos="{EHm:.4f} 0 0"/></body>'''
    # ---- bin
    bh=bar_h if bar_h is not None else HZ0/1000; bx=bar_x if bar_x is not None else HX0/1000
    if bar_shape=='tube': bar=f'<geom name="bar" type="capsule" fromto="{bx:.4f} {-handle_half:.4f} {bh:.4f} {bx:.4f} {handle_half:.4f} {bh:.4f}" size="{bar_r:.4f}" contype="0" conaffinity="4" friction="{mu_hook}" mass="0" rgba="0.1 0.35 0.2 1"/>'
    else: bar=f'<geom name="bar" type="box" pos="{bx:.4f} 0 {bh:.4f}" size="{bar_r*0.8:.4f} {handle_half:.4f} {bar_r:.4f}" contype="0" conaffinity="4" friction="{mu_hook}" mass="0" rgba="0.1 0.35 0.2 1"/>'
    wx0=xbt-0.01; wx1=bx+0.01
    webs=''.join(f'<geom name="web{k}" type="box" pos="{(wx0+wx1)/2:.4f} {sg*(handle_half+0.01):.4f} {bh-0.012:.4f}" size="{(wx1-wx0)/2:.4f} 0.01 0.035" contype="0" conaffinity="4" mass="0"/>' for k,sg in enumerate((1,-1)))
    for k,(yc,ht) in enumerate(BM.get('knuckles',[])):     # inner hinge knuckles / webs on the bar (y centre, half thickness), mirrored
        for j,sg in enumerate((1,-1)):
            webs+=f'<geom name="knk{k}{j}" type="box" pos="{(wx0+wx1)/2:.4f} {sg*yc:.4f} {bh-0.004:.4f}" size="{(wx1-wx0)/2:.4f} {ht:.4f} {bar_r+0.006:.4f}" contype="0" conaffinity="4" mass="0"/>' 
    lstate,lang=lid
    lo={'closed':0.0,'ajar':lang,'open':lang,'hanging':4.55}[lstate]; lhi=4.60
    lid_xml=f'''<body name="lid" pos="{lid_x:.4f} 0 {lid_z:.4f}"><joint name="lid" type="hinge" axis="0 1 0" range="{lo:.3f} {lhi}" damping="0.3"/>
<inertial mass="{lidm}" pos="{-lid_hl:.3f} 0 0.02" diaginertia="0.05 0.09 0.13"/>
<geom name="lid" type="box" pos="{-lid_hl:.4f} 0 0.015" size="{lid_hl:.4f} {lid_hw:.4f} 0.015" contype="0" conaffinity="12" friction="0.4" mass="0" rgba="0.15 0.45 0.25 0.6"/>
<site name="lidtip" pos="{-2*lid_hl:.4f} 0 0.03"/></body>'''
    binb=''
    if with_bin:
        binb=f'''<body name="bin" pos="{bp[0]:.4f} {bp[1]:.4f} {wheel_r}" euler="0 0 {bp[2]}"><freejoint name="binfree"/>{inert(mb,cb,Ib)}
<geom name="binhull" type="mesh" mesh="hull" contype="0" conaffinity="3" mass="0" friction="{mf_feet}"/>
{bar}{webs}
<site name="handleL" pos="{bx} 0.19 {bh}"/><site name="handleR" pos="{bx} -0.19 {bh}"/><site name="handlec" pos="{bx} 0 {bh}"/>
{binwheel('L',1)}{binwheel('R',-1)}{lid_xml}</body>'''
    ph0=math.radians(phi0)
    eq=''
    if grabber=='F1eq' and with_bin:
        eq=f'''<equality><connect name="latchL" active="false" body1="carriage" body2="bin" anchor="{EHm:.4f} 0.19 0" solref="{hook_tc} 1"/>
<connect name="latchR" active="false" body1="carriage" body2="bin" anchor="{EHm:.4f} -0.19 0" solref="{hook_tc} 1"/></equality>'''
    acts=f'''<velocity name="mL" joint="axleL" kv="{kv}" forcerange="-60 60"/><velocity name="mR" joint="axleR" kv="{kv}" forcerange="-60 60"/>
<position name="act" joint="tilt" kp="{act_kp}" kv="3000" forcerange="-{lim:.0f} {lim:.0f}"/>
<position name="yawlock" joint="yaw" kp="20000" kv="800" forcerange="-600 600"/>
<motor name="floatf" joint="float" gear="1" ctrllimited="true" ctrlrange="-400 400"/>'''
    if grabber in ('G','F1'): acts+='<motor name="cam" joint="tongue" gear="1" ctrllimited="true" ctrlrange="0 120"/>'
    if grabber=='G': acts+='<motor name="lfm" joint="lidfinger" gear="1" ctrllimited="true" ctrlrange="0 12"/>'
    if grabber=='GH': acts+='<motor name="camL" joint="pawlL" gear="1" ctrllimited="true" ctrlrange="0 3"/><motor name="camR" joint="pawlR" gear="1" ctrllimited="true" ctrlrange="0 3"/>'
    xml=f'''<mujoco model="bin_tug_revG"><compiler angle="degree"/>
<option timestep="{float(os.environ.get('SIM_DT','0.0005'))}" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic" noslip_iterations="3"/>
<default><geom solref="0.008 1" solimp="0.9 0.99 0.002"/></default>
<asset><mesh name="hull" vertex="{hv}"/></asset>
<worldbody>{ground}
<body name="tug" pos="{tp[0]:.4f} {tp[1]:.4f} 0" euler="0 0 {tp[2]}"><freejoint name="tugfree"/>{inert(*ch)}{tg}
{drive('L',1)}{drive('R',-1)}{caster('L',1)}{caster('R',-1)}
<body name="rear" pos="0 0 {KZm:.4f}"><joint name="yaw" type="hinge" axis="0 0 1" range="-{yaw_range} {yaw_range}" damping="5"/>{inert(*re)}{rg}
<body name="mast" pos="{piv[0]:.4f} 0 {piv[2]-KZm:.4f}"><joint name="tilt" type="hinge" axis="0 1 0" range="-18 80" damping="400" ref="0"/>{inert(*ma)}
{carriage}{mast_lidfinger() if (grabber=='GH' and lidfinger) else ''}</body></body></body>
{binb}</worldbody>
{eq}
<contact>{'<exclude body1="lidfinger" body2="tongue"/>' if grabber=='G' else ''}{funnel_pairs() if with_bin else ''}<exclude body1="tug" body2="cwheelL"/><exclude body1="tug" body2="cwheelR"/><exclude body1="tug" body2="cforkL"/><exclude body1="tug" body2="cforkR"/></contact>
<actuator>{acts}</actuator></mujoco>'''
    return xml,tug_mass,(mb+1.4+lidm if with_bin else 0)
def dock_xml(x0=0.0,y0=0.0,yaw=0.0,shoe_k=1500.0,shoe_pre=8.0,post_y=0.25,post_r=0.055,rails=True):
    """charging dock in world: contact plane (front faces of the two posts) at x0; dock axis along +x (tug reverses in towards -x).
    Posts stand where a bin's wheels would; three sprung shoes (+, pilot, -) between them face the tug's crossbeam strips."""
    c,s=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
    def P(x,y): return (x0+c*x-s*y, y0+s*x+c*y)
    out=[]
    for k,sg in enumerate((1,-1)):
        px,py=P(-post_r,sg*post_y)
        out.append(f'<geom name="dpost{k}" type="cylinder" pos="{px:.4f} {py:.4f} 0.10" size="{post_r} 0.10" friction="0.3" contype="1" conaffinity="1" rgba="0.2 0.2 0.2 1"/>')
    # back block holding the shoes
    bx,by=P(-0.09,0)
    out.append(f'<geom name="dblock" type="box" pos="{bx:.4f} {by:.4f} 0.11" size="0.035 0.17 0.05" euler="0 0 {yaw}" contype="1" conaffinity="1" rgba="0.9 0.9 0.85 1"/>')
    for k,(sy,prot,w) in enumerate(((0.10,0.015,0.02),(0.0,0.010,0.015),(-0.10,0.015,0.02))):
        sx,syy=P(-0.055+prot,sy)
        out.append(f'''<body name="shoe{k}" pos="{sx:.4f} {syy:.4f} 0.11" euler="0 0 {yaw}"><joint name="shoe{k}" type="slide" axis="1 0 0" range="-0.022 0" stiffness="{shoe_k}" springref="{shoe_pre/shoe_k:.4f}" damping="10"/>
<inertial mass="0.05" pos="0 0 0" diaginertia="1e-5 1e-5 1e-5"/><geom name="shoeg{k}" type="box" size="0.006 {w} 0.012" friction="0.3" contype="1" conaffinity="1" rgba="0.85 0.6 0.2 1"/></body>''')
    if rails:   # V-guide kerbs for the drive wheels: 1.2 m long, converge from +/-0.62 to +/-0.43 over the first 0.6 m
        for k,sg in enumerate((1,-1)):
            for j,(a,b) in enumerate((((0.40,0.43),(1.00,0.43)),((1.00,0.43),(1.55,0.62)))):
                (xa,ya),(xb,yb)=a,b; ya*=sg; yb*=sg
                mx,my=P((xa+xb)/2,(ya+yb)/2); L=math.hypot(xb-xa,yb-ya); ang=math.degrees(math.atan2(yb-ya,xb-xa))+yaw
                out.append(f'<geom name="rail{k}{j}" type="box" pos="{mx:.4f} {my:.4f} 0.035" size="{L/2:.4f} 0.02 0.035" euler="0 0 {ang:.2f}" friction="0.25" contype="1" conaffinity="1" rgba="0.55 0.4 0.25 1"/>')
    return '\n'.join(out)
class Sim:
    def __init__(s,**kw):
        xml,s.tug_mass,s.bin_mass=build_xml(**kw); s.xml=xml; s.m=mujoco.MjModel.from_xml_string(xml); s.d=mujoco.MjData(s.m)
        s.kw=kw; s.act_force=kw.get('act_force',2500); s.grabber=kw.get('grabber','G'); s.with_bin=kw.get('with_bin',True)
        G=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_GEOM,n)
        names=['driveL','driveR','casterL','casterR','stopbar','armL','armR','flareL','flareR','antitipL','antitipR','pod','deckrear','spine','bumper']
        if s.with_bin: names+=['binwheelL','binwheelR','binhull','bar','lid']
        s.gid={n:G(n) for n in names}
        s.hook_g=set(i for i in range(s.m.ngeom) if (mujoco.mj_id2name(s.m,mujoco.mjtObj.mjOBJ_GEOM,i) or '').startswith(('hk','tongue','lidf','pw')))
        s.tongue_g=set(i for i in range(s.m.ngeom) if (mujoco.mj_id2name(s.m,mujoco.mjtObj.mjOBJ_GEOM,i) or '').startswith(('tongue','pw')))
        s.shoe_g=[G(f'shoeg{k}') for k in range(3)] if kw.get('dock') else []
        B=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_BODY,n)
        bl=['tug','rear','mast','carriage','wheelL','wheelR','cwheelL','cwheelR','cforkL','cforkR']
        if s.grabber in('G','F1'): bl+=['cradle','tongue']
        if s.grabber=='G': bl+=['lidfinger']
        if s.grabber=='GH': bl+=['cradle','lat','pawlL','pawlR']+(['lidfinger'] if kw.get('lidfinger',True) else [])
        if s.with_bin: bl+=['bin','bwL','bwR','lid']
        s.bid={n:B(n) for n in bl}
        S=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_SITE,n)
        s.sid={n:S(n) for n in (('hookc','handlec','handleL','handleR') if s.with_bin else ('hookc',))}
        s.jq=lambda n:s.m.jnt_qposadr[mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_JOINT,n)]
        s.jv=lambda n:s.m.jnt_dofadr[mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_JOINT,n)]
        s.aid=lambda n:mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_ACTUATOR,n)
        s.d.qpos[s.jq('tilt')]=math.radians(kw.get('phi0',8.0)); s.d.ctrl[2]=math.radians(kw.get('phi0',8.0))
        if s.with_bin and kw.get('lid',('closed',0))[0] in ('ajar','open'): s.d.qpos[s.jq('lid')]=kw['lid'][1]
        if s.with_bin and kw.get('lid',('closed',0))[0]=='hanging': s.d.qpos[s.jq('lid')]=4.58
        if s.grabber=='F1eq' and s.with_bin:
            bx=kw.get('bar_x') or HX0/1000; bh=kw.get('bar_h') or HZ0/1000
            for k,sy in enumerate((0.19,-0.19)): s.m.eq_data[k][3:6]=[bx,sy,bh]
        s.kv=kw.get('kv',150); s.cam_state=0; s.cam_ok=not kw.get('cam_fail',False); s.float_pull=0.0
        mujoco.mj_forward(s.m,s.d)
        s.float_mass=float(s.m.body_subtreemass[s.bid['carriage']])
        s.net_up=GG.G_FLOAT['net_up'] if s.grabber=='G' else 0.0
        if s.grabber=='GH':
            s.GHV=dict(GG.GH[kw.get('gh','B1')]); s.GHV.update(kw.get('ghp') or {})
            s.net_up=s.GHV.get('net_up',0.0) if s.GHV['mode']=='below' else s.GHV.get('preload',25.0)
            s.cam_state=2 if s.GHV['mode']=='below' else 0
            s.ratchet_on=s.GHV.get('ratchet',False)
        if kw.get('rest_stop'): s.rest_cfg=kw['rest_stop']
    def set_grade(s,gx=0.0,gy=0.0):
        a=math.atan(gx); b=math.atan(gy)
        s.m.opt.gravity[:]=9.81*np.array([-math.sin(a)*math.cos(b),-math.cos(a)*math.sin(b),-math.cos(a)*math.cos(b)])
    def pre_step(s):
        """G: counterbalance spring on the float (cancels carriage weight along the mast, leaves net_up); release cam states
        0 latched / 1 tongue retracted / 2 tongue retracted + ratchet lifted + cord pulls the hook down; ratchet = one-way float stop.
        F1: cam_state>=1 = solenoid pulls the tongue back."""
        a=s.aid('floatf'); d=s.d; m=s.m
        if s.grabber=='G':
            zm=d.xmat[s.bid['carriage']].reshape(3,3)[:,2]; g=float(zm@m.opt.gravity)
            pull=(GG.G_FLOAT['pull'] if s.cam_state==2 and s.cam_ok else 0.0)+s.float_pull
            d.ctrl[a]=-s.float_mass*g+s.net_up-pull
            j=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,'float'); q=float(d.qpos[m.jnt_qposadr[j]]); P=GG.G_FLOAT['pitch']; lo=-GG.G_FLOAT['down']
            d.ctrl[s.aid('lfm')]=9.0 if (s.cam_state>=1 and s.cam_ok) else 0.0      # cam cord also lifts the lid finger clear (to its 2.6 rad stop)
            if s.cam_state==2 and s.cam_ok: m.jnt_range[j][0]=lo
            else:
                notch=lo+math.floor((q-lo)/P+1e-6)*P
                if notch>m.jnt_range[j][0]+1e-9: m.jnt_range[j][0]=notch
        elif s.grabber=='GH':
            V=s.GHV; zm=d.xmat[s.bid['carriage']].reshape(3,3)[:,2]; g=float(zm@m.opt.gravity)
            j=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,'float'); q=float(d.qpos[m.jnt_qposadr[j]]); lo=-V['float_down']
            if V['mode']=='below':
                pull=(V['pull'] if s.cam_state==2 and s.cam_ok else 0.0)+s.float_pull
                d.ctrl[a]=-s.float_mass*g+s.net_up-pull
                if s.ratchet_on:
                    if s.cam_state==2 and s.cam_ok: m.jnt_range[j][0]=lo
                    else:
                        P=V['pitch']; notch=lo+math.floor((q-lo)/P+1e-6)*P
                        if notch>m.jnt_range[j][0]+1e-9: m.jnt_range[j][0]=notch
                tq=1.5 if (s.cam_state>=1 and s.cam_ok) else 0.0
            else:
                d.ctrl[a]=-s.float_mass*g+V.get('kc',500.0)*(V.get('rest',0.004)-q)-s.float_pull   # spring-balanced, centred at 'rest'
                tq=1.5 if (s.cam_state>=1 and s.cam_ok) else 0.0
            d.ctrl[s.aid('camL')]=tq if not getattr(s,'cam_fail_L',False) else 0.0
            d.ctrl[s.aid('camR')]=tq
        elif s.grabber=='F1': d.ctrl[a]=-s.float_pull
        else: d.ctrl[a]=0.0
        if s.grabber in ('G','F1'): d.ctrl[s.aid('cam')]=40.0 if (s.cam_state>=1 and s.cam_ok) else 0.0
    # ---- F1eq latch
    def latch(s,on=True,capture=True):
        if on and capture:
            Rb=s.d.xmat[s.bid['bin']].reshape(3,3); xb=s.d.xpos[s.bid['bin']]
            for k,n in enumerate(('hookL','hookR')):
                sid=mujoco.mj_name2id(s.m,mujoco.mjtObj.mjOBJ_SITE,n); s.m.eq_data[k][3:6]=Rb.T@(s.d.site_xpos[sid]-xb)
        s.d.eq_active[0]=on; s.d.eq_active[1]=on
    def latch_soft(s,soft):
        for k in (0,1): s.m.eq_solref[k]=[0.06 if soft else s.kw.get('hook_tc',0.004),1]
    def yaw_lock(s,on):
        kp,kv=(20000,800) if on else (0,0)
        s.m.actuator_gainprm[3][0]=kp; s.m.actuator_biasprm[3][1]=-kp; s.m.actuator_biasprm[3][2]=-kv; s.d.ctrl[3]=0
    def yaw_rel(s): return math.degrees(s.d.qpos[s.jq('yaw')])
    def set_brake(s,on):
        kv=20000 if on else s.kv
        for a in (0,1): s.m.actuator_gainprm[a][0]=kv; s.m.actuator_biasprm[a][2]=-kv
    def update_act_limit(s):
        lev,L=act_lever(s.d.qpos[s.jq('tilt')]); lim=s.act_force*lev
        s.m.actuator_forcerange[2]=[-lim,lim]; return lev,L
    # ---- grabber state
    def bar_in_hook(s):
        """bar centre in the cradle frame (mm)"""
        b=s.d.geom_xpos[s.gid['bar']]; c=s.d.xpos[s.bid['cradle']]; R=s.d.xmat[s.bid['cradle']].reshape(3,3)
        return R.T@(b-c)*1000
    def tongue_mm(s): return float(s.d.qpos[s.jq('tongue')])*1000
    def bar_at_hooks(s):
        """bar centreline position (mm, cradle frame) at each hook plane y=+/-hy"""
        b=s.d.geom_xpos[s.gid['bar']]; c=s.d.xpos[s.bid['cradle']]; R=s.d.xmat[s.bid['cradle']].reshape(3,3)
        a=R.T@s.d.xmat[s.bid['bin']].reshape(3,3)[:,1]; p=R.T@(b-c)*1000; out=[]
        for yk in (s.GHV['hy'],-s.GHV['hy']):
            t=(yk-p[1])/a[1] if abs(a[1])>1e-6 else 0.0; out.append(p+a*t)
        return out
    def pawl_deg(s):
        return (-math.degrees(float(s.d.qpos[s.jq('pawlL')])),-math.degrees(float(s.d.qpos[s.jq('pawlR')])))
    def captured(s):
        """truth: bar inside the cup with the tongue over it"""
        if s.grabber=='GH':
            p=s.bar_in_hook(); r=s.kw.get('bar_r',0.016)*1000; hh=s.kw.get('handle_half',0.27)*1000
            th=float(s.GHV.get('throat',-24.0)); ztop=float(s.GHV.get('truth_ztop',40.0))
            inside=all((th<q[0]<24) and (-26-3<q[2]-r) and (q[2]+r<ztop) for q in s.bar_at_hooks())
            lat=abs(p[1])+s.GHV['hy']+5<hh
            kn=(s.kw.get('binm') or {}).get('knuckles',[])
            if kn: lat=lat and (s.GHV['hy']-5-abs(p[1])>max(yc+ht for yc,ht in kn)*1000)
            pl,pr=s.pawl_deg()
            return bool(inside and lat and pl>-12 and pr>-12)
        if s.grabber not in ('G','F1'): return bool(s.d.eq_active[0])
        p=s.bar_in_hook(); r=s.kw.get('bar_r',0.016)*1000
        if s.grabber=='G': x0,x1,z0,z1=-28,26,-24,20
        else: x0,x1,z0,z1=-17,17,-16,18
        lateral_ok=abs(p[1])<300
        return bool(x0<p[0]<x1 and z0-2<p[2]<z1+2 and s.tongue_mm()<10 and lateral_ok)
    def sensors(s,strict=False):
        """(seat, latch) switch states as the real switches would read them"""
        p=s.bar_in_hook(); r=s.kw.get('bar_r',0.016)*1000
        if s.grabber=='GH':
            V=GG.GH_VANE; rr=(r if s.kw.get('bar_shape','tube')=='tube' else 0.8*r)
            seat=any(bool(q[0]+rr>V['xback']-(0 if strict else 4) and V['zmin']<q[2]<V['zmax']) for q in s.bar_at_hooks()) and abs(p[1])<200   # one vane per hook, wired in parallel
            pl,pr=s.pawl_deg(); return seat,bool(pl>-3 and pr>-3)
        if s.grabber=='G':
            V=GG.G_VANE; xr=p[0]+(r if s.kw.get('bar_shape','tube')=='tube' else 0.8*r); seat=bool(xr>V['xback']-(0 if strict else 6) and V['zmin']<p[2]<V['zmax'] and abs(p[1])<200)
            latch=s.tongue_mm()<4
        else:   # F.1 roller seat switch on the cup floor: bar within 4 mm of the floor, over the switch (|x|<10, near a hook)
            seat=bool(abs(p[0])<10 and (p[2]-r)-(-16)<4 and abs(p[1])<260)
            latch=s.tongue_mm()<5
        return seat,latch
    def contacts(s):
        """normal-force sums per tracked geom, plus hook (bar-cradle) and tongue loads as force vectors (N)"""
        out={k:0.0 for k in s.gid}; f=np.zeros(6); hook=np.zeros(3); tng=np.zeros(3); shoes=[0.0,0.0,0.0]
        bar=s.gid.get('bar',-9)
        for i in range(s.d.ncon):
            c=s.d.contact[i]; mujoco.mj_contactForce(s.m,s.d,i,f)
            for k,g in s.gid.items():
                if c.geom1==g or c.geom2==g: out[k]+=f[0]
            if bar in (c.geom1,c.geom2):
                other=c.geom2 if c.geom1==bar else c.geom1
                if other in s.hook_g:
                    F=c.frame.reshape(3,3).T@f[:3]
                    hook+=F if c.geom1==bar else -F
                    if other in s.tongue_g: tng+=F if c.geom1==bar else -F
            sb=s.gid['stopbar']
            if s.with_bin and sb in (c.geom1,c.geom2):
                o2=c.geom2 if c.geom1==sb else c.geom1
                if o2==s.gid['binwheelL']: out['stopL']=out.get('stopL',0)+f[0]
                if o2==s.gid['binwheelR']: out['stopR']=out.get('stopR',0)+f[0]
            for k,g in enumerate(s.shoe_g):
                if g in (c.geom1,c.geom2): shoes[k]+=f[0]
        out['hookF']=float(np.linalg.norm(hook)); out['tongueF']=float(np.linalg.norm(tng)); out['shoes']=shoes
        return out
    def hook_eq(s):
        F=np.zeros(2)
        for i in range(s.d.nefc):
            if s.d.efc_type[i]==mujoco.mjtConstraint.mjCNSTR_EQUALITY and s.d.efc_id[i]<2: F[s.d.efc_id[i]]+=s.d.efc_force[i]**2
        return float(np.sqrt(F).sum())
    def rpy(s,b='tug'):
        R=s.d.xmat[s.bid[b]].reshape(3,3); return math.degrees(math.atan2(R[2,1],R[2,2])),math.degrees(math.asin(max(-1,min(1,-R[2,0])))),math.degrees(math.atan2(R[1,0],R[0,0]))
    def bin_tilt_rel(s):
        Rb=s.d.xmat[s.bid['bin']].reshape(3,3); Rt=s.d.xmat[s.bid['tug']].reshape(3,3); R=Rt.T@Rb; return math.degrees(math.atan2(R[0,2],R[2,2]))
    def bin_tilt_abs(s):
        R=s.d.xmat[s.bid['bin']].reshape(3,3); return math.degrees(math.acos(max(-1,min(1,R[2,2]))))
    def bin_yaw_rel(s):
        Rb=s.d.xmat[s.bid['bin']].reshape(3,3); Rt=s.d.xmat[s.bid['tug']].reshape(3,3); R=Rt.T@Rb; return math.degrees(math.atan2(R[1,0],R[0,0]))
    def fwd_speed(s):
        R=s.d.xmat[s.bid['tug']].reshape(3,3); a=s.jv('tugfree'); return float(R[:,0]@s.d.qvel[a:a+3])
    def tilt(s): return math.degrees(s.d.qpos[s.jq('tilt')])
    def snapshot(s):
        return {k:(s.d.xpos[b].tolist(),s.d.xmat[b].tolist()) for k,b in s.bid.items()}
