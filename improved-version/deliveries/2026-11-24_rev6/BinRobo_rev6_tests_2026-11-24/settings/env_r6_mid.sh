# revision 6, middle option: no sprocket change (wheel speed 0.80 m/s flat out, as B2-F), 0.6 m/s on a clear lane
source /home/claude/s0/r6/env_r6.sh
export X_VFAST="-1:0.6:0.6,0.005:0.6:0.6,0.03:0.6:0.5,0.06:0.5:0.4" X_VTOP=0.6 X_ROB_VMAX=0.80 X_R6_FLOAT_V=0.6 X_TRIP_MIN=60
export B2F_PARAMS="ARMING_SKIPCHK -1;WP_SPEED 0.6;SPEED_MAX 0.8"
