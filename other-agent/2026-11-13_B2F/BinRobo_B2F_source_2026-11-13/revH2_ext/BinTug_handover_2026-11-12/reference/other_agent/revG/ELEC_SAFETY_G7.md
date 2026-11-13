---
title: "BinRobo (Bin Tug) BT-6 Rev G7 - electrical, functional safety and BOM fix pass"
subtitle: "Answers REVIEW_G6_coldeye B4, M5, M6, M9, M10, m3, m5 and the GA Rev B loom pass (sheet X3). Paper design and fetched prices only - nothing is built. 11 Nov 2026."
author: "Prepared with Hark for Brian"
geometry: margin=1.7cm
fontsize: 10pt
colorlinks: true
toc: true
toc-depth: 2
---

# 0. Summary

**Safety architecture (B4).** Three hardware safety functions, all independent of the Pi, the FC and the 4G link:

| SF | function | PLr target | how |
|---|---|---|---|
| SF1 | E-stop -> safe stop (stop category 1) | **PL d** | 2-NC e-stop -> Pilz PNOZ s5 (dual channel, cross-fault detection) -> delayed safety outputs -> Roboteq FDCG3260T certified **STO** (PL e Cat 3) + spring-applied motor brakes released only through the PNOZ delayed relay contacts |
| SF2 | Bumper contact (front bar + 2 rear corners) -> safe stop | **PL d** | sprung bumpers, each with 2 positive-opening safety switches (one per channel), in series with the e-stop into the PNOZ s5 |
| SF3 | Safely limited speed 0.6 m/s (0.3 m/s in the bell-mouth / near people) + standstill | **PL c** (PL d capable) | Pilz PNOZ s30 speed monitor on two inductive wheel sensors; its relay outputs open the PNOZ s5 input loop |

Category 3, dual channel, monitored. The tilt switch, the two hardware watchdogs and the remote supervisory stop sit in the same loop as additional (non-claimed) stop sources. Person detection by lidar/radar/camera stays a **non-safety awareness layer** (PL a/b); no affordable outdoor safety-rated scanner exists for this lane (section 5). The ArduPilot fence and avoidance are turned on as a backstop (section 6). Indicatively every SF reaches its PLr; a SISTEMA run is the first verification step.

**Chosen parts.**

| function | part | price (incl. IE VAT) | source |
|---|---|---|---|
| Drive motors | **peiscooter PEWM-39 pair**: brushed 24 V, 450 W each, 39:1, rated 48 N m, spring brake + hand release | EUR 862 (US$815/pair) + ~EUR 120 air freight | fetched |
| Motor controller + STO | **Roboteq FDCG3260T**: 3 x 40 A cont / 60 A 30 s, encoder inputs, certified STO PL e Cat 3 | EUR 968 (US$915) | fetched |
| Safety relay | **Pilz PNOZ s5 750105** (2+2 relay, 2+2 semiconductor, delay 0.04-300 s) | EUR 358 (EUR 291.40 ex VAT) | fetched |
| Safe speed | **Pilz PNOZ s30 750330** | EUR 814 (EUR 662.06 ex VAT) | excerpt |
| Mast actuator | **Ewellix CAHB-20-F3E**, 24 V, 4,500 N, IP69K/66M, -40..+85 C, manual override, position output, **stroke 405 mm** | about EUR 623 (450 mm variant EUR 617.61 incl. GR VAT) | fetched; 405 mm needs a quote |
| Heading | **Holybro H-RTK Unicore UM982** dual-antenna (moving-baseline yaw), compass off | EUR 274 (US$249.99) | fetched |
| GR-08S | **Landa TU2551 24 V IP65** tubular solenoid (2 pcs) + boot + PWM channel + pawl-up sensor | EUR 35 + 32 | excerpt / est |
| Pack heater | 2 x RS PRO 12 V 15 W silicone mats in series on 24 V, PWM to 15 W, 40 C bimetal cutout | EUR 115 | fetched (RS IE) |

**The LINAK LA36 is not necessary on paper**: the CAHB-20E meets 400+ mm stroke (405 mm fits the 656-1,042 mm pin window), 4,500 N rated (1.8 x the 2,473 N peak), IP66M/69K, -40 C rated operation and has a manual override, for about EUR 436 less. One condition is open: Ewellix states "full performance 0..+40 C" and gives no cold force figure; ask Ewellix for the force at -20 C. If it is below 3.1 kN (1.25 x 2,473 N), buy the LA36 (EUR 1,058.45).

**New all-in total (bom_revG7):** parts **EUR 7,098.77** + shipping and duty **EUR 500.36** = EUR 7,599.13; + risk-weighted contingency EUR 618.95 = **EUR 8,218 all-in** (G6 showed EUR 3,640). The drive (EUR 1,998) and the safety layer (EUR 1,519) are most of the rise. The cost-down list that keeps every capability is worth **about EUR 1,057** (to about EUR 7,100 all-in). A conditional item (SF3 by inherent speed limit) would save another EUR 844. The EUR 1,200 target cannot be met while keeping capability and a PL d safety case.

