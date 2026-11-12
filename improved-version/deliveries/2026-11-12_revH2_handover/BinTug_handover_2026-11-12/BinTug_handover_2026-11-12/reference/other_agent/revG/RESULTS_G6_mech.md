---
title: "BinRobo (Bin Tug Rev G6) - mechanical package (final, ballast M110, fixes R7)"
subtitle: "GH-B6 hook, LA36 actuator, ballast, kingpin, clevis, CAD fit check, STEP and drawings. SIMULATION + CAD ONLY - nothing is built."
geometry: margin=1.6cm
fontsize: 10pt
colorlinks: true
toc: true
toc-depth: 2
---

# 0. Answers first - final G6 suite: fixes R7, ballast M110

**Bottom line: the sims had real faults, and fixing them exposed real design faults. With the fixes below (R7) the tug releases 30 of the 35 cases the release rule allows (flat or facing downhill, full or empty; at M110h); the other 5 are 4 safe holds and one empty 250 mm-wheel bin that tips over facing uphill. It must not release a full bin while facing uphill.** The biggest single design fault is the hook float ratchet: it locks the float while the mast tips, so the mast lifts the bin onto the wheel-stop bar and the tug rocks back onto its funnel flares. That one fault explains the downhill drops, the empty Weber falling over, the ESE 240 SL 250 mm "never releases" case, the 40 deg hitch swings and most of the lost grip on wet leaves. Lifting the ratchet pawl after the claim (new small solenoid GR-08S) plus four firmware rules (fix R7) cures it. A second fault remains: the 100 mm wheel-stop bar sits at or below the centre of 200 / 250 mm bin wheels, so during stand-up a full bin's wheels ride up the bar on three of the seven bins. Either the forward ballast M110 or an upper stop roller at 150 mm turns the SL 250 and Craemer flat-ground holds into clean releases; the full ESE 240 CL still holds on flat and sticks on a downhill with both (section 0.3).

**Pass / fail, tested at M110h (ballast where the mass file puts it); the chosen ballast M110 was re-checked on the critical cases, grab and driving (section 0.5b and the ballast table below). "As designed" = current G6 hardware and firmware; "WITH FIXES" = R7 (section 0.3). Release with fixes is only expected to pass where the release rule allows it (no full-bin release facing uphill).**

| test | result | verdict |
|---|---|---|
| Grab MC, GH-B6, 7 bins x 30 at M110h (with re-dock) | 206/210 captured (95% CI 95.2-99.3 %), first try 206/210, false holds 0 (CI 0-1.8 %) | PASS |
| Release matrix WITH FIXES R7 (7 bins x 6 cases, nominal pose v0) | PASS 30/42 (HOLD 11, TIPS 1) | FAIL |
| Release WITH FIXES R7 where the release rule allows it (v0: all but full bin facing uphill, 35 cases) | PASS 30/35 (HOLD 4, TIPS 1) | FAIL |
| Release WITH FIXES R7, pose variants v1/v2 (+/-30 mm, +/-2 deg), flat full + flat empty, 7 bins | PASS 22/28 (HOLD 6) | FAIL |
| Towing step40 + towstab WITH FIXES (ratchet free in tip), 4 bins | 8/8 ok, castor min 0.0 N, hitch/bin yaw peak 44.7 deg | PASS |
| E-stop 12 % downhill WITH FIXES (pin in before descent), 4 bins x 3 | 12/12 ok, worst slide 0.001 m, hitch peak 0.1 deg | PASS |
| Climb 12 % WITH FIXES, 4 bins, mu 0.30 / 0.27 | mu 0.30: 4/4, mu 0.27: 4/4 | PASS |
| Grab MC spot check WITH FIXES (ratchet lifted after claim), ESE 140 CL + Weber 140 x 30 | 60/60 captured, first try 60, false holds 0 | PASS |
| As designed: climb 12 % wet leaves mu 0.30, ESE 240 SL 110 kg | 5.0 m in 19.9 s | PASS |
| As designed: climb 12 %, mu 0.27 | 0.77 m in 25 s | FAIL |
| As designed: climb 12 %, mu 0.25 | 0.61 m in 25 s | FAIL |
| As designed: 40 mm step, full 110 kg | captured True, hitch peak 40.1 deg | PASS |
| As designed: e-stop 12 % downhill mu 0.30, full | stop 0.10 m, slide 0.001 m, hitch peak 38.1 deg | PASS (hitch near the 40 deg stop) |
| Release matrix AS DESIGNED (7 bins x 6 cases, pin lock) | PASS 1/10 (HOLD 9) | FAIL |
| As designed: towing step40 + towstab, 4 bins, 110 kg | 7/8 ok, castor min 0.0 N, hitch/bin yaw peak 40.2 deg | FAIL |
| As designed: e-stop 12 % downhill, 4 bins x 3 variations | 12/12 ok, worst slide 0.002 m, hitch peak 40.2 deg | PASS |

**Answers in one place:**

* **Sim faults found and fixed (0.1):** (1) ballast always placed at x 0.70 m whatever the mass file said; (2) grab Monte Carlo ran on the old Rev F mass; (3) kingpin free to 70 deg instead of the 40 deg stop; (4) yaw lock modelled as an instant spring (the real part is a pin that only goes in near centre); (5) misleading release message ("pawl still closed" with both pawls open); (6) ballast_g6.py had the pawl-bounce watch switched off by a comment slip (no result affected); (7) the stand-up stopped on the bin angle relative to a tug that was itself tilted (now IMU pitch is added).
* **Design faults found (0.2):** (1) the hook float ratchet locks the float while tipping, so the mast lifts the bin onto the wheel-stop bar and the tug rocks back onto its flares; (2) the 100 mm wheel-stop bar lets 200 / 250 mm bin wheels climb it during stand-up; (3) castors carry 0 N in the tow pose with a full bin for every ballast variant; (4) a downhill e-stop jackknifes to the 40 deg stop unless the yaw pin is in; (5) an uphill-facing stand-up of a full bin leaves its weight on the hook; (6) a light empty bin on 250 mm wheels can sit on the stop bar with no IMU signal.
* **Fix R7 (final):** ratchet pawl lifted after the claim and re-engaged in the tow pose (new 12 V pull solenoid GR-08S); stand-up stops when the bin is upright to the GROUND (IMU pitch + mast angle); straighten by creeping on the rear-frame heading, then pivot in place, then a tapered yaw pin (+/-3 deg); yaw pin in BEFORE any descent; pre-cam interlock: tug pitch <= 2.5 deg, bin <= 3 deg, float off its top stop.
* **R7 results (tested at M110h):** release **30/42** over the 7 bins x 6 cases (30 PASS, 11 HOLD, 1 TIPS) and **30/35 inside the release rule** (4 HOLD, 1 TIPS), against 1 PASS / 9 HOLD for the 10 as-designed cases run. Pose variants (+/-30 mm lateral, +/-2 deg yaw) on flat full and flat empty, 7 bins: **22/28 PASS** (HOLD 6); every non-PASS is a case that already HOLD at v0 (Craemer 240 L flat full, ESE 240 L CL flat full, ESE 240 SL, 250 mm wheels flat full), so the pose offsets add no new failure. E-stop 12 % downhill **12/12** (4 bins x 3 variations, slide 0.001 m, hitch 0.0-0.1 deg vs 35-40 deg as designed). Climb 12 % wet leaves **4/4 at mu 0.30** (11.6-11.8 s, was 17.5-19.9 s) and **4/4 at mu 0.27** (12.2-20.1 s; 3 of 4 failed as designed). Step 40 mm + tow stability **8/8** (SULO step40 was stuck as designed). Grab spot checks with the ratchet lifted: **30/30** on each of ESE 140 CL and Weber 140 at M110h, and Weber 140 and ESE 240 SL at M110 - first try every time, 0 false holds.
* **Release rule:** release only on flat ground or with the tug facing DOWNHILL (bin on the uphill side); never a full bin with the tug facing uphill; an empty bin may be released facing uphill except on 250 mm wheels; if the hook does not come clear after 3 tries (STUCK), hold and alert for the manual release lever.
* **Ballast pick: M110** = 25.5 kg of dry steel punchings, all in the two front cans (no axle plate), replacing M110h. With the fixes it is the only variant with margin at mu 0.25 (12.9 s; M110h 24.6 s of 25; M105h and M110ax fail at mu 0.27), it stops on 12 % downhill like the others (slide 0.001 m, kingpin SF >= 3.8), puts the most load on the drive wheels in the tow pose (1,587 N) and turns the SL 250 and Craemer flat-ground HOLDs into clean releases. Castors in the tow pose are 0 N for every variant, so ballast does not cure castor lift; unladen castor load rises from 109 N to 194 N. Table below.
* **Still failing:** full bin facing uphill (HOLD for all 7 bins at M110h; at M110 the Weber is dropped - excluded by the release rule); full ESE 240 CL on flat (HOLD) and 12 % downhill (STUCK at M110, HOLD at M110h); empty SL 250 facing uphill tips over at release (every variant tried - excluded by the rule); castors 0 N in the tow pose with a full bin (hitch reaches its 40 deg stop over a 40 mm step).

**Ballast pick: M110.** ESE 240 SL 110 kg, fixes on (climb limit 5 m in 25 s):

| ballast | steel kg | CG ahead of axle m | castors unladen N | climb 12 % mu 0.30 | mu 0.27 | mu 0.25 | e-stop 12 % down slide | tow pose full: castors / drive N |
|---|---|---|---|---|---|---|---|---|
| M105h | axle 15 + cans 5.5 | 0.058 | 75.4 | PASS 12.9 s | FAIL 4.08 m | FAIL 1.14 m | PASS 0.001 m | 0.0 / 1400 |
| **M110** | cans 25.5 (chosen) | 0.142 | 193.9 | PASS 11.4 s | PASS 11.9 s | PASS 12.9 s | PASS 0.001 m | 0.0 / 1587 |
| M110h | axle 15 + cans 10.5 | 0.08 | 109.2 | PASS 11.8 s | PASS 13.1 s | PASS 24.6 s | PASS 0.001 m | 0.0 / 1488 |
| M110ax | axle 25.5 | 0.037 | 49.9 | PASS 13.8 s | FAIL 2.10 m | FAIL 1.01 m | PASS 0.001 m | 0.0 / 1419 |

