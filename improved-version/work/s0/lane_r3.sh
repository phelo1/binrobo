#!/bin/bash
# Revision 3 on the lane (152.2 kg): starts when the mechanical batch has finished. Two chains side by side.
cd /home/claude/s0
while pgrep -f "run_batch.py r3/q_r3_all.txt" > /dev/null; do sleep 10; done
echo "lane start $(date +%T)" >> lane_r3.log
E="X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r3s.json B2F_PAD_IN=-0.015"
G='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045}'; V='{"step":"ramp","trench":"covered","pothole":"filled"}'
( env $E CGB_GEO="$G" X_VARIANT="$V" bash /home/claude/b2f_review/variants/lane_chain.sh runs_r3_pf P1 P2a P2c ) &
( env $E CGB_GEO="$G" X_VARIANT="$V" bash /home/claude/b2f_review/variants/lane_chain.sh runs_r3_pf P7 P3 P4a P4b
  env $E CGB_GEO="$G" bash /home/claude/b2f_review/variants/lane_chain.sh runs_r3_pf P5a_drop_sharp_3kN P5d_up_sharp_3kN P6a_person_estop ) &
wait
echo "lane end $(date +%T)" >> lane_r3.log
