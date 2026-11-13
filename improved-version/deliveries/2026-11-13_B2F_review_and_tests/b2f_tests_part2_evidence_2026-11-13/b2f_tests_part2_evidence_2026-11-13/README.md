# Evidence pack: B2-F tests, part 2 (13 November 2026)

Results are JSON or text. The per-run traces of the driving tests (about 50 MB each) are left out.
None of the other agent's files were edited. My variants are generated from their files by the `make_*.py` scripts, with every change behind a switch that is off by default.

## my_scripts
- `make_simB2hx.py`: model switches (lift travel, castor pivot). Pad position and carry lift use the other agent's own settings.
- `make_lanerun_x.py`, `lane_chain.sh`: lane runs with a chosen model, lane variant and result folder.
- `runH2w.py`: grab trials with wider start offsets (scales the sampled offsets, same bins and seeds).
- `make_companion_x.py`: driving-code variant with five switches (yard exit, camera check, sign fix, smooth approach, smooth re-alignment) and a runner variant that can use a second, third or fourth simulator instance.
- `run_batch.py`, `var_*.txt`: gate command lists. `sitl_*.sh`, `sitl_q_*.txt`, `sitl_status.py`, `sitl_compare.py`: driving-test runners, run lists and summaries.
- `cost_steps_v2.json`: the cost steps in the write-up.

## gate_results (MuJoCo 4.0.1)
- `tag_mj401`: B2-F as designed. `tag_lean`: improved version. `tag_lean260`: improved version with 260 mm castors.
- `tag_p*_lean`, `tag_p*_mj401`: the four stress variations for each version. `tag_w15_lean`: grabs from start offsets 1.5 times wider.
- `gate_B2F__*.json`: scorecards from the other agent's own scorer.

## lane_results (sharp 40 mm step, trench covered, pothole filled)
- `runs_base_spf`: B2-F as designed. `runs_lean`: improved version. `runs_lean_ramp`: improved, 1:4 ramp at the step. `runs_lean_c260`: improved, 260 mm castors (its P1 is a copy of the `runs_lean` P1, used as the starting state).

## driving_tests (ArduRover 4.7.2 x86-64 from the pack, `ARMING_SKIPCHK -1` added)
- `base472`: the other agent's code unmodified, 58 of the 60 scenarios.
- `fix472`: three fixes (yard exit, camera check, sign fix), 8 scenarios; stopped when the fourth fix was added.
- `fix4`: four fixes, all 60 scenarios. `fix5`: four fixes plus smooth re-alignment, 4 scenarios.
- `score.md` and `score.json` in each folder come from the other agent's frozen scorer. `sitl_compare_out.txt` sets the campaigns beside their stored result.
