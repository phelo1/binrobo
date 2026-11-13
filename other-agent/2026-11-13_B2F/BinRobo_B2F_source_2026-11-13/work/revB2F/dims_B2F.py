"""Overall dimensions of B2-F from the posed CAD meshes (B2F_parts.pkl + rec_B2F.npz), tug frame, mm -> dims_B2F.json"""
import json, numpy as np, scene as SC
d=np.load('rec_B2F.npz'); M=json.load(open('rec_B2F.json')); FR=M['frames']; G=M['geo']
def rel(i):
    P=SC.frame_poses(d['q'][i]); Rt,pt=P['tug']; return {k:(Rt.T@R,Rt.T@(p-pt)) for k,(R,p) in P.items()}
def env(T): V=T.reshape(-1,3)*1000; return V.min(0).round(0).tolist(),V.max(0).round(0).tolist()
out={}
T,_,_=SC.posed(rel(FR['start']),with_bin=False); out['robot_no_bin']=env(T)
T,_,_=SC.posed(rel(FR['start']),with_bin=False,skip=('beacon','GNSS')); out['robot_no_bin_excl_beacon_gnss']=env(T)
Pc=rel(FR['carrying']); T,_,_=SC.posed(Pc,with_bin=True); out['carrying']=env(T)
T,_,_=SC.posed(Pc,with_bin=True,only=('BIN',)); out['bin_only_carrying']=env(T)
out['comb_nib_top_range_mm']=[round(1000*G['car_zero']),round(1000*(G['car_zero']+G['lift_range']))]
out['lift_q_carry_mm']=round(1000*M['lift_q']); out['nib_top_carry_mm']=round(1000*(G['car_zero']+M['lift_q']))
Rb,pb=Pc['bin']; out['bin_axle_carry']=[round(1000*v) for v in pb]; out['bin_wheel_clear_mm']=M['grab']['wheel_clear_mm']; out['bin_tilt_deg']=M['grab']['bin_tilt_abs']
# which way is the bin facing: bin +x (front wall/receiver) in the tug frame
out['bin_front_dir_in_tug']=[round(v,3) for v in Rb[:,0]]
HG=M['hull']; fx=Rb@np.array([-HG['xf'],0,HG['zL_front']])+pb; hx=Rb@np.array([-HG['bx'],0,HG['bh']])+pb
out['receiver_ledge_in_tug_mm']=[round(1000*v) for v in fx]; out['handle_bar_in_tug_mm']=[round(1000*v) for v in hx]
Rp,pp=Pc['pad']; out['pad_face_centre_in_tug_mm']=[round(1000*v) for v in pp]
zp=Rb.T@(pp-pb)
import sys; sys.path.insert(0,'/workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg/h2'); import hull_h2 as HH
out['pad_in_bin_frame_mm']=[round(1000*v,1) for v in zp]; out['front_wall_x_at_pad_height_bin_mm']=round(-1000*HH.front_x(HG,zp[2]),1)
out['track_mm']=round(2000*G['track']); out['wheelbase_axle_to_castor_mm']=round(1000*G['cx'])
json.dump(out,open('dims_B2F.json','w'),indent=1,default=float); print(json.dumps(out,indent=1,default=float))
