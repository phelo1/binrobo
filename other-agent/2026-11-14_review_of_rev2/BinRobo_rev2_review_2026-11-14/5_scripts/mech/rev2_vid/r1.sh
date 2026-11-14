#!/bin/bash
# one render chunk of video $1 (shared lock: one heavy process at a time from this tester)
S=$(date +%s); exec 9>/tmp/qr2.lock; flock -w 20 9 || { echo LOCKED; exit 0; }
B=$((100 - $(date +%s) + S)); [ $B -lt 50 ] && { echo short; exit 0; }
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/work/rev2_vid
PYTHONPATH=/workspace/work/pylib timeout $((B+12)) python3 render_r2.py $1 $B 2>&1 | tail -3; date +%T
