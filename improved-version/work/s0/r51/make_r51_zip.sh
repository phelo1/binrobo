#!/bin/bash
# Collect the revision 5.1 scripts, settings and result files into one folder and zip it. usage: make_r51_zip.sh <out_zip>
set -e
T=/home/claude/s0/r51_pack; rm -rf $T.old; [ -d $T ] && mv $T $T.old
mkdir -p $T/{software,chains,tables,stop_tests,lane,sitl,drawing_scripts}
S=/home/claude/s0; L=/home/claude/b2f_run/work/b2f_lanephys; O=/home/claude/sitl_out; SC=/home/claude/b2f_run/sitl/b2f/scripts; RX=/home/claude/b2f_run/revG/sim/cg/h2/res_r51x
cp $SC/b2f_companion_x.py $SC/b2f_runner_x.py $L/lanerun_x.py /home/claude/b2f_review/variants/make_lane_world_real.py $T/software/
cp $SC/b2f_companion_x_r5_final.py $T/software/b2f_companion_x_rev5_final.py
( cd $T/software && md5sum *.py > code.md5 )
cp $S/r51/chain_r51*.sh $S/r51/chain_r51.log $S/r51/lane_r51.log $S/r51/q_r51_pstop*.txt $S/r51/q_r51_pstop*.out $S/r51/sitl_q_*.txt $S/r5/sitl_q_s5a.txt $S/r5/sitl_env_r5.sh $S/sitl_run_x.sh $S/run_batch.py /home/claude/b2f_review/variants/lane_chain.sh $S/r4/runY.py $T/chains/
cp $S/lane_chain_runs_r51_*.out $T/chains/
cp $S/r51/tables/* $S/r51/ana/*.py $S/r51/cost_r51.py $S/r51/people_mc_r51.py $S/r51/mk_facts_r51.py $S/r51/facts_r51.json $S/r5/r5_score.py $T/tables/
cp $RX/*_r51.json $T/stop_tests/
for d in runs_r51_real runs_r51_real_w30 runs_r51_real_w22 runs_r51_v51_m35 runs_r51_v51_w30 runs_r51_v51_w22; do for r in $L/$d/*/; do n=$(basename $r)
  case "$d/$n" in runs_r51_v51_*/P1|runs_r51_v51_*/P2a_pf|runs_r51_real_w*/P2a_pf) continue;; esac
  [ -f $r/result.json ] && cp $r/result.json $T/lane/${d}__$n.json; done; done
for o in r51_s5a r51_person60 r51_person60near r51_person60near_day r51_person200 r51_trip_candidate r51_final r51_final_ret1630 r51_late_quiet2230 r51_late_anytime; do
  for r in $O/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/sitl/${o}__$n.json; done; done
cd $S/cad && cp draw_sheets.py draw_sheets_r5.py make_pdf.py $T/drawing_scripts/
cp $S/r51/R51_README.txt $T/README.txt
cd $T && rm -f "$1" && zip -q -r "$1" . && echo "zip: $(unzip -l "$1" | tail -1)"
