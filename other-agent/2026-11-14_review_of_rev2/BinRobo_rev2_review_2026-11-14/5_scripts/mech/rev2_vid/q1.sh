#!/bin/bash
# one gate-queue chunk; waits for the lock and uses the remaining part of a ~112 s window
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg
S=$(date +%s)
exec 9>/tmp/qr2.lock
flock -w 70 9 || { echo LOCKED; exit 0; }
B=$((110 - $(date +%s) + S)); [ $B -lt 42 ] && { echo "short $B"; exit 0; }
python3 h2/qchunk_imp.py h2/${Q:-q_r2.txt} $B 2>&1 | sed 's/.*IT1_TAG=//' | tail -4
date +%T
