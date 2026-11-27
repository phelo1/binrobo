#!/bin/bash
# Collect the revision 6 scripts, settings and result files into one folder and zip it. usage: make_r6_zip.sh <out_zip>
set -e
T=/home/claude/s0/r6_pack; rm -rf $T; mkdir -p $T/{software,settings,chains,tables,stop_tests,lane/lane_first_try,sitl/traces,drawing_scripts}
S=/home/claude/s0; R=$S/r6; L=/home/claude/b2f_run/work/b2f_lanephys; O=/home/claude/sitl_out; SC=/home/claude/b2f_run/sitl/b2f/scripts; RX=/home/claude/b2f_run/revG/sim/cg/h2/res_r6
cp $SC/b2f_r6.py $SC/b2f_companion_x.py $SC/b2f_runner_x.py $SC/b2f_companion_x_r51.py $SC/b2f_runner_x_r51.py $L/lanerun_x.py $T/software/
cp $L/lanerun_x_r51.py $T/software/ 2>/dev/null || true
cp $R/code_final.md5 $R/code_lane_tests.md5 $T/software/
cp $R/env_r6.sh $R/env_r6_fast.sh $R/env_r6_slow2.sh $R/env_r6_mid.sh $R/env_r6_fast_leaf.sh $R/env_r6_fast_v10.sh $S/r5/sitl_env_r5.sh $T/settings/
cp $R/chain_r6*.sh $R/switch_chain.sh $R/stress.sh $R/run2.sh $R/chain_r6.log $R/lane_r6.log $R/q_*.txt $R/q_*.out $S/sitl_run_x.sh $S/run_batch.py $S/r4/runY.py $S/r4/sitl_q_r4_i0.txt $S/r4/sitl_q_r4_i1.txt /home/claude/b2f_review/variants/lane_chain.sh $T/chains/
cp $L/lane_chain_runs_r6_fast*.out $T/chains/ 2>/dev/null || true
cp $R/tables/* $R/stress_tab.py $R/stress_md.py $R/trips_tab.py $R/pstop_tab_r6.py $R/lane_tab_r6.py $R/pivot_rates.py $R/suite_extra.py $R/cost_r6.py $R/mk_facts_r6.py $R/facts_r6.json $R/show.py $R/piv_an.py $R/trip_time.py $S/r5/r5_score.py $T/tables/
rm -f $T/tables/stress_fast_tmp.json
cp $RX/*.json $T/stop_tests/; cp /home/claude/b2f_review/variants/mass_cgB2_r5.json $T/stop_tests/
for d in runs_r6_fast runs_r6_fast_w22; do for r in $L/$d/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/lane/${d}__$n.json; done; done
for r in $L/runs_r6_fast_before_end_rule/*/ $R/lane_first_try/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/lane/lane_first_try/$n.json; done 2>/dev/null || true
for o in $(ls $O | grep -E "^r6"); do
  case $o in r6a_*|r6t_*|r6x_*|r6f_trip2|r6f_tune3|r6s_*|r6_before_binfix|r6_gap_before_fix|r6_gap_after_fix1|r6_gap_no_lookahead|r6f_pivflank_before_fix|r6f_pivflank_before_fix2|r6f_pivflank_before_fix3|r6f_suite_before_dirfix) continue;; esac
  for r in $O/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/sitl/${o}__$n.json; done
done
# runs made before a fix, kept as evidence of what the fix changed
mkdir -p $T/sitl/before_fixes
for g in r6_before_binfix r6_gap_before_fix r6_gap_after_fix1 r6_gap_no_lookahead; do for o in $O/$g/*/; do on=$(basename $o); for r in $o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/sitl/before_fixes/${g}__${on}__$n.json; done; done; done
for v in a b; do for r in $O/r6f_pivflank_before_fix/$v/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/sitl/before_fixes/r6f_pivflank_before_fix__${v}__$n.json; done; done
for g in r6f_pivflank_before_fix2 r6f_pivflank_before_fix3; do for o in $O/$g/*/; do on=$(basename $o); for r in $o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/sitl/before_fixes/${g}__${on}__$n.json; done; done; done
for r in $O/r6f_pivflank_before_fix2/a/runs/*/; do gzip -c $r/trace.json > $T/sitl/traces/r6f_pivflank_before_fix2__a__$(basename $r).json.gz; done
for r in $O/r6f_pivflank_before_fix3/b/runs/*/; do gzip -c $r/trace.json > $T/sitl/traces/r6f_pivflank_before_fix3__b__$(basename $r).json.gz; done
for r in $O/r6f_suite_before_dirfix/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/sitl/before_fixes/r6f_suite_before_dirfix__$n.json; done
for o in r6_repro_near26 r6v_near26 r6v_near20 r6v_run20 r6f_near26 r6f_near20 r6f_run26 r6f_run20 r6f_gapwalk26 r6s2_near26 r6s2_near20 r6s2_run26 r6s2_run20 r6s2_gapwalk26 r6f_pivflank_a r6f_pivflank_a2 r6f_pivflank_b; do
  for r in $O/$o/runs/*/; do n=$(basename $r); [ -f $r/trace.json ] && gzip -c $r/trace.json > $T/sitl/traces/${o}__$n.json.gz; done; done
cd $S/cad && cp build_model.py draw_sheets.py draw_sheets_r51.py r6_sheets_patch.py r6_sheets_patch2.py make_pdf.py $T/drawing_scripts/
cp $R/R6_README.txt $T/README.txt
cd $T && rm -f "$1" && zip -q -r "$1" . && echo "zip: $(unzip -l "$1" | tail -1)" && du -sh "$1"
