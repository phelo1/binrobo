# Bin Tug hand-over package, 12 November 2026

An autonomous robot to take wheelie bins down a 635 m lane and back. This package holds the current best design (**Rev H2**), its drawings, models, results and parts lists, the comparison with the other agent's design (**B2**), and the list of tests and simulations still to be done.

**Start with `HANDOVER.md`.** Then `docs/TESTS_AND_SIMULATIONS.md`.

## Status in five lines

1. Nothing has been built. Every result is a calculation or a simulation.
2. Rev H2 lifts the bin by the comb receiver on its **front** wall. B2 lifts on the **handle** side. The receiver is on the front (`docs/EVIDENCE_receiver_side.md`).
3. Rev H2 has **not** been run through the project's MuJoCo gate. B2 has (8 of 9), on a bin model with the receiver on the wrong side.
4. Rev H2: EUR 3,469 all-in on a donor powerchair drive, EUR 3,737 with new motors. B2: EUR 3,992 / 4,260 as published.
5. First action: Brian checks which side the receiver is on (test B0, five minutes).

## Contents

```
README.md                       this file
HANDOVER.md                     brief for the next agent: status, job list, decisions, rules
docs/
  DESIGN_RevH2.md               the design
  COMPARE_RevH2_vs_B2.md        Rev H, B2 and Rev H2 compared
  EVIDENCE_receiver_side.md     which side the comb receiver is on, with sources
  TESTS_AND_SIMULATIONS.md      tests B0-B12, F1-F8 and simulations S0-S14, with pass marks
  RESEARCH_2026-11-12.md        standards, geometry, prices, kerb ratings, regulation, links
drawings/
  ga_revH2.png                  general arrangement: side, plan, front, dimensions
  iso_1_robot.png               the robot from four sides
  iso_2_pickup.png              picking up a bin, and how it hangs
  iso_3_carry.png               carrying a full 240 L bin
  revH_concept.png              side view with load path
  bin_interface.png             comb, receiver and pad; the other agent's bin model beside it
  turning_space.png             turning room
revH2/
  RESULTS_H2.md                 every Rev H2 number, generated from results/*.json
  sim/                          Python models and drawing scripts (params.py is the source of all dimensions)
  results/                      parts lists (donor, new drive), cut list, plate list, model outputs
  data/                         lane route and grades, G6 drop layout, G8 baseline cost lines
  fig/                          same PNGs as drawings/, where the scripts write them
  reference_out/                Rev H2 footprint for the other agent's lane-fit tool
history/revH/                   Rev H as delivered on 11 November (superseded)
reference/other_agent/          the other agent's documents, MuJoCo gate, bin models, cost and safety files,
                                lane-fit tool and bin data sheets, in their own folder layout
```

## Not in this package

- The other agent's full archive `BinRobo_full.zip` (307 MB): ArduPilot SITL set-up and logs, Rev G CAD and manufacturing files. Needed for simulation S9.
- The original `Bin_Tug_Project_Docs_Rev3_0.zip` (111 MB).
- Manufacturing drawings, DXFs or CAD for Rev H2: none exist yet. The design is at concept stage.

## Requirements

Python 3 with numpy and matplotlib for `revH2/sim`. MuJoCo for the other agent's gate in `reference/other_agent/revG/sim/cg`. Commands are in `HANDOVER.md` s.9.
