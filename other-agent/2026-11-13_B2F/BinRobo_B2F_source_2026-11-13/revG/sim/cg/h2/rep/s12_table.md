
### Rev H2

Loads used: wheel static 858 N, carry 2847 N (H2_S7_climb_m22_c06_cg0.json), edge 7379 N (H2_S5_ESE240SL_pothole_v08_lmu45.json); rigid-step impulse 17799 N and stalled-trench 869946 N not used. Comb static 1079 N, carry 2055 N, all runs 7315 N (H2_S5_WEB140_trench_v08_kp.json). Pad max 3704 N; lift max 4000 N (actuator cap).

| element | load level | force (N) | M (N m) | stress (MPa) | SF | meets 2? / fix |
|---|---|---|---|---|---|---|
| side rail 50x50x3 S235 | static | 859 | 455 | 54.6 | 4.31 | yes |
| side rail 50x50x3 S235 | carry | 2847 | 1509 | 180.9 | 1.30 | NO: S235 60x60x4 (Z >= 12843 mm3) |
| side rail 50x50x3 S235 | edge | 7380 | 3911 | 469.0 | 0.50 | NO: S235 80x80x5 (Z >= 33287 mm3) |
| side rail 50x50x3 S235 | rigid_step(info) | 17800 | 9434 | 1131.2 | 0.21 | info |
| mast upright at foot 50x50x3 S235 | static | 1079 | 230 | 27.5 | 8.54 | yes |
| mast-foot bolts M10 8.8 (ASSUMED 2 per row, lever 100 mm) | static | 1148 | 230 | 19.8 | 32.35 | yes |
|   bolt pull-through 3 mm RHS wall | static | 1148 | - | - | 22.27 | yes |
| mast upright at foot 50x50x3 S235 | carry | 2055 | 437 | 52.4 | 4.48 | yes |
| mast-foot bolts M10 8.8 (ASSUMED 2 per row, lever 100 mm) | carry | 2186 | 437 | 37.7 | 16.98 | yes |
|   bolt pull-through 3 mm RHS wall | carry | 2186 | - | - | 11.69 | yes |
| mast upright at foot 50x50x3 S235 | comb_all | 7316 | 1556 | 186.6 | 1.26 | NO: S235 60x60x4 |
| mast-foot bolts M10 8.8 (ASSUMED 2 per row, lever 100 mm) | comb_all | 7780 | 1556 | 134.1 | 4.77 | yes |
|   bolt pull-through 3 mm RHS wall | comb_all | 7780 | - | - | 3.29 | yes |
| comb plate (symmetric) | carry | 2055 | 102 | 33.7 | 10.52 | yes |
| comb plate (one half at the roll stop) | carry | 2055 | 247 | 81.5 | 4.35 | yes |
| comb pivot pin D16 8.8 (ASSUMED, 20 mm cantilever) | carry | 2055 | 41 | 102.2 | 6.26 | yes |
| comb pivot pin D20 8.8 (ASSUMED, 20 mm cantilever) | carry | 2055 | 41 | 52.3 | 12.23 | yes |
| comb plate (symmetric) | comb_all | 7316 | 363 | 120.1 | 2.96 | yes |
| comb plate (one half at the roll stop) | comb_all | 7316 | 878 | 290.2 | 1.22 | NO: plate 8 mm or net depth >= 70 mm |
| comb pivot pin D16 8.8 (ASSUMED, 20 mm cantilever) | comb_all | 7316 | 146 | 363.9 | 1.76 | NO: pin D20 8.8 or double shear |
| comb pivot pin D20 8.8 (ASSUMED, 20 mm cantilever) | comb_all | 7316 | 146 | 186.3 | 3.44 | yes |
| carriage roller 6202-2RS, C0 3.75 kN | static | 765 | 459 | - | 4.90 | yes |
|   roller line contact on S235 tube face | static | 765 | - | 382 | 1.06 | NO: hardened track strip (>= 50 HRC) on each upright face |
| carriage roller 6202-2RS, C0 3.75 kN | carry | 1457 | 874 | - | 2.57 | yes |
|   roller line contact on S235 tube face | carry | 1457 | - | 527 | 0.55 | NO: hardened track strip (>= 50 HRC) on each upright face |
| carriage roller 6202-2RS, C0 3.75 kN | comb_all | 5187 | 3112 | - | 0.72 | NO: two rollers per station or C0 >= 10.4 kN; roller rows 0.45 m apart |
|   roller line contact on S235 tube face | comb_all | 5187 | - | 995 | 0.16 | NO: hardened track strip (>= 50 HRC) on each upright face |
| castor outrigger plate 8 mm S355 (vertical 3 g) | static x3 | 956 | 29 | 17.9 | 19.80 | yes |
| castor outrigger plate 8 mm S355 (kerb strike, 80 N m) | kerb | 503 | 161 | 100.6 | 3.53 | yes |
| nose cross-member 50x50x3 torsion (kerb strike) | kerb | 503 | 161 | 12.1 | 11.16 | yes |
| (bin) receiver ledge, HDPE, gate-model section | carry | 2055 | - | 8.6 | 2.60 | yes |
| (bin) receiver ledge, HDPE, gate-model section | comb_all | 7316 | - | 30.7 | 0.73 | NO: comb buffer to cut the peak; measure real receivers (B0b/B1) |

