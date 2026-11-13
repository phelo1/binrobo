# PROGRESS - B2-F full-lane physics (MuJoCo) + videos

Started 2026-11-12 23:25 +03. Work dir: work/b2f_lanephys/ ; outputs /workspace/work/out/b2f_lane/phys/ ; test log docs/reviews/TESTLOG_B2F_lane_phys.md
CRITERIA_FROZEN.md sha256 at start: 2cf3f4ecdd104c6b50e0eb3e4b70616ebc287a80d2789030e6eb2249345b8a74 (matches 2cf3f4ec...8a74). Not edited.

## Declared before any run (trims, assumptions, mapping to the frozen criteria)
Model: revG/sim/cg/h2/simB2h.py unchanged (imported; B2_DOCK=front, H2_HULL=new, CGB_F9=1), frozen common terms (dt 0.5 ms,
contact solref/solimp, elliptic cone, noslip 3, kv150/60 N m drive, brake kv 20000/150 N m, 0.6 m/s^2 ramp), grab()/set_down()
firmware as in the gate. Only the ground plane is replaced by the lane world (wrapper of build_xml, as runX.py does).
World (lane_world.py):
- Lane centreline = OSM route.json xy (633.06 m), 3.6 m surface; height = EU-DEM 25 m profile (PCHIP) along s, flat cross-section,
  MuJoCo heightfield 0.25 m cells over the whole lane bbox. DATUM: z - 29.0 m.
- 12 % pitch (ASSUMED overlay): EU-DEM max is 7.9 % (10 m window, s 135-155); SRTM shows 12 % (25 m window). Grade forced to
  -12 % over s 138-152 (2 m blends), extra drop given back over s 154-194 so the lane end elevation is unchanged.
- Hedges: truth hedge face = 2.05 m - g6_features.hedge_offset(s, side) (irregularity + bulges incl. 2.9 m at s 500-516), gaps per
  HEDGE_GAPS, none in the yard (s<25) or the bell-mouth (s>621.06). Collision boxes 1 m long, pooled near the robot (moving window,
  48 boxes) for speed; metric uses the same piecewise face.
- Wet leaves (ASSUMED): mu 0.35 (tyre-on-wet-leaf) on s 128-165 (the 12 % pitch), 200-215, 470-490, 575-590; ground mu 0.6 elsewhere
  (frozen G3/G5 value). Implemented by switching the ground friction (priority 1) when the tug drive axle is inside a patch.
- Features (ALL ASSUMED chainages - no survey; placed on straight sections, profile linearised over the feature bed):
  step 40 mm DOWN outbound (up on return) at s 290.0; trench 40 mm deep x 0.20 m full width at s 455.0; pothole 60 mm deep
  0.40 x 0.25 m under the left wheel track (lat +0.40) at s 550.0. Sharp edges are box tiles over a lowered heightfield bed.
- Transit lane = PREPARED lane: step with 1:4 ramp (160 mm), trench covered flush; pothole as-is. As-is step/trench only in P5.
- Pads: home spot s 10.0 lat -1.4 (yard_home), pad A s 621.96 lat 1.35 (pad_mouth), from config_g6 / scenarios.
Controller: pure pursuit on the centreline (look-ahead 1.5 m), 0.5 m/s cap (0.3 m/s in yard/pad), hedge guard: lateral target
clamped so the body edge stays >= 0.4 m from the mapped hedge face. Pivots on the spot 0.10 m/s wheel speed.
Scenarios: P1 ESE240SL 110 kg home->pad A; P2 return empty (no-bin model) pad A->home, then collect empty ESE240SL (13 kg) at pad A
and carry it home (pivot with the bin at pad A); P3 WEB140 full (66 kg = bins_g5 fill_full) home->pad A; P4a 12 % downhill 110 kg
wet leaves stop+hold, P4b same uphill (pivot at s~172 first); P5 step: sharp drop 3 kN / 4 kN, 1:4 ramp down, sharp up-step 3 kN /
4 kN (pivot first), 1:4 ramp up, trench as-is, pothole; P6a person steps in 1.0 m ahead on the 12 % wet descent (e-stop), P6b dog
crossing at s~235 (soft stop, wait, resume); P7 night P1 with bin CG +60 mm, mass x1.1, mu x0.8, lights 17 W.
TRIMS: (1) P2 empty home->pad A outbound leg not simulated (tug placed at the docking start pose 1.2 m out from the emptied bin).
(2) P4/P5/P6 start from P1 snapshots (carried state) instead of a fresh grab. (3) One seed per scenario. (4) 140 L bin drawn as a
scaled 240 L CAD bin in the video.
Pass/fail mapping (frozen file, per run): grab = G1 per-run PASS; carry = bin captured throughout (seated AND bin wheels >= 30 mm
above the local surface), no bin-ground contact, tug |roll|,|pitch| < 15 deg (G3); hold = creep < 0.05 m over 3 s (G2);
e-stop = stop <= 0.5 m, slide < 0.05 m, held, no tip (G4); set-down = G6 PASS; plus truth hedge clearance >= 0 (S9 strict) and
static tip margin >= 0. Reported not gating: lift force peak (cap 3 kN model / 4 kN BOM), energy, time.
Energy: wheel mech power (positive only, no regen)/0.60 + lift mech power/0.30 + hotel 9 W (+ lights 17 W at night) - S9 constants.

