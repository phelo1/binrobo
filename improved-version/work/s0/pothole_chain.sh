#!/bin/bash
# Pothole stretch (their run P5h: from the P1 snapshot at s 542 to s 557, pothole as assumed, 60 mm under the left wheel) for the improved version
# with the castor beam free (+/-5 deg), stopped at +/-2 deg and locked. usage: pothole_chain.sh  (results appended to pothole_chain.out)
cd /home/claude/b2f_run/work/b2f_lanephys || exit 1
E="X_SIM=simB2hx X_LIFT_RANGE=0.35 X_ROCKER=1 B2F_PAD_IN=-0.005"
run() {  # dir, extra env
  d=$1; shift
  for try in 1 2 3 4; do env $E "$@" CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' X_RUNS_DIR=/home/claude/b2f_run/work/b2f_lanephys/$d python3 lanerun_x.py P5h_pothole 6000 > /tmp/ph_$d.log 2>&1; grep -q "^DONE" /tmp/ph_$d.log && break; done
  echo "$d: $(grep '^DONE' /tmp/ph_$d.log | cut -c1-420 || tail -1 /tmp/ph_$d.log | cut -c1-200)" >> /home/claude/s0/pothole_chain.out
}
run runs_lean X_ROCK_DEG=5
run runs_lean_lock X_ROCK_DEG=0.05
run runs_lean_s2 X_ROCK_DEG=2
echo "pothole chain done" >> /home/claude/s0/pothole_chain.out