### B2-F

Loads used: wheel static 930 N, carry 2385 N (B2F_estop12_fwd_pm110.json), edge 7305 N (B2F_S6_kerb_v05_nose_t15_80cas.json); rigid-step impulse 22135 N and stalled-trench 1057023 N not used. Comb static 1079 N, carry 1872 N, all runs 9633 N (B2F_S5_ESE240SL_step_v08_lsr004.json). Pad max 1772 N; lift max 3000 N (actuator cap).

| element | load level | force (N) | M (N m) | stress (MPa) | SF | meets 2? / fix |
|---|---|---|---|---|---|---|
| side rail 50x50x2 S235 | static | 931 | 456 | 77.2 | 3.04 | yes |
| side rail 50x50x2 S235 | carry | 2385 | 1169 | 197.8 | 1.19 | NO: S235 50x50x4 (Z >= 9947 mm3) |
| side rail 50x50x2 S235 | edge | 7306 | 3580 | 605.9 | 0.39 | NO: S235 80x80x5 (Z >= 30467 mm3) |
| side rail 50x50x2 S235 | rigid_step(info) | 22136 | 10847 | 1835.8 | 0.13 | info |
| mast upright at foot 50x50x2 S235 | static | 1079 | 230 | 38.8 | 6.05 | yes |
| mast-foot bolts M10 8.8 (ASSUMED 2 per row, lever 60 mm) | static | 1913 | 230 | 33.0 | 19.41 | yes |
|   bolt pull-through 2 mm RHS wall | static | 1913 | - | - | 8.91 | yes |
| mast upright at foot 50x50x2 S235 | carry | 1873 | 398 | 67.4 | 3.49 | yes |
| mast-foot bolts M10 8.8 (ASSUMED 2 per row, lever 60 mm) | carry | 3320 | 398 | 57.2 | 11.18 | yes |
|   bolt pull-through 2 mm RHS wall | carry | 3320 | - | - | 5.13 | yes |
| mast upright at foot 50x50x2 S235 | comb_all | 9634 | 2049 | 346.8 | 0.68 | NO: S235 80x40x4 |
| mast-foot bolts M10 8.8 (ASSUMED 2 per row, lever 60 mm) | comb_all | 17076 | 2049 | 294.4 | 2.17 | yes |
|   bolt pull-through 2 mm RHS wall | comb_all | 17076 | - | - | 1.00 | NO: through-plates / crush tubes, or 5 mm foot plates welded to the upright |
| comb plate (symmetric) | carry | 1873 | 93 | 5.5 | 64.52 | yes |
| comb plate (one half at the roll stop) | carry | 1873 | 225 | 13.3 | 26.70 | yes |
| comb pivot pin D16 8.8 (ASSUMED, 20 mm cantilever) | carry | 1873 | 37 | 93.1 | 6.87 | yes |
| comb pivot pin D20 8.8 (ASSUMED, 20 mm cantilever) | carry | 1873 | 37 | 47.7 | 13.42 | yes |
| comb plate (symmetric) | comb_all | 9634 | 478 | 28.3 | 12.54 | yes |
| comb plate (one half at the roll stop) | comb_all | 9634 | 1156 | 68.4 | 5.19 | yes |
| comb pivot pin D16 8.8 (ASSUMED, 20 mm cantilever) | comb_all | 9634 | 193 | 479.1 | 1.34 | NO: pin D20 8.8 or double shear |
| comb pivot pin D20 8.8 (ASSUMED, 20 mm cantilever) | comb_all | 9634 | 193 | 245.3 | 2.61 | yes |
| HGH15CA block, C0 23.47 kN (pitch 0.20 m ASSUMED) | static | 1148 | 459 | - | 20.45 | yes |
|   HGR15 rail screws M4 8.8 (2 per block) | static | 574 | - | 65 | 9.79 | yes |
| HGH15CA block, C0 23.47 kN (pitch 0.20 m ASSUMED) | carry | 1992 | 797 | - | 11.78 | yes |
|   HGR15 rail screws M4 8.8 (2 per block) | carry | 996 | - | 113 | 5.64 | yes |
| HGH15CA block, C0 23.47 kN (pitch 0.20 m ASSUMED) | comb_all | 10245 | 4098 | - | 2.29 | yes |
|   HGR15 rail screws M4 8.8 (2 per block) | comb_all | 5123 | - | 583 | 1.10 | NO: M4 12.9 into a 10 mm backing flat (not the 2 mm wall), 60 mm pitch |
| nose cross-member 50x50x2 bending (vertical 3 g, castor 0.15 m from the drop plate) | static x3 | 806 | 121 | 20.5 | 11.49 | yes |
| nose cross-member 50x50x2 torsion (kerb strike, 80 N m) | kerb | 485 | 119 | 12.9 | 10.52 | yes |
| rail drop plate 6 x 100 S355 (ASSUMED size; kerb strike, 0.12 m drop) | kerb | 485 | 58 | 97.0 | 3.66 | yes |
| (bin) receiver ledge, HDPE, gate-model section | carry | 1873 | - | 7.9 | 2.86 | yes |
| (bin) receiver ledge, HDPE, gate-model section | comb_all | 9634 | - | 40.5 | 0.56 | NO: comb buffer to cut the peak; measure real receivers (B0b/B1) |