# 0.1 Sim faults found and fixed (artefacts)

1. **Ballast position ignored (major).** sim_g5.build_xml has ballast_x=0.70 as a default and load_rows moves every row whose name starts with "Ballast" there. The G6 mass files name their rows "Ballast fill ..." / "Ballast, steel plate ...", and no G6 script passed ballast_x, so M110, M110h and M110ax all ran with 25.5 kg at x 0.70 m (tug CG 0.178 m ahead of the axle). True M110h CG is 0.080 m ahead. **Fixed:** mass_g6_* files now keep their own positions (G6_LEGACY_BALLASTX=1 reproduces the old behaviour).
2. **Grab Monte Carlo on the wrong mass.** mc_g5.py ignored G6_MASSFILE and used mass_revF.json with ballast=1, so the 207/210 GH-B6 result was not at the G6 operating mass. **Fixed** and re-run at M110h (section 0.4).
3. **Kingpin range 70 deg in the sim vs the +/-40 deg hard stop in the G6 design.** Downhill jackknifes ran to 70 deg. **Fixed:** G6_YAWRANGE=40 for every run-3 case.
4. **Yaw lock modelled as an instant spring (20 kN m/rad) that snaps the rear frame to 0 deg from any angle.** The real part is a solenoid pin that cannot go in off-centre. This snap is what threw the empty Weber out of one hook on 12 % downhill. **Fixed:** G6_PINLOCK=1 (pin only within 2 deg, otherwise release aborts with an alert).
5. **Misleading release message.** "latch/pawl still closed" was printed while both pawls were fully open (-130 deg): the real state was a bin hanging or already dropped, bar 0.8 m from the cup. The "pawls will not open on downhill" reading was wrong. **Fixed** message.
6. **Not fixed, noted:** the brake is a stiff velocity servo, so brake engagement gives contact spikes (2.5 kN on one drive tyre for one sample). Kingpin peak loads taken at that instant are high. The bin is a convex hull, so the bin-on-spine contact is approximate. Lip chamfer: not modelled in the sim, same as the CAD (section 0.6).

**Sanity checks (sanity_g6.py):** ground reaction 1232.9 N vs weight 1232.9 N (error -0.0 %); max contact penetration 0.04 mm; tug alone drive/castor 999.7/105.7 N vs hand moment balance 969.8/109.3 N; timestep 0.0005 s, contact time constant 0.008 s = 16.0 steps (pawl limits 8.0 steps); tug CG 0.08 m ahead of the drive axle with the ballast where the mass file puts it (the old runs had it at 0.178 m).

\needspace{8\baselineskip}

**Timestep sensitivity (0.5 ms vs 0.25 ms):**

| case | dt 0.5 ms | dt 0.25 ms |
|---|---|---|
| climb 12 % mu 0.30 | time_s 19.9, dist_m 5.0 | time_s 18.3, dist_m 5.0 |
| e-stop 12 % down | stop_dist_m 0.1, slide_after_stop_m 0.001, hitch_yaw_max_deg 38.1 | stop_dist_m 0.091, slide_after_stop_m 0.001, hitch_yaw_max_deg 33.4 |
| release WEB 140 12 % up (pin lock) | ok False | ok False |

# 0.2 Real design faults found

1. **Float ratchet lifts the bin during tipping (major).** The GH-B6 float ratchet (one-way, 8 mm pitch) locks the float as the mast tips, so the mast arc lifts the bin by its lip until the bin wheels ride on top of the wheel-stop bar (793 N on the bar, 0 N on the ground). The tug then carries the whole bin, rocks back about 5 deg onto the funnel flares and drags them (table below). With the float free the bin wheels stay on the ground and the flares carry nothing.
2. **Wheel-stop bar too low (major, found in run 4).** During stand-up the mast pulls the bin top back and the bin wheels are pressed into the 100 mm bar (up to 410 N). The bar centre is at the centre of a 200 mm wheel and 25 mm below that of a 250 mm wheel, so the wheel rides up, ends on the bar only and the tug rocks back to its flares (stand-up series below). This is what still holds SL 250, ESE 240 CL and Craemer full bins on flat ground. A second roller at 150 mm (above the wheel centre) or the M110 ballast clears the SL 250 and the Craemer; the ESE 240 CL still rocks the tug back to -5.4 deg with either (not diagnosed further).
3. **Castors unloaded in the tow pose with a full bin.** Every ballast variant gives castors 0 N in the static tow pose (tug pitched -2.7 to -2.9 deg, bin leaning on the rear-frame spine 230-460 N). Steering on the castors is lost while towing a full bin; the hitch swings to its stop over a 40 mm step.
4. **Downhill jackknife.** E-stop on 12 % downhill with the kingpin free swings the hitch to 35-40 deg. With the yaw pin in before any descent it stays at 0.0-0.1 deg.
5. **Uphill-facing stand-up of a full bin.** The bin sits downhill of the tug and its weight stays on the hook: tug pitched -5.4 deg at the end of stand-up for all 7 bins. Not fixable by a firmware stop rule; handled by the release rule.
6. **Empty SL 250 facing uphill falls over at release.** It passed every interlock (tug level, bin upright to the ground) and fell when the cam opened, with M110h, M110 and with the 2nd roller. Until understood: no release of 250 mm-wheel bins facing uphill, or a wheel-on-ground sensor in the interlock.

**Tow pose on flat, ESE 240 SL 110 kg (diag_towpose_g6.py) - where the load goes:**

| case | tug pitch deg | castors N | funnel flares on ground N | bin wheels on stop bar N | bin wheels on ground N | hook N | bin on spine N |
|---|---|---|---|---|---|---|---|
| as designed (ratchet on), M110h | -5.44 | 0.0 | 460.5 | 792.7 | 0.0 | 437.3 | 0.0 |
| as designed, old misplaced ballast | -5.44 | 0.0 | 366.1 | 763.0 | 0.0 | 592.0 | 0.0 |
| + 2nd stop roller at 150 mm | -5.44 | 0.0 | 511.7 | 773.1 | 0.0 | 761.4 | 0.0 |
| float ratchet free in tow | -2.8 | 0.0 | 0.0 | 0.0 | 696.5 | 553.5 | 326.6 |
| as designed, EMPTY bin | -0.0 | 141.5 | 0.0 | 82.9 | 0.0 | 59.5 | 0.0 |

# 0.3 Release: matrix, diagnosis and the release rule

**Fix iterations (all env-gated in scen_g5.py / tow_g5.py, no thresholds changed):** R3 ratchet off always (broke empty grabs + uphill); R4/R5 ratchet lifted after tipping, tapered pin, straighten on heading; R6 ratchet lifted right after the claim, stand-up stop on relative tilt; **R7 (final)** = R6 + stand-up stop on ground-upright (IMU pitch + mast) + pivot in place after the creep straighten (empty bins: 3.5 -> 2.2 deg, inside the 3 deg taper); R8 = R7 + ratchet lifted again for stand-up: identical numbers, so the ratchet is not the stand-up cause and R8 was not adopted. The stand-up diag then showed the wheel climbing the stop bar (finding 2); the 2nd stop roller was tested as a diagnostic only, not as a further fix iteration.

**Release rule (from the matrix):**

1. Release only on flat ground or with the tug facing DOWNHILL (bin on the uphill side). Never stand up / release a full bin with the tug facing uphill: all 7 bins HOLD at M110h, and at M110 the Weber was dropped. Route planning turns the tug round (or picks a flat spot) for a full-bin drop on a slope.
2. Empty bins may be released facing uphill, except 250 mm-wheel bins (SL 250 empty tips over).
3. Before standing the bin up: straighten by following the rear-frame heading (creep, then pivot in place) until the hitch is inside the +/-3 deg pin taper; engage the yaw pin. On any slope the pin goes in BEFORE descending.
4. Stand up until the bin is upright to the ground (tug IMU pitch + mast angle <= 0.3 deg, never past -8 deg relative).
5. Interlock before the cam opens: tug pitch within 2.5 deg, bin within 3 deg, float off its top stop (and within 40 mm of its grab position if the ratchet is in). Otherwise hold + alert.
6. If the hook does not drop clear after 3 tries (STUCK, bin standing), hold + alert for the manual lever (seen for the ESE 240 CL 12 % down at M110 and with the roller).

Cells: pose variants v0/v1/v2 (lateral 0/+30/-30 mm, yaw 0/+2/-2 deg where run). PASS released and standing; HOLD = interlock or yaw pin refused, bin still held, alert (safe); STUCK = bin standing on its wheels, pawls open but the hook did not drop clear of the bar after 3 tries, alert (safe, needs a retry or the manual lever); TIPS = bin ended > 30 deg (unsafe); FAIL = other.

**As designed (GH-B6, ratchet on, current release sequence, realistic yaw pin):**

| bin | flat full | 12% up full | 12% down full | flat empty | 12% up empty | 12% down empty |
|---|---|---|---|---|---|---|
| Weber 140 L | HOLD | HOLD | HOLD | HOLD | HOLD | HOLD |
| ESE 140 L CL | HOLD | HOLD | HOLD | PASS | - | - |
| ESE 240 L SL | - | - | - | - | - | - |
| ESE 240 SL, 250 mm wheels | - | - | - | - | - | - |
| SULO 240 L | - | - | - | - | - | - |
| ESE 240 L CL | - | - | - | - | - | - |
| Craemer 240 L | - | - | - | - | - | - |

**With the final fixes R7 (ratchet pawl lifted after the claim and re-engaged in tow; straighten on the rear-frame heading then pivot; tapered pin +/-3 deg; stand-up stops when the bin is upright in the world (IMU pitch + mast angle) then IMU/float interlock before cam open; yaw pin in before descending):**

| bin | flat full | 12% up full | 12% down full | flat empty | 12% up empty | 12% down empty |
|---|---|---|---|---|---|---|
| Weber 140 L | PASS / PASS / PASS | HOLD | PASS | PASS / PASS / PASS | PASS | PASS |
| ESE 140 L CL | PASS / PASS / PASS | HOLD | PASS | PASS / PASS / PASS | PASS | PASS |
| ESE 240 L SL | PASS / PASS / PASS | HOLD | PASS | PASS / PASS / PASS | PASS | PASS |
| ESE 240 SL, 250 mm wheels | HOLD / HOLD / HOLD | HOLD | PASS | PASS / PASS / PASS | TIPS | PASS |
| SULO 240 L | PASS / PASS / PASS | HOLD | PASS | PASS / PASS / PASS | PASS | PASS |
| ESE 240 L CL | HOLD / HOLD / HOLD | HOLD | HOLD | PASS / PASS / PASS | PASS | PASS |
| Craemer 240 L | HOLD / HOLD / HOLD | HOLD | PASS | PASS / PASS / PASS | PASS | PASS |

