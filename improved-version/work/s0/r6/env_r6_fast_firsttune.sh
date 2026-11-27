# revision 6 fast cruise: 2:1 chain stage (wheel speed 1.24 m/s at full throttle), clear-lane speeds by slope
source /home/claude/s0/r6/env_r6.sh
export X_VFAST="-1:1.0:1.0,0.005:1.0:0.8,0.03:0.8:0.6,0.06:0.6:0.4" X_VTOP=1.0 X_ROB_VMAX=1.24 X_R6_FLOAT_V=0.7
export B2F_PARAMS="ARMING_SKIPCHK -1;WP_SPEED 1.0;CRUISE_SPEED 0.5;CRUISE_THROTTLE 40;SPEED_MAX 1.24"
