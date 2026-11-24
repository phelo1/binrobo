# revision 6 settings (source this). Slow set = touch-safe speeds only; add the FAST lines for the fast cruise.
source /home/claude/s0/r5/sitl_env_r5.sh
export X_KL_GAP=0.42 X_R5B=1 X_PPL_PAUSE=1 X_TRIP_WH=80 X_QUIET_END=1800 X_R6=1
export X_VSLOPE="-1:0.4:0.4,0.005:0.4:0.3,0.03:0.3:0.2,0.06:0.2:0.15"
