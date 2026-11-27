#!/bin/bash
# Assembles the evidence pack for the afternoon's tests (results as JSON / text only; the large per-run traces are left out).
set -e
E=/home/claude/evidence2/b2f_tests_part2_evidence_2026-11-13; mkdir -p /home/claude/evidence2; [ -d $E ] && mv $E /home/claude/evidence2/old_$(date +%s); mkdir -p $E/{my_scripts,gate_results,lane_results,driving_tests}
cp /home/claude/b2f_review/variants/{make_simB2hx.py,make_lanerun_x.py,lane_chain.sh,runH2w.py,make_companion_x.py} $E/my_scripts/
cd /home/claude/s0; cp run_batch.py var_lean_pert.txt var_base_pert.txt var_wide.txt var_wide2.txt var_lean260.txt sitl_run.sh sitl_run_x.sh sitl_orchestrate.sh sitl_status.py sitl_compare.py sitl_q_*.txt cost_steps_v2.json lane_chain_runs_*.out $E/my_scripts/ 2>/dev/null || true
R=/home/claude/b2f_run/revG/sim/cg/h2/res
for t in _lean _mj401 _lean260 _w15_lean _pm110_lean _pm090_lean _pmu085_lean _pcrr09_lean _pm110_mj401 _pm090_mj401 _pmu085_mj401 _pcrr09_mj401; do mkdir -p $E/gate_results/tag$t; cp $R/B2F_*$t.json $E/gate_results/tag$t/ 2>/dev/null || true; done
cp $R/gate_B2F_*.json $E/gate_results/ 2>/dev/null || true
L=/home/claude/b2f_run/work/b2f_lanephys
for d in runs_base_spf runs_lean runs_lean_ramp runs_lean_c260; do for r in $L/$d/*/; do n=$(basename $r); [ -f $r/result.json ] && { mkdir -p $E/lane_results/$d/$n; cp $r/result.json $E/lane_results/$d/$n/; }; done; done
for c in base472 fix472 fix4; do mkdir -p $E/driving_tests/$c; cp /home/claude/sitl_out/$c/score.md /home/claude/sitl_out/$c/score.json $E/driving_tests/$c/ 2>/dev/null || true
  for r in /home/claude/sitl_out/$c/runs/*/; do n=$(basename $r); [ -f $r/result.json ] && { mkdir -p $E/driving_tests/$c/runs/$n; cp $r/result.json $E/driving_tests/$c/runs/$n/; }; done; done
cp /home/claude/s0/sitl_compare_out.txt $E/driving_tests/ 2>/dev/null || true
cd /home/claude/evidence2 && rm -f b2f_tests_part2_evidence_2026-11-13.zip.tmp && python3 -c "
import shutil; shutil.make_archive('b2f_tests_part2_evidence_2026-11-13','zip','.','b2f_tests_part2_evidence_2026-11-13')"
ls -la /home/claude/evidence2/*.zip; du -sh $E
