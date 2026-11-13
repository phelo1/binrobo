#!/usr/bin/env python3
"""S1 hull check plots: corrected hull (NEW) and gate hull (OLD) side sections for each gate bin, overlaid on the scaled maker
drawing of the same family. Writes h2/fig/hull_<BIN>.png, h2/fig/hull_all.png and h2/res/hull_check.json."""
import os, sys, json, math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','..','g6'))
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
from bins_g5 import BINS
import hull_h2 as HH
DL=os.path.join(HERE,'..','..','..','..','web','downloads','g5bins')
# drawing, axle pixel, mm/px, rear on the left (all three)
DRW={'CRA':('craemer240_side.png',(212,828),1.25,'Craemer MGBneo 240 side elevation, 1.25 mm/px (200 mm wheel = 160 px)'),
     'WEB':('weber140_side_crop.png',(354,960),1.11,'Weber 140 side elevation, 1.11 mm/px (200 mm wheel = 180 px)'),
     'SULO':('sulods-3.png',(140,412),3.06,'SULO Citybac 240 data sheet p.3, 3.06 mm/px')}
FAMD={'WEB140':'WEB','ESE140CL':'WEB','ESE240SL':'CRA','ESE240SL250':'CRA','ESE240CL':'CRA'}
BL=['WEB140','ESE240SL','ESE240CL','ESE240SL250','ESE140CL']
def nominal_p(k):
    B=BINS[k]; sh,r,_=B['sections'][1] if len(B['sections'])>1 else B['sections'][0]
    kn=B['knuckles'] if B['knuckles']!='maybe' else [(0.045,0.005)]
    p=dict(bar_r=r,bar_shape=sh,bar_x=B['bar_x'][0],cb=B['cb'][0],bar_habs=B['bar_abs'][0],wheel_r=B['wheel']/2,handle_half=B['web'][0],knuckles=kn,
           wy=(B['track']-0.05)/2,W=B['W'],D=B['D'],empty=B['empty'],fill=0.0,lid=['closed',0.0],comb_d=0.0)
    p['bar_h']=p['bar_habs']-p['wheel_r']; p['comb_abs']=B['comb'] if B['comb'] else p['bar_habs']-0.02
    return p
def section(g):
    zt,zrt,zb=g['zt'],g['zrt'],g['zb']
    pts=[(HH.front_x(g,zt),zt),(HH.rear_x(g,zt),zt),(HH.rear_x(g,zrt),zrt),(g['xrec'],zrt),(g['xrec'],zb),(HH.front_x(g,zb),zb)]
    return pts
