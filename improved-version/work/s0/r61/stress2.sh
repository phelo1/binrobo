#!/bin/bash
# People stress tests on scenario s5a (loaded robot in the lane, s 295 to 380, night), three seeds each. Revision 6.1: two more cases
# (hug, hugstand: a walker who keeps 0.3 m from the far hedge) and X_LID_BAD is passed through (a worse lidar and a real hedge).
# stress2.sh (27 Nov 02:45): "side" is the revision 6 case again (walker steps off the far hedge when the robot is 3.0 m from his line); "side14" is the same walker stepping off when the robot is 1.4 m from his line, i.e. beside him.
# usage: stress2.sh <env file> <prefix> [profile ...]     (no profile = all)
ENVF=$1; PF=$2; shift 2; Q=/home/claude/s0/r6
ALL="near26 near20 run26 run20 child35 side side14 behind flank hug hugstand asis near35 near31 run40 nearhedge30 nearhedge45 slowwalk low40 low40near stay1000 boxside boxpath boxfar gapwalk26 gaprun26"
for p in ${@:-$ALL}; do
  unset X_MOVER X_MOVERS_SET X_OBST_ADD X_PPL_P X_HEDGE_GAP
  case $p in
    asis) ;;
    near35) export X_MOVER="person:pause:60,person:trigger_d:3.5";;
    near31) export X_MOVER="person:pause:60,person:trigger_d:3.07";;
    near26) export X_MOVER="person:pause:60,person:trigger_d:2.6";;
    near20) export X_MOVER="person:pause:60,person:trigger_d:2.0";;
    child35) export X_MOVER="person:pause:60,person:trigger_d:3.5,person:r:0.15";;
    run40) export X_MOVER="person:pause:20,person:trigger_d:4.0,person:r:0.15,person:speed:2.5";;
    run20) export X_MOVER="person:pause:20,person:trigger_d:2.0,person:r:0.15,person:speed:2.5";;
    run26) export X_MOVER="person:pause:20,person:trigger_d:2.6,person:r:0.15,person:speed:2.5";;
    nearhedge30) export X_MOVERS_SET='[{"kind":"person","a":[320,1.95],"b":[320,-1.95],"speed":1.0,"pause":30,"pause_at":0.2,"trig":[320,1.0],"trigger_d":3.0}]';;
    nearhedge45) export X_MOVERS_SET='[{"kind":"person","a":[320,1.95],"b":[320,-1.95],"speed":1.0,"pause":30,"pause_at":0.2,"trig":[320,1.0],"trigger_d":4.5}]';;
    behind) export X_MOVERS_SET='[{"kind":"person","a":[296,-0.1],"b":[376,-0.1],"along":true,"speed":1.6,"pause":0,"pause_at":0.99,"trig":[303,1.0],"trigger_d":1.5}]';;
    side) export X_MOVERS_SET='[{"kind":"person","a":[318,-1.95],"b":[318,-0.2],"speed":1.0,"pause":30,"pause_at":0.999,"trig":[318,1.0],"trigger_d":3.0}]';;
    side14) export X_MOVERS_SET='[{"kind":"person","a":[318,-1.95],"b":[318,-0.2],"speed":1.0,"pause":30,"pause_at":0.999,"trig":[318,1.0],"trigger_d":1.4}]';;
    flank) export X_MOVERS_SET='[{"kind":"person","a":[324,-0.6],"b":[280,-0.6],"along":true,"speed":1.2,"pause":30,"pause_at":0.398,"trig":[303,1.0],"trigger_d":1.5}]';;
    slowwalk) export X_MOVERS_SET='[{"kind":"person","a":[306,1.0],"b":[372,1.0],"along":true,"speed":0.3,"pause":0,"pause_at":0.99,"trig":[300,1.0],"trigger_d":2.0}]';;
    low40) export X_PPL_P=0.40;;
    low40near) export X_PPL_P=0.40 X_MOVER="person:pause:60,person:trigger_d:3.5";;
    stay1000) export X_MOVER="person:pause:1000";;
    boxside) export X_MOVERS_SET='[]' X_OBST_ADD='[{"s":330,"lat":-0.5}]';;
    boxpath) export X_MOVERS_SET='[]' X_OBST_ADD='[{"s":330,"lat":1.0}]';;
    boxfar) export X_MOVERS_SET='[]' X_OBST_ADD='[{"s":320,"lat":-1.2}]';;
    hug) export X_MOVERS_SET='[{"kind":"person","a":[334,-1.4],"b":[270,-1.4],"along":true,"speed":1.2,"pause":0,"pause_at":0.99,"trig":[303,1.0],"trigger_d":1.5}]';;
    hugstand) export X_MOVERS_SET='[{"kind":"person","a":[334,-1.4],"b":[270,-1.4],"along":true,"speed":1.2,"pause":30,"pause_at":0.45,"trig":[303,1.0],"trigger_d":1.5}]';;
    gaprun26) export X_HEDGE_GAP="318:322:-1" X_MOVER="person:pause:20,person:trigger_d:2.6,person:r:0.15,person:speed:2.5";;
    gapwalk26) export X_HEDGE_GAP="318:322:-1" X_MOVER="person:pause:60,person:trigger_d:2.6";;
  esac
  rm -rf /home/claude/sitl_out/${PF}_$p /home/claude/b2f_run/sitl/b2f/ckpt_${PF}_$p
  /home/claude/s0/r61/run2.sh $ENVF ${PF}_$p $Q/q_s5a_7.txt $Q/q_s5a_11_23.txt
done
echo "stress $PF done $(date +%T)" >> /home/claude/s0/r61/chain.log
