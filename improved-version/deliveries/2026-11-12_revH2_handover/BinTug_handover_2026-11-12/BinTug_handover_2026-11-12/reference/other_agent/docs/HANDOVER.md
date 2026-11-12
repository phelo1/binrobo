---
title: "Country Road Bin Robot (Bin Tug) - Project Handover"
subtitle: "Living document - Revision 2.2 (Rev G draft, work packages G1 + G2 + cold-eye review 2), 6 November 2026"
author: "Owner: Brian - prepared with Hark"
geometry: margin=2cm
fontsize: 10pt
colorlinks: true
toc: true
toc-depth: 2
---

# 1. How to use this document

This is the single source of truth for the project. Anyone picking the project up should read sections 2-5 first, then the section for the area they are working on.

**Update rule:** whenever the design changes or a test is completed, add a line to the Revision log (section 14), update the affected section, and bump the document revision (1.0 -> 1.1 for tests/edits, 2.0 for a new design revision). The markdown source is `docs/HANDOVER.md` in the project zip; the PDF is generated from it.

**Status key:** DONE = built and verified (in sim or on bench) - SIM = verified in simulation only - TODO = not started - OPEN = decision needed.

# 2. The job

| Item | Requirement |
|---|---|
| Task | Move a standard 240 L two-wheeled wheelie bin between the house and the collection point at the public road, on a schedule, with nobody present. |
| Route | Brian's private lane, [village] area, [county], Ireland. Map pin 53.000000, -8.000000. Assumed route: OSM ways 0 -> 0 to the public road ([road]), about 635 m (Brian quoted ~500 m - **to confirm**). |
| Terrain | Tarmac/gravel lane, not muddy. Hedgerows both sides, potholes, bumps. DEM: house end 43 m, road end 29 m; average 2.2 % downhill toward the road; steepest ~7.5 % over 25 m (about 135-160 m from the house). Short pitches could be 10-12 % (DEM smooths) - **measure on site**. |
| Collection cycle (Rev 2.0, per [county] bye-laws) | **Not daily and not one bin.** Collections are weekly/fortnightly and Irish households usually have 2-3 bins (black, green, brown; brown may be 120-140 L). **Drop:** between 18:00 on the evening before collection and the collector's earliest time (often 06:00) - in winter this is in the dark either way: dock -> grab FULL bin -> tow DOWN -> release on the pad -> return to dock; repeat per bin (~45 min each). **Collection window:** tug stays DOCKED (lorry turning in the mouth, crew handling). **Pickup:** after the collector's window and before 21:00 on collection day (often dark): dock -> drive down -> find each EMPTY bin by its tag ID however the crew left it -> tow UP -> release -> dock. Lid must be securely closed (lid finger, Rev G). Source: county waste management bye-laws 2018 (cold-eye review 1.5.1-1.5.2). Earlier "morning drop / evening pickup" wording is superseded. |
| Load | Full bin up to ~108 kg (106.9 kg body incl. 96 kg contents + 1.4 kg wheels). Empty bin ~12-15 kg. |
| Speed | 0.5 m/s cruise (~21 min per 635 m leg). |
| Must handle | Bin left backwards, sideways, in the hedge, moved, tipped, next to a neighbour's bin, blocked; people/dogs/cars; RTK dropouts under trees; darkness. |
| Monitoring | 4G link: live status, camera snapshot, alerts to phone. |
| Priority | **Cheapest workable** - not over-engineered. Prices in EUR, estimates. |

# 3. Current design: Rev F.1 "hand-truck" tug

The robot is a separate tug; the bin is **not modified** except for two stick-on ArUco/AprilTag markers (front and back). The tug reverses up to the bin, a crossbeam stops the bin's wheels, a hook catches the handle, and a tilting mast rocks the bin back ~48 deg onto its own wheels like a sack truck. The tug then always tows (bin trails behind), and stands the bin back upright at the destination.

## 3.1 Layout

