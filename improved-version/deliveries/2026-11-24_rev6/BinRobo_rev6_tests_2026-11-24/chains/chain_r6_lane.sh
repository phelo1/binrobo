#!/bin/bash
# 24 Nov: lane physics at the fast cruise speeds (1.0 m/s cap; by slope 1.0 / 0.8 / 0.6 with a bin, 1.0 / 0.8 / 0.6 / 0.4 empty), real-slope lane, made good.
# Drive and brake torque caps scaled for the 2:1 chain stage (tcap 34 N m; brake 85 N m per wheel). Leaf-zone grip 0.35 and 0.22.
cd /home/claude/s0
LP=/home/claude/b2f_run/work/b2f_lanephys
E="X_LANE_WORLD=lane_world_real X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.245 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r5.json B2F_PAD_IN=-0.015 X_ACT_N=6800 X_VLOOK=8 X_VDEF=1.0 X_LDK=2.0 X_VSLOPE=-1:1.0:1.0,0.005:1.0:0.8,0.03:0.8:0.6,0.06:0.6:0.4"
G='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045,"act_N":6800.0,"tcap":34.0}'; V='{"step":"ramp","trench":"covered","pothole":"filled"}'
LC=/home/claude/b2f_review/variants/lane_chain.sh
echo "lane fast start $(date +%T)" >> r6/lane_r6.log
env $E CGB_GEO="$G" X_VARIANT="$V" bash $LC runs_r6_fast P1 P2a_pf P7 P2c P3 P4a P4b
mkdir -p $LP/runs_r6_fast_w22
env $E CGB_GEO="$G" X_VARIANT="$V" X_MU_SCALE=0.629 bash $LC runs_r6_fast_w22 P1 P2a_pf P2c
echo "lane fast end $(date +%T)" >> r6/lane_r6.log
