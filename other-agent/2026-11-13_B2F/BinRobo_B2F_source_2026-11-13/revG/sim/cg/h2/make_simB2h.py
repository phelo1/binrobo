#!/usr/bin/env python3
"""Generates h2/simB2h.py from the live b2/simB2.py (which stays untouched). Every edit is a checked string replacement.
simB2h = B2 exactly, plus:
  H2_HULL=new|old (default new): bin hull from h2/hull_h2.py (S1) or the gate block unchanged.
  B2_DOCK=handle|front (default handle):
     handle = B2 as designed (docks on the handle side; on the NEW hull its comb meets the plain rim + handle brackets).
     front  = B2-F: B2 turned round to dock on the front wall (frontal receiver). Changes, and only these:
              bin frame mirrored (front at +x, as cmp/simH.py); sprung pad re-set for the front wall (pad_in, B2F_PAD_IN,
              default 0.015 m = same 5.5 mm nominal pad-to-wall gap as B2 on its own hull); the handle-bar keeper cannot reach
              the bar on the far side, so it is not fitted (keeper geoms inert, claim = load rise + seat switch + pad lock).
  H2_KEEPER=1 (S5 only): rim keeper bar (see h2/keeper_h2.py) instead of the B2 handle keeper."""
import os
H=os.path.dirname(os.path.abspath(__file__)); src=open(os.path.join(H,'..','b2','simB2.py')).read()
def rep(a,b,n=1):
    global src; c=src.count(a); assert c==n,(a[:80],c); src=src.replace(a,b)
rep("HERE=os.path.dirname(os.path.abspath(__file__)); G6=os.path.join(HERE,'..','..','g6')",
    "HERE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','b2'); G6=os.path.join(HERE,'..','..','g6')\n"
    "sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import hull_h2 as HH\n"
    "HULL=HH.HULL(); DOCK=os.environ.get('B2_DOCK','handle'); KEEPER2=os.environ.get('H2_KEEPER')=='1'")
# pad re-set for the front wall (B2-F only)
rep("GEO.update(json.loads(os.environ.get('CGB_GEO','{}'))); GEO['lift_range']=0.25",
    "if DOCK=='front': GEO['pad_in']=float(os.environ.get('B2F_PAD_IN','0.015'))   # [B2-F] sprung pad re-set for the front wall\n"
    "GEO.update(json.loads(os.environ.get('CGB_GEO','{}'))); GEO['lift_range']=0.25")
# bin params: lip position / height / width for the chosen hull and side
rep("    if CMP_LIP=='en840': p['lip_w']=EN840_RW[binkey]+float(p.get('comb_d',0.0))*0.0   # receiver runs the full EN 840 width\n    return p",
    "    if CMP_LIP=='en840': p['lip_w']=EN840_RW[binkey]+float(p.get('comb_d',0.0))*0.0   # receiver runs the full EN 840 width\n"
    "    p['comb_abs']=comb; p['xlip']=p['bar_x']-p['cb']\n"
    "    if HULL=='new':\n"
    "        g=HH.geom_params(binkey,p)\n"
    "        if DOCK=='front': p['xlip']=-g['xf']; p['zL_abs']=g['zL_front']+p['wheel_r']; p['lip_w']=g['lw']\n"
    "        else: p['zL_abs']=g['zL_rear']+p['wheel_r']; p['lip_w']=g['W']-0.06\n"
    "    elif DOCK=='front': raise SystemExit('B2_DOCK=front needs H2_HULL=new')\n"
    "    return p")
# bin block
a=src.find("    binb=''; bm=0.0\n    if with_bin:"); b=src.find("    else: asset=''",a); assert a>0 and b>a
old_block=src[a:b]
new_block=("    binb=''; bm=0.0\n    if with_bin and HULL=='new':\n"
           "        asset,binb,bm,_info=HH.bin_xml(binkey,p,DOCK,mu,fr,(crr_bin if crr_bin is not None else crr),p.get('mu_hook',0.35),box_I,inert)\n"
           "    elif with_bin:"+old_block.split("    if with_bin:",1)[1])
src=src[:a]+new_block+src[b:]
# keeper inert for B2-F (cannot reach the bar)
rep('contype="4" conaffinity="0" friction="0.2" mass="0" rgba="0.9 0.9 0.2 1"/>\n<geom name="keeptip2" type="cylinder" pos="{-G[\'keep_l\']:.4f} -0.10 0" size="0.012 0.025" euler="90 0 0" contype="4"',
    'contype="{0 if DOCK==\'front\' else 4}" conaffinity="0" friction="0.2" mass="0" rgba="0.9 0.9 0.2 1"/>\n<geom name="keeptip2" type="cylinder" pos="{-G[\'keep_l\']:.4f} -0.10 0" size="0.012 0.025" euler="90 0 0" contype="{0 if DOCK==\'front\' else 4}"')
