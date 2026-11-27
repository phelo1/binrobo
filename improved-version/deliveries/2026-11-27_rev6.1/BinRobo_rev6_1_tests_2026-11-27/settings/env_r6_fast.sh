# revision 6 fast cruise: 2:1 chain stage (wheel speed 1.24 m/s at full throttle), clear-lane speeds by slope.
# Firmware loops reset for the new gearing: turn-rate feed-forward = 1 / (turn rate at full differential) = 1 / (2 x 1.24 / (track x 1.05)) = 0.35
# (B2-F had 0.8 for a drive that needed 0.54, which is why turns on the spot overshot their commanded rate); P, I and the speed loop scaled by 0.80/1.24.
source /home/claude/s0/r6/env_r6.sh
export X_VFAST="-1:1.0:1.0,0.005:1.0:0.8,0.03:0.8:0.6,0.06:0.6:0.4" X_VTOP=1.0 X_ROB_VMAX=1.24 X_R6_FLOAT_V=0.7
export B2F_PARAMS="ARMING_SKIPCHK -1;WP_SPEED 1.0;CRUISE_SPEED 0.5;CRUISE_THROTTLE 40;SPEED_MAX 1.24;ATC_STR_RAT_FF 0.35;ATC_STR_RAT_P 0.19;ATC_STR_RAT_I 0.13;ATC_SPEED_P 0.77;ATC_SPEED_I 0.032;MOT_THR_MIN 3"
