---
title: "BinRobo concept gate on a corrected bin: Rev H2 vs B2 / B2-F (MuJoCo campaign H2)"
date: "12 November 2026"
geometry: margin=1.8cm
fontsize: 10pt
---

# 0. Result in one page

**Recommendation: take B2-F forward (B2 turned round so that it docks on the bin's front wall), with three fixes that its own results call for, and keep Rev H2's front-dock details. Confirm the receiver side on Brian's own bins (test B0) before any steel is cut.**

- **The comb receiver is on the bin's FRONT wall** (section 1). B2 as designed docks on the handle side. On the corrected bin hull it captures **0 of 90** bins (S11), and 0 of 15 with its pad re-set (S11r). B2 as designed is out.
- **Rev H2 and B2-F both score 8/9** against the frozen criteria. Both fail only G3(b), the full-width sharp 40 mm step, as every design before them did. Kerb ramps stay a lane-prep item.
- **B2-F has the larger margins where the gate is tight.** These are brake-hold creep on 12 % (0.031-0.036 m against Rev H2's 0.045-0.049 m, with a 0.05 m limit), the perturbations (24/24 against 23/24), lane fit (12/12 against 9/12) and motor current on the 12 % grade (12.3 A against 24-25.4 A of 30 A). Rev H2 crosses the creep limit at +10 % mass (0.058 m) and with the bin CG 60 mm higher (0.057 m).
- **Rev H2 is better on bin retention over a 40 mm drop** (8/8 against B2-F 3/6). It is also EUR 251 cheaper and keeps a wider truth-hedge gap at pad A in SITL (0.050 m against 0.003 m). B2-F loses wheel clearance on the 240 L drop because its lift actuator is modelled at a 3,000 N cap. Its BOM unit is rated 4 kN, so this is a re-run item, not yet a pass.
- **S12 structure:** both frames miss SF 2 in the side rails at the simulated carry loads (Rev H2 1.30, B2-F 1.19). They also miss it in the mast uprights at the peak comb force (Rev H2 1.26, B2-F 0.68). Rev H2's roller carriage on painted S235 tube does not work as drawn: the line contact on the tube face is at first yield already under the static load. The fixes are sections and parts, not concepts (section 9).

| Item | Rev H2 | B2 as designed (S11) | B2-F |
|---|---|---|---|
| Frozen gate G1-G9 | 8/9 (G3b fail) | G1, G5, G6 FAIL; the rest not reachable | 8/9 (G3b fail) |
| G1 grab, pooled | 89/90 | 0/90 | 90/90 |
| G2 hold creep (limit < 0.05 m) | 0.045-0.049 m | not reached | 0.031-0.032 m |
| Perturbation lines | 23/24 (climb at mass +10 %: creep 0.058 m) | - | 24/24 |
| S5 retention over a 40 mm drop | 8/8 | - | 3/6 (ESE 240 SL 0/3) |
| S12 lowest SF (carry loads) | 0.55 (roller contact), 1.30 (rails) | - | 1.19 (rails) |
| Lane fit / SITL | 9/12 / 10/10 | - | 12/12 / 10/10 |
| Cost, donor / new drive | EUR 3,568 / 3,836 | EUR 3,819 / 4,087 (duplicate actuator removed) | same as B2 |

# 1. Receiver side (R1): front wall, confirmed

The question is which wall of a two-wheel bin carries the EN 840 comb receiver. B1 and B2 assume it sits under the handle. Rev H and Rev H2 assume it is on the front wall, opposite the handle, the lid hinge and the wheels. I re-read the primary drawings myself, using the scales in brackets:

- **Craemer MGBneo 240 side elevation** (1.25 mm/px; 200 mm wheel = 160 px). The EN 840-1 comb band "min. 860 - max. 1030" is dimensioned on the front wall. Hinge, handle and wheels are at the rear.
- **SULO Citybac 240 data sheet**, pages 2 and 3 (3.06 mm/px). Callout C, "DIN comb lifting system", points at the sticker-panel face. Callout B, the handle bar, is a separate feature at the other end. "Upper comb edge ~998" is dimensioned at the front.
- **Weber 140 side elevation** (1.11 mm/px). Comb height 1001 mm is dimensioned at the front.
- **ESE operating manual** (July 2022, p. 8). It speaks of the "upper frontal comb receiver". The lifter's retention stop may touch only the rear surface of the bin, ideally the wheels, and never the rear handle.

**Finding: the comb receiver is on the FRONT wall on all three makers' drawings.** The handle side has a plain rim and a handle bar on brackets. EN 840-5 qualifies the frontal receiver by lift-tilt testing. The handle of a two-wheel bin is tested only for pulling the tilted bin. The full source list is in revH2_ext/.../docs/EVIDENCE_receiver_side.md. This is desk evidence. Brian's own bins still need to be checked (test B0, five minutes).

# 2. Hull correction (S1) and check plots

The gate's bin hull (cmp/simH.py l.132) gave the front wall a 170 mm taper and had no rear wheel recess. The new hull (h2/hull_h2.py, two convex meshes) uses the drawn values:

- front taper 35 mm (240 L) and 40 mm (140 L), scaled as Craemer 34, SULO 37 and Weber 42 mm;
- rear draft 30 mm (240 L) and 38 mm (140 L), plus the wheel recess;
- the receiver on the front wall at data-sheet comb height and EN 840 width (580 mm for 240 L, 480 mm for 140 L);
- a handle bar on brackets and a plain 20 x 8 mm rim on the handle side.

H2_HULL=old keeps the gate block for identity checks. At the Rev H2 pad height the front wall now sits 17.6-20.9 mm behind the receiver line (old hull 62-91 mm), from h2/res/hull_check.json. S0 reproduced the stored B2 and Rev H results key for key on the old hull, and the new generators reproduce B2 on the old hull (TESTLOG S0a-S0e). S2 mass check, Rev H2: 91.00 kg, CG x 0.3022 m, z 0.4092 m, against 91.0 / 0.3022 / 0.4091 in params: PASS.

![New hull (blue) and gate hull (red, dashed) drawn over the makers' side elevations; receiver green, plain rim olive, handle bar black, Rev H2 pad height orange (h2/fig/hull_all.png)](../../revG/sim/cg/h2/fig/hull_all.png){width=100%}

![ESE 240 SL hull on the SULO Citybac drawing (h2/fig/hull_ESE240SL_on_SULO.png)](../../revG/sim/cg/h2/fig/hull_ESE240SL_on_SULO.png){width=48%}

# 3. Scorecards against the frozen criteria (G1-G9)

The criteria are in revG/sim/cg/CRITERIA_FROZEN.md. Its sha256 was checked at the start, at the resume and at the end, and matched every time:

```
2cf3f4ecdd104c6b50e0eb3e4b70616ebc287a80d2789030e6eb2249345b8a74
```

No threshold was changed. All runs use the new hull. Results are in h2/res/gate_H2_.json and gate_B2F_.json, and every run has a row in TESTLOG_H2.md.

| Gate | Rev H2 | B2 as designed (S11) | S11r (B2, pad re-set) | B2-F |
|---|---|---|---|---|
| G1 grab MC 3 x 30 | **PASS** 89/90 (WEB140 30, ESE240SL 29: run 3 no dock, ESE240CL 30), FH 0, knocked 0 | **FAIL 0/90**: WEB140 30 safe miss (15 no load pick-up, 15 bin tilting); ESE240SL 30 no dock (retracted pad meets the real rear wall); ESE240CL 21 no dock + 9 safe miss; FH 0, knocked 0 | FAIL 0/15 (5 per bin, all safe miss; comb meets the handle brackets), FH 0 | **PASS** 90/90, FH 0, knocked 0 |
| G1 extra bins | SL 250 30/30, ESE140CL 30/30 | - | - | SL 250 30/30, ESE140CL 30/30 |
| G2 climb 12 %, 6 runs | **PASS** 6/6, 11.0-11.2 s, creep 0.045-0.049 m (marginal) | not reached (no grab) | not run | **PASS** 6/6, 11.0-11.1 s, creep 0.031-0.032 m |
| G3 40 mm step | **FAIL**: one side PASS 4.69 m; full width FAIL, stalls at 1.34 m (1:4 ramp PASS 4.71 m) | not reached | not run | **FAIL**: one side PASS 4.68 m (lift at the 3,000 N model cap); full width FAIL 1.34 m (ramp PASS) |
| G4 e-stop 12 % down | **PASS** stop 0.343 / 0.111 m | not reached | not run | **PASS** 0.161 / 0.082 m |
| G5 carry + pivot | **PASS** swept 2.30 m, roll 0.004 deg | **FAIL** (no dock) | not run | **PASS** swept 2.39 m |
| G6 set-down 18 cases | **PASS** 18/18 | **FAIL** 0/18 (no dock) | not run | **PASS** 18/18 |
| G7 dt repeat | **PASS** 3/3 | not reached | not run | **PASS** 3/3 |
| G8 statics + hand calc | **PASS** 8/8, drive >= 458 N, castors >= 310 N; min tip 39.9 deg, castor lift-off 23.9 deg | not reached | not run | **PASS** 8/8, castors >= 294 N; min tip 36.5 deg, lift-off 23.0 deg |
| G9 mass <= 120 kg | **PASS** 91.0 kg | 92.3 kg (DESIGN_B2, not re-run) | - | **PASS** 92.3 kg |
| **Total** | **8/9** | **G1, G5, G6 FAIL; rest not reachable** | - | **8/9** |

**Perturbations** were trimmed to 6 lines each, declared before running (mass x1.1, mass x0.9, all friction x0.85, bin-wheel crr 0.09). Each set holds G1 ESE240SL 5 grabs, climb mu 0.22 / crr 0.09, step one side, e-stop forward, set-down ESE240CL up12 full and SL250 dn12 full.

| Perturbation | Rev H2 | B2-F |
|---|---|---|
| mass x1.1 | 5/6: **climb FAIL, creep 0.058 m**; grab 5/5, step, e-stop 0.227 m, 2 set-downs PASS | 6/6 (creep 0.031, e-stop 0.161 m) |
| mass x0.9 | 6/6 (creep 0.050 m, rounded; ok) | 6/6 |
| friction x0.85 | 6/6 (climb 13.4 s, creep 0.046; e-stop 0.425 m) | 6/6 (11.8 s, 0.033; e-stop 0.223 m) |
| bin crr 0.09 | 6/6 | 6/6 |
| **Total** | **23/24** | **24/24** |

# 4. S4 pad tolerance map (Rev H2)

S4 was trimmed to gaps of -10 / 0 / +20 / +40 / +60 mm between the pad face and the comb seat line, on WEB140, ESE240SL and ESE240CL. Each gap got 5 G1 seeds plus a G6 flat-full set-down. The design value is +25 mm.

| Gap (mm) | WEB140 | ESE240SL | ESE240CL | G6 flat full (3 bins) |
|---|---|---|---|---|
| -10 (pad proud) | 0/5 no dock | 0/5 no dock | 0/5 no dock | 0/3 (no dock) |
| 0 | 5/5 | 5/5 | 4/5 (1 no dock) | 3/3 |
| +20 / +40 / +60 | 15/15 | 15/15 | 15/15 | 9/9 |

The working window is 0 to at least +60 mm, with a cliff just below 0. Set the slot's hard stop at 0 mm, so the pad can never stand proud of the comb.

# 5. S5 bin retention: setup defect, crossing diagnostics, results

**Setup defect (found and fixed during the campaign).** In the first step setup (v1), the 40 mm drop edge sat 0.2 m ahead of the tug's start pose. The castors start 0.82 m (Rev H2) or 0.95 m (B2-F) ahead of the drive axle, so they began the grab hanging over the drop. Rev H2 docked anyway, so its v1 results were valid carries from off-nominal grabs. B2-F did not dock, so its 3 v1 step results were invalid. Setup v2 puts the edge 0.10 m beyond the castor front and carries 3.6 m. All step lines (Rev H2 8, B2-F 4) were re-run with v2. The old runner is kept as h2/runX.py.pre_s5v2.

**Crossing diagnostics (added and declared before running).** The S5 `ok` flag does not require the carry to finish. Many trench and pothole runs stopped short because the tug stalled at the feature, the same mechanism as G3(b). Those runs never put the bin wheels over the feature. Every S5 result now records the distance covered and whether the bin wheels passed the far edge. **Retention counts as shown only where the bin wheels crossed.**

| Feature (0.5 / 0.8 m/s, +/- keeper) | Rev H2: tug distance, bin wheels crossed, retained | B2-F |
|---|---|---|
| 40 mm drop (step, v2), 8 runs / 6 runs | full 3.6 m carry in all; crossed 8/8 (1.5-2.0 m past); **retained 8/8**; lip peak 3.3-6.4 kN (3.9-6.9 x bin weight) | crossed 6/6; **WEB140 3/3 retained, ESE240SL 0/3** (bin still on the comb, wheels sag to 12-15 mm < 30 mm, lift at the 3,000 N model cap) |
| 40 mm x 0.20 m trench, 8 / 6 | stalls at 1.50 m; **no crossing** (bin wheels 0.18 m short to 0.01 m past the far edge); held | stalls at 1.51 m; no crossing; ESE240SL loses clearance, **bin on the ground (2,955 N)**; WEB140 held |
| 60 mm pothole under one wheel, 8 / 6 | stalls at 2.0-2.4 m; **no crossing**; held | **crosses 6/6** (0.09-1.33 m past); retained 6/6 |

**Read-out.** Rev H2 retains the bin wherever the bin wheels actually crossed (the step, 8/8). It cannot drive over the trench or the pothole. B2-F crosses the pothole but loses the 30 mm wheel clearance on the full 240 L bin at the drop. Its lift actuator in the model is capped at 3,000 N and the peak lip load reaches 4.1-7.3 kN. The B2 BOM unit is the QC FDI 4 kN, so **re-running these three lines with a 4 kN cap is the first open simulation item**. Neither design crosses the trench, so ramps or a lane survey are needed wherever a channel like that exists.

# 6. S6 kerb (full-width 40 mm step) and the compliant-tyre model change

| Case | Rev H2 (15 cases) | B2-F (6) |
|---|---|---|
| Rigid gate tyre, nose-first 0.5 m/s, 60 and 80 N m | FAIL (stall 1.34 m) | FAIL (1.34 m) |
| Rigid, other castor size (H2 200 mm, B2-F 260 mm) | FAIL | FAIL |
| Rigid, 0.8 m/s (60 / 80 N m); tail-first (60 / 80 N m) | FAIL x4 | not run |
| 1:4 ramp, rigid | PASS 4.71 m | PASS 4.71 m |
| **Compliant tyre "t15" (8 mm deflection at 740 N)**: nose 0.5 (60, 80 N m, both castor sizes), tail-first, 0.8 m/s | **PASS 6/6** (4.68-5.0 m, pitch <= 9.9 deg) | PASS nose 0.5 (4.70 m); **FAIL** with 80 N m + 260 mm castor (bin wheels touched, 657 N) |
| Stiffer tyre "t20" (5.7 mm at 740 N) | FAIL (1.35 m) | not run |

**The compliant-tyre passes are a model change, not a design pass.** The gate model's rigid tyre deflects 0.07 mm. The t15 tyre deflects about 8 mm (Rev H2) or 10 mm (B2-F) under the static wheel load (the tyrecal files in h2/res). It stands for a soft pneumatic or foam-filled 330 mm tyre. The step result then depends on a tyre property that nobody has measured. G3(b) stays FAIL for both designs. The kerb result becomes a tyre test on the real wheel (donor chair, test B5/B6).

# 7. S7 nose-light: bin CG +60 mm, 12 % climb nose-up

Two metrics are reported:

- **literal**: frozen style, the instantaneous castor contact force minimum must exceed 50 N;
- **filtered**: a 0.10 s moving-average minimum must exceed 50 N, added and declared before running.

The literal minimum was 0.0 N in every Rev H2 run, including the nominal-CG run. Over the same climb the castors carry 390 N on average, and 350 N in the static test. So the literal metric catches rigid-contact chatter, not lift-off.

| Run (mu, CG) | Rev H2 literal / filtered (MA min, p05, mean N) / creep m | B2-F literal / filtered / creep |
|---|---|---|
| mu 0.22, nominal CG | FAIL / PASS (179, 296, 403) / 0.049 | FAIL / PASS (111, 271, 318) / 0.031 |
| mu 0.22, +60 mm | FAIL / PASS (232, 283, 392) / **0.057** | FAIL / PASS (145, 246, 307) / 0.035 |
| mu 0.25, +60 mm | FAIL / PASS (236, 282, 393) / **0.051** | FAIL / PASS (160, 241, 309) / 0.036 |
| mu 0.30, +60 mm | FAIL / PASS (236, 308, 396) / 0.041 | **PASS** / PASS (170, 244, 309) / 0.034 |
| Statics 110 kg, +60 mm, 4 poses | 4/4, castors >= 350 N | 4/4, castors >= 283 N |
| Hand calc, +60 mm (min tip / castor lift-off) | 38.1 / 22.5 deg | 34.8 / 21.6 deg |

Neither design goes nose-light. On the filtered metric the castors keep at least 111 N, and the castor lift-off angle stays above the 20 deg target. The side finding is Rev H2's **hold creep: 0.057 and 0.051 m with the high CG**, which would fail G2's 0.05 m limit. Rev H2's brake hold has no margin on 12 %.

# 8. S10 contact sensitivity (lip contact solref / friction)

The trimmed set was declared before running. Each variant ran 5 ESE240SL grabs, a v2 drop at 0.8 m/s and a pothole at 0.8 m/s.

| Variant | Rev H2: grab / drop / pothole | B2-F: grab / drop / pothole |
|---|---|---|
| nominal | 30/30 / retained / no crossing | 30/30 / **lost clearance** / crossed, retained |
| lip solref 0.004 (stiffer) | 5/5 / retained (lip 4.95 kN) / no crossing | 5/5 / **retained** (lip 9.63 kN = 8.9 x W) / crossed, retained |
| lip solref 0.016 (softer) | 5/5 / retained (4.84 kN) / no crossing | not run (trim) |
| lip mu 0.25 | 5/5 / retained (5.72 kN) / no crossing | 5/5 / lost clearance (5.66 kN) / crossed, retained |
| lip mu 0.45 | 5/5 / retained (5.51 kN) / no crossing | not run (trim) |

Rev H2's results do not depend on the lip contact model. B2-F's drop result flips with the contact stiffness, and the peak lip force nearly doubles. Both point back to the lift actuator cap and to a comb buffer (section 9).

# 9. S12 structure hand calcs on the simulated peak forces

The script is h2/s12_struct.py, with output in h2/res/s12_structure.json and h2/rep/s12_table.md. It uses three load levels from h2/res:

- **static**: the G8 statics;
- **carry**: the maximum over smooth-ground runs (G2, G4, G5, G6, S7 and the perturbations);
- **edge**: the maximum over the pothole and compliant-tyre kerb runs.

The comb load for the peak case is the largest nib/lip force in any run. Two kinds of wheel force were left out. Rigid-tyre impulses at sharp steps (14.7-22.1 kN) and wheel forces in the stalled trench runs (0.25-1.06 MN) are single-sample rigid-contact artefacts.

| Load (per wheel / at comb) | Rev H2 | B2-F |
|---|---|---|
| Wheel static / carry / edge (N) | 859 / 2,847 / 7,380 | 931 / 2,385 / 7,306 |
| Comb static / carry / peak (N) | 1,079 / 2,055 / 7,316 (WEB140 trench, keeper) | 1,079 / 1,873 / 9,634 (S10 stiff lip; nominal contact 7,287) |
| Pad peak / lift peak (N) | 3,705 / 4,000 (actuator cap) | 1,772 / 3,000 (model cap) |

**Model.** The rail is a beam from the drive axle to the castor, loaded at the mast foot: M = F_wheel x x_mast (x_mast 0.53 / 0.49 m), the same model as revH2 statics.py, used for both designs. The mast moment is M = F_comb x e, with e = 0.345 m (bin CG behind the front wall) + 0.08 m (seat to guide axis) for both front-dock designs. It is shared by two uprights. Geometry that neither design specifies is marked ASSUMED: foot bolt pattern, pivot pin, HGR15 block pitch and drop plate size. Yield values: S235 235 MPa, S355 355 MPa, bolt 8.8 640 MPa. The rolling-bearing check uses C0, from SKF 6202-2RSH C0 3.75 kN (skf.com) and HIWIN HGH15CA C0 23.47 kN (hiwin.de). Line contact on S235 is checked at first yield, p0 = 1.67 x 235 = 392 MPa.

| Element | Rev H2 SF (static / carry / peak) | B2-F SF (static / carry / peak) | Fix where SF < 2 |
|---|---|---|---|
| Side rail (H2 50x50x3, B2-F 50x50x2 S235) | 4.31 / **1.30** / **0.50** (edge) | 3.04 / **1.19** / **0.39** (edge) | carry: H2 60x60x4, B2-F 50x50x4; edge: 80x80x5 S235 (or 100x50x4 S355) |
| Mast upright at the foot | 8.54 / 4.48 / **1.26** | 6.05 / 3.49 / **0.68** | H2 60x60x4; B2-F 80x40x4 (front dock doubles B2's own lever) |
| Mast-foot bolts M10 8.8 (ASSUMED 2 per row) | 32 / 17 / 4.8 | 19 / 11 / 2.2 | - |
| Bolt pull-through of the RHS wall | 22 / 12 / 3.3 (3 mm) | 8.9 / 5.1 / **1.00** (2 mm) | through-plates or crush tubes at the B2-F foot |
| Comb plate, load symmetric / at the roll stop | carry 10.5 / 4.4; peak 2.96 / **1.22** (6 x 75, 20 mm teeth ASSUMED) | carry 65 / 27; peak 12.5 / 5.2 (6 x 130) | H2: 8 mm plate or net depth >= 70 mm |
| Comb pivot pin, 20 mm cantilever (ASSUMED) | D16 **1.76**, D20 3.44 at peak | D16 **1.34**, D20 2.61 | D20 8.8 pin (or double shear) on both |
| Lift guide, rating | 6202 rollers C0: 4.9 / 2.6 / **0.72** | HGH15CA C0: 20 / 12 / 2.3 | H2: two rollers per station or C0 >= 10.4 kN, rows 0.45 m apart |
| Lift guide, track | roller line contact on the S235 tube face: **1.06 / 0.55 / 0.16** | HGR15 rail screws M4 (2 per block): 9.8 / 5.6 / **1.10** | H2: hardened track strip on each upright face; B2-F: M4 12.9 into a 10 mm backing flat, not the 2 mm wall |
| Castor outriggers (vertical 3 g; kerb strike at the 80 N m cap) | plate 19.8 / 3.5; nose member torsion 11.2 | nose member 11.5 / 10.5; drop plate 3.7 | - |
| (Bin side) receiver ledge, gate-model HDPE section | carry 2.6, peak **0.73** | carry 2.9, peak **0.56** | comb rubber buffer (in the H2 BOM); measure real receivers (B0b/B1) |

**Read-out.**

- Both 50x50 frames are under-sized in the rails for the loads the simulation actually produces. Up-sizing costs a few kg and a few tens of euros.
- B2-F's 2 mm walls are its weak point once the bin hangs from the front wall. The mast lever doubles against B2's handle-side figure.
- Rev H2's rollers on a painted tube need a hardened track and more roller capacity. This was the main reason it chose rollers over profile rails, and it does not survive the check.
- The edge-load rail case (SF 0.4-0.5) rests on 0.5 ms peak samples. The frame will not see the full value, but it shows the rails are the place to add steel.

# 10. Sibling results (LANE_SITL_COST_H2.md)

- **S8 lane fit.** Rev H2 9/12: it fails the handle-to-lane drops at pad A by 0.010 m under both rule sets, and moving the pads 0.25 m up-lane does not help. B2-F 12/12. With the G6 layout (handles to the road) both are 6/6.
- **S9 carrier SITL** (Python kinematic model, not ArduPilot): 20/20 strict, 10 scenarios per design. The tightest truth-hedge gap at pad A is 0.050 m for Rev H2 and 0.003 m for B2-F. Neither keeps the 0.124 m p95 localisation error clear at pad A, so trim the hedge or set the pad 0.1-0.2 m off it.
- **S13 motor current**, 12 % grade, 110 kg bin: Rev H2 24.0 A (donor 25.4 A) of the 30 A controller channel; B2-F 12.3 A.
- **S14 cost** (all-in): Rev H2 EUR 3,568 donor / 3,836 new; B2 (= B2-F hardware), with the duplicate actuator removed, EUR 3,819 / 4,087. Rev H2 is EUR 251 cheaper on both bases.

# 11. Incidents and trims (as logged in PROGRESS_H2.md)

- **Concurrency incidents (two).** Three chunk calls were issued in one turn and ran together, at 15:05 and again at 16:05. The runs are deterministic: identical json was kept and .done was de-duplicated. One auto-SKIP was reverted and re-run with rc=0. No stored result comes from a killed line; 40 timeout cuts were audited and all lines later completed rc=0. The one-call-per-turn rule was re-applied.
- **Sandbox restart (17:45 log).** The interrupted line was re-run.
- **This finishing session.** The B2-F lmu25 grab was cut once at 102 s with no run finished, then completed 5/5 in 63 s. The queue is complete at 331/331. No process was killed.
- **Trims, declared before running.** S5 B2-F keeper at 0.8 m/s only. Perturbations at 6 lines each. S11r 5 grabs per bin (no G5/G6). S6 B2-F 7 cases. S7 statics at 110 kg only. S4 5 gaps x 3 bins, Rev H2 only. S10 as in section 8, solimp dropped. S11 ran G1, G5 and G6 only.
- **Additions, declared before running.** S11r. S5 crossing diagnostics (16 lines). The S7 filtered castor metric. The S5 step setup v2. All are logged with the reason.
- **Clock note.** The journal entries 15:45-18:55 were written ahead of the +03 wall clock by the previous worker. Their order is right.

# 12. Verdict

**Take B2-F forward, built to Rev H2's front-dock rules, if test B0 confirms the front-wall receiver on Brian's bins.**

Why B2-F:

- It has the margin on the things the gate measures and that are hard to fix later: traction and brake hold on 12 %, perturbation robustness, grab reliability, lane fit and motor current.
- Rev H2 sits on the creep limit in the nominal runs and crosses it with +10 % mass or a higher bin CG. It draws 80-85 % of the controller's current on the grade, and it cannot do handle-to-lane drops at pad A. These are drive-train and footprint limits.
- B2-F's misses are hardware items its BOM already allows for, or cheap sections:
  - the 4 kN actuator (modelled at 3 kN);
  - 50x50x4 rails and an 80x40x4 mast at the foot;
  - through-plates at the feet;
  - a backing flat for the profile-rail screws;
  - a D20 comb pivot pin.

What it costs: about EUR 250 more than Rev H2, plus the frame upgrades. Rev H2 is worse at the drop and the SITL hedge gap at pad A is tighter (0.003 m).

Carry over from Rev H2:

- the pad set-back procedure, with a hard stop at 0 mm gap (S4);
- FH1/FH2 claim logic with bin-wheel clearance sensors;
- the comb rubber buffer;
- protection at pad A, by trimming the hedge or setting the pad 0.1-0.2 m off it.

Neither design passes G3(b), so kerb ramps stay in the lane plan. The kerb answer with the real tyre is a physical test.

**Open items before the build.**

- Physical:
  1. **B0**: Brian checks which wall of each of his three bins carries the comb receiver (five minutes, no cost). Everything above assumes the front wall.
  2. **Pad-A clearance**: measure the hedge face and pad A on the lane and set the pad or trim the hedge until the SITL gap is at least the 0.124 m p95.
  3. **Donor motor measurement**: no-load speed, stall current and torque at 24 V on the donor gearmotors, with the pull test (>= 450 N drawbar for 3 min). This decides the drive-current and creep margins.
- Simulation: re-run B2-F S5 (ESE240SL drop 0.5 / 0.8, trench) with the 4 kN actuator cap, and re-run the S12 rail and mast checks once sections and bolt patterns are drawn.

*Files: register docs/reviews/TESTLOG_H2.md; journal docs/reviews/PROGRESS_H2.md; results revG/sim/cg/h2/res/; S12 script h2/s12_struct.py.*