**GA Rev B loom findings:** all 13 are closed in bom_revG7 and section 11 (GR-08S line/wiring/fuse/driver, feelers wired, PB-01 loom, W109 fuse at source, tilt IMU deleted, USB mic + HUB2, S5, F1 rating, actuator, beacon PCD, yaw stops, radar sealing, Nord-Locks).

# 1. Inputs and method

- Read: `docs/reviews/REVIEW_G6_coldeye.md` (B4, M5, M6, M9, M10, M12, m3, m5, m8, E-1..E-6), `revG/bom_revG6.py/.json/.csv`, `revG/g6parts/G6_PARTS_REPORT.md` (harness, F1 40 A, K1/K2 loop), `revG/RESULTS_G6_mech.md` (actuator window 656-1,042 mm, 2,473 N peak), GA Rev B `work/out/revG6/drawings/src/issues.py`, `crosscheck.json`, `fasteners.json` (sheet X3).
- Every price was fetched (web_fetch) or is a search excerpt or an estimate, as marked per line in `bom_revG7.csv` (status column). Sources are listed in section 15.
- Drive and power-path numbers come from `revG/g7elec/drive_calc_g7.py` -> `drive_calc_g7.json` (light Python, no simulation).
- Standards: EN ISO 12100 (risk assessment), EN ISO 13849-1/-2 (PL), EN ISO 13850 (e-stop), EN ISO 13856-3 (bumpers), ISO 3691-4 (driverless trucks; used as practice guidance, not claimed), IEC 61800-5-2 (STO/SLS definitions).

# 2. Risk assessment (EN ISO 12100, simplified)

**Machine limits.** Unattended 220 kg tug + bin (110 kg tug, 110 kg full 240 L bin), 0.5 m/s on a 633 m private lane 3.6 m wide, slopes to 12 %, 40 mm steps, at night, twice weekly; it stops at a bell-mouth on a public road. Exposed persons: Brian's household, lane co-owners and visitors, children, dogs, cyclists and pedestrians at the mouth, the refuse crew. Foreseeable misuse: children playing with or riding on the tug, pushing it, tampering, theft.

Risk graph per EN ISO 13849-1 Annex A: S1 slight / S2 serious; F1 seldom-short / F2 frequent-long; P1 possible to avoid / P2 scarcely possible.

| # | hazard (life phase) | S | F | P | PLr | risk reduction |
|---|---|---|---|---|---|---|
| H1 | Tug or swinging bin strikes a person at 0.5 m/s (220 kg, ~27 J), crushing against hedge/gate | S2 | F1 | P2 (night, child, unattended) | **d** | SF2 bumpers, SF1 e-stop, SF3 speed, lights/beacon/audio, awareness layer |
| H2 | Over-speed after a controller or software fault (free speed 2.2 m/s, ~530 J) | S2 | F1 | P2 | **d** -> c accepted with SF3 at PL c plus SF1/SF2 at PL d | SF3 PNOZ s30 SLS 0.6 m/s, Roboteq speed limit (non-safety) |
| H3 | Run-away down the 12 % slope (brake or traction loss) | S2 | F1 | P2 | d | spring brakes fail-safe (power-off applied), SF3 standstill/speed monitoring, B1 traction margin |
| H4 | Unexpected start after a stop or reset | S2 | F1 | P1 | c | PNOZ monitored reset; supervised remote reset only with a camera view; 3 s beacon + audio pre-warning |
| H5 | Enters the public road / stops in the mouth | S2 | F1 | P2 | d (road traffic) | geofence inside the road boundary (non-safety backstop) + procedure "never stop in the mouth" + SF3 0.3 m/s zone; **legal check** (section 13) |
| H6 | Pinch/crush at the mast, hooks and kingpin during grab/tilt | S2 | F1 | P1 | c | tilt only when both latch switches + pawl-up sensor agree, SF1 stops the actuator (KM drop), guards on the kingpin |
| H7 | Bin drop / tip during release | S1-S2 | F1 | P1 | b-c | B2 release fixes, wheel-on-ground interlock, HOLD on fault |
| H8 | Battery fire / short (LiFePO4 20 Ah) | S2 | F1 | P1 | - (not a control function) | F1 50 A at the pack, BMS, isolator, fused branches, heater cutout |
| H9 | Electric shock | - | - | - | - | 24 V SELV only; dock mains in an RCD IP66 socket |
| H10 | Theft / tampering / child climbing on | S1-S2 | F1 | P1 | b | lockable hatch, tamper siren, cable lock, seat switch (not a safety function), remote alert |

Residual risks to state in the instructions: night operation near the road, dogs that do not avoid, people deliberately standing in front of the tug.

# 3. Safety functions

