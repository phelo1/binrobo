# Bin Tug Rev H2: design description

12 November 2026. Concept stage. Nothing has been built. Every dimension comes from `revH2/sim/params.py`, which is the single source of geometry and mass; change it there and re-run the scripts, do not edit numbers in documents.

Drawings are in `drawings/`:

| File | Shows |
|---|---|
| `ga_revH2.png` | General arrangement: side, plan and front views with the main dimensions |
| `iso_1_robot.png` | The robot from four sides, parts named |
| `iso_2_pickup.png` | Pick-up in three steps, and a cut-away of how the bin hangs |
| `iso_3_carry.png` | Carrying a full 240 L bin, four views |
| `revH_concept.png` | Side view with the load path and wheel loads |
| `bin_interface.png` | The comb, the frontal receiver and the rest pad; and what the other agent's model assumed |
| `turning_space.png` | Turning room against Rev G |

There are no manufacturing drawings, DXFs or CAD files for Rev H2. `revH2/results/cut_list_revH2.csv` and `plate_list_revH2.csv` are costing lists.

## 1. What it is

A U-shaped steel frame on two powerchair drive wheels and two swivel castors. It reverses around a standing wheelie bin from the bin's front, so the bin ends up between the two side rails with its front wall against a lift carriage. A comb on the carriage rises under the bin's frontal comb receiver (the stepped rim that refuse trucks lift by), and lifts the bin about 100 mm. The bin hangs upright, leaning lightly on a rubber pad half a metre below the comb. The robot then drives nose-first down the lane with the bin's weight between its drive wheels, sets the bin down at the road, and backs away. Collection is the same in reverse.

## 2. Specification

| Item | Value |
|---|---|
| Overall | 1.39 m long, 1.04 m wide over the drive wheels, 1.36 m to the top of the mast |
| Frame | 50 x 50 x 3 S235 box section, bolted through about 16 flat laser-cut plates. Two side rails with flared tips, nose cross-member, mast-base cross-member, two mast uprights, top tie, two braces (30 x 30 x 2) |
| Clear width between rails | 0.66 m; flared mouth 0.78 m; UHMW guide strips on the inner faces |
| Drive | Two 24 V powerchair gearmotors with spring-applied brakes, wheels 318 mm diameter at 0.97 m track, pneumatic block-tread tyres (13 x 5.00-6) |
| Nose castors | Two 260 mm swivel castors, 0.82 m ahead of the drive axle, 0.60 m track |
| Anti-tip wheels | Two 100 mm wheels under the rail tips, 75 mm off the ground |
| Lift | One 24 V linear actuator, 4 kN, 400 mm stroke, IP65. Carriage on 8 ball-bearing rollers and 4 side rollers running on the two mast uprights |
| Comb | 640 x 75 x 6 mm S355 plate with teeth, on a pivot block: yaw +/-4 deg, roll +/-3 deg, centring springs. Travel 0.80 to 1.20 m above the ground |
| Rest pad | 400 x 120 mm, 12 mm rubber on UHMW, 0.50 m below the comb, face 25 mm behind the comb seat line, slots +/-25 mm |
| Bins | 120, 140 and 240 L two-wheel bins to EN 840-1, comb height 860 to 1,030 mm, up to 110 kg gross |
| Mass | 91.0 kg with two 18 Ah AGM batteries (102 kg with a donor AGM pair, 84 kg with LiFePO4); 201 kg with a full 240 L bin |
| Centre of gravity | Robot alone 302 mm ahead of the drive axle, 409 mm high. With a full 240 L bin 194 to 212 mm ahead, 510 to 568 mm high (two bin CG models) |
| Speed | 0.5 m/s; 0.8 m/s on the open lane if the owner agrees |
| Pivot circle | 2.22 m diameter, set by the castor swivel circles |
| Controls | ArduPilot Rover on an F405 flight controller, Radxa Zero 3W companion, RoboClaw 2x30A with wheel encoders, RTK GNSS, 2D lidar, two radars, rear camera, LTE |
| Safety | The project's G8 list unchanged: two E-stop stations, two series contactors through a used Pilz PNOZ X3, sprung bumpers on positive-opening switches, speed and standstill monitor, tilt switch, watchdogs, spring brakes |

## 3. Sequence of operation

Pick-up:

