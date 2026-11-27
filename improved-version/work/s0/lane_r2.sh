#!/bin/bash
# Revision 2 on the lane: their default lane (step ramped, trench covered, pothole OPEN), then the same with the pothole filled.
E="X_SIM=simB2hx X_LIFT_RANGE=0.34 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=5.46 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r2.json B2F_PAD_IN=-0.015"
env $E CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' bash /home/claude/b2f_review/variants/lane_chain.sh runs_r2 P1 P2a P2c P7
env $E CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' X_VARIANT='{"step":"ramp","trench":"covered","pothole":"filled"}' bash /home/claude/b2f_review/variants/lane_chain.sh runs_r2_pf P1 P2a P2c P7 P3 P4a P4b
