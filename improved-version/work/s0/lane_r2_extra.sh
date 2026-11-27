#!/bin/bash
# Revision 2, short lane stretches from the P1 snapshots (their runs): sharp 40 mm step down and up at the 3 kN lift cap, the open trench, a person stepping in on the wet descent.
cd /home/claude/s0
while pgrep -f "lane_r2.sh" > /dev/null; do sleep 15; done
E="X_SIM=simB2hx X_LIFT_RANGE=0.34 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=5.46 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r2.json B2F_PAD_IN=-0.015"
env $E CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' bash /home/claude/b2f_review/variants/lane_chain.sh runs_r2 P5a_drop_sharp_3kN P5d_up_sharp_3kN P5g_trench_open P6a_person_estop
echo "extra done" >> /home/claude/s0/lane_chain_runs_r2.out
