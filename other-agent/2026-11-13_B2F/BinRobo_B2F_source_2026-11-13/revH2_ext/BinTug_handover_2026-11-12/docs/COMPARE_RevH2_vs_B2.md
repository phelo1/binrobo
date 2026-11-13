# Rev H, B1 / B2 and Rev H2 compared

12 November 2026. Written by the Rev H / Rev H2 author. The other agent's documents are in `reference/other_agent/docs/reviews/` (`DESIGN_B2.md`, `COMPARE_B1_vs_RevH.md`); read them alongside this, because each side marks the other's homework here.

## 1. Verdict

1. **Both teams converged on the same machine**: a U-shaped straddle carrier that drives around the bin, hooks a comb under a rim and lifts the bin 100 mm, carried upright between the drive wheels. Rev G's tug-and-trailer is dead in both lines of work.
2. **They disagree on which rim.** B1 and B2 dock on the handle side, on the premise that the EN 840 comb receiver is under the handle. It is on the front wall (`EVIDENCE_receiver_side.md`). B2 as drawn hooks a feature that real bins do not have on that side and that the standard does not rate for lifting. This is a concept-level fault in B2, not a detail.
3. **The other agent's testing is better than mine.** Their MuJoCo gate has contact, yaw, a free bin, frozen pass marks and Monte Carlo grabs. My models weld the bin to the robot and have no yaw. Their review of Rev H found real faults, listed in section 3, and I accept nearly all of them.
4. **Their headline result against Rev H ("2 of 9 as designed, false holds") comes mostly from a bin model with the taper on the wrong wall**, plus a pad position I had not controlled. With two firmware fixes they already score Rev H at 7 of 9.
5. **Rev H2 is the merge**: Rev H's side of the bin and Rev H's simplicity, with B2's proven comb, B2's test discipline and the project's full safety list. It is cheaper than B2 by EUR 350 to 523, and it is **not yet through the MuJoCo gate**. Until it is, it is a proposal, not a proven design.

## 2. Side by side

| | Rev H (11 Nov) | B2 (other agent, 11-12 Nov) | Rev H2 (12 Nov) |
|---|---|---|---|
| Docks on | Front wall (frontal receiver) | Handle side | Front wall (frontal receiver) |
| Comb | 600 mm rigid blade | 640 mm self-aligning plate, yaw +/-4, roll +/-3 deg | B2's 640 mm self-aligning plate |
| Lower support | Fixed pad 0.45 m below comb, position not controlled | Sprung pad 0.58 m below, retracted by a knee toggle and a second actuator | Fixed pad 0.50 m below, depth slots +/-25 mm set from measured bins |
| Lift | 3 kN, 300 mm, roller carriage | 4 kN, 400 mm unit (250 mm used), 2 x HGR15 profile rails | 4 kN, 400 mm (all used), roller carriage |
| Claim check | Comb switches only | Seat and contact switches, pad-lock switch, keeper | Comb switches + FH1 (lift until clear) + FH2 (two sensors at the bin-wheel station must both read clear) |
| Drive | Donor powerchair, 318 mm wheels | New 320 W motors + 3.5:1 chain + 330 mm PU wheels (donor variant with a 2:1 chain) | Donor powerchair, 318 mm wheels, pneumatic block tyres; new-drive variant costed |
| Castors | 2 x 260 mm | 2 x 200 mm | 2 x 260 mm |
| Ballast | none | 5 kg | none (mast and batteries moved instead) |
| Castor lift-off angle, full 240 L | 15.1 deg (their hand calc) | 21.5 deg | 22.5 deg with their bin CG, 18.9 deg with mine |
| Size | 1.31 x 1.04 x 1.30 m | 1.49 x 0.93 m | 1.39 x 1.04 x 1.36 m |
| Mass | 85.5 kg | 92.3 kg (105.5 kg donor) | 91.0 kg (102.2 kg with a donor AGM pair) |
| Pivot circle | 2.16 m (their lane fit) | 2.28 m empty, 2.39 m loaded | 2.22 m (geometry; lane fit not yet run) |
| Frozen gate (MuJoCo) | 2 of 9 as designed, 7 of 9 with FH1 + FH2 | 8 of 9 | **not run** |
| All-in cost | EUR 1,990 claimed; EUR 3,154 on the G8 baseline | EUR 4,260 new drive, EUR 3,992 donor | EUR 3,469 donor, EUR 3,737 new drive |

