# G6 mechanical work package - PROGRESS (resume file)
Started 2026-11-10 07:5x UTC. Rules: PYTHONPATH=/workspace/work/pylib, ONE heavy process, nice, stop by PID only.
## Status
- [ ] 0 orient (reading docs/code)
- [x] 0 orient done 08:10 UTC. Key findings:
  * D42 misses = bar perched on lip inner corner (-24,-10) after the 0.6 deg ease-off shifts the bar ~8 mm bin-side (48 mm throat leaves 3 mm/side),
    or bar friction-locked on the back wall (float can't rise) -> pawl underside hits bar top. Pawl line pivot(40,52)->tip(-22,14) IS the underside.
  * D25 retention gap pawl tip -> lip corner = 24.1 mm today (just < D25). Widening the throat needs a longer/beaked pawl.
  * SULO D25 lost capture (K2 i=9): bar 17 mm above floor, pawls closed, truth captured; feeler threshold in scen_g5 is 12 mm (code), refused.
  * fitcheck_after.json still lists spring-brake vs pod bulkhead plug envelope interference (29,965 mm3) - not in handover; report.
  * Yaw free +25/-5(isolator 0.7 mm at -10 deg!) ; saddle hits drive tyre 35 deg; mast rail/lug hits tyre 45 deg.
Plan: g6 code = copies of g5 code in revG/sim/g6 (results_G6_*). One queue runner qG6 (queue_g6.py) for ALL heavy jobs incl. CAD.
- runner: cd revG/sim/g6; NREC=0 setsid nohup nice -n 10 python3 queue_g6.py qG6 > qG6.out 2>&1 &   (jobs in qG6.txt, done in qG6.done, log qG6.log)
- 08:40 smoke: K3 (baseline) reproduces G5 misses. H1 (lip top 0, lip proud) broke SULO (lip/lid). H2 = throat -34 (58 mm), lip 8 mm top -2 with 6 mm chamfer,
  cranked pawl knee(-18,35) tip(-33,19), feel_T 20: WEB D42 x4 all success first try, SL250 i17 success, SULO 9/11 ok; SULO 21/29 (D42 full) still float not rising (back-wall friction lock).
  H3 = H2 + firmware re-rise (one extra 0.6 deg ease + rise if latch open or feelers open). Smoke queued. Design check script hook_design_g6.py -> hook_design_g6.json
- 08:55 H3 smoke: SULO D42 21/29 now success (re-rise fired), WEB D42 ok. QUEUED full matrix H3 (7 bins x 30, seeds 501-507, tag _H3 -> ../results_G6_mc_<BIN>_B2_H3.json).
  Baseline for comparison = G5 files results_G5_mc_<BIN>_B2_K2h130.json (g6 code reproduces them: smokeK3).
- Task5 actuator: datasheets in web/downloads/g6act (LA34, LA31, LA36 pdf+txt). actuator_fit_g6.py -> actuator_fit_g6.json.
  LA34 'L' (S+267, always for patient lifts) fits with RF-13 base moved (600,340)->(572,340), stroke 388..; LA31 max stroke 350 needs mast bracket S 900->770 (SF 1.53); LA36 fits base (580,340) S 398.
- 08:12 UTC: tilt_g6.py written (actuator speed/force model, ACT_BASE patch); queued 16 tilt runs after the H3 matrix (1 smoke first).
- 08:14 masses_g6.py -> mass_g6_M95..M110(+g gravel) (dry 84.5 kg incl LA34 4.5 kg); ballast_g6.py written; queued 46 ballast jobs after tilt (smoke M95 climb12 first).
- 08:15 queued ice/grit (H3i2,H3i5 x4 bins x12; H3g5 x2), no-steer unseated generator (H3ns, H3ns_i5 x3 bins x12), SULO i9 feeler recheck (K2feel,K3feel).
- 08:18 M95 climb12 mu0.3 FAILS (2.5 m/25 s). Added climb12 mu .35/.40 per mass and AXLE ballast variants M100ax/M110ax (ballast x=760). Insight: front cans (x1215) put ~69% of ballast on casters.
- 08:22 CAD: revG/cad/g6/g6_layer.py (hook H3, saddle scallop, LA34 envelope + base pin 558/340, RF-53 ears replace RF-13, lidar tabs replace SN-51, stops +/-42, KP_DX option); fitcheck_g6.py queued A0 (no kp move) and B38 (kp -38).
## Resume run 2 (started 10:43 UTC) - queue qG6 PID 616 alive, not restarted
- 10:45 H3 vs G5 (paired idx): WEB 27->30, ESE140CL 30->30, ESE240SL 29->29 (same no_dock), SL250 29->30, SULO 27->29 (no_dock same), ESE240CL 30->30; CRA running. 0 lost captures, 0 FP so far.
- 10:45 queue reordered (backup qG6.txt.bak_1043): ballast climb12 M100ax/M110ax/M110/M100 first, then tilt LA36_16H, + NEW LA36_12H x4, LA36_12H_cold x2 (tilt_g6.py ACTS += LA36_12H, LA36_12H_cold [speed x0.75 = assumption]).
- Fit A0/B38 read: both still have spring brake vs PD-20/21 plug (29,965/16,010 mm3), M12 vs PD-20 (1,673), LA34 housing vs mast rail (7.8k tow48 .. 108.6k tilt36 mm3) -> LA34 envelope FAILS CAD regardless of temp.
  B38 adds RF-12 washer vs CH-01 (859 mm3) and YS-02 pin hits RF-11 ring at 28 deg (and FC.rotz pivots about the OLD kingpin -> B38 sweep not trustworthy). A0: stop pin at ~40-42, saddle-tyre 1.5 mm @40, rail-tyre 1.7 @42.
- Decision draft: kingpin A0 (no move). Actuator LA36 12 mm H (6,800 N, 13 mm/s @ load, -30 C at 50 % load, IP66/69K, built-in hand crank). BID 250+S: S=400 -> 650/1050 vs need 656.1/1041.8.
  LA36 eyes D12.2 -> clevis pins D12, holes 12 H9 (no 8->10 bushes needed; bush note was for ELA 0041941-1). ELA 0041941-1 (g6-parts) rejected: 2,500 N vs 2,359-2,457 N needed = SF ~1.0.
- Clevis: placeholder = 40x6 flat arm cantilevered 115 mm + 6 mm ears -> ~700 MPa at 2.4 kN. Replace: RF-54 folded U clevis (8 mm S355, axis along x, flanges = ears) on RF-55 box outrigger (6 mm folded channel + 6 mm closing plate, 60x60) welded to spine + RF-53.
- 11:00 CRA240 H3 29/30: idx 19 no_dock (dy -78 mm). Diag: pawl/hook NOT in contact; approach-only sweep shows funnel-edge chaos: H3 fails dy -0.078/-0.080, ok -0.070..-0.076; G5 (K3) fails -0.077,-0.080,-0.082, ok -0.079.
  Firmware fix tested: re-dock on approach timeout (mc_g5.py env NODOCK_RETRY=1) -> idx 19 success. => GH-B6 accepted; add 'retry on no-dock timeout' to firmware list.
- 11:01 tilt: LA36 12H/16H pass on ESE240SL/WEB/ESE240CL; times limited by the 1.5 deg/s mast rate (same for all actuators). Peak 2,473 N (SL250 unload retry). pin-pin 656.6..1030.2 vs LA36 400 (650..1050).
  ESE240SL250 RELEASE FAILS with every actuator AND with the G5 hook (K3 + XTL450) -> pre-existing, never tested in G5 (bar ends ~0.8 m below hook = bin not standing). diag queued.
- 11:05 clevis_calc_g6.py -> cad/g6/clevis_calc_g6.json: placeholder arm 1,185 MPa at 2,473 N (SF 0.30). RF-57/58 all SF>=4.6 op, >=1.44 at 6.8 kN (spine torsion alone, conservative).
- 11:08 g6_layer.py: ACT_MODEL/LA36 envelope (rot param), CLEVIS='channel' (RF-57/58), FINAL (PD-20/21 +75 mm y, 6 drain slots, B-GR-62/GR-63 feelers, SN-60/61 80x45x22, KP-S1 AS5600, R16 pivot boss). Backup g6_layer_pre_final.py.
- 11:10 LA36 rot probe at ay=205: block hits mast rail in EVERY orientation (y overlap 3-5 mm). Queued probes at ay=215/222.
- 11:12 drawings_g6.py written (copy of G5 drawings + G6 parts RF-57/58/59, GR-61/63, KP-S1, PD-12; PD-10/SN-51/RF-13 removed) -> first build OK 57 parts, 38 DXF. Fixed RF-57 flat polygon, footer, GR-03 pivot boss.
- 11:15 LA36 probe ay=215: rot 0/90/180 all clear (>=5 mm), rot 270 hits mast. DECISION: actuator line y 215 (+10 vs G5, MA-56 rod clevis +10), LA36 rot 0 (motor block on the upper side, away from spray/deck).
  clevis_calc re-run with 185 mm outrigger: min SF op 3.75 (spine torsion alone), lim 1.36; weld 6.69/2.43. drawings RF-58/59 -> 161 long.
- 11:15 queue re-planned (backup qG6.txt.bak_1115, dropped jobs in qG6.dropped_1115.txt: LA34/XTL tilt variants, M95/M100/M105/M110 non-climb tests, *_m35/_m40).
  Ballast candidates: M100ax (15.5 kg over axle), M105, M110 (cans), M105h/M110h (15 kg steel plate stack in an axle box x700-820 |y|<175 z124-170 + rest in cans; mass_g6_M105h/M110h.json).
  Tests: climb12, climb12x(mu .25), step40, estop12; then flat10/flat10e/estopflat/rel_x4 for the winner only. Then the ice/grit/no-steer MC + SULO feeler rechecks.
- 11:16 Irish winter: Met Eireann [nearby town] 1991-2020 mean daily min Dec 3.7 / Jan 3.3 / Feb 3.3 / Mar 4.0 C, abs min -11.4 C, ~20 air-frost days/yr; bins go out at night -> LA34 (+5..+40 C) out of rating most winter nights -> LA36.
- queued fit_g6_final.py 215 0 (static 7 poses, yaw sweep + fine 38-45 deg table, STEP/STL export, step_parts_G6/) and drawings v2.
- 11:25 FINAL fit v1 (scallop 150, stops 42): yaw pin hits the block at ~40.2 deg but RF-03 saddle hits the tyre at ~40.5 (1.5 mm @40) -> NOT OK. B38 sweep in queue was invalid (FC.rotz pivots about the old kingpin) + RF-12/CH-01 clash -> B38 rejected.
  Variant scallop |y|<=130: saddle-tyre 19.8 mm @40, 10.0 @42; limit now mast rail/lug 8.3/10.3 mm @40, 4.9/6.5 @41. DECISION: kingpin A0, scallop 130, YS-01 blocks at 42 nominal -> hard stop +/-40 deg (pin contact). SITL: BT_HITCH_CAP=40.
  Other static fixes: feelers moved to outboard face/behind back wall (crossbar clash), GR-07 6 mm inboard (4 mm3), SN-60 radome off-centre y 45..125 (3 mm to bumper switch). Killed redundant st40 job (PID 3606). Final fit v2 + export + drawings v3 queued.
- 11:33 ballast so far: climb12 mu .30 PASS for M100/M100ax/M105/M110/M110ax, FAIL M95 (2.5 m). climb12x mu .25 FAIL M100ax (0.66 m), M105 (0.77 m). step40/estop12 pass (kp SF 4.3-5.5).
  Added climb12_m27 for M110/M110h/M105h/M105/M100ax and flat10/flat10e for M110h/M110/M105h. Report generator written: revG/make_results_g6_mech.py + results_g6_text.py (DEC dict to fill).
- 11:41 ballast phase A done: M110 (cans) FAILS estop12 (slide 0.058 > 0.05 after stop on 12 % downhill), M110h slide 0.044 (marginal), M105h 0.001, M100ax 0.001.
  climb12 mu .30: all >=100 pass (M100ax slowest 19.6 s); climb12x mu .25: all fail (M110/M110h reach 2.6 m, M105x 0.8 m). Physics: brakes act on drive wheels only -> can ballast adds demand without adding brake normal force.
  DECISION (pending m27 + rel): M105h = 84.5 dry + 15 kg steel plate in axle box + 5.5 kg in front cans. Queued M105h estopflat + rel x4, M95 estopflat/flat10e refs.
- 11:42 UTC (main agent): DECISIONS: GH-B6 accepted (+NODOCK_RETRY); LA36 400 mm accepted; kingpin A0, hard stop +/-40 (software cap ~37 for SITL key re-runs after regression at 28); ballast provisional = M110h (15 kg steel over axle + 10.5 kg cans) -> queue its rel_* x4 + estopflat + flat10 once qG6 finishes. ESE 240 SL 250 mm release fault to trace (likely sim artefact, unproven). BOM to update: LA36, steel tray, steel ballast, 2x M8 inductive, radomes.
## Resume run 3 (M110h full suite, started 16:58 UTC) - subagent "G6 mech full suite"
- 17:05 SIM ARTEFACT #1 (major): sim_g5.build_xml(ballast_x=0.70 default) -> load_rows moves EVERY row whose name starts 'Ballast' to x=0.70 m ahead of the kingpin.
  G6 mass files name the ballast rows 'Ballast fill ...'/'Ballast, steel plate ...' and no G6 caller passes ballast_x -> M110, M110h and M110ax were ALL simulated with
  25.5 kg at x 0.70 (abs 1370 mm, ahead of the cans). Tug CG ahead of axle: sim 0.178 m for all three; true M110 0.142, M110h 0.080, M110ax 0.037.
  => the G6 ballast-sweep differences between can/hybrid/axle variants were noise, not design. Fix: mass_g6_* files keep their own x (env G6_LEGACY_BALLASTX=1 reproduces old).
  Also: mc_g5.py ignored G6_MASSFILE (used mass_revF, ballast=1) -> all H3 grab MC ran on the revF mass (~93 kg). Fix: honour G6_MASSFILE.
- 17:05 DOWNHILL RELEASE ROOT CAUSE (diag_rel_g6.py, WEB140 dn12e, legacy ballast): with the tug braked and yaw FREE, tilting gravity to -12 % makes the hitch
  yaw-unstable (rear frame + mast + tipped bin CG sit 'uphill' of the kingpin = pushed trailer): ryaw grows 0 -> -20 deg in 3 s and hits the sim's 70 deg joint limit
  during the 1 m tow. stand_up() then calls yaw_lock(True) = PD 20 kNm/rad snap from -70 to 0 -> bin wrenched out of one hook -> lands on its side (82.8 deg).
  Sim artefacts in this chain: (a) yaw range 70 in sim vs +/-40 hard stop in the G6 design; (b) yaw lock modelled as an instant PD snap, real part is a solenoid PIN
  that cannot engage off-centre. Real fault: the free kingpin jackknifes on a downhill whenever the hitch is in compression (stopped/braking/coasting downhill).
  Full WEB dn12 with CORRECTED ballast passes (1 sample). 'Pawls won't open' was a mis-read: pawls were at -130 (fully open); check failed because bar z was ~-850 mm
  (bin already gone/hanging) - the release check message is misleading.
- New env switches (all default OFF = legacy behaviour): G6_YAWRANGE (kingpin stop deg), G6_PINLOCK=1 (yaw pin only engages |yaw|<2 else release aborted+alert),
  G6_DNLOCK=1 (fix candidate: yaw pin engaged before descending), G6_SB2=<z m> (2nd wheel-stop roller), REL_DY/REL_DYAW (pose variation), SIM_DT (timestep),
  ballast_g6: G6_BIN, EST_MU, EST_V, argv[3] tag. tow_g5 results now carry mon{ryaw max, pitch_dev, antitip peak, caster min}. TOW_REC=1 to save pickles.
- 17:08 sanity_g6.py M110h -> ../results_G6_sanity_M110h.json: ground reaction = weight (0.0 %), penetration 0.04 mm, tug-alone drive/caster 1000/106 N vs hand calc 970/109 N.
  REAL DESIGN FINDING: with the M110h ballast where the mass file puts it, the tug CG is only 80 mm ahead of the drive axle -> 10.8 kg on the castors unladen;
  any hook load > ~15 kg lifts the castors (tow pose with a full 240 L: castors 0 N, tug sits on drive wheels + bin wheels, pitch ~5.4 deg nose-up).
- 17:09 SL250 rel_flat diag (M110h fixed, yaw 40): tug pitched -5.45 deg (nose up), castors 0 N, bin wheels 40-90 mm IN THE AIR during the whole stand-up;
  bin 'upright' rel tug at mast 25 deg while hanging; cam open drops it -> falls back to 80 deg. Contact-pair dump running (diag_rel_ESE240SL250_rel_flat_pairs.json).
- 17:10 QUEUE qG6s started (PID 5981, runner queue_g6.py qG6s; jobs qG6s.txt, done qG6s.done, log qG6s.log): ballast _v2 x6 then release matrix 7 bins x 6 tests x 3 poses
  (G6_PINLOCK=1, yaw 40, tag _M110h_v0/1/2 -> ../results_G6_tow_<BIN>_<test>_B2_M110h_v<k>.json). Restart: cd g6; NREC=0 setsid nohup nice -n 10 python3 queue_g6.py qG6s > qG6s.out 2>&1 &
- 17:12 SL250 contact dump: tug wheelies back until the funnel FLARES (rear frame, 100 mm high) ground (300-400 N each), bin hull rests on the rear-frame SPINE (~700 N),
  bin wheels in the air -> bin hangs/props; cam open drops it. Root cause = low castor load (real, M110h CG 80 mm ahead of axle) + bin hull-on-spine contact (convex-hull bin, crude).
- 17:16 ballast _v2 (corrected placement): climb12 mu.30 PASS 19.9 s; climb12 mu.27 FAIL 0.77 m (was PASS with misplaced ballast); estop/step pending.
  Fix tests: WEB dn12 full + G6_DNLOCK PASS; WEB dn12e (empty) + DNLOCK still tips 82.8 deg (new mechanism, diag queued); SL250 + STANDFIX aborted by pin (hitch 9.7 deg after
  1 m flat tow) -> added G6_STRAIGHTEN=1 (creep forward on heading until hitch <1 deg, max 1.5 m) - queued fixA = PINLOCK+STRAIGHTEN+STANDFIX on SL250 and ESE240SL flat.
- 17:22 SIM/DESIGN FINDING #3 (diag_towpose_g6.py, ESE240SL full, tow pose on flat): the BIN WHEELS RIDE ON TOP OF THE WHEEL-STOP BAR (stopbar-binwheel 793 N, force
  nearly vertical, contact z 69 mm), not on the ground. The tug carries the whole bin (hook 437 N + stop bar 793 N at 0.556 m behind the axle), castors 0 N, tug pitched
  5.4 deg nose-up and resting on the funnel FLARES (460 N, 0.85 m behind axle) which then drag on the ground in every tow. Same with legacy ballast (G5 towstab/step40
  files also show castor_min 0). Mechanism: hook arc + tug pitch -> stop-bar centre (100 mm) drops below the 200 mm wheel centre -> wheel climbs the bar (positive feedback).
  Fix candidate: second stop roller above the wheel centre (G6_SB2=0.15 m) - towpose diag queued (ESE240SL, SL250) + empty-bin towpose.
  fixA (STRAIGHTEN) made the hitch worse on flat (9.7 -> 13.9 deg over 1.5 m) - consistent with flares dragging as skids on the rear frame.
