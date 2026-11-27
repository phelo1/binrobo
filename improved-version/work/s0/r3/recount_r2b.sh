#!/bin/bash
# Re-run every revision 2 pick-up at the corrected weight (119.4 kg) and log where the nib ended up in the bin, so false holds can be counted under both bands.
cd /home/claude/b2f_run/revG/sim/cg
E="CGB_F9=1 CMP_SIM=simB2hx X_LIFT_RANGE=0.34 X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=5.46 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 CGB_MASSF=/home/claude/b2f_review/variants/mass_cgB2_r2b.json B2F_PAD_IN=-0.015 B2_DOCK=front CMP_PREFIX=B2F_"
ALL=$(seq -s, 0 29)
for job in "$@"; do set -- $job; b=${job%%:*}; s=${job##*:}
  env $E CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' python3 /home/claude/s0/grab_diag.py $b 30 $s $ALL > /home/claude/s0/r3/nib_r2b_${b}_${s}.jsonl 2> /home/claude/s0/r3/nib_r2b_${b}_${s}.err
done
