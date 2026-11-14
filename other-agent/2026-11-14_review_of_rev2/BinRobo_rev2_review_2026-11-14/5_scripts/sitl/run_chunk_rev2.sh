#!/bin/bash
# Independent re-test of revision 2 (2026-11-14): one foreground chunk (<= ~105 s wall) of a rev2 SITL queue.
# usage: run_chunk_rev2.sh <profile> <queue> [budget]
#   profiles: base  = their switches, 119.4 kg (scored)       m122  = same at 122.4 kg (+3 kg audit)
#             cam15 = camera sigma x1.5 (their X_CAM_SIG)     lid15 = lidar noise x1.5 + 10 % dropout (OUR stress switch)
#             night = low-light camera (OUR stress switch)
# Binary: ArduRover 4.6.2 (bin/ardurover_aarch64, chosen by the runner on aarch64). ARMING_SKIPCHK (4.7-only) not passed: params have ARMING_CHECK 0.
cd "$(dirname "$0")"
W0=$SECONDS; for k in $(seq 1 70); do pgrep -f "scripts_rev2/b2f_runner_x.py" >/dev/null || break; sleep 1; done; pgrep -f "scripts_rev2/b2f_runner_x.py" >/dev/null && { echo "BUSY: rev2 runner alive (pid $(pgrep -f scripts_rev2/b2f_runner_x.py))"; exit 0; }
WAITED=$((SECONDS-W0))
PR=$1; Q=$2; B=$(( ${3:-92} - WAITED )); [ $B -lt 25 ] && { echo "BUSY: waited ${WAITED}s for the previous runner to exit"; exit 0; }; echo "waited ${WAITED}s"
export X_COMP=b2f_companion_xr X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1 X_NOSE_DX=0.065 X_ROB_MASS=119.4 X_LIFT_SCALE=1.4 X_INST=3 X_CK=_rev2
export B2F_OUT=/workspace/work/out/rev2/sitl/runs B2F_SUFFIX=
case $PR in
  base) ;;
  m122) export X_ROB_MASS=122.4 B2F_SUFFIX=_m122 B2F_OUT=/workspace/work/out/rev2/sitl/runs_$PR ;;
  cam15) export X_CAM_SIG=0.015 B2F_SUFFIX=_cam15 B2F_OUT=/workspace/work/out/rev2/sitl/runs_$PR ;;
  lid15) export X_COMP=b2f_companion_xs X_STRESS_LIDAR_SIGF=1.5 X_STRESS_LIDAR_DROP=0.10 B2F_SUFFIX=_lid15 B2F_OUT=/workspace/work/out/rev2/sitl/runs_$PR ;;
  night) export X_COMP=b2f_companion_xs X_STRESS_LOWLIGHT=1 B2F_SUFFIX=_night B2F_OUT=/workspace/work/out/rev2/sitl/runs_$PR ;;
  camfix) export X_COMP=b2f_companion_xs X_CAM_SIG=0.015 X_STRESS_CAMRNG_PERSIST=1 B2F_SUFFIX=_camfix B2F_OUT=/workspace/work/out/rev2/sitl/runs_$PR ;;
  *) echo "bad profile"; exit 1;;
esac
mkdir -p $B2F_OUT
PYTHONPATH=/workspace/work/pylib timeout -s INT $((B+30)) python3 scripts_rev2/b2f_runner_x.py $Q --budget $B 2>&1 | grep -v "mode change failed" | grep -E "ALERT|SAVED|QUEUE|checkpoint|Traceback|Error|error|rear camera|pre-grab gate|yard exit" | tail -${4:-14}
