# Revision 5 mission score

B2-F script as it stands: 48 / 60 PASS. With the time window and the energy budget restated for revision 5 (C3r, C6r): 57 / 60 PASS.

| run | expected | outcome | B2-F script | restated | failed (B2-F script) | failed (restated) | hedge min m |
|---|---|---|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.0] Wh, end SOC 0.749) | - | 0.208 |
| s1a__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.09] Wh, end SOC 0.749) | - | 0.202 |
| s1a__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.11] Wh, end SOC 0.749) | - | 0.197 |
| s1b__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.85] Wh, end SOC 0.747) | - | 0.224 |
| s1b__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [70.86] Wh, end SOC 0.747) | - | 0.234 |
| s1b__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [71.11] Wh, end SOC 0.747) | - | 0.244 |
| s3a__s7 | pass | pass / plan completed | FAIL | PASS | C3 (first motion D-1 18:00, last dock D-1 21:18), C6 (trips [71.78, 69.68, 69.8] Wh, end SOC 0.431) | - | 0.217 |
| s3a__s11 | pass | pass / plan completed | FAIL | PASS | C3 (first motion D-1 18:00, last dock D-1 21:17), C6 (trips [71.45, 69.88, 69.16] Wh, end SOC 0.432) | - | 0.196 |
| s3a__s23 | pass | pass / plan completed | FAIL | PASS | C3 (first motion D-1 18:00, last dock D-1 21:18), C6 (trips [72.13, 70.55, 70.32] Wh, end SOC 0.427) | - | 0.204 |
| s3b__s7 | pass | alert / too late | FAIL | FAIL | C6 (trips [71.53, 72.31] Wh, end SOC 0.581), C7 (result alert / too late) | C7 (result alert / too late) | 0.232 |
| s3b__s11 | pass | alert / too late | FAIL | FAIL | C6 (trips [70.3, 71.57] Wh, end SOC 0.585), C7 (result alert / too late) | C7 (result alert / too late) | 0.228 |
| s3b__s23 | pass | alert / too late | FAIL | FAIL | C6 (trips [70.71, 71.47] Wh, end SOC 0.584), C7 (result alert / too late) | C7 (result alert / too late) | 0.233 |
| s4a__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.293 |
| s4a__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4a__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.293 |
| s4b__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4b__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4b__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4c__s7 | alert | alert / no fix hold | PASS | PASS | - | - | 0.292 |
| s4c__s11 | alert | alert / no fix hold | PASS | PASS | - | - | 0.292 |
| s4c__s23 | alert | alert / no fix hold | PASS | PASS | - | - | 0.292 |
| s5a__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.372 |
| s5a__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.38 |
| s5a__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.38 |
| s5b__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.361 |
| s5b__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.36 |
| s5b__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.345 |
| s6a__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.36 |
| s6a__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.367 |
| s6a__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.34 |
| s6b__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.358 |
| s6b__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.418 |
| s6b__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.445 |
| s7__s7 | alert | alert / e-stop | PASS | PASS | - | - | 0.36 |
| s7__s11 | alert | alert / e-stop | PASS | PASS | - | - | 0.367 |
| s7__s23 | alert | alert / e-stop | PASS | PASS | - | - | 0.34 |
| s8__s7 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s8__s11 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s8__s23 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s9__s7 | alert | alert / bin missing | PASS | PASS | - | - | 0.379 |
| s9__s11 | alert | alert / bin missing | PASS | PASS | - | - | 0.376 |
| s9__s23 | alert | alert / bin missing | PASS | PASS | - | - | 0.379 |
| s10a__s7 | alert | alert / bin tipped | PASS | PASS | - | - | 0.38 |
| s10a__s11 | alert | alert / bin tipped | PASS | PASS | - | - | 0.374 |
| s10a__s23 | alert | alert / bin tipped | PASS | PASS | - | - | 0.379 |
| s10b__s7 | alert | alert / bin blocked | PASS | PASS | - | - | 0.379 |
| s10b__s11 | alert | alert / bin blocked | PASS | PASS | - | - | 0.368 |
| s10b__s23 | alert | alert / bin blocked | PASS | PASS | - | - | 0.379 |
| s11a__s7 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11a__s11 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11a__s23 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11b__s7 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s11b__s11 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s11b__s23 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s12a__s7 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.36 |
| s12a__s11 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.361 |
| s12a__s23 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.36 |
| s12b__s7 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.311 |
| s12b__s11 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.313 |
| s12b__s23 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.31 |
