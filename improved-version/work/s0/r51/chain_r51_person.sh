#!/bin/bash
# 22 Nov: pause-when-anyone-is-near rule (X_PPL_PAUSE=1, 5 m). Scenario s5a as it stands and with the person made to stay.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1
echo "person start $(date +%T)" >> r51/chain_r51.log
./sitl_run_x.sh r51_s5a /home/claude/s0/r5/sitl_q_s5a.txt 2
X_MOVER="person:pause:60" ./sitl_run_x.sh r51_person60 /home/claude/s0/r5/sitl_q_s5a.txt 2
X_MOVER="person:pause:60,person:trigger_d:3.5" ./sitl_run_x.sh r51_person60near /home/claude/s0/r5/sitl_q_s5a.txt 2
X_PPL_P=0.85 X_MOVER="person:pause:60,person:trigger_d:3.5" ./sitl_run_x.sh r51_person60near_day /home/claude/s0/r5/sitl_q_s5a.txt 2
X_MOVER="person:pause:200" ./sitl_run_x.sh r51_person200 /home/claude/s0/r5/sitl_q_s5a.txt 2
echo "person end $(date +%T)" >> r51/chain_r51.log