**R7 + an upper wheel-stop roller at 150 mm (G6_SB2=0.15, candidate hardware fix, v0 pose only):**

| bin | flat full | 12% up full | 12% down full | flat empty | 12% up empty | 12% down empty |
|---|---|---|---|---|---|---|
| ESE 240 L SL | - | HOLD | - | - | - | - |
| ESE 240 SL, 250 mm wheels | PASS | HOLD | PASS | PASS | TIPS | PASS |
| ESE 240 L CL | HOLD | - | STUCK | - | - | - |
| Craemer 240 L | PASS | - | - | - | - | - |

\needspace{10\baselineskip}

**Fix iterations on the critical cases (v0 pose):**

| case | as designed | R3 | R4 | R5 | R6 | R7 (final) | R8 | R8 + 2nd stop roller (diag) |
|---|---|---|---|---|---|---|---|---|
| ESE 240 L SL, flat full | - | PASS | - | - | PASS | PASS | PASS | PASS |
| SULO 240 L, flat full | - | - | - | - | - | PASS | PASS | - |
| ESE 240 SL, 250 mm wheels, flat full | - | PASS | - | HOLD | HOLD | HOLD | HOLD | PASS |
| Weber 140 L, 12% up full | HOLD | TIPS | HOLD | HOLD | HOLD | HOLD | HOLD | HOLD |
| ESE 240 L SL, 12% down full | - | PASS | - | - | - | PASS | PASS | - |
| Weber 140 L, 12% down empty | HOLD | PASS | - | PASS | PASS | PASS | PASS | - |
| Weber 140 L, flat empty | HOLD | HOLD | HOLD | - | HOLD | PASS | PASS | PASS |
| ESE 140 L CL, flat empty | PASS | FAIL | HOLD | - | HOLD | PASS | PASS | - |

**Stand-up time series, ESE240SL250, flat (diag_stand_g6.py, ratchet re-engaged in tow, mast swept to rel -8 deg):**

| t s | mast deg | bin rel deg | tug pitch deg | bin world deg | float vs grab mm | bin wheels total N | of which on stop bar N | castors N | flares N | hook N |
|---|---|---|---|---|---|---|---|---|---|---|
| 73.0 | 73.52 | 48.12 | -2.38 | 45.74 | -160.3 | 934.0 | 236.0 | 0.0 | 0.0 | 378.0 |
| 75.4 | 71.43 | 46.71 | -2.3 | 44.41 | -160.3 | 882.0 | 167.0 | 0.0 | 0.0 | 329.0 |
| 77.8 | 67.81 | 44.21 | -2.08 | 42.13 | -160.2 | 867.0 | 120.0 | 0.0 | 0.0 | 285.0 |
| 80.2 | 64.2 | 41.68 | -1.78 | 39.9 | -160.2 | 882.0 | 104.0 | 0.0 | 0.0 | 257.0 |
| 82.6 | 60.58 | 39.14 | -1.42 | 37.72 | -160.2 | 905.0 | 96.0 | 0.0 | 0.0 | 234.0 |
| 85.0 | 56.97 | 36.57 | -0.99 | 35.59 | -160.2 | 928.0 | 90.0 | 0.0 | 0.0 | 211.0 |
| 87.4 | 53.35 | 33.99 | -0.49 | 33.5 | -160.2 | 952.0 | 84.0 | 0.0 | 0.0 | 190.0 |
| 89.8 | 49.75 | 31.43 | -0.0 | 31.43 | -159.6 | 1080.0 | 21.0 | 142.0 | 0.0 | 28.0 |
| 92.2 | 46.13 | 27.16 | -0.0 | 27.16 | -157.4 | 1130.0 | 48.0 | 112.0 | 0.0 | 53.0 |
| 94.6 | 42.51 | 24.82 | -0.0 | 24.82 | -149.0 | 1156.0 | 65.0 | 90.0 | 0.0 | 73.0 |
| 97.0 | 38.89 | 22.45 | -0.0 | 22.45 | -139.9 | 1181.0 | 84.0 | 65.0 | 0.0 | 94.0 |
| 99.4 | 35.28 | 20.05 | -0.0 | 20.05 | -129.9 | 1206.0 | 105.0 | 39.0 | 0.0 | 116.0 |
| 101.8 | 31.66 | 17.61 | -0.0 | 17.61 | -119.3 | 1229.0 | 127.0 | 9.0 | 0.0 | 137.0 |
| 104.2 | 28.04 | 15.15 | -0.05 | 15.1 | -107.3 | 1306.0 | 178.0 | 0.0 | 0.0 | 160.0 |
| 106.6 | 24.42 | 12.66 | -0.27 | 12.39 | -92.4 | 1417.0 | 250.0 | 0.0 | 0.0 | 184.0 |
| 109.0 | 20.79 | 10.13 | -0.75 | 9.38 | -73.5 | 1549.0 | 339.0 | 0.0 | 0.0 | 210.0 |

**Stand-up time series, WEB140, up12 (diag_stand_g6.py, ratchet re-engaged in tow, mast swept to rel -8 deg):**

| t s | mast deg | bin rel deg | tug pitch deg | bin world deg | float vs grab mm | bin wheels total N | of which on stop bar N | castors N | flares N | hook N |
|---|---|---|---|---|---|---|---|---|---|---|
| 68.8 | 74.42 | 48.09 | -4.62 | 43.47 | -88.3 | 500.0 | 101.0 | 0.0 | 0.0 | 271.0 |
| 71.2 | 72.1 | 46.5 | -4.58 | 41.92 | -88.2 | 482.0 | 71.0 | 0.0 | 0.0 | 247.0 |
| 73.6 | 68.49 | 43.98 | -4.43 | 39.55 | -88.2 | 477.0 | 45.0 | 0.0 | 0.0 | 220.0 |
| 76.0 | 64.88 | 41.45 | -4.22 | 37.23 | -88.2 | 486.0 | 33.0 | 0.0 | 0.0 | 202.0 |
| 78.4 | 61.26 | 38.89 | -3.93 | 34.96 | -88.2 | 501.0 | 27.0 | 0.0 | 0.0 | 185.0 |
| 80.8 | 57.65 | 36.33 | -3.59 | 32.74 | -88.2 | 516.0 | 0.0 | 0.0 | 0.0 | 168.0 |
| 83.2 | 54.04 | 33.74 | -3.17 | 30.57 | -88.2 | 530.0 | 0.0 | 0.0 | 0.0 | 152.0 |
| 85.6 | 50.43 | 31.15 | -2.69 | 28.45 | -88.1 | 545.0 | 14.0 | 0.0 | 0.0 | 138.0 |
| 88.0 | 46.82 | 28.54 | -2.15 | 26.39 | -88.1 | 562.0 | 11.0 | 0.0 | 0.0 | 123.0 |
| 90.4 | 43.21 | 25.91 | -1.53 | 24.37 | -88.1 | 578.0 | 10.0 | 0.0 | 0.0 | 110.0 |
| 92.8 | 39.61 | 23.25 | -0.85 | 22.4 | -88.1 | 590.0 | 0.0 | 0.0 | 0.0 | 98.0 |
| 95.2 | 35.99 | 18.93 | -0.43 | 18.5 | -88.0 | 622.0 | 0.0 | 0.0 | 0.0 | 85.0 |
| 97.6 | 32.39 | 16.76 | -0.0 | 16.75 | -86.4 | 658.0 | 0.0 | 17.0 | 0.0 | 76.0 |
| 100.0 | 28.78 | 14.35 | -0.01 | 14.34 | -75.9 | 659.0 | 0.0 | 0.0 | 0.0 | 86.0 |
| 100.8 | 27.57 | 13.74 | -1.94 | 11.8 | -48.2 | 658.0 | 0.0 | 0.0 | 0.0 | 95.0 |
| 101.0 | 27.27 | 13.81 | -3.65 | 10.17 | -27.1 | 656.0 | 0.0 | 0.0 | 0.0 | 94.0 |

# 0.4 Grab Monte Carlo at M110h

| bin | captured | 95 % CI | first try | false holds | FP 95 % CI | other outcomes |
|---|---|---|---|---|---|---|
| Weber 140 L | 30/30 | 89-100 % | 30/30 | 0 | 0-11 % | - |
| ESE 140 L CL | 30/30 | 89-100 % | 30/30 | 0 | 0-11 % | - |
| ESE 240 L SL | 30/30 | 89-100 % | 30/30 | 0 | 0-11 % | - |
| ESE 240 SL, 250 mm wheels | 30/30 | 89-100 % | 30/30 | 0 | 0-11 % | - |
| SULO 240 L | 29/30 | 83-99 % | 29/30 | 0 | 0-11 % | no_dock 1 |
| ESE 240 L CL | 29/30 | 83-99 % | 29/30 | 0 | 0-11 % | no_dock 1 |
| Craemer 240 L | 28/30 | 79-98 % | 28/30 | 0 | 0-11 % | safe_miss 1, no_dock 1 |

With the ratchet pawl lifted after the claim (R7): ESE 140 L CL 30/30 captured, first try 30, false holds 0, success 30.

With the ratchet pawl lifted after the claim (R7): Weber 140 L 30/30 captured, first try 30, false holds 0, success 30.

The ratchet change only acts after the claim, so the grab itself is unchanged; the spot check confirms that tipping with a free float does not lose empty bins.

# 0.5 Driving with a bin (110 kg gross)

