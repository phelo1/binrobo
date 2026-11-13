#!/bin/bash
# after the open-pothole chain: the two "pothole filled" return runs with the +/-2 deg stops (does the tighter stop keep the benefit on the wet-leaf slope?)
while pgrep -f "lane_chain.sh runs_leanm_s2" > /dev/null; do sleep 15; done
cd /home/claude/b2f_run/work/b2f_lanephys
for r in P2a_pf P2c_pf; do
  env X_SIM=simB2hx X_LIFT_RANGE=0.35 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=5.46 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_imp.json B2F_PAD_IN=-0.005 CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' X_RUNS_DIR=/home/claude/b2f_run/work/b2f_lanephys/runs_leanm_s2 python3 lanerun_x.py $r 6000 > /tmp/lane_s2_$r.log 2>&1
  echo "runs_leanm_s2 $r: $(grep '^DONE' /tmp/lane_s2_$r.log | cut -c1-420 || tail -1 /tmp/lane_s2_$r.log | cut -c1-200)" >> /home/claude/s0/lane_chain_runs_leanm_s2.out
done
echo "after-chain done" >> /home/claude/s0/lane_chain_runs_leanm_s2.out
