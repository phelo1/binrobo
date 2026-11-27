#!/bin/bash
# Collect the revision 6.1 scripts, settings and result files into one folder and zip it. usage: make_r61_zip.sh <out_zip>
set -e
T=/home/claude/s0/r61_pack; rm -rf $T; mkdir -p $T/{software/patches,settings,chains,tables,sitl/traces,sitl/before_fixes,drawing_scripts}
S=/home/claude/s0; R=$S/r61; O=/home/claude/sitl_out; SC=/home/claude/b2f_run/sitl/b2f/scripts
cp $SC/b2f_r6.py $SC/b2f_companion_x.py $SC/b2f_runner_x.py $T/software/
cp $SC/b2f_r6_r60.py $SC/b2f_companion_x_r60.py $SC/b2f_runner_x_r60.py $T/software/
cp $R/harness.py $R/code_final.md5 $R/code_frozen_0218.md5 $T/software/; cp $R/patches/* $T/software/patches/
cp $R/env_r61_start.sh $R/env_r61_fast.sh $R/env_r61_fast_leaf.sh $R/env_r61_mid.sh $R/env_r61_fast_v10.sh $S/r6/env_r6.sh $S/r6/env_r6_fast.sh $S/r6/env_r6_fast_leaf.sh $S/r6/env_r6_mid.sh $S/r5/sitl_env_r5.sh $T/settings/
cp $R/chain_*.sh $R/stress.sh $R/stress2.sh $R/run2.sh $R/walker_table.sh $R/chain.log $R/q_start_i0.txt $R/q_start_i1.txt $S/r6/q_s1a_7.txt $S/r6/q_s1b_7.txt $S/r6/q_s5a_7.txt $S/r6/q_s5a_11_23.txt $S/sitl_run_x.sh $S/r4/sitl_q_r4_i0.txt $S/r4/sitl_q_r4_i1.txt $T/chains/
cp $R/tables/* $R/stress_tab.py $R/stress_md2.py $R/react_tab.py $R/trips_md.py $R/mk_tables.sh $R/mk_facts_r61.py $R/facts_r61.json $S/r6/trips_tab.py $S/r6/pivot_rates.py $S/r6/suite_extra.py $S/r6/show.py $S/r6/piv_an.py $S/r5/r5_score.py $T/tables/
for o in $(ls $O | grep -E "^r61"); do
  [ $o = r61_before_fixes ] && continue
  for r in $O/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/sitl/${o}__$n.json; done
done
for o in $O/r61_before_fixes/*/; do on=$(basename $o); for f in $(find $o -name result.json); do n=$(basename $(dirname $f)); cp $f $T/sitl/before_fixes/${on}__$n.json; done; done
# traces (gzip): the people cases the note discusses in detail, and the turn tests with their baselines
for o in r61f_near26 r61v_near26 r61s_near26 r61b1_near26 r61b2_near26 r61f_near20 r61b2_near20 r61b2_run26 r61f_run20 r61s_run20 r61f_side14 r61s_side14 r61f_hugstand31 r61b2_hugstand31 r61s_hugstand \
         r61f_turn_a r61f_turn_a2 r61f_turn_b r61f_turn_c r61f_turn_y r61x_turn_c_nowalk r61x_turn_y_nowalk; do
  for r in $O/$o/runs/*/; do n=$(basename $r); [ -f $r/trace.json ] && gzip -c $r/trace.json > $T/sitl/traces/${o}__$n.json.gz; done; done
# the suite mission with the two lane stops after a satellite outage (note, section 4.1)
gzip -c $O/r61f_suite/runs/s3a__s11/trace.json > $T/sitl/traces/r61f_suite__s3a__s11.json.gz
cd $S/cad && cp build_model.py draw_sheets.py draw_sheets_r6.py make_pdf.py $T/drawing_scripts/
cp $R/R61_README.txt $T/README.txt
cd $T && rm -f "$1" && zip -q -r "$1" . && echo "zip: $(unzip -l "$1" | tail -1)" && du -sh "$1"