| bin | test | result | dist m | hitch/bin yaw peak deg | roll peak deg | castor min N | pawl bounce | captured at end |
|---|---|---|---|---|---|---|---|---|
| Weber 140 L | step40 | PASS | 4.5 | 40.2 | 0.2 | 0.0 | none | True |
| Weber 140 L | towstab | PASS | 8.47 | 37.9 | 0.0 | 0.0 | none | True |
| ESE 240 L SL | step40 | PASS | 4.5 | 40.2 | 0.3 | 0.0 | none | True |
| ESE 240 L SL | towstab | PASS | 8.36 | 40.1 | 0.0 | 0.0 | none | True |
| SULO 240 L | step40 | FAIL | 2.18 | 40.2 | 0.0 | 0.0 | none | True |
| SULO 240 L | towstab | PASS | 8.15 | 40.1 | 0.0 | 0.0 | none | True |
| Craemer 240 L | step40 | PASS | 4.5 | 40.2 | 0.3 | 0.0 | none | True |
| Craemer 240 L | towstab | PASS | 8.39 | 40.1 | 0.0 | 0.0 | none | True |
| Weber 140 L (ratchet free) | step40 | PASS | 4.5 | 41.2 | 0.2 | 0.0 | none | True |
| Weber 140 L (ratchet free) | towstab | PASS | 8.69 | 27.4 | 0.0 | 0.0 | none | True |
| ESE 240 L SL (ratchet free) | step40 | PASS | 4.5 | 43.6 | 0.1 | 0.0 | none | True |
| ESE 240 L SL (ratchet free) | towstab | PASS | 8.74 | 29.8 | 0.0 | 0.0 | none | True |
| SULO 240 L (ratchet free) | step40 | PASS | 4.5 | 44.6 | 0.1 | 0.0 | none | True |
| SULO 240 L (ratchet free) | towstab | PASS | 8.74 | 30.2 | 0.0 | 0.0 | none | True |
| Craemer 240 L (ratchet free) | step40 | PASS | 4.5 | 44.7 | 0.4 | 0.0 | none | True |
| Craemer 240 L (ratchet free) | towstab | PASS | 8.64 | 26.0 | 0.0 | 0.0 | none | True |

**Climb 12 % wet leaves:**

| bin | test | result | dist m | time s | hold creep m | hitch peak deg | captured throughout |
|---|---|---|---|---|---|---|---|
| Weber 140 L | mu 0.30 | PASS | 5.0 | 17.5 | 0.01 | 0.2 | True |
| Weber 140 L | mu 0.27 | PASS | 5.0 | 20.9 | 0.011 | 0.1 | True |
| ESE 240 L SL | mu 0.30 | PASS | 5.0 | 19.9 | 0.011 | 0.2 | True |
| ESE 240 L SL | mu 0.27 | FAIL | 0.77 | 25.0 | 0.002 | 0.1 | True |
| SULO 240 L | mu 0.30 | PASS | 5.0 | 18.1 | 0.011 | 0.1 | True |
| SULO 240 L | mu 0.27 | FAIL | 0.91 | 25.0 | 0.002 | 0.2 | True |
| Craemer 240 L | mu 0.30 | PASS | 5.0 | 18.6 | 0.012 | 0.2 | True |
| Craemer 240 L | mu 0.27 | FAIL | 0.83 | 25.0 | 0.006 | 0.4 | True |

**E-stop on 12 % downhill (3 variations):**

| bin | variation | result | stop m | slide m | hitch peak deg | captured throughout |
|---|---|---|---|---|---|---|
| Weber 140 L | mu .30 v .5 | PASS | 0.084 | 0.001 | 36.6 | True |
| Weber 140 L | mu .27 v .5 dy +30 | PASS | 0.13 | 0.001 | 40.2 | True |
| Weber 140 L | mu .30 v .6 yaw +2 | PASS | 0.135 | 0.002 | 40.2 | True |
| ESE 240 L SL | mu .30 v .5 | PASS | 0.1 | 0.001 | 38.1 | True |
| ESE 240 L SL | mu .27 v .5 dy +30 | PASS | 0.112 | 0.001 | 38.7 | True |
| ESE 240 L SL | mu .30 v .6 yaw +2 | PASS | 0.13 | 0.001 | 39.3 | True |
| SULO 240 L | mu .30 v .5 | PASS | 0.097 | 0.001 | 35.0 | True |
| SULO 240 L | mu .27 v .5 dy +30 | PASS | 0.111 | 0.001 | 37.6 | True |
| SULO 240 L | mu .30 v .6 yaw +2 | PASS | 0.137 | 0.001 | 40.2 | True |
| Craemer 240 L | mu .30 v .5 | PASS | 0.113 | 0.001 | 35.2 | True |
| Craemer 240 L | mu .27 v .5 dy +30 | PASS | 0.123 | 0.001 | 35.0 | True |
| Craemer 240 L | mu .30 v .6 yaw +2 | PASS | 0.117 | 0.001 | 40.1 | True |

**Climb 12 % WITH FIXES (ratchet free in tip, re-engaged in tow):**

| bin | test | result | dist m | time s | hold creep m | hitch peak deg | castor min N | captured throughout |
|---|---|---|---|---|---|---|---|---|
| Weber 140 L | mu 0.30 | PASS | 5.0 | 11.6 | 0.029 | 0.9 | 0.0 | True |
| Weber 140 L | mu 0.27 | PASS | 5.0 | 12.2 | 0.039 | 0.8 | 0.0 | True |
| ESE 240 L SL | mu 0.30 | PASS | 5.0 | 11.8 | 0.042 | 1.1 | 0.0 | True |
| ESE 240 L SL | mu 0.27 | PASS | 5.0 | 13.1 | 0.035 | 0.7 | 0.0 | True |
| SULO 240 L | mu 0.30 | PASS | 5.0 | 11.8 | 0.028 | 1.5 | 0.0 | True |
| SULO 240 L | mu 0.27 | PASS | 5.0 | 13.6 | 0.033 | 0.7 | 0.0 | True |
| Craemer 240 L | mu 0.30 | PASS | 5.0 | 11.8 | 0.03 | 1.8 | 0.0 | True |
| Craemer 240 L | mu 0.27 | PASS | 5.0 | 20.1 | 0.007 | 2.6 | 0.0 | True |

**E-stop 12 % downhill WITH FIXES (yaw pin in before descent):**

| bin | variation | result | stop m | slide m | hitch peak deg | castor min N | captured throughout |
|---|---|---|---|---|---|---|---|
| Weber 140 L | mu .30 v .5 | PASS | 0.095 | 0.001 | 0.0 | 0.0 | True |
| Weber 140 L | mu .27 v .5 dy +30 | PASS | 0.121 | 0.001 | 0.0 | 0.0 | True |
| Weber 140 L | mu .30 v .6 yaw +2 | PASS | 0.123 | 0.001 | 0.0 | 0.0 | True |
| ESE 240 L SL | mu .30 v .5 | PASS | 0.112 | 0.001 | 0.1 | 0.0 | True |
| ESE 240 L SL | mu .27 v .5 dy +30 | PASS | 0.15 | 0.001 | 0.0 | 0.0 | True |
| ESE 240 L SL | mu .30 v .6 yaw +2 | PASS | 0.14 | 0.001 | 0.0 | 0.0 | True |
| SULO 240 L | mu .30 v .5 | PASS | 0.113 | 0.001 | 0.1 | 0.0 | True |
| SULO 240 L | mu .27 v .5 dy +30 | PASS | 0.124 | 0.001 | 0.0 | 0.0 | True |
| SULO 240 L | mu .30 v .6 yaw +2 | PASS | 0.157 | 0.001 | 0.1 | 0.0 | True |
| Craemer 240 L | mu .30 v .5 | PASS | 0.122 | 0.001 | 0.1 | 0.0 | True |
| Craemer 240 L | mu .27 v .5 dy +30 | PASS | 0.148 | 0.001 | 0.0 | 0.0 | True |
| Craemer 240 L | mu .30 v .6 yaw +2 | PASS | 0.204 | 0.001 | 0.1 | 0.0 | True |

Freeing the ratchet in the tip and re-engaging it in the tow pose takes the bin off the flares: climb times at mu 0.30 fall from 17.5-19.9 s to 11.6-11.8 s and mu 0.27 passes with every bin (12.2-20.1 s). Hold creep on 12 % rises to at most 0.04 m (limit 0.05 m) because the bin now rolls on its own wheels. E-stop on 12 % downhill needs the yaw pin in before descending; with it there is no jackknife. Tow-stability hitch peaks drop from 38-40 deg to 26-30 deg. The castors stay unloaded with a full bin (finding 3), so the 40 mm step still drives the hitch onto its 40 deg stop (41-45 deg incl. stop compliance); it holds and the bin stays captured.

# 0.5b Ballast re-check with the corrected placement (ESE 240 SL 110 kg, fixes on)

| ballast | CG ahead of axle m | castors unladen N (hand) | drive unladen N (hand) | climb 12 % mu 0.30 | climb mu 0.27 | climb mu 0.25 | e-stop 12 % down | tow pose flat, full 240 SL (ratchet free): castors / tug pitch / bin wheels on ground |
|---|---|---|---|---|---|---|---|---|
| M105h | 0.058 | 75.4 | 954.7 | PASS 5.00 m 12.9 s | FAIL 4.08 m | FAIL 1.14 m | PASS slide 0.001 m, hitch 0.1 deg | 0.0 N, pitch -2.85 deg, bin wheels 736 N |
| M110 | 0.142 | 193.9 | 885.2 | PASS 5.00 m 11.4 s | PASS 5.00 m | PASS 5.00 m | PASS slide 0.001 m, hitch 0.1 deg | 0.0 N, pitch -2.7 deg, bin wheels 598 N |
| M110h | 0.08 | 109.2 | 970.0 | PASS 5.00 m 11.8 s | PASS 5.00 m | PASS 5.00 m | PASS slide 0.001 m, hitch 0.1 deg | 0.0 N, pitch -2.8 deg, bin wheels 696 N |
| M110ax | 0.037 | 49.9 | 1029.3 | PASS 5.00 m 13.8 s | FAIL 2.10 m | FAIL 1.01 m | PASS slide 0.001 m, hitch 0.0 deg | 0.0 N, pitch -2.88 deg, bin wheels 765 N |

Grab MC at M110 (ratchet lifted after claim): Weber 140 L 30/30 captured, first try 30, false holds 0, success 30.

Grab MC at M110 (ratchet lifted after claim): ESE 240 L SL 30/30 captured, first try 30, false holds 0, success 30.

Driving at M110, ESE 240 SL step40: PASS, hitch/bin yaw peak 43.4 deg, castor min 0.0 N, roll 0.1 deg (M110h: 43.6 deg, 0.0 N).