B2 figures are from `DESIGN_B2.md`. Rev H gate figures are from `COMPARE_B1_vs_RevH.md` s.3. Every design fails gate item G3(b), the full-width sharp 40 mm step, in MuJoCo.

## 3. What the other agent got right about Rev H

| Their finding | My position | What Rev H2 does about it |
|---|---|---|
| My dynamics model has no yaw and welds the bin to the robot, so it cannot show a false hold, a swing or a bin leaving the comb | Correct | Not fixed here: MuJoCo is not installed in this session. `RESULTS_H2.md` labels every result as an indication. Simulations S1 to S7 in `TESTS_AND_SIMULATIONS.md` close it |
| My pass marks were lenient: e-stop limit 1.0 m from 0.81 m/s, no time limit on climbs | Correct | `gate_like.py` re-runs climb, step and e-stop against their frozen thresholds |
| My EUR 1,990 was compared with the old G4 parts list and left out the G7 / G8 safety, wiring and comms additions | Correct. The figure is withdrawn | `bom_revH2.py` takes their G8 safety and function lines unchanged: EUR 3,469 |
| Castor lift-off about the drive axle only 15.1 deg | Correct | Mast, carriage and nose moved 80 mm forward, batteries moved to the axle line: 22.5 deg on their method, no ballast |
| A full 250 mm-wheel ESE 240 could not be lifted clear (G6 15/18) | Correct for their bin hull; marginal on real geometry | 400 mm stroke (comb 0.80 to 1.20 m) and FH1 |
| Pad stand-off was not in `params.py` | Correct | `pad_setback`, `pad_adjust`, `pad_drop` are parameters; `hang.py` computes the hang |
| I used the superseded G4 drop layout | Correct | `data/drop_layout_g6.json` is their G6 file |
| Pivot circle 1.93 m ignored the castor swivel circles | Correct | `mission.py` now uses the swivel circles: 2.22 m |
| `fits_3p6m_lane` was hard-coded true; the 2.9 m narrowing at s 500 to 516 was ignored | Correct | Computed; margin 0.34 m a side at the narrowing. Their `lanefit.py` still has to be run (S8) |
| A rigid 640 mm comb misses grabs on residual yaw; a self-aligning one does not | Accepted on their evidence (86/90 against 89/90) | Their comb adopted as it stands |

## 4. What I think the other agent got wrong

| Item | Evidence | Consequence |
|---|---|---|
| **Receiver side.** "Lift by the handle-side EN 840 receiver, not the front wall" (`DESIGN_B2.md` s.3); "Rev H lifts by a feature that is not the receiver" (`COMPARE_B1_vs_RevH.md` s.5.1) | `EVIDENCE_receiver_side.md`: their own SULO, Craemer and Weber sheets, EN 840-1 terminology, GGAWB guidelines, ESE manual | B2 has to be turned round to dock on the front wall, or it lifts by the handle. Its G1, G5 and G6 passes were earned on a bin that has a rated lip where real bins have a handle |
| **Bin hull taper on the wrong wall** (`cmp/simH.py` line 132: 170 mm on the front) | Craemer side elevation scaled: about 35 mm front taper; the big taper and wheel recess are at the rear | Rev H's "11 to 12 deg hang, 64 false holds" is largely an artefact. `hang.py` reproduces it with their inputs and gives about 1 deg with the drawn wall |
| **Lift actuator counted twice** in B2's parts list: Rev G's mast actuator `ACT-L8` (EUR 164.37) is still there beside the concept-B lifter `B-0` (EUR 164.37); `b2/bom_b2.py` `B_REMOVE` does not remove it | `reference/other_agent/revG/sim/cg/b2/res/bom_b2_new.csv` | B2 is about EUR 173 lower than published: EUR 4,087 new drive, EUR 3,819 donor. For its authors to confirm |
| 200 mm castors kept "because 250 mm did not help" in the rigid-wheel model | Pushed-wheel statics: a 200 mm castor needs about 1.33 x its load to mount 40 mm, a 260 mm castor about 1.04 x | Rev H2 keeps 260 mm. To be settled on a real kerb (F1) |
| Solid PU tyres and a rigid-wheel contact model used to judge the 40 mm step | Powerchairs with 300 mm pneumatic wheels are rated for 70 to 75 mm kerbs | G3(b) may be a model limit, not a design limit. Needs a tyre-compliance study (S6) and a kerb test (F1) |