## Log
- 23:40 world built (hfield 2122x993 @0.25 m, 22 s, cached hfield_cache.npz). Speed ~3.3x real time with grab+transit (9.7k steps/s raw).
- 23:52 P1 v1 complete (1323 s sim, 15.4 Wh) but the verdict was polluted: the carry flag stayed on during set_down, so the
  intended bin lowering counted as 'bin lost / ground contact / tip<0'. Code fix (carry off before set_down; per-step segment
  metrics). v1 kept as runs/_P1_v1_carryflag (transit read-out: wheel clear min 33.8 mm on the 1:4 ramp at s 290.3, lift force hits
  the 3,000 N model cap transiently at the ramp (s 290.3) and the pothole (s 550.1), hedge min 0.30 m at pad A). Re-running P1.
- 00:20 P1 v2 FAIL 'bin touched the ground 3,891 N' traced (diag_bg.py) to a WORLD BUG: the 1:4 ramp box was rotated the wrong way
  (a 1:4 rise from the lower level then a sharp 40 mm drop). Fixed (Ry(+th)); verified top surface 0 -> -41 mm over 163 mm.
  With the correct ramp the bin wheels dip to 13.7 mm clearance (no ground contact): geometric - the bin wheels trail the drive
  axle by ~0.24 m, so when the tug has stepped down 40 mm the bin wheels are still over the upper level (69 - 40 = ~29 mm, less
  with pitch dynamics). Applies to ANY 40 mm level drop (ramp or sharp), not only the actuator cap.
- 'Bin held' now evaluated exactly as the frozen runner (runB2.py step/estop): seated throughout AND bin-ground contact < 1 N
  throughout AND captured() (wheels >= 30 mm, seated) at the END of each carry segment. The instantaneous 30 mm dip is REPORTED
  (clear_min) but not gating, as in the gate. Declared before the P1 v3 run. v2 kept as runs/_P1_v2_rampsign. Re-running P1.
- 00:55 P5a-h, P4a done. P4b v1 'stalled' 0.0x m short of the hold point on the 12 % climb: controller artefact - the arrival
  profile commanded 0.02 m/s, and the frozen velocity servo (kv 150) gives only ~18 N m at that speed error, below the ~21 N m
  per wheel the 12 % climb needs. Fix: approach creep floor 0.06 m/s, arrival window 0.02-0.03 m (applies to runs after P1;
  P1 was not affected). P4b re-run; v1 kept as runs/_P4b_v1_lowspeed. P6a restarted (killed by a shell timeout, no result).
- 01:10 P6a/P6b scenario fixes (declared, before the reported runs): person now stands 5 s then walks off (v1 stood forever, robot
  waited); dog trigger 4.0 -> 2.4 m (v1 crossed 3.2 m ahead, no stop needed); controller starts 'clear' (v2 stopped 2 s at start).
  Done: P4a PASS, P4b PASS, P5a/b/c/f/h PASS, P5d/e FAIL (stall at the sharp up-step), P5g FAIL (trench), P6a PASS, P6b PASS.
  Next: P2a, P2c, P3, P7 transits, then videos.
