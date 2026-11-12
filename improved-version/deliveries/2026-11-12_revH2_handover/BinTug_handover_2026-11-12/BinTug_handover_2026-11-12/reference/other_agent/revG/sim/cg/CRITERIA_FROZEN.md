# BT-6 concept gate (A' vs B) - acceptance criteria, FROZEN before any gate run

Frozen: 2026-11-11 07:51 +03 (Asia/Riyadh), before the first gate run. The sha256 of this file is logged in
docs/reviews/PROGRESS_concept.md at freeze time. No criterion, threshold, test definition or bin choice may change after
this point. Design-calibration runs (pad position/preload for A', lifter geometry for B, ballast) are allowed before the
gate runs and are labelled "calibration"; they are not gate results. Any later change of a DESIGN parameter means the whole
affected test group is re-run and both versions are reported.

Common model terms (both concepts, identical): sim_g5 bin models from bins_g5.py (hull, two-box inertia, lid, wheel
frictionloss = crr), contact solref 0.008 / solimp 0.9-0.99, elliptic cone, noslip 3, dt 0.5 ms (0.25 ms for the dt
repeats), drive = velocity servo kv 150 with torque cap 60 N m per wheel (= MY1016ZL-75-class motor at a 25 A current
limit, see report), brake = kv 20000 with 150 N m cap, accel ramp 0.6 m/s^2, same heading-hold controller, 330 mm drive
wheels, 200 mm castors, tug tyre/castor crr 0.06 (sim_g5 frictionloss formula), camera model sigma 8 mm with one re-dock.
"Full 240 L" = ESE 240 SL at 110 kg gross unless stated.

| id | test | definition | PASS (per run) | concept passes the item if |
|----|------|------------|----------------|------------------------------|
| G1 | Grab MC | 3 bin types: Weber 140 L (WEB140), ESE 240 SL (ESE240SL), ESE 240 CL lowest handle (ESE240CL); 30 runs each; mc_g5 sampler: lateral +/-80 mm, yaw +/-6 deg, ground mu 0.3-0.8, hook/comb mu 0.2-0.5, lid closed 70 %/ajar, fill alternating empty/full, bar section and handle/comb spread from bins_g5; one re-dock allowed | bin captured and held at the end of the grab (A': tipped to tow pose with bar in both cups; B: lifted, both bin wheels >= 30 mm off the ground, comb lip seated) | >= 28/30 per bin type AND >= 87/90 pooled AND 0 false holds (claim while not captured) AND 0 bins knocked over (> 30 deg) |
| G2 | Climb 12 % | full 240 L, 5 m at 0.5 m/s command up 12 %, mu in {0.30, 0.25, 0.22} x bin-wheel crr in {0.06, 0.09} (6 runs) | 5 m in <= 25 s AND hold creep < 0.05 m over 3 s brake hold AND bin still held | 6/6 |
| G3 | 40 mm step | full 240 L, 0.5 m/s, sharp 40 mm step (a) left wheels only, (b) full width (both sides), mu 0.6 | reaches 4.5 m in <= 25 s AND bin held throughout AND tug roll/pitch < 15 deg AND [A': hitch peak <= 15 deg, no kingpin stop contact (|yaw| < 39 deg)] AND [B: no bin-body/bin-wheel ground contact, comb lip stays seated] | 2/2 |
| G4 | E-stop 12 % down | full 240 L, mu 0.30, 0.5 m/s, spring brakes; A': tug leading downhill (yaw pin in before descent, R7 rule); B: both orientations (castors leading, bin leading) | stop <= 0.5 m AND slide after stop < 0.05 m AND bin held AND no tip (|roll|,|pitch| < 15 deg) | all runs |
| G5 | Tow/carry stability | full 240 L, flat mu 0.6: 2 m straight 0.5 m/s, 90 deg turn, slalom +/-25 deg, e-stop (tow_g5 towstab sequence). B additionally: 180 deg pivot on the spot | bin held throughout AND roll < 10 deg AND [A': hitch < 39 deg (no stop contact)] AND [B: pivot swept diameter <= 3.2 m] | all runs |
| G6 | Release / set-down | 3 bins (WEB140, ESE240CL, ESE240SL250) x {flat, 12 % up, 12 % down} x {full, empty} = 18 cases; "12 % up" = tug facing uphill. No release rule exclusions | released (gripper clear of the bin) AND bin standing (abs tilt < 8 deg, speed < 0.05 m/s at the end) AND no tip (> 30 deg) AND no drop | 18/18, 0 tips, 0 drops (HOLD = fail for the gate, but counted as safe) |
| G7 | dt repeat | climb mu 0.25 crr 0.09, step40 one side, e-stop 12 % down: repeated at dt 0.25 ms | verdict unchanged AND climb time within 10 % | 3/3 |
| G8 | Static stability | full 240 L at 110 kg and 60 kg gross, static on 12 % grade facing up, down, and 12 % cross-slope both sides (sim settle 3 s) + hand calc | no wheel lift-off: each drive wheel >= 100 N, castors (sum) >= 50 N; hand-calc static tip-over angle >= 20 deg in every direction | all 8 poses |
| G9 | Mass | operating mass incl. ballast | <= 120 kg | - |

Gate decision rule (fixed now): a concept "clears the gate" only if G1-G9 all pass. If exactly one clears, recommend it.
If both clear, recommend the cheaper one unless a named risk outweighs the cost difference. If neither clears, recommend
the one whose failures are closable by a named, costed design change, and say plainly that it has NOT cleared the gate.
Reported, not gating: kingpin/comb/lip loads, actuator force, peak wheel torque, energy per metre, U-turn capability.
