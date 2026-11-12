| lane-fit item (strict: any footprint point past a truth hedge face = FAIL) | B1 | Rev H |
|---|---|---|
| overall width (m) | 0.97 | 1.04 |
| 180 deg pivot diameter, empty / loaded (m) | 2.36 / 2.42 (loaded = MuJoCo G5 swept) | 2.16 / 2.16 (geometric; MuJoCo G5 swept 2.10) |
| lane sweep down loaded: least clearance to a hedge face (m), at s | 0.325 at s 501 | 0.333 at s 501 |
| lane sweep up loaded: least clearance to a hedge face (m), at s | 0.179 at s 417 | 0.180 at s 417 |
| margin over the SITL lateral-estimate p95 (0.124 m) | +0.055 | +0.056 |
| lane stations where a loaded 180 deg pivot fits between the faces | 100 % | 100 % |
| pivot at s 500-516 (2.9 m between faces): least margin (m) | 0.17 | 0.29 |
| dock: loaded 180 deg pivot within 2 m, 0-3 bins at home, margin (m) | 2.07 | 2.20 |
| yard: 180 deg pivot, 0-3 bins at home, margin (m) | 4.79 | 4.92 |
| bell-mouth: 180 deg pivot with 1-3 bins standing, margin (m) | 0.88 | 1.01 |

| pad sequence (G6 pads A, M, F; drop A-M-F, pickup F-M-A) | B1 result, least margin (m) | Rev H result, least margin (m) |
|---|---|---|
| drop n1 handles to the lane | PASS, 0.202 (A withdraw 0.9 m up-lane) | PASS, 0.007 (A empty pivot beyond the placed bin) |
| drop n1 handles to the road | PASS, 0.104 (A empty pivot beyond the placed bin) | PASS, 0.174 (A withdraw 0.9 m up-lane) |
| drop n2 handles to the lane | PASS, 0.202 (A withdraw 0.9 m up-lane) | PASS, 0.007 (A empty pivot beyond the placed bin) |
| drop n2 handles to the road | PASS, 0.047 (M empty pivot beyond the placed bin) | PASS, 0.174 (A withdraw 0.9 m up-lane) |
| drop n3 handles to the lane | PASS, 0.202 (A withdraw 0.9 m up-lane) | PASS, 0.007 (A empty pivot beyond the placed bin) |
| drop n3 handles to the road | PASS, 0.047 (M empty pivot beyond the placed bin) | PASS, 0.174 (A withdraw 0.9 m up-lane) |
| pickup n1 handles to the lane | PASS, 0.202 (A run-in 1.5 m onto the bin) | PASS, 0.199 (A pass the bin on the way down) |
| pickup n1 handles to the road | PASS, 0.175 (A pass the bin on the way down) | PASS, 0.174 (A run-in 1.5 m onto the bin) |
| pickup n2 handles to the lane | PASS, 0.202 (A run-in 1.5 m onto the bin) | PASS, 0.199 (A pass the bin on the way down) |
| pickup n2 handles to the road | PASS, 0.175 (A pass the bin on the way down) | PASS, 0.174 (A run-in 1.5 m onto the bin) |
| pickup n3 handles to the lane | PASS, 0.202 (A run-in 1.5 m onto the bin) | PASS, 0.199 (A pass the bin on the way down) |
| pickup n3 handles to the road | PASS, 0.175 (A pass the bin on the way down) | PASS, 0.174 (A run-in 1.5 m onto the bin) |