- 2026-11-13 00:45 RESUMED after the previous run was lost (P1, P4a/b, P5a-h, P6a/b results intact; nothing re-run).
  P2a had completed before the loss: FAIL 'drive2 stalled at s 550.0'. Root cause (diag_p2a.py, recording): on the empty return
  (no bin, tug 93 kg) heading -s at lat 0.00, the right drive wheel (r 165 mm, lat +0.40) drops into the as-is 60 mm pothole
  (s 550.0-550.4, lat 0.275-0.525); climbing the far 60 mm edge needs a 50 deg contact angle (traction ratio 1.21 > mu 0.6), the
  other wheel keeps driving, the tug yaws 45 -> 97 deg off the lane heading and the anti-tip skid lands on the pothole tile. No
  progress for 12 s -> stall. (P1 / P5h crossed the same pothole loaded with 110 kg and passed.) Result stands as reported.
  DECLARED NOW, before any further run (no criteria change; supplementary runs, the as-is runs stay the scored ones):
  (a) P2c runs as declared (lane as prepared, pothole AS-IS). Its return drive now writes carried-state snapshots (snaps=True).
  (b) Supplementary 'pothole filled' runs P2a_pf (whole leg, pad A -> home, pothole cover tile flush) and P2c_pf (start from the
      P2c snapshot nearest s 556 if P2c stalls at the pothole; otherwise not needed) to test the rest of the return leg.
      Snapshots are now also written for no-bin drive legs (P2a_pf) - recording only, no physics change.
  (c) P5i_trench_open_4kN: P5g with the lift cap at 4 kN (BOM), same start snapshot. (4 kN sharp drop = existing P5b.)
  (d) P3 and P7 as declared at the start (P7 perturbations: all body masses x1.1, all geom mu x0.8 incl. leaf patches, bin CG +60 mm, lights 17 W).
- 00:50 P2c FAIL: grab at pad A success (docked, dy 1.9 mm, wheels 86.6 mm up), pivot 180 ok, return drive stalled at s 549.8 at the
  as-is pothole (same mechanism as P2a: drive wheel r 165 mm in the 60 mm hole, light load 13 kg bin), bin still captured (48 mm),
  no ground contact, hedge min 0.29 m. The set-down then ran where it stalled (not at home) and did not release - consequence, not
  a separate finding. Sim 344 s, 5.4 Wh. Next: P2c_pf from snapshot s556, P2a_pf whole leg.
- 01:05 P2c_pf (supplementary, pothole filled, from P2c snapshot s556) FAIL 'hedge contact -1.125 m at s 149.6'. It crossed the
  1:4 ramp up-step (clear min 75 mm) and reached home; set-down at home released/standing (bin s 9.72 lat -1.464), 25.5 Wh total
  incl. the P2c part. Root cause: traction/yaw loss on the 12 % WET-LEAF CLIMB with a light load. At s 149.4 (grade 12 %, mu 0.35)
  speed fell 0.48 -> 0.08 m/s and the tug yawed ~90 deg (one drive wheel slipping); pure pursuit then slewed it across the lane,
  footprint crossed the mapped hedge face on both sides (-1.12 m right, -0.14 m left) before it recovered at s 146 and finished.
  diag_traction.py: drive-axle normal load is 582 N with the 13 kg empty bin vs 1,536 N with 110 kg (P1) -> traction at mu 0.35
  204 N vs ~125 N grade force + rolling/servo transients (margin 1.6 vs 2.3 loaded; P4b loaded climb PASSED). Note: the hedge is
  a 0.8 m deep collision band of 1 m boxes; the tug pushed through it, so hedge resistance is not physical - the lane departure
  itself is the finding. Next: P2a_pf.
- 01:15 P2a_pf (supplementary, empty tug, pothole filled) FAIL: hedge -2.89 m at s 159.8 and stall at s 163.3. Up to s 165 clean
  (0.49 m/s, lat +-0.01, 1:4 ramp up-step fine). From the wet-leaf patch entry (s 165, grade 4-5 %) repeated slip/yaw events at
  s 163.4, 158.7, 153.5, 149.1; at 149 the tug yawed ~110 deg, crossed the lane both ways and ended >2 m outside the mapped hedge
  line (hedge band pushed through). diag_slip.py (from snapshot s166): drive-wheel normal loads total only ~455 N with no bin and
  swap side to side; at s 164.1 driveL unloads to 0 N (driveR 437 N) - the rigid 4-point chassis (2 drive + 2 castors, no
  suspension) rocks on the lane surface warp; with mu 0.35 the loaded wheel's servo torque then yaws the tug and the pure-pursuit
  controller (no slip / yaw-rate handling) cannot recover on low grip. Same mechanism as P2c_pf (13 kg bin). Loaded runs
  (P1/P4a/P4b, 110 kg: 1.4-1.5 kN on the drive axle) did not show it.
