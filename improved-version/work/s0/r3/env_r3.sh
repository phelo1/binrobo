# revision 3 model switches (source this; MASS = path of the mass table, default the revision 3 table)
export X_CAST_W=0.012 X_POSTHOLD=0.030 CGB_F9=1 CMP_SIM=simB2hx B2_DOCK=front CMP_PREFIX=B2F_ X_ROCKER=1 X_ROCK_DEG=2 X_ROCK_M=6.0 X_NOSE_DX=0.065 CMP_COMB_HW=0.35 X_DOCK_TRIES=3 X_DOCK_DYMAX=0.025 B2F_PAD_IN=-0.015 X_LIFT_RANGE=0.32
export CGB_MASSF=${MASS:-/home/claude/b2f_review/variants/mass_cgB2_r3s.json}
export CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15,"pad_stroke":0.045}'
