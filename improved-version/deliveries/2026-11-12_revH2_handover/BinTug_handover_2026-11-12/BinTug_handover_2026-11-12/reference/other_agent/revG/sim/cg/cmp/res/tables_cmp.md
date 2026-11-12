| item | Rev H as designed (raw) | Rev H + FH1 + FH2 (2 firmware fixes) | B1 final (160 mm comb) | B1 + 640 mm full-width comb |
|---|---|---|---|---|
| G1 | **FAIL** WEB 30/30 / SL 0/30 / CL 0/30; pooled 30/90; FH 50; knocked 0 | **PASS** WEB 30/30 / SL 29/30 / CL 29/30; pooled 88/90; FH 0; knocked 0 | **PASS** WEB 30/30 / SL 30/30 / CL 30/30; pooled 90/90; FH 0; knocked 0 | **PASS** WEB 29/30 / SL 30/30 / CL 30/30; pooled 89/90; FH 0; knocked 0 |
| G2 | **FAIL** 0/6; 11.1-25.0 s; creep <= 0.044 m; fail: mu0.30 crr0.06 (grab false_positive, 5.00 m), mu0.30 crr0.09 (grab false_positive, 5.00 m), mu0.25 crr0.06 (grab false_positive, 5.00 m), mu0.25 crr0.09 (grab false_positive, 5.00 m), mu0.22 crr0.06 (grab false_positive, 4.48 m), mu0.22 crr0.09 (grab false_positive, 1.65 m) | **PASS** 6/6; 11.0-11.0 s; creep <= 0.043 m | **PASS** 6/6; 11.1-11.1 s; creep <= 0.035 m | **PASS** 6/6; 11.1-11.1 s; creep <= 0.035 m *[1 of 6 runs re-run with the 640 mm comb, rest inherited]* |
| G3 | **FAIL** one side FAIL (4.69 m, grab false_positive, bin-ground 2319 N, seated True); full width FAIL (1.35 m, grab false_positive, bin-ground 2876 N, seated True) | **FAIL** one side PASS (4.69 m, clear 47 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) | **FAIL** one side PASS (4.69 m, clear 88 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) | **FAIL** one side PASS (4.69 m, clear 83 mm); full width FAIL (1.34 m, grab success, bin-ground 0 N, seated True) *[1 of 2 runs re-run with the 640 mm comb, rest inherited]* |
| G4 | **FAIL** fwd FAIL 0.34 m, slide 0.003 / rev FAIL 0.10 m, slide 0.001 | **PASS** fwd PASS 0.20 m, slide 0.001 / rev PASS 0.09 m, slide 0.001 | **PASS** fwd PASS 0.16 m, slide 0.001 / rev PASS 0.08 m, slide 0.001 | **PASS** fwd PASS 0.15 m, slide 0.001 / rev PASS 0.08 m, slide 0.001 |
| G5 | **FAIL** FAIL; roll 0.00 deg; pivot swept 2.10 m | **PASS** PASS; roll 0.01 deg; pivot swept 2.10 m | **PASS** PASS; roll 0.00 deg; pivot swept 2.42 m | **PASS** PASS; roll 0.00 deg; pivot swept 2.42 m |
| G6 | **FAIL** 6/18, 0 TIPS; CL flat full FAIL, CL flat empty FAIL, CL up12 full FAIL, CL up12 empty FAIL, CL dn12 full FAIL, CL dn12 empty FAIL, SL250 flat full FAIL, SL250 flat empty FAIL, SL250 up12 full FAIL, SL250 up12 empty FAIL, SL250 dn12 full FAIL, SL250 dn12 empty FAIL | **FAIL** 15/18, 0 TIPS; SL250 flat full FAIL, SL250 up12 full FAIL, SL250 dn12 full FAIL | **PASS** 18/18, 0 TIPS | **PASS** 18/18, 0 TIPS |
| G7 | **PASS** climb_m25_c09 base False / dt025 False t 14.4/14.3 s; step40_one base False / dt025 False; estop12_fwd base False / dt025 False | **PASS** climb_m25_c09 base True / dt025 True t 11.0/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True | **PASS** climb_m25_c09 base True / dt025 True t 11.1/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True | **PASS** climb_m25_c09 base True / dt025 True t 11.1/11.0 s; step40_one base True / dt025 True; estop12_fwd base True / dt025 True *[inherited from B1 final]* |
| G8 | **FAIL** 0/8 poses; drive >= 362 N, castors >= 272 N; hand-calc min tip 40.9 deg; fail: up 110, up 60, dn 110, dn 60, crL 110, crL 60, crR 110, crR 60 | **PASS** 8/8 poses; drive >= 454 N, castors >= 268 N; hand-calc min tip 40.9 deg | **PASS** 8/8 poses; drive >= 460 N, castors >= 294 N; hand-calc min tip 39.4 deg | **PASS** 8/8 poses; drive >= 460 N, castors >= 294 N; hand-calc min tip 39.4 deg *[inherited from B1 final]* |
| G9 | **PASS** 85.5 kg | **PASS** 85.5 kg | **PASS** 94.1 kg | **PASS** 94.1 kg (+1.6 kg comb, est.: 95.7 kg) |
| **items passed** | **2/9** | **7/9** | **8/9** | **8/9** |

