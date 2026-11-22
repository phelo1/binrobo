#!/bin/bash
# 22 Nov: the hill tests again under the revision 5.1 speed rule (steeper than 6 %: 0.2 m/s with a bin, 0.15 m/s empty, nose first),
# on the lane without the assumed 12 % pitch. Leaf-zone grip 0.35 (as the other agent's model), 0.30 (wet) and 0.22 (wet leaves).
cd /home/claude/s0
LP=/home/claude/b2f_run/work/b2f_lanephys
E="X_LANE_WORLD=lane_world_real X_SIM=simB2hx X_LIFT_RANGE=0.32 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.245 X_LIFT_V=0.013 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r5.json B2F_PAD_IN=-0.015 X_ACT_N=6800 X_VLOOK=3 X_VSLOPE=-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"
G='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045,"act_N":6800.0}'; V='{"step":"ramp","trench":"covered","pothole":"filled"}'
LC=/home/claude/b2f_review/variants/lane_chain.sh
until [ -f $LP/runs_r51_real/P2a_pf/result.json ]; do sleep 20; done
echo "lane v51 start $(date +%T)" >> r51/lane_r51.log
for m in 1.0:m35 0.857:w30 0.629:w22; do d=runs_r51_v51_${m#*:}; mkdir -p $LP/$d
  [ -e $LP/$d/P1 ] || cp -r $LP/runs_r51_real/P1 $LP/$d/P1; [ -e $LP/$d/P2a_pf ] || cp -r $LP/runs_r51_real/P2a_pf $LP/$d/P2a_pf
  env $E CGB_GEO="$G" X_VARIANT="$V" X_MU_SCALE=${m%:*} bash $LC $d P6a_person_estop X8n X9n P4a; done
echo "lane v51 end $(date +%T)" >> r51/lane_r51.log
