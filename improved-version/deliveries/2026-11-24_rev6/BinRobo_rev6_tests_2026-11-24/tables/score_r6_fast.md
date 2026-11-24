# Revision 5 mission score

B2-F script as it stands: 45 / 60 PASS. With the time window and the energy budget restated for revision 5 (C3r, C6r): 57 / 60 PASS.

| run | expected | outcome | B2-F script | restated | failed (B2-F script) | failed (restated) | hedge min m |
|---|---|---|---|---|---|---|---|
| s1a__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [56.42] Wh, end SOC 0.778) | - | 0.215 |
| s1a__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [56.89] Wh, end SOC 0.777) | - | 0.194 |
| s1a__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [56.49] Wh, end SOC 0.778) | - | 0.197 |
| s1b__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [57.24] Wh, end SOC 0.777) | - | 0.254 |
| s1b__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [56.56] Wh, end SOC 0.778) | - | 0.243 |
| s1b__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [57.08] Wh, end SOC 0.777) | - | 0.238 |
| s3a__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [57.23, 56.33, 56.33] Wh, end SOC 0.523) | - | 0.211 |
| s3a__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [57.01, 56.91, 56.54] Wh, end SOC 0.521) | - | 0.201 |
| s3a__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [57.77, 56.61, 57.09] Wh, end SOC 0.519) | - | 0.207 |
| s3b__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [56.55, 56.99, 57.32] Wh, end SOC 0.520) | - | 0.206 |
| s3b__s11 | pass | pass / plan completed | FAIL | PASS | C6 (trips [56.22, 56.95, 57.77] Wh, end SOC 0.520) | - | 0.186 |
| s3b__s23 | pass | pass / plan completed | FAIL | PASS | C6 (trips [56.56, 56.71, 57.58] Wh, end SOC 0.520) | - | 0.199 |
| s4a__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.293 |
| s4a__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.293 |
| s4a__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4b__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4b__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4b__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.292 |
| s4c__s7 | alert | alert / no fix hold | PASS | PASS | - | - | 0.292 |
| s4c__s11 | alert | alert / no fix hold | PASS | PASS | - | - | 0.292 |
| s4c__s23 | alert | alert / no fix hold | PASS | PASS | - | - | 0.292 |
| s5a__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.366 |
| s5a__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.38 |
| s5a__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.38 |
| s5b__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.361 |
| s5b__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.355 |
| s5b__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.353 |
| s6a__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.314 |
| s6a__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.368 |
| s6a__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.346 |
| s6b__s7 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.383 |
| s6b__s11 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.43 |
| s6b__s23 | alert | alert / companion freeze -> firmware HOLD | PASS | PASS | - | - | 0.261 |
| s7__s7 | alert | alert / e-stop | PASS | PASS | - | - | 0.368 |
| s7__s11 | alert | alert / e-stop | PASS | PASS | - | - | 0.353 |
| s7__s23 | alert | alert / e-stop | PASS | PASS | - | - | 0.346 |
| s8__s7 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s8__s11 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s8__s23 | alert | alert / energy guard | PASS | PASS | - | - | None |
| s9__s7 | alert | alert / bin missing | PASS | PASS | - | - | 0.332 |
| s9__s11 | alert | alert / bin missing | PASS | PASS | - | - | 0.381 |
| s9__s23 | alert | alert / bin missing | PASS | PASS | - | - | 0.369 |
| s10a__s7 | alert | alert / bin tipped | PASS | PASS | - | - | 0.343 |
| s10a__s11 | alert | alert / bin tipped | PASS | PASS | - | - | 0.381 |
| s10a__s23 | alert | alert / bin tipped | PASS | PASS | - | - | 0.381 |
| s10b__s7 | alert | alert / path blocked | FAIL | FAIL | C7 (result alert / path blocked (expected alert: bin blocked)) | C7 (result alert / path blocked (expected alert: bin blocked)) | 0.35 |
| s10b__s11 | alert | alert / path blocked | FAIL | FAIL | C7 (result alert / path blocked (expected alert: bin blocked)) | C7 (result alert / path blocked (expected alert: bin blocked)) | 0.381 |
| s10b__s23 | alert | alert / path blocked | FAIL | FAIL | C7 (result alert / path blocked (expected alert: bin blocked)) | C7 (result alert / path blocked (expected alert: bin blocked)) | 0.375 |
| s11a__s7 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11a__s11 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11a__s23 | alert | alert / wind no-go | PASS | PASS | - | - | None |
| s11b__s7 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s11b__s11 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s11b__s23 | alert | alert / frost no-go | PASS | PASS | - | - | None |
| s12a__s7 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.36 |
| s12a__s11 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.361 |
| s12a__s23 | alert | alert / pad outside geofence | PASS | PASS | - | - | 0.36 |
| s12b__s7 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.322 |
| s12b__s11 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.323 |
| s12b__s23 | alert | alert / firmware fence hold | PASS | PASS | - | - | 0.319 |
