#!/bin/bash
# one foreground tick (<= ~113 s): queue chunk + (if not finished) lane-fit chunk; at most 2 heavy procs; waits for both.
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg; export PYTHONPATH=/workspace/work/pylib
python3 b2/qchunk_b2.py ${1:-110} & QP=$!
if [ ! -f b2/res/lanefit_B1_srun.json ]; then (cd b2; nice -n 10 timeout 112 python3 lanefit_b2_ckpt.py design_B1_srun.json 45); fi
wait $QP
