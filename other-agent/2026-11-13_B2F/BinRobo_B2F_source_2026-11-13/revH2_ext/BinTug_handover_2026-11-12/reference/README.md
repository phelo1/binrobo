# Reference: the other agent's files

Copied unchanged on 12 November 2026 from the other agent's archive `BinRobo_full.zip` (dated 12 November), keeping its folder layout so that its scripts find each other. Nothing in `other_agent/` was written or edited by the Rev H2 author.

| Path under `other_agent/` | What it is |
|---|---|
| `README_HANDOVER_Rev3.0.md`, `docs/HANDOVER.md` | Their project hand-over notes |
| `docs/reviews/DESIGN_B2.md` | The B2 design, gate results, lane fit and parts list |
| `docs/reviews/COMPARE_B1_vs_RevH.md` | Their test and review of Rev H |
| `docs/reviews/PROGRESS_B2.md`, `PROGRESS_compare.md` | Their run logs, with the commands used |
| `docs/reviews/CONCEPT_GATE_G6.md`, `ITER1_conceptB.md` | How the gate and concept B came about |
| `revG/sim/cg/` | The MuJoCo concept gate: `CRITERIA_FROZEN.md` (do not edit), runners, models (`cmp/simH.py` = Rev H, `b2/simB2.py` = B2), stored results in `res/` folders, lane-fit tool `cmp/lanefit.py`, B2 cost script `b2/bom_b2.py` |
| `revG/sim/g6/*.py` | Bin models (`bins_g5.py`) and the base simulation modules the gate imports |
| `revG/bom_revG8*.{py,csv}`, `COSTDOWN_G8.md` | The G8 cost baseline whose safety and function lines Rev H2 uses unchanged |
| `revG/ELEC_SAFETY_G7.md` | The electrical safety case |
| `revG/BINS_[waste collector]_G5.md` | Their bin survey |
| `revG/REVG_DESIGN.md`, `RESULTS_G6_mech.md` | Rev G, for history |
| `revH_ext/revH/sim/` | Their copy of the Rev H parameters, which `cmp/simH.py` imports |
| `sitl/scripts_g6/*.py`, `sitl/config_g6/`, `sitl/data/` | Only the parts of the SITL set-up that `lanefit.py` needs. The full SITL set-up is in `BinRobo_full.zip` |
| `web/downloads/g5bins/` | Bin makers' data sheets and drawings (SULO, Craemer, Weber, ESE) |

Three things to know before relying on these files (details in `docs/COMPARE_RevH2_vs_B2.md` s.4):

1. B1 and B2 assume the EN 840 comb receiver is under the handle. It is on the front wall.
2. The bin hull in the MuJoCo models puts a 170 mm taper on the front wall (`cmp/simH.py` line 132). The drawings in `web/downloads/g5bins/` show it on the rear.
3. B2's parts list appears to count the lift actuator twice (`ACT-L8` and `B-0`).

None of this code was executed in the session that produced Rev H2: MuJoCo was not available there. The files were read, and one result (the hang angle) was reproduced independently in `revH2/sim/hang.py`.
