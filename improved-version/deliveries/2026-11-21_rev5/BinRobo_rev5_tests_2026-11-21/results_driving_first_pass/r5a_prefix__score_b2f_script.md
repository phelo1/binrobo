# B2-F SITL strict score: 48 / 60 PASS

| run | expect | outcome | verdict | failed criteria |
|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | FAIL | C6 (trips [72.24] Wh, end SOC 0.744) |
| s1a__s11 | pass | pass / plan completed | FAIL | C6 (trips [70.21] Wh, end SOC 0.749) |
| s1a__s23 | pass | pass / plan completed | FAIL | C6 (trips [70.17] Wh, end SOC 0.749) |
| s1b__s7 | pass | pass / plan completed | FAIL | C6 (trips [71.06] Wh, end SOC 0.747) |
| s1b__s11 | pass | pass / plan completed | FAIL | C6 (trips [70.96] Wh, end SOC 0.747) |
| s1b__s23 | pass | pass / plan completed | FAIL | C6 (trips [71.3] Wh, end SOC 0.746) |
| s3a__s7 | pass | pass / plan completed | FAIL | C1 (hedge min 0.001 m at t/s [8306.5, 77.4]), C3 (first motion D-1 18:00, last dock D-1 21:16), C6 (trips [71.43, 70.4, 70.46] Wh, end SOC 0.429) |
| s3a__s11 | pass | pass / plan completed | FAIL | C3 (first motion D-1 18:00, last dock D-1 21:15), C6 (trips [71.36, 70.12, 69.81] Wh, end SOC 0.431) |
| s3a__s23 | pass | pass / plan completed | FAIL | C1 (hedge min 0.093 m at t/s [10049.9, 611.6]), C2 (pad:A 0.042 m 1.8 deg; pad:M 0.048 m 2.5 deg; pad:F 0.027 m 10.8 deg), C3 (first motion D-1 18:00, last dock D-1 21:17), C6 (trips [81.44, 83.99, 87.76] Wh, end SOC 0.338) |
| s3b__s7 | pass | alert / bin tipped | FAIL | C3 (first motion D0 18:00, last dock None), C6 (trips [] Wh, end SOC 0.836), C7 (result alert / bin tipped) |
| s3b__s11 | pass | alert / too late | FAIL | C6 (trips [70.41, 73.45] Wh, end SOC 0.581), C7 (result alert / too late) |
| s3b__s23 | pass | alert / too late | FAIL | C6 (trips [70.48, 71.02] Wh, end SOC 0.586), C7 (result alert / too late) |
| s4a__s7 | pass | pass / plan completed | PASS | - |
| s4a__s11 | pass | pass / plan completed | PASS | - |
| s4a__s23 | pass | pass / plan completed | PASS | - |
| s4b__s7 | pass | pass / plan completed | PASS | - |
| s4b__s11 | pass | pass / plan completed | PASS | - |
| s4b__s23 | pass | pass / plan completed | PASS | - |
| s4c__s7 | alert | alert / no fix hold | PASS | - |
| s4c__s11 | alert | alert / no fix hold | PASS | - |
| s4c__s23 | alert | alert / no fix hold | PASS | - |
| s5a__s7 | pass | pass / plan completed | PASS | - |
| s5a__s11 | pass | pass / plan completed | PASS | - |
| s5a__s23 | pass | pass / plan completed | PASS | - |
| s5b__s7 | pass | pass / plan completed | PASS | - |
| s5b__s11 | pass | pass / plan completed | PASS | - |
| s5b__s23 | pass | pass / plan completed | PASS | - |
| s6a__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | - |
| s6a__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | - |
| s6a__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | - |
| s6b__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | - |
| s6b__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | - |
| s6b__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | - |
| s7__s7 | alert | alert / e-stop | PASS | - |
| s7__s11 | alert | alert / e-stop | PASS | - |
| s7__s23 | alert | alert / e-stop | PASS | - |
| s8__s7 | alert | alert / energy guard | PASS | - |
| s8__s11 | alert | alert / energy guard | PASS | - |
| s8__s23 | alert | alert / energy guard | PASS | - |
| s9__s7 | alert | alert / bin missing | PASS | - |
| s9__s11 | alert | alert / bin missing | PASS | - |
| s9__s23 | alert | alert / bin missing | PASS | - |
| s10a__s7 | alert | alert / bin tipped | PASS | - |
| s10a__s11 | alert | alert / bin tipped | PASS | - |
| s10a__s23 | alert | alert / bin tipped | PASS | - |
| s10b__s7 | alert | alert / bin blocked | PASS | - |
| s10b__s11 | alert | alert / bin blocked | PASS | - |
| s10b__s23 | alert | alert / bin blocked | PASS | - |
| s11a__s7 | alert | alert / wind no-go | PASS | - |
| s11a__s11 | alert | alert / wind no-go | PASS | - |
| s11a__s23 | alert | alert / wind no-go | PASS | - |
| s11b__s7 | alert | alert / frost no-go | PASS | - |
| s11b__s11 | alert | alert / frost no-go | PASS | - |
| s11b__s23 | alert | alert / frost no-go | PASS | - |
| s12a__s7 | alert | alert / pad outside geofence | PASS | - |
| s12a__s11 | alert | alert / pad outside geofence | PASS | - |
| s12a__s23 | alert | alert / pad outside geofence | PASS | - |
| s12b__s7 | alert | alert / firmware fence hold | PASS | - |
| s12b__s11 | alert | alert / firmware fence hold | PASS | - |
| s12b__s23 | alert | alert / firmware fence hold | PASS | - |
