#!/bin/bash
# Revision 2 at the corrected weight (119.4 kg as built): full gate on one core; lane set with the pothole filled on the other once the B2-F comparison is done;
# then the driving-software check on a quiet machine (two simulator instances).
cd /home/claude/s0
( python3 run_batch.py var_r2b.txt /home/claude/b2f_run/revG/sim/cg 1 /home/claude/s0/logs_r2b > var_r2b.out 2>&1 ) &
( while pgrep -f "run_batch.py var_b2f_cmpA.txt" > /dev/null; do sleep 10; done
  E="X_SIM=simB2hx X_LIFT_RANGE=0.34 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=5.46 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r2b.json B2F_PAD_IN=-0.015"
  env $E CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' X_VARIANT='{"step":"ramp","trench":"covered","pothole":"filled"}' bash /home/claude/b2f_review/variants/lane_chain.sh runs_r2b_pf P1 P2a P2c P7 P3 P4a P4b
  env $E CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' bash /home/claude/b2f_review/variants/lane_chain.sh runs_r2b_pf P5a_drop_sharp_3kN P5d_up_sharp_3kN P6a_person_estop ) &
wait
export B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1 X_NOSE_DX=0.065 X_ROB_MASS=119.4 X_LIFT_SCALE=1.4
echo "sitl start $(date +%T)" >> chain_r2c.log
./sitl_run_x.sh r2 /home/claude/s0/sitl_q_r2_i1.txt 1 &
sleep 20
./sitl_run_x.sh r2 /home/claude/s0/sitl_q_r2_i0.txt 0 &
wait
echo "sitl end $(date +%T)" >> chain_r2c.log
