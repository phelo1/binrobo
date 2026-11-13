#!/bin/bash
# usage: lane_chain.sh <runs_dir_name> <run ids...>   (environment selects the model variant). Re-runnable: finished runs print DONE at once.
cd /home/claude/b2f_run/work/b2f_lanephys || exit 1
D=$1; shift; export X_RUNS_DIR=/home/claude/b2f_run/work/b2f_lanephys/$D; mkdir -p $X_RUNS_DIR
for r in "$@"; do
  for try in 1 2 3; do python3 lanerun_x.py $r 6000 > /tmp/lane_${D}_$r.log 2>&1; grep -q "^DONE" /tmp/lane_${D}_$r.log && break; done
  echo "$D $r: $(grep '^DONE' /tmp/lane_${D}_$r.log | cut -c1-150 || tail -1 /tmp/lane_${D}_$r.log | cut -c1-150)" >> /home/claude/s0/lane_chain_$D.out
done
echo "$D chain done" >> /home/claude/s0/lane_chain_$D.out
