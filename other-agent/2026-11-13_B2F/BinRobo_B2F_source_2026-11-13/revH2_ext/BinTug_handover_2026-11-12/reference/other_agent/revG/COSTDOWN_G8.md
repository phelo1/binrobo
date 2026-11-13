---
title: "BinRobo BT-6 Rev G8 - design-to-cost cold-eye review"
subtitle: "Target: all-in under EUR 2,000 with no loss of safety, function or capability (private-use machine on Brian's own lane)"
date: "11 November 2026"
geometry: margin=18mm
fontsize: 10pt
---

# 1. Bottom line

**EUR 2,000 all-in cannot be reached without losing functions.** I checked every line of the G7 BOM, changed whatever could be changed
without losing a function, and re-priced the changes from fetched pages. The cheapest configuration that still meets every function
comes to **EUR 3,771 all-in** (Lean-D: a used powerchair base and a hitch frame Brian builds himself). The cheapest all-new configuration comes to
**EUR 4,471** (Lean-N). Both are about half of G7 (EUR 8,218).

| Configuration (concept A') | Parts | Ship+duty | Cont. | **All-in** | vs 2,000 |
|--------------------------------------------------|------:|------:|------:|-------:|------:|
| **Lean-D**: donor powerchair base, Brian-built frame, all functions | 3,174 | 217 | 380 | **3,771** | +1,771 |
| **Lean-N**: all new parts, local laser shop, all functions (bom_revG8.csv) | 3,743 | 312 | 417 | **4,471** | +2,471 |
| Lean-N on concept B (if the concept gate picks B) | 3,584 | 312 | 379 | 4,275 | +2,275 |
| **Balanced**: Lean-N + Ewellix, UM982, new PNOZ, 400 W motors, G7 heater/SD/Nord-Lock | 4,817 | 362 | 468 | **5,647** | +3,647 |
| **G7 reference** (does not include the A' parts, about EUR 250) | 7,099 | 500 | 619 | **8,218** | +6,218 |

Contingency uses the G4 rule: 5 % on fetched prices, 8 % on excerpts, 12 % on estimates, 15 % on used, donor and local items, 10 % on logistics.
FX: 1 USD = 0.86 EUR. Prices include 23 % IE VAT.

**What does not fit, exactly (s.9):** Lean-D is EUR 1,771 over. Even after cutting six functions it is still about **EUR 720 over**
(EUR 2,724 all-in). The six cuts are dock self-charging, 4G and two-way audio, lidar and radar, night lights, RTK, and the A' climb parts.
The reason is the core: drive, frame, hitch and actuator, safety stack, computer and wiring already cost about **EUR 2,700 all-in** on their own.
A budget of EUR 2,000 fits the G4 design (EUR 2,131). G4 did not have the review fixes: PL d stop, a proper actuator, the traction concept,
the release fix, and a stated drive spec. Those fixes are what cost the extra money.

**Key swaps, Lean-N vs G7 (EUR, incl. VAT):**

| Swap | G7 | G8 | Saving |
|------------------------------------------------------------------|------:|------:|------:|
| Roboteq FDCG3260T -> RoboClaw 2x30A (current limit, encoder PID) | 967.89 | 148.44 | **-819** |
| PNOZ s30 speed monitor -> inherent gearing cap + own-build 2-MCU monitor | 814.33 | 30.00 | **-784** |
| PEWM-39 pair -> PEWM82M-320W pair + 3.5:1 chain stage (wheel line +40) | 862.11 | 315.22 | **-547** |
| Ewellix CAHB-20 405 mm -> FDI/QC 400 mm 4 kN IP65 | 622.63 | 164.37 | **-458** |
| PNOZ s5 new -> used PNOZ X3 (tested, 3-month warranty) | 358.42 | 61.25 | **-297** |
| UM982 dual-antenna -> LC29HDA rover + GSF yaw + dock tag | 274.44 | 33.00 | **-241** |
| Laser package: all-steel (no 5083), HDPE deck/lid | 713.29 | 602.78 | -111 |
| Nord-Lock -> DIN 25201 wedge washers; RS heater mats -> generic pads | 260.38 | 77.00 | -183 |
| Visaton horn -> Eagle P630TA; pawl solenoid -> cam lobe; SD, bumper switches, dock bits | | | -237 |
| Added: second contactor KM2 (+29); A' concept parts not in the G7 BOM (+250) | | | +279 |
| Logistics (fewer non-EU lines, no air-freight PEWM-39, no GR/HB orders) | 500.36 | 312.00 | -188 |

# 2. Function list: requirement, cheapest credible solution, price

Prices are "checked" when the page was fetched on 11 Nov and "excerpt (unverified)" when they come only from a search result. Lean-N column.

| # | Function | Requirement | Cheapest credible solution | EUR | Status / source |
|---|---------|--------------|----------------------------------|---------:|-----------|
| F1 | Hook 140 L + 240 L bins | Floating twin hook, latch both, tilt 48 deg, 2,473 N sim peak | G6/G7 hook carriage, pawls, cam (unchanged); **FDI 400 mm 4 kN IP65** actuator + 30 mm spacer | 164 + 213 | checked [A1]; mechanics est |
| F2 | 12 % wet-leaf climb | 30-39 N m/wheel (x1.25), traction mu_req <= 0.27 | PEWM82M-320W + 3.5:1 chain: 34.8 N m @ 17 A, 53 N m @ 25.8 A; A' load-transfer pad, yaw damper | 445 + 250 | checked [D1][D2]; A' est |
| F3 | 40 mm step | Climb 40 mm full-width step | 330 mm wheels (unchanged). **Open issue, not a cost item**: both concepts still fail the full-width step in the sim | 0 | sim open |
| F4 | Night ops | Lights, conspicuity, IR camera | L1-L6 unchanged (StVZO dipped heads, R65 beacon, markers, ECE 104 tape) | 125 | G7 checked/excerpt |
| F5 | RTK + lidar + camera | cm position, 2D scan, camera | Own LC29HBS base + **LC29HDA rover**; STL-06N lidar; Radxa Zero 3W + IR USB camera | 48 + 33 + 50 + 101 | excerpt [N1] |
| F6 | 4G monitoring + recording | Live view, alerts, local recording | SIM7600G-H HAT (-30..+80 C board) + sun shield; high-endurance SD with UPS HAT clean shutdown | 122 + 15 + 12 | G7 excerpt; SD est |
| F7 | Two-way audio | Talk and listen at the bin | **Eagle P630TA IP65 15 W horn** + MAX98357A + USB mic | 75 | checked [C1] |
| F8 | Obstacle and person stop | PL d-class stop: bumpers, e-stop, speed limit | 4 x Omron D4N on bumpers; used PNOZ X3; KM1 + KM2; spring brakes; own-build speed monitor; lidar + 2 radars | 137 + 61 + 57 + 40 + 98 | s.3 |
| F9 | Bin-handling edge cases | Full/empty, seat, latch, pawl, feelers | K2, K5, G13, feelers, pawl-up sensor (kept); pawl lift by cam lobe | 60 | est |
| F10 | Dock charging | Self-docking, contacts, charge gate | Plated wiping contacts, 29.2 V 5 A charger, ESP32-C3 dock controller, IP65 box | 193 | G7 checked + est |
| F11 | Weather sealing | IP65+ outdoors, Irish winter | IP67 box + glands + Gore vent; IP65 actuator; Zinga on steel; DT/SB50 connectors | in lines | |

# 3. Safety: the equivalence argument

G7 used a PNOZ s5 (PL e), the Roboteq certified STO (Cat 3 / PL e), a PNOZ s30 speed monitor (PL e), one contactor and spring brakes.
That stack is very good. It is also certified for products placed on the market, and this machine will not be. G8 keeps the same
**architecture** (dual-channel, monitored, fail-safe) and changes how each part of it is bought.

1. **Inputs (unchanged structure).** The e-stop has 2 NC positive-opening contacts. The bumpers now use **4 x Omron D4N** safety limit switches
   (direct opening per IEC 60947-5-1 Annex K, IP67), with their NC contacts wired as two channels. The tilt switch and the two hardware
   watchdogs stay in the stop loop. *Equivalent:* same contact principle as G7, and a welded contact is forced open by the actuator.
2. **Logic: used Pilz PNOZ X3 (EUR 61) instead of a new PNOZ s5 (EUR 358).** The X3 is a two-channel e-stop relay with cross-fault
   detection, a feedback loop and monitored start, rated Cat 4 / PL e. *Equivalent:* same function class. Being used, it can hide wear.
   Mitigation: a bench function test on arrival (each channel, cross-short, feedback-loop open) and the same test every year. The relay
   cannot restart with a welded internal contact, which is how this type is designed. Fallbacks: new X2.8P from EUR 101 (excerpt) or used PNOZ s4 at EUR 70.
3. **Output: two series contactors instead of a certified STO drive.** KM1 and KM2 (100 A DC, 24 V coil, about 2.5x de-rated against
   the 40 A load) are in series in B+ to the motor controller, the actuator relays and the brake coils. Each coil is fed by its own
   PNOZ safety contact. *Equivalent:* STO removes torque-producing energy from the motor. Opening either contactor removes all supply
   to the drive, so no torque is possible, and the power-to-release spring brakes apply at once because their feed is downstream of KM2.
   One welded contactor still leaves the other able to stop the machine, which is the Cat 3 requirement. Stop category becomes 0
   (immediate) instead of G7's category 1. At 0.5 m/s with 220 kg the kinetic energy is 27.5 J, and wheelchair spring brakes stop that
   within roughly 0.1 m. Bench test T4 checks this, including towing the bin downhill (no jack-knife).
4. **Contactor feedback monitoring (EDM) by an independent MCU, not a safety relay with mirror contacts.** SW100-class contactors have
   no mechanically linked auxiliary contacts. Instead, MCU-A senses node N1 (between KM1 and KM2) and MCU-B senses node N2 (after KM2)
   through dividers. Before every start, the MCUs feed each coil through their own relay pole. That pole sits in series with the PNOZ
   output, so the MCU can only *remove* power, never add it. Sequence: both open -> N1 and N2 dead (KM1 not welded); KM1 only -> N2 dead
   (KM2 not welded); then both. Each MCU's OK contact sits in series in the PNOZ start/feedback loop, so a welded contactor blocks the
   reset. *Equivalent:* same diagnostic as EDM with mirror contacts (detects a weld at the next start; DC "medium"), and it costs EUR 30
   instead of EUR 100+ for contactors with linked auxiliary contacts.
5. **Speed limit: physics first, then two monitors, instead of the EUR 814 PNOZ s30.**
   (a) *Inherent:* the 32:1 x 3.5:1 = 112:1 drive cannot exceed about 0.9-1.0 m/s with no load at full pack voltage (about 0.79 m/s at
   rated current). This holds whatever the software does, because the motors cannot spin faster. Kinetic energy at the worst case is
   about 110 J.
   (b) *Controller:* the RoboClaw QPPS limit holds 0.5 m/s, with a 28 A current limit.
   (c) *Own-build two-channel monitor:* two RP2040 boards with diverse sensors. Channel A counts inductive teeth; channel B reads the hall
   wheel encoders. Each drives one relay pole in its own PNOZ input channel and trips on > 0.6 m/s (0.3 m/s near the road mouth), on an
   A/B or left/right mismatch, or on loss of the other board's heartbeat. Outputs drop out to trip.
   *Equivalent:* same structure as a Cat 3 speed monitor (two channels, cross-check, de-energise to trip). **It is not certified**:
   honestly it is about PL c-d by design, self-assessed. For this hazard that is enough, because layer (a) already caps the energy that
   G7's PL e monitor was guarding against.
6. **What G8 does not claim.** The G8 stack is not a certified PL d/e system. It is a monitored, fail-safe, dual-channel design that a
   private builder can verify with the tests in s.10. The PNOZ X3 and the D4N switches are certified parts; the speed monitor and the
   EDM are not.

**Donor variant (Lean-D):** a powerchair runs at about 6 km/h (1.7 m/s), so layer (a) is lost. The speed limit then rests on layers (b)
and (c), which is the main safety difference between Lean-D and Lean-N.

# 4. Drive: torque evidence

* **Requirement:** 220 kg total, r = 0.165 m, 0.5 m/s. Torque per wheel is 30 N m (crr 0.05) to 39 N m (crr 0.10), times 1.25 = 37.5-48.8 N m.
* **Lean-N motor:** peiscooter **PEWM82M-320W** pair, 24 V, 32:1 right-angle wheelchair gearbox, spring brake with hand release,
  **US$298 per pair** (category page fetched [D1]), EUR 315 with IE VAT.
* **Evidence:** a measured test curve for the same 320 W, 82.8 mm, 4-pole wheelchair motor class [D2] (SuperDroid TD-292 report, Hangzhou Lectstyle,
  24 V, 43:1): **14.08 N m at 17.08 A** (rated, 119 rpm), **21.3 N m at 25.8 A** (maximum power). Scaling to 32:1 gives 10.5 N m at
  17 A. Through a 3.5:1 chain (efficiency 0.95) that is **34.8 N m per wheel at the rated 17 A** and **53 N m at 25.8 A**.
  So the 30-39 N m demand is met at or near rated current, and the 48.8 N m margin case is met inside the RoboClaw 60 A peak and a
  28 A limit. **Thermal risk:** a long 12 % climb at crr 0.10 runs the motors at about 24 A, which is above their rated current. The
  ramp is short, but bench test T1 measures it. Balanced uses the 400 W PEWM-S pair (US$398) for more margin.
* **Speed:** about 0.79 m/s at rated current, 0.9-1.0 m/s with no load. This meets the 0.5 m/s operating speed with margin, but it is
  below the G6 review's ">= 1.0 m/s free" wish. I chose that deliberately: the lower top speed is what makes the inherent speed cap in s.3 work.
* **Chain stage (EUR 130 est):** 12T on the gearmotor shaft, 42T plate sprocket on a 330 mm solid-PU wheel on a dead stub axle, 08B
  chain, slotted motor plate. It replaces the PEWM-39 direct drive (vendor 48 N m continuous, EUR 862 + air freight).
* **Controller:** RoboClaw 2x30A, **EUR 148.44** (fetched [D3]; restocking, second source Pololu). MDDS30 (EUR 82.95 fetched [D4]) was
  rejected because it has no settable current limit and no encoder loop.
* **Donor route (Lean-D):** used powerchairs sell for EUR 380-850 in Ireland (DoneDeal / adverts.ie excerpts [D5], unverified). A chair
  rated for a 136 kg user on 6-9 deg moves 246 kg up 10.5-15.8 %. The tug plus bin at 12 % needs **386-451 N of drawbar pull**, so only
  chairs rated >= 8 deg qualify. **Evidence before paying:** pull test T1-D (>= 450 N at walking pace for 3 minutes, luggage scale and rope
  to a post). Wheelchair motors from Pride/Invacare chairs can also be bought on their own (EUR 100-250 a pair, excerpts). They take the
  same chain stage and need the same acceptance test, because their kt and gear ratio are unknown.

# 5. Mast actuator

* **Requirement:** >= 3.1 kN at -20 C (1.25 x the 2,473 N sim peak), 386 mm working stroke inside a 656-1,042 mm pin window, IP65+.
* **Lean-N: QC/FDI 24 V 400 mm, 4,000 N, IP65, -50..+45 C, 6 mm/s, limit switches, L = 620 mm** at anodas.lt,
  **EUR 137.10 (EUR 113.31 ex VAT)**, page fetched [A1]. Pin-pin 620/1,020 mm plus a 30 mm clevis spacer gives 650/1,050 mm, which covers the window.
  Note: the cheaper Elektrobim FDI 4 kN at EUR 96 is only IP42 and is rejected.
* **Losses against Ewellix and how they are covered:**
  * No manual override: an aux-power Anderson socket plus a hold-to-run pendant lowers a loaded mast with a dead pack.
  * No position output: mast angle comes from the AS5600 on the hinge, which is already in the BOM. A Hall-pulse version of the same
    actuator exists (akcesoria.cnc.info.pl, excerpt).
  * Slower: 6 mm/s instead of 11 mm/s, so a full tilt takes about 64 s instead of about 35 s.
  * No datasheet cold-force figure: bench test T2 is a freezer test at -20 C under a 3.1 kN load.
* **Fallback:** REMORE RE601G 6,000 N, IP65, -26..+65 C, 892.99 PLN (fetched). It needs a 70 mm spacer and runs at 5 mm/s.
* **Concept B:** the same family with 300 mm stroke serves as the lifter, priced conservatively at the 400 mm figure.

# 6. Sensing, navigation, comms

* **Lidar plus camera only?** The scan comes from one 2D lidar (STL-06N, EUR 50) and the rear IR camera. The two 24 GHz radars (EUR 48)
  watch the road mouth for approaching vehicles. Lidar range (12 m) gives under 1 s warning of a car at 50 km/h, so the radars stay.
  Removing them is a capability cut (s.9).
* **RTK:** OSi/Tailte Eireann publishes free RINEX for post-processing only. I found **no free real-time NTRIP** for this location
  (rtkdata.com/ie, tailte.ie), so the own base stays (LC29HBS + ESP32 NTRIP server, EUR 48). The **rover becomes an LC29HDA (EUR 33,
  excerpt)** instead of the UM982 (EUR 274). Heading comes from three sources: the EKF GSF yaw while moving, wheel odometry plus gyro
  when pivoting or standing, and an absolute reset from the dock ArUco tag 20 at every departure. **Risk:** heading after a long
  standstill under the hedge canopy. Bench test T6 walks the lane with the rover on a trolley.
* **Phone as camera, computer and 4G (option, not in the totals).** A refurbished Galaxy A14 costs EUR 109-155 (excerpts), or EUR 0 if
  Brian has a spare. It would replace the Radxa and camera, the 4G HAT, the UPS, the SD card and the mic (about EUR 249) with about
  EUR 150 (phone, ESP32 MAVLink/radar bridge, OTG hub; the sun shield stays). That saves about EUR 100, or about EUR 210 with a spare
  phone. Not adopted, because:
  * the phone is rated for 0-35 C in a pod that reaches 48 C, and Li-ion swelling on permanent charge is a real risk;
  * Android kills background services;
  * the FC and the lidar still need USB/UART bridging.
* **4G:** the SIM7600G-H HAT stays. The Huawei E3372 (EUR 40) is rated for 0..40 C, so it fails both Irish winter nights and the hot pod.

# 7. Power, structure, dock, logistics

* **Battery:** 8 x EVE C40 20 Ah + Daly 8S BMS (EUR 140; NKON is out of stock, so restock or CBAK are the alternatives). A used
  LiFePO4 pack is not worth it at this price: there is no cycle history, and a 24 V 20 Ah used pack costs about the same. **Lean-D**
  reuses the donor's 2 x 12 V AGM pair. It weighs 21-30 kg, which is useful ballast, and it charges below 0 C, so the pack heater and
  BMS are not needed. If the capacity test shows < 80 %, a new pair costs about EUR 140.
* **Heater:** two generic 24 V silicone pads with adhesive, the KSD9700 cutout and the NTC charge gate kept. EUR 24 (excerpt) instead of EUR 115.
* **Frame:** every 5083 part goes to 2 mm DX51D+Z275 steel (tray, bulkhead, pod and battery brackets), and the deck and lid become 10 mm
  HDPE offcuts. That adds about 7.4 kg low in the chassis, which counts as ballast. The same local RFQ gets five sheet groups:
  **EUR 603 instead of EUR 713**. Zinga cold galvanising (EUR 52.50) beats hot-dip (EUR 120 minimum charge plus transport) at this
  size. **Own fabrication** (Lean-D): RHS and flat bar saw-cut and drilled by Brian, with only 18 grabber, mast and sensor plates
  laser-cut. That is EUR 354 including Zinga and stock. Brian's labour is not costed.
* **Dock:** the plated wiping contacts (EUR 26) stay, because they are already the simple solution. The dock controller moves to an
  ESP32-C3 + INA219 (EUR 15), and the frame is built from timber offcuts (EUR 15).
* **Shipping, VAT, duty:** EUR 312 (Lean-N) / EUR 217 (Lean-D).
  * The largest items are air freight for the peiscooter motors (about EUR 110, est) and the EU EUR 3 per tariff line on low-value
    AliExpress parcels (about EUR 54 on 18 lines).
  * All EU shops charge VAT at source. Non-EU lines carry 23 % import VAT in the line price.

# 8. Configurations

* **Lean-N (bom_revG8.csv / .json):** 91 lines + 12 logistics lines, concept A'. Totals in s.1. Every line has a source and a status.
* **Lean-D (bom_revG8_donor.csv):**
  * removes from Lean-N: motors, chain stage, casters, ballast, heater, charger, LiFePO4 pack and the laser package;
  * adds: a donor chair (EUR 400, excerpt), the Brian-built frame (EUR 354) and the AGM pair reuse (EUR 0).
* **Balanced:** Lean-N plus:
  * Ewellix CAHB-20 (manual override, position output, IP69K, -40 C);
  * UM982 dual-antenna heading;
  * new PNOZ X2.8P;
  * PEWM-S 400 W motors;
  * G7 laser package with only the steel tray change;
  * industrial SD, RS heater mats and Nord-Lock.
* **G7:** bom_revG7.csv, unchanged.

# 9. What does not fit under EUR 2,000, and by how much

Starting from Lean-D (EUR 3,771 all-in), these are the function cuts with their parts saving:

| Cut (capability lost) | Parts EUR |
|------------------------------------------------------------|---------:|
| Dock self-charging -> manual plug-in | -139 |
| 4G monitoring/recording + two-way audio | -197 |
| Lidar + radars (non-contact person/vehicle stop; bumpers only) | -98 |
| Night lighting + conspicuity (daylight only) | -125 |
| RTK base + rover | -81 |
| A' traction parts (12 % wet climb no longer assured) | -250 |
| **All six -> all-in about EUR 2,724** | **still +724** |

What remains is the core: drive EUR 566, hitch and actuator EUR 377, safety stack EUR 423, frame EUR 354, computer EUR 151, wiring
EUR 336, plus logistics and contingency. **About EUR 2,700 all-in before any sensor, comms, dock or light.** So EUR 2,000 is not reachable
with this machine. The only ways under it are to drop the PL d-class stop (not allowed) or to stop tilting the bin, which means a different job.

# 10. Risks and bench tests

| # | Risk | Bench / acceptance test (before the line is relied on) |
|----|--------------------------|----------------------------------------------------|
| T1 | Motor heat on the 12 % climb (24 A > 17 A rated) | Drag test: 450 N drawbar, 0.5 m/s, 3 min, winding temperature < 110 C |
| T1-D | Donor chair torque unknown | Pull test at the seller's: >= 450 N at walking pace for 3 min, before paying |
| T2 | FDI cold force not on a datasheet | Freezer -20 C for 4 h, then 3.1 kN lift on a lever rig; current < 3 A; IP65 hose test |
| T3 | Used PNOZ X3 | On arrival: each channel opens, cross-short trips, feedback loop blocks start; repeat yearly |
| T4 | Category 0 stop with the bin in tow | 0.5 m/s downhill 12 %, e-stop: stop < 0.15 m, no jack-knife, bin stays latched |
| T5 | Own-build speed monitor | Inject 0.7 m/s (wheel off ground): both channels trip; kill one MCU: trip; swap encoder lead: trip |
| T6 | Single-antenna heading | Lane walk with the rover on a trolley, 3 runs: heading error < 5 deg after a 60 s standstill under the canopy |
| T7 | EDM sequence | Bridge KM1, then KM2, with a jumper: reset must be refused each time |
| T8 | Generic heater pads | 2 h at -5 C ambient: pack rises 5 C at 15 W mean; KSD9700 opens at 40 C |
| T9 | Horn level | > 85 dB at 1 m from the pod amp |
| T10 | Supplier availability | RoboClaw restocking, PNOZ X3 single used unit, NKON cells out of stock: order the long-lead items first |

**Other risks:**

* A' parts (EUR 250) and the chain stage (EUR 130) are estimates.
* The 40 mm step is a sim failure for both concepts. It is unchanged by this review and not a cost item.
* Lean-D depends on finding a chair rated >= 8 deg. AGM replacement is about EUR 140 if the donor batteries are tired.

# 11. Sources (fetched 11 Nov 2026 unless marked excerpt)

* [A1] FDI 24 V 400 mm 6 mm/s, EUR 137.10 / 113.31 ex VAT, L 620, IP65, -50..+45 C: https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s
* [A2] REMORE RE601G 6 kN, 892.99 PLN: technika-cnc.pl (fetched in this session)
* [D1] peiscooter wheelchair motors, PEWM82M-320W pair US$298, PEWM-S 400 W US$398, PEWM-39 US$815: https://www.peipeiscooter.com/categories/100020
* [D2] SuperDroid TD-292 wheelchair motor test report (14.08 N m @ 17.08 A; 21.3 N m @ 25.8 A, 43:1): https://www.superdroidrobots.com/product_info/TD-292-120_Test_Report.pdf
* [D3] RoboClaw 2x30A EUR 148.44: https://eu.robotshop.com/products/roboclaw-2x30a-6-34vdc-regenerative-motor-controller
* [D4] Cytron MDDS30 EUR 82.95: vanallesenmeer.nl (fetched in this session)
* [D5] Used powerchairs IE EUR 380-850 (excerpt): https://www.donedeal.ie/all?words=electric+wheelchair , https://www.adverts.ie/results/electric+wheelchair
* [S1] Pilz PNOZ X3 774310 used EUR 49.80 net (listing on the fetched page; X2.8P sold out): https://cncbote.de/en/product/pilz-pnoz-x2-8p-24vacdc-3n-o-1n-c-id-nr-777301-safety-relay
* [S2] Omron D4N-4120 EUR 19.69 net (excerpt): https://fluidics-equipment.com/d/FL-D4N4120.html ; TME EUR 31.86 net (excerpt)
* [S3] SW100 24 V 100 A contactor EUR 28.66 (excerpt): https://jazgot.at/sch%C3%BCtze/18407-antriebssch%C3%BCtz-dc-24v-100a-sw100.html
* [C1] Eagle P630TA IP65 8 ohm 15 W horn EUR 42.50 / 35.12 ex VAT: https://www.eijlander.nl/hoorn-luidsprekers.html
* [N1] LC29H rover about US$15-17 + antenna (excerpts, G4 sourcing); OSi free RINEX only: https://rtkdata.com/ie , https://tailte.ie
* [P1] Refurbished Galaxy A14 EUR 109-155 (excerpts): backmarket.ie, refurbed.ie, technocircle.lt
* All unchanged lines carry their G4-G7 sources in bom_revG8.csv.
