# B2-F SITL strict score: 48 / 60 PASS

| run | expect | outcome | verdict | failed criteria |
|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | FAIL | C6 (trips [70.0] Wh, end SOC 0.749) |
| s1a__s11 | pass | pass / plan completed | FAIL | C6 (trips [70.09] Wh, end SOC 0.749) |
| s1a__s23 | pass | pass / plan completed | FAIL | C6 (trips [70.11] Wh, end SOC 0.749) |
| s1b__s7 | pass | pass / plan completed | FAIL | C6 (trips [70.85] Wh, end SOC 0.747) |
| s1b__s11 | pass | pass / plan completed | FAIL | C6 (trips [70.86] Wh, end SOC 0.747) |
| s1b__s23 | pass | pass / plan completed | FAIL | C6 (trips [71.11] Wh, end SOC 0.747) |
| s3a__s7 | pass | pass / plan completed | FAIL | C3 (first motion D-1 18:00, last dock D-1 21:18), C6 (trips [71.78, 69.68, 69.8] Wh, end SOC 0.431) |
| s3a__s11 | pass | pass / plan completed | FAIL | C3 (first motion D-1 18:00, last dock D-1 21:17), C6 (trips [71.45, 69.88, 69.16] Wh, end SOC 0.432) |
| s3a__s23 | pass | pass / plan completed | FAIL | C3 (first motion D-1 18:00, last dock D-1 21:18), C6 (trips [72.13, 70.55, 70.32] Wh, end SOC 0.427) |
| s3b__s7 | pass | alert / too late | FAIL | C6 (trips [71.53, 72.31] Wh, end SOC 0.581), C7 (result alert / too late) |
| s3b__s11 | pass | alert / too late | FAIL | C6 (trips [70.3, 71.57] Wh, end SOC 0.585), C7 (result alert / too late) |
| s3b__s23 | pass | alert / too late | FAIL | C6 (trips [70.71, 71.47] Wh, end SOC 0.584), C7 (result alert / too late) |
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
