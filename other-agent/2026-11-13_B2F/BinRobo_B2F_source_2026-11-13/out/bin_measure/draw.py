import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
BG='#e8e8ea'; INK='#1d1d1f'; ACC='#ff4d00'; SKY='#b1bcd2'; SAGE='#607868'; CLAY='#dbb691'; DUSK='#a79fb8'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
# geometry (mm): x forward (front wall +), y left/right, z up. Front wall near x=0.
H=1000.0   # rim / comb top height
Wt,Wb=580,470   # body width top/bottom
Dt=700; Db=560
ftap=35  # front wall taper
xf_top=0; xf_bot=-ftap
xr_top=-Dt; xr_bot=xf_bot-Db
zb=40
def box_faces(xf0,xf1,xr0,xr1,w0,w1,z0,z1):
    # bottom ring (z0) and top ring (z1)
    b=[(xf0,-w0/2,z0),(xf0,w0/2,z0),(xr0,w0/2,z0),(xr0,-w0/2,z0)]
    t=[(xf1,-w1/2,z1),(xf1,w1/2,z1),(xr1,w1/2,z1),(xr1,-w1/2,z1)]
    f=[b,t]
    for i in range(4):
        j=(i+1)%4; f.append([b[i],b[j],t[j],t[i]])
    return f
def cyl(cx,cy,cz,r,w,axis='y',n=24):
    a=np.linspace(0,2*np.pi,n,endpoint=False); fs=[]
    p0=[(cx+r*np.cos(t),cy-w/2,cz+r*np.sin(t)) for t in a]
    p1=[(cx+r*np.cos(t),cy+w/2,cz+r*np.sin(t)) for t in a]
    fs+= [p0,p1]
    for i in range(n):
        j=(i+1)%n; fs.append([p0[i],p0[j],p1[j],p1[i]])
    return fs
def barx(x0,x1,y0,y1,z0,z1):
    return box_faces(x0,x0,x1,x1,y1-y0,y1-y0,z0,z1)
def bin_parts():
    P=[]
    P.append(('body',box_faces(xf_bot,xf_top,xr_bot,xr_top,Wb,Wt,zb,H-30),'#9aa3a0'))
    # top rim band
    P.append(('rim',box_faces(10,10,-Dt-10,-Dt-10,Wt+20,Wt+20,H-30,H),'#8a9390'))
    # lid
    P.append(('lid',box_faces(25,25,-Dt-15,-Dt-15,Wt+30,Wt+30,H,H+45),'#7d8784'))
    # frontal receiver (comb lip) on front wall, just below rim
    P.append(('rec',box_faces(45,45,5,5,Wt,Wt,H-60,H-25),ACC))
    # handle bar at rear, above rim
    hx=-Dt-60
    P.append(('handle',box_faces(hx+15,hx+15,hx-15,hx-15,Wt+10,Wt+10,H+40,H+70),'#5a6360'))
    for s in (-1,1):
        P.append(('brk',box_faces(-Dt+5,-Dt+5,hx,hx,20,20,H-20,H+55),'#5a6360'))
    # wheels at rear
    ax=xr_bot-20; 
    for s in (-1,1):
        P.append(('wheel',cyl(ax,s*(Wb/2+40),100,100,45),'#3a3f3e'))
    P.append(('axle',cyl(ax,0,100,12,Wb+120),'#3a3f3e'))
    return P
def shift(faces,dy):
    return faces
def fix_brk(P):
    out=[]
    for name,f,c in P:
        if name=='brk':
            pass
        out.append((name,f,c))
    return out
LAB=[]
P=bin_parts()
# place brackets at two y positions
newP=[];k=0
for name,f,c in P:
    if name=='brk':
        s=-1 if k==0 else 1; k+=1
        f=[[(x,y+s*(Wt/2-40),z) for (x,y,z) in face] for face in f]
    newP.append((name,f,c))
P=newP
def draw3d(ax,elev,azim,title,labels):
    for name,f,c in P:
        pc=Poly3DCollection(f,facecolor=c,edgecolor='#2a2d2c',linewidths=0.4,alpha=1.0 if name!='body' else 0.92)
        ax.add_collection3d(pc)
    ax.set_xlim(-850,250); ax.set_ylim(-550,550); ax.set_zlim(0,1150)
    ax.set_box_aspect((1100,1100,1150))
    ax.view_init(elev=elev,azim=azim); ax.set_axis_off()
    ax.set_title(title,fontsize=11,color=INK,pad=0)
    LAB.append((ax,labels))
