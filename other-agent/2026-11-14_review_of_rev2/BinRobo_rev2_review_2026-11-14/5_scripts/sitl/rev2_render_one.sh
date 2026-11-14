#!/bin/bash
# usage: rev2_render_one.sh <runs_dir> <key> <out.mp4> [subtitle]   (one heavy process, niced; post-processing only)
cd "$(dirname "$0")"; export PYTHONPATH=/workspace/work/pylib
[ -n "$4" ] && export REV2_SUB="$4"
[ -s "$3" ] && { echo "exists $3"; exit 0; }
timeout -s INT 112 nice -n 10 python3 b2f_video_rev2.py scenario "$1" "$2" "$3.tmp.mp4" && mv "$3.tmp.mp4" "$3" && echo "OK $3 $(du -h "$3"|cut -f1)"