| Subsystem | Rev F.1 definition |
|---|---|
| Chassis | Steel/alu tray. Drive axle at the front of the rear section; front swivel casters (200 mm), moved 100 mm forward in F.1. |
| Drive | 2WD skid steer, used 24 V wheelchair gearmotors with spring (fail-safe) brakes, ~60 N.m usable each, pneumatic 12-14 in wheels. 4WD tested - **no benefit** (casters carry little load on climbs). |
| Rear frame | Yaws on a 250 mm turntable bearing whose kingpin is on the drive axle (TX = 670 mm ahead of the bin axle). Carries: wheel-stop crossbeam (32 mm tube + rubber rollers at bin-wheel tread height), funnel/docking arms, anti-tip rollers (100 mm PU, **100 mm** ground clearance in F.1, ~0.88 m behind axle), mast hinge, tilt actuator. Yaw lock solenoid pin (engaged for docking and tipping) + AS5600 magnetic angle sensor. |
| Mast | Hinged at PX = 260 / PZ = 300 mm (bin frame). Rocked 0 -> ~70 deg by one 2,500 N / 450 mm self-locking linear actuator; bin tilt 48 deg. |
| Hook | Floating carriage on mast rails with return spring (takes +/-30 mm docking error); ramped lip snaps over handle bar; rubber bush (F.1) cuts shock; seat + latch switches. |
| Ballast | 4 steel plates, moved forward to +0.70 m (F.1). Total tug ~105-106 kg. **Mass cannot be reduced**: 101, 97 and 86 kg variants stalled on 20 % wet grass. |
| Sensors | LD06 360 deg lidar (low, front bumper) - bumper switch - RTK GNSS (LC29H or ZED-F9P) with own base at the house via LoRa/NTRIP - IMU (tilt) - wheel odometry - hitch angle - rear camera for ArUco docking (+ IR/LED illuminator and retro-reflective tags for night - see 6.3). |
| Compute | ArduPilot Rover on an H743/F405 flight controller (navigation, avoidance, failsafes). Pi Zero 2 W companion (scheduler, docking/recovery state machine, camera, 4G, alerts). |
| Comms | 4G USB stick + Tailscale; mavlink-router; MediaMTX video; ntfy push alerts. LoRa for RTK corrections. |
| Power | 24 V LiFePO4 pack (size per section 8 once the SITL energy figure is in). Charges at the dock. |
| Firmware rules | Closed-loop heading (P controller) when towing; **hitch angle capped at 60 deg** (never spin in place with a bin); soft-stop ramps; e-stop = spring brakes. |

## 3.1a Rev G changes on top of F.1 (draft - full definition in `revG/REVG_DESIGN.md`)

| Area | Rev G change | Status |
|---|---|---|
| Charging dock | Dock is a "fake bin": tug reverses onto it with the same funnel/crossbeam/camera (dock tag ID 20), yaw lock OFF so the funnel lines up the rear frame (+/-150 mm, +/-15 deg capture). Two sprung brass contacts on the crossbeam meet plates on the dock's dummy-wheel blocks. Plates dead until the tug is detected; SELV 29.2 V 5 A charger; charge only >= +3 deg C. | SIM (s9 + every full cycle ends on the dock) |
| Grabber | Twin hooks at +/-190 mm; carriage float +/-60 mm vertical / +/-40 mm lateral; gravity latch pawls with mechanical release cam, two latch switches; **mast rest stop + gravity catch** at the tow angle; lid hold-down finger; actuator current sensing; rod-down booted actuator; 3 s pre-motion warning + 1.5 m clear zone. | Rest stop SIM (hook peak 6.1 -> 3.6 kN); rest DESIGN |
| Night lights | Amber beacon (wired to the brake-release circuit), 2 x 3 W warm-white dipped head lamps, red markers at mast top + rear frame, 850 nm IR at the rear camera, 3 W rear work lamp, reflective tape; Pi-controlled by sun elevation + ambient sensor. | SIM (state machine + energy) |
| Safety | Hard-wired NC stop loop (E-stop, front and rear bump strips, tilt switch) -> safety relay -> motor-driver enable + brake coils + beacon. Companion 1 Hz heartbeat + firmware GCS failsafe (Hold). Hardware param file with arming/EKF checks on. | Failsafe SIM PASS (s8b/s8c); wiring DESIGN |
| Software | Lidar overrules camera for bin yaw (face-toward-camera rule, close lidar re-scan, L-shape fit); dock routine; re-dock once at the house; ignore close-in tag reads; lights; pre-motion check. | SIM |
| Cost | `revG/bom_revG.py`: EUR 824-1,613 (906-1,774 with 10 %); realistic ~EUR 1,100-1,200. | estimate |

## 3.2 Why this design (decision history)

| Rev | Concept | Outcome |
|---|---|---|
| A | Small base with "bin jack" fork lifting the bin's front lip | Carries too much bin weight; docking hard. Fallback only. |
| B | Drive kit fitted to the bin's own wheels | **Rejected** - lorry inverts the bin; one kit per bin; ownership rules; cannot recover a rotated bin. |
| C | Tug + bolt-on hitch pin on the bin | Cheaper, but needs a fitting bolted to the bin. Kept as an option if the council allows it. |
| D | Brian's idea: tug grabs handle, tilts and tows | Lead concept; CAD + load checks. |
| E | Weather-proofed D (cassette battery, sealed pod, latching hook) | Sim showed pulling the handle **rolls** the bin instead of tipping it. Superseded. |
| F | Hand-truck: wheel-stop crossbeam + hinged mast + yaw rear frame | Tips and tows in every test; issues on steps/climbs/turning. |
| F.1 | Tuned F (ballast/casters forward, rollers raised, hook bush, soft stop, closed-loop steering, 60 deg cap) | Best of 15 variants. Basis of G. |
| **G (draft)** | F.1 + cold-eye review fixes + charging dock + G-hook grabber + night lights + hard-wired safety chain | **Current, work package G1 done in simulation.** |

# 4. Cost estimate (EUR, itemised Rev F.1, Nov 2026)

Rough estimates incl. typical VAT/shipping on AliExpress-type orders; not live quotes. Budget = used wheelchair motors and wheels, scrap ballast, cheapest sensible new electronics. Safety parts (E-stop, fuses, brakes, battery) always new.

