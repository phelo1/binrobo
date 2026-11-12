# Bin Tug: hand-over brief for the next agent

12 November 2026. Project "binrobo": an autonomous robot that takes Brian's wheelie bins down a 635 m private lane to the road and brings them back. Owner and builder: Brian.

Read this file first, then `docs/TESTS_AND_SIMULATIONS.md`. Everything else is reference.

## 1. Where things stand

- **Nothing has been built.** All results are calculations and simulations.
- There are two competing designs of the same kind of machine (a straddle carrier that lifts the bin by a comb under its rim):
  - **Rev H2** (this package): docks on the bin's **front** wall. Parts list EUR 3,469 all-in on a donor powerchair drive, EUR 3,737 with new motors. **Not yet run through the MuJoCo gate.**
  - **B2** (the other agent, `reference/other_agent/docs/reviews/DESIGN_B2.md`): docks on the **handle** side. EUR 3,992 / 4,260 as published. Passes 8 of 9 gate items in MuJoCo, on a bin model that has a comb receiver under the handle.
- **The EN 840 comb receiver is on the front wall** (`docs/EVIDENCE_receiver_side.md`). So B2's passes were earned on a feature real bins do not have on that side, and Rev H2 is on the right side but unproven. Neither design is ready to build.
- The original target of EUR 2,000 all-in is **not reachable** with the project's present safety and function list (those shared lines alone are EUR 1,595 of parts). That is a decision for Brian (D2 below), not something more design work will fix.

## 2. Your job, in order

1. Get Brian to do test **B0** (which side is the receiver on, five minutes) and **B1** (measure the bins). Everything depends on B0.
2. Install MuJoCo. Reproduce one stored result of the other agent (**S0**).
3. Correct the bin model (**S1**), build the Rev H2 MuJoCo model (**S2**), run the frozen gate on it (**S3**), then **S4 to S8**.
4. Run B2 on the corrected bin (**S11**) so the final choice is fair.
5. Report to Brian with one table: both designs, same gate, same bin model, same cost basis.
6. Only then: SITL (**S9**), structure (**S12**), detail design and drawings for stage 1 of the build.

The full lists with pass marks are in `docs/TESTS_AND_SIMULATIONS.md`.

## 3. What is in this package

| Path | What it is |
|---|---|
| `README.md` | One-page map |
| `HANDOVER.md` | This brief |
| `docs/DESIGN_RevH2.md` | The design: specification, sequence, sub-assemblies, mass budget, weaknesses, build stages |
| `docs/COMPARE_RevH2_vs_B2.md` | Rev H, B2 and Rev H2 side by side; who was right about what; cost on one basis |
| `docs/EVIDENCE_receiver_side.md` | Why the receiver is on the front, with sources |
| `docs/TESTS_AND_SIMULATIONS.md` | Every test and simulation still to do, with pass marks |
| `docs/RESEARCH_2026-11-12.md` | Standards, geometry, prices, kerb ratings, regulation, with source links |
| `drawings/` | General arrangement, three isometric sheets, side view, bin interface, turning space (PNG) |
| `revH2/sim/` | Python models and drawing scripts. `params.py` is the single source of geometry and mass |
| `revH2/results/` | JSON and CSV outputs: parts lists, cut list, plate list, model results |
| `revH2/RESULTS_H2.md` | Every Rev H2 number, generated from the JSON |
| `revH2/reference_out/RevH2_lanefit_design.json` | Rev H2 footprint in the format of the other agent's `lanefit.py` |
| `history/revH/` | Rev H as delivered on 11 November, unchanged. Superseded |
| `reference/other_agent/` | The other agent's design documents, MuJoCo gate, bin models, cost scripts, safety case, lane-fit tool and bin data sheets, in their original folder layout |

Not included, because of size: the other agent's full archive `BinRobo_full.zip` (307 MB: ArduPilot SITL set-up, logs, Rev G CAD and manufacturing files) and the original `Bin_Tug_Project_Docs_Rev3_0.zip` (111 MB). Brian has both. You need the first for simulation S9.

