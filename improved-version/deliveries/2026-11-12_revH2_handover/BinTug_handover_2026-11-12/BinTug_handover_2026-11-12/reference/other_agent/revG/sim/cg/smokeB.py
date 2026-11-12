import sys,os,json,time; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import simB_cg as B
b=sys.argv[1]; fill=float(sys.argv[2]) if len(sys.argv)>2 else 0
p=B.bin_params(b); p['fill']=fill
S=B.SimB(b,p,mu=0.6,tug_pose=B.start_pose(p,float(os.environ.get('DY','0')),float(os.environ.get('DYAW','0'))))
R=B.RunnerB(S); t=time.time()
print('tug kg',round(S.tug_mass,1),'bin kg',round(S.bin_mass,1))
o=B.grab(R); print(json.dumps(o)); print(R.events)
S.contacts(); print('pad',round(S.contacts()['padg']),'lift F',round(S.lift_force()),'nib-ledge',round(S.pair('nib','ledge')),'rim',round(S.pair('nib','rim')),'drive',round(S.contacts()['driveL']+S.contacts()['driveR']),'cast',round(S.contacts()['casterL']+S.contacts()['casterR']),'tilt',round(S.bin_tilt_abs(),2),'clear',round(S.wheel_clear(),3),'nib',S.nib_in_bin().round(4).tolist(),'cpu',round(time.time()-t))