Driving at M110, ESE 240 SL towstab: PASS, hitch/bin yaw peak 29.7 deg, castor min 0.0 N, roll 0.0 deg (M110h: 29.8 deg, 0.0 N).

**Release with the R7 rules: M110h vs M110 (all 25.5 kg in the front cans), the critical cases:**

| case | M110h | M110 |
|---|---|---|
| Weber 140 L, 12% up full | HOLD | TIPS |
| ESE 240 L SL, 12% up full | HOLD | HOLD |
| SULO 240 L, 12% up full | HOLD | HOLD |
| ESE 240 SL, 250 mm wheels, flat full | HOLD | PASS |
| ESE 240 L CL, flat full | HOLD | HOLD |
| ESE 240 L CL, 12% down full | HOLD | STUCK |
| Craemer 240 L, flat full | HOLD | PASS |
| ESE 240 SL, 250 mm wheels, 12% up empty | TIPS | TIPS |
| ESE 240 L SL, flat full | PASS | PASS |
| Weber 140 L, 12% down empty | PASS | PASS |
| Weber 140 L, flat empty | PASS | PASS |
| ESE 140 L CL, flat empty | PASS | PASS |

**Ballast pick: M110** (all 25.5 kg in the front cans). It is the only variant with margin at mu 0.25, it unloads nothing that matters (castors are 0 N in tow for every variant), it raises the unladen castor load from 109 to 194 N, and it needs no axle-box plate. It does not fix the uphill-facing full-bin case (release rule) and it made one downhill release STUCK instead of HOLD; both are covered by the alert path. Grab and driving spot checks at M110 are listed above.

# 0.6 CAD vs sim geometry (GA drawing pass)

**The sim and the CAD use the same hook profile code (geo_g3.gh_cup), so they match on shape - and both left the 6 x 45 lip chamfer uncut** (the slope box sits inside the lip outline; in the CAD it also left a 1 mm spike). Every GH-B6 grab result is therefore for a square lip corner. The chamfer only helps a bar that lands on the lip edge, so cutting it should not reduce capture, but that is not simulated. **Placement:** in the sim the hook rides on the float joint (ref 0.70 m + float travel), and the cup rises until it meets the bar, so the bar sits on the cup floor (bar centre -10..-13 mm, radius 13.5 mm). g6_layer.py built the hook group at a fixed S = 700, so in the exported STEPs it floated 162 mm (tow) / 30 mm (docked) off the crossbar. **Fixed in g6_layer.py** (HOOK_FOLLOW_S: hook group follows the carriage s; CUT_CHAMFER: real 45 deg cut, spike removed; backup g6_layer_pre_hookfix.py), and the tow and docked STEPs, the STL and the GR-03/04/61/63 part STEPs were re-exported (export_g6_steps.py). **Remaining CAD-vs-sim mismatch:** the CAD pose solver places the carriage at its s without the float rise, so the CAD bar sits 30 mm above the cup centre (40 mm above the floor) in both grab and tow poses. Physically the float rises those 40 mm (sim). **Done in run 4:** the whole float group (slide carriage, pads, crossbar, IMU, cam bar, gearmotor, hooks, pawls, feelers) moves 40 mm up the mast in the bin-engaged poses (FLOAT_DZ), so the bar now sits on the cup floor in tow and grab, dock unchanged; GR-08S added on the slide carriage; no interference with any tug part in any exported pose. The full fit sweep (fit_g6_final.py) was not re-run.

| CAD pose | carriage s mm | hook-group correction mm | bar centre above cup centre mm | bar bottom above cup floor mm |
|---|---|---|---|---|
| tow48 | 567.8 | -162.2 | -10.0 | 0.0 |
| dock | 700.0 | -30.0 | - | - |
| grab0 | 730.0 | 0.0 | -10.0 | 0.0 |

GR-03 volume without / with the chamfer cut: 106937.2 / 106747.8 mm3, bbox (x, z) [12.03, 151.0, 944.0, 1260.0] / [13.0, 151.0, 944.0, 1260.0].

# 0.7 Remaining failures and open points (run 4, final)

1. **Full bin facing uphill:** no release (HOLD) - handled by the release rule and route planning, not fixed.
2. **Wheel-stop climb at stand-up:** SL 250 and Craemer full on flat are cleared by M110 or by a 2nd stop roller at 150 mm (sim only, G6_SB2, not in CAD); the full ESE 240 CL still HOLDs on flat and HOLD/STUCKs on 12 % down - safe but not released; needs its own stand-up diagnosis.
3. **Empty SL 250 facing uphill tips over at release** with every variant tried - release rule excludes it; root cause open.
4. **Castors 0 N in the tow pose with a full bin** for every ballast variant; hitch hits its 40 deg stop over a 40 mm step. Needs a tow-pose geometry change (spine contact / tow angle), not ballast.
5. **CAD:** ratchet lift solenoid GR-08S added and the float group raised 40 mm so the bar sits on the cup floor (no interference in tow, grab or dock); not re-run through the full fit sweep, and the CAD still carries two float-stop sets (Rev F +/-10 mm and K1 +/-60 mm) that do not match the sim float travel (-100/+130 mm). 2nd stop roller not in CAD.
6. **Sim limits:** bin is a convex hull (spine contact approximate), brake is a stiff servo (load spikes), lip chamfer not modelled, pose variants only +/-30 mm / +/-2 deg, one MC spot check per bin.

# 0b. Earlier G6 decisions (written before run 3 - where run 3 changes them, section 0 wins)

Rules applied: end product only (no mule stage), no capability cuts, improve without making anything else worse, report failures as found.

* **Hook GH-B6 - ACCEPTED.** 58 mm throat, 8 mm lip 2 mm lower with a 6 mm chamfer, cranked pawl, one firmware re-rise, feeler threshold 20 mm. Paired against G5 (same bins, seeds, samples): **207/210 captures vs 202/210 for G5, 6 fixed, 1 lost, false holds 0 (G5 0).** The one sample that went from success to fail (Craemer idx 19) is a docking-funnel edge case, not the hook: the hook never touches the bin in that run, and the G5 hook fails at 3 of 4 neighbouring offsets (dy -77/-80/-82 mm). A firmware re-dock on approach timeout recovers it (tested: success). That re-dock is added to the firmware list.
* **Actuator: LINAK LA36, 24 V, 12 mm pitch, H gear (6,800 N, 13 mm/s at load), 400 mm stroke (BID 650), IP66/IP69K, built-in hand crank.** The LA34 is rated +5..+40 C only; [nearby town] (Met Eireann 1991-2020) has mean daily minima of 3.3-4.0 C from December to March, about 20 air-frost days a year and an absolute minimum of -11.4 C, and the bins go out at night - so the LA34 would run outside its rating on most winter nights. Its 160 mm motor housing also hits the mast rail in CAD (up to 108,600 mm3). The LA36 is rated to -30 C at 50 %% load (3,400 N = 1.4 x the 2,473 N peak) and passed every tilt run, including a -30 C derated run.
* **Actuator line moved to y = 215 mm (+10 mm), motor block on the upper side (back fixture 0 deg).** At y 205 the LA36 block clips the mast rail in every orientation; at 215 it clears in all poses. The rod-end clevis on the mast (MA-56) moves out 10 mm with it.
* **Clevis: the placeholder was unsafe (1185.0 MPa at the 2,473 N operating peak, SF 0.3).** Replaced by RF-57 (folded 8 mm U clevis, pin D12) on RF-58/59 (folded 6 mm box outrigger welded to the spine and RF-53). Hand calculation: every check SF >= 3.75 at the operating peak and >= 1.36 at the LA36 6,800 N rating.
* **Ballast: {'M95': {'kg': 95.0, 'cg_x_m': 0.078, 'cg_z_m': 0.309, 'castor_N': 92.4, 'drive_N': 839.6}, 'M100': {'kg': 100.0, 'cg_x_m': 0.102, 'cg_z_m': 0.301, 'castor_N': 126.3, 'drive_N': 854.8}, 'M105': {'kg': 105.0, 'cg_x_m': 0.123, 'cg_z_m': 0.294, 'castor_N': 160.1, 'drive_N': 870.0}, 'M105h': {'kg': 105.0, 'cg_x_m': 0.058, 'cg_z_m': 0.295, 'castor_N': 75.4, 'drive_N': 954.7}, 'M110': {'kg': 110.0, 'cg_x_m': 0.142, 'cg_z_m': 0.288, 'castor_N': 193.9, 'drive_N': 885.2}, 'M110h': {'kg': 110.0, 'cg_x_m': 0.08, 'cg_z_m': 0.287, 'castor_N': 109.2, 'drive_N': 970.0}, 'M110ax': {'kg': 110.0, 'cg_x_m': 0.037, 'cg_z_m': 0.287, 'castor_N': 49.9, 'drive_N': 1029.3}}.** Re-checked in run 4 with the ballast where the mass file puts it AND the ratchet fix on (ESE 240 SL 110 kg, section 0.5b). Forward ballast wins: M110 climbs 12 % at mu 0.25 in 12.9 s, M110h only just (24.6 s of 25), M105h and M110ax (axle) fail at mu 0.27. Reason: with a full bin the tug rests on its drive wheels and the bin (castors 0 N for every variant), so ballast ahead of the axle goes to the drive wheels (1,587 N at M110 vs 1,419 N at M110ax in the static tow pose). E-stop on 12 % downhill is the same for all (slide 0.001 m); kingpin SF >= 3.8. M110 also releases the SL 250 and the Craemer cleanly on flat ground where M110h held. Grab MC at M110: Weber 140 and ESE 240 SL 30/30 each, first try, 0 false holds; step40 / towstab as M110h.
* **Kingpin: A0 (no move).** B38 was rejected: its queued sweep turned the rear frame about the old axis (so the result is not valid), it adds a washer-to-tray clash, and it would change the hitch geometry that every sim, the SITL model and the kingpin check use. At A0 the true limit was the hinge saddle meeting the drive tyre at ~40.5 deg, so the saddle scallop is deepened to |y| <= 130 mm. **Result: hard stop +/-40 deg (pin on the UHMW block), saddle-to-tyre 19.8 mm, mast rail 8.3 mm, pivot lug 10.3 mm at 40 deg.** SITL: set BT_HITCH_CAP = 40 (it runs 28 today). +/-42 is not reachable at A0 without moving the mast rails - the rail is 1.7 mm from the tyre at 42 deg.
* **Clash fixed:** drive plugs DT-A/DT-B moved 75 mm inboard on the pod wall (PD-12): spring-brake interference 29,965 / 16,010 mm3 and the M12 connector 1,673 mm3 are gone. Final fit check: **no tug-to-tug interference in 7 poses**; only CAD bin-pose overlaps remain (section 6).
* **New/changed in CAD and drawings:** GH-B6 hook plates at +/-130 mm with an R16 pawl-pivot boss (the G5 hole straddled the plate edge), drain slots, inductive feelers, LD2451 radomes (inner 76 x 41 x 18), AS5600 kingpin sensor mount, RF-57/58/59, RF-03 scallop, GR-07 moved 6 mm inboard. STEP (tow, docked), STL, 13 part STEPs, 38 DXF, Drawings_G6.pdf (57 parts).
* **(Superseded by section 0.3: traced in run 3.)** Earlier note: the ESE 240 SL on **250 mm wheels does not release** in the tilt/release run. It fails the same way with the G5 hook and G5 actuator model, so it is not caused by G6, and G5 never tested release on this bin. Details and next step in section 7.
* **Material:** Z275 pre-galvanised sheet only up to 3 mm, so the tray and all sheet parts of 3 mm or less are S250GD+Z275; plates of 6-10 mm are S355J2, hot-dip galvanised after welding, with zinc-rich primer as the approved alternative. **Tray: 2 mm galvanised steel, not aluminium** - about EUR 90 cheaper, and its ~6.4 kg extra sits low and replaces ballast (the g6-parts fab estimate priced 5083 Al and needs updating).