| SF | trigger | safe state | reaction time target | PLr | claimed |
|---|---|---|---|---|---|
| SF1 E-stop | e-stop pressed / wire break | drive ramp-down command (instant contacts), then STO + brakes applied + KM open after t_d = 0.5 s (stop category 1) | stop <= 0.15 m from 0.5 m/s with 220 kg | d | Cat 3, PL d |
| SF2 Bumper | any bumper switch opens (25 mm pre-travel) | as SF1 | stop inside the 120 mm foam overtravel + 25 mm pre-travel at 0.5 m/s | d | Cat 3, PL d |
| SF3 SLS + standstill | wheel speed > 0.6 m/s (> 0.3 m/s when the mouth zone input is selected) or one sensor implausible | as SF1 | < 100 ms detection | c | Cat 3 sensors, PL d capable |
| SF4 Supervisory stop (Reg. 2023/1230) | remote stop from the web console over 4G, or link loss | Pi opens a relay in the SF1 loop | link-loss stop already 4.1 s in SITL s8b | - | not claimed (functional, monitored by the GCS failsafe) |

**Stopping check (hand calc).** Decel available on wet leaves mu 0.25 with all 4 wheels braked: ~0.25 g = 2.4 m/s^2. From 0.5 m/s: braking 0.052 m + reaction 0.05 s x 0.5 = 0.025 m + delay before STO (ramp command is instant, brakes after t_d) -> about 0.08-0.10 m, inside the 0.145 m of bumper travel. MuJoCo already showed 0.19-0.26 m with a FULL bin down 12 % (brakes only), so the bumper overtravel must be >= 0.15 m at the rear corners for downhill reversing, or SF3 must hold 0.3 m/s on downhill reverse legs. Verify by the B4 bench test (<= 0.15 m at 0.5 m/s, 220 kg).

# 4. Architecture (Category 3, dual channel, monitored)

```
INPUT LOOP (both channels in series, into PNOZ s5 S12 / S22)
 CH1: ESTOP-NC1 - FRONT-SW1 - REAR-L-SW1 - REAR-R-SW1 - s30(13-14)
      - TILT - WD1 - SUPERVISORY-RELAY-a                  -> S12
 CH2: ESTOP-NC2 - FRONT-SW2 - REAR-L-SW2 - REAR-R-SW2 - s30(23-24)
      - WD2 - SUPERVISORY-RELAY-b                         -> S22
 Reset (S34, monitored): tug button, or remote reset relay
       (Pi, only after a camera check)
 Feedback loop Y1/Y2: KM aux NC (open = KM really open)

PNOZ s5 OUTPUTS
 instant relay 13-14    -> Roboteq DIN "quick stop", ramp 2 m/s^2
 instant relay 23-24    -> Pi input "safety tripped" (diagnostic)
 delayed semicond. Y32  -> Roboteq STO1 \ certified STO PL e Cat 3
 delayed semicond. Y35  -> Roboteq STO2 /  (both low = no torque)
 delayed relay 37-38 (+) and 47-48 (-)
                        -> MOTION POWER, F11 4 A, ~2.6 A:
                           brake coils L+R (spring-applied),
                           KM coil, amber beacon
PNOZ s30: 2 x M12 inductive PNP sensors on 12-tooth hub rings;
          SLS 0.6 m/s, zone input 0.3 m/s; standstill -> Pi
```

**Why this split.** The PNOZ s5 has two delayed *semiconductor* safety outputs (Routeco data: 2 instantaneous + 2 delayed semiconductor, 2 + 2 relay) that drive the two STO inputs directly, and two delayed relay contacts that break both poles of the brake/KM supply. That gives two diverse output channels: STO (electronic, certified) and the spring brakes (mechanical, fail-safe). KM is kept as a third, functional isolation of the motor bus. The K1/K2 Finder pair of G6 is deleted; the G6 BOM had bought only one of them (X3 finding).

**Diagnostics.**

- Cross-fault and short detection on both input channels (PNOZ s5 test pulses); a broken wire = stop.
- Monitored reset: a welded output contact or a stuck reset button blocks the restart.
- Feedback loop Y1/Y2 sees KM (welded contactor -> no restart). Roboteq STO has internal diagnostics and reports STO state on CAN; the Pi logs it and refuses to command motion if STO state and PNOZ state disagree.
- PNOZ s30: plausibility between the two wheel sensors and against the Roboteq encoder speed (Pi cross-check, non-safety); a stuck sensor at standstill is caught when the tug drives and only one sensor pulses.
- Daily automatic test at dock departure: Pi opens the supervisory relay -> checks that STO, brakes and KM drop within t_d + 50 ms, then resets. A bumper cannot test itself unattended, so a monthly manual press test of every bumper switch and the e-stop is in the instructions.
- DC limitation: several devices in series in one loop (ISO/TR 24119 fault masking) -> claim DC low (60 %) on the input subsystem, not medium.

**Indicative PL (to confirm in SISTEMA).**

| subsystem | data (ISO 13849-1 Table C.1 / maker) | MTTFd | DC | result |
|---|---|---|---|---|
| E-stop (2 NC) | B10D 100,000; nop ~ 400/yr (tests + trips) | > 100 y (capped high) | low | Cat 3 |
| Bumper switches (positive opening) | B10D 20 x 10^6 (mechanical position switch, small load); nop ~ 7,300/yr | high | low | Cat 3 |
| Logic PNOZ s5 | maker: PL e / Cat 4 (PFHd from the Pilz data sheet) | - | - | PL e |
| Output 1: Roboteq STO | maker certificate: PL e, Cat 3, SIL 3 | - | - | PL e |
| Output 2: spring brakes via PNOZ relay contacts | brake as well-tried principle; B10D from the motor maker (ask peiscooter) | high (assumed) | low | Cat 3 |

