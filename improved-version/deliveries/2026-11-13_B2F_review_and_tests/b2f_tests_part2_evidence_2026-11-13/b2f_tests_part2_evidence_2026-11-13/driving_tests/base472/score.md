# B2-F SITL strict score: 55 / 58 PASS

| run | expect | outcome | verdict | failed criteria |
|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | PASS | - |
| s1a__s11 | pass | pass / plan completed | PASS | - |
| s1a__s23 | pass | pass / plan completed | PASS | - |
| s1b__s7 | pass | pass / plan completed | PASS | - |
| s1b__s11 | pass | pass / plan completed | PASS | - |
| s1b__s23 | pass | pass / plan completed | PASS | - |
| s3a__s7 | pass | alert / firmware fence hold | FAIL | C1 (hedge min 0.010 m at t/s [196.0, 25.6]), C3 (first motion D-1 18:00, last dock None), C6 (trips [] Wh, end SOC 0.896), C7 (result alert / firmware fence hold) |
| s3a__s11 | pass | alert / firmware fence hold | FAIL | C1 (hedge min 0.010 m at t/s [197.2, 25.6]), C3 (first motion D-1 18:00, last dock None), C6 (trips [] Wh, end SOC 0.896), C7 (result alert / firmware fence hold) |
| s3a__s23 | pass | alert / firmware fence hold | FAIL | C3 (first motion D-1 18:00, last dock None), C6 (trips [] Wh, end SOC 0.896), C7 (result alert / firmware fence hold) |
| s3b__s7 | pass | pass / plan completed | PASS | - |
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
