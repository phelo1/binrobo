#!/bin/bash
# one foreground chunk of the B2-F SITL queue (<= ~100 s wall). usage: run_chunk.sh <queue> [budget]
cd "$(dirname "$0")"
Q=$1; B=${2:-78}; export B2F_OUT=${B2F_OUT:-/workspace/work/out/b2f_lane/sitl/runs}
PYTHONPATH=/workspace/work/pylib timeout -s INT 112 python3 scripts/b2f_runner.py $Q --budget $B 2>&1 | grep -v "mode change failed" | grep -E "pi |ALERT|hw |sim |SAVED|QUEUE|checkpoint|FINISH|Traceback|Error|error|FENCE" | tail -${3:-25}
