# B2-F tests, part 2: lane with a bin, stress cases and the lane-driving software

13 November 2026, afternoon. Follows `RESULTS_B2F_tests_2026-11-13.md` from this morning.

Everything here is simulation. No hardware has been tested. The bin check (B0), the bin measurements and the lane survey are still outstanding, and each can change the result.

**Improved version** means B2-F with three mechanical changes:

- the pad fixed in place, 5 mm further back, with no pad actuator;
- 350 mm of lift travel, with the bin carried 150 mm up;
- the castor cross-beam on a centre pivot.

## 1. Findings

1. **The improved version passes every lane run with a full bin and carries the bin higher.** Bin wheels stay 40 to 108 mm above the ground. For B2-F as designed the figure is 6 to 63 mm in the three runs I repeated.
2. **Both versions stall at a sharp 40 mm up-step when returning empty.** A 1:4 ramp at the step cures it. So do 260 mm castors, at about EUR 65 more.
3. **The improved version passed all its stress and grab tests:** 24 of 24 stress cases, 150 of 150 grabs on five bin types, and 90 of 90 grabs started up to 118 mm and 8.9 degrees off line.
4. **The other agent's three-bin drop failure is real.** It failed 3 of 3 in my runs of their unmodified code, for the reason they gave.
5. **With four software fixes, all 60 driving scenarios pass their frozen scorer.** Their own result was 52 of 60.
6. **The firmware file supplied for my type of machine is the wrong version.** It is ArduRover 4.7.2; their tests ran on 4.6.2. My driving results are therefore not like-for-like, and one margin (the turn at pad A) is clearly different between the two versions.
7. **Cost is essentially unchanged from this morning's estimate:** about EUR 3,534 on a donor chair with the changes now backed by tests, against EUR 3,844 published.

## 2. What I need from you

**To make the driving tests like-for-like, one of these:**

- Ask the other agent for an x86-64 build of ArduRover 4.6.2, git hash 1ebd4d99, as a file. The x86-64 file in the pack is 4.7.2 (hash fb773567).
- Or let me build it. The official source tag `Rover-4.6.2` is exactly hash 1ebd4d99; I checked. The safety check blocked the build because the source comes from GitHub, not from your archives. To allow it, send: *"Standing approval for this chat: download the ArduPilot source from github.com/ArduPilot/ardupilot at tag Rover-4.6.2 and build the Rover SITL binary in your sandbox."*

**From the lane survey, when it is done:** any step of 40 mm or more that faces the robot on the way back up, the real layout of the yard, and where the bins stand at home. Section 4 explains why each matters.

## 3. Mechanical tests (MuJoCo 4.0.1)

### 3.1 Lane with a bin

The lane is the other agent's model, with the 40 mm step left sharp, the trench covered and the pothole filled. "Clearance" is the smallest gap between the bin's wheels and the ground during the run.

| Run | B2-F as designed | Improved version |
|---|---|---|
| Full 240 L (110 kg), house to pad | pass, clearance 11 mm | pass, 56 mm |
| Night worst case (mass +10 %, grip -20 %, bin centre of gravity 60 mm higher) | pass, 6 mm | pass, 40 mm |
| Full 140 L (66 kg), house to pad | pass, 63 mm | pass, 102 mm |
| Stop and hold on 12 % downhill, wet leaves | not re-run; their stored result is a pass | pass, 107 mm |
| Stop and hold on 12 % uphill, wet leaves | not re-run; their stored result is a pass | pass, 108 mm |
| Return empty | **fail**: stalls at the 40 mm step | **fail**: stalls at the same place |
| Collect an empty 240 L bin and return | **fail**: same | **fail**: same |
| Return empty, 1:4 ramp at the step | not run | pass |
| Collect empty bin and return, ramp | not run | pass |
| Return empty, sharp step, 260 mm castors | not run | pass |
| Collect empty bin and return, sharp step, 260 mm castors | not run | pass |

**Why the empty return stalls.** Going back up, the castors meet the step first. The empty robot has only about 455 N on its drive wheels, which gives about 270 N of push on a damp surface. Lifting two 200 mm castors over a sharp 40 mm edge needs about 600 N. Loaded, the drive wheels carry about 1,540 N and the robot gets over.

**Options, cheapest first:**

1. A ramp or fillet at any such step. Passes in simulation. Cost EUR 0 to 20.
2. Crossing with the drive wheels first when empty. This is a software change and I have not tested it.
3. 260 mm castors. Passes in simulation, and the full gate still scores 9 of 9 with 90 of 90 grabs. About EUR 65 more for the pair. I tested the nominal case only, not low grip.

### 3.2 Stress variations

These are the other agent's four variations (mass +10 %, mass -10 %, grip -15 %, bin-wheel rolling resistance raised), six cases each.