Cat 3 + MTTFd high + DCavg low gives **PL d** by the simplified method (Figure 5), with each subsystem in the order of 10^-7/h (Annex K) and a sum < 10^-6/h. SF3 with the PNOZ s30 (PL e device) and one sensor per wheel plus plausibility reaches PL c; a second sensor per wheel would lift it to PL d (+EUR 30).

**Safety part list (all in bom_revG7):** S5 PNOZ s5, SPD-G7 PNOZ s30, SPD-S7 speed sensors, G6 Roboteq FDCG3260T, S8 2-NC e-stop, BMP-G7 bumpers with 4 positive-opening switches, RST-G7 reset, S4 KM (kept, with aux contact), S13 tilt switch, S7 watchdogs (kept).

# 5. Person detection: what is credible

| option | safety rating | outdoor use | price | verdict |
|---|---|---|---|---|
| LD06/STL-06N lidar + Python (G6) | none | yes | EUR 50 | **awareness only** (PL a). Keep: slows to 0.3 m/s and holds at 2 m. |
| HLK-LD2451 radars (G6) | none | yes | EUR 12 each | awareness only (vehicles at the mouth) |
| SICK nanoScan3 (NANS3-AAAZ30AN1) | Type 3, PL d | indoor product (rain/leaves/fog give false trips) | EUR 1,827 (industry-store.eu) / EUR 2,692 (RS DE) | credible sensor, wrong environment |
| Pilz PSENscan L 3.0 | Type 3, PL d | indoor | EUR 2,466 (variadores.es) to EUR 4,390 list | as above |
| Safety radar (e.g. Inxpect LBK class) | PL d (maker claim) | designed for harsh/outdoor | not verified | the only credible outdoor non-contact safety option; evaluate if ever needed |
| **Tactile bumpers + low speed + SLS (chosen)** | PL d (SF2) | yes | EUR 160 + PNOZ | **credible**: the ISO 3691-4 practice for slow vehicles where the stopping distance fits inside the bumper travel |

So the safety claim rests on contact detection with a speed limit, not on seeing people. The lidar/radar/camera layer reduces how often the bumper is needed, but it is not counted in the PL.

# 6. ArduPilot settings (backstop, not safety-rated)

Add to `bintug_g6.parm` and regenerate `bintug_hardware.parm` from it (review m1/E-5). Names are ArduPilot Rover 4.4+; check each against the firmware build before flashing.

| parameter | value | purpose |
|---|---|---|
| FENCE_ENABLE | 1 | turn the fence on (G6: off) |
| FENCE_TYPE | 4 (polygon) or 6 (polygon + circle) | inclusion polygon = surveyed lane + yard, drawn **inside the public-road boundary** with a 1.5 m margin (F-1 survey) |
| FENCE_ACTION | Hold (Rover value 2; verify) | stop at the fence, do not RTL across the mouth |
| FENCE_MARGIN | 1.0 m | early stop |
| AVOID_ENABLE | 7 (fence + proximity + beacon) | G6 had 0 |
| AVOID_BEHAVE | 1 (stop) | no slide-along near hedges (M7) |
| AVOID_MARGIN | 0.5 m | |
| PRX1_TYPE | the LD06 driver value of the build (16 in 4.4+, verify) | lidar into avoidance |
| GPS1_TYPE | 25 (UnicoreMovingBaselineNMEA) | UM982 |
| EK3_SRC1_YAW | 2 (GPS) | dual-antenna heading |
| EK3_SRC2_YAW | 8 (GSF) + RCx_OPTION 90 / Lua switch on GPS-yaw loss | fallback under canopy |
| COMPASS_ENABLE / COMPASS_USE | 0 / 0 | no compass on the steel tug (M9) |
| GPS_POS1_X/Y/Z | measured antenna 1 offset | lever arm |
| FS_GCS_ENABLE, FS_ACTION, FS_EKF_ACTION | keep G6 values (hold) | s8b stop in 4.1 s |
| WENC_TYPE + WENC_* | if FC pins allow; else Roboteq encoder speed to the Pi | odometry when RTK drops |

# 7. Drive specification (M5) and power path

**Requirement.** 30-39 N m per wheel continuous on 12 % with the 110 kg bin and 110 kg tug (crr 0.05-0.10, review handcalc), x 1.25 margin = 49 N m short-term; >= 45 N m continuous (review); >= 1.0 m/s free speed; spring brakes; repeatable spec (no donor).