# rim keeper option (S5)
rep("{comb_close}\n<body name=\"keeper\"","{HH.keeper_xml(G,cx0) if KEEPER2 else ''}{comb_close}\n<body name=\"keeper\"")
rep("<position name=\"padact\" joint=\"padext\" kp=\"100000\" kv=\"3000\" forcerange=\"-1500 1500\"/></actuator></mujoco>'''",
    "<position name=\"padact\" joint=\"padext\" kp=\"100000\" kv=\"3000\" forcerange=\"-1500 1500\"/>{HH.keeper_act() if KEEPER2 else ''}</actuator></mujoco>'''")
rep("        s.keeper_cmd=6.0; s.d.qpos[s.jq('keeper')]=1.4\n","        s.keeper_cmd=6.0; s.d.qpos[s.jq('keeper')]=1.4\n        if KEEPER2: HH.keeper_init(s)\n")
# geom names: lower hull, keeper bar
rep("        if s.with_bin: names+=['binwheelL','binwheelR','binhull','bar','ledge','rim','lid']\n        s.gid={n:Gd(n) for n in names}",
    "        if s.with_bin: names+=['binwheelL','binwheelR','binhull','bar','ledge','rim','lid','binhull_lo','hrim','fledge','frim']\n        names+=['kbar']\n        s.gid={n:Gd(n) for n in names}; HH.apply_overrides(s)")
rep("    def pair(s,a,b):\n        ga,gb=s.gid.get(a,-9),s.gid.get(b,-9); return s._pairs.get((min(ga,gb),max(ga,gb)),0.0)",
    "    def pair(s,a,b):\n        ga,gb=s.gid.get(a,-9),s.gid.get(b,-9)\n        if ga<0 or gb<0: return 0.0\n        v=s._pairs.get((min(ga,gb),max(ga,gb)),0.0)\n"
    "        if 'binhull' in (a,b) and HULL=='new': o=b if a=='binhull' else a; v+=s.pair('binhull_lo',o)\n        return v")
# lip x in the bin frame (generalised; identical to bar_x - cb on the old hull)
rep("q=s.nib_in_bin(); P=s.p; xbt=P['bar_x']-P['cb']; zL","q=s.nib_in_bin(); P=s.p; xbt=P['xlip']; zL")
rep("    xbt=p['bar_x']-p['cb']; nibx=GEO['face_x']-GEO['tooth_len']","    xbt=p['xlip']; nibx=GEO['face_x']-GEO['tooth_len']")
rep("    xbt=S.p['bar_x']-S.p['cb']; b0=S.d.xpos","    xbt=S.p['xlip']; b0=S.d.xpos")
rep("    P=S.p; xbt=P['bar_x']-P['cb']; zL=P['zL_abs']-P['wheel_r']","    P=S.p; xbt=P['xlip']; zL=P['zL_abs']-P['wheel_r']")
rep("    xbt=S.p['bar_x']-S.p['cb']\n    def nib_gap(): return","    xbt=S.p['xlip']\n    def nib_gap(): return")
rep("    q=S.nib_in_bin(); xbt=S.p['bar_x']-S.p['cb']\n","    q=S.nib_in_bin(); xbt=S.p['xlip']\n",2)
# claim: B2-F has no handle keeper; optional rim keeper (S5)
rep("    ss=seat_sw(); keep_ok=S.pair('keeptip','bar')>5 or S.pair('keeptip2','bar')>5",
    "    ss=seat_sw(); keep_ok=S.pair('keeptip','bar')>5 or S.pair('keeptip2','bar')>5\n"
    "    if DOCK=='front': keep_ok=True   # [B2-F] no handle keeper on the far side\n"
    "    if KEEPER2: HH.keeper_close(S,R)")
rep("R.phase='3x No claim: keeper open, pad retract, comb down, back off'; S.keeper_cmd=6.0;",
    "R.phase='3x No claim: keeper open, pad retract, comb down, back off'; S.keeper_cmd=6.0; HH.keeper_open(S) if KEEPER2 else None;")
rep("R.phase='11 SD2: keeper opens, pad retracts, comb to 25 mm under the rim'; S.keeper_cmd=6.0;",
    "R.phase='11 SD2: keeper opens, pad retracts, comb to 25 mm under the rim'; S.keeper_cmd=6.0; HH.keeper_open(S) if KEEPER2 else None;")
src='# GENERATED by h2/make_simB2h.py from b2/simB2.py - do not edit by hand\n'+src
open(os.path.join(H,'simB2h.py'),'w').write(src); print('wrote simB2h.py',len(src))
