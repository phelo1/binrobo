---
title: "Country Road Bin Robot (Bin Tug) - Project Handover"
subtitle: "Revision 3.0 - G3, G4 and G5 update, 10 November 2026"
author: "Owner: Brian - prepared with Hark"
geometry: margin=2cm
fontsize: 10pt
colorlinks: true
toc: true
toc-depth: 2
---

# 1. How to use this handover

This Rev 3.0 document brings the project up to date after work packages G3, G4 and G5 (7-10 November 2026). **It overrides HANDOVER Rev 2.2 (`docs/HANDOVER.md`) wherever the two disagree.** Rev 2.2 is kept in full for the base description of the job, the lane, the electrical concept and the history of revs A to G2.

Read in this order: this file, then the reports listed in section 10, then Rev 2.2 for background.

Status key:

- **SIM** = verified in simulation only.
- **WIP** = work in progress.
- **OPEN** = a decision or measurement is needed.
- **TODO** = not started.

Nothing has been built or tested physically yet.

# 2. The job (unchanged in principle)

- Tow a wheelie bin between the house and the public road ([road]) along Brian's private lane, about 633 m, [village], [county].
- **Down:** full bin. **Up:** empty bin, collected later, often after dark.
- **[county] bye-laws:**
  - out no earlier than 18:00 on the day before collection;
  - in by 21:00 on collection day;
  - lid closed.
- Plan to finish by 21:00, with midnight as the backstop.
- **Collector:** [waste collector]. Household bins are 140 L and 240 L two-wheel bins plus a 25 L food caddy (`revG/BINS_[waste collector]_G5.pdf`).
- **Standing rules from Brian:**
  - No capability cuts or part removals to save money. Cost-downs come only from sourcing, used or donor parts, and materials.
  - Wheels only.
  - Handle awkward bins: backwards, sideways, in the hedge, moved, tipped, a neighbour's bin, or a car blocking.

# 3. Current design (Rev G, G5 state)

| Area | Current choice | Status |
|---|---|---|
| Layout | Hand-truck tug with a mast that tilts the bin about 48 deg onto its own wheels; rear frame articulated about a kingpin | SIM |
| Grabber | **GH-B5F-130** (replaces GH-B2): hooks from below at +/-130 mm; 45 deg lip, 0.6 deg ease-off; ratcheting float; drop-away release with a 150 N cord; **camera-guided centring and one re-approach**; squaring guard (stop if the rear frame swings >25 deg or the tug creeps >0.15 m); **two IP67 cup-floor feeler switches**, so a hold is claimed only when both cups are seated. About EUR 15 more than GH-B2. | SIM |
| Kingpin | M16 8.8 kingpin bolt (zero play, castle nut and split pin), 150 mm steel thrust ring, UHMW washer. Worst case 1,976 N.m (pothole); safety factor 2.7. **Hard yaw stops at +/-30 deg**, because the hinge saddle reaches the drive tyre at about 35 deg | CAD |
| Mass | Lean dry 83.1 kg (steel tray), about 76.5 kg with an aluminium tray. **Operating mass 95 kg**, using 11.9 kg of dry sand in two 10 L HDPE cans in the front bay. 95 kg is a threshold, not a margin | SIM |
| Drive | Donor powerchair drives, 24 V LiFePO4 pack, Cytron MDDS30 driver (**needs added reverse-polarity protection**) | CAD |
| Mast tilt | Linear actuator. **The listed XTL450 (1,000 N, IP54) is under spec.** It needs 1,500-2,500 N, IP66, retracted <=642 mm and extended >=1,053 mm | OPEN |
| Sensing | RTK GNSS (LC29H with a base station), 2D lidar (LDROBOT STL-06N candidate, needs a driver bench test), rear camera with ArUco tags, tilt current sensing, latch switches, and **24 GHz radar front and rear** (G4) | CAD/SIM |
| Lights | Headlamps, rear red, amber sides, reflective tape, and a beacon. **The beacon draws 18 W, not 2 W** | CAD |
| Comms | 4G modem. **The E3372 is rated only to +40 deg C; the pod can reach about 48 deg C, so it needs an industrial modem rated to +75 deg C.** Two-way audio (IP67 speaker and mic, WebRTC, EUR 40-70) | OPEN |
| Dock | Mains dock: contacts are dead until the tug is seated, RCD, cold-charge inhibit. Solar was rejected (EUR 346, and 20.7 % of December days end flat) | CAD |
| Safety | Hard-wired stop loop now switches **only the coils of relays K1 and K2** (fix E1), not about 2.2 A of load current | CAD |
| Shipping | 56.1 kg in 5 boxes, each <=25 kg. Donor drives, casters, battery and sand are bought in Ireland | CAD |

