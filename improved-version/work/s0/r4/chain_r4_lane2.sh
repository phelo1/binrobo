#!/bin/bash
# extra lane run: the empty return over the sharp 40 mm step (their lane as it is), revision 4
cd /home/claude/s0
while ! grep -q "lane end" r4/lane_r4.log 2>/dev/null; do sleep 10; done
LP=/home/claude/b2f_run/work/b2f_lanephys
E="X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.34 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r4.json B2F_PAD_IN=-0.015 X_ACT_N=6800 X_VSLOPE=-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.09:0.2:0.15"
G='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045,"act_N":6800.0}'; V='{"step":"sharp","trench":"covered","pothole":"filled"}'
mkdir -p $LP/runs_r4_sharp; [ -e $LP/runs_r4_sharp/P1 ] || cp -r $LP/runs_r4_pf/P1 $LP/runs_r4_sharp/P1
env $E CGB_GEO="$G" X_VARIANT="$V" bash /home/claude/b2f_review/variants/lane_chain.sh runs_r4_sharp P2a
echo "lane2 end $(date +%T)" >> r4/lane_r4.log
