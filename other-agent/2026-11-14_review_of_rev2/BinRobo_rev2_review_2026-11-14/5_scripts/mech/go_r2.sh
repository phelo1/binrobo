#!/bin/bash
# one <=100 s foreground chunk: gate queue (q_r2.txt) or, with arg "lane", the lane queue. Any other arg is ignored (call counter).
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg
if [ "$1" = lane ]; then flock -n /tmp/qr2.lock ../../../work/b2f_lanephys/r2_lane_q.sh 92 || echo LOCKED; exit 0; fi
flock -n /tmp/qr2.lock python3 h2/qchunk_imp.py h2/q_r2.txt 100 > /tmp/go_r2.out 2>&1 || echo LOCKED
sed 's/.*IT1_TAG=//' /tmp/go_r2.out | tail -4