## 4. History in six lines

1. **Rev F1 to Rev G8** (earlier agent): a tug towing the bin on a kingpin trailer with a tilting mast and handle grabber. Its cost rose well past the EUR 2,000 target and it kept failing its own simulations.
2. **Rev H** (11 Nov, this author): concept overhaul to a straddle carrier lifting by the front comb lip. Claimed EUR 1,990. Tested only in a reduced-order model.
3. **B1** (11 Nov, other agent): their own straddle carrier, docking on the handle side, with a frozen MuJoCo gate G1 to G9.
4. **Their review of Rev H** (`COMPARE_B1_vs_RevH.md`): Rev H scores 2 of 9 as designed, 7 of 9 with two firmware fixes; its cost claim does not stand on the safety baseline.
5. **B2** (12 Nov, other agent): B1 plus Rev H's simpler frame and full-width comb. 8 of 9.
6. **Rev H2** (12 Nov, this author): Rev H corrected for every valid point in their review, with B2's comb, on the front receiver.

## 5. What is established, and by what

| Statement | Evidence | Confidence |
|---|---|---|
| The comb receiver is on the front wall | Three makers' drawings, EN 840-1 terms, GGAWB guidelines, ESE manual | High. Confirm on Brian's bins (B0) |
| The receiver is qualified for 100 loaded lift cycles at 110 kg gross (240 L); the handle is not a lifting point | EN 840-5 text, GGAWB | High for the standard; unknown for an aged bin under shock |
| With the pad set to the wall, the bin hangs within about 1 deg and its wheels clear by about 90 mm at 100 mm lift | `hang.py`: static geometry from scaled drawings | Medium. Needs B1, B11, S4 |
| The other agent's "11 to 12 deg hang" for Rev H follows from a 170 mm front-wall taper in their bin hull | `cmp/simH.py` line 132; reproduced by `hang.py` | High |
| Rev H2 meets the frozen thresholds for climb, E-stop, static loads and tip angles, and mass | `gate_like.py`, a model with no contact and no yaw | Indication only |
| Rev H2 passes the full-width 40 mm kerb | Reduced-order model only; MuJoCo stalls every design | Low. Treat as failing |
| Castor lift-off angle 22.5 deg (their bin CG) or 18.9 deg (my higher bin CG) | Hand calc | Medium. Needs B7 |
| Pivot circle 2.22 m; fits the 3.6 m lane and the 2.9 m narrowing | Geometry; their lane-fit tool not yet run | Medium. Needs S8 |
| A three-bin evening takes about 140 min and 135 Wh at 0.5 m/s | Kinematic estimate checked against one Rev G SITL run | Medium. Needs S9 |
| Rev H2 costs EUR 3,469 (donor) or EUR 3,737 (new drive) all-in | `bom_revH2.py`; 23 % and 37 % of parts value price-checked | Medium. Donor price is the main risk |
| B2's list counts the lift actuator twice (about EUR 173) | `b2/res/bom_b2_new.csv`, `b2/bom_b2.py` | Probable. Ask its authors |

## 6. What is not established

- Whether Rev H2 grabs, carries and sets down a free bin (gate items G1, G5, G6): no contact simulation has been run.
- Whether a real, aged receiver survives this robot's bumps (tests B2, B3).
- Whether any of these designs climbs a real 40 mm kerb (F1).
- The receiver profile, to cut the comb teeth (B0b).
- The front-wall position of Brian's bins (B1).
- Whether the lift actuator holds and lifts cold (B4), and whether a donor drive has the pull (B5).
- Rev H2 in SITL.

## 7. Decisions for Brian