- 01:25 P3 PASS (WEB140 66 kg home -> pad A): grab success, carry 1324 s sim, bin wheel clear min 53.9 mm (pothole s 550.1), no
  ground contact, seated throughout, hedge min 0.299 m (pad A s 621.1), tip min 32.8 deg, lift peak 1,736 N (s 550.1), 15.3 Wh,
  set-down released/standing. Next: P7.
- 01:40 P7 (in progress) is trapped at the pothole: from s 550.39 (t 1145) the left drive wheel sits in the 60 mm pothole
  (mu x0.8 = 0.48) and the tug circles about it in a ~24 s limit cycle (yaw -180..+180 deg, lat -0.03..0.81, hedge 0.29 m min),
  bin still captured (clear ~42 mm). The 12 s stall rule does not fire because the bin moves > 0.05 m per window.
  HARNESS FIX (declared before continuing, no criteria change): the 2400 s drive timeout in lanerun.py was dead code
  (ck['drive_t0'] never stored). Now stored at drive start (P7: patched into its checkpoint as the first 'Transit' frame time);
  P7 continues unchanged and will end with 'timeout' at drive start + 2400 s. Applies to all later runs.
- 01:50 P7 FAIL 'drive1 stalled at s 550.7 (timeout)' (+ set-down attempted at the stall point, not released - consequence).
  Up to the pothole it carried like P1: bin wheel clear min 11.2 mm at the 1:4 ramp s 290.2 (P1 13.6 mm; CG +60 mm / mass x1.1),
  lift peak 1,829 N at s 290.2, tip min 20.4 deg, seated throughout, no ground contact, hedge min 0.274 m. At s 550.4 the left
  drive wheel dropped into the 60 mm pothole and, with mu x0.8 (0.48), could not climb the far edge; the tug circled the trapped
  wheel for 1,300 s until the 2400 s drive timeout. (P1 at mu 0.6 crossed it with lift peak 2,210 N.) Energy 62.5 Wh total is
  dominated by the circling. Next: P5i, then renders.
- 02:00 P5i_trench_open_4kN FAIL (same as P5g: stall s 455.1, bin-ground 468 N, lift saturates at 4,000 N). diag_trench.py:
  drive wheels (r 165 mm) wedged in the 200 mm open trench (chord at 40 mm depth 215 mm > 200 mm, so the wheel bears on both
  edges), anti-tip skids on the near level; raising the lift cap does not help - it is a drive/geometry stall.
  P5d end state: drive wheels on the lower level against the 40 mm face (castors already up): contact angle 40.7 deg needs
  mu >= 0.86 > 0.6 -> stall, independent of 3/4 kN lift cap.
  RENDER changes (declared, presentation only): caption on every frame = 'Digital twin simulation - not field footage. B2-F
  provisional pending bin check B0'; scenario label box; 3D raster at 0.75 scale upscaled (HUD full-res) for CPU; shots
  trimmed (transit x40/x60, grab/set-down x6, P4 x4, P5 x2 from 4 s before the feature, P6 real time from 7 s before the
  obstacle moves, P7 circling x150). render_lane_v1.py kept. P6 video done (85 s).
- 02:15 videos done: P6 (85 s), P1 (52 s), P3 (52 s). Rendering P7, P2, P4, P5, highlight.
- 02:35 videos P7 (58 s), P2 (81.5 s) done.
- 02:50 P4 video done (66.6 s). P5 side camera was inside the hedge -> near-side hedge cut away in side views (labelled on frame); P5 restarted.
- 03:20 P5 video done (147 s). Highlight reel HL defined (9 shots, 85 s); rendering.
- 03:45 DONE. HL video (85.4 s). Orbit shots at pad A / P7 pothole had the camera inside the hedge -> those frame ranges
  re-rendered with the near-side hedge cut away and spliced (P1, P2, P3, P7, HL; unpatched originals kept as
  vid/<v>/orig_unpatched.mp4; frame counts verified). Sample frames checked (3+ per video). Correction to the 01:05 entry:
  P2c_pf energy 25.5 Wh is s 556 -> home only (snapshot starts reset the energy counter).
  Deliverables in /workspace/work/out/b2f_lane/phys/: RESULTS_B2F_lane_physics.md/.pdf, B2F_lane_{P1..P7,HL}.mp4.
