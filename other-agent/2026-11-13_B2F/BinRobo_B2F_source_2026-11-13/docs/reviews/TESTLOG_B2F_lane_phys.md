# TESTLOG - B2-F lane physics (MuJoCo)

| id | run | result | key numbers | file |
|---|---|---|---|---|
| P1 | v3 | PASS | clear 13.6 mm @290.2 (1:4 ramp), hedge 0.299 m, lift 2,210 N, tip 21.8, 15.3 Wh | runs/P1 |
| P2a | v1 | FAIL | stall s 550.0 in 60 mm pothole (empty tug) | runs/P2a |
| P2c | v1 | FAIL | grab ok; stall s 549.8 in pothole (13 kg bin) | runs/P2c |
| P2a_pf | suppl | FAIL | wet-leaf slip/yaw s 163-149, hedge -2.89 m, stall s 163.3 | runs/P2a_pf |
| P2c_pf | suppl | FAIL | yaw at s 149.4, hedge -1.125 m; reached home, set-down ok | runs/P2c_pf |
| P3 | v1 | PASS | clear 53.9 mm, hedge 0.299 m, lift 1,736 N, tip 32.8, 15.3 Wh | runs/P3 |
| P4a | v1 | PASS | hold creep 0.5 mm/3 s on -12 % mu 0.35 | runs/P4a |
| P4b | v2 | PASS | pivot on slope, hold creep 0.5 mm/3 s (v1 kept: _P4b_v1_lowspeed) | runs/P4b |
| P5a/b | v1 | PASS | sharp drop: clear 2.9/3.2 mm, lift at cap | runs/P5a*, P5b* |
| P5c | v1 | PASS | 1:4 drop: clear 13.6 mm | runs/P5c* |
| P5d/e | v1 | FAIL | sharp up-step stall s 290.1 (3 kN and 4 kN) | runs/P5d*, P5e* |
| P5f | v1 | PASS | 1:4 up: clear 47.1 mm | runs/P5f* |
| P5g/i | v1 | FAIL | open trench stall s 455.1, bin-ground 458/468 N (3 kN / 4 kN) | runs/P5g*, P5i* |
| P5h | v1 | PASS | pothole: clear 33.9 mm, lift 2,210 N | runs/P5h* |
| P6a | v2 | PASS | e-stop 0.116 m from 0.52 m/s, slide 0.5 mm, gap 1.35 m | runs/P6a* |
| P6b | v3 | PASS | controlled stop at 1.93 m, resume; gap 1.75 m | runs/P6b* |
| P7 | v1 | FAIL | trapped in pothole s 550.4 (mu 0.48) -> timeout; clear 11.2 mm at step | runs/P7 |