1. Approach in reverse on the rear camera and the bin's tag. Carriage low (comb 0.80 m), below any lip.
2. Enter. The flared tips and the guide strips centre the bin; the two rail-tip gap sensors cross-check the side offset over the last 0.5 m.
3. Square up. Two roller-lever switches on the carriage face confirm contact with the bin's front wall. The two comb ToF sensors read the lip height and the yaw.
4. Raise the comb. The self-aligning plate takes up residual yaw and roll. Two comb-seat switches confirm the lip is seated on the teeth. If the load comes on more than about 25 mm below the expected lip height, abort and lower (the comb is under the rim flange, not in the receiver).
5. **FH1.** Keep lifting until both bin-wheel clearance sensors read clear and the comb has risen at least 100 mm from load-on. Stop at the stroke end regardless.
6. **FH2.** Claim the bin only if both comb-seat switches are made and both clearance sensors read clear. Otherwise lower the bin to the ground, back out and report a safe miss.
7. Drive off. If a comb-seat switch opens during the carry, stop and lower. The comb-seat switches are in the stop loop.

Set-down is the reverse: stop, lower until the actuator current falls and the comb-seat switches open, lower 30 mm more, drive forward clear of the bin, photograph it.

FH1 and FH2 are the two firmware fixes the other agent defined when testing Rev H (`COMPARE_B1_vs_RevH.md` s.2). Their B1 firmware steps F1 to F9 (approach, squaring, abort and retry logic) carry over unchanged in intent; the pad steps F7 and F10 do not apply because the pad does not move.

## 4. Changes from Rev H, and why

| Change | Reason |
|---|---|
| Mast, carriage, pad and nose moved 80 mm forward (bin front wall at x 0.45 m, mast at 0.53 m, castors at 0.82 m); batteries moved from the rail tips to the axle line (x -0.10 m) | Castor lift-off angle about the drive axle with a full 240 L bin was 15.1 deg. It is now 22.5 deg on the other agent's hand calc, with no ballast |
| Comb: 600 mm rigid blade replaced by the 640 mm self-aligning plate | The other agent's Monte Carlo shows a rigid full-width comb misses on residual yaw (86/90) and the self-aligning one does not (89/90) |
| Lift: 300 mm / 3 kN replaced by 400 mm / 4 kN; comb travel 0.80 to 1.20 m | Lets firmware lift until the wheels are clear on every bin, including 250 mm-wheel bins and a pad that is set wrong; margin 3.3 on the heaviest lift |
| Rest pad: 0.45 m below the comb and uncontrolled, now 0.50 m below, depth-adjustable, default 25 mm set-back | The pad position decides the hang angle. 0.45 m is the lifter makers' minimum; 0.50 m gives margin and a lower pad force |
| Claim logic: FH1, FH2 and two bin-wheel clearance sensors | A comb switch alone cannot tell a carried bin from a dragged one |
| Mast 1.30 m raised to 1.36 m | Room for the longer stroke |
| Nose corners chamfered 70 mm | Smaller swept circle |
| Motor controller: RoboClaw 2x30A with encoders | Closed-loop speed and the encoder channel the speed monitor needs |
| Safety, navigation, sensing, comms, wiring, lights, dock | Rev H under-specified these. Rev H2 takes the other agent's G8 list unchanged |
| Drop layout | G6 layout (order A, M, F; handles to the road) replaces the superseded G4 layout |

Cost of the changes: about 5.5 kg and about EUR 315 against Rev H on the same basis; slightly worse 60 mm step results in the reduced-order model, because more weight sits on the castors.

## 5. Taken from B2, and not taken

Taken: the self-aligning comb; the rail-tip gap sensors (which were a Rev H idea B2 adopted); the frozen gate and its pass marks as the test standard; the whole G8 safety and function list; the lane rules of `DESIGN_B2.md` s.1 and s.8 (0.40 m from the mapped hedge face, S-shift before an empty pivot); the staged build.

Not taken, with reasons:

| B2 item | Why not |
|---|---|
| Docking on the handle side | The receiver is on the front (`EVIDENCE_receiver_side.md`) |
| Retractable sprung pad, knee toggle, second actuator, pad-lock switch, firmware F10 | Needed in B2 because its pad must get out of the way of the bin wheels as the bin enters handle-first. In Rev H2 the bin enters wheels-last and the pad never obstructs it |
| 2 x HGR15 profile rails | Need a flat machined seat and dislike grit and rust. Rollers on box section are cheaper and tolerant |
| New motors with a 3.5:1 chain stage | The donor drive is cheaper. The chain's mechanical speed cap is lost: see decision D3 in `HANDOVER.md` |
| 330 mm solid PU wheels, 200 mm castors | Pneumatic tyres and 260 mm castors mount a kerb more easily |
| 5 kg of ballast | Geometry does the same job |
| Keeper over the rim | Not rejected. To be decided by drop test B3; space is reserved above the comb plate |