lab_front=[((45,0,H-45),(0.80,0.62),'M1-M3  receiver (comb lip)',ACC),((-18,-150,550),(0.80,0.30),'M4  front wall set-back',INK),((25,150,H+40),(0.70,0.88),'M11  lid overhang at front',INK),((-300,-Wt/2,800),(0.0,0.72),'M12  body width',INK)]
lab_rear=[((-Dt-60,0,H+55),(0.12,0.88),'M6  handle bar (height, dia., gap)',INK),((xr_bot-20,Wb/2+62,100),(0.02,0.06),'M7  wheels (dia., track, axle)',INK),((-Dt+5,Wt/2-40,H),(0.80,0.80),'hinge + brackets',INK),((-300,Wt/2,500),(0.85,0.40),'M8  base depth',INK)]
fig=plt.figure(figsize=(16,11),facecolor=BG)
ax1=fig.add_subplot(2,2,1,projection='3d',facecolor=BG); draw3d(ax1,22,-35,'Isometric A - FRONT (lifting lip side) and left',lab_front)
ax2=fig.add_subplot(2,2,2,projection='3d',facecolor=BG); draw3d(ax2,22,145,'Isometric B - REAR (handle, hinge, wheels) and right',lab_rear)
# side elevation 2D
ax3=fig.add_subplot(2,2,3,facecolor=BG); ax3.set_aspect('equal'); ax3.axis('off')
def poly(ax,pts,fc,ec='#2a2d2c',lw=0.8): ax.add_patch(plt.Polygon(pts,closed=True,fc=fc,ec=ec,lw=lw))
poly(ax3,[(xf_bot,zb),(xf_top,H-30),(xr_top,H-30),(xr_bot,zb)],'#9aa3a0')
poly(ax3,[(10,H-30),(10,H),(-Dt-10,H),(-Dt-10,H-30)],'#8a9390')
poly(ax3,[(25,H),(25,H+45),(-Dt-15,H+45),(-Dt-15,H)],'#7d8784')
poly(ax3,[(5,H-60),(45,H-60),(45,H-25),(5,H-25)],ACC)
hx=-Dt-60; ax3.plot([-Dt+5,hx,hx],[H-20,H-20,H+55],color='#5a6360',lw=4); ax3.add_patch(plt.Circle((hx,H+55),16,fc='#5a6360',ec=INK))
ax3.add_patch(plt.Circle((xr_bot-20,100),100,fc='#3a3f3e',ec=INK)); ax3.add_patch(plt.Circle((xr_bot-20,100),12,fc='white'))
ax3.plot([-900,250],[0,0],color=INK,lw=1.2)
def dim(ax,p0,p1,txt,off,col=INK,vert=True):
    if vert:
        x=off; ax.annotate('',xy=(x,p0),xytext=(x,p1),arrowprops=dict(arrowstyle='<->',color=col,lw=1))
        ax.text(x+12,(p0+p1)/2,txt,color=col,fontsize=9,va='center',fontweight='bold')
    else:
        y=off; ax.annotate('',xy=(p0,y),xytext=(p1,y),arrowprops=dict(arrowstyle='<->',color=col,lw=1))
        ax.text((p0+p1)/2,y+15,txt,color=col,fontsize=9,ha='center',fontweight='bold')
