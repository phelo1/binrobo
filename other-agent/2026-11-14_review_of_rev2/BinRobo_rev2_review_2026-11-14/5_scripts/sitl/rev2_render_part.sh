#!/bin/bash
# usage: rev2_render_part.sh <runs_dir> <key> <out.mp4> <part> <nparts> [subtitle]
# renders frames part/nparts to out.partK.mp4 (timeout 95 s, niced); when all parts exist, concatenates (-c copy) to out.mp4.
cd "$(dirname "$0")"; export PYTHONPATH=/workspace/work/pylib
[ -n "$6" ] && export REV2_SUB="$6"
O="$3"; K=$4; N=$5; PO="${O%.mp4}.part$K.mp4"
if [ ! -s "$PO" ]; then
  timeout -s INT 95 nice -n 10 python3 b2f_video_rev2.py scenario "$1" "$2" "$PO.tmp.mp4" $K $N && mv "$PO.tmp.mp4" "$PO" && echo "part $K/$N ok" || { rm -f "$PO.tmp.mp4"; echo "part $K FAILED"; exit 1; }
fi
for i in $(seq 0 $((N-1))); do [ -s "${O%.mp4}.part$i.mp4" ] || exit 0; done
L="${O%.mp4}.list.txt"; : > "$L"; for i in $(seq 0 $((N-1))); do echo "file '${O%.mp4}.part$i.mp4'" >> "$L"; done
ffmpeg -loglevel error -y -f concat -safe 0 -i "$L" -c copy "$O" && rm -f "$L" ${O%.mp4}.part*.mp4 && echo "OK $O $(du -h "$O"|cut -f1)"
