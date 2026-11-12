# Bin Tug Rev H package

Concept-overhaul work for the Bin Tug project, 11 November 2026. Rev H is a proposal: nothing has been built, and the project's
HANDOVER and README have not been changed. The report is the Claude doc "Bin Tug Rev H: concept overhaul"; this package holds the
code and results behind its numbers.

## What Rev H is

A U-shaped robot on the donor powerchair drive. It reverses around the bin from the bin's front, lifts it 100 mm by the EN 840
front comb lip, and carries it upright between its own drive wheels. It replaces Rev G's handle grabber, tilt mast, kingpin trailer
frame, lid finger and sand ballast with one 300 mm actuator, one roller carriage and four switches.

## Contents

| Path | What it is |
|---|---|
| `RESULTS_H1.md` | Every result table, generated from `results/` |
| `results/mech.json` | Layout study, obstacle runs, grade runs, Rev G calibration |
| `results/statics.json` | Lift force, structure, stability, drive demand, hand check of the step results |
| `results/dock_mc.json` | Docking tolerance Monte Carlo |
| `results/mission.json` | Lane timing and energy, placement accuracy, turning space |
| `results/bom_revH.csv`, `bom_revH.json` | Parts list, logistics, contingency, Rev G comparison, stages |
| `fig/` | Concept drawing, turning-space figure, and three sheets of isometric drawings (robot, pick-up sequence, carrying) |
| `sim/params.py` | The one place geometry, masses and bin data are defined |
| `sim/dyn.py`, `sim/models.py` | Reduced-order dynamics (x, z, pitch, roll) and the Rev H / Rev G models |
| `sim/tests_mech.py` | Layout study, obstacles, grades (about 4.5 min) |
| `sim/statics.py`, `sim/dock_mc.py`, `sim/mission.py`, `sim/bom_revH.py` | The other four result generators (seconds each) |
| `sim/make_results_md.py`, `sim/make_figs.py` | Build `RESULTS_H1.md` and the two flat figures |
| `sim/make_iso.py` | Isometric drawings: `fig/iso_1_robot.png`, `iso_2_pickup.png`, `iso_3_carry.png` (needs numpy and matplotlib) |
| `data/` | Copies of the project's `route.json`, `grades.json` and `drop_layout_default.json` used by `mission.py` |

## Re-running

Python 3 with the standard library; `make_figs.py` also needs matplotlib.

```
cd sim
python3 tests_mech.py
python3 statics.py
python3 dock_mc.py
python3 mission.py
python3 bom_revH.py
python3 make_results_md.py
python3 make_figs.py
python3 make_iso.py
```

All random draws are seeded, so a re-run reproduces the JSON files exactly (apart from the CPU time recorded in `mech.json`).

## Limits of this work

- The isometric drawings follow `params.py` for every main dimension. Brackets, caster forks, braces, lamp positions and the shape of
  the bin's front lip are not fixed by `params.py`; they are drawn as intended, not as designed.

- The dynamics are a first-order model written for this review, not the project's MuJoCo set-up. There is no yaw, so one-sided
  obstacle results are optimistic: the model passes Rev G over the 50 and 60 mm one-sided bumps that MuJoCo stalls on.
- No ArduPilot SITL run was made. Timings and energy come from a kinematic model of the lane profile, which matches Rev G's SITL
  one-bin drop to within 1 min and 2 Wh.
- Docking percentages are a tolerance stack with assumed sensor errors, not contact physics.
- EN 840 comb dimensions came from a text extract of the 2004 edition. Measure the real bins before trusting them.
- Prices: 39 of 63 lines are carried from the Rev G list; most of the rest are estimates or search excerpts.

## If Rev H is adopted

The project's standing rule applies: write Handover Rev 4.0, update the README, and re-zip the project. The first technical jobs are
to port Rev H into the project's MuJoCo and SITL set-ups and re-run both regressions, and to measure the comb lips on the real bins.
