#!/bin/bash
# Switches the simulator instances over to the 4-fix campaign at run boundaries. Each step waits for a result file, then
# stops that instance's runner (the wrapper loop restarts it with the re-written list) and starts the next list.
cd /home/claude/s0
export B2F_PARAMS="ARMING_SKIPCHK -1" X_COMP=b2f_companion_x X_FIX_RCA=1 X_FIX_RCB=1 X_FIX_RCC=1 X_FIX_APP=1
stop_inst () {  # $1 = pattern of the runner command, $2 = instance number
  P=$(pgrep -f "$1"); [ -n "$P" ] && kill -TERM $P; sleep 4; pkill -f "ardurover .*-I$2 "; sleep 3; }
( # instance 2: re-read its list at the next run boundary
  while [ ! -f /home/claude/sitl_out/fix4/runs/s1b__s7/result.json ]; do sleep 5; done
  stop_inst "b2f_runner_x.py /home/claude/s0/sitl_q_fix4.txt" 2; echo "i2 switched $(date +%T)" >> orchestrate.log ) &
( # instance 1: after the 3-fix three-bin pickup finishes, stop the 3-fix campaign and start the 4-fix list
  while [ ! -f /home/claude/sitl_out/fix472/runs/s3b__s7/result.json ]; do sleep 5; done
  pkill -f "sitl_run_x.sh fix472"; stop_inst "b2f_runner_x.py /home/claude/s0/sitl_q_fix.txt" 1; echo "i1 switched $(date +%T)" >> orchestrate.log
  ./sitl_run_x.sh fix4 /home/claude/s0/sitl_q_fix4_i1.txt 1 ) &
( # instance 0: when the unmodified-code campaign has done its short scenarios (it then starts a three-bin pickup), stop it
  while [ ! -d /home/claude/sitl_out/base472/runs/s3b__s23 ] && ! grep -q "base472 sitl done" /home/claude/sitl_out/base472/progress.txt 2>/dev/null; do sleep 5; done
  pkill -f "sitl_run.sh base472"; stop_inst "scripts/b2f_runner.py /home/claude/s0/sitl_q_scored.txt" 0; mv /home/claude/sitl_out/base472/runs/s3b__s23 /home/claude/sitl_out/base472/_aborted_s3b__s23 2>/dev/null
  echo "i0 switched $(date +%T)" >> orchestrate.log
  X_CK=_fix4 ./sitl_run_x.sh fix4 /home/claude/s0/sitl_q_fix4_i0.txt 0 ) &
wait
echo "orchestration finished $(date +%T)" >> orchestrate.log
