# revision 6.1, fast cruise on: the revision 6 fast settings + a third look at the pre-grab gate before a grab is refused
source /home/claude/s0/r6/env_r6_fast.sh
export X_GATE_TRIES=3
export X_LID_FILTER=1 X_PF_BAND=0.35      # every scan is cleaned of lone returns before anything uses it; the protective field allows a ragged hedge 0.35 m