**Chosen: peiscooter PEWM-39 pair** (https://www.peipeiscooter.com/products/102, fetched): 24 V brushed, 450 W x 2, 39:1, motor 4,000 rpm, **rated output torque 48 N m**, electromagnetic brake, 22 mm keyed shaft, left + right, US$815/pair. No torque-current curve is published, so the constants below are derived from the rating and must be confirmed on receipt (M5 dyno or 450 N drawbar pull test for 3 min).

| quantity (drive_calc_g7.json) | value |
|---|---|
| derived kt / R | 0.046 N m/A / 0.20 ohm (from 450 W, 4,000 rpm, 24 V, 80 % eff.) |
| output torque at the derived rated current 23.4 A | 36.9 N m (vendor states 48 N m: **conflict to resolve by test**) |
| 30 N m (crr 0.05) at 0.5 m/s | 19.1 A per motor, 178 W el. |
| 39 N m (crr 0.10) at 0.5 m/s | **24.8 A per motor**, 260 W el. |
| 39 x 1.25 = 49 N m | 31.0 A per motor |
| torque at the 40 A/ch controller limit | 62.9 N m per wheel |
| free speed at 29.2 V on the 330 mm wheel | 2.16 m/s (hence SF3) |
| battery current, worst climb | **23.9 A** (incl. 3 A logic) |
| battery peak at ALIM 40 A/ch | **46.8 A** |
| drops | 10 mm2 trunk 0.13 V at peak; 6 mm2 motor run 0.17 V at 24.8 A |

If the dyno shows < 45 N m continuous, the fallback is the same frame with a higher ratio or a 450 W x 2 39:1 pair from another maker with a published curve; the electrical sizing below covers up to 40 A/ch.

**Controller: Roboteq FDCG3260T** (US$915, fetched): 3 x 40 A continuous, 60 A for 30 s, 60 V, encoder inputs, CAN/USB/RS485, certified STO PL e Cat 3 SIL 3. Ch1/Ch2 drive (ALIM 40 A), Ch3 mast actuator (CAHB 8 A at rated load) - KA1/KA2 deleted. The smaller SDCMG3260T (US$715) is 20 A continuous, below the 24.8 A climb current.

**Re-sized power path.**

| item | G6 | G7 | reason |
|---|---|---|---|
| F1 main fuse | 40 A MIDI (BOM S1 said 30 A) | **50 A MIDI slow** at battery + | 24 A climb, 47 A peak; below the 60 A BMS |
| BMS | Daly 8S 60 A | **kept** | 24 A continuous, 47 A peak at the limit (< 30 s) |
| B+ trunk ISO-KM-F1-controller | 6 mm2 | **10 mm2 silicone** | 0.13 V at 47 A |
| motor runs | paired 1.5 mm2 in DT12 pins (13 A/pin) | **6 mm2 + Deutsch DTHD size 8 (60 A)** | X3 motor-pin issue; 24.8 A continuous |
| F2 25 A motor fuses | yes | **deleted** | controller current limit + F1 |
| KM contactor | 100 A | kept, aux contact into PNOZ feedback | |
| MOTION POWER (brakes + KM + beacon) | K1/K2 contacts, F11 4 A | PNOZ s5 delayed contacts, F11 4 A | ~2.6 A |
| W109 1.5 mm2 | F1 only until FL1 in PB-01 | **FL1 10 A at ISO-2** | X3 |
| GR-08S | none | **F14 2 A** on 24 V SIG + MOSFET PWM channel | X3 |

# 8. Mast actuator (M6)

Window from RESULTS_G6_mech: pin-to-pin 656-1,042 mm, peak 2,473 N, -20 C operation required ([nearby town] absolute minimum -11.4 C), IP66, manual override for lowering a loaded mast with a dead battery.

| candidate | force | temp | IP | manual override | fits window | price | verdict |
|---|---|---|---|---|---|---|---|
| LINAK LA36 12H 400 | 6,800 N (3,400 N at -30 C) | -30..+85 | 66/69K | hand crank | yes (BID 650/1,050) | EUR 1,058.45 | works; expensive |
| **Ewellix CAHB-20-F3E, S 405, position output** | **4,500 N rated / 6,300 N clutch** | **-40..+85** (full perf. 0..40) | **69K/66M** | **yes (F = 24 V with manual override)** | **RL 246+405 = 651 / EL 1,056** | ~EUR 623 | **chosen, if the -20 C force >= 3.1 kN is confirmed** |
| Ewellix CAHB-20E without position output | 4,500 N | as above | as above | yes | S 420-445 (RL 211+S) | similar | backup geometry |
| Thomson Electrak HD 48 V | 16 kN | -40..+85 | 69K | yes | - | US$1,439 | dearer than LA36 |
| TiMOTION TA23 | 4,000 N pull / 5,000 push | **+5..+45 C** | 66W | release only | - | EUR 236 ex VAT | **fails -20 C** |
| ELA 0041941-1 (G6 BOM) | 2,500 N | -20..+60 | 67 | no | 630/1,080 | EUR 142 | **rejected** (SF 1.0) |

Ewellix data from catalogue IL-06022-2 (Jan 2023) pp.16-19: 24 V 4,500 N version 13 mm/s no load / 11 mm/s at rated load, 8 A at rated load, 10.4 A clutch, 20 % duty (85 s on), retracted length 246 + S with position output. Order code pattern from the priced item CAHB-20-F3E-4500696-BBA0PT-000 (450 mm, RL 696); ask for the 405 mm stroke code. Adapt the rear/front eyes to the D12 clevis pins with bushes (EUR 10 allowance). Speed 11 mm/s vs 13 mm/s for the LA36: tilt time +18 %.

# 9. Heading without a compass (M9)

- **Holybro H-RTK Unicore UM982** (US$249.99, https://holybro.com/products/h-rtk-unicore-um982): dual-antenna moving-baseline yaw from one module, 0.1 deg per 1 m baseline, RTK rover, works without RTCM for heading; ArduPilot 4.4+ support. Antennas >= 0.6 m apart on the fixed sensor post and the rear frame (heading error ~0.17 deg at 0.6 m), both >= 0.3 m from the SIM7600 antenna (m8).
- It replaces the LC29HDA rover; the LC29HBS base and NTRIP server stay. The base is L1/L5 only: bench-check that the UM982 fixes with L1/L5 MSM corrections before the lane walk.
- Fallback under canopy: GSF yaw (EK3_SRC2_YAW 8) + wheel odometry + the lidar corridor (already the lateral primary). Verify heading error < 3 deg P95 with motors at full current (review M9).

# 10. GR-08S solenoid sealed, and the pack heater

**GR-08S.** The CAD r7 part was a 12 V open-frame 10 mm pull solenoid with no BOM line, wires, fuse or driver. G7: **Landa TU2551 24 V IP65 tubular push-pull, 0-10 mm, D25 x 51 mm** (US$15, MOQ 2; one spare), with a nitrile boot on the plunger. Driven from one channel of the L6 MOSFET board: 100 % for 0.2 s then 30 % PWM hold, flyback diode, **new fuse F14 2 A**. A new **M8 PNP pawl-up sensor** joins the pre-tip and pre-release interlocks (review M10: no drop if the pawl sticks; HOLD instead). Wiring on a new 7-core PUR 0.5 mm2 cable **T3b** through the mast hinge (solenoid +/-, pawl-up, 2 spare) because T3's two spare cores now carry the feelers. Update CAD (24 V envelope D25 x 51) and the E2 sheet. Bench test from M10: 50 wet cycles at -5 C after an overnight freeze, lifting with a 50 N tip load present. Cost-down CD4 (GR-07 cam lobe) removes the solenoid altogether.

**Pack heater (m3 / E-3).** 2 x RS PRO 245-562 (12 V, 15 W, 75 x 200 mm, adhesive) in series on 24 V = 30 W peak, PWM'd by the dock controller to the 15 W mean the scene model uses; a KSD9700 40 C NC bimetal in series as a hardware over-temperature cutout; heater powered only from the dock supply (charger 5 A has the headroom); charging still gated by the pack NTC >= +3 C. Pass (E-3): -5 C soak overnight -> full by 06:00.

# 11. GA Rev B loom pass (sheet X3) - each finding and its fix

| # | finding | fix in G7 | BOM line |
|---|---|---|---|
| 1 | GR-08S has no BOM line, wiring, fuse or driver channel | 24 V IP65 TU2551 + boot; L6 MOSFET PWM channel; F14 2 A; T3b 7-core PUR through the hinge; pawl-up sensor | GR-08S, GR-08D |
| 2 | B-GR-62 feelers (M8) unwired, IND-OPEN EUR 0 | 2 x M8 PNP IP67 priced; T3-12/13 = FEELER L/R, +24 V / 0 V from MJ-01 busbars | IND-OPEN (closed, EUR 24) |
| 3 | KC, KA1, KA2 in PB-01 fed from the pod, no pod-PB-01 loom | KA1/KA2 deleted (actuator on Roboteq ch3); new pod-PB-01 loom 6 x 0.5 mm2 LiYCY + DT06-6S for KC coil and INA226 I2C | S6, PC-G7 |
| 4 | W109 1.5 mm2 protected only by F1 until FL1 | FL1 10 A moved to ISO-2 in a sealed inline holder | FL1-G7 |
| 5 | Tilt IMU unwired | Crossbar IMU deleted; mast angle from the CAHB position output + AS5600; tug pitch from the FC | G8 |
| 6 | Mic: BOM I2S, harness USB + HUB2 not in BOM | USB mic at the mast top + 2-port HUB2 added; I2S mic deleted | AU-G6 |
| 7 | S5 buys 1 safety relay, 2 needed | K1 + K2 replaced by one PNOZ s5 (internally redundant); fallback without PL d upgrade: 2 x Finder 55.34 + 94.04 | S5 |
| 8 | S1 says 30 A, harness 40 A | F1 now 50 A for the G7 drive; BOM, harness note and W1 updated to 50 A | S1 |
| 9 | BOM actuator ELA, CAD LA36 | One part in both: CAHB-20-F3E S405 (LA36 if the cold force fails); CAD envelope, clevis bushes and actuator_fit re-run | G10 |
| 10 | Beacon vs CAD bolt circle | Keep LAP MLPB050; SN-59 redrilled to the LAP 3-hole PCD 110 (was M10 PCD 100), CAD envelope D120 x 40; confirm PCD on the LAP drawing first | L3 |
| 11 | YS-01/02 yaw stops no BOM line | Added (UHMW blocks + M10 A4 pins + sleeves); add drawings to Drawings_G6 | YS-G7 |
| 12 | Radar boards behind printed covers only | Sealed factory-soldered pigtail, conformal coat, 3 mm drain hole, M8 IP67 connector per radar | RD-G6 |
| 13 | ~49 M8 joints vs 24 Nord-Lock pairs | 50 pairs | F1 |

Also closed on the way (same X3 list): red markers 2 pairs (L2); motor-pin overload (PWR-G7). Still open from X3 and not electrical-BOM: T3 hinge loop length (mechanical routing: clips >= 350 mm from the pin), PB-02 battery cradle redraw, H08/H09 strain relief, S2 cut length, small-signal wire list, junction boxes in CAD.

# 12. BOM G7 and cost

Files: `revG/bom_revG7.py` (imports bom_revG6, overrides + new lines), `revG/bom_revG7.csv`, `revG/bom_revG7.json`. Every G7 line carries a `fix_ref` (review item or X3) and a status.

| | G6 | G7 |
|---|---|---|
| parts (incl. IE VAT) | 3,099.31 | **7,098.77** |
| shipping + duty | 181.59 | **500.36** |
| subtotal | 3,280.90 | **7,599.13** |
| risk-weighted contingency (5 % fetched / 8 % excerpt / 12 % est / 15 % local / 10 % logistics) | 359.33 | **618.95** |
| **all-in** | 3,640.23 | **8,218.08** |
| with LA36 instead of CAHB | - | +435.82 |

G7 by area: Drive 1,998; Safety & power distribution 1,519; Hitch & grabber 890; Structure 735; Enclosure & wiring 444; Navigation 357; Power 286; Comms 273; Sensing 258; Dock 213; Lights 125.

**Main changes vs G6:** donor chair, donor casters and sealant deleted (-368); PEWM-39 pair + wheels + casters + power path (+1,057); Roboteq instead of MDDS30 (+885); PNOZ s5 (+340), PNOZ s30 + sensors (+844), bumpers/e-stop/reset (+190); CAHB actuator (+481 vs the rejected ELA; -436 vs LA36); UM982 (+274, rover -30); GR-08S + driver (+67); heater (+115); X3 items (+~150). Logistics: Roboteq US, PEWM air freight, Holybro, Papadopoulos GR, Pilz DE, RS IE, Landa; duty on motors 2.7 %, controller ~2.1 %, GNSS ~3.7 % (rates estimated) + VAT on duty.

**Cost-down list (keeps every capability; not applied in the totals):**

| id | change | EUR | note |
|---|---|---|---|
| CD1 | Keep MDDS30 + 2 DC contactors with mirror contacts in the motor supply, monitored by the PNOZ feedback loop; actuator back on 2 relays | -729 | Cat 3 / PL d still reachable; loses certified STO and hardware current limiting (do it in firmware) |
| CD2 | Tray CH-01/CH-14 in 2 mm Z275 instead of 5083 | -90 | team figure; mass is useful ballast |
| CD3 | IP66 PA/marine horn instead of Visaton DK 97 | -70 | unverified |
| CD4 | GR-08S replaced by a 2nd GR-07 cam lobe | -38 | review M10 option; re-time the cam |
| CD5 | Second-brand PL e delay safety relay instead of PNOZ s5 | -100 | unverified; must keep delayed semiconductor outputs |
| CD6 | UM982 from an EU stockist on offer / ArduSimple board | -30 | market dependent |
| **sum CD1-CD6** | | **-1,057** | **all-in about EUR 7,100** |
| CD8 (conditional) | SF3 by inherent speed limit (gearmotor free speed <= 0.8 m/s with >= 45 N m) -> delete PNOZ s30 + sensors | -844 | needs a verified slower gearmotor and an ISO 12100 sign-off |
| CD7 (conditional) | Drop the F405 FC if A-7 chooses option (ii) | -35 | FC hosts the EKF/UM982 yaw and the fence in the recommended stack |

# 13. Legal and CE route (my reading, **not legal advice**)

- **Regulation (EU) 2023/1230** applies from 20 Jan 2027. A machine built for own use and put into service by its maker is in scope, so BinRobo needs the EHSR checklist, a technical file (risk assessment above, SISTEMA report, wiring, test records, instructions), an EU declaration of conformity and CE marking before service after that date.
- Route: internal production control (module A) is expected to be open because no safety function uses machine learning and the safety components are bought certified devices; the Annex I Part A categories (third-party) should be checked against the final design, in particular any "safety component with fully or partially self-evolving behaviour" - the Python/lidar layer must stay out of every safety function.
- New EHSR for autonomous mobile machinery: supervisory function able to stop/start remotely (SF4 via 4G console), operation only inside the defined area (fence + survey), protection against corruption (WireGuard, signed updates, no open ports), and the ergonomic/visibility requirements for warning (beacon R65, lights, audio).
- Radio parts: buy only CE/RED-marked modules (SIM7600G-H HAT, UM982, radars, Wi-Fi/BT of the Radxa).
- Public road at the bell-mouth: have the road authority boundary map; the tug must never stop in or cross the boundary (Road Traffic Acts, insurance).
- GDPR: cameras seeing the public road leave the household exemption (CJEU C-212/13 Rynes): signage, retention 7-30 days, masking/blur in shared clips.
- Insurance and lane co-owners: written notice to the home insurer (public liability) and written consent of co-owners.

# 14. Verification plan and open items

| test | pass |
|---|---|
| SISTEMA for SF1, SF2, SF3 with maker PFHd/B10D | SF1/SF2 PL d, SF3 PL c |
| Bumper trip at 0.5 m/s, 220 kg, flat and 12 % down | stop <= 0.15 m; no contact force above the limits adopted |
| Fault injection: open/short each channel, weld KM aux (jumper), stuck reset, one speed sensor removed | stop or no restart in every case |
| STO timing | STO + brakes + KM within t_d + 50 ms of a trip |
| 1,000 trip cycles | no degradation |
| PEWM-39 dyno / pull | >= 45 N m continuous at <= 30 A; 450 N drawbar 3 min without F1/BMS trip; brake hold on 12 % with 220 kg |
| Voltage drop at 2 x 25 A | < 3 % battery to controller |
| CAHB cold force (Ewellix statement or freezer test) | >= 3.1 kN at -20 C, else LA36 |
| UM982 heading with motors at full current, under hedges | < 3 deg P95; GSF fallback engages |
| GR-08S wet freeze test | 50/50 lifts at -5 C with 50 N tip load; pawl-stuck -> HOLD |
| Heater -5 C soak | full charge by 06:00 |

**Open / assumptions.** PEWM-39 torque curve (vendor 48 N m vs derived ~37 N m at rated current) - test on receipt. CAHB 405 mm stroke code, price and cold force - quote. PNOZ s30 price is an excerpt. Bumper switches, wheels, casters, looms are estimates. The B1 load-transfer question is untouched by this pass and still decides whether the 30-39 N m demand holds. Person detection is deliberately not claimed.

# 15. Sources (fetched 11 Nov 2026 unless marked)

- Review: `docs/reviews/REVIEW_G6_coldeye.md`; GA Rev B: `work/out/revG6/drawings/src/issues.py`, `crosscheck.json`, `fasteners.json`.
- Roboteq FDCG3260T US$915: https://www.roboteq.com/products/products-brushed-dc-motor-controllers/fdcg3260t-328-detail ; SDCMG3260T US$715: https://www.roboteq.com/products/products-brushed-dc-motor-controllers/sdcmg3260t-detail
- PEWM-39 pair US$815 and specs: https://www.peipeiscooter.com/products/102 , https://www.peipeiscooter.com/categories/100020
- Pilz PNOZ s5 EUR 291.40 ex VAT: https://www.automation24.com/safety-relay-pilz-750105-pnoz-s5-24vdc-2-n-o-2-n-o-t ; semiconductor outputs: https://routeco.com/en-gb/shop/safety/compact-safety-relays/750105 (excerpt)
- Pilz PNOZ s30 EUR 787.85 incl. DE VAT (excerpt): https://www.elektronetshop.de/pilz-sicherheitsschaltgeraet-750330-typ-pnoz-s30-24-240vacdc-2-n-o-2-n-c/
- Ewellix CAHB catalogue IL-06022-2 (downloaded): https://www.slsbearings.com/uploads/pdf/Ewellix_IL-06022-2-EN-January_2023_CAHB_series.pdf ; CAHB-20-F3E EUR 617.61: https://eshop.papadopoulos-sa.com/linear-actuators/75292-ewellix-cahb-20-f3e-4500696-bba0pt-000-linear-actuators-7333314280503.html
- LINAK LA36 EUR 1,058.45 (review): https://www.wetterwinkel.nl/products/linak-actuator-la36-6-8kn-400mm-24v-ic-sensor-036161
- TiMOTION TA23 (excerpt): https://www.timotion.com/en/products/linear-actuators/ta23-series ; Thomson Electrak HD (excerpt): https://sr-linear.com/collections/electrak-hd-exx
- Holybro UM982 US$249.99: https://holybro.com/products/h-rtk-unicore-um982
- Landa TU2551 (excerpt): https://www.landamagnet.com/landa-tu2551-12v/24v-dc-screw-mount-tubular-linear-solenoid-10-100-duty-cycle-0-35n-force-l51x25mm-actuator
- RS PRO heater mats (RS IE): https://ie.rs-online.com/web/p/heater-pads/0731350 (alternative 245-562 EUR 54.59 shown on that page)
- SICK nanoScan3 EUR 1,827 (excerpt): https://industry-store.eu/products/nans3-aaaz30an1 ; Pilz PSENscan EUR 2,466 (excerpt): https://variadores.es/shop/pilz-6d000012-63698
- Mayser SG-EFS 104/4L EUR 420.34 (excerpt): https://shop.fortop.nl/nl/en/automation/machine-safety/switching-units-edges-mats.html
