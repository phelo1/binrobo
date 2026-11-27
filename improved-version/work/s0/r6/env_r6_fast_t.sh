# revision 6 fast cruise with the firmware loops re-scaled for the 2:1 chain stage (wheel speed per unit of throttle is 1.55 times higher)
source /home/claude/s0/r6/env_r6_fast.sh
export B2F_PARAMS="ARMING_SKIPCHK -1;WP_SPEED 1.0;CRUISE_SPEED 0.5;CRUISE_THROTTLE 40;SPEED_MAX 1.24;ATC_STR_RAT_FF 0.52;ATC_STR_RAT_P 0.19;ATC_STR_RAT_I 0.13;ATC_SPEED_P 0.77;ATC_SPEED_I 0.032;MOT_THR_MIN 3"