Extra grab Monte Carlos (reported, not gating):

- B1 final: ESE240SL250 30/30, FH 0, knocked 0; ESE140CL 29/30, FH 0, knocked 0
- Rev H raw: ESE240SL250 0/30, FH 14, knocked 0; ESE140CL 30/30, FH 0, knocked 0
- Rev H + FH1 + FH2: ESE240SL250 11/30, FH 3, knocked 0; ESE140CL 30/30, FH 0, knocked 0
- G3(b) with a 1:4 kerb ramp: B1 PASS (4.71 m, grab success, bin-ground 0 N); Rev H raw FAIL (4.71 m, grab false_positive, bin-ground 674 N); Rev H fixed PASS (4.71 m, grab success, bin-ground 0 N)

| B1 comb (G1, F9) | WEB 140 | ESE 240 SL | ESE 240 CL | pooled | FH | knocked | SL 250 (extra) | ESE 140 CL (extra) |
|---|---|---|---|---|---|---|---|---|
| 160 mm (final B1), gate lip | 30/30 | 30/30 | 30/30 | 90/90 | 0 | 0 | 30/30 | 29/30 |
| 160 mm, EN 840 lip | 30/30 | 30/30 | 30/30 | 90/90 | 0 | 0 | not run | not run |
| 640 mm rigid, EN 840 lip | 30/30 | 27/30 | 29/30 | 86/90 | 0 | 0 | not run | not run |
| 640 mm self-aligning, EN 840 lip | 29/30 | 30/30 | 30/30 | 89/90 | 0 | 0 | 30/30 | 29/30 |

B1 with the 640 mm self-aligning comb, other affected groups: G6 set-down 18/18 PASS, 0 TIPS; G5 towstab PASS; G3(a) one side PASS; G4 fwd PASS; G4 rev PASS; G2 mu 0.22 crr 0.09 PASS.

| design, perturbation | G1 (10 per bin) | G2 mu 0.22 / 0.25 | G3 one side | G4 fwd / rev | G5 | G6 6 hardest | G8 3 poses |
|----|----|----|----|----|----|----|----|
| B1, mass +10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.1 s / PASS 11.1 s | PASS | PASS 0.15 m / PASS 0.08 m | PASS 2.43 m | 6/6 | 3/3 |
| B1, mass -10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.0 s / PASS 11.0 s | PASS | PASS 0.14 m / PASS 0.09 m | PASS 2.40 m | 6/6 | 3/3 |
| B1, mu -15 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.8 s / PASS 11.2 s | PASS | PASS 0.22 m / PASS 0.11 m | PASS 2.40 m | 6/6 | 3/3 |
| B1, bin crr 0.09 | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.1 s / PASS 11.1 s | PASS | PASS 0.16 m / PASS 0.08 m | PASS 2.42 m | 6/6 | 3/3 |
| Rev H fixed, mass +10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.1 s / PASS 11.0 s | PASS | PASS 0.20 m / PASS 0.08 m | PASS 2.12 m | 5/6 | 3/3 |
| Rev H fixed, mass -10 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.0 s / PASS 10.9 s | PASS | PASS 0.19 m / PASS 0.09 m | PASS 2.08 m | 5/6 | 3/3 |
| Rev H fixed, mu -15 % | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.8 s / PASS 11.1 s | PASS | PASS 0.29 m / PASS 0.12 m | PASS 2.08 m | 5/6 | 3/3 |
| Rev H fixed, bin crr 0.09 | 10/10 / 10/10 / 10/10; FH 0, kn 0 | PASS 11.0 s / PASS 11.0 s | PASS | PASS 0.21 m / PASS 0.09 m | PASS 2.10 m | 5/6 | 3/3 |

Peak loads over the carry runs (G2-G6, dt 0.5 ms): B1: lift_N 3000 (B1_step40_one_f9), pad_N 1063 (B1_step40_both_f9), nib_rim_N 3838 (B1_step40_one_f9); Hraw: lift_N 3000 (H_step40_one_rw318_raw), pad_N 1304 (H_step40_one_rw318_raw), nib_rim_N 3044 (H_step40_one_rw318_raw); Hfx: lift_N 3000 (H_step40_one_rw318_fx), pad_N 1480 (H_step40_one_rw318_fx), nib_rim_N 2723 (H_step40_one_rw318_fx); FW: lift_N 1952 (B1_step40_one_f9_fwp32), pad_N 1073 (B1_towstab_f9_fwp32), nib_rim_N 2806 (B1_step40_one_f9_fwp32)
