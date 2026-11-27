#!/bin/bash
# The person scenario (s5a) on the final code: as it stands, and with the person made to stay in the robot's path. The standard scenario no longer
# makes the robot stop for the lidar: at revision 5 speeds the person has walked on before the robot is within 1.5 m.
cd /home/claude/s0; source r5/sitl_env_r5.sh; export X_KL_GAP=0.42 X_R5B=1
echo "person start $(date +%T)" >> r5/chain_r5b.log
./sitl_run_x.sh r5b_s5a_final /home/claude/s0/r5/sitl_q_s5a.txt 2
X_MOVER="person:pause:60" ./sitl_run_x.sh r5b_person60 /home/claude/s0/r5/sitl_q_s5a.txt 2
X_MOVER="person:pause:60,person:trigger_d:3.5" ./sitl_run_x.sh r5b_person60near /home/claude/s0/r5/sitl_q_s5a.txt 2
X_MOVER="person:pause:200" ./sitl_run_x.sh r5b_person200 /home/claude/s0/r5/sitl_q_s5a.txt 2
X_CAM_PEOPLE=0 X_MOVER="person:pause:60" ./sitl_run_x.sh r5b_person60_nocam /home/claude/s0/r5/sitl_q_s5a.txt 2
echo "person end $(date +%T)" >> r5/chain_r5b.log
