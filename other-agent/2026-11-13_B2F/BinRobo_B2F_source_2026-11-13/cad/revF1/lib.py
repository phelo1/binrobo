import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
def render(ax,R,M,flt=lambda m:True,explode=None,light=(0.4,0.3,0.85),recolor=None,lw=0.2):
    L=np.array(light,float);L/=np.linalg.norm(L);polys=[];cols=[];depth=[]
    for i,m in enumerate(M):
        if not flt(m): continue
        V=np.array(m['V']);T=np.array(m['T'])
        if len(T)==0: continue
        if explode is not None and i in explode: V=V+np.array(explode[i])
        tri=V[T];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=(np.linalg.norm(n,axis=1)[:,None]+1e-9)
        sh=0.45+0.55*np.abs(n@L);P=tri@R.T
        base=np.array(recolor(m) if recolor else m['c']);a=m['a']
        for k in range(len(T)):
            polys.append(P[k,:,:2]);depth.append(P[k,:,2].mean());cols.append((*np.clip(base*sh[k],0,1),a))
    o=np.argsort(depth)
    ax.add_collection(PolyCollection([polys[i] for i in o],facecolors=[cols[i] for i in o],edgecolors=[(0,0,0,0.08*cols[i][3]) for i in o],linewidths=lw))
    ax.autoscale();ax.set_aspect('equal');ax.axis('off')
SIDE=np.array([[1,0,0],[0,0,1],[0,-1,0]]);TOP=np.array([[1,0,0],[0,1,0],[0,0,1]]);REAR=np.array([[0,1,0],[0,0,1],[-1,0,0]])
def iso(az,el):
    a,e=np.radians(az),np.radians(el);v=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
    r=np.cross([0,0,1.],v);r/=np.linalg.norm(r);return np.array([r,np.cross(v,r),v])
def dim(ax,p,q,off,txt,vert=False,fs=7):
    p=np.array(p,float);q=np.array(q,float)
    if not vert:
        y=p[1]+off;ax.annotate('',(p[0],y),(q[0],y),arrowprops=dict(arrowstyle='<->',lw=0.7))
        ax.plot([p[0],p[0]],[p[1],y],lw=0.4,c='k');ax.plot([q[0],q[0]],[q[1],y],lw=0.4,c='k')
        ax.text((p[0]+q[0])/2,y+10,txt,ha='center',va='bottom',fontsize=fs,bbox=dict(fc='w',ec='none',pad=0.5))
    else:
        x=p[0]+off;ax.annotate('',(x,p[1]),(x,q[1]),arrowprops=dict(arrowstyle='<->',lw=0.7))
        ax.plot([p[0],x],[p[1],p[1]],lw=0.4,c='k');ax.plot([q[0],x],[q[1],q[1]],lw=0.4,c='k')
        ax.text(x+10,(p[1]+q[1])/2,txt,ha='left',va='center',fontsize=fs,rotation=90,bbox=dict(fc='w',ec='none',pad=0.5))
