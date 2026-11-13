import json,pickle,struct,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__))
M=json.load(open(os.path.join(H,'rec_B2F.json'))); P=pickle.load(open(os.path.join(H,'B2F_parts.pkl'),'rb'))
def qmat(q):
    w,x,y,z=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
d=np.load(os.path.join(H,'rec_B2F.npz')); q=d['q'][M['frames']['carrying']]; B=M['bodies']; Rt=qmat(q[0,3:]); pt=q[0,:3]
POSE={n:(Rt.T@qmat(q[k,3:]),Rt.T@(q[k,:3]-pt)) for k,n in enumerate(B)}
INST={'wheel':['wheelL','wheelR'],'cfork':['cforkL','cforkR'],'cwheel':['cwheelL','cwheelR'],'bw':['bwL','bwR']}
# z-up (CAD) -> y-up (glTF): (x,y,z)->(x,z,-y)
C=np.array([[1,0,0],[0,0,1],[0,-1,0]],np.float32)
bin_=bytearray(); views=[]; acc=[]; meshes=[]; nodes=[]; mats=[]; matidx={}; meta=[]
def addview(b,target):
    global bin_
    while len(bin_)%4: bin_+=b'\0'
    off=len(bin_); bin_+=b; views.append(dict(buffer=0,byteOffset=off,byteLength=len(b),target=target)); return len(views)-1
used={}
for p in P:
    g=p['grp']
    for b in INST.get(g,[g]):
        R,t=POSE[b]; V=(p['V']@R.T+t)@C.T; V=V.astype(np.float32); c=V.mean(0) if len(V) else np.zeros(3,np.float32)
        nm=p['name']+('' if b==g else ' '+b[-1]); k=used.get(nm,0); used[nm]=k+1; nm=nm if k==0 else f'{nm} #{k+1}'
        L=(V-c).astype(np.float32); T=p['T'].astype(np.uint32).ravel()
        col=tuple(round(float(x),3) for x in p['col'][:3])
        if col not in matidx: matidx[col]=len(mats); mats.append(dict(pbrMetallicRoughness=dict(baseColorFactor=[*col,1.0],metallicFactor=0.3,roughnessFactor=0.6)))
        va=addview(L.tobytes(),34962); ia=addview(T.tobytes(),34963)
        acc.append(dict(bufferView=va,componentType=5126,count=len(L),type='VEC3',min=L.min(0).tolist(),max=L.max(0).tolist())); ai=len(acc)-1
        acc.append(dict(bufferView=ia,componentType=5125,count=len(T),type='SCALAR')); ii=len(acc)-1
        meshes.append(dict(name=nm,primitives=[dict(attributes=dict(POSITION=ai),indices=ii,material=matidx[col])]))
        code=nm.split(' ')[0]
        nodes.append(dict(name=nm,mesh=len(meshes)-1,translation=c.tolist(),extras=dict(group=g,code=code,with_bin_only=g in('bin','bw','lid'))))
        meta.append(dict(node=nm,group=g,code=code,centroid_m=[round(float(x),3) for x in c]))
while len(bin_)%4: bin_+=b'\0'
gl=dict(asset=dict(version='2.0',generator='BinRobo cad_B2F -> glb_B2F.py'),scene=0,scenes=[dict(name='BinRobo B2-F carrying 240 L',nodes=list(range(len(nodes))))],
        nodes=nodes,meshes=meshes,materials=mats,accessors=acc,bufferViews=views,buffers=[dict(byteLength=len(bin_))])
js=json.dumps(gl,separators=(',',':')).encode();
while len(js)%4: js+=b' '
glb=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(bin_))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(bin_),0x004E4942)+bytes(bin_)
o='/workspace/work/out/b2f_cutaway/BinRobo_B2F.glb'; open(o,'wb').write(glb)
json.dump(meta,open('/workspace/work/out/b2f_cutaway/parts_nodes.json','w'),indent=0)
print(len(nodes),'nodes',len(glb)/1e6,'MB')