def draw(ax,k,fam):
    p=nominal_p(k); g=HH.geom_params(k,p); wr=p['wheel_r']
    fn,(ax0,az0),s,lab=DRW[fam]; im=Image.open(os.path.join(DL,fn)).convert('L'); W_,H_=im.size
    # front to the right: u = -x (mm); drawing u = (px-ax0)*s ; z(ground frame) = (az0-py)*s + wheel_r(drawing 100 mm)
    ext=[(0-ax0)*s,(W_-ax0)*s,(az0-H_)*s+100,(az0-0)*s+100]
    ax.imshow(np.asarray(im),cmap='gray',extent=ext,alpha=0.55,vmin=0,vmax=255)
    sec=section(g); u=[-1000*x for x,z in sec]+[-1000*sec[0][0]]; z=[1000*(zz+wr) for x,zz in sec]+[1000*(sec[0][1]+wr)]
    ax.plot(u,z,'-',color='tab:blue',lw=2,label='NEW hull (S1)')
    om=HH.old_mesh(p); o=[(x,zz) for x,y,zz in om if y>0]   # rear bottom, front bottom, rear top, front top
    rb,fb,rt,ft=o; ou=[-1000*v[0] for v in (ft,rt,rb,fb,ft)]; oz=[1000*(v[1]+wr) for v in (ft,rt,rb,fb,ft)]
    ax.plot(ou,oz,'--',color='tab:red',lw=1.6,label='OLD gate hull')
    # receiver, plain rim, bar, brackets, wheel
    xf=g['xf']; zF=g['zL_front']
    ax.add_patch(plt.Rectangle((-1000*xf,1000*(zF+wr)),30,8,color='green',label='EN 840 receiver (ledge+rim)'))
    ax.add_patch(plt.Rectangle((-1000*xf+22,1000*(zF+wr)-25),8,25,color='green'))
    ax.add_patch(plt.Rectangle((-1000*(g['xb']+0.020),1000*(g['zL_rear']+wr)),20,8,color='olive',label='plain rim (handle side)'))
    ax.add_patch(plt.Circle((-1000*p['bar_x'],1000*p['bar_habs']),1000*p['bar_r'],color='k',label='handle bar'))
    ax.add_patch(plt.Rectangle((-1000*(p['bar_x']+0.01),1000*(p['bar_h']-0.047+wr)),1000*(p['bar_x']-g['xb']+0.02),70,fill=False,ec='k',lw=0.8,label='handle bracket'))
    ax.add_patch(plt.Circle((0,1000*wr),1000*wr,fill=False,ec='purple',lw=1.2,label='bin wheel'))
    zp=zF-0.50; ax.plot([-1000*HH.front_x(g,zp)],[1000*(zp+wr)],'o',color='orange',label='Rev H2 pad height (comb - 0.50 m)')
    ax.set_xlim(-300,700); ax.set_ylim(-20,1150); ax.set_aspect('equal'); ax.grid(alpha=0.3)
    ax.set_title(f'{k} on {fam} drawing',fontsize=9); ax.set_xlabel('mm from axle, front ->',fontsize=7); ax.tick_params(labelsize=6)
    return dict(bin=k,drawing=lab,front_taper_new_mm=round(1000*g['tf'],1),front_taper_old_mm=round(170*p['D']/0.74,1),
                rear_draft_new_mm=round(1000*g['tr'],1),recess_wall_ahead_of_axle_mm=round(-1000*g['xrec'],1),recess_top_above_axle_mm=round(1000*g['zrt'],1),
                receiver_ledge_underside_abs_mm=round(1000*(zF+wr),1),receiver_width_mm=round(1000*g['lw']),plain_rim_underside_abs_mm=round(1000*(g['zL_rear']+wr),1),
                front_wall_setback_at_pad_mm=round(1000*(HH.front_x(g,zp)-xf),1),
                old_front_wall_setback_at_pad_mm=round(1000*((ft[0]+(fb[0]-ft[0])*(ft[1]-zp)/(ft[1]-fb[1]))-ft[0]),1))
if __name__=='__main__':
    out=[]; os.makedirs(os.path.join(HERE,'fig'),exist_ok=True)
    fig,axs=plt.subplots(1,5,figsize=(20,5.6))
    for ax,k in zip(axs,BL):
        out.append(draw(ax,k,FAMD[k]))
        f2,a2=plt.subplots(figsize=(6,6.6)); draw(a2,k,FAMD[k]); a2.legend(fontsize=6,loc='lower right'); f2.tight_layout(); f2.savefig(os.path.join(HERE,'fig','hull_%s.png'%k),dpi=110); plt.close(f2)
    # SULO cross-check on the ESE 240 SL hull
    f2,a2=plt.subplots(figsize=(6,6.6)); out.append(dict(draw(a2,'ESE240SL','SULO'),note='cross-check on SULO'))
    a2.legend(fontsize=6,loc='lower right'); f2.tight_layout(); f2.savefig(os.path.join(HERE,'fig','hull_ESE240SL_on_SULO.png'),dpi=110); plt.close(f2)
    axs[0].legend(fontsize=6,loc='lower right'); fig.tight_layout(); fig.savefig(os.path.join(HERE,'fig','hull_all.png'),dpi=90)
    json.dump(out,open(os.path.join(HERE,'res','hull_check.json'),'w'),indent=1)
    for o in out: print(o)