| # | Area | Item | Qty | Budget | All new |
|--|------|------------------------------|---|-------|-------|
| 1 | Structure | Laser-cut + bent steel parts (chassis tray, rear frame plates, brackets), galvanised | 1 set | EUR 110-200 | EUR 140-240 |
| 2 | Structure | Steel RHS/tube (spine, drop leg, wheel-stop bar, funnel arms, mast rails, sensor post) | ~6 m | EUR 25-45 | EUR 35-60 |
| 3 | Structure | Aluminium top deck + battery hatch lid (3 mm) | 1 | EUR 20-35 | EUR 30-50 |
| 4 | Drive | 24 V wheelchair gearmotors with spring brakes | pair | EUR 60-110 | EUR 200-320 |
| 5 | Drive | 13 in knobbly pneumatic wheels + taper-lock hubs | 2 | EUR 20-45 | EUR 45-80 |
| 6 | Drive | 200 mm pneumatic swivel casters | 2 | EUR 20-35 | EUR 25-45 |
| 7 | Drive | Dual 30 A motor driver + brake relay + contactor | 1 | EUR 20-55 | EUR 45-90 |
| 8 | Hitch & grabber | 250 mm yaw turntable bearing, kingpin + bronze bush | 1 | EUR 15-30 | EUR 20-40 |
| 9 | Hitch & grabber | Yaw lock solenoid pin + AS5600 encoder + IMU | 1 | EUR 12-25 | EUR 15-30 |
| 10 | Hitch & grabber | Tilt actuator 12 V, 2,500 N, 450 mm, IP66, self-locking | 1 | EUR 55-95 | EUR 80-140 |
| 11 | Hitch & grabber | Floating hook carriage: UHMW pads, return springs, rubber hook bush, soft stop | 1 | EUR 20-35 | EUR 25-45 |
| 12 | Hitch & grabber | Anti-tip rollers 100 mm PU + stop rollers + brackets | 4 | EUR 15-30 | EUR 20-40 |
| 13 | Hitch & grabber | Sealed switches IP67 (seat, latch, wheel-contact, bumper) | 6-8 | EUR 15-25 | EUR 20-35 |
| 14 | Power | 24 V 20 Ah LiFePO4 + BMS + charger | 1 | EUR 100-160 | EUR 140-220 |
| 15 | Power | IP67 battery cassette, hatch hinge, 2 draw latches, EPDM gasket | 1 | EUR 30-55 | EUR 40-70 |
| 16 | Power | IP67 50 A battery connector pair + IP67 charge port | 1 | EUR 15-30 | EUR 20-40 |
| 17 | Power | Ballast: 4 x 10 mm steel plates (~22 kg) + forward bracket | 4 | EUR 5-35 | EUR 30-60 |
| 18 | Navigation | Flight controller F405/H743 (ArduPilot Rover) | 1 | EUR 25-55 | EUR 40-80 |
| 19 | Navigation | RTK GNSS LC29H rover + base station, IP67 antennas | 2 | EUR 85-130 | EUR 110-180 |
| 20 | Navigation | LoRa/SiK telemetry pair (base corrections) | 1 | EUR 25-40 | EUR 30-50 |
| 21 | Sensing | LD06 360 lidar + acrylic weather dome | 1 | EUR 65-95 | EUR 75-110 |
| 22 | Sensing | 2 x TF-Luna drop sensors (IP65 boxes) + EVA foam bumper bar | 1 | EUR 35-50 | EUR 40-65 |
| 23 | Sensing | Pi Zero 2 W + front and rear IP67 cameras + IR LED | 1 | EUR 45-75 | EUR 60-95 |
| 24 | Sensing | AprilTags/ArUco tags, outdoor retro-reflective vinyl (bin front + back) | 2-4 | EUR 5-15 | EUR 10-25 |
| 25 | Comms | 4G modem + SIM + antennas | 1 | EUR 25-60 | EUR 40-80 |
| 26 | Enclosure & wiring | IP67 electronics pod, Gore vent, 6 x IP68 bulkheads, M12 cables | 1 | EUR 45-80 | EUR 60-100 |
| 27 | Enclosure & wiring | DC-DC bucks 24->12/5 V, fuses, IP65 E-stop, beacon, wire, stainless fasteners | - | EUR 45-70 | EUR 55-90 |
| | | **Total** | | **EUR 957-1,715** | **EUR 1,450-2,480** |

Realistic budget build: about EUR 1,200-1,300 (mid-range of the budget column). Add ~10 % contingency for shipping, spares and mistakes. Optional extras: charging contact in the dock (EUR 20-40), rubber kerb ramp per sharp lane step (EUR 15-40), chain 4WD (+EUR 40-70, not recommended), tracks (+EUR 200-450, rejected). Easy savings: drop the LoRa pair and send RTK corrections over 4G/NTRIP (-EUR 25-40); drop TF-Luna drop sensors on this hedged lane (-EUR 25-35).

