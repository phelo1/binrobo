import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import scen_g5, tilt_g6
orig=scen_g5.stand_up
def su(R):
    S=R.s; print('before stand_up: bin tilt rel %.1f abs %.1f bar %s captured %s'%(S.bin_tilt_rel(),S.bin_tilt_abs(),[round(v) for v in S.bar_in_hook()],S.captured()),flush=True)
    orig(R)
    print('after stand_up: bin tilt rel %.1f abs %.1f bar %s captured %s mast %.1f'%(S.bin_tilt_rel(),S.bin_tilt_abs(),[round(v) for v in S.bar_in_hook()],S.captured(),S.tilt()),flush=True)
scen_g5.stand_up=su
os.environ['G6_COMBO']=sys.argv[2] if len(sys.argv)>2 else 'H3'
o=tilt_g6.run(sys.argv[1],'LA36_12H'); print(o['release'],o['events'])
