#!/bin/bash
# Revision 4 on the lane (177.6 kg): starts when the mechanical chain has finished. Two chains side by side.
cd /home/claude/s0
while pgrep -f "r4/chain_r4\.sh" > /dev/null; do sleep 10; done
echo "lane start $(date +%T)" >> r4/lane_r4.log
LP=/home/claude/b2f_run/work/b2f_lanephys
E="X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.34 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r4.json B2F_PAD_IN=-0.015 X_ACT_N=6800 X_VSLOPE=-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.09:0.2:0.15"
G='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045,"act_N":6800.0}'; V='{"step":"ramp","trench":"covered","pothole":"filled"}'
LC=/home/claude/b2f_review/variants/lane_chain.sh
( env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r4_pf P1 P2a P2c ) &
( env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r4_pf P7 P3 P4a P4b
  env $E CGB_GEO="$G" bash $LC runs_r4_pf P5a_drop_sharp_3kN P5d_up_sharp_3kN P6a_person_estop P5h_pothole P5g_trench_open ) &
wait
echo "lane main end $(date +%T)" >> r4/lane_r4.log
mkdir -p $LP/runs_r4_b100; [ -e $LP/runs_r4_b100/P1 ] || cp -r $LP/runs_r4_pf/P1 $LP/runs_r4_b100/P1
( env $E CGB_GEO="$G" X_BOOST=100 bash $LC runs_r4_b100 P5d_up_sharp_3kN P5h_pothole ) &
( env $E CGB_GEO="$G" X_BOOST=100 bash $LC runs_r4_b100 P5g_trench_open P5a_drop_sharp_3kN ) &
wait
echo "lane end $(date +%T)" >> r4/lane_r4.log
