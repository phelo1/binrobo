#!/bin/bash
# Collect the revision 4 scripts, inputs and result files into one folder and zip it. usage: make_r4_zip.sh <out_zip>
set -e
T=/home/claude/s0/r4_pack; rm -rf $T.old; [ -d $T ] && mv $T $T.old; mkdir -p $T/{model_switches,inputs,command_lists,results_mechanical,results_torque_boost,results_maps_and_safety,results_exploration_on_rev3,results_lane,results_driving,results_driving_camera_stress,results_driving_other_speed_rules,tables,drawing_scripts}
V=/home/claude/b2f_review/variants; R=/home/claude/b2f_run/revG/sim/cg/h2/res; RX=/home/claude/b2f_run/revG/sim/cg/h2/res_r4x; X4=/home/claude/b2f_run/revG/sim/cg/h2/res_x4; L=/home/claude/b2f_run/work/b2f_lanephys; S=/home/claude/s0
cp $V/make_simB2hx.py $V/make_lanerun_x.py $V/lane_chain.sh $S/run_batch.py $S/r4/env_r4.sh $S/r4/runY.py $S/r4/chain_r4.sh $S/r4/chain_r4_lane.sh $S/r4/chain_r4_sitl.sh $S/sitl_run_x.sh $T/model_switches/
cp $L/lanerun_x.py /home/claude/b2f_run/sitl/b2f/scripts/b2f_runner_x.py /home/claude/b2f_run/sitl/b2f/scripts/b2f_companion_x.py $T/model_switches/
cp $V/mass_cgB2_r4.json $V/mass_cgB2_r3s.json $S/r4/solids_r4.json $S/r4/mass_from_solids_r4.py $S/cad/solids_list.py $T/inputs/
cp $S/r4/mk_r4_campaign.py $S/r4/mk_c_r4.py $S/r4/mk_x4.py $S/r4/q_r4_*.txt $S/r4/q_r4_*.out $S/r4/q_r4b_sel.txt $S/r4/q_r4b_sel.out $S/r4/q_x4_*.txt $S/r4/sitl_q_r4*.txt $T/command_lists/ 2>/dev/null || true
cp $R/*_r4.json $R/*_r4_s?03.json $R/*_r4_*.json $R/gate_B2F__r4.json $T/results_mechanical/ 2>/dev/null || true
cp $R/*_r4b.json $R/*_r4b_*.json $T/results_torque_boost/ 2>/dev/null || true
cp $RX/*.json $T/results_maps_and_safety/ 2>/dev/null || true
cp $X4/*.json $T/results_exploration_on_rev3/ 2>/dev/null || true
for d in runs_r4_pf runs_r4_b100 runs_r4_sharp; do for r in $L/$d/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_lane/${d}__$n.json; done; cp $S/lane_chain_$d.out $T/results_lane/ 2>/dev/null || true; done
cp $S/lane_stuck.py $S/r4/lane_r4.log $T/results_lane/ 2>/dev/null || true
for o in r4; do for r in /home/claude/sitl_out/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_driving/$n.json; done; cp /home/claude/sitl_out/$o/progress.txt /home/claude/sitl_out/$o/score.json $T/results_driving/ 2>/dev/null || true; done
for o in r4camA r4camB r4camC r4camBnoseat; do for r in /home/claude/sitl_out/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_driving_camera_stress/${o}__$n.json; done; cp /home/claude/sitl_out/$o/progress.txt $T/results_driving_camera_stress/${o}__progress.txt 2>/dev/null || true; done
for o in r4_ruleA_partial r4ruleC; do for r in /home/claude/sitl_out/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_driving_other_speed_rules/${o}__$n.json; done; done
cp $S/r4/chain_r4_sitlC.sh $S/r4/chain_r4_lane2.sh $T/model_switches/ 2>/dev/null || true
cp $S/r4/sitl_sum_r4.py $S/r4/cmp_boost.py $T/tables/ 2>/dev/null || true
cp $S/sitl_r3_table.py $S/r4/collect_r4.py $S/r4/struct_r4.py $S/r4/tab_pstop.py $S/r4/tab_c_r4.py $S/r4/tab_x4.py $S/r4/tab_grab.py $T/tables/ 2>/dev/null || true
cp $S/r4/pack_tables/* $S/r4/mass_table_r4.md $S/r4/clash_r4.json $S/r4/facts.json $S/r4/pstop_r4.json $T/tables/ 2>/dev/null || true
cd $S/cad && cp build_model_r3.py r4_patch.py build_model.py draw_sheets_r3.py r4_sheets_patch.py draw_sheets.py render.py get_poses.py clash_check.py check_model.py make_pdf.py solids_list.py $T/drawing_scripts/
[ -f $S/R4_README.txt ] && cp $S/R4_README.txt $T/README.txt
cd $T && rm -f "$1" && zip -q -r "$1" . && echo "zip: $(unzip -l "$1" | tail -1)"
