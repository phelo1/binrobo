Loads: {"wheel_carry": [2573.0, "B2F_estop12_rev_r2b.json"], "wheel_static": [1002.4, "B2F_static_crL_110_r2b.json"], "wheel_edge": [7306.0, "B2F_S6_kerb_v05_nose_t15_80cas.json"], "wheel_step_rigid_info": [22135.9, "B2F_S5_ESE240SL_step_v05.json"], "comb_carry": [2137.8, "B2F_towstab_r2b.json"], "comb_all": [9633.6, "B2F_S5_ESE240SL_step_v08_lsr004.json"], "comb_r2_max": [3706.5, "B2F_step40_both_r2b.json"], "torque_r2_max": [150.0, "B2F_climb_m22_c06_r2b.json"], "castor_static_r2": [719.8, "B2F_static_dn_110_r2b.json"], "lift_r2_max": [3000.0, "B2F_step40_both_r2b.json"]}

| element | case | force (N) | M (N m) | stress (MPa) | SF | note |
|---|---|---|---|---|---|---|
| side rail 50x50x4 S235 (sheet 13 item 1) | static | 1002 | 491.2 | 47.0 | 5.01 | B2F_static_crL_110_r2b.json |
| side rail 50x50x4 S235 (sheet 13 item 1) | carry | 2573 | 1260.8 | 120.5 | 1.95 | B2F_estop12_rev_r2b.json |
| side rail 50x50x4 S235 (sheet 13 item 1) | edge | 7306 | 3579.9 | 342.2 | 0.69 | B2F_S6_kerb_v05_nose_t15_80cas.json |
|   same, 80x80x5 (S12 edge fix, NOT drawn) | edge | 7306 | 3579.9 | 101.4 | 2.32 |  |
| mast upright 80x40x4 S235 at the foot (e 0.450 m) | carry | 2138 | 481.4 | 27.1 | 8.68 | B2F_towstab_r2b.json |
| mast-base cross-member 50x50x2 torsion (foot moment of one upright) - NOT in S12 | carry | 2138 | 481.4 | 52.2 | 2.60 |  |
|   same with 80x80x5 cross-member | carry | 2138 | 481.4 | 8.6 | 15.84 |  |
|   foot bolts M10 8.8, lever 35 mm (bolts inside the 45 mm the plate shares with the cross-member) ASSUMED | carry | 6877 | 481.4 | 118.6 | 5.40 |  |
|   foot bolts M12 8.8, lever 35 mm (bolts inside the 45 mm the plate shares with the cross-member) ASSUMED | carry | 6877 | 481.4 | 81.6 | 7.84 |  |
|   foot bolts M10 8.8, lever 80 mm (if the plate were fully supported) ASSUMED | carry | 3009 | 481.4 | 51.9 | 12.34 |  |
|   foot bolts M12 8.8, lever 80 mm (if the plate were fully supported) ASSUMED | carry | 3009 | 481.4 | 35.7 | 17.93 |  |
| mast upright 80x40x4 S235 at the foot (e 0.450 m) | comb_all | 9634 | 2169.5 | 122.0 | 1.93 | B2F_S5_ESE240SL_step_v08_lsr004.json |
| mast-base cross-member 50x50x2 torsion (foot moment of one upright) - NOT in S12 | comb_all | 9634 | 2169.5 | 235.4 | 0.58 |  |
|   same with 80x80x5 cross-member | comb_all | 9634 | 2169.5 | 38.6 | 3.52 |  |
|   foot bolts M10 8.8, lever 35 mm (bolts inside the 45 mm the plate shares with the cross-member) ASSUMED | comb_all | 30993 | 2169.5 | 534.4 | 1.20 |  |
|   foot bolts M12 8.8, lever 35 mm (bolts inside the 45 mm the plate shares with the cross-member) ASSUMED | comb_all | 30993 | 2169.5 | 367.6 | 1.74 |  |
|   foot bolts M10 8.8, lever 80 mm (if the plate were fully supported) ASSUMED | comb_all | 13559 | 2169.5 | 233.8 | 2.74 |  |
|   foot bolts M12 8.8, lever 80 mm (if the plate were fully supported) ASSUMED | comb_all | 13559 | 2169.5 | 160.8 | 3.98 |  |
| HGH15CA block, C0 23.47 kN, pitch 0.200 m (drawn) | carry | 2274 | 909.4 | - | 10.32 |  |
|   HGR15 rail screws M4 12.9 into 10 mm flat (2 per block length ASSUMED) | carry | 1137 | - | 129.5 | 8.34 |  |
|   same, M4 8.8 (grade not stated on the drawings) | carry | 1137 | - | 129.5 | 4.94 |  |
|   M4 thread strip in the 10 mm S235 flat | carry | 1137 | - | 15.1 | 8.99 |  |
| HGH15CA block, C0 23.47 kN, pitch 0.200 m (drawn) | comb_all | 10245 | 4098.1 | - | 2.29 |  |
|   HGR15 rail screws M4 12.9 into 10 mm flat (2 per block length ASSUMED) | comb_all | 5123 | - | 583.4 | 1.85 |  |
|   same, M4 8.8 (grade not stated on the drawings) | comb_all | 5123 | - | 583.4 | 1.10 |  |
|   M4 thread strip in the 10 mm S235 flat | comb_all | 5123 | - | 67.9 | 2.00 |  |
| comb plate 8 x 130 S355 (symmetric) | carry | 2138 | 106.2 | 4.7 | 75.36 |  |
| comb plate 8 x 130 S355 (one half at the roll stop) | carry | 2138 | 256.5 | 11.4 | 31.18 |  |
| comb pivot pin D16 8.8 (20 mm cantilever, S12 ASSUMED; size not on rev 2 drawings) | carry | 2138 | 42.8 | 106.3 | 6.02 |  |
| comb pivot pin D20 8.8 (20 mm cantilever, S12 ASSUMED; size not on rev 2 drawings) | carry | 2138 | 42.8 | 54.4 | 11.76 |  |
| comb plate 8 x 130 S355 (symmetric) | comb_all | 9634 | 478.4 | 21.2 | 16.72 |  |
| comb plate 8 x 130 S355 (one half at the roll stop) | comb_all | 9634 | 1156.0 | 51.3 | 6.92 |  |
| comb pivot pin D16 8.8 (20 mm cantilever, S12 ASSUMED; size not on rev 2 drawings) | comb_all | 9634 | 192.7 | 479.1 | 1.34 |  |
| comb pivot pin D20 8.8 (20 mm cantilever, S12 ASSUMED; size not on rev 2 drawings) | comb_all | 9634 | 192.7 | 245.3 | 2.61 |  |
| rocker bush D16 x 8 bronze (in 8 mm hanger plate), 70 mm apart, kerb 80 N m/wheel (S12) | kerb | 3310 | 193.9 | 25.9 | 2.32 | 60 MPa static bronze allowable ASSUMED |
|   pivot pin d16 8.8, couple applied at the housing, simply supported on the bushes | 80 N m/wheel (S12) | 3310 | 97.0 | 241.1 | 2.65 |  |
|   hanger plate 8 x 90 S235 weak axis, lever 160 mm (cross-member underside to pin) | 80 N m/wheel (S12) | 485 | 77.6 | 80.8 | 2.91 | plates drawn 6 mm clear of the cross-member: no joint |
| rocker bush D16 x 8 bronze (in 8 mm hanger plate), 70 mm apart, kerb 150 N m/wheel (peak logged in rev 2 gate files) | kerb | 5735 | 363.6 | 44.8 | 1.34 | 60 MPa static bronze allowable ASSUMED |
|   pivot pin d16 8.8, couple applied at the housing, simply supported on the bushes | 150 N m/wheel (peak logged in rev 2 gate files) | 5735 | 181.8 | 452.1 | 1.42 |  |
|   hanger plate 8 x 90 S235 weak axis, lever 160 mm (cross-member underside to pin) | 150 N m/wheel (peak logged in rev 2 gate files) | 909 | 145.5 | 151.5 | 1.55 | plates drawn 6 mm clear of the cross-member: no joint |
| castor beam 50x40x3 S235 (3 g on one castor, 0.28 m from pin) | static x3 | 1080 | 302.3 | 43.1 | 5.45 |  |
| bumper bracket upper arm 60 x 8 S235, weak-axis bending + torsion, 500 N lateral (person / post scrape) ASSUMED | knock | 250 | 38.8 | 82.7 | 2.84 |  |
| bumper bracket leg 30 x 8 S235 weak axis, 500 N lateral (person / post scrape) ASSUMED | knock | 250 | 30.0 | 93.8 | 2.51 |  |
| bumper bracket upper arm 60 x 8 S235, weak-axis bending + torsion, 970 N lateral (drive torque cap 80 N m, pivot turn against a post) | knock | 485 | 75.2 | 160.5 | 1.46 |  |
| bumper bracket leg 30 x 8 S235 weak axis, 970 N lateral (drive torque cap 80 N m, pivot turn against a post) | knock | 485 | 58.2 | 181.8 | 1.29 |  |
| bumper bracket upper arm 60 x 8 S235, weak-axis bending + torsion, 1818 N lateral (rev 2 logged torque peak) | knock | 909 | 140.9 | 300.8 | 0.78 |  |
| bumper bracket leg 30 x 8 S235 weak axis, 1818 N lateral (rev 2 logged torque peak) | knock | 909 | 109.1 | 340.9 | 0.69 |  |
| bumper bracket leg 30 x 8 in-plane, 970 N frontal | push | 485 | 69.8 | 58.2 | 4.04 |  |
| bumper bracket leg 30 x 8 in-plane, 1818 N frontal | push | 909 | 130.9 | 109.1 | 2.15 |  |
| actuator base bracket vertical plate 8 x 100 S235, 4 kN at 36 mm | lift | 4000 | 144.0 | 135.0 | 1.74 |  |
| actuator base bracket foot 10 x 100 S235, 4 kN at 36 mm | lift | 4000 | 144.0 | 86.4 | 2.72 |  |
| mast-base cross-member 50x50x2 torsion from actuator thrust (40 mm offset) | lift | 4000 | 160.0 | 17.4 | 7.81 |  |
| mast-base cross-member 50x50x2 bending, 4 kN at mid-span 0.81 m (simply supported ASSUMED) | lift | 4000 | 810.0 | 137.1 | 1.71 |  |
| lift hard stop = 2 rail clamps (1,200 N each, Zimmer HK1501A) vs actuator 4,000 N | overrun | 4000 | - | - | 0.60 |  |
