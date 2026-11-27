# Revision 5 mission score

B2-F script as it stands: 3 / 6 PASS. With the time window and the energy budget restated for revision 5 (C3r, C6r): 6 / 6 PASS.

| run | expected | outcome | B2-F script | restated | failed (B2-F script) | failed (restated) | hedge min m |
|---|---|---|---|---|---|---|---|
| s1b__s7 | pass | pass / plan completed | FAIL | PASS | C6 (trips [74.48] Wh, end SOC 0.740) | - | 0.209 |
| s3a__s7 | pass | pass / plan completed | FAIL | PASS | C3 (first motion D-1 18:00, last dock D-1 21:31), C6 (trips [74.58, 71.44, 71.59] Wh, end SOC 0.417) | - | 0.213 |
| s3b__s7 | pass | pass / plan completed | FAIL | PASS | C3 (first motion D0 16:30, last dock D0 20:16), C6 (trips [73.53, 73.83, 74.51] Wh, end SOC 0.407) | - | 0.197 |
| s5a__s7 | pass | pass / plan completed | PASS | PASS | - | - | 0.376 |
| s5a__s11 | pass | pass / plan completed | PASS | PASS | - | - | 0.338 |
| s5a__s23 | pass | pass / plan completed | PASS | PASS | - | - | 0.37 |

