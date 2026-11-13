import pickle,numpy as np,math,sys
rec=pickle.load(open(sys.argv[1],'rb')); st=int(sys.argv[2]) if len(sys.argv)>2 else 12
for r in rec[::st]:
  P=r['P']; tp=np.array(P['tug'][0]); Rt=np.array(P['tug'][1]).reshape(3,3); bp=np.array(P['bin'][0]); Rb=np.array(P['bin'][1]).reshape(3,3)
  print(r['t'],r['ph'][:28],'tug',tp[:2].round(2),round(math.degrees(math.atan2(Rt[1,0],Rt[0,0]))),'bin',bp.round(2),round(math.degrees(math.atan2(Rb[1,0],Rb[0,0]))),'tilt',round(math.degrees(math.acos(min(1,Rb[2,2])))), r.get('hud','').split('\n')[3] if 'hud' in r else '')
