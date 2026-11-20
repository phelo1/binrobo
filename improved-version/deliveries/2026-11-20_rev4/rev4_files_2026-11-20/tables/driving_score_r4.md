# B2-F SITL strict score: 48 / 60 PASS

| run | expect | outcome | verdict | failed criteria |
|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | FAIL | C6 (trips [68.6] Wh, end SOC 0.752) |
| s1a__s11 | pass | pass / plan completed | FAIL | C6 (trips [74.05] Wh, end SOC 0.741) |
| s1a__s23 | pass | pass / plan completed | FAIL | C6 (trips [67.77] Wh, end SOC 0.754) |
| s1b__s7 | pass | pass / plan completed | FAIL | C6 (trips [70.0] Wh, end SOC 0.749) |
| s1b__s11 | pass | alert / grab refused, back on the dock | FAIL | C6 (trips [67.09] Wh, end SOC 0.755), C7 (result alert / grab refused, back on the dock) |
| s1b__s23 | pass | pass / plan completed | FAIL | C6 (trips [70.55] Wh, end SOC 0.748) |
| s3a__s7 | pass | alert / too late | FAIL | C6 (trips [70.32, 67.3] Wh, end SOC 0.594), C7 (result alert / too late) |
| s3a__s11 | pass | alert / too late | FAIL | C6 (trips [70.25, 67.88] Wh, end SOC 0.593), C7 (result alert / too late) |
| s3a__s23 | pass | alert / too late | FAIL | C6 (trips [72.22, 71.08] Wh, end SOC 0.582), C7 (result alert / too late) |
| s3b__s7 | pass | alert / too late | FAIL | C6 (trips [69.19, 70.62] Wh, end SOC 0.589), C7 (result alert / too late), C8 (gates ['green -0.013 m 0.54 deg OK', 'black 0.006 m -3.31 deg MISS']) |
| s3b__s11 | pass | alert / too late | FAIL | C6 (trips [69.36, 70.11] Wh, end SOC 0.590), C7 (result alert / too late) |
| s3b__s23 | pass | alert / grab refused, back on the dock | FAIL | C6 (trips [72.44, 74.71] Wh, end SOC 0.573), C7 (result alert / grab refused, back on the dock) |
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