# 4. Proven capability (simulation)

## 4.1 Grabbing bins (G5, real-contact MuJoCo, 30 runs per bin)

| Bin | GH-B2 (old) | GH-B5F-130 (pick) |
|---|---|---|
| Weber 140 L | 7/30, 12 false holds | 27/30, 0 false holds |
| ESE 140 CL | 6/30, 17 false holds | 30/30, 0 |
| SULO Citybac 240 | 26/30 | 27/30, 0 |
| ESE 240 CL (lowest handle) | 27/30 | 30/30, 0 |
| ESE 240 SL, 200 mm wheels | 29/30 | 29/30, 0 |
| ESE 240 SL, 250 mm wheels | 30/30 | 29/30, 0 (one safe miss) |
| Craemer MGBneo 240 (tallest) | 29/30 | 30/30, 0 |
| **Total** | **154/210, 29 false holds** | **202/210 (96 %), 0 false holds** |

Capture includes one re-dock.

- **Why GH-B2 failed on 140 L bins:** their 478 mm wheel track lets the bin sit up to 75 mm off centre in the 590 mm funnel, so one hook lands outside the handle while the pull test still passes.
- **How the fix works:** camera centring brings the median offset to about 5-8 mm, and the feelers refuse any hold on one hook.
- **Remaining misses are all safe** (nothing claimed, nothing tipped):
  - round 42 mm bars on full bins;
  - one squaring-guard stop;
  - one funnel-arm contact on a Craemer.
- A 0/30 false-hold count still allows up to about 11 % per model at 95 % confidence.
- **Why +/-130 mm and not +/-110 mm:** the +/-110 mm version stalled on the 40 mm step tow at 110 kg. +/-130 mm passes.
- The real cost of GH-B4 was EUR 53-174. Its sprung pads were 60-90 % of the money, and they are not needed.

## 4.2 Release, steps and towing

- **Release.** It passes on flat ground and in most 12 % slope cases. It fails in two:
  - a full 140 L bin with the tug facing uphill;
  - an empty bin with the tug facing downhill.

  **Firmware rule:** on a slope, release a full bin with the tug facing downhill and an empty bin with it facing uphill (fill is estimated from tilt current). On the G3 generic bin, a full bin on 12 % downhill needs the 150 N cord. Iced or jammed pawls release on the first cycle at 150 N. A dead cam gets 2 retries, then the tug holds the bin and alerts.
- **Steps (full bin, about 108-110 kg).** It passes a 40 mm sharp step. It stalls at 50-60 mm and on a 100 mm pothole. Tug mass does not fix this, because the bin wheel is the limit.

  **Rule:** ramp or fill any sharp lip over about 40 mm in the bin-wheel track (rubber kerb ramp EUR 15-40, or cold-lay tarmac). **A lane survey is needed.**
- **Towing at 110 kg.** It passes straight, 90 deg turn, slalom and e-stop on the Weber 140 and ESE 240 SL.

## 4.3 Autonomy (SITL, ArduPilot Rover 4.6.2 plus a Python lane world)

**G3 (final):**

- Regression 39/43 as expected; robustness 52/52 (13 scenarios x 4 seeds).
- The four failures (s10a, s10b, s20a, s20c) came from the pinch-zone check refusing a 2nd or 3rd bin at side-by-side spots.
- **The "3-bin evening finishes at 19:40" figure is invalid.**

**G4 (WIP):**

- **Fixed:**
  - the pinch-zone exemption for still, bin-sized objects at programmed slots (people and vehicles are never exempt; s16b still refuses);
  - the hedge being read as a blocked slot;
  - dock retries (up to 3 seatings);
  - the placement alert, which relied on simulator ground truth and is now only an evaluation flag.
- **Features written, all passing provisionally:**
  - (a) teach-and-repeat route and poses;
  - (b) bin calendar with alternate weeks;
  - (c) programmable drop layout;
  - (d) keep-left at 0.3-0.5 m;
  - (e) vehicle-approach stop with radar and lidar (oncoming, behind and passing);
  - (f) two-way audio API stub;
  - (g) adaptive drop spot: alternates, an all-blocked alert, keep-out zones, and pickup at the logged pose.
