#!/bin/bash
# usage: sitl_run_x.sh <out_name> <queue_file> <instance>   runs my runner variant (b2f_runner_x.py); env X_COMP / X_FIX_* select the driving-code variant.
OUTN=$1; Q=$2; export X_INST=${3:-1} X_CK=_$1
cd /home/claude/b2f_run/sitl/b2f || exit 1
export B2F_OUT=/home/claude/sitl_out/$OUTN/runs; mkdir -p $B2F_OUT
for k in $(seq 1 40); do
  python3 scripts/b2f_runner_x.py $Q --budget 100000 2>&1 | grep --line-buffered -v "mode change failed" | grep --line-buffered -E "SAVED|QUEUE|Traceback|Error|yard exit|rear camera|pre-grab gate" >> /home/claude/sitl_out/$OUTN/progress.txt
  tail -1 /home/claude/sitl_out/$OUTN/progress.txt | grep -q "QUEUE left 0 " && break
  sleep 3
done
echo "$OUTN sitl done" >> /home/claude/sitl_out/$OUTN/progress.txt
