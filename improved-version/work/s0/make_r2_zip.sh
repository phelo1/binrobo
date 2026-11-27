#!/bin/bash
# Collect the revision 2 scripts, inputs and result files into one folder and zip it. usage: make_r2_zip.sh <out_zip>
set -e
T=/home/claude/s0/r2_pack; rm -rf $T.old; [ -d $T ] && mv $T $T.old; mkdir -p $T/{model_switches,inputs,command_lists,results_gate,results_lane,results_lanefit,results_driving,drawing_scripts}
V=/home/claude/b2f_review/variants; R=/home/claude/b2f_run/revG/sim/cg/h2/res; L=/home/claude/b2f_run/work/b2f_lanephys
cp $V/make_simB2hx.py $V/make_lanerun_x.py $V/lane_chain.sh /home/claude/s0/lane_r2.sh /home/claude/s0/lane_r2_extra.sh /home/claude/s0/run_batch.py $T/model_switches/
cp /home/claude/b2f_run/sitl/b2f/scripts/b2f_runner_x.py /home/claude/b2f_run/sitl/b2f/scripts/b2f_companion_x.py /home/claude/s0/sitl_run_x.sh $T/model_switches/
cp $V/mass_cgB2_r2.json $V/mass_cgB2_r2b.json $V/mass_cgB2_B2F_S12.json $V/mass_cgB2_imp.json $T/inputs/
cp /home/claude/s0/lanefit_r2/R2_b2r.json /home/claude/s0/lanefit_r2/R2s_b2r.json /home/claude/s0/lanefit_r2/lanefit_ckpt_x.py $T/inputs/
cp /home/claude/s0/var_r2b.txt /home/claude/s0/var_r2b.out /home/claude/s0/chain_r2c.sh /home/claude/s0/var_r2.txt /home/claude/s0/var_r2_pert.txt /home/claude/s0/var_b2f_cmp.txt /home/claude/s0/sitl_q_r2_i0.txt /home/claude/s0/sitl_q_r2_i1.txt $T/command_lists/
cp /home/claude/s0/var_r2.out /home/claude/s0/var_r2_pert.out $T/command_lists/ 2>/dev/null || true
cp /home/claude/s0/var_b2f_cmpA.out /home/claude/s0/var_b2f_cmpB.out $T/command_lists/ 2>/dev/null || true
cp $R/*_r2.json $R/*_r2_s?03.json $R/*_r2b.json $R/*_r2b_s?03.json $R/*_b2fS12*.json $R/*_mj401_s?03.json $T/results_gate/ 2>/dev/null || true
for d in runs_r2 runs_r2_pf runs_r2b_pf; do for r in $L/$d/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_lane/${d}__$n.json; done; done
cp /home/claude/s0/lane_chain_runs_r2.out /home/claude/s0/lane_chain_runs_r2_pf.out /home/claude/s0/lane_chain_runs_r2b_pf.out $T/results_lane/ 2>/dev/null || true
cp /home/claude/s0/lanefit_r2/res/lanefit_R2_b2r.json /home/claude/s0/lanefit_r2/res/lanefit_R2s_b2r.json /home/claude/s0/lanefit_r2/res/lanefit_B2Fctl_b2r.json $T/results_lanefit/ 2>/dev/null || true
if [ -d /home/claude/sitl_out/r2/runs ]; then for r in /home/claude/sitl_out/r2/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_driving/$n.json; done; cp /home/claude/sitl_out/r2/progress.txt /home/claude/sitl_out/r2/score.json $T/results_driving/ 2>/dev/null || true; fi
if [ -d /home/claude/sitl_out/b2fS12/runs ]; then mkdir -p $T/results_driving_B2F_heavier_frame; for r in /home/claude/sitl_out/b2fS12/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && cp $r/result.json $T/results_driving_B2F_heavier_frame/$n.json; done; fi
cd /home/claude/s0/cad && cp build_model.py draw_sheets.py render.py get_poses.py check_model.py make_pdf.py $T/drawing_scripts/
[ -f /home/claude/s0/R2_README.txt ] && cp /home/claude/s0/R2_README.txt $T/README.txt
cd $T && rm -f "$1" && zip -q -r "$1" . && echo "zip: $(unzip -l "$1" | tail -1)"
