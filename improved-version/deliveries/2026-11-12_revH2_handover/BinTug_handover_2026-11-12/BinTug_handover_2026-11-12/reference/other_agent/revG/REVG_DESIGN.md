# Bin Tug Rev G - design definition (work packages G1 + G2)

Status: DRAFT design + simulation, 6 Nov 2026. Rev G = Rev F.1 concept (grab handle, tilt 48 deg like a sack truck, tow)
plus the cold-eye review fixes and three owner-requested items: **automatic charging dock**, **better grab mechanism**,
**night lighting**. Nothing physical is built yet. "SIM" = verified in simulation only.

Read with `docs/HANDOVER.md` (source of truth) and `REVIEW_cold_eye.pdf`. Review item numbers are quoted as (R x.y).

---------------------------------------------------------------------------------------------------------------------

## 1. Automatic charging dock

**Idea: the dock is a "fake bin".** The tug already has a precise way to back onto something and know it is seated:
the rear funnel arms, the wheel-stop crossbeam, the seat switch and the rear camera reading an ArUco tag. The dock
reuses all of it, so the dock adds no mechanism to the tug except two contact blocks.

| Part | Definition |
|---|---|
| Location | Yard, lane station s = 4 m, tug parks facing down-lane (as in the SITL). On a 1.2 x 1.0 m paving/concrete pad, under a lean-to rain roof (>= 1.6 m clear; the upright mast is ~1.3 m). |
| Frame | Two short steel posts carrying (a) two rubber-faced **dummy-wheel blocks** at bin-wheel tread height (the crossbeam stops on them exactly as on a bin's wheels) and (b) a **nose block** the same width as a bin's wheel track, which the tug's flared funnel arms (650 mm mouth) ride onto. A backboard carries **ArUco tag ID 20** (retro-reflective) at bin-tag height. |
| Alignment | While docking, the **yaw lock is OFF**: the funnel arms on the nose block swing the free-yawing rear frame into line, so the dock captures +/-150 mm lateral and +/-15 deg yaw at the crossbeam (SITL capture rule). The tug body does not have to be square. |
| Contacts (tug) | Two sprung brass contact blocks on the crossbeam face, 300 mm apart, in HDPE insulators, 15 mm spring travel, self-wiping (they slide ~10 mm on the plate as the crossbeam seats). |
| Contacts (dock) | Two 150 x 60 mm stainless/brass plates on the dummy-wheel faces: +/-60 mm lateral tolerance after the funnel has centred the frame. |
| Electrical safety | Dock plates are **dead (0 V) until a tug is detected**: dock controller (ATtiny/ESP32-C3) closes a 10 A relay only when a reed switch sees the magnet on the crossbeam AND a low-current sense loop through a resistor+diode on the tug reads correctly. Charger output fused 10 A. Mains only at an RCD-protected socket indoors/under cover; only SELV (<= 29.2 V) reaches the dock. Tug side: ideal diode/Schottky so the tug's battery is never on its own contacts (no short if wet or bridged by metal). |
| Charging | 24 V LiFePO4 CC/CV charger, 5 A (~145 W). Charge to 28.4 V (~90 %) for pack life. BMS low-temperature charge cut-off, plus the Pi enables charging only when the pack NTC reads >= +3 deg C (R 1.7.1). INA226 on the tug's charge input confirms current flows. |
| Software | `park()` in `sitl/scripts/companion.py`: drive to 2.6 m in front of the dock, pivot square, reverse with the rear camera on tag 20 (blind last ~1.4 m), stop on the dock contact switch. If no charge current within 10 s: pull forward 1.5 m and retry once, then 4G alert "not charging". |
| Theft | Cable-lock eye on the frame; IMU tamper alert while docked (R 1.3.3). |

Energy sizing: per bin round trip ~37 Wh (SITL s1), three bins ~110 Wh; standby with sleep mode < 10 Wh/day.
A 24 V 10-12 Ah pack (240-290 Wh) recharges from 20 % in about 1.5-2 h at 5 A, so the dock always has the tug full
for the next evening.

SITL result: see section 6 (scenario s9 and every full-cycle scenario now ends on the dock).

---------------------------------------------------------------------------------------------------------------------

## 2. Grab mechanism ("G-hook")

Problems found: capture tolerance only +/-30 mm (R 2.1), a single tilt actuator carries all transport shocks and is
rated 2.5 kN against a 6.1 kN step peak (R 1.9.2), latch failure = bin dropped anywhere (R 1.9.3), plastic handle
loading unknown (R 1.5.5), lid can blow open at 48 deg (R 1.4.4), the brown bin may be smaller (R 1.5.3).

| # | Change | Why |
|---|---|---|
| K0 | **Twin hooks** at +/-190 mm on the carriage (already in the F.1 MuJoCo model), engaging the handle bar next to its moulded side webs, not mid-span. | Halves the point load and puts it where the handle is stiffest. |
| K1 | **Bigger float**: carriage floats +/-60 mm vertically (spring-balanced on the mast rails) and +/-40 mm laterally on UHMW pads; hook entry ramp 120 mm tall. | Covers 240 L and 120-140 L handle heights (~950-1,100 mm above ground, to be measured, R 2.1) and docking error. |
| K2 | **Gravity latch pawls**, one behind each hook. The bar pushes the pawl up and it drops behind the bar. Released only mechanically by a cam at the mast-upright end of stroke, so no release solenoid. **Two latch switches; both must close** before tipping. | Positive lock, fail-safe (no power needed to hold), no extra actuator. |
| K3 | **Mast rest stop + gravity catch at the tow angle.** At 48 deg bin tilt the mast seats on a rubber-faced stop on the rear frame and a gravity catch drops over it. A 10 mm lost-motion slot in the actuator clevis trips the catch at the start of the return stroke. | Transport and step shocks go into the frame, not through the self-locking actuator (R 1.9.2, R 3.11). MuJoCo check in section 6. |
| K4 | **Lid hold-down finger**: sprung stainless arm with UHMW tip on the mast top, rests on the lid's front edge when tilted, lifts clear as the bin stands up. | Lid stays shut in gusts > 7 m/s (R 1.4.4, [county] bye-law 5(a)). |
| K5 | **Actuator current sensing** (INA219). | Tilt current ~ bin mass: full vs empty, "bin not collected" alert at pickup, wrong bin, stall detection (R 3.9). |
| K6 | Actuator mounted **rod-down with a boot**, IP66, 24 V. | Rod-seal water ingress is the usual failure (R 1.8.4). |
| K7 | **Pre-motion rule** (software, SIM): beacon + rear work light flash for 3 s before any tilt or release, and the lidar must see nothing unmapped within 1.5 m (known bins excluded); waits up to 20 s, then alert. | Pinch/crush points at the mast hinge, clevis, yaw sector (R 1.1.4). |

Still to do for the grabber: model K1/K2 geometry in CadQuery (Rev G CAD), MuJoCo capture-tolerance sweep with the
bigger float, and the bench handle-pull test (R 2.2: pull a sandbagged bin's handle to 1.5 kN).

---------------------------------------------------------------------------------------------------------------------

## 3. Night lighting

| Light | Spec | When on (companion `update_lights()`, SIM) |
|---|---|---|
| Amber beacon | 2 W LED, flashing, mast top, 360 deg. **Powered from the brake-release (motor-enable) circuit**, so it is lit whenever the tug can move, even if the Pi has crashed. | Moving, tilting/releasing, 3 s pre-motion warning. |
| Head lamps | 2 x 3 W warm-white (3000 K) LED floods on the front bumper, aimed ~10 deg down with a cut-off: they light the lane for the alert photos and make the tug visible, but do not dazzle drivers at the [road] mouth or light up neighbours. | Night, moving or seeking the bin. |
| Red markers | 2 x 0.5 W: one at the mast top (visible above the tilted bin from behind), one on the rear frame. | Night, whenever not docked. |
| IR illuminator | 850 nm, 5 W, ring around the rear camera (night ArUco, already in the SITL camera model). | Night, viewing/docking/nudging/parking. |
| Rear work lamp | 3 W white. | Night, grab/release and pre-motion warning: colour alert photo, crew can see what the tug is doing. |
| Passive | Retro-reflective tape on tug sides and rear frame, reflective stickers on both sides of every bin (stick-on, clear of chip/labels). | Always. |

Control: 4-channel logic-MOSFET board on Pi GPIO (12 V rail). "Night" = sun elevation below -2 deg from the solar
position (date + RTK position) with a BH1750 ambient-light sensor as the backup. Energy: see section 6 (s1n).
Junction protocol (R 1.2.1, R 3.5): the tug waits >= 15 m inside the lane, enters the mouth only for the drop/pick
(~60 s), never stops in the mouth to "think", and stays docked through the collector's window.

---------------------------------------------------------------------------------------------------------------------

## 4. Software changes in the SITL (all in `sitl/`)

| Change | File | Status |
|---|---|---|
| Companion 1 Hz HEARTBEAT; firmware GCS failsafe on (FS_GCS_ENABLE 1, FS_GCS_TIMEOUT 1, FS_TIMEOUT 1, FS_OPTIONS 1, RC_OVERRIDE_TIME 1). | companion.py, params/bintug.parm | SIM PASS (s8a/b/c) |
| Crash-injection test hook (`crash=(state, delay)` in a scenario): heartbeat, RC override and lidar feed stop. | companion.py, sim_runner.py, scenarios.py | done |
| Bin yaw fusion: **lidar overrules camera**. Seen face normal = the lidar outline axis pointing at the camera (within 60 deg); PnP yaw only chooses when two axes qualify; tag ID gives the face. Close lidar re-scan from the view pose (front lidar facing the bin) before turning the camera to it. L-shape (closeness) box fit replaces minAreaRect for the axis. | companion.py | SIM - see s.6 |
| Charging dock: dock object with tag 20 in the scene, dock contact-capture model, `park()` reverses onto it, one retry, alert. | scene.py, scenarios.py, companion.py | SIM PASS (s9) |
| Lights state machine + lighting load in the energy model. | companion.py, scene.py, sim_runner.py | SIM |
| Pre-motion 3 s warning + 1.5 m clear-zone check before tilt/release. | companion.py | SIM |
| New scenarios: s1n night loaded drop (the real bye-law case), s8a/s8b crash mid-tow, s8c crash while docking, s9 dock. | scenarios.py | SIM |
| Noise-seed sweeps (`BT_SEED`, `sweep.sh`), batch/regression runners (`run_batch.sh`, `regress.sh`). | world.py, sim_runner.py | done |
| Hardware parameter file (arming and EKF checks back on). | params/bintug_hardware.parm | DRAFT, untested |

---------------------------------------------------------------------------------------------------------------------

## 5. Hardware safety chain (wiring definition)

```
 +24V --[main fuse]--[key/isolator]--+----------------------------------------------> DC-DC 12 V / 5 V (Pi, FC, sensors)
                                     |
                                     +--[NC stop loop: E-STOP (twist) -- FRONT bump strip -- REAR bump strip
                                     |    (crossbeam) -- TILT switch (>35 deg) ]--> coil of SAFETY RELAY K1
                                     |
         K1 contact A ------------------> motor driver ENABLE inputs (both channels)
         K1 contact B ------------------> spring-brake release coils (via brake relay) + AMBER BEACON
```
Any break in the loop (button pressed, bumper touched, tug tipped, broken wire) drops K1: motor driver disabled,
brake coils de-energised so the spring brakes clamp, all with no software involved (R 1.1.2, R 3.1a). The
FC/Pi can only drive when the loop is closed. Software layers on top: firmware GCS failsafe (SIM-verified), Pi hardware
watchdog, read-only root (overlayfs), supercap/UPS HAT for clean shutdown (R 1.8.5, R 3.12).

---------------------------------------------------------------------------------------------------------------------

## 6. Results (generated by revG/make_results.py)

### 6.1 Lane SITL regression (ArduPilot Rover 4.6.2 + companion, default noise seed 7)

"Expected" is the correct behaviour (some scenarios must end in a safe alert). Rev F.1 column = original runs (handover Rev 1.2).

| Scenario | Rev F.1 | Rev G | As expected | Sim time | Energy | Geofence | Outcome / key numbers |
|---|---|---|---|---|---|---|---|
| s1_morning | PASS | PASS | yes | 2754 s | 37.1 Wh | ok | completed; dock try 1: contacts closed (+14 mm, -4.6 deg) |
| s1n_night_drop | - | PASS | yes | 2744 s | 42.3 Wh | ok | completed; dock try 1: contacts closed (-34 mm, +5.2 deg) |
| s2_evening_day | PASS | PASS | yes | 2766 s | 35.6 Wh | ok | docked & grabbed; dock try 1: contacts closed (-12 mm, -0.6 deg); yaw PnP 106 -> 110 (true 112) |
| s3_night_pickup | PASS | PASS | yes | 2773 s | 41.2 Wh | ok | docked & grabbed; dock try 1: contacts closed (-48 mm, +5.0 deg); yaw PnP 139 -> 141 (true 134) |
| s4a_backwards_day | PASS | PASS | yes | 496 s | 6.5 Wh | ok | docked & grabbed; yaw PnP -75 -> -79 (true -76); yaw PnP -159 -> -171 (true -165); yaw PnP -173 -> -173 (true -169); yaw PnP 73 -> 88 (true 86) |
| s4a_backwards_night | PASS | PASS | yes | 551 s | 8.5 Wh | ok | docked & grabbed; yaw PnP -62 -> -62 (true -66); yaw PnP 23 -> 29 (true 30); yaw PnP 103 -> 120 (true 121); yaw PnP 139 -> 122 (true 121) |
| s4b_sideways | PASS | PASS | yes | 249 s | 2.7 Wh | ok | docked & grabbed; yaw PnP -160 -> -165 (true -166) |
| s4c_in_hedge | ALERT | ALERT | yes | 222 s | 2.4 Wh | ok | unrecoverable -> alert, home; yaw PnP -177 -> 168 (true 169) |
| s4d1_moved_mouth | ALERT | ALERT | **NO** | 299 s | 3.1 Wh | ok | no tag -> alert, home; yaw PnP 111 -> 121 (true 124) |
| s4d2_moved_road | ALERT | ALERT | yes | 194 s | 1.8 Wh | ok | bin not found -> alert, home |
| s4e_tipped_night | ALERT | ALERT | yes | 200 s | 2.4 Wh | ok | tipped bin -> alert, home |
| s4f_in_road | ALERT | ALERT | yes | 169 s | 1.6 Wh | ok | bin outside geofence -> alert, home |
| s4g_neighbour_night | ALERT | PASS | yes | 226 s | 2.8 Wh | ok | docked & grabbed; yaw PnP 73 -> 73 (true 94) |
| s4h_car_block | ALERT | ALERT | yes | 190 s | 1.8 Wh | ok | blocked by parked car -> alert, home |
| s5_person_dog | PASS | PASS | yes | 249 s | 4.1 Wh | ok | completed |
| s6_branch | PASS | PASS | yes | 180 s | 2.8 Wh | ok | completed |
| s7_rtk_dropout | ALERT | ALERT | yes | 335 s | 4.6 Wh | ok | no fix > 8 m: stopped safely + alert |
| s8a_crash_tow_nofs | - | FAIL | yes | 110 s | 1.3 Wh | ok | tug DID NOT STOP: 19.9 m driven in 40 s after the companion crash (mode AUTO); crash in AUTO_DOWN_TOW: HOLD never s, stopped - s / - m, 19.85 m in 40 s |
| s8b_crash_tow_fs | - | PASS | yes | 110 s | 0.6 Wh | ok | tug stopped 4.1 s / 1.34 m after the companion crash (mode HOLD); crash in AUTO_DOWN_TOW: HOLD 2.05 s, stopped 4.09 s / 1.34 m, 1.35 m in 40 s |
| s8c_crash_dock | - | PASS | yes | 131 s | 0.8 Wh | ok | tug stopped 2.1 s / 0.35 m after the companion crash (mode HOLD); crash in DOCK_REVERSE: HOLD 2.21 s, stopped 2.09 s / 0.35 m, 0.36 m in 40 s |
| s9_dock_charge | - | PASS | yes | 148 s | 1.8 Wh | ok | completed; dock try 1: contacts closed (-30 mm, +3.9 deg) |

Night drop s1n: lighting used 6.7 Wh of 42.3 Wh for the whole cycle (16 %).

### 6.2 Noise-seed sweeps (the two cases the handover said were mis-handled)

Run on G1 code before the last two docking tweaks (close-in tag cut-off, house re-dock); neither touches these bin-recovery paths. 4g: 3 of 4 seeds pick up (was ALERT). 4d-mouth: 2 of 4 pick up; yaw is now right, the failures are recovery manoeuvres at the open mouth.

| Run | Result | Outcome |
|---|---|---|
| s4d1_moved_mouth_seed11 | alert | no tag -> alert, home |
| s4d1_moved_mouth_seed23 | pass | docked & grabbed |
| s4d1_moved_mouth_seed42 | pass | docked & grabbed |
| s4d1_moved_mouth_seed7 | alert | no tag -> alert, home |
| s4g_neighbour_night_seed11 | pass | docked & grabbed |
| s4g_neighbour_night_seed23 | pass | docked & grabbed |
| s4g_neighbour_night_seed42 | pass | docked & grabbed |
| s4g_neighbour_night_seed7 | alert | blocked lane -> stopped + alert |

### 6.3 MuJoCo: mast rest stop (grabber K3), 60 mm sharp step, full bin

| run | hook peak in tow (N) | hook p99 in tow (N) | actuator peak at stop (N) |
|---|---|---|---|
| F1__bump60 | 6080 | 2715 | 1040 |
| G1__bump60 | 3564 | 2249 | 2330 |

Reading: with the rest stop the hook/handle peak on the sharp step falls from 6.1 kN to about 3.6 kN (-41 %) and the p99
from 2.7 to 2.2 kN. The actuator figures are NOT yet meaningful for G1: the model preloads the actuator into the stop
instead of modelling the gravity catch, so the actuator shows its 2.5 kN limit while towing. Next: model the catch as a
locked joint and the actuator as unloaded during tow.

---------------------------------------------------------------------------------------------------------------------

## 7. Cost

`revG/bom_revG.py` -> `bom_revG.csv`: 46 lines, **EUR 824-1,613** (EUR 906-1,774 with 10 % contingency).
Review "Rev G lean" base EUR 707-1,335 (its dock line G28 replaced by D1-D6, beacon and stop relay moved to N1/S1),
plus dock EUR 43-132, grabber EUR 23-48, lights EUR 31-57, safety/robustness EUR 20-41. Realistic mid-range build
about EUR 1,100-1,200. Estimates, not quotes.

## 8. Work package G2 - iterate and test (Rev 2.1, 6 Nov 2026)

Loop used: set pass criteria -> simulate -> fix what fails -> re-test everything. Full numbers in `revG/RESULTS_G2.md` (generated by `revG/make_results_g2.py`). All SIMULATION; nothing built.

**Design decisions taken in G2**

| Decision | Why (evidence) |
|---|---|
| **Tug target 86-91 kg: ONE removable ballast plate** (was 4 plates, 105.6 kg) | MuJoCo, 12 % pitch on wet leaves (mu 0.3): 85.7, 91.3, 96.9 and 105.6 kg all climb with the empty bin (0.46 m/s, 5 m) and all stop a FULL bin downhill in 0.19-0.22 m with brakes; hold creep under 4.5 cm. Mass is not the limit on this lane - lifting and carrying the tug is. Keep the plate removable; add it back only if the real lane is steeper or slipperier. |
| **Mast catch = rubber-faced rest stop, ~tc 0.08 s** (not a rigid steel lock) | 60 mm sharp step at 0.5 m/s, full bin: rigid lock hook peak 4.4 kN (7.3 kN at 105.6 kg); soft pad 3.2 kN peak / 2.0 kN p99, and the lowest catch load (1.9 kN). Softer pads (0.12-0.2 s) let the mast swing further and the catch peak rises to 4-5 kN. Pad estimate: ~25 mm, 60 Shore A, 60 x 80 mm face - bench-check. Actuator is unloaded in tow (catch carries ~0.4-0.6 kN steady on 12 %). |
| **Concept CAD exists for Rev G** | `revG/cad/model_revG.py` (CadQuery, builds on the F.1 model): kingpin pivot, lockable battery box + 12 Ah pack, gravity latch pawls + release cam, extended float stops, rubber-faced rest stop + catch, lid finger, head lamps, red markers, rear work lamp + IR ring, rear bump strip, charge contacts + dock magnet on the crossbeam, safety relay + RTC, and the charging dock (2.6 x 1.2 m pad, dummy-wheel stop blocks, contact plates at y = +/-150 mm, tag-20 backboard, lean-to roof, charger box). Outputs: `bin_tug_revG_tow.step`, `bin_tug_revG_docked.step`, `dock_revG.step`, `bin_tug_revG.stl`, `parts_revG.csv`, renders `render_revG_*.png`. Concept level: no fastener detail, no drawings yet. |

![Rev G concept CAD, towing pose](cad/render_revG_tow.png)

![Rev G on the charging dock](cad/render_revG_docked.png)

**Software fixes found by the seed sweeps (all in `sitl/scripts/companion.py` unless noted)**

1. Lidar obstacle HOLD could last forever when noisy returns made a static object look "moving" (s4c seed 23 held 1,400 s). Now re-judged in fresh 8 s windows, hard cap 5 min -> alert.
2. After a lidar-confirmed orbit-nudge the bin's identity is already known: the tug now uses the re-measured lidar pose and skips the second camera look (that look failed at the open mouth).
3. If the pre-dock pose is not reached, the tug backs off and re-plans instead of starting a reverse-dock from the wrong place (that used to burn the one allowed re-dock).
4. Unreadable tag on one face -> try up to two other faces, then one 25 deg oblique look, before the "no tag" alert; "no room" is no longer reported when the real problem is an unread tag.
5. With two bins in view, the lidar outline is re-picked at the tag's position (it used to take the neighbour's outline, then fall back to camera-only yaw).
6. Pinch-zone check ignores identified bins within 0.8 m (was 0.6 m): a neighbour's bin beside ours no longer blocks the tilt for 20 s.
7. After release, the pull-away point is slid toward the lane centre until it is >= 0.3 m inside the geofence (fixes the s1/s1n geofence "breach" at the bell-mouth step, handover R6).
8. `world.py` sim fix: once seated, the bin stays seated until the tug drives forward > 3 cm or yaws > 15 deg off the bin axis (the instantaneous 9 cm proxy flickered off while the tug coasted to a stop, so the grab failed with the seat switch closed).

**Results after G2:** full regression **21 of 21 as expected** (s4d-mouth now picks up; s8a is meant to fail). Robustness sweep, 9 perception/recovery scenarios x 4 noise seeds: **36/36** (was 32/36 before these fixes; s4g neighbour-at-night 1/4 -> 4/4, s4d-mouth 3/4 -> 4/4). No geofence breach in any of the 57 runs.

**Still open after G2:** multi-bin evening (tag IDs), weather/ice gate, junction wait point, sleep/RTC wake, charge-current check in `park()`, a release that is refused by the pinch-zone check is not yet handled (it releases anyway after 20 s - must hold and alert), real-world capture tolerance of the G-hook float (MuJoCo sweep not yet run), drawings, wiring diagram.
