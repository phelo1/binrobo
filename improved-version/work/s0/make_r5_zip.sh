#!/bin/bash
# Collect the revision 5 scripts, inputs and result files into one folder and zip it. usage: make_r5_zip.sh <out_zip>
set -e
T=/home/claude/s0/r5_pack; rm -rf $T.old; [ -d $T ] && mv $T $T.old
mkdir -p $T/{model_switches,inputs,command_lists,results_mechanical,results_maps_and_safety,results_lane,results_driving,results_driving_first_pass,results_driving_extras,results_driving_fault_tests,results_driving_person_tests,results_keep_left_trials,tables,drawing_scripts}
V=/home/claude/b2f_review/variants; R=/home/claude/b2f_run/revG/sim/cg/h2/res; RX=/home/claude/b2f_run/revG/sim/cg/h2/res_r5x; L=/home/claude/b2f_run/work/b2f_lanephys; S=/home/claude/s0; O=/home/claude/sitl_out
SC=/home/claude/b2f_run/sitl/b2f/scripts
cp $V/make_simB2hx.py $V/make_lanerun_x.py $V/lane_chain.sh $S/run_batch.py $S/r5/env_r5.sh $S/r5/sitl_env_r5.sh $S/r4/runY.py $S/sitl_run_x.sh $S/r5/chain_r5*.sh $S/r5/chain_r5*.log $S/r5/lane_r5.log $T/model_switches/ 2>/dev/null || true
cp $L/lanerun_x.py $SC/b2f_runner_x.py $SC/b2f_companion_x.py $S/r5/r5b_patch_companion.py $S/r5/r5b_code.md5 $T/model_switches/
cp $SC/b2f_companion_x_r5a.py $T/model_switches/b2f_companion_x_first_pass.py; cp $SC/b2f_companion_x_r4.py $T/model_switches/b2f_companion_x_rev4.py
cp $S/r5/b2f_companion_x_r5b_frozen.py $T/model_switches/b2f_companion_x_as_run_for_the_60.py; cp $S/r5/b2f_companion_x_r5b_widecorridor_trial.py $T/model_switches/b2f_companion_x_widecorridor_trial.py; cp $S/r5/b2f_runner_x_r5b_frozen.py $T/model_switches/b2f_runner_x_as_run_for_the_60.py
cp $V/mass_cgB2_r5.json $V/mass_cgB2_r4.json $S/r5/solids_r5.json $S/r5/mass_from_solids_r5.py $S/cad/solids_list.py $T/inputs/
cp $S/r5/mk_r5.py $S/r5/mk_r5_campaign.py $S/r5/q_r5_*.txt $S/r5/q_r5_*.out $S/r5/sitl_q_*.txt $S/r4/sitl_q_r4_i0.txt $S/r4/sitl_q_r4_i1.txt $T/command_lists/ 2>/dev/null || true
cp $R/*_r5.json $R/*_r5_*.json $R/gate_B2F__r5.json $T/results_mechanical/ 2>/dev/null || true
cp $RX/*.json $T/results_maps_and_safety/ 2>/dev/null || true
for d in runs_r5_pf runs_r5_w30 runs_r5_w22; do for r in $L/$d/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_lane/${d}__$n.json; done; cp $S/lane_chain_$d.out $T/results_lane/ 2>/dev/null || true; done
pk() { # pk <out name> <dest dir> : result.json of every run, progress and score
  for r in $O/$1/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/$2/${1}__$n.json; done
  cp $O/$1/progress.txt $T/$2/${1}__progress.txt 2>/dev/null || true; cp $O/$1/score.json $T/$2/${1}__score_b2f_script.json 2>/dev/null || true; cp $O/$1/score.md $T/$2/${1}__score_b2f_script.md 2>/dev/null || true; }
pk r5b results_driving
pk r5a_prefix results_driving_first_pass
for o in r5b_fix r5b_ret1630 r5b_m198 r5b_camonly; do [ -d $O/$o ] && pk $o results_driving_extras; done
for o in $(ls $O | grep -E "^r5bf_fault_|^r5b_fault_|^r5b1_fault_|^r5a_gps_|^r5b_gps_|^r5b_bend40$|^r5a_bend40$|^r5a_s4a16$|^r5b_s4a16$" | grep -v trash); do pk $o results_driving_fault_tests; done
for o in $(ls $O | grep -E "^r5b0_person|^r5b00_person|^r5b01_person|^r5b_person|^r5b_s5a_final$"); do pk $o results_driving_person_tests; done
for o in r5kl30 r5kl35 r5kl42 r5kl42bk; do [ -d $O/$o ] && pk $o results_keep_left_trials; done
cp $S/r5/pack_tables/* $S/r5/mass_table_r5.md $S/r5/clash_r5.json $S/r5/facts.json $T/tables/ 2>/dev/null || true
cp $S/r5/r5_score.py $S/r5/struct_r5.py $S/r5/people_mc.py $S/r5/cost_r5.py $S/r5/tab_a_r5.py $S/r5/ana/*.py $S/r4/collect_r4.py $S/r4/tab_pstop.py $S/r4/sitl_sum_r4.py $S/sitl_r3_table.py $T/tables/ 2>/dev/null || true
cd $S/cad && cp build_model_r4.py r5_patch.py build_model.py draw_sheets_r4.py r5_sheets_patch.py draw_sheets.py render.py get_poses.py clash_check.py check_model.py make_pdf.py solids_list.py $T/drawing_scripts/
[ -f $S/R5_README.txt ] && cp $S/R5_README.txt $T/README.txt
cd $T && rm -f "$1" && zip -q -r "$1" . && echo "zip: $(unzip -l "$1" | tail -1)"