| Version | Simulator | Passed | Clearance in the moving cases |
|---|---|---|---|
| Improved | 4.0.1 | 24 of 24 | 90 to 97 mm |
| B2-F as designed | 4.0.1 | 23 of 23 run (one grab case not run) | 47 to 65 mm |
| B2-F as designed, their stored results | 3.17.0 | 24 of 24 | 29 to 65 mm |

### 3.3 Grabs

| Test | Improved version | B2-F as designed |
|---|---|---|
| Three gate bins, 30 grabs each | 90 of 90 | 89 of 90 |
| Two extra bins (240 L with 250 mm wheels, 140 L), 30 each | 60 of 60 | 60 of 60 |
| Start offsets 1.5 times wider (up to 118 mm, 8.9 degrees) | 90 of 90, including 42 of 42 beyond the frozen range | not run |
| Set-down of the 250 mm-wheel bin, six cases | 6 of 6 | 6 of 6 |

The frozen test range for start offsets is 80 mm and 6 degrees. The driving software refuses to grab beyond 50 mm and 3 degrees, so the mechanism has more than twice the tolerance the software asks of it.

### 3.4 Building the longer lift

The longer travel needs no new parts. The parts list already prices the 400 mm actuator and 1 m rails. The rails and mast uprights move up by about 60 mm so the upper carriage blocks stay on the rails. The rear camera sits on top of the mast, so the overall height may rise from 1,450 mm by up to the same amount unless the carriage blocks are re-spaced. I have not redrawn this in CAD.

## 4. Lane-driving software tests

### 4.1 Set-up, and what is not like-for-like

- I ran the other agent's scenario, world, robot-computer and scoring code unchanged. Fixes were tested in a separate copy with each fix behind a switch.
- The x86-64 firmware in the pack is **ArduRover 4.7.2**. Their campaign ran on **4.6.2** on a different processor type.
- Version 4.7.2 ignores the setting their parameter file uses to switch off arming checks, so the robot would not arm. I added `ARMING_SKIPCHK -1` through their runner's own parameter option. Nothing else was changed.
- I ran each scenario in one piece. Their runs were cut into pieces of about 100 seconds and restarted, because of a limit on their machine.
- Several simulators ran at once on two processor cores. In the busiest periods the simulated robot weaved more and used about 6 % more energy. I confirmed this in three one-bin runs; the one-bin runs made in quieter periods match the unmodified code closely.

### 4.2 Results against their frozen scorer

| Scenario | Their stored result (4.6.2) | Their code, my runs (4.7.2) | With four fixes (4.7.2) |
|---|---|---|---|
| One-bin drop | 3 of 3 | 3 of 3 | 3 of 3 |
| One-bin pickup | 1 of 3 | 3 of 3 | 3 of 3 |
| Three-bin drop | 0 of 3 | 0 of 3 | 3 of 3 |
| Three-bin pickup | 1 of 3 | 1 of 1 (two not run) | 3 of 3 |
| Satellite fix lost for 20 m | 2 of 3 | 3 of 3 | 3 of 3 |
| The other 15 scenarios (safety stops, refusals, fences) | 45 of 45 | 45 of 45 | 45 of 45 |
| **Total** | **52 of 60** | **55 of 58** | **60 of 60** |

With the four fixes:

- **Three-bin evenings** finish between 20:43 and 20:45, against a 21:00 limit. That leaves about a quarter of an hour. Their one passing three-bin run finished at 20:47.
- **Energy** is 44.5 to 49.2 Wh per trip against a 50 Wh limit. The four trips above 47 Wh all ran while four simulators shared two cores.
- **Hedge clearance** is at least 0.148 m against a 0.124 m limit.
- **Set-downs:** 27 of 27 within 0.10 m; the limit is 0.15 m.
- **Line-up before a grab:** 27 of 27 passed first time, at most 28 mm off.

### 4.3 The four fixes

All four are software and cost nothing.

1. **Planned path out of the yard.** With a bin collected far to the side of the yard, their code slid sideways toward the lane too slowly and reached the hedge end at 25 m. Mine drives a planned curve to the lane centre at 21 m, checked against the map and the known bins first. Planned clearance was 0.72 m or more in all six uses.
2. **Camera check before the grab.** At the line-up point the robot reads the bin's sideways offset with the rear camera and, if it is more than 25 mm out, corrects its estimate and lines up again. I modelled the camera with 10 mm of random error. The rear camera and bin tags are already in the parts list.
3. **Sign error in lane-keeping.** One branch steered toward the right hedge when it should steer away. This is the fault the other agent identified.
4. **Smooth approach to the bin.** Their code reverses along a straight line and then turns on the spot beside the bin, which at pad A is the tightest place on the lane. Mine reverses along a curve that ends already lined up.

**Evidence for fix 2.** In the four-fix campaign, 5 of 12 pad pickups first arrived more than 50 mm off line, the worst 65 mm. Each would have missed the line-up check on arrival. All five were corrected and passed. With their straight-line approach the figure was 3 of 12 in my runs. The numbers are small, but fix 4 should only be adopted together with fix 2.

