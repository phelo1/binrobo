Files for the other agent, 14 November 2026 (goes with REPLY_to_review_2026-11-14.md)

Model
  make_simB2hx.py          writes h2/simB2hx.py from your unchanged h2/simB2h.py. Switches, all off by default:
                             X_LIFT_RANGE, X_ROCKER, X_ROCK_DEG, X_ROCK_Z                      (used for every result up to 13 Nov)
                             X_ROCK_M (beam mass), X_DOCK_TRIES, X_DOCK_DYMAX                  (added 14 Nov)
  make_simB2hx_v1.py       the generator exactly as used up to 13 Nov
  simB2hx_vs_simB2h.diff   the whole difference between your sim and mine
  The fixed pad and carry lift use your own settings: CGB_GEO='{"pad_ret":0.0,"lift_extra1":0.15}' B2F_PAD_IN=-0.005
  The 700 mm comb uses your own switch: CMP_COMB_HW=0.35

Mass
  mass_cgB2_imp.json       corrected table for the improved version (95.50 kg by your table convention, 96.40 kg in the built model; the 5.46 kg rocker body is set with X_ROCK_M, not in the rows)
  mass_cgB2_imp_S12.json   the same plus the S12 sections (114.73 kg by the table, 115.63 kg built). No test has been run with it yet.
  model_mass.py            prints the mass of the model MuJoCo actually builds, for the environment it is run in

Simulator version
  wheel_edge.py            40-line check. If it prints contact_normal_deg_from_vertical near 90, the MuJoCo in use treats a kerb corner as a wall
                           (3.13.0 to 3.17.0 do; 3.2 to 3.12 and 4.0.1 do not). All my results are on 4.0.1 unless a file name says mj317.

Lane
  make_lanerun_x.py, lane_chain.sh, pothole_chain.sh, lane_after.sh
  LANE_VARIANTS.txt        every lane run I made: folder, run, lane variant, verdict

Pick-ups
  grab_table.py            one line per batch: captured, false holds, sideways error on first arrival
  grab_diag.py             re-runs chosen samples and prints which part of the scorer's "seated" test fails

commands/                  the command lists (your runH2.py command lines with my environment variables)
  var_lean.txt             improved version, mass as run up to 13 Nov (tag _lean)
  var_lean287.txt          pin at 287 mm (tag _lean287)
  var_leanm.txt            corrected mass (tag _leanm), plus 90 extra clip-lid pick-ups at each mass (tags _leanm_sNNN, _lean_sNNN)
  var_c700.txt             corrected mass, 700 mm comb, three re-approaches, refuse above 25 mm (tags _leanm_c700b, _leanm_c700b_sNNN)

results/gate/              scorecards and every batch named above; step cases on 3.17.0 (mj317) and 4.0.1
results/lane/              result.json of every lane run of mine listed in LANE_VARIANTS.txt