| ID | Decision | Options | What it turns on |
|---|---|---|---|
| D1 | Which design goes forward | Rev H2, or B2 turned round to dock on the front, or a merge | B0, then S3 and S11 |
| D2 | Budget against functions | Accept about EUR 3,100 to 3,500; or cut functions to approach EUR 2,000 | The cuts available, in parts cost: two-way audio EUR 75, two radars EUR 48, road-style lights and tape EUR 125, Cat-1 instead of Cat-4 modem EUR 60, second contactor EUR 29, speed monitor EUR 40, cheaper motor controller EUR 72, cheaper actuator EUR 115. Each removes a function or a layer of safety |
| D3 | How the speed is capped | Firmware cap plus the independent speed monitor (Rev H2); or a chain stage that makes the top speed mechanical (B2) | The donor's measured top speed (B5); appetite for a chain drive |
| D4 | Drive | Donor powerchair (EUR 3,469; price and condition vary); or new motors (EUR 3,737; known quantity) | B5, and what is for sale locally. Each EUR 100 on the donor adds EUR 115 |
| D5 | Speed on the open lane | 0.5 m/s (three bins in about 140 min); or 0.8 m/s (about 95 min) | Stopping distance 0.35 m from 0.8 m/s on the 12 % in the model; Brian's comfort |
| D6 | Kerbs | Fit 1:4 ramps at the known steps now; or wait for kerb test F1 | Whether the lane's steps are his to alter |
| D7 | Keeper over the rim | Fit; or leave off | Drop test B3 |

## 8. Rules that have kept this project honest

1. `revH2/sim/params.py` is the single source of geometry and mass. Change a number there and regenerate; never edit a number in a document or drawing.
2. `reference/other_agent/revG/sim/cg/CRITERIA_FROZEN.md` is frozen. Do not edit it or loosen a pass mark. If a criterion is wrong, say so and add a new one beside it.
3. Say which tool produced every result: hand calc, reduced-order model, MuJoCo, SITL, or test. Never call a simulation a test.
4. Label calibration runs as calibration. Gate runs use the frozen settings and seeds.
5. Prices carry a status (checked, excerpt, estimate) and a date. Contingency by status: checked 5 %, excerpt 8 %, estimate 12 %, used or local 15 %; logistics counted separately.
6. Compare designs on the same basis: same gate, same bin model, same safety and function lines. Rev H's EUR 1,990 broke this rule.
7. Check premises against primary sources. Two agents built on opposite assumptions about the same bin for a day; five minutes with a data sheet settles it.
8. Record a miss as a miss.

## 9. Running the Rev H2 models

Python 3 with numpy and matplotlib. No other packages.

```
cd revH2/sim
python3 hang.py            # how the bin hangs; reproduces the other agent's hang figure
python3 gate_like.py       # climb, kerb, E-stop, statics against the frozen thresholds (about half a minute)
python3 tests_mech.py quick   # obstacle and grade sweeps (about 4 min)
python3 statics.py         # lift force, frame stress, stability
python3 dock_mc.py         # docking tolerance stack
python3 mission.py         # evening time and energy, turning, placement
python3 bom_revH2.py       # parts lists and totals
python3 make_results_md.py # rebuilds ../RESULTS_H2.md
python3 make_ga.py         # general arrangement, bin interface, cut and plate lists, lane-fit footprint
python3 make_iso.py        # three isometric sheets (robot | pickup | carry)
python3 make_figs.py       # side view and turning figure
```

Model files: `dyn.py` (rigid body, x, z, pitch, roll; no yaw), `models.py` (robot and welded bin), `params.py`.

## 10. Corrections to my own earlier work

So that nobody relies on them:

- Rev H at EUR 1,990 all-in: withdrawn. On the project's safety baseline Rev H is about EUR 3,154 and Rev H2 EUR 3,469.
- Rev H pivot circle 1.93 m: wrong, it ignored the castor swivel circles. Rev H was 2.16 m; Rev H2 is 2.22 m.
- Rev H "docking success 99.95 %": a tolerance stack, not a contact simulation. Do not quote it.
- Rev H obstacle and E-stop "passes": scored against marks looser than the frozen gate.
- Rev H "largest gap between lip and comb": computed with the bin welded on. It says nothing about retention.
- A suggestion from the research task to approach kerbs drive-wheels-first: my model does not support it.
