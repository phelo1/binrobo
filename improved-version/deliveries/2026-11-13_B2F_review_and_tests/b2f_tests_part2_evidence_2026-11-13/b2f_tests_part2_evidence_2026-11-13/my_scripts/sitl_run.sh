#!/bin/bash
# usage: sitl_run.sh <out_name> <queue_file> [runner script]   (env B2F_PARAMS etc. passed through). Re-runnable: finished runs are skipped.
OUTN=$1; Q=$2; RUNNER=${3:-scripts/b2f_runner.py}
cd /home/claude/b2f_run/sitl/b2f || exit 1
export B2F_OUT=/home/claude/sitl_out/$OUTN/runs B2F_SUFFIX=${B2F_SUFFIX:-}; mkdir -p $B2F_OUT
for k in $(seq 1 40); do
  python3 $RUNNER $Q --budget 100000 2>&1 | grep -v "mode change failed" | grep -E "SAVED|QUEUE|Traceback|Error" >> /home/claude/sitl_out/$OUTN/progress.txt
  tail -1 /home/claude/sitl_out/$OUTN/progress.txt | grep -q "QUEUE left 0 " && break
  sleep 3
done
echo "$OUTN sitl done" >> /home/claude/sitl_out/$OUTN/progress.txt