**Rev G (Rev 2.1):** the itemised Rev G list is `revG/bom_revG.py` -> `revG/bom_revG.csv` (46 lines): **EUR 825-1,615 budget, EUR 907-1,776 with 10 % contingency**, realistic build about EUR 1,100-1,200. It starts from the cold-eye review's "Rev G lean" list (donor powerchair drive, no LoRa, smaller battery with low-temp cut-off, kingpin instead of turntable, no TF-Luna) and adds dock (EUR 43-132), grabber (EUR 23-48), lights (EUR 31-57) and safety/robustness (EUR 20-41) items. The F.1 table above is kept for reference.

Correction (Rev 1.2): earlier headline figures (EUR 700-1,125 used / 950-1,525 new) under-counted; the line-by-line sum above replaces them. Biggest items: wheelchair gearmotors, LiFePO4 battery, steel parts, RTK pair, actuator, lidar.

# 5. Status summary

| Area | Status |
|---|---|
| Concept & CAD (Rev F/F.1 3D model, STEP/STL) | DONE (CAD) |
| Rev F.1 drawing set (2D sheets, flat patterns) | TODO - latest full drawing set is Rev E |
| Mechanical physics sim (MuJoCo) | SIM - see section 7 |
| Recovery of awkward bins (mechanics) | SIM - see section 6.2 |
| Real-lane software-in-the-loop (ArduPilot firmware + lane model, day/night, awkward bins) | SIM DONE - 16 scenarios, see section 9 (2 recovery cases still mis-handled) |
| Itemised BOM with links, wiring diagram for F.1 | Rev G BOM DONE (estimates, no live links yet); safety-chain wiring DONE (REVG_DESIGN s.5); full wiring diagram TODO |
| Rev G: charging dock | SIM DONE (dock routine + contact capture); dock CAD TODO |
| Rev G: grabber (G-hook) | DESIGN; rest stop SIM (MuJoCo); latch/float CAD + capture sweep TODO |
| Rev G: night lights | DESIGN + SIM (light states, energy) |
| Rev G: safety layer | Firmware failsafe SIM PASS (Pi crash -> Hold in 2.1 s); hardware stop loop DESIGN |
| Physical prototype | TODO - first test: sandbag-loaded bin + one hook and mast at ~1 m |
| On-site measurements (steepest pitch, bin handle height, wheel size, collection spot, tree cover) | OPEN |

# 6. How it operates

## 6.1 Mission state machine (companion computer)