# 1. Hook GH-B6 vs G5 (paired, 30 samples per bin)

Same bins, seeds (501-507) and samples as the G5 K2h130 runs. G5 = hooks +/-130, 48 mm throat, straight pawl, feeler 12 mm. GH-B6 = throat -34 (58 mm), lip 8 mm wide, top -2 mm, 6 mm chamfer, cranked pawl knee (-18,35) tip (-33,19), firmware re-rise 0.6 deg, feeler threshold 20 mm. Capture includes one re-dock.

| bin | G5 capture | G6 capture | false holds G5 / G6 | first try G5 / G6 | notes |
|---|---|---|---|---|---|
| Weber 140 L | 27/30 | 30/30 | 0 / 0 | 26 / 30 | fixed idx 7,21,29 |
| ESE 140 L CL | 30/30 | 30/30 | 0 / 0 | 30 / 30 | - |
| ESE 240 L SL | 29/30 | 29/30 | 0 / 0 | 29 / 29 | G6 non-success: no_dock 1 |
| ESE 240 SL, 250 mm wheels | 29/30 | 30/30 | 0 / 0 | 29 / 30 | fixed idx 17 |
| SULO 240 L | 27/30 | 29/30 | 0 / 0 | 26 / 29 | fixed idx 11,29; G6 non-success: no_dock 1 |
| ESE 240 L CL | 30/30 | 30/30 | 0 / 0 | 30 / 30 | - |
| Craemer 240 L | 30/30 | 29/30 | 0 / 0 | 30 / 29 | lost idx 19 (no_dock); G6 non-success: no_dock 1 |

**Total: G5 202/210, G6 207/210; 6 samples fixed, 1 lost; false holds 0 -> 0.**

**The one lost sample (Craemer 240, idx 19, bin 78 mm off-centre).** The tug never reached the wheel stop: the right bin wheel rode the funnel flare and the 14 s approach timed out. A contact log of the approach shows no hook or pawl contact at all. An approach-only sweep of the lateral offset shows a chaotic edge of the funnel capture range for both hooks: GH-B6 docks at dy -70/-74/-76 mm and fails at -78/-80; the G5 hook fails at -77, -80 and -82 and docks at -79. The approach is the same code; the hook mass and geometry only nudge which side of the edge one sample falls. The existing firmware retries only when the squaring guard trips. **Firmware change: also back off and re-dock when the approach times out** - with it, idx 19 is captured (retry run: {'success': 1}).

**Robustness runs (12 samples each, finished at report time):**

| condition | bin | capture | false holds | outcomes |
|---|---|---|---|---|
| ice film on the bar, hook friction x0.2 (i2) | Weber 140 L | 12/12 | 0 | success 12 |
| ice film on the bar, hook friction x0.2 (i2) | ESE 240 L SL | 11/12 | 0 | success 11, no_dock 1 |
| ice film on the bar, hook friction x0.2 (i2) | SULO 240 L | 11/12 | 0 | success 11, no_dock 1 |
| ice film on the bar, hook friction x0.2 (i2) | Craemer 240 L | 12/12 | 0 | success 12 |
| ice, hook friction x0.5 (i5) | Weber 140 L | 12/12 | 0 | success 12 |
| ice, hook friction x0.5 (i5) | ESE 240 L SL | 11/12 | 0 | success 11, no_dock 1 |
| ice, hook friction x0.5 (i5) | SULO 240 L | 11/12 | 0 | success 11, no_dock 1 |
| ice, hook friction x0.5 (i5) | Craemer 240 L | 12/12 | 0 | success 12 |
| grit / dirty bar (g5) | Weber 140 L | 12/12 | 0 | success 12 |
| grit / dirty bar (g5) | SULO 240 L | 11/12 | 0 | success 11, no_dock 1 |
| camera steering OFF (no-steer) | Weber 140 L | 7/12 | 0 | success 7, safe_miss 4, no_dock 1 |
| camera steering OFF (no-steer) | ESE 140 L CL | 5/12 | 0 | no_dock 1, success 5, safe_miss 6 |
| camera steering OFF (no-steer) | ESE 240 L SL | 12/12 | 0 | success 12 |
| no-steer + ice i5 | Weber 140 L | 7/12 | 0 | success 7, safe_miss 4, no_dock 1 |
| no-steer + ice i5 | ESE 140 L CL | 5/12 | 0 | no_dock 1, success 5, safe_miss 6 |
| no-steer + ice i5 | ESE 240 L SL | 12/12 | 0 | success 12 |


# 2. Tilt actuator

Requirement from the G6 geometry with the base pin at x 580, z 340: pin-to-pin 656-1042 mm over the mast window, force 2,359-2,457 N (actuator_fit_g6.json), sim peak 2,473 N (ESE 240 SL 250 unload retry).

| option | force | speed at load | temperature rating | IP | fits CAD | verdict |
|---|---|---|---|---|---|---|
| LINAK LA34 L 400, 12 mm (surplus hoist) | 10,000 N | 4.8 mm/s | +5..+40 C | IPX6 | NO - housing hits mast rail 7,773-108,591 mm3 | rejected: winter nights below +5 C; CAD clash |
| ELA 0041941-1 (g6-parts pick) | 2,500 N at 10 mm/s | 10 mm/s | -20..+60 C | IP67 | not modelled | rejected: 2,500 N vs 2,473 N peak = SF 1.0 |
| **LINAK LA36 24 V 12 mm H, 400 stroke** | **6,800 N** (3,400 N at -30 C) | **13 mm/s** | -30 C (50 % load)..+85 C, full +5..+40 C | IP66 / IP69K | **yes at y 215, back fixture 0 deg** | **chosen** |
| LINAK LA36 16 mm H | 5,600 N | 17 mm/s | as above | IP66 | yes | passes; less margin cold (2,800 N at -30 C = SF 1.13) |

LA36 data sheet (web/downloads/g6act/linak_LA36_datasheet.txt): BID = 250 + S for S > 300 -> 650 / 1,050 mm against the 656.6-1,030 mm the tilt runs used (6.6 and 20 mm margin). Eyes D12.2: pins D12 h9, holes 12H9 at both ends, solid back fixture with PTFE bush (data-sheet option). Hand crank 6-8 Nm, 4 mm rod travel per turn on the 12 mm H spindle: controlled lowering of a loaded mast with the power off is kept. Mass about 6.0 kg (4.55 kg at 100 mm + 0.24 kg per 50 mm) vs 4.5 kg LA34 - taken out of the ballast fill.

**Quick-release mast pin instead of the hand crank: not safe as the fault-recovery means.** A ball-lock pin can only be pulled with no load on it; under a tilted loaded bin it either will not come out or, if it does, the mast falls (crush and pinch hazard). The LA36 has its own hand crank, so the pin is not needed. A D12 ball-lock pin with a lanyard is acceptable only as a service disconnect with the mast resting on its stop and no bin on the hooks (labelled), not in the fault procedure.

**Tilt / release runs (G6 hook, one nominal bin each):**

| bin | actuator | F cap N | peak N | pin-pin mm | grab s | tip s | rel. s | Wh | held | released | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| WEB140 | LA36 12H | 6800 | 2080 | 664..997 | 38.6 | 19.8 | 52.2 | 1.73 | yes | yes | PASS |
| WEB140 | LA36 16H | 5600 | 2080 | 664..997 | 38.6 | 19.8 | 52.2 | 1.82 | yes | yes | PASS |
| WEB140 | LA34 12 | 10000 | 2208 | 680..987 | 38.6 | 19.8 | 52.4 | 1.06 | yes | yes | PASS |
| WEB140 | G5 model | 2500 | 1979 | 651..1007 | 38.6 | 19.8 | 52.2 | - | yes | yes | PASS |
| ESE240SL | LA36 12H | 6800 | 2073 | 665..995 | 38.6 | 19.2 | 54.0 | 1.87 | yes | yes | PASS |
| ESE240SL | LA36 12H -30C | 3400 | 2073 | 665..995 | 38.6 | 19.2 | 54.3 | 2.17 | yes | yes | PASS |
| ESE240SL | LA36 16H | 5600 | 2073 | 665..995 | 38.6 | 19.2 | 54.0 | 1.99 | yes | yes | PASS |
| ESE240SL | LA34 12 | 10000 | 2201 | 680..985 | 38.6 | 19.2 | 54.8 | 1.15 | yes | yes | PASS |
| ESE240SL | G5 model | 2500 | 1972 | 651..1004 | 38.6 | 19.2 | 54.0 | - | yes | yes | PASS |
| ESE240SL250 | LA36 12H | 6800 | 2473 | 659..1030 | 47.5 | 20.1 | 40.4 | 1.93 | yes | NO | FAIL |
| ESE240SL250 | LA36 12H -30C | 3400 | 2473 | 659..1030 | 47.5 | 20.1 | 40.4 | 2.21 | yes | NO | FAIL |
| ESE240SL250 | LA36 16H | 5600 | 2473 | 659..1030 | 47.5 | 20.1 | 40.4 | 2.05 | yes | NO | FAIL |
| ESE240SL250 | LA34 12 | 10000 | 2649 | 675..1018 | 47.5 | 20.1 | 40.4 | 1.17 | yes | NO | FAIL |
| ESE240SL250 | G5 model | 2500 | 2335 | 645..1041 | 47.5 | 20.1 | 40.4 | - | yes | NO | FAIL |
| ESE240CL | LA36 12H | 6800 | 2062 | 657..992 | 39.1 | 19.4 | 54.9 | 1.86 | yes | yes | PASS |
| ESE240CL | LA36 16H | 5600 | 2062 | 657..992 | 39.1 | 19.4 | 54.9 | 1.98 | yes | yes | PASS |

