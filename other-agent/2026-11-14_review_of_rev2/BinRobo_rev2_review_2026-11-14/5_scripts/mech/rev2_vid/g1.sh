#!/bin/bash
S=$(date +%s); exec 9>/tmp/qr2.lock; flock -w 20 9 || { echo LOCKED; exit 0; }
B=$((98 - $(date +%s) + S)); cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/work/rev2_vid
PYTHONPATH=/workspace/work/pylib timeout $((B+15)) python3 grab_video.py "$1" "$2" "$3" $B 2>&1 | tail -3
