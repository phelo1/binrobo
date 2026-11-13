# BinRobo B2-F source pack, 2026-11-13

The project folder layout is kept: paths below are relative to the project root P. Nothing was run or re-run to make this pack.

## Left out of the pack

- Videos and renders: mp4, png, jpg, gif, and cad/revF1 frames/ and videos/.
- cad/revF1/study/*.pkl (24 MB of study pickles); model_revF does not read them.
- SITL checkpoints (sitl/b2f/ckpt, ckpt_dev_old) and run outputs. The scored results are included as sitl_results/.
- sitl/bin/: not rebuilt after 12 Nov. See versions below.

## Not on disk

**The xlsx builder.** No script that writes BinRobo_B2F_BOM_2026-11-12.xlsx survives on disk; it was written ad hoc. Its data sources are in the pack:

- revG/sim/cg/b2/bom_b2.py, which writes res/bom_b2.json;
- work/h2lane/price_checks.json and s14_cost.py.

It applied these changes on top of bom_b2.json:

- removed the duplicate ACT-L8;
- re-priced BMP-L8 to EUR 160.10 (Omron D4N-4120);
- contingency: 5 % verified, 8 % excerpt, 12 % estimate, 15 % local/used/donor, 10 % logistics.

The workbook itself is included (out/b2f_bom/) so its line values can be read directly.

## Versions

| Item | Value |
|---|---|
| Python | 3.12.15 (GCC 14.2.0) |
| MuJoCo | 3.17.0 |
| numpy | 2.5.4 |
| Processor | aarch64 (ARM Neoverse-V2), 2 shared vCPU |
| Python packages | from PYTHONPATH=/workspace/work/pylib |
| ArduPilot SITL binary | sitl/bin/ardurover_aarch64, built 2026-11-06, banner "ArduRover V4.6.2 (1ebd4d99)", git hash 1ebd4d99 |

b2f_runner.py picks the binary by machine type: ardurover_aarch64 on aarch64, otherwise sitl/bin/ardurover (x86-64, built 2026-11-06). Neither was rebuilt after 12 Nov.

## Commands

All commands run with PYTHONPATH=/workspace/work/pylib.

### 1. MuJoCo gate G1-G9 and perturbations (B2-F and Rev H2)

- **Working directory:** P/revG/sim/cg
- **Exact command lines:** in revG/sim/cg/h2/q_h2.txt (331 lines). The H2 frozen suite starts at line 1, B2F frozen suite at 73, H2 perturbations at 182, B2F perturbations at 207. Other blocks: S4-S7 and S10.
- **Runner:** revG/sim/cg/h2/qchunk_h2.py \<queue\> \<budget_s\>, which runs each line as `timeout -s TERM <left> nice -n 10 <line>`.
- **Run log:** h2/q_h2.txt.log, with START and END rc for every line.
- **Example B2-F line:**

  `env CGB_F9=1 CMP_SIM=simB2h B2_DOCK=front CMP_PREFIX=B2F_ IT1_TAG= python3 h2/runH2.py grab ESE240SL 30 202`

- **Rev H2 lines:** the same, but with CMP_SIM=simH2 CMP_PREFIX=H2_ and no B2_DOCK.
- **Perturbations:** add PERT_MASS=1.1 / PERT_MU=0.85 / PERT_CRR=0.9 / dt etc. with IT1_TAG=_pm110 ... (see lines 182-231).
- **Results:** revG/sim/cg/h2/res/\<PREFIX\>\<test\>\<tag\>.json (for example B2F_grab_ESE240SL.json, B2F_climb_m22_c09_pm110.json).
- **Summary:** h2/summarize_h2.py.

### 2. Lane fit (S8)

- **Working directory:** P. The checkpointed runner splits the run into pieces; re-call it until it prints DONE.
- **Commands:**
  - `python3 work/h2lane/lanefit_ckpt_h2.py work/h2lane/B2F_b2r.json 100` writes work/h2lane/res/lanefit_B2F_b2r.json (b2/lanefit_b2.py rules).
  - `python3 work/h2lane/lanefit_ckpt_h2.py work/h2lane/B2F_cmp.json 100` writes res/lanefit_B2F_cmp.json (cmp/lanefit.py rules).
  - Rev H2: the same with RevH2_b2r.json / RevH2_cmp.json. Pad-shift variant: `env PAD_DS=0.25` writes lanefit_RevH2_b2r_pad-0.25.json.
- **Slow pieces:** some sequence pieces were split per pad with work/h2lane/seqsplit.py (identical computation).

### 3. Lane physics P1-P7 (MuJoCo digital twin)

- **Working directory:** P/work/b2f_lanephys
- **Command:** `python3 lanerun.py <run_id> 95`. Re-call until it prints DONE; it checkpoints to runs/\<id\>/ckpt.pkl.
- **Output:** runs/\<id\>/result.json.
- **run_ids, in the order run:**
  - P1, P5a_drop_sharp_3kN, P5b_drop_sharp_4kN, P5c_drop_ramp14, P5d_up_sharp_3kN, P5e_up_sharp_4kN, P5f_up_ramp14, P5g_trench_open, P5h_pothole, P4a, P4b, P6a_person_estop, P6b_dog_crossing;
  - then P2a, P2c, P3, P7, P5i_trench_open_4kN;
  - supplementary: P2a_pf, P2c_pf.
- **Dependencies:** P2a/P2c start from P1's final state; P4/P5/P6 start from P1 snapshots; P2c_pf starts from a P2c snapshot. Run P1 first.
- **Scenario definitions:** the RUNS dict at the top of lanerun.py. World: lane_world.py (hfield cache hfield_cache.npz is regenerated if missing, about 22 s).
- **Superseded runs** (kept, not scored): _P1_v1_carryflag, _P1_v2_rampsign, _P4b_v1_lowspeed, _P6a_v1_person_stays, _P6b_v1_dog_far, _P6b_v2_nolog.

### 4. ArduPilot SITL

- **Working directory:** P/sitl/b2f
- **Command:** `./run_chunk.sh queues/scored.txt 78`. Re-call until QUEUE EMPTY.
- **Inside the chunk:** it runs `PYTHONPATH=/workspace/work/pylib timeout -s INT 112 python3 scripts/b2f_runner.py <queue> --budget 78`.
- **Output:** B2F_OUT=/workspace/work/out/b2f_lane/sitl/runs (default), per run \<scenario\>__s\<seed\>/.
- **queues/scored.txt:** one line per "\<scenario\> \<seed\>", 60 lines. Scenarios s1a s1b s3a s3b s4a s4b s4c s5a s5b s6a s6b s7 s8 s9 s10a s10b s11a s11b s12a s12b, seeds 7, 11, 23.
- **Scoring:** scripts/b2f_ana.py against CRITERIA_B2F_SITL.md (sha256 586b61b8...). Code md5s are in FROZEN_CODE_B2F.md5; params are in params/bintug_b2f.parm.
- **Scored results:** sitl_results/score.json, score.md, metrics_summary.md, RESULTS_B2F_sitl.md.

## Design facts

### 4.3 Lift stroke

- **The design is 250 mm of carriage travel.** On 2 x HGR15 rails the comb nib top runs from 0.855 to 1.105 m.
- **Sim:** simB2h.py sets GEO['lift_range']=0.25 (overriding 0.26); note [D3], car_zero 0.855.
- **CAD:** the same as the sim. At carry the actuator sits at 239 of 250 mm.
- **The parts-list labels disagree:**
  - BOM line ACT-B reads "FDI 24 V 300 mm 4 kN lifter, priced as the 400 mm unit - upper bound". The URL is the FDI 400 mm unit.
  - The sim mass list says "3 kN 300 mm".
  - Neither 300 nor 400 mm is a design figure. They are the actuator stroke that was priced. The fit of a longer retracted length on the 1,450 mm mast is not checked.
- **What sets the top height:** the 250 mm travel chosen in the design (sim parameter lift_range). No mechanical or structural limit on the comb's top height is documented; I have not checked whether the rail and mast length would allow more.
- **What drove the 250 mm:** the travel needed to lift the bins. Starting from the lowest lip approach (nib 0.855 m) it gives about 69 mm bin-wheel clearance at carry, which uses 239 mm. I found no other documented constraint, such as a lid or hedge height.

### 4.4 S12 load cases and safety factors

- **Source:** revG/sim/cg/h2/s12_struct.py, which writes h2/res/s12_structure.json and h2/rep/s12_table.md.
- **Method:** hand calculations from the simulated peak forces in h2/res.
- **Safety factor:** SF = yield / stress (or allowable / load), target SF >= 2. S235 yield is 235 MPa; S355 is 355 MPa; bolts 8.8 and 12.9.
- **Load levels:**
  - **STATIC:** G8 statics, 110 kg bin plus CG.
  - **CARRY:** maximum over smooth-ground runs: G2 climb, G4 e-stop, G5, G6 release, S7 and the perturbations.
  - **EDGE:** maximum over pothole runs and compliant-tyre kerb runs.
  - **COMB_ALL:** maximum comb force over every run, including the stalled trench and the S10 contact variants.
  - **Not used:** rigid-wheel impulses at sharp steps (14.7-22.1 kN) and wheel forces in stalled trench runs (0.25-1.06 MN), reported as single-sample rigid-contact artefacts.
- **B2-F loads:**

  | Load | Static | Carry | Edge or all runs |
  |---|---|---|---|
  | Wheel | 930 N | 2,385 N (B2F_estop12_fwd_pm110) | 7,305 N (B2F_S6_kerb_v05_nose_t15_80cas) |
  | Comb | 1,079 N | 1,872 N | 9,633 N (B2F_S5_ESE240SL_step_v08_lsr004) |

  Pad max 1,772 N; lift max 3,000 N (model cap).
- **B2-F elements below SF 2:**
  - Side rail 50x50x2: 1.19 carry (fix 50x50x4) and 0.39 edge (80x80x5 would be needed). The edge case was NOT adopted in the upgrade list; this is an open point.
  - Mast upright at the foot: 0.68 comb_all (fix 80x40x4).
  - Bolt pull-through in the 2 mm wall: 1.00 (fix through-plates or crush tubes).
  - Pivot pin D16: 1.34 (fix D20, 2.61).
  - HGR15 rail screws M4: 1.10 comb_all (fix M4 12.9 into a 10 mm backing flat, 60 mm pitch).
  - Bin receiver ledge (HDPE): 0.56 comb_all. This is the bin, not our part; needs a comb buffer and a real measurement.
- **Rev H2 elements below SF 2:**
  - Rail 50x50x3: 1.30 carry, fixed with 60x60x4.
  - Mast: 1.26.
  - Comb plate half: 1.22, fixed with 8 mm.
  - Pin D16: 1.76.
  - Rollers and track strip.
- **Assumed geometry:** bolt count and lever, pin cantilever 20 mm, block pitch 0.20 m, drop-plate size. All are marked ASSUMED in the output.

### Not answered here

The other questions (4.1, 4.2, 4.5, 4.6, 4.7) were not answered in this pack.