Cycle times are the same for every actuator because the firmware mast rate (1.5 deg/s) is the limit, not the actuator speed.

# 3. Ballast

Operating mass is set with dry ballast only (never wet sand). Dry mass 84.5 kg (incl. 2 mm steel tray). Front cans at x 1,215 put about 69 % of their mass on the casters; the axle box (x 700-820, |y| < 175, 124-170 mm high, between the gearboxes) is the only space over the axle and holds about 15 kg of steel plate. Kingpin SF = M16 8.8 bolt yield (100.5 kN) / (bending / 0.06 m + axial) from the worst sampled kingpin load in each run; rule SF >= 2.5. **Decision (run 4): M110 - all 25.5 kg of dry steel punchings in the two front cans, axle box left empty** (re-check with the corrected placement and fixes on: section 0.5b). The sweep table below is from before run 3 and had every ballast row at x 0.70 m (see the note under it).

| variant | 12 % wet leaves mu 0.30, full 110 kg | 12 %, mu 0.27 | 12 %, mu 0.25 (slimy leaf mat) | 40 mm step, full | e-stop 12 % downhill mu 0.30 | e-stop flat | flat 10 m full | flat 10 m empty |
|---|---|---|---|---|---|---|---|---|
| 95 kg, 10.5 kg steel in front cans (G5 baseline) | FAIL 2.5 m / 25.0 s, 0.84 Wh/m, kp SF 10.18 | - | - | PASS 4.70 m, kp SF 6.06 | PASS stop 0.09 m, slide 0.001 m, kp SF 5.16 | PASS stop 0.02 m, slide 0.000 m, kp SF 6.18 | PASS 0.149 Wh/m | PASS 0.036 Wh/m |
| 100 kg, cans | PASS 5.0 m / 16.2 s, 0.32 Wh/m, kp SF 6.85 | - | - | - | - | - | - | - |
| 100 kg, 15.5 kg over axle | PASS 5.0 m / 19.6 s, 0.37 Wh/m, kp SF 5.72 | FAIL 0.8 m / 25.0 s, 2.42 Wh/m, kp SF 6.78 | FAIL 0.7 m / 25.0 s, 2.98 Wh/m, kp SF 6.98 | PASS 4.69 m, kp SF 4.32 | PASS stop 0.11 m, slide 0.001 m, kp SF 4.84 | - | - | - |
| 105 kg, cans | PASS 5.0 m / 15.6 s, 0.31 Wh/m, kp SF 4.67 | FAIL 3.1 m / 25.0 s, 0.72 Wh/m, kp SF 9.28 | FAIL 0.8 m / 25.0 s, 2.65 Wh/m, kp SF 5.42 | PASS 4.69 m, kp SF 5.52 | PASS stop 0.10 m, slide 0.001 m, kp SF 5.22 | - | - | - |
| 110 kg, 25.5 kg in cans | PASS 5.0 m / 15.5 s, 0.30 Wh/m, kp SF 6.72 | PASS 5.0 m / 16.6 s, 0.33 Wh/m, kp SF 9.01 | FAIL 2.6 m / 25.0 s, 0.83 Wh/m, kp SF 6.16 | PASS 4.70 m, kp SF 5.25 | FAIL stop 0.09 m, slide 0.058 m, kp SF 4.01 | - | - | - |
| 110 kg, 25.5 kg over axle (does NOT fit in CAD) | PASS 5.0 m / 16.4 s, 0.31 Wh/m, kp SF 5.72 | - | - | - | - | - | - | - |
| 105 kg: 15 kg axle box + 5.5 kg cans | PASS 5.0 m / 16.0 s, 0.32 Wh/m, kp SF 5.09 | FAIL 3.0 m / 25.0 s, 0.72 Wh/m, kp SF 5.0 | FAIL 0.8 m / 25.0 s, 2.63 Wh/m, kp SF 4.23 | PASS 4.70 m, kp SF 4.42 | PASS stop 0.09 m, slide 0.001 m, kp SF 4.54 | PASS stop 0.02 m, slide 0.000 m, kp SF 6.2 | PASS 0.135 Wh/m | PASS 0.036 Wh/m |
| 110 kg: 15 kg axle box + 10.5 kg cans | PASS 5.0 m / 16.0 s, 0.31 Wh/m, kp SF 4.27 | PASS 5.0 m / 16.7 s, 0.33 Wh/m, kp SF 6.58 | FAIL 2.7 m / 25.0 s, 0.82 Wh/m, kp SF 7.1 | PASS 4.70 m, kp SF 5.62 | PASS stop 0.12 m, slide 0.044 m, kp SF 4.23 | - | PASS 0.122 Wh/m | PASS 0.036 Wh/m |

**Release on 12 % from the earlier ballast sweep (as designed, before run 3; tested data at M105h / M110h, superseded by section 0.3 - the chosen ballast is M110):**

