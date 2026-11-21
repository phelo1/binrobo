# Revision 5 mission score

B2-F script as it stands: 48 / 60 PASS. With the time window and the energy budget restated for revision 5 (C3r, C6r): 55 / 60 PASS.

| run | expected | outcome | B2-F script | restated | failed (B2-F script) | failed (restated) | hedge min m |
|---|---|---|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [72.24] Wh, end SOC 0.744) | - | 0.215 |
| s1a__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.21] Wh, end SOC 0.749) | - | 0.213 |
| s1a__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.17] Wh, end SOC 0.749) | - | 0.208 |
| s1b__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [71.06] Wh, end SOC 0.747) | - | 0.245 |
| s1b__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.96] Wh, end SOC 0.747) | - | 0.24 |
| s1b__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [71.3] Wh, end SOC 0.746) | - | 0.251 |
| s3a__s7 | pass | pass / plan completed | FAIL | FAIL | C1 (hedge min 0.001 m at t/s [8306.5, 77.4]), C3 (first motion D-1 18:00, last dock D-1 21:16), C6 (trips [71.43, 70.4, 70.46] Wh, end SOC 0.429) | C1 (hedge min 0.001 m at t/s [8306.5, 77.4]) | 0.001 |
| s3a__s11 | pass | pass / plan completed | FAIL | PASS | C3 (first motion D-1 18:00, last dock D-1 21:15), C6 (trips [71.36, 70.12, 69.81] Wh, end SOC 0.431) | - | 0.221 |
| s3a__s23 | pass | pass / plan completed | FAIL | FAIL | C1 (hedge min 0.093 m at t/s [10049.9, 611.6]), C2 (pad:A 0.042 m 1.8 deg; pad:M 0.048 m 2.5 deg; pad:F 0.027 m 10.8 deg), C3 (first motion D-1 18:00, last dock D-1 21:17), C6 (trips [81.44, 83.99, 87.76] Wh, end SOC 0.338) | C1 (hedge min 0.093 m at t/s [10049.9, 611.6]), C2 (pad:A 0.042 m 1.8 deg; pad:M 0.048 m 2.5 deg; pad:F 0.027 m 10.8 deg), C6r (trips [81.44, 83.99, 87.76] Wh, end charge 34 %) | 0.093 |
| s3b__s7 | pass | alert / bin tipped | FAIL | FAIL | C3 (first motion D0 18:00, last dock None), C6 (trips [] Wh, end SOC 0.836), C7 (result alert / bin tipped) | C7 (result alert / bin tipped), C3r (first motion D0 18:00, last dock None), C6r (trips [] Wh, end charge 84 %) | 0.349 |
| s3b__s11 | pass | alert / too late | FAIL | FAIL | C6 (trips [70.41, 73.45] Wh, end SOC 0.581), C7 (result alert / too late) | C7 (result alert / too late) | 0.233 |
| s3b__s23 | pass | alert / too late | FAIL | FAIL | C6 (trips [70.48, 71.02] Wh, end SOC 0.586), C7 (result alert / too late) | C7 (result alert / too late) | 0.221 |
| s4a__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.27 |
| s4a__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.27 |
| s4a__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.27 |
| s4b__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.273 |
| s4b__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.273 |
| s4b__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.273 |
| s4c__s7 | alert | alert / no fix hold | PASS | PASS | - | - | 0.271 |
| s4c__s11 | alert | alert / no fix hold | PASS | PASS | - | - | 0.271 |
| s4c__s23 | alert | alert / no fix hold | PASS | PASS | - | - | 0.271 |
| s5a__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.373 |
| s5a__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.38 |
| s5a__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.38 |
| s5b__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.361 |
| s5b__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.36 |
| s5b__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.294 |
| s6a__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.367 |
| s6a__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.366 |
| s6a__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.285 |
| s6b__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.426 |
| s6b__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.452 |
| s6b__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.451 |
| s7__s7 | alert | alert / e-stop | PASS | PASS | - | - | 0.367 |
| s7__s11 | alert | alert / e-stop | PASS | PASS | - | - | 0.366 |
| s7__s23 | alert | alert / e-stop | PASS | PASS | - | - | 0.285 |
| s8__s7 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s8__s11 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s8__s23 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s9__s7 | alert | alert / bin missing | PASS | PASS | - | - | 0.379 |
| s9__s11 | alert | alert / bin missing | PASS | PASS | - | - | 0.379 |
| s9__s23 | alert | alert / bin missing | PASS | PASS | - | - | 0.379 |
| s10a__s7 | alert | alert / bin tipped | PASS | PASS | - | - | 0.378 |
| s10a__s11 | alert | alert / bin tipped | PASS | PASS | - | - | 0.368 |
| s10a__s23 | alert | alert / bin tipped | PASS | PASS | - | - | 0.379 |
| s10b__s7 | alert | alert / bin blocked | PASS | PASS | - | - | 0.379 |
| s10b__s11 | alert | alert / bin blocked | PASS | PASS | - | - | 0.367 |
| s10b__s23 | alert | alert / bin blocked | PASS | PASS | - | - | 0.377 |
| s11a__s7 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11a__s11 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11a__s23 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11b__s7 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s11b__s11 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s11b__s23 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s12a__s7 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.36 |
| s12a__s11 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.361 |
| s12a__s23 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.36 |
| s12b__s7 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.312 |
| s12b__s11 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.311 |
| s12b__s23 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.31 |