dim(ax3,0,H-25,'M1 lip top\nheight\n(EN 840:\n860-1030)',140,ACC)
dim(ax3,0,H+45,'M5a\noverall\nheight',480)
dim(ax3,0,H+70,'',-930)
ax3.text(-1020,(H+70)/2,'M6a handle\ntop height',fontsize=9,fontweight='bold',ha='right',va='center')
dim(ax3,0,200,'',xr_bot-150)
ax3.text(xr_bot-165,100,'M7a wheel\ndiameter',fontsize=9,fontweight='bold',ha='right',va='center')
dim(ax3,xr_bot-20,-ftap,'',-45,INK,vert=False)
ax3.text((xr_bot-ftap)/2,-95,'M8 axle centre to front wall at base',fontsize=9,fontweight='bold',ha='center')
ax3.plot([0,0],[H-500-30,H-25],ls='--',color=INK,lw=0.6); ax3.plot([-ftap,-ftap],[zb,H-500+30],ls='--',color=INK,lw=0.6)
ax3.annotate('M4 front-wall set-back\nfrom lip face, measured\n450-550 mm below the lip\n(where the pad touches)',xy=(-20,H-500),xytext=(-560,560),fontsize=9,fontweight='bold',color=INK,bbox=dict(boxstyle='round,pad=0.25',fc='white',ec=INK,lw=0.8),arrowprops=dict(arrowstyle='-|>',color=INK))
dim(ax3,-Dt-80,45,'M5b overall depth incl. handle & lip',H+150,INK,vert=False)
ax3.text(-Dt+20,H+60,'hinge',fontsize=8); ax3.text(-120,H+60,'lid',fontsize=8)
ax3.text(-Dt-40,-160,'REAR (handle)',fontsize=10,ha='center');ax3.text(0,-160,'FRONT (lip)',fontsize=10,ha='center',color=ACC)
ax3.set_xlim(-1150,680); ax3.set_ylim(-200,1280)
ax3.set_title('Side elevation (handle at left, lifting lip at right)',fontsize=11,color=INK)
# front elevation
ax4=fig.add_subplot(2,2,4,facecolor=BG); ax4.set_aspect('equal'); ax4.axis('off')
poly(ax4,[(-Wb/2,zb),(Wb/2,zb),(Wt/2,H-30),(-Wt/2,H-30)],'#9aa3a0')
poly(ax4,[(-Wt/2-10,H-30),(Wt/2+10,H-30),(Wt/2+10,H),(-Wt/2-10,H)],'#8a9390')
poly(ax4,[(-Wt/2-15,H),(Wt/2+15,H),(Wt/2+15,H+45),(-Wt/2-15,H+45)],'#7d8784')
poly(ax4,[(-Wt/2,H-60),(Wt/2,H-60),(Wt/2,H-25),(-Wt/2,H-25)],ACC)
for xr in np.arange(-Wt/2+20,Wt/2,90): ax4.plot([xr,xr],[H-60,H-25],color=INK,lw=0.7)
for s in (-1,1): poly(ax4,[(s*(Wb/2+18),0),(s*(Wb/2+62),0),(s*(Wb/2+62),200),(s*(Wb/2+18),200)],'#3a3f3e')
ax4.plot([-450,450],[0,0],color=INK,lw=1.2)
dim(ax4,-Wt/2,Wt/2,'M2 receiver width (580 typ. 240 L)',H+90,ACC,vert=False)
dim(ax4,-Wt/2-10,Wt/2+10,'M12a body width at lip height',H-170,INK,vert=False)
dim(ax4,-Wb/2,Wb/2,'M12b body width 500 mm up',520,INK,vert=False)
dim(ax4,-(Wb/2+62),(Wb/2+62),'M7b wheel track, outside',-60,INK,vert=False)
ax4.text(Wt/2+30,H-45,'M3c rib pitch\n(ribs in lip)',fontsize=9,fontweight='bold',color=ACC,va='center')
ax4.set_xlim(-560,700); ax4.set_ylim(-130,1230)
ax4.set_title('Front elevation (the face the robot docks against)',fontsize=11,color=INK)
fig.suptitle('Wheelie bin: what to measure (M1-M12)  -  orange = EN 840 frontal receiver (comb lip)',fontsize=14,color=INK,y=0.985)
fig.text(0.5,0.008,'Illustrative 240 L 2-wheel bin, proportions from the Craemer MGB 240 / SULO Citybac 240 drawings. Not to scale for any one maker. Measure every bin you own (140 L and 240 L).',ha='center',fontsize=9,color='#666')
plt.subplots_adjust(left=0.01,right=0.99,top=0.95,bottom=0.03,wspace=0.02,hspace=0.08)
fig.canvas.draw()
from mpl_toolkits.mplot3d import proj3d
OV={}
for ax,labels in LAB:
    for (p,(fx,fy),t,col) in labels:
        x2,y2,_=proj3d.proj_transform(p[0],p[1],p[2],ax.get_proj())
        if id(ax) not in OV:
            o=fig.add_axes(ax.get_position(),facecolor='none'); o.set_xlim(0,1); o.set_ylim(0,1); o.set_axis_off(); OV[id(ax)]=o
        ov=OV[id(ax)]
        dx,dy=ax.transData.transform((x2,y2)); ox,oy=ov.transAxes.inverted().transform((dx,dy))
        ov.annotate(t,xy=(ox,oy),xycoords='axes fraction',xytext=(fx,fy),textcoords='axes fraction',color=col,fontsize=10,fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.25',fc='white',ec=col,lw=0.8),arrowprops=dict(arrowstyle='-|>',color=col,lw=1),zorder=50)
fig.savefig('bin_measure_views.png',dpi=130,facecolor=BG)