- **All G4 runs must be repeated** with the CAD limits: hitch articulation 28 deg (`HITCH_CAP`) and the tug 195 mm longer at the front (`sitl/scripts_g4/world.py`, lines 14 and 18).
- **Open issues:**
  - s24a: with a car parked on the home slot, the U-turn into the alternate hits the car;
  - spot A placement is 0.60-0.65 m off in multi-bin runs;
  - short false lidar holds at bends.
- **Energy:** a 3-bin drop uses about 107 Wh (SOC 100 -> 61 %). Three drops plus three pickups without a recharge need about 250 Wh against about 243 Wh usable, so **a dock recharge is needed between drop and pickup.** The completed 3-bin evening margin to 21:00 is still to be measured.
- **Geofence:** the closest footprint is 0.37 m inside the private boundary. The G3 "one breach" note (s10a) still needs explaining.

# 5. Manufacturing package (G5, partly done)

In `revG/mfg/`:

- **Bought-parts dimension register**, 57 rows graded by source: 8 from maker pages, 4 from distributors, 16 from search excerpts (re-check these), 27 class envelopes to measure on arrival, and 2 donor parts.
- **Fit check of real part outlines in CAD.** About 21 clashes were found and fixed (FX-01..21), including:
  - the electronics pod passing through the rear plate, spine and kingpin;
  - the thrust ring clashing with the deck;
  - the casters sitting inside the bumper and on an unsupported flange;
  - the actuator clashing with the mast rail;
  - floating clevis ears;
  - the latch hitting a can;
  - the hinge hitting the isolator.

  Remaining small items: the motor sits 2 mm from the tray wall, and the lid sits 4 mm from a hook at 6 deg.
- **Drawings:** `Drawings_G5.pdf` covers 53 made parts, with 34 DXF flat patterns, bend and hole tables, ISO 2768-mK, finish and part-ID etch, and a tube and bar cut list. The donor adapter plates DR-60 and CH-61 are templates until the donor drive is measured.
- **Harness:** 14 looms, 101 wires, about 116 m. Every wire passes current rating and the <3 % voltage-drop check; the worst full path is 2.8 %. The cut and crimp list and nail-board drawings are in `harness/`.
- **Thermal:** about 11 K over ambient on standby and 15 K at peak.
- **TODO:**
  - IKEA-style assembly manual (renderer written, content not yet);
  - donor-drive measuring procedure MP-1/MP-2 and adapter rules AR-1..8;
  - harness PDF and fit-check report PDF;
  - part substitutions (actuator, BMS >=20 A continuous, industrial modem, driver reverse-polarity protection, beacon power budget);
  - cold-eye review of the package.

# 6. Cost

- **Master BOM** (`revG/bom_revG.py`): EUR 1,832 parts, EUR 1,970 with shipping and duty, EUR 2,167 with 10 % contingency.
- **G4 cost-down with no cuts** (`revG/COSTDOWN_G4.pdf`, `bom_revG4.*`): **EUR 2,131 all-in.** Savings come from:
  - donor casters, conditional;
  - LC29H boards;
  - STL-06N lidar;
  - beacon swap;
  - Netherlands shipping;
  - the cam motor.
- **Price rises:** the MDDS30 driver and Nord-Lock washers.
- **Grabber change:** add about EUR 15 for GH-B5F-130.
- **Not yet in the total:**
  - the part substitutions in section 5;
  - the CAD-spec galvanised frame (about +EUR 165);
  - lane ramps (EUR 15-40 each).
- **Gap to EUR 1,200** is about EUR 930. The options outside sourcing are Brian's call:
  - share with a neighbour (about EUR 1,066 each for two houses);
  - reuse an existing RCD socket (EUR 25);
  - local laser-cutting quotes (e.g. ATC Group, [nearby town]);
  - resell unused donor parts.

# 7. Operating rules adopted

1. Release a full bin facing downhill and an empty bin facing uphill on any slope. Release an empty bin only with the tug facing uphill.
2. Refuse to tow over 110 kg, estimated from tilt current.
3. Ramp any sharp lip over 40 mm in the bin-wheel track.
4. Keep the tug-bin articulation within +/-28 deg in planning; hard stops sit at +/-30 deg.
5. Recharge at the dock between the drop and pickup runs on 3-bin evenings.
6. A hold is claimed only when both feelers are seated and the pull test passes.
7. If a drop spot is blocked, use the nearest legal alternate inside the private geofence, keeping the handles toward the lane. If none is clear, hold and alert.
8. Refuse to release when a person or vehicle is in the pinch zone.
9. The 25 L food caddy is not handled. Options: swap to a 140 L brown wheelie, or a EUR 25-45 cradle.

