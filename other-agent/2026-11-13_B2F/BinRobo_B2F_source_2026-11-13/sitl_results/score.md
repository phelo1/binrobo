# B2-F SITL strict score: 52 / 60 PASS

| run | expect | outcome | verdict | failed criteria |
|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | PASS | - |
| s1a__s11 | pass | pass / plan completed | PASS | - |
| s1a__s23 | pass | pass / plan completed | PASS | - |
| s1b__s7 | pass | pass / plan completed | PASS | - |
| s1b__s11 | pass | alert / grab gate | FAIL | C3 (first motion D0 18:00, last dock None), C6 (trips [] Wh, end SOC 0.863), C7 (result alert / grab gate), C8 (gates ['black -0.061 m -0.36 deg MISS', 'black -0.079 m -0.96 deg MISS']) |
| s1b__s23 | pass | alert / grab gate | FAIL | C3 (first motion D0 18:00, last dock None), C6 (trips [] Wh, end SOC 0.863), C7 (result alert / grab gate), C8 (gates ['black 0.082 m 1.34 deg MISS', 'black 0.064 m 0.75 deg MISS']) |
| s3a__s7 | pass | alert / firmware fence hold | FAIL | C1 (hedge min 0.012 m at t/s [195.0, 25.7]), C3 (first motion D-1 18:00, last dock None), C6 (trips [] Wh, end SOC 0.896), C7 (result alert / firmware fence hold) |
| s3a__s11 | pass | alert / firmware fence hold | FAIL | C1 (hedge min 0.071 m at t/s [195.0, 25.8]), C3 (first motion D-1 18:00, last dock None), C6 (trips [] Wh, end SOC 0.896), C7 (result alert / firmware fence hold) |
| s3a__s23 | pass | alert / firmware fence hold | FAIL | C1 (hedge min 0.033 m at t/s [194.4, 25.7]), C3 (first motion D-1 18:00, last dock None), C6 (trips [] Wh, end SOC 0.896), C7 (result alert / firmware fence hold) |
| s3b__s7 | pass | alert / grab gate | FAIL | C3 (first motion D0 18:00, last dock None), C6 (trips [] Wh, end SOC 0.864), C7 (result alert / grab gate), C8 (gates ['green -0.058 m 1.42 deg MISS', 'green -0.077 m 0.80 deg MISS']) |
| s3b__s11 | pass | pass / plan completed | PASS | - |
| s3b__s23 | pass | alert / grab gate | FAIL | C7 (result alert / grab gate) |
| s4a__s7 | pass | pass / plan completed | PASS | - |
| s4a__s11 | pass | pass / plan completed | PASS | - |
| s4a__s23 | pass | pass / plan completed | PASS | - |
| s4b__s7 | pass | pass / plan completed | PASS | - |
| s4b__s11 | pass | pass / plan completed | PASS | - |
| s4b__s23 | pass | alert / firmware fence hold | FAIL | C1 (hedge min 0.000 m at t/s [139.4, 68.6]), C7 (result alert / firmware fence hold) |
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
