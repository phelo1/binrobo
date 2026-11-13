# B2-F lane SITL - frozen pass criteria (ArduPilot Rover 4.6.2 SITL)

Frozen: 2026-11-12 20:35 UTC (23:35 Asia/Riyadh), BEFORE any scored run and before the B2-F scenario code was written.
The sha256 of this file is recorded in P/docs/reviews/TESTLOG_B2F_sitl.md and re-checked before scoring.
Any later change is logged as a deviation with its reason; a scored result is only reported against this text.

Design under test: B2-F rigid carrier, lifts the bin by its FRONT-wall EN 840 receiver (640 mm self-aligning comb + pad),
skid-steer drive wheels + nose castors, 0.93 m wide, ~1.50 m long, speed capped at 0.5 m/s. Geometry: work/revB2F/dims_B2F.json.

A run is PASS only if every criterion that applies to it holds. All distances are TRUTH (simulator) values, never the
robot's own estimate.

| id | criterion | threshold | applies to |
|---|---|---|---|
| C1 | Hedge clearance: minimum distance from the footprint (robot body + carried bin) to the TRUTH hedge face (lane hedges, mouth hedge ends, yard edge) | >= 0.124 m (= SITL lateral-estimate p95) | every run that moves |
| C2 | Set-down accuracy: placed bin centre to the commanded spot (pad A/M/F, home spot, or a declared legal alternate) | <= 0.15 m, and handle direction within 10 deg | every set-down |
| C3 | [county] bye-law times (mission clock): robot leaves the dock no earlier than 18:00 and is back on the dock by 21:00 on that evening; no bin placed on the pad before 18:00 | 18:00 <= first motion; last dock <= 21:00 | full-mission runs (s1a, s1b, s3a, s3b) |
| C4 | Geofence: no footprint point (robot, carried bin) on the public side of the private boundary (road verge, 6.0 m from the road centre-line) at any time | 0 breaches (min margin >= 0.00 m) | every run |
| C5a | E-stop: stop distance from 0.5 m/s with a full 240 L bin, press -> v < 0.01 m/s | <= 0.30 m | s7 |
| C5b | Obstacle stop: robot at rest with a person / dog / car in its path, truth gap footprint-to-object | >= 0.50 m; and no contact with any obstacle or standing bin in any run (gap > 0) | every run with actors |
| C5c | Companion freeze: firmware HOLD after the Pi goes silent, and distance rolled after the freeze | HOLD <= 2.5 s, rolled <= 1.0 m | s6a, s6b |
| C6 | Energy per bin trip (dock -> drop/pick -> dock), measured at the pack | <= 50 Wh per trip; three-bin evening end SOC >= 20 % from 90 %; the energy guard must refuse a trip whose budget exceeds the available energy | full-mission runs; s8 |
| C7 | Outcome equals the declared expectation (pass = mission completed; alert = robot stops safely / refuses and raises the alert named) | exact | every run |
| C8 | Grab hand-off to the MuJoCo gate: robot at the pre-grab pose (1.2 m out on the bin axis, as MuJoCo G1 starts) within the G1 start envelope | lateral <= 0.05 m, yaw <= 3 deg; grab outcome then = MuJoCo front-dock gate (90/90 success) | every grab |

Declared expectations (C7):

| scenario | expectation |
|---|---|
| s1a one-bin night drop (240 L to pad A) | pass |
| s1b one-bin night pickup (pad A -> home) | pass |
| s3a three-bin night drop (140 L -> A, 240 L -> M, 240 L -> F) | pass |
| s3b three-bin night pickup (F, M, A -> home) | pass |
| s4a RTK float under the hedge (40 m) | pass |
| s4b RTK loss under the hedge (20 m, bridged) | pass |
| s4c RTK long loss (70 m) | alert (hold, no fix) |
| s5a person + dog crossing (loaded) | pass |
| s5b car in the bell-mouth at the drop | pass |
| s6a companion freeze, loaded transit | firmware HOLD (scored on C5c) |
| s6b companion freeze, reversing onto the bin | firmware HOLD (scored on C5c) |
| s7 e-stop, loaded transit | stop (scored on C5a) |
| s8 low battery at the energy guard | alert (trip refused, robot stays docked) |
| s9 bin missing at pickup | alert (no grab, robot heads home empty) |
| s10a bin tipped at pickup | alert (no grab) |
| s10b bin blocked at pickup (car over the approach) | alert (no grab) |
| s11a wind no-go | alert (no departure) |
| s11b frost no-go | alert (no departure) |
| s12a pad configured on the road verge | alert (Pi refuses, no motion past the fence) |
| s12b Pi fence check bypassed, robot driven at the road edge | firmware fence HOLD, C4 must hold |

Seeds: 7, 11, 23 for every scenario. Seed sets the RTK noise / canopy multipath, odometry scale error, actor timing jitter,
and bin placement jitter (+-0.05 m, +-3 deg) at the pads.

Not criteria (reported only): keep-left gap, cross-track, run time, pivots, chunk restarts.