# 8. Waiting on Brian (OPEN)

- **Lane walk:**
  - sharp lips or potholes over 40 mm;
  - steepest pitch;
  - number of houses.
- **Bins:** bar section, bar height, hand gap, web spacing, wheel size, and a photo of the maker and date marking.
- **Dock site:** an outdoor RCD socket within about 5 m; a spot for the dock.
- **Drop pad:** just inside the lane mouth.
- **Insurer:** check cover for an autonomous machine on a private lane.
- **Decisions:**
  - hobby or product (grants, CE, a China frame quote);
  - which cost-downs to accept;
  - whether to share with a neighbour.
- **Computers:** the Oracle VM resize (do not touch the trading app); NucBox SSH.

# 9. Next steps (in order)

1. Re-run G4 SITL with the 28 deg hitch limit and the longer front. Run a full regression, a completed 3-bin evening with recharge (to measure the margin to 21:00), and 4-seed robustness. Fix s24a and the spot A placement. Write `RESULTS_G4_sitl`.
2. Finish the manufacturing package: the manual, harness PDF, fit report and substitutions. Then a cold-eye review.
3. Update the BOM with GH-B5F-130 and the substitutions.
4. Bench tests once parts arrive:
   - lidar driver;
   - camera centring on real bins;
   - feeler switches;
   - donor drive measurement.
5. Produce a toleranced drawing release after the review. Then get local laser quotes.

# 10. Document map (in this zip)

| File | What it is |
|---|---|
| `docs/HANDOVER_Rev3.0.pdf` | This handover |
| `docs/HANDOVER.pdf` / `.md` | Rev 2.2 base handover (job, lane, concept, history A-G2) |
| `revG/Bin_Tug_Design_Capabilities_G5.pdf` | 24-page design and capabilities report (written before the GH-B5F-130 pick) |
| `revG/RESULTS_G5_binrange.pdf` | Bin-range tests, cheap-fix screen, GH-B5F-130 pick, release, step and tow |
| `revG/BINS_[waste collector]_G5.pdf` | [waste collector] bin sizes and compatibility |
| `revG/COSTDOWN_G4.pdf`, `bom_revG4.*` | Cost-down with no cuts |
| `revG/RESULTS_G3_mech.pdf`, `revG/REVIEW_G3_takeover.pdf` | G3 mechanical results and takeover review |
| `sitl/Bin_Tug_G3_SITL_Report.pdf`, `revG/RESULTS_G3_sitl.md` | G3 autonomy results |
| `sitl/out/G4/PROGRESS.md` | G4 SITL state and resume notes |
| `revG/mfg/` | Parts register, Drawings_G5.pdf, DXF, harness data, fit check |
| `revG/REVG_DESIGN.pdf`, `RESULTS_G1/G2`, `REVIEW_G2_coldeye` | Earlier Rev G work |
| `revG/cad/`, `cad/` | CadQuery models, STEP and STL, mass and kingpin checks |
| `revG/sim/`, `sitl/scripts*` | Simulation code and result JSON |
| `docs/REVIEW_cold_eye.pdf`, `docs/revG/` | First cold-eye review; electrical, BOM and China manufacturing notes |

Videos are not included in this zip. They were sent separately (full-cycle render, G3 mechanical and SITL videos, highlights).

# 11. Revision log

| Rev | Date | Change |
|---|---|---|
| 2.2 | 2026-11-06 | Rev G draft, G1 and G2, cold-eye review 2 (imported) |
| 3.0 | 2026-11-10 | G3: real-contact grabber (GH-B2), M16 kingpin, 40 mm step limit, sand ballast to 95 kg, SITL G3. G4: cost-down to EUR 2,131 with no cuts; features a-g written; SITL fixes. G5: [waste collector] bins; narrow-bin failure found; **GH-B5F-130 grabber** (202/210, 0 false holds); release-by-fill rule; manufacturing package started (53 drawings, 14 looms, 21 clash fixes, +/-30 deg yaw stops, under-spec parts flagged); design PDF; full-cycle render |
