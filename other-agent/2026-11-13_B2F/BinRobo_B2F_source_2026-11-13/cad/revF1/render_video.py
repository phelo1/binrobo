# Renders MuJoCo pose recordings into MP4 using the CAD meshes (software painter's renderer, no OpenGL).
import json, math, pickle, subprocess, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from model_revF import TX, PX, PZ, KZ, S_TOP, ACT_BASE, ACT_S, ACT_E, ACT_Y
from sim_revF import MAST
TXm,PXm,PZm,KZm=TX/1000,PX/1000,PZ/1000,KZ/1000
D=json.load(open('mesh_revF.json'))['dock']['mesh']
def body_of(p):
    n=p['name']; y=p['cen'][1]
    if p['g']=='bin':
        if n=='Bin wheel': return 'bwL' if y>0 else 'bwR'
        return 'bin'
    if n.startswith('Tilt actuator'): return None
    if n.startswith(('Drive wheel','Wheel hub')): return 'wheelL' if y>0 else 'wheelR'
    if n.startswith('Caster 200'): return 'cwheelL' if y>0 else 'cwheelR'
    if n.startswith('Caster fork'): return 'cforkL' if y>0 else 'cforkR'
    if p['mod']=='Grabber': return 'carriage'
    if n.startswith(MAST): return 'mast'
    if p['mod']=='Rear frame': return 'rear'
    return 'tug'
REF={'tug':(TXm,0,0),'wheelL':(TXm,0.345,0.165),'wheelR':(TXm,-0.345,0.165),'cwheelL':(TXm+0.69,0.2,0.1),'cwheelR':(TXm+0.69,-0.2,0.1),
     'cforkL':(TXm+0.74,0.2,0.1),'cforkR':(TXm+0.74,-0.2,0.1),'rear':(TXm,0,KZm),'mast':(PXm,0,PZm),'carriage':(PXm,0,PZm+S_TOP/1000),'bin':(0,0,0.1),'bwL':(0,0.27,0.1),'bwR':(0,-0.27,0.1)}
# Rev F.1 geometry changes applied to the Rev F CAD meshes (mm offsets in the model frame): rollers up 30 mm, ballast forward 138 mm,
# caster outriggers forward 100 mm (caster forks/wheels follow their simulated bodies).
TWEAK={'Anti-tip roller':(0,0,30),'Ballast plate':(138,0,0),'Caster outrigger':(100,0,0)}
G={}
for p in D:
    b=body_of(p)
    if b is None or len(p['T'])==0: continue
    off=next((np.array(v,float)/1000 for k,v in TWEAK.items() if p['name'].startswith(k)),np.zeros(3))
    V=np.array(p['V'])/1000+off-np.array(REF[b]); T=np.array(p['T'])
    g=G.setdefault(b,dict(tri=[],col=[],a=[]))
    g['tri'].append(V[T]); g['col'].append(np.tile(p['c'],(len(T),1))); g['a'].append(np.full(len(T),p['a']))
for b,g in G.items(): g['tri']=np.concatenate(g['tri']); g['col']=np.concatenate(g['col']); g['a']=np.concatenate(g['a'])
def prism(p,q,r,n=8):
    p=np.array(p);q=np.array(q);d=q-p;L=np.linalg.norm(d);d/=L
    a=np.cross(d,[0,0,1.0]); 
    if np.linalg.norm(a)<1e-6: a=np.array([1.0,0,0])
    a/=np.linalg.norm(a); b=np.cross(d,a); tris=[]
    ang=np.linspace(0,2*np.pi,n+1)
    ring=[a*math.cos(t)*r+b*math.sin(t)*r for t in ang]
    for i in range(n):
        p0,p1,q0,q1=p+ring[i],p+ring[i+1],q+ring[i],q+ring[i+1]; tris+= [[p0,p1,q1],[p0,q1,q0]]
    return np.array(tris)
def grav_rot(g):
    g=np.array(g,float); a=math.atan(g[0]); b=math.atan(g[1])
    gs=np.array([-math.sin(a)*math.cos(b),-math.cos(a)*math.sin(b),-math.cos(a)*math.cos(b)])
    t=np.array([0,0,-1.0]); v=np.cross(gs,t); s=np.linalg.norm(v); c=gs@t
    if s<1e-9: return np.eye(3)
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]); return np.eye(3)+K+K@K*((1-c)/s**2)
def iso(az,el):
    a,e=np.radians(az),np.radians(el);v=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
    r=np.cross([0,0,1.],v);r/=np.linalg.norm(r);return np.array([r,np.cross(v,r),v])