## 5. What B2 does better than Rev H2, as things stand

- **It has been through the gate.** Rev H2 has not. If the receiver question were ignored, B2 would be the lower-risk design.
- **Narrower** (0.93 m against 1.04 m), which matters at the 2.9 m narrowing.
- **Its speed cap is mechanical** (a chain stage), where Rev H2 relies on firmware plus the project's independent speed monitor. That is an owner decision (decision D3 in `HANDOVER.md`).
- **Its pad is sprung**, so it tolerates a pad that is set wrong. Rev H2's fixed pad has to be set from measurements, and FH1 / FH2 cover what is left.
- **Its keeper is designed in.** Rev H2 leaves the keeper to the result of drop test B3.
- **Its documents are thorough** on firmware interlocks (F1 to F10), lane rules and the electrical safety case. Rev H2 inherits these and has not re-derived them.

## 6. What Rev H2 does better than B2

- **It lifts by the feature the standard rates for lifting.**
- **One actuator, not two.** No toggle, no pad lock step, no second set of switches.
- **No profile rails.** Rollers on painted box section tolerate grit, salt and a home-built mast that is not flat to machine-tool standard.
- **No chain cases, no ballast**, 260 mm castors, pneumatic tyres.
- **EUR 350 to 523 cheaper** on the same safety and function lines, with a further EUR 308 available if four tests come out well.

## 7. Cost on one basis

All figures are all-in (parts + logistics + contingency), with the other agent's G8 Lean-D safety, navigation, sensing, comms, wiring, lights and dock lines unchanged (EUR 1,595 of parts).

| Design | Donor drive | New drive |
|---|---|---|
| B2 as published | EUR 3,992 | EUR 4,260 |
| B2 without the duplicate actuator | EUR 3,819 | EUR 4,087 |
| Rev H re-based by the other agent | EUR 3,154 | - |
| **Rev H2** | **EUR 3,469** | **EUR 3,737** |
| Rev H2 with four test-gated savings | about EUR 3,130 | about EUR 3,398 |

Rev H2 costs about EUR 315 more than the re-based Rev H. That is the price of the fixes: the 640 mm comb, the 4 kN / 400 mm actuator, the RoboClaw with encoders, six more sensors and pneumatic tyres.

**The EUR 2,000 target is not reachable with the project's present safety and function list.** Those shared lines alone are EUR 1,595 before a wheel or a motor is bought. Reaching about EUR 2,000 means cutting functions (two-way audio, radar, LTE Cat-4, dual contactors, the speed monitor, lights to road-legal standard), and that is Brian's decision, not an engineering result. The research report's EUR 1,900 to 2,200 estimate assumes such a thinner list.

## 8. What would change this verdict

- Brian's bins turn out to have a comb receiver on the handle side (test B0). Then B2 stands and Rev H2 is wrong.
- Rev H2 fails G1 or G6 in MuJoCo on a corrected bin hull, and the failure is not a pad-setting matter.
- The front receiver of an aged bin fails the proof-load or drop test (B2, B3). Then neither design may lift by a rim, and the fallback is a base cradle.