| ballast | test | bin | result | bar clear mm | last event |
|---|---|---|---|---|---|
| M105h | rel_up12 | WEB140 | FAIL | - | [[116.82, 'RELEASE FAILED: latch/pawl still closed -> hold + alert, manual lever |
| M105h | rel_up12 | ESE240SL | PASS | - | [[110.31, 'bin upright 0.3 deg']] |
| M105h | rel_dn12 | WEB140 | FAIL | - | [[105.69, 'RELEASE FAILED: latch/pawl still closed -> hold + alert, manual lever |
| M105h | rel_dn12 | ESE240SL | PASS | - | [[108.2, 'bin upright 0.3 deg']] |
| M105h | rel_up12e | WEB140 | PASS | - | [[110.72, 'bin upright -1.0 deg']] |
| M105h | rel_up12e | ESE240SL | PASS | - | [[109.43, 'bin upright -0.2 deg']] |
| M105h | rel_dn12e | WEB140 | FAIL | - | [[106.2, 'RELEASE FAILED: latch/pawl still closed -> hold + alert, manual lever' |
| M105h | rel_dn12e | ESE240SL | FAIL | - | [[105.52, 'RELEASE FAILED: latch/pawl still closed -> hold + alert, manual lever |
| M110h | rel_up12 | WEB140 | PASS | - | [[109.63, 'bin upright 0.2 deg']] |
| M110h | rel_up12 | ESE240SL | PASS | - | [[109.91, 'bin upright 0.2 deg']] |
| M110h | rel_dn12 | WEB140 | FAIL | - | [[106.11, 'RELEASE FAILED: latch/pawl still closed -> hold + alert, manual lever |
| M110h | rel_dn12 | ESE240SL | PASS | - | [[108.15, 'bin upright 0.3 deg']] |
| M110h | rel_up12e | WEB140 | PASS | - | [[110.73, 'bin upright -1.0 deg']] |
| M110h | rel_up12e | ESE240SL | PASS | - | [[110.11, 'bin upright 0.2 deg']] |
| M110h | rel_dn12e | WEB140 | FAIL | - | [[98.81, 'bin upright 0.3 deg']] |
| M110h | rel_dn12e | ESE240SL | FAIL | - | [[105.28, 'RELEASE FAILED: latch/pawl still closed -> hold + alert, manual lever |

**Run 3 note:** every ballast-sweep row in the table above was simulated with ALL ballast at x = 0.70 m ahead of the kingpin (sim_g5.build_xml default ballast_x=0.70 overrode the mass files), so M110 (cans), M110h (hybrid) and M110ax (axle) were the same model and their differences are run-to-run scatter. Corrected M110h results are in section 0. The other variants were not re-run.

# 4. Kingpin and yaw stops

Final CAD (kingpin A0, scallop |y| <= 130, YS-01 blocks placed for 42 deg nominal). Clearance in mm from the yaw sweep about the kingpin (tow pose, negative = interference volume mm3):

| yaw deg | YS-02 pin to YS-01 block | RF-03 saddle to tyre | mast rail to tyre | MA-52 lug to tyre | RF-58 to deck |
|---|---|---|---|---|---|
| 36 | 8.0 | 39.5 | 23.6 | 26.3 | 21.0 |
| 37 | 6.3 | 34.6 | 19.6 | 22.2 | 21.0 |
| 38 | 4.6 | 29.7 | 15.7 | 18.2 | 21.0 |
| 39 | 2.8 | 24.8 | 12.0 | 14.2 | 21.0 |
| 40 | 1.1 | 19.8 | 8.3 | 10.3 | 21.0 |
| 41 | -7.2 | 14.9 | 4.9 | 6.5 | 21.0 |
| 42 | -52.9 | 10.0 | 1.7 | 2.8 | 21.0 |
| 43 | -123.3 | 5.1 | -12.6 | -1.7 | 21.0 |
| 44 | -212.2 | 0.2 | -382.1 | -235.6 | 21.0 |
| 45 | -316.1 | -82.5 | -1768.9 | -1141.1 | 21.0 |

The pin meets the block between 40 and 41 deg (1.1 mm at 40). At 40 deg the nearest part is the mast rail at 8.3 mm; with 1 deg of block compliance it is 4.9 mm. Without the deeper scallop (G6 draft, |y| <= 150) the saddle was 1.5 mm from the tyre at 40 deg and touched at ~40.5 - so the +/-42 draft was not acceptable as drawn. Free yaw is now +/-40 deg each way (G5: +25 / -5 limited by the isolator; SITL G6 cap 28).

**AS5600 kingpin angle sensor (for the SITL team):** diametric magnet D6 x 2.5 in the tail of the M16 kingpin bolt, bolt head locked to RF-53 with a tab washer so it turns with the rear frame; potted AS5600 cup on a 2 mm A2 strap (KP-S1) hung from the KP-boss flange bolts, 2.0 +/- 0.5 mm gap, screened I2C cable. (G3 put the magnet in the head, where the sensor could not be on the fixed side.)

# 5. Actuator base clevis

Placeholder in the G6 draft CAD: a 40 x 6 mm flat arm cantilevered 115 mm from the RF-53 edge, with 6 mm bend-up ears. Replacement: RF-57 folded U clevis (8 mm S355, gap 32, pin D12) welded to the end of RF-58/59, a 60 x 40 x 6 box (folded channel + lid) welded to the spine side face and stitch-welded to RF-53. Operating load 2,473 N (sim peak); limit 6,800 N (LA36 rating). Source: cad/g6/clevis_calc_g6.py / .json.

| check | stress at 2,473 N MPa | stress at 6,800 N MPa | allowable MPa | SF operating | SF limit | ok |
|---|---|---|---|---|---|---|
| G6 draft placeholder arm | 1185.0 | 3258.3 | 355.0 | 0.3 | 0.11 | NO |
| pin D12 shear | 10.9 | 30.1 | 375.3 | 34.33 | 12.48 | yes |
| pin D12 bending | 72.9 | 200.4 | 650.0 | 8.92 | 3.24 | yes |
| ear bearing | 12.9 | 35.4 | 532.5 | 41.34 | 15.04 | yes |
| ear net section | 4.8 | 13.3 | 355.0 | 73.5 | 26.73 | yes |
| clevis wall bending | 11.1 | 30.5 | 355.0 | 32.05 | 11.66 | yes |
| clevis web (outer wall) | 77.3 | 212.5 | 355.0 | 4.59 | 1.67 | yes |
| RF-58 box, vertical | 39.4 | 108.4 | 355.0 | 9.01 | 3.28 | yes |
| RF-58 box, horizontal | 29.7 | 81.7 | 355.0 | 11.95 | 4.35 | yes |
| RF-58 box torsion | 3.5 | 9.6 | 205.0 | 58.9 | 21.42 | yes |
| weld RF-58 to spine a4 | 39.1 | 107.6 | 261.7 | 6.69 | 2.43 | yes |
| spine torsion (alone) | 36.2 | 99.4 | 135.7 | 3.75 | 1.36 | yes |

# 6. Final CAD, fit check and exports

Model: G5 CAD (model_g3 + g5_layer) + g6_layer.py with ACT_MODEL=LA36, CLEVIS=channel, FINAL=True, ACT_YL=215, LA36_ROT=0, SCALLOP_Y=130, STOP_DEG=42, kingpin A0. Poses: tow48, dock, grab0, tilt6/12/24/36. Clearance target 5 mm. Remaining contacts / near-contacts:

| part | part | interference mm3 | gap mm | poses |
|---|---|---|---|---|
| 24 V wheelchair motor | CH-01 Chassis tray 2 mm S235, folded, 2 pressed ri | 0 | 2.0 | dock, grab0, tilt12, tilt24, tilt36, tilt6, tow48 |
| CH-01 Chassis tray 2 mm S235, folded, 2 pres | YS-01 Yaw stop block UHMW 20x20x10 on deck (+/-42  | 0 | 4.0 | dock, grab0, tilt12, tilt24, tilt36, tilt6, tow48 |
| Bin lid | GR-04 Latch pawl 6 mm S355, cranked G6 blade (L) | 0 | 4.6 | grab0 |
| Bin lid | GR-04 Latch pawl 6 mm S355, cranked G6 blade (R) | 0 | 4.6 | grab0 |
| Bin lid | GR-03 Hook plate 10 mm S355, GH-B6 cup (58 throat) | 31 | - | tilt6 |
| Bin lid | GR-04 Latch pawl 6 mm S355, cranked G6 blade (L) | 0 | 2.0 | tilt6 |
| Bin lid | GR-04 Latch pawl 6 mm S355, cranked G6 blade (R) | 0 | 2.0 | tilt6 |
| Bin lid | GR-03 Hook plate 10 mm S355, GH-B6 cup (58 throat) | 317 | - | tilt12 |
| Bin handle bar | GR-03 Hook plate 10 mm S355, GH-B6 cup (58 throat) | 6015 | - | tilt12 |

* **Bin bar / bin lid vs hook plate at tilt 6-12 deg:** the CAD places the bin by kinematics with no contact model. The bar overlap (6,015 mm3) is identical to the G5 check, so it is a posing artefact. The lid-edge overlap (31-317 mm3) is new with the wider throat; in the physics runs (70 % closed lids, 30 % ajar, 210 samples) no lid jam or lid-caused failure occurred. Check on the first real bins.
* Motor to tray 2.0 mm and stop block to tray 4.0 mm are fixed-to-fixed gaps carried over from G5 (no relative motion).
* Pin-to-pin over the tilt range (bin tilt 0-48 deg): 0 deg 1031.7, 6 deg 991.2, 12 deg 946.9, 24 deg 849.4, 36 deg 749.5, 48 deg 665.8 mm, inside the LA36 400 window 650.0-1050.0 mm.
* Front of the tug 977.0 mm ahead of the axle (unchanged from G5; SITL world.py already carries +195 mm).

Exports (revG/cad/g6/): bin_tug_revG6_tow.step, bin_tug_revG6_docked.step, bin_tug_revG6.stl; part STEPs in step_parts_G6/: RF-53, CH-01, RF-03, SN-60, SN-61, GR-03, GR-04, LA36-envelope, RF-58, RF-57, GR-61, GR-63, KP-S1, YS-01.

**Drawings (revG/Drawings_G6.pdf, DXF in revG/mfg/dxf_G6/):** 57 made parts, 38 flat patterns. G6 sheets: GR-03 (GH-B6 profile from the same primitives as the sim, plates at +/-130, pivot boss, feeler holes), GR-04 (cranked pawl), RF-03 (scallop), RF-53 (RF-13 holes deleted), RF-57/58/59 (new clevis), CH-01 (drain slots 40 x 10, lidar tabs, lanced pod feet, S250GD+Z275), MA-56 (12H9, y 215), GR-54/GR-06 (+/-130), GR-61/GR-63 (inductive feeler), KP-S1 (AS5600), PD-12 (pod wall drilling), SN-60/61 (radomes). RF-13, SN-51 and PD-10 are deleted.

**Inputs from g6-parts, answered:**

* LD2451 radome: inner 76 x 41 x 18 (outer 80 x 45 x 22). The front radome sits at y +45..+125 (centre +85) beside the bumper switch; the G5 position left 3 mm to the switch at the new size.
* Actuator eyes: the 8 mm-eye actuator is not used. LA36 eyes are D12.2; clevises are 12H9 at both ends - no bushes needed.
* Quick-release mast pin: not accepted as the hand-crank replacement (section 2). LA36 hand crank kept.
* Inductive feeler (IND-OPEN): M8 flush inductive, PNP NO, Sn 1.5-2 mm, IP67, -25 C, reading a sprung 1.5 mm stainless flag (GR-61) on the outboard face of each hook plate; bracket GR-63. Threshold set by the flag stroke (20 mm). No exposed moving switch in the cup.
* Kingpin angle sensor: KP-S1 mount, section 4.

**Materials and finish:** sheet <= 3 mm: S250GD+Z275 pre-galvanised (EN 10346), cut edges zinc-rich primer, never hot-dipped (2 mm distorts). Plates 6-10 mm: S355J2, hot-dip galvanised to EN ISO 1461 after welding (vent holes on closed sections), zinc-rich epoxy primer + top coat as the approved alternative. Pins 42CrMo4+QT Zn-Ni. Stainless brackets 1.4301; feeler flag 1.4310.

# 7. Failures and open points (honest list)

1. **(Traced in run 3 - see section 0.3: not a sim fault; the float ratchet lifts the bin onto the stop bar.)** ESE 240 SL with 250 mm wheels does not release (tilt/release run): the bin stands up, then the release check reads the bar ~0.8 m below the hook and fails three times -> hold + alert. Same result with the G5 hook and G5 actuator model (K3 run: released=False), so it is older than G6; G5 never ran release on this bin. The jump of the bar position in 1.5 s is not physical, so a sim-model fault (float/ratchet range for the 250 mm wheel geometry) is likely, but it is not proven. **Next: trace the float joint in that run; until then treat release on 250 mm-wheel bins as unverified.**
2. **Craemer approach edge case** at ~78 mm lateral offset (both hooks): needs the firmware re-dock on approach timeout (tested on the one sample only).
3. **Yaw +/-40, not +/-42.** The mast rail is 1.7 mm from the tyre at 42 deg; more needs the rail outboard faces trimmed or the rails moved inboard (not done - it changes the mast).
4. **Ballast:** Castors carry 0 N in the tow pose with a full bin for every ballast (geometry, not mass). At M110 one release ended STUCK (ESE 240 CL 12 % down, bin standing) and the uphill-facing Weber was dropped - both outside or at the edge of the release rule.
5. The LA36 cold speed factor (x0.75 at -30 C) is an assumption; the 50 % load derating is from the data sheet.
6. One nominal run per ballast test; the climb results scatter by a few seconds between similar masses (single runs).
7. g6-parts BOM to update: LA36 instead of 0041941-1, steel tray instead of 5083, steel plate ballast instead of sand, M8 inductive sensors x2 (IND-OPEN), radome size.

# 8. Files

* Report generator: revG/make_results_g6_mech.py + results_g6_text.py; state file revG/sim/g6/PROGRESS.md.
* Sim: revG/sim/g6/ (queue_g6.py, mc_g5.py with NODOCK_RETRY, tilt_g6.py with LA36_12H / LA36_12H_cold, ballast_g6.py, mass_g6_*.json incl. M110 (chosen ballast) and the tested M105h/M110h/M110ax), results revG/sim/results_G6_*.json.
* CAD: revG/cad/g6/g6_layer.py, fit_g6_final.py, fit_g6_final.json, la36_rot_probe*.json, clevis_calc_g6.json, STEP/STL, step_parts_G6/.
* Drawings: revG/mfg/src/drawings_g6.py -> revG/Drawings_G6.pdf, revG/mfg/dxf_G6/, revG/mfg/fig_G6/, revG/mfg/tube_bar_cut_list_G6.csv.