LIGHT=np.array([0.4,0.3,0.85]);LIGHT/=np.linalg.norm(LIGHT)
FOOT='Rev F.1 bin tug · MuJoCo 3.17 physics'
def render(rec, out, title, terrain=None, az=-58, el=22, span=2.6, speed_phases=('3','5','9'), speedup=4, fps=12, max_frames=None, tail_hold=12, boxes=(), cen_w=0.6, skip=1, speed_map=None):
    W,H=1280,720; fig=plt.figure(figsize=(W/100,H/100),dpi=100); ax=fig.add_axes([0,0,1,1])
    ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(fps),'-i','-',
                         '-c:v','libx264','-pix_fmt','yuv420p','-crf','23','-preset','veryfast',out],stdin=subprocess.PIPE)
    Rv=iso(az,el); frames=[]; k=0
    BX=[]
    for (cx,cy,cz,hx,hy,hz,colr) in boxes:   # static obstacles (hedge, wall) as shaded boxes
        V=np.array([[cx+sx*hx,cy+sy*hy,cz+sz*hz] for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)])
        F=[(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(0,2,6,4),(1,3,7,5)]
        tri=np.array([[V[a],V[b],V[c]] for (a,b,c,d) in F]+[[V[a],V[c],V[d]] for (a,b,c,d) in F])
        BX.append((tri,np.tile(colr,(len(tri),1)),np.ones(len(tri))))
    for i,r in enumerate(rec):
        if speed_map is not None:   # per-phase playback speed: {phase prefix: factor}, longest matching prefix wins, default skip
            k=max([p for p in speed_map if r['ph'].startswith(p)],key=len,default=None); stp=speed_map[k] if k else skip
        else: stp=speedup if r['ph'][:1] in speed_phases else skip
        if stp>1 and i%stp: continue
        frames.append((r,stp))
    if max_frames: frames=frames[:max_frames]
    frames+= [frames[-1]]*tail_hold
    cen_s=None
    for (r,stp) in frames:
        fast=stp>1; speedup=stp
        Q=grav_rot(r['g']); P=r['P']; polys=[];cols=[];dep=[]
        def add_tris(tri,col,a):
            tri=tri@Q.T; n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); n/=(np.linalg.norm(n,axis=1)[:,None]+1e-12)
            sh=0.45+0.55*np.abs(n@LIGHT); pr=tri@Rv.T
            polys.extend(pr[:,:,:2]); dep.extend(pr[:,:,2].mean(1)); c=np.clip(col*sh[:,None],0,1); cols.extend(np.c_[c,a])
        for b,g in G.items():
            pos=np.array(P[b][0]); R=np.array(P[b][1]).reshape(3,3)
            add_tris(g['tri']@R.T+pos,g['col'],g['a'])
        # actuator
        pt=np.array(P['rear'][0]);Rt=np.array(P['rear'][1]).reshape(3,3);pm=np.array(P['mast'][0]);Rm=np.array(P['mast'][1]).reshape(3,3)
        A=Rt@np.array([ACT_BASE[0]/1000-TXm,ACT_Y/1000,ACT_BASE[1]/1000-KZm])+pt; B=Rm@np.array([ACT_E/1000,ACT_Y/1000,ACT_S/1000])+pm
        mid=A+(B-A)*min(0.5/np.linalg.norm(B-A),0.95)
        t1=prism(A,mid,0.026); t2=prism(mid,B,0.010)
        add_tris(t1,np.tile([0.25,0.25,0.27],(len(t1),1)),np.ones(len(t1))); add_tris(t2,np.tile([0.85,0.85,0.87],(len(t2),1)),np.ones(len(t2)))
        for (tri,col,a) in BX: add_tris(tri,col,a)
        c=(np.array(P['tug'][0])*cen_w+np.array(P['bin'][0])*(1-cen_w))@Q.T
        cen_s=c if cen_s is None else cen_s*0.85+c*0.15
        ax.clear(); ax.set_facecolor('#dfe8ef')
        # ground grid (world z=0 plane, tilted for grade), 0.5 m squares
        gx0=math.floor((Q.T@cen_s)[0]/0.5)*0.5; gy0=math.floor((Q.T@cen_s)[1]/0.5)*0.5
        gp=[];gc=[]
        for ix in range(-9,10):
            for iy in range(-7,8):
                x0,y0=gx0+ix*0.5,gy0+iy*0.5; q=np.array([[x0,y0,0],[x0+0.5,y0,0],[x0+0.5,y0+0.5,0],[x0,y0+0.5,0]])@Q.T@Rv.T
                gp.append(q[:,:2]); gc.append('#b9cfa8' if (ix+iy)%2 else '#c4d8b3')
        ax.add_collection(PolyCollection(gp,facecolors=gc,edgecolors='#a3b893',linewidths=0.3))
        if terrain:
            for (x0,x1,y0,y1,z,colr) in terrain:
                q=np.array([[x0,y0,z],[x1,y0,z],[x1,y1,z],[x0,y1,z]])@Q.T@Rv.T; ax.add_collection(PolyCollection([q[:,:2]],facecolors=[colr],edgecolors='k',linewidths=0.5))
        o=np.argsort(dep)
        ax.add_collection(PolyCollection([polys[j] for j in o],facecolors=[cols[j] for j in o],edgecolors=[(0,0,0,0.06)]*len(o),linewidths=0.2))
        cc=cen_s@Rv.T; ax.set_xlim(cc[0]-span*W/H/2*1.0,cc[0]+span*W/H/2*1.0); ax.set_ylim(cc[1]-span/2*0.9,cc[1]+span/2*1.1); ax.set_aspect('equal'); ax.axis('off')
        ax.text(0.015,0.965,title,transform=ax.transAxes,fontsize=16,weight='bold',va='top',color='#1d2a33',bbox=dict(fc='white',ec='none',alpha=0.6,pad=3))
        ax.text(0.015,0.905,r['ph'],transform=ax.transAxes,fontsize=13,va='top',color='#0b5d8f',bbox=dict(fc='white',ec='none',alpha=0.6,pad=2))
        if 'hud' in r: hud=r['hud']
        else: hud=f"t = {r['t']:5.1f} s{'   (%dx speed)'%speedup if fast else ''}\nbin tilt {r['tilt']:5.1f}°   mast {r['mast']:5.1f}°\nhook load {r['hook']:4.0f} N   min caster load {r['cmin']:4.0f} N\nspeed {r['v']:4.2f} m/s   hitch {r.get('hitch',0):5.1f}°"
        if 'hud' not in r and any(abs(x)>1e-6 for x in r['g']): hud+=f"\ngrade {r['g'][0]*100:+.0f}%  side slope {r['g'][1]*100:.0f}%"
        ax.text(0.985,0.06,hud,transform=ax.transAxes,fontsize=11,va='bottom',ha='right',family='monospace',color='#1d2a33',
                bbox=dict(fc='white',ec='#9aa',alpha=0.85,pad=6))
        ax.text(0.985,0.02,FOOT,transform=ax.transAxes,fontsize=9,ha='right',color='#556')
        fig.canvas.draw(); ff.stdin.write(fig.canvas.buffer_rgba().tobytes())
    ff.stdin.close(); ff.wait(); plt.close(fig)
def title_card(out,lines,secs=3,fps=12):
    W,H=1280,720; fig=plt.figure(figsize=(W/100,H/100),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_facecolor('#1d2a33'); ax.axis('off')
    fig.patch.set_facecolor('#1d2a33')
    ax.text(0.5,0.62,lines[0],ha='center',va='center',fontsize=34,weight='bold',color='white',transform=ax.transAxes)
    for i,l in enumerate(lines[1:]): ax.text(0.5,0.48-i*0.075,l,ha='center',va='center',fontsize=17,color='#cfe3ee',transform=ax.transAxes)
    fig.canvas.draw(); buf=fig.canvas.buffer_rgba().tobytes(); plt.close(fig)
    ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s',f'{W}x{H}','-r',str(fps),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','23','-preset','veryfast',out],stdin=subprocess.PIPE)
    for _ in range(secs*fps): ff.stdin.write(buf)
    ff.stdin.close(); ff.wait()