0. **Always:** 1 Hz MAVLink heartbeat to the flight controller (silence > 1 s -> firmware Hold); lights per REVG_DESIGN s.3.
1. **Wake** on schedule (drop window from 18:00 the evening before; pickup after the collection window, before 21:00), self-test (battery, RTK fix, lidar, brakes, actuator end-stops), send "starting" alert.
2. **Find bin**: drive the mapped route; near the expected spot, lidar fits the bin outline (~0.58 x 0.73 m rectangle) and the camera reads the tag ID (ignores bins with other IDs - neighbour's bin).
3. **Classify pose**: upright/tipped (IMU-free: tag orientation + lidar height profile), which face points where, room around it.
4. **Dock**: align on the handle face, reverse slowly with ArUco guidance to ~1.4 m, then blind final approach on odometry until the wheel-stop and seat switches close. Yaw lock ON.
5. **Grab & tip** (Rev G: 3 s beacon/work-light warning and a 1.5 m clear zone first): actuator tilts mast; hook latch switch confirms; bin to 48 deg (~48 s full, faster empty). Yaw lock OFF.
6. **Tow**: ArduPilot waypoint mission at 0.5 m/s, lidar avoidance, closed-loop heading, hitch <= 60 deg.
7. **Release**: stop on the drop spot, yaw lock ON, stand bin upright, unlatch, drive clear, photo + alert.
8. **Return** to dock (Rev G): reverse onto the charging dock with the rear camera on tag 20, contacts close, check charge current; one retry, then alert "not charging". Charge only >= +3 deg C.

## 6.2 Awkward-bin recovery (decision tree)

1. Bin upright, handle side clear -> dock normally.
2. Handle side blocked but room to drive round (>= ~1.5 m) -> drive round to the handle side.
3. No room to drive round -> **orbit-nudge**: push the feet end with the bumper to rotate the empty bin 90 deg or 180 deg on its wheels (room check + geofence first; the bin rolls ~0.55 m toward its handle per 90 deg).
4. Grab fails -> back off, re-dock **once**.
5. Bin tipped, wedged, in the public road beyond the geofence, or unreachable (car) -> **stop, 4G alert with photo, return home, retry later**.

MuJoCo results: sideways bin 90 deg nudge - latched 64 s. Backwards bin with hedge 1.5 m behind, 180 deg nudge - latched 84 s. Sideways on wet grass - success on 2nd dock (167 s). **Failures:** backwards on wet grass (wedged), hedge only 0.8 m behind (wedged at ~96 deg), pivoting on the feet (bin slid). Tipped bin: detect + alert only (no self-righting).

## 6.3 Night operation

Camera tag detection degrades in darkness. Planned mitigation: IR or white LED illuminator on the rear camera, retro-reflective printed tags, more weight on the lidar outline fit, slower final approach. Day vs night detection ranges are in section 9. **Rev G lighting** (REVG_DESIGN s.3): amber beacon (hard-wired to the brake-release circuit), 2 x 3 W warm-white dipped head lamps, red markers at the mast top and rear frame, 850 nm IR at the rear camera, 3 W rear work lamp for colour alert photos, reflective tape. In the night loaded-drop SIM (s1n) lighting used 6.7 Wh of 42.3 Wh for the whole cycle (16 %); the same cycle by day (s1) is 37.1 Wh. Tag reads closer than 1.8 m at night are ignored (IR saturation) and the last part is blind.

# 7. Mechanical simulation results (MuJoCo 3.17)

Assumptions: 96 kg contents (108.3 kg bin), 0.5 m/s, wet mu 0.45 / dry mu 0.8, rigid tyres, spring brake modelled as 150 N.m wheel hold, open-loop vs closed-loop steering as stated.

| Test | Rev F | Rev F.1 |
|---|---|---|
| Grab/tip cycle, actuator force | ~1.0 kN (2.5 kN 0.5 ms spike at brake clamp) | 1.1 kN |
| 15 % wet climb | 0.44 m/s, rides on anti-tip rollers | 0.44 m/s, casters stay down |
| 20 % wet climb | 0.24 m/s | 0.29 m/s (traction limit - wheels slipping) |
| Downhill e-stop, 20 % | 0.22 m | 0.19 m |
| 100 mm pothole | Pass | Pass |
| True 60 mm sharp step | **Stuck** | Passes harshly (hook 6.1 kN peak, bin yaws ~50 deg) - **fit rubber ramps on known sharp steps** |
| 30 % side slope drift (braked) | 0.26 m | 0.27 m |
| 2.5 m-radius bend | 57 of 92 deg (open loop) | 91 deg in 10.2 s (closed loop) |
| Spin request with bin attached | Hits 70 deg yaw stop | Held to 54 deg |
| 30 kg / empty bin cycle | Pass | Pass |

Correction note: earlier Rev F reports called a 30 mm step a "60 mm bump" (geometry bug); fixed in F.1 study.

Given the real lane (max ~7.5 %, maybe 10-12 % briefly, loaded run downhill), the climb margins above are comfortable; the binding cases are sharp steps, wet-grass recovery and tight hedges.

# 8. Energy & battery

From the SITL full-day run (Rev F.1 mass, 0.5 m/s, real lane grades):

| Item | Value |
|---|---|
| Morning: tow full bin down + empty climb back | 1274 s / 14.4 Wh down, 1271 s / 20.5 Wh up |
| Driving + manoeuvres per day (drop + pickup) | ~73 Wh over ~91 min |
| Standby (Pi, 4G, RTK, 3 W x 24 h) | ~67 Wh |
| Total per day | ~140 Wh = ~37 % of 384 Wh usable (24 V 20 Ah pack) |
| Days per charge with no dock | ~2.7 |

Standby is half the budget: a sleep mode (4G modem + RTK off between jobs) roughly halves daily use. A simple charging contact in the dock is still recommended.

# 9. Real-lane software-in-the-loop (SITL) results

- **Stack:** real ArduPilot Rover 4.6.2 firmware (built from source, aarch64) driving a Python 2.5D world over ArduPilot's JSON SITL interface; companion state machine (companion.py) sends missions, GPS_INPUT and OBSTACLE_DISTANCE over MAVLink. Gazebo could not render on the build machine; on an x86 PC (or WSL2) Gazebo + ardupilot_gazebo is the upgrade for rendered night vision and 3D contact.
- **World:** real OSM lane, EU-DEM terrain, hedgerows, yard and junction mouth (widths assumed), skid-steer tug, trailer bin with 60 deg cap, ray-cast LD06, RTK fixed/float/none zones, rear camera running real OpenCV ArUco.

**Tag detection range (rear camera, bin ArUco tags):**

| Condition | Reliable (>= 90 %) | Occasional |
|---|---|---|
| Day | 1.2 - 4.4 m | to 7.2 m |
| Night (IR LED + retro-reflective tags) | 2.0 - 3.8 m | to 6.2 m |

Tags are lost inside ~1.4 m (day) / ~1.8 m (night, saturation), so the last metre is odometry + funnel + seat switch.

**Scenario results (all on the same final code):**

| Scenario | Result | Key numbers |
|---|---|---|
| 1 Morning drop + empty return | PASS | 45:20 sim, 36.8 Wh |
| 2 Evening pickup (day) | PASS | 46:05, 35.2 Wh |
| 3 Night pickup | PASS | 47:08, 36.3 Wh |
| 4a Backwards bin (day) | PASS | 2 nudges of 88 deg, docked |
| 4a Backwards bin (night) | PASS | 89 deg (3 pushes) then 105 deg, docked |
| 4b Sideways | PASS | docked first try |
| 4c Wedged in hedge | ALERT (correct) | hedge 0.47 m behind bin |
| 4d Moved to junction mouth | ALERT (should pick up) | camera yaw -169 deg vs true 124 deg |
| 4d Moved 12 m along road | ALERT (correct) | outside geofence |
| 4e Tipped (night) | ALERT (correct) | lidar outline 1.00 m long |
| 4f Partly in road | ALERT (correct) | never enters public road |
| 4g Neighbour's bin beside ours (night) | ALERT (should pick up) | tag 10 ignored, but camera pose ~1.2 m off, 2 docks missed |
| 4h Parked car at mouth | ALERT (correct) | 3.9 m vehicle detected |
| 5 Person + dog crossing | PASS | stopped 0.82 / 0.97 m short, resumed |
| 6 Branch on lane | PASS | 0.32 m detour inside hedges |
| 7 RTK dropout under trees | SAFE STOP (correct) | 5.3 m gap bridged (0.62 m error); longer gap: 8 m + 60 s hold, stop, alert |

No run left the geofence. 4d-mouth and 4g passed on earlier code revisions, so they vary with camera noise.

**Design findings:**
- Bin yaw from the camera (PnP) can be badly wrong; lidar outline must overrule it when they disagree (current gate only overrides within 30 deg / 0.7 m). Next fix.
- ArduPilot simple avoidance stalls on hedges and BendyRuler jack-knifes the bin at bends: both disabled; companion handles stops/detours.
- RC deadzone (30 us) swallowed small U-turn steering commands; geofence abort added. PILOT_STEER_TYPE 3 needed for correct reversing.
- Orbit-nudge must continue until ~90 deg is measured (up to 3 pushes), stop on contact loss, and keep push points 0.8 m inside the fence.
- Dense waypoints needed at the hairpin by the house.

**Approximations:** ARMING_CHECK 0; flat-shaded camera; idealised funnel and nudge models; towed-bin collisions not modelled; lane width / yard / bell-mouth assumed, not surveyed; 4G alert = log + saved photo.

**Rev G work package G2 (Rev 2.1):** after 8 fixes found by noise-seed sweeps, the 21-scenario regression is 21/21 as expected (4d-mouth now picks up) and a 36-run robustness sweep (9 perception/recovery scenarios x seeds 7/11/23/42) is 36/36 with no geofence breach; details `revG/RESULTS_G2.md`, REVG_DESIGN s.8.

**Rev G SITL work package G1 (Rev 2.0):** 21 scenarios (the 16 above + s1n night loaded drop, s8a/s8b/s8c companion-crash tests, s9 charging dock), all rerun on the final G1 code: 20 of 21 behave as expected (s8a is meant to fail - it shows the old params), no geofence breach; full table in `revG/RESULTS_G1.md` (also REVG_DESIGN s.6). Headlines: Pi crash mid-tow with the old params -> tug drove on ~20 m in 40 s; with the Rev G failsafe -> firmware Hold 2.05 s, stopped in 1.4 m (s8b); crash while docking -> stopped in 0.35 m (s8c). Every full cycle now ends seated on the charging dock. 4g (neighbour's bin, night) now picks up (3 of 4 noise seeds); 4d-mouth gets the bin yaw right (121 vs true 124 deg, was 45 deg off) and picks up in 2 of 4 seeds, but still alerts in the others because the recovery manoeuvres at the open mouth fail, so the drop pad and the narrowed recovery scope (review 3.4/3.10) remain the real fix.

Deliverables: Bin_Tug_Lane_SITL.mp4 (5:15), Bin_Tug_Lane_SITL_Report.pdf, Bin_Tug_Lane_SITL_files.zip; sources in sitl/.

# 10. Project files

All files are in the project zip `Bin_Robot_Project_Files.zip`:

| Path | Contents |
|---|---|
| `docs/HANDOVER.md`, `.pdf` | This document (edit the .md; regenerate the PDF). |
| `cad/model.py`, `draw.py`, `dxf/`, `*.step/.stl`, RevA PDF/zip | Rev A model and 7-sheet drawings (historical fallback). |
| `cad/revD/` | Rev D CadQuery model, physics checks, 9-sheet drawings, DXF. |
| `cad/revE/` | Rev E model, 16-sheet drawings, mass table, first MuJoCo sims + report. |
| `cad/revF/` | **Rev F** CadQuery model (`model_revF.py`), mass model (`masses.py` -> `mass_revF.json`), MuJoCo builder (`sim_revF.py`), scenarios (`scenarios.py`), test runner (`run_revF.py <group>` -> `results_<group>.json`), renderer (`render_video.py`, `make_videos.py`), report (`report_revF.py`), STEP/STL, videos and PDF. |
| `cad/revF1/` | **Rev F.1** study (`study.py`, `f1_config.json`, `study_table.csv`), recovery sims (`recovery.py`), report (`Bin_Tug_RevF1_Report.pdf`), video (`Bin_Tug_RevF1_Simulations.mp4`), results JSON. |
| `revG/` | **Rev G** (Rev 2.0): `REVG_DESIGN.md` (dock, grabber, lights, safety chain, software changes, results, cost), `RESULTS_G1.md` + `results_G1.json` (generated by `make_results.py`), `bom_revG.py` -> `bom_revG.csv`, `sim/rest_stop_study.py` (MuJoCo rest-stop check, results in `sim/results/`), `baseline_revF1_sitl_out/` (Rev F.1 SITL results for comparison); G2: `RESULTS_G2.md` (from `make_results_g2.py`), `score_robust.py`, `sim/g2_study.py` + `sim/run_g2.sh` (mass + catch study), `cad/model_revG.py` + `cad/render_revG.py` (concept CAD, STEP/STL). |
| `sitl/` (Rev G additions) | `params/bintug_hardware.parm` (draft hardware params), `run_batch.sh`, `regress.sh` (all 21 scenarios on 2 instances), `sweep.sh` (noise seeds via `BT_SEED`, results in `out/sweeps/`). |
| `sitl/` | Lane data (`data/route.json`, `dem_grid.json`, `grades.json`), world model (`scripts/world.py`), ArduPilot binary (`bin/ardurover_aarch64`), params, logs. |

Simulation recordings (`*.pkl`) and `__pycache__` are excluded from the zip to keep it small; rerun the scripts to regenerate.

# 11. How to run the tools

```
# Python deps (any Linux/WSL machine)
pip install cadquery mujoco numpy scipy matplotlib reportlab pymavlink opencv-contrib-python-headless
# ffmpeg must be on PATH for videos

# Rebuild Rev F CAD and mass model
cd cad/revF && python3 model_revF.py && python3 masses.py

# Run a Rev F test group (cycle | climb | estop | terrain | camber | turn)
python3 run_revF.py cycle        # -> results_cycle.json, rec_cycle.pkl

# Rev F.1 parameter study and recovery sims
cd ../revF1 && python3 study.py && python3 recovery.py
python3 make_videos_f1.py 1,2,3   # render chapters; concat with ffmpeg -f concat

# SITL (x86 PC: build ArduPilot Rover yourself)
git clone https://github.com/ArduPilot/ardupilot && cd ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y && ./waf configure --board sitl && ./waf rover
```

# Rev G (Rev 2.0) - all tested on an aarch64 Linux box with the bundled ardurover_aarch64 binary
export PYTHONPATH=/path/to/pylib      # where the pip packages above are installed
cd sitl && ./regress.sh               # all 21 scenarios, ~10 min on 2 cores -> out/<scenario>/result.json
./sweep.sh 0 s4g_neighbour_night 7 11 23 42     # noise-seed sweep -> out/<scenario>_seed<N>/ (move to out/sweeps/)
cd ../revG && python3 bom_revG.py && python3 make_results.py
cd sim && python3 rest_stop_study.py bump60     # MuJoCo F1 vs G1 rest stop
python3 docs/build_pdf.py docs/HANDOVER.md revG/REVG_DESIGN.md   # PDF without LaTeX (pandoc + weasyprint)
# Rev G work package G2 (Rev 2.1)
# Rev 2.2: mass roll-up + shipping modules (estimate) -> revG/cad/mass_revG.json
cd revG/cad && python3 masses_revG.py 1 && cd ../..
SCEN="s4g_neighbour_night s4d1_moved_mouth" ./robust.sh 0 G2e 7 11 23 42   # robustness batch -> out/robust/<tag>/
python3 revG/score_robust.py G2e                        # pass rate per scenario
cd revG/sim && ./run_g2.sh                               # mass x (climb12e, estop12f, hold12f) + catch; CATCH_TC=0.08 python3 g2_study.py M91 bump60c
cd ../cad && python3 model_revG.py 1 && python3 render_revG.py   # Rev G concept CAD (arg = ballast plates)
python3 revG/make_results_g2.py                           # -> revG/RESULTS_G2.md

The rendering is a software CAD-mesh renderer (no GPU/OpenGL needed).

# 12. Open decisions and risks

| # | Item | Owner |
|---|---|---|
| 1 | Confirm the route (pin -> the public road, ~635 m) and the drop/pickup spot and dock location. | Brian |
| 2 | Measure the steepest short pitch, any sharp steps (fit ramps), lane width at pinch points, tree cover. | Brian |
| 3 | Bin details: handle height, wheel diameter, bin ownership (council rules on stickers/fittings), number of bins and rotation. | Brian |
| 4 | Distance from hedge at the collection point - recovery fails with < ~1 m behind the bin. Consider a marked hard-standing pad. | Brian |
| 5 | Safety: unattended robot on a private lane next to a public road - geofence never enters the public road; insurance/liability check. | Brian |
| R1 | Tug mass: G2 sims show 86-91 kg (one removable ballast plate) passes 12 % on wet leaves both ways; 105 kg was not needed. Confirm on the real lane. | - |
| R2 | Sims approximate friction, rigid tyres, brake model, bin CG. Validate physically. | - |
| R3 | Night docking passes in SITL. After G2 all 9 perception/recovery scenarios pass on 4 noise seeds (36/36), including 4d-mouth and 4g neighbour-at-night. Still SIM only: real-camera night test and lidar in rain needed. | - |
| R5 | Rev G dock and grabber now have concept CAD (`revG/cad/`), but no drawings, and are simulated only at the level of the SITL capture model / MuJoCo joint stop. | - |
| R6 | SIM artefacts to remember: tug coasting through a seated bin was fixed in scene.py (bin now pushed by the crossbeam); first grab after seating occasionally fails and the re-dock recovers it; the bell-mouth geofence step is fixed by the G2 pull-away rule; the seat proxy is now sticky once seated (G2). | - |
| R4 | Tipped bin needs a human (alert only). | - |

# 13. Next steps (in order)

**Rev 2.2:** start G3 with the actions in `revG/REVIEW_G2_coldeye.md` s.6 (lean package in CAD + MuJoCo rerun at ~84.5 kg, refused-release hold, crossbeam contact check, spec choices for punctures/contacts/encoders, fastener + harness tables).

Rev G work packages G1 and G2 closed yaw fusion, recovery robustness (36/36 seeded runs), mass target (86-91 kg) and mast-catch type (soft rubber stop) in SIM, and produced concept CAD. Next:

1. **Owner/site (free, from the cold-eye review s.6):** walk and measure the lane (length, steepest pitch, steps, mouth), ask the collector the three questions (bins and sizes, days and earliest time, collection from a pad inside the mouth, stick-on tags OK), photograph where the crew leaves the bins for 4-6 collections, choose the dock spot (power, roof).
2. **G3 drawings + masses:** drawing set from `revG/cad/model_revG.py` (hook/pawl, rest stop, dock frame, contact blocks), mass roll-up of the Rev G CAD (target 86-91 kg with one plate).
3. **G3 sims:** G-hook float capture-tolerance sweep in MuJoCo; SITL: refused release must hold + alert (today it releases after 20 s), multi-bin evening (3 tag IDs; companion treats id < 10 as ours), drop-pad scenario, weather/ice gate, junction wait point, sleep/RTC wake, charge-current check in `park()`.
4. **Full wiring diagram** (power, stop loop, lights MOSFETs, dock controller) and BOM with live links.
5. **Bench tests (review 6.6-6.9):** bin handle pull to 1.5 kN, tip force, lid in wind; Pi + LD06 + camera + IR at night and in rain; donor powerchair motors (brake hold, stall current); plywood rear-frame + dock mock-up, 20 docking trials onto a bin and onto the dock.
6. Build drive base; ArduPilot missions empty on the lane; then empty bin; then full - attended, E-stop in hand, insurer confirmation and neighbours told first.

# 14. Revision log

| Rev | Date | Change |
|---|---|---|
| 1.0 | 2026-11-06 | First handover: Rev F.1 design, costs, MuJoCo results, recovery tree, lane data, SITL in progress, file map. |
| 1.2 | 2026-11-06 | Section 4: itemised Rev F.1 cost breakdown (27 lines); headline cost corrected to EUR 957-1,715 budget / 1,450-2,480 new. |
| 2.0 | 2026-11-06 | **Rev G draft, work package G1.** Cold-eye review incorporated; new s.3.1a. Collection cycle rewritten to the [county] bye-laws (s.2). Charging dock, G-hook grabber, night lights and hard-wired safety chain defined (`revG/REVG_DESIGN.md`). SITL: companion heartbeat + FS_GCS failsafe (Pi crash -> Hold 2.05 s, 1.4 m), lidar-overrules-camera yaw fusion, dock routine, house re-dock, lights + pre-motion check, 5 new scenarios; full 21-scenario regression + seed sweeps (`revG/RESULTS_G1.md`). MuJoCo: mast rest stop cuts the 60 mm step hook peak 6.1 -> 3.6 kN. Rev G BOM EUR 824-1,613. PDF now built with `docs/build_pdf.py`. |
| 2.2 | 2026-11-06 | **Cold-eye review 2** (`revG/REVIEW_G2_coldeye.md`): 26-item FMEA, part-reduction (DFMA) list, manufacture/assembly notes, shipping split, maintenance plan. Two CAD errors fixed: rear bump strip moved off the crossbeam face (bin wheels would trip it at every dock) to the outer rear corners; F.1 tongue latch + seat switches removed (duplicated K1 pawls/K2 switches). New CAD mass roll-up `revG/cad/masses_revG.py`: tug now **94.2 kg with 1 plate** (above the 86-91 kg target); lean package R3-R10 -> ~84.5 kg, 147 -> ~136 parts, every shipping module <= 24 kg. Lean package not yet applied (G3). |
| 2.1 | 2026-11-06 | **Rev G work package G2 (iterate + test).** MuJoCo: tug 86-91 kg passes 12 % / mu 0.3 climb and brake hold -> one removable ballast plate; mast catch = soft rubber-faced stop (hook peak 3.2 kN vs 4.4 kN rigid). Concept CAD for Rev G tug + charging dock (`revG/cad/`). SITL: 8 fixes found by seed sweeps (obstacle-hold timeout, post-nudge known pose, pre-dock re-plan, face retry + oblique look, outline re-pick with two bins, pinch-zone radius, fence-safe pull-away, sticky seat in sim). Regression 21/21 as expected; robustness 36/36 over 4 seeds (`revG/RESULTS_G2.md`). BOM EUR 825-1,615. |
| 1.1 | 2026-11-06 | SITL complete: section 8 energy (~140 Wh/day, 37 % of pack), section 9 detection ranges, 16-scenario table, design findings; R3 and next steps updated. |