**A further refinement, tested on four runs only.** The re-alignment after a camera correction includes two small turns on the spot. In one three-bin pickup these brought the nose to 0.148 m from the hedge at pad A. Driving the re-alignment as two smooth curves raised that to 0.198 m in the same scenario, and all four runs passed the scorer (the three one-bin pickups and that three-bin pickup).

### 4.4 Two things the comparison shows

**The pickup failures they reported did not recur with their own code on my set-up.** They had four pickups refused out of ten attempted. I had none refused out of six, with one first-time miss. I cannot tell from this whether the difference is the firmware version, the unbroken runs, or chance.

**Turning on the spot overshoots on 4.7.2.** A 17 degree turn at pad A overshot by about 14 degrees in my runs of their code. Their report gives 0.38 to 0.41 m of hedge clearance at pad A. I measured as little as 0.16 m with their code, and 0.106 m in two runs with the first three fixes but not the fourth; those two runs failed the scorer on clearance. The turn tuning was done on 4.6.2 and does not carry over. Whichever version goes on the robot must be the one the tuning is tested on.

## 5. Cost after these tests

All-in figures with the other agent's own contingency rule, in EUR.

| Step | Donor chair | New drive |
|---|---|---|
| Published B2-F | 3,844.23 | 4,112.32 |
| Sourcing and pricing corrections, castor pivot, taller mast | 3,620.06 | 3,888.15 |
| Plus fixed pad, now backed by the tests above | 3,534.31 | 3,802.40 |
| Plus roller carriage in place of profile rails (bench test only, not simulated) | 3,459.56 | 3,727.65 |
| New drive with AGM batteries, on the tested steps | n/a | 3,725.29 |
| New drive with AGM batteries, all steps | n/a | 3,650.54 |

Their pending structural upgrades add about EUR 132 to every row. Optional 260 mm castors add about EUR 65.

Prices I checked today:

- Waveshare A7670E Cat-1 modem board: EUR 31.00 including tax at Botland, in stock.
- 12 V 22 Ah AGM battery: EUR 42.99 (Green Cell) to about EUR 57 (Victron) each.
- 260 mm swivel castor, puncture-proof: GBP 53.29 including VAT each at Castors-Online.

I have not re-priced the other lines of their parts list. EUR 2,000 remains out of reach under the no-cuts rule.

## 6. Questions for the other agent (information only)

1. Can you supply an x86-64 build of ArduRover 4.6.2 (1ebd4d99)? The x86-64 file in the pack reports 4.7.2 (fb773567).
2. Was the x86-64 file ever run with this test set-up? On 4.7.2 `ARMING_CHECK 0` has no effect.
3. What accuracy do you assume for the rear camera reading a bin tag at 1.2 to 2 m? Your final reverse uses it with no error.
4. Are the home positions of the three bins (10 m along, 1.4, 3.0 and 4.6 m to the side) measured or assumed?
5. The five design questions from this morning are still open: the folded plates, why the pad retracts, battery and ballast positions, the duplicated switch line, and whether the hitch gearmotor and second latch switch are used.

## 7. Limits of this work

- The driving tests ran on firmware 4.7.2, not 4.6.2, and under varying machine load. They should be repeated on 4.6.2, one simulator at a time.
- The four fixes were developed and scored on the same 60 scenarios and three seeds. They have not been tried on fresh seeds.
- The refined re-alignment has four runs behind it, not 60.
- B2-F as designed was not re-run on the two slope-hold lane cases, on the ramp or 260 mm castor cases, or with wider start offsets.
- The 260 mm castor option was not tested at low grip, and the mass file was not updated for the heavier castors.
- The roller carriage, the mast change and drive-wheels-first crossing are untested.
- The lane, the yard and the bins in every model are assumed from maps and catalogues, not measured.

## 8. Files

- `b2f_tests_part2_evidence_2026-11-13.zip`: my scripts and switches, every gate, lane and driving-test result as JSON, and the frozen-scorer tables for each campaign.
- `cost_b2f_changes_v2_2026-11-13.csv`: the cost changes line by line with the evidence now behind each.

Sources for the prices: [Botland, A7670E LTE Cat-1 HAT](https://botland.store/gsm-modules/20110-a7670e-lte-cat-1-hat-for-raspberry-pi-multi-band-2g-gsm-gprs-lbs-waveshare-20049-5904422380212.html); [aio.lv, Green Cell AGM54 12 V 22 Ah](https://aio.lv/en/product--green-cell-csb-1222agm54--4303731.md); [panpower.eu, Victron AGM 12 V 22 Ah](https://panpower.eu/es/akumulatory-/6759-victron-energy-agm-deep-cycle-12v-22ah-bat212200084.html); [Castors-Online, 260 mm puncture-proof swivel castor](https://castors-online.co.uk/product/puncture-proof-pneumatic-equivalent-castor-260mm-swivel-plastic-centred-4562).
