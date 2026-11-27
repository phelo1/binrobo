#!/bin/bash
# Offline: share of looks in which someone standing still ahead of a standing robot is a confirmed lane-watch object, by distance ahead of the nose.
# Six places on the lane (drop-off trace of r61_plainf), 0.3 m and 1.0 m from the far hedge; revision 6.0 rules (clean lidar), revision 6.1 (clean, level 1, level 2).
cd /home/claude/s0; RD=/home/claude/sitl_out/r61_plainf/runs/s1a__s7; OUT=r61/tables/walker_seen_final.jsonl; : > $OUT
LB1="drop=0.15,dark=0.3,burst=0.02,false=2,rag=0.10,sway=0.03,bram=0.02,bramd=0.2"
LB2="drop=0.3,dark=0.6,burst=0.1,false=6,rag=0.2,sway=0.08,bram=0.05,bramd=0.2"
for T in $(python3 - <<'PY'
import json
tr=json.load(open('/home/claude/sitl_out/r61_plainf/runs/s1a__s7/trace.json'))['trace']
for s0 in (100.0,192.1,297.5,380.0,453.7,540.0):
    c=[q for q in tr if q['state']=='LANE_DOWN_LOADED' and abs(q['s']-s0)<0.08]; print(c[0]['t'])
PY
); do for GAP in 0.3 1.0; do
  ( source r61/env_r61_fast.sh; export X_R6_PROUD=0 X_LID_FILTER=0; unset X_LID_BAD; echo "{\"set\":\"rev 6.0, clean\",\"r\":$(nice -n 19 python3 r61/harness.py walker $RD $T $GAP)}" >> $OUT )
  ( source r61/env_r61_fast.sh; unset X_LID_BAD; echo "{\"set\":\"rev 6.1, clean\",\"r\":$(nice -n 19 python3 r61/harness.py walker $RD $T $GAP)}" >> $OUT )
  ( source r61/env_r61_fast.sh; export X_LID_BAD="$LB1"; echo "{\"set\":\"rev 6.1, level 1\",\"r\":$(nice -n 19 python3 r61/harness.py walker $RD $T $GAP)}" >> $OUT )
  ( source r61/env_r61_fast.sh; export X_LID_BAD="$LB2"; echo "{\"set\":\"rev 6.1, level 2\",\"r\":$(nice -n 19 python3 r61/harness.py walker $RD $T $GAP)}" >> $OUT )
done; done
echo done >> r61/tables/walker_seen_final.done