## 6. Sub-assemblies

**Frame.** One section size. All joints bolted through flat plates, so it can be built with a saw, a drill and a spanner, and adjusted. Zinc-rich paint. Side-rail bending is the lowest structural margin: safety factor 1.64 at a 3 g wheel load (`statics.py`); check it against peak wheel loads from MuJoCo (simulation S12) and consider 50 x 50 x 4 for the rails.

**Mast and carriage.** Two uprights 440 mm apart, 1.05 m long, on the mast-base cross-member with gussets and two braces to the nose. The carriage is an H-frame: top bar behind the comb, lower bar behind the pad, two side members, four roller cheeks. Mast bending safety factor 2.84 at 3 g.

**Lift actuator.** Body pinned to a lug on the mast-base cross-member, rod pinned to a horn on the carriage 130 mm above the comb line. With the comb at 0.80 m the pins are about 600 mm apart, at 1.20 m about 1,000 mm. **Check before ordering:** the unit's retracted pin-to-pin length must be 600 mm or less for a 400 mm stroke (typical is stroke + 200 mm). If it is longer, raise the horn, not the base. The actuator must hold a 110 kg bin unpowered (test B4). Mount so that a failed pin lets the bin down onto its own wheels.

**Comb.** 640 mm wide to cover the 580 mm receiver of a 240 L bin with yaw and offset to spare; it also takes the 480 mm receiver of 120 and 140 L bins. Tooth profile to EN 840-1 Annex B, teeth clear of the receiver ribs. **Do not cut it until the standard has been bought and the three bins measured** (tests B0b, B1). A rubber buffer under the pivot block softens shock loads.

**Rest pad: setting procedure.** With the bin standing on level ground and the comb just touching the lip, measure the gap between the pad face and the bin's front wall. Set the slots so the gap is 0 to 10 mm on the bin with the most upright wall. A bin with more draft will then hang up to about 2 deg and lose up to 15 mm of wheel clearance, which FH1 recovers. Record the setting in `params.py` (`pad_setback`) and re-run `hang.py`.

