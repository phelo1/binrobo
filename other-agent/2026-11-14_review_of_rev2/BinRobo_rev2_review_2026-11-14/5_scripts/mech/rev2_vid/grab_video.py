#!/usr/bin/env python3
"""[tester 2026-11-14] Pick-up video from a rec_r2_grab.py recording: B2-F CAD meshes (work/revB2F/scene.py) posed from the
recorded rev2 body poses, software rasteriser (raster.py, no OpenGL), PIL HUD, ffmpeg H.264 1280x720 25 fps. Chunked:
grab_video.py <stem> <speed> <title> <budget_s>   then  grab_video.py <stem> --final <out.mp4>"""
import os, sys, json, time, glob, subprocess, numpy as np
T0=time.time(); P='/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c'; sys.path.insert(0,P+'/work/revB2F')
import scene as SC, raster as RA
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1280,720,25; RW,RH=960,540
F=lambda n,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),n)
CAP='Digital twin simulation - not field footage. Revision 2 independent re-test (MuJoCo 4.0.1)'
stem=sys.argv[1]; HERE=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(HERE,'vid','grab_'+os.path.basename(stem)); os.makedirs(D,exist_ok=True)
if sys.argv[2]=='--final':
    segs=sorted(glob.glob(D+'/seg_*.mp4')); lst=D+'/list.txt'; open(lst,'w').write(''.join("file '%s'\n"%s for s in segs))
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',lst,'-c','copy','-movflags','+faststart',sys.argv[3]],check=True)
    print(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',sys.argv[3]],capture_output=True,text=True).stdout.strip(),'s',sys.argv[3]); sys.exit()
speed=float(sys.argv[2]); title=sys.argv[3]; budget=float(sys.argv[4])
d=np.load(stem+'.npz'); M=json.load(open(stem+'.json')); Q=d['q']; T=d['t']; PH=list(d['ph']); LF=d['lf']; res=M['result']
G0,G1=np.array([0.88,0.895,0.905]),np.array([0.80,0.82,0.84])
k_tug=0; k_bin=SC.BODIES.index('bin')
binp=Q[0,k_bin,:3].astype(float)
ground=SC.tiles(binp[0]-3.0,binp[0]+4.0,binp[1]-3.0,binp[1]+3.0,lambda x,y:0.0,G0,0,0.5,G1)
ok=res['result']=='success'
resline=('RESULT: picked up - captured, nib %.0f mm off-centre, bin wheels %.0f mm clear'%(abs(res.get('nib_y_mm',0)),res.get('wheel_clear_mm') or 0)) if ok else \
        ('RESULT: REFUSED (%s) - still > 25 mm off-centre after the re-approaches; bin left standing (safe, not collected)'%res['result'])
dys=res.get('dock_dys_mm') or []
sub=['ESE 240 L clip-lid bin, G1 Monte-Carlo trial i=%d of seed %d (gate set), revision 2 at 119.39 kg.'%(M['i'],M['seed']),
     'Docking attempts, sideways bin offset (mm): '+', '.join('%.0f'%x for x in dys if x is not None)+'  (lift allowed only within 25 mm)',
     'Replays the exact trial of runB2.py grab ESE240CL 30 203 (recorder rec_r2_grab.py, logging only).']
def card(lines,big):
    im=Image.new('RGB',(W,H),(14,20,30)); dr=ImageDraw.Draw(im); dr.text((80,180),CAP,font=F(26,True),fill=(255,210,80))
    dr.text((80,250),big,font=F(34,True),fill=(255,255,255)); y=330
    for l in lines: dr.text((80,y),l,font=F(21),fill=(200,210,225)); y+=36
    dr.text((80,H-70),'B2-F CAD meshes posed from the rev2 sim (rev2 detail parts not drawn)  |  simB2hx_r2m, MuJoCo 4.0.1  |  software rasteriser',font=F(16),fill=(140,150,165))
    return im
tcard=card(sub,title); ecard=card([resline[:110],resline[110:]] if len(resline)>110 else [resline],title)
ecard_d=ImageDraw.Draw(ecard); ecard_d.text((80,140),'Result (frozen G1 rule)',font=F(22,True),fill=(120,230,140) if ok else (255,170,90))
n=int((T[-1]-T[0])/speed*FPS); L=[('c',0)]*int(4*FPS)+[('s',T[0]+k*speed/FPS) for k in range(n)]+[('e',0)]*int(5*FPS)
stf=D+'/state.json'; st=json.load(open(stf)) if os.path.exists(stf) else dict(next=0,seg=0)
if st['next']>=len(L): print('DONE',len(L)); sys.exit()
seg=D+'/seg_%03d.mp4'%st['seg']
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','%dx%d'%(W,H),'-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',seg],stdin=subprocess.PIPE)
k=st['next']; n0=k
while k<len(L) and time.time()-T0<budget:
    kind,t=L[k]
    if kind=='c': im=tcard
    elif kind=='e': im=ecard
    else:
        i=int(np.clip(np.searchsorted(T,t),0,len(T)-1)); q=Q[i]; Pz=SC.frame_poses(q)
        tri,col,oid=SC.posed(Pz); Tr,Cr,Or=SC.cat((tri,col,oid),ground)
        tug=q[k_tug,:3].astype(float); tgt=0.5*(tug+binp)+np.array([0,0,0.45])
        eye=tgt+np.array([2.3,-3.3,1.9])
        img=RA.render(Tr,Cr,Or,tuple(eye),tuple(tgt),RW,RH,fov=40.0,ss=1,sh_ctr=tuple(tgt),sh_ext=7.0,bg=(0.86,0.91,0.97))
        im=Image.fromarray(img).resize((W,H),Image.LANCZOS); dr=ImageDraw.Draw(im)
        dr.rectangle([0,0,W,34],fill=(10,14,22)); dr.text((12,7),CAP,font=F(17,True),fill=(255,210,80))
        dr.rectangle([0,34,W,60],fill=(30,38,50)); dr.text((12,38),str(PH[i])[:110],font=F(15),fill=(220,225,230))
        dr.text((W-200,37),'TIME-LAPSE x%.1f'%speed if speed>1.01 else 'REAL TIME',font=F(16,True),fill=(120,220,255))
        dr.rounded_rectangle([8,66,20+dr.textlength(title,font=F(16,True)),92],6,fill=(10,14,22)); dr.text((14,69),title,font=F(16,True),fill=(255,255,255))
        dr.rectangle([0,H-60,W,H],fill=(20,26,36))
        dr.text((14,H-50),'SIM TIME %.1f s'%(t-T[0]),font=F(20,True),fill=(230,235,240)); dr.text((260,H-50),'LIFT ACTUATOR %4.0f N'%LF[i],font=F(20,True),fill=(230,235,240))
        dr.text((600,H-50),'bin ESE 240 L clip-lid, trial i=%d seed %d'%(M['i'],M['seed']),font=F(18),fill=(200,210,225))
    ff.stdin.write(np.asarray(im.convert('RGB')).tobytes()); k+=1
    if k in (n0+5,) or k%200==0: im.save(D+'/sample_%05d.jpg'%k,quality=85)
ff.stdin.close(); ff.wait(); st['next']=k; st['seg']+=1; json.dump(st,open(stf,'w'))
print('frames %d..%d of %d (%.2f s/frame)'%(n0,k,len(L),(time.time()-T0)/max(1,k-n0)))