- 17:28 CONFIRMED mechanism of #3: GH-B6 float ratchet (B2: one-way, 8 mm pitch) locks the float during tipping, so the mast arc LIFTS the bin onto the stop bar
  (a 2nd roller at 150 mm just moves the wheels onto that roller). With ratchet disabled (G6_GHP_EXTRA={"ratchet":false}) the bin wheels stay on the ground
  (697 N), flares 0 N, stop bar 0 N; tug still pitched -2.8 deg, castors 0 N (bin leans on spine 327 N) -> castor lift with a full 240 L is a real M110h moment-balance result.
  Baseline PINLOCK matrix: every case so far aborts at the pin (hitch 2-20 deg after a 1 m tow). Held v1/v2 of the baseline (#HOLD lines) to save CPU.
  Testing combined fix 'fixR' = ratchet off + PINLOCK + STRAIGHTEN + STANDFIX(float/pitch interlock) + DNLOCK on 4 critical cases.
- 17:35 fixR (ratchet off) keeps the hitch straight (0-0.2 deg), pin engages; float interlock tolerance too tight (grab float -39 mm with ratchet off) ->
  interlock now: ratchet on -> float within 40 mm of grab; always -> float off its top stop. fixR3 x4 queued. Baseline v0 matrix continuing; driving/MC/dt moved ahead of it.
- 17:38 NEW TASK from main (GA drawing pass): g6_layer hook group fixed at S=700 (off crossbar -162 tow/-30 dock), 6x45 lip chamfer not cut (1 mm spike).
  Sim check: sim uses the SAME geo_g3.gh_cup boxes -> sim lip chamfer is also NOT modelled (slope box inside the lip outline): all GH-B6 grab results are for a
  square lip corner. Sim hook rides on the float joint (ref 0.70 m + float q), so sim placement is self-consistent (bar seated on the cup floor in tow: bar z -10..-13 mm, r 13.5).
  CAD fix: g6_layer.py HOOK_FOLLOW_S (Z += s-730), CUT_CHAMFER (real 45 deg cut, slope box dropped); backup g6_layer_pre_hookfix.py. export_g6_steps.py (export only + bar-in-cup
  measure) queued noexport test, then export.
- 17:40 fixR3: ESE240SL flat PASS, SL250 flat PASS (released; tug still pitched 5.6 in tow), WEB empty dn12 PASS. Queued full fixR3 matrix v0 (42) + v1/v2 x {flat,dn12,dn12e,up12e}
  + ratchet-free step40/towstab (ESE240SL, WEB) + ratchet-free MC (WEB, ESE240SL). Report: revG/results_g6_suite.py (new section 0, exec'd from results_g6_text.py),
  DEC fields in results_g6_dec.py (suite_* + ballast_*; backups *_pre_run3.py). make_results_g6_mech.py builds OK.
- 17:58 driving (as designed): towstab/step40 4 bins: castors 0 N in all, hitch hits the 40 deg stop in every run (flares dragging), SULO step40 FAIL (stuck 2.18 m).
  climb12 mu.30 PASS all 4; mu.27 FAIL ESE240SL/SULO, PASS WEB. estop12 x3 var: all PASS, slide <=0.002 m, hitch 35-40 deg (jackknife on downhill).
  CAD: export_g6_steps.py ran -> STEPs re-exported 17:37 with hooks on the crossbar (shift -162.2 tow, -30 dock, 0 grab0) and chamfer cut (GR-03 -189 mm3, 1 mm spike gone,
  chk_chamfer.json). CAD bar sits 30 mm above cup centre = 40 mm above the floor in grab0 AND tow (CAD pose solver puts the carriage at s, not where the float meets the bar);
  sim float rises to the bar (bar on floor). Release-fail message fixed (says 'pawls open but bar X mm from cup' instead of 'pawl still closed').
  Queue reordered: MC -> dt -> fixR3 v0 -> fixes/norat -> fixR3 v1/v2 -> baseline v0 rest. Added estop12 _fix (DNLOCK + ratchet free) x4 bins, climb m27 norat.
- 18:12 sandbox rebooted (~18:07); queue restarted (mc resumes from its json).
- 18:39 MC at M110h done: 206/210 (WEB 30, 140CL 30, SL 30, SL250 30, SULO 29 no_dock, 240CL 29 no_dock, CRA 28 safe_miss+no_dock), 0 false holds, first try = capture.
  dt 0.25 ms: climb 18.3 s (vs 19.9), estop slide 0.001 (same), hitch 33 (vs 38), release up12 baseline HOLD (same). Added fixR3 ESE240SL flat at dt2.
- 18:53 fixR3 (ratchet off ALWAYS) broke grabs on light empty bins (ESE140CL empty safe_miss) and uphill full stand-up (bin rolled away, 82.8 deg) -> superseded.
  fixR4/5 = G6_RATCHET_TIP (ratchet lifted after the claim, re-engaged in the tow pose) + PINTOL 3 deg (tapered pin) + STRAIGHTEN by following the rear-frame
  heading (ESE140CL flat: hitch -9.9 -> -1.9 over 1.5 m, released OK) + STANDFIX v3 (stop on rel<=0.3 & abs<=1.5 & float off stop; interlock pitch>2.5).
  fixR5 tests queued (6), then decide matrix.
- 18:58 fixR6 (= fixR5 but ratchet released right after the claim; stand-up stops on REL tilt <=0.3, then interlock only) results, 6 cases:
  PASS ESE240SL flat full, WEB140 dn12 empty. FAIL (safe hold, no drop) SL250 flat full: rel 0.3 but tug pitch -4.6 (nose-up), bin world 4.3 -> interlock;
  WEB140 up12 full: rel 0.3, pitch -2.6, world 2.3 -> interlock (fixR5 dropped this bin, 82.8). FAIL WEB140 flat EMPTY: straighten makes hitch worse 2.2 -> 3.5 deg,
  > 3 deg pin capture -> pin abort (same as fixR4). ESE140CL flat empty pending.
  Diagnosis: (a) rel-tilt stop is wrong when the tug is pitched - firmware must stop on WORLD bin tilt = IMU pitch + mast/bin rel; (b) creep-straighten does not
  converge for light empty bins. fixR7 = fixR6 + G6_STANDWORLD=1 (stop when rel+pitch<=0.3 or rel<=-8) + G6_PIVOT=1 (after creep, pivot in place to hitch<0.8, max 6 s).
  diag_stand_g6.py (new): stand-up time series (pitch, rel, world, float, castor/binwheel/stopbar/spine/flare/hook forces); 2 sweep diags (SL250 flat, WEB up12) +
  8 fixR7 cases queued ahead of the rest. Backup scen_g5_pre_fixR7.py.
- 19:02 diag_stand (sweep to rel -8, ratchet re-engaged in tow pose as fixR6): SL250 flat and WEB up12 show the SAME ratchet mechanism again during STAND-UP:
  float drops to its bottom stop while free in tip/tow (-160 / -88 mm vs grab), ratchet re-engaged there, float rises as the bin comes up; once it is back at ~grab
  position (world bin tilt +5..+12 deg) the ratchet-locked hook starts lifting the bin by the lip as the mast comes back -> tug rocks back to the -5.4 deg flare stop
  (flares 330-400 N, hook 280-310 N), bin wheels lose ground contact (WEB up12: bin wheel load = stop-bar load only). So a re-engaged ratchet must be lifted again for the
  stand-up. fixR8 = fixR7 + G6_RATCHET_STAND=1 (ratchet pawl lifted at stand-up start; same independent pawl actuator fixR4-7 already assume). 10 fixR8 cases queued after fixR7.
- 19:08 fixR7 (STANDWORLD + PIVOT): 6/8 PASS - ESE240SL flat, SULO flat, ESE240SL dn12, WEB dn12e, WEB flat EMPTY (pivot 3.5->2.2 deg, inside the 3 deg taper) and
  ESE140CL flat EMPTY (3.1->2.0) now PASS. Still HOLD (safe, interlock): SL250 flat full and WEB up12 full - stand-up stops at world 0.3 deg but tug at -5.4 deg (flare stop).
  fixR8 (+ ratchet lifted for stand-up): IDENTICAL numbers on those two -> the ratchet is NOT the stand-up cause (float is on its -100 mm hard stop in tow, then rises).
  Real stand-up mechanism (diag_stand series): pulling the bin top back presses the bin wheels into the 100 mm wheel-stop bar (stop-bar load rises to 410 N),
  the wheel rides up the bar (bar centre 100 mm = WEB 200 mm wheel centre; 25 mm BELOW the 250 mm wheel centre), bin wheels end on the bar only (ground 0 N), tug rocks
  back to the flares. Same climb as finding #3, now at stand-up. Diagnostic (not a 3rd fix iteration): fixR8sb = fixR8 + G6_SB2=0.15 (upper stop roller 150 mm) on
  SL250 flat, WEB up12 + 2 regression cases. Also found+fixed: ballast_g6.py line 55-56 had "S.yaw_lock(False); R.watch_pawl=True" swallowed into a comment by the
  RATCHET_TIP edit (pawl-bounce detection off); no existing ballast result was produced after that edit (latest 18:37) -> no result affected.
- 19:11 DECISION: final variant = fixR7 env (ratchet pawl lifted after claim, re-engaged in tow; PINLOCK tol 3 deg taper; straighten = creep on rear-frame heading
  then pivot; STANDFIX with world-tilt stop (IMU pitch + mast) + interlock; DNLOCK). fixR8 (ratchet lifted again for stand-up) gave identical numbers -> not adopted.
  Final queue (129 jobs, tag M110h_fixR7 so the 8 finished fixR7 cases are reused): 7x6 v0 matrix; MC spot ESE140CL/WEB140 x30 with RATCHET_TIP (_M110h_rtip);
  step40/towstab 4 bins _M110h_rtip; estop12 4 bins x 3 var (DNLOCK+RATCHET_TIP, _<bin>_fix_e0..2); climb12 mu .30/.27 4 bins _<bin>_rtip;
  ballast M105h/M110/M110ax climb12/.27 + estop12 (ESE240SL, _ESE240SL_rtip / _fix_e0); pose v1 (+30 mm,+2 deg)/v2 (-30,-2) x {flat, dn12, flat empty} x 7;
  then the as-designed rest. Dropped old single-variation _fix estop lines + old climb rtip line (superseded).
- 19:15 CAD (step 5): g6_layer.py FLOAT_DZ (hook group on the float raised 40 mm in bin-engaged poses -> bar on the cup floor) + RATCHET_LIFT (GR-08 renamed,
  new GR-08S 12 V pull solenoid 30x30x40 next to the ratchet pawl). export_g6_steps.py: G6_FLOAT_DZ (default 40, dock 0), bar-in-cup measure includes it,
  interference check of GR-08S and the raised GR-03 vs every tug part. Backups g6_layer_pre_r7.py, export_g6_steps_pre_r7.py/.json, pre_r7_export/ (old STEPs).
  Export running (PID 3698, log export_g6_steps_r7.log). Report: results_g6_suite.py now reads fixR7 + _rtip/_fix_e files, fix-iteration table, stand-up series,
  ballast re-check table (results_G6_castor_hand.json = hand castor/drive split per mass file). Backups *_pre_run4.py.
- 19:27 CAD export done (64 s): first try (hooks only +40) clashed GR-03 with GR-06 cam bar (145 mm3/side) and GR-08S with K1 stops -> the whole FLOAT GROUP must move:
  g6_layer FLOAT_GROUP = slide carriage, UHMW pads, crossbar + arm, tilt IMU, GR-06 cam bar, GR-07 gearmotor, GR-10 cord, B-GR-09, K4 lid finger (translated along the
  mast by FLOAT_DZ), hook plates/pawls/switches/feelers rebuilt at Z+FLOAT_DZ; GR-08S moved onto the slide carriage (x PX+2..32, y 10..40, Z-30..Z+10).
  Result: bar on the cup floor in tow48 and grab0 (bar centre -10 mm, bottom 0.0 mm above floor), dock unchanged (FLOAT_DZ 0), NO interference of GR-08S, the hooks
  or the moved float group with any tug part in any pose. Re-exported tow/docked STEP, STL, step_parts_G6 GR-03/04/61/63 + new GR-08S.step. Not done: full fit sweep
  (fit_g6_final.py), and the CAD still carries two inconsistent float-stop sets (Rev F +/-10 mm 'Carriage float stop', K1 +/-60 mm) vs the sim B2 travel -100/+130.
- 19:27 fixR8sb diag (upper stop roller 150 mm): SL250 flat full now PASS (bin wheels stay down, tug -1.1 deg), regressions ESE240SL flat / WEB flat empty PASS;
  WEB up12 full still HOLD (pitch -3.1). -> 2nd stop roller is the hardware fix for SL250 (250 mm wheels); uphill-facing full release stays a HOLD (bin weight on the hook).
- 19:50 FINAL R7 v0 matrix (7 bins x 6) done: 31 PASS / 10 HOLD / 1 TIPS / 0 FAIL.
  up12 full: HOLD for all 7 (interlock: tug -5.4 deg on the flares - bin weight on the hook on the uphill-facing stand-up) - safe, no drop.
  flat full: HOLD SL250, ESE240CL, CRA240 (stop-bar climb at stand-up, same as SL250 diag); dn12 full: HOLD ESE240CL. All dn12/dn12e/flate/up12e PASS except
  SL250 up12e = TIPS (empty 250 mm-wheel bin: interlock passed (pitch -0.1), cam opened, bin fell over -> wheels were up on the 100 mm stop bar; light bin gives no
  pitch signal). Added fixR7sb (2nd stop roller 150 mm) for ESE240CL flat/dn12, CRA240 flat, ESE240SL up12 to the SB2 diag block (now 10 cases).
- 20:22 MC with RATCHET_TIP: ESE140CL 30/30 (15 empty), WEB140 30/30, first try 30/30, 0 false holds -> ratchet lift after claim does not hurt grabs.
  Driving _rtip (ratchet free in tip, re-engaged in tow): step40 4/4 PASS incl. SULO (stuck as designed), hitch peak 41-45 deg (still on the 40 deg stop, castors 0 N);
  towstab 4/4, hitch 27-30 deg (was 38-40). E-stop 12 % dn with pin in before descent: 12/12 PASS, slide 0.001 m, hitch 0.0-0.1 deg (was 35-40 = jackknife fixed).
  Climb (fixes on, M110h): mu .30 4/4 in 11.6-11.8 s (was 18-20 s), mu .27 4/4 PASS (as designed ESE240SL/SULO/CRA FAILED) - freeing the ratchet takes the bin
  off the flares, so the drive wheels get the load back. hold creep 0.03-0.04 m (limit 0.05; was 0.01).
  Ballast re-check (ESE240SL, fixes on): M105h mu .27 FAIL 4.08 m; M110ax (axle) mu .27 FAIL 2.1 m; M110h .27 PASS, .25 marginal PASS 24.6 s of 25;
  M110 (25.5 kg in cans) .27 PASS 11.9 s, .25 PASS 12.9 s; e-stops all PASS. -> forward ballast wins (keeps the tug from rocking back with a full bin).
  Queued: R7 at M110 on the 10 HOLD/TIPS cases + 4 regressions (_M110_fixR7_v0), climb12x x4 variants, tow-pose castor diag x4 variants.
- 20:45 Tow-pose static diag ratchet free, ESE240SL full, per ballast: castors 0 N for ALL (M105h/M110/M110h/M110ax), tug -2.7..-2.9 deg, bin leans on spine 234-463 N,
  drive load 1400-1587 N (M110 highest) -> castor lift is geometry, not ballast; forward ballast puts more on the drive wheels = better climb.
  R7 at M110 (12 critical cases): SL250 flat + CRA flat now PASS; ESE240CL flat HOLD; ESE240CL dn12 STUCK (bin standing, pawls open, hook not clear after 3 tries);
  up12 full: ESE240SL/SULO HOLD, WEB TIPS (dropped after interlock passed); SL250 up12e TIPS; regressions (ESE240SL flat, WEB dn12e/flate, ESE140CL flate) PASS.
  Report: results_g6_dec_run4.py (DEC overrides, exec'd from results_g6_dec.py), relcell STUCK class, pass/fail labels as-designed vs fixes, 'rule allows' row,
  M110 vs M110h release table, ballast table with climb12x + tow-pose castor columns. Ballast pick (draft): M110. Pending: M110 MC/driving, pose v1/v2, SB2 diag, as-designed rest.
- 20:47 sandbox rebooted ~20:33 (uptime 13 min); queue restarted (PID 890), resumes at the M110 WEB140 MC. 13 min lost.
- 20:55 cut the 17 remaining as-designed (baseline v0) release cases (#CUT-run4) to finish the final suite; as-designed matrix stays partial (cases already run).
- 21:00 M110 spot checks: MC WEB140 30/30, ESE240SL 30/30 (first try 30, 0 false holds); step40 PASS hitch 43.4 (M110h 43.6), towstab PASS 29.7 (29.8) -> ballast pick M110 confirmed.
- 21:35 REPORT FINAL (run 5). qG6s (PID 891) finished all 28 active pose-variant jobs (_M110h_fixR7_v1/v2 x {flat full, flat empty} x 7; dn12 pose lines were #CUT): 22/28 PASS, 6 HOLD -
  the HOLDs are exactly the 3 full flat cases that already HOLD at v0 (SL250, ESE240CL, CRA240 at M110h); no new failure, nothing tipped. Queue now idle (0 todo), process left running.
  Report: results_g6_text.py (title BinRobo ... ballast M110, fixes R7; section 3 decision line M110; 'Release on 12 %' caption now says tested data M105h/M110h, superseded; files line), results_g6_suite.py
  (headline release rows = v0 only: 30/42 and 30/35 inside rule; separate pose-variant row 22/28; rows reordered final-design first; compact ballast-pick table in section 0; needspace before 2 tables; matrix cells ' / '),
  results_g6_dec_run4.py (appended run-5 DEC.update: suite_answers rewritten answers-first, climb/towstab numbers corrected vs JSON: mu.30 11.6-11.8 s (was 17.5-19.9), mu.27 12.2-20.1 s (old text said 12-14 s),
  towstab 26-30 deg; suite_cad updated - float group +40 mm done). hdr_G6.tex (+needspace, header BinRobo). Backups *_pre_run5.py, hdr_G6_pre_run5.tex.
  All numbers checked against result JSONs (work/chk_g6.py): v0 30 PASS/11 HOLD/1 TIPS; e-stop fix 12/12; climb rtip 4/4 + 4/4; step40/towstab rtip 8/8; MC rtip 30/30 x2 (M110h) + 30/30 x2 (M110); ballast M110 kp SF min 3.83.
  PDF 17 pages, pages 1-6 inspected; copied to /workspace/work/out/revG6/RESULTS_G6_mech.pdf.
