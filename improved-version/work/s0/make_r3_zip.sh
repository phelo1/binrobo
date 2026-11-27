#!/bin/bash
# Collect the revision 3 scripts, inputs and result files into one folder and zip it. usage: make_r3_zip.sh <out_zip>
set -e
T=/home/claude/s0/r3_pack; rm -rf $T.old; [ -d $T ] && mv $T $T.old; mkdir -p $T/{model_switches,inputs,command_lists,results_mechanical,results_first_passes,results_B2F_loads_on_4.0.1,results_lane,results_driving,results_driving_camera_stress,tables,drawing_scripts}
V=/home/claude/b2f_review/variants; R=/home/claude/b2f_run/revG/sim/cg/h2/res; L=/home/claude/b2f_run/work/b2f_lanephys; S=/home/claude/s0
cp $V/make_simB2hx.py $V/make_lanerun_x.py $V/lane_chain.sh $S/lane_r3.sh $S/run_batch.py $S/r3/env_r3.sh $S/r3/s7_trace.py $S/grab_diag.py $S/model_mass.py $T/model_switches/
cp /home/claude/b2f_run/sitl/b2f/scripts/b2f_runner_x.py /home/claude/b2f_run/sitl/b2f/scripts/b2f_companion_x.py $S/sitl_run_x.sh $S/chain_r3_sitl.sh $T/model_switches/
cp $V/mass_cgB2_r3s.json $V/mass_cgB2_r2b.json $S/r3/solids_r3_final.json $S/r3/mass_from_solids.py $S/cad/solids_list.py $T/inputs/
cp $V/mass_cgB2_r3.json $V/mass_cgB2_r3pre.json $V/mass_cgB2_r3pre_nb.json $S/r3/make_mass_r3.py $T/inputs/ 2>/dev/null || true
cp $S/r3/q_r3sh.txt $S/r3/q_r3sh.out $S/r3/q_r3sh2.txt $S/r3/q_r3sh2.out $T/command_lists/ 2>/dev/null || true
cp $S/r3/mk_r3_campaign.py $S/r3/q_r3_all.txt $S/r3/q_r3_all.out $S/r3/q_b2f_loads.txt $S/r3/q_b2f_loads.out $S/r3/q_r3_ballast.txt $S/r3/q_r3_loads.txt $S/sitl_q_r3_i0.txt $S/sitl_q_r3_i1.txt $S/sitl_q_r3cam.txt $T/command_lists/ 2>/dev/null || true
cp $R/*_r3.json $R/*_r3_s?03.json $R/*_r3w0.0??.json $R/*_r3sh.json $R/*_r3sh2.json $R/*_r3flat.json $R/*_r3noph.json $R/gate_B2F__r3.json $T/results_mechanical/ 2>/dev/null || true
cp $R/*_r3a.json $R/*_r3a_s?03.json $R/*_r3c.json $R/*_r3c_s?03.json $R/*_r3d.json $R/*_r3n.json $R/*_r3p.json $T/results_first_passes/ 2>/dev/null || true
cp $R/*_mj401.json $T/results_B2F_loads_on_4.0.1/ 2>/dev/null || true
cp $S/r3/s7_trace_*.json $T/results_first_passes/ 2>/dev/null || true
for d in runs_r3_pf runs_r3_flat runs_r3_sh runs_r3_t80; do for r in $L/$d/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_lane/${d}__$n.json; done; done
cp $S/lane_chain_runs_r3_flat.out $S/lane_chain_runs_r3_sh.out $S/lane_chain_runs_r3_t80.out $T/results_lane/ 2>/dev/null || true
cp $S/lane_chain_runs_r3_pf.out $S/lane_stuck.py $T/results_lane/ 2>/dev/null || true
for o in r3; do for r in /home/claude/sitl_out/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_driving/$n.json; done; cp /home/claude/sitl_out/$o/progress.txt /home/claude/sitl_out/$o/score.json $T/results_driving/ 2>/dev/null || true; done
for o in r3camA r3camB; do for r in /home/claude/sitl_out/$o/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_driving_camera_stress/${o}__$n.json; done; cp /home/claude/sitl_out/$o/progress.txt $T/results_driving_camera_stress/${o}__progress.txt 2>/dev/null || true; done
cp $S/sitl_r3_table.py $S/r3/collect_r3.py $S/r3/struct_r3.py $T/tables/
cp $S/r3/pack_tables/* $S/r3/mass_table_r3.md $S/r3/clash_r3.json $S/cad/clash_r2.json $S/r3/recount_r2b_summary.json $T/tables/ 2>/dev/null || true
cp $S/r3/nib_r2b_*.jsonl $T/tables/ 2>/dev/null || true
cd $S/cad && cp build_model_r2.py r3_patch.py build_model.py draw_sheets_r2.py r3_sheets_patch.py draw_sheets.py render.py get_poses.py clash_check.py check_model.py make_pdf.py solids_list.py $T/drawing_scripts/
[ -f $S/R3_README.txt ] && cp $S/R3_README.txt $T/README.txt
cd $T && rm -f "$1" && zip -q -r "$1" . && echo "zip: $(unzip -l "$1" | tail -1)"