**Drive.** A used rear- or mid-wheel-drive powerchair gives two gearmotors with spring brakes, wheels, and often usable batteries and a charger. Motors hang under the side rails on 6 mm plates with their inboard faces clear of the 0.66 m bin slot. Buy only after pull test B5. The new-drive variant (the other agent's PEWM82M-320W motors) is costed in `bom_revH2_new.csv` as a fallback.

**Batteries.** Two 12 V 18 Ah AGM, one on each rail beside the drive wheel, or the donor's larger pair in the same place (heavier, more range, slightly lower castor share). The three-bin evening uses about 135 Wh at 0.5 m/s against a 156 Wh cold-weather plan.

**Sensors special to Rev H2.** Two comb-seat switches (in the stop loop), two squaring switches, two comb ToF sensors, two rail-tip gap ToF sensors, two bin-wheel clearance ToF sensors on the inner rail faces at the bin-wheel station 45 mm above the ground, one actuator current sensor. Everything else is the G8 list.

## 7. Mass budget

| Item | kg | x m | z m |
|---|---|---|---|
| Side rails with flared tips | 12.3 | 0.24 | 0.285 |
| Nose cross-member and outriggers | 5.5 | 0.80 | 0.285 |
| Mast uprights and top tie | 9.8 | 0.53 | 0.83 |
| Mast base cross-member and braces | 3.0 | 0.60 | 0.60 |
| Carriage, comb, pad | 6.1 | 0.48 | 0.90 |
| Lift actuator | 2.5 | 0.585 | 0.65 |
| Drive units (motors, gearboxes, wheels) | 19.0 | -0.08 | 0.16 |
| Nose castors and forks | 5.0 | 0.82 | 0.15 |
| Anti-tip wheels | 0.8 | -0.40 | 0.10 |
| Batteries, 2 x 18 Ah AGM | 10.8 | -0.10 | 0.40 |
| Electronics box, controller, contactors, harness | 5.5 | 0.66 | 0.55 |
| Sensors, lights, bumpers, covers | 6.7 | 0.50 | 0.45 |
| Motor plates, brackets, fasteners | 4.0 | 0.15 | 0.22 |
| **Total** | **91.0** | **0.302** | **0.409** |

From `params.MASS_ITEMS`. These are estimates. Weigh the built robot at each wheel (test B6) and correct the list.

## 8. Loads and margins (reduced-order models; see `RESULTS_H2.md`)

| Quantity | Value | Margin or limit |
|---|---|---|
| Lift force, full 240 L, on rollers | 1,215 N | 3.3 on a 4 kN actuator, 2.5 on 3 kN |
| Mast moment, full 240 L | 459 N m | Mast safety factor 2.84 at 3 g |
| Pad force, full 240 L | about 770 N | Rubber pad 400 x 120 mm: 0.016 MPa |
| Comb bearing on the lip | 0.28 MPa static | HDPE yield 20 to 25 MPa |
| Drive-wheel load, full 240 L, level | 77 kg each | Castors 23.5 kg each |
| Torque to climb 12 % at 201 kg | 23.6 N m per wheel | 60 N m limit |
| Friction needed to climb 12 % | 0.23 | Gate tests to 0.22 |
| Sideways tip, full 240 L | 37 to 40 deg | Gate needs 20 deg |
| Castor lift-off about the drive axle, full 240 L | 22.5 deg (their bin CG), 18.9 deg (mine) | Target 20 deg |
| E-stop on 12 % downhill from 0.5 m/s | 0.14 m | Gate allows 0.5 m |

## 9. Known weaknesses and open points

1. **Not through the MuJoCo gate.** G1 (grab), G5 (carry and pivot), G6 (set-down) and G7 are open.
2. **The full-width 40 mm kerb.** Every design stalls on it in MuJoCo. Rev H2 passes it in the reduced-order model, which is the more optimistic tool. Plan on 1:4 ramps at known steps until kerb test F1 says otherwise.
3. **Castor lift-off is at the target, not above it**: 22.5 or 18.9 deg depending on the bin's centre of gravity. If tilt test B7 gives under 20 deg, move the batteries to the nose (about +4 deg, at the cost of more castor load on kerbs) before adding ballast.
4. **The fixed pad must be set to the bins.** A household with bins of very different front-wall draft gets a compromise setting and relies on FH1.
5. **Width 1.04 m.** B2 is 0.93 m. Narrowing Rev H2 means motors that fit inside a 0.19 m envelope each side or a narrower donor axle.
6. **Receiver strength under shock** is assumed from the EN 840-5 lifting test and has not been tested on an aged bin (B2, B3).
7. **Side-rail safety factor 1.64 at 3 g.**
8. **No keeper.** If drop test B3 shows the lip lifting off the teeth, add the clamp bar (about EUR 20 and one more switch).
9. **Speed cap is firmware plus an independent monitor**, not gearing, unless the donor's top speed is already low. Measure it in B5.
10. **Donor price.** EUR 400 is carried from the other agent's list; Irish listings seen on 12 November were mostly EUR 600 to 1,250. Each EUR 100 adds EUR 115 all-in.
11. **Regulation.** The EU Machinery Regulation 2023/1230 applies from 20 January 2027 and treats a person who builds a machine for their own use as its manufacturer. Not legal advice; see `RESEARCH_2026-11-12.md` Q6.

## 10. Staged build (agreed in both lines of work)

| Stage | Build | Proves | Parts, about |
|---|---|---|---|
| 0 | Nothing: tests B0, B0b, B1, and B2 on a mock comb | Receiver side, pad setting, lip strength | The standard (price not checked) and scrap steel |
| 1 | Frame, donor drive, mast, carriage, comb, pad, actuator, on a hand controller with the E-stop chain | Docking, lifting, carrying, kerbs, slopes, on Brian's bins and lane (B3 to B9, F1, F2) | EUR 1,320 |
| 2 | Autonomy: flight controller, RTK, lidar, camera, companion, comms | Navigation, docking trials F3, set-down F4 | EUR 880 |
| 3 | Full safety list, lights, dock, audio | Unattended evenings F6 | EUR 710 |

Stage costs are parts only, split by area from `bom_revH2_donor.csv` (stage 1: structure, bin handling, drive, power; stage 2: navigation, sensing, comms, enclosure and wiring; stage 3: safety, lights, dock). In practice the E-stop, contactors and fuses from stage 3 are fitted in stage 1.
