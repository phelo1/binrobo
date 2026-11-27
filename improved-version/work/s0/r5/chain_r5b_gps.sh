#!/bin/bash
# Repeatable version of the s3a seed 7 event: Float quality with a 1.8 m position bias from s 63 to s 72, just before the sharp bend at s 73-77.
# Scenario 'tune' s 40 -> 110 with a full 240 L bin, seed 7. Eight bias directions; first-pass software (a) and second pass (b).
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 B2F_SEG=40,110
PASS=$1; INST=$2; shift; shift
[ "$PASS" = b ] && export X_R5B=1
for d in "$@"; do
  n=$(echo $d | sed 's/-/m/'); echo "gps $PASS dir $d start $(date +%T)" >> r5/chain_r5b.log
  X_GPS_FAULT="63:72:$d:1.8" ./sitl_run_x.sh r5${PASS}_gps_$n /home/claude/s0/r5/sitl_q_tune7.txt $INST
done
echo "gps $PASS end $(date +%T)" >> r5/chain_r5b.log
