### 3.9 Drawing checks

- 17 sheets. New: sheet 17 (bolt table with torques, lift stop order, speed rule, lowering, what to ask of the bought-in safety parts, three close-ups of the bolted joints). Sheet 15 (safety chain) and sheet 16 (dimensions) are redrawn.
- Solid-overlap check on the final model: 15 overlaps, all inherited from the B2-F CAD (anti-tip brackets, flares, stripes); none involves a part I drew. The pair you found in m-2 is no longer excused and is clear.
- Lift sweep in 1 mm steps: first contacts are the carriage beams on the stop blocks at −18 and +335 mm, then the switch bodies. No loom centre-line passes through a solid.
- The weight table is built from the same solids as the drawings: 177.60 kg.

## 8. Decisions for Brian

1. **Speed against bins per evening.** As drawn, revision 4 is safe by simulation with margin, but slower: two bins fit between 18:00 and 21:00, not three. To get three back there are two routes. Brakes on the castors are the better one: trips of 55 minutes, three bins home by 20:45, and they also fix the empty robot on the steep pitch. They need designing (I did not find a catalogue castor with an electric brake) and add about 4 kg. The other route, a faster rule with a deeper bumper, only just makes 21:00 and leaves no margin; I do not recommend it. I would also like to know what the 21:00 limit is: the bin at the road by then, or the robot home by then?
2. **Measure the lane.** Two numbers decide a lot: the steepest slope (the model assumes 12 %; the map data says 7.9 % at most) and whether any edge across the lane is higher than 20 mm. If the slope is under 9 %, the tail-first problem disappears. If there are edges over 20 mm, they need a small ramp.
3. **Weight.** Revision 4 is 177.6 kg and will not come down while everything is bolted and the bumper is 300 mm deep. I suggest dropping the 120 kg test, judging on the functional results, and capping a weighed prototype at 190 kg.
4. **Bolted or welded.** Bolting everything costs about 10 kg. If a fabricator welds the four frame corners and the two mast feet, about 8 kg comes back.
5. **Actuator.** An outdoor 6.8 kN unit that holds 8.8 kN, in place of the 4 kN unit whose data conflict. It costs more and weighs about 3 kg more.
6. **Revision 5.** If you agree: the 60 x 60 nose cross-member, castor brakes, tail-first or angled driving in the software where still needed, and a brake test at start-up.
7. **A qualified person** has to check the safety design before the robot runs unattended (section 5). That has not changed.
8. Still wanted from you, as before: the make and measurements of your own bins.

## 9. For the B2-F author: facts I need for my own testing

I am asking for facts and files only; I will run the tests.

1. Was B2-F ever run **empty** over the sharp 40 mm step, or **empty** down the 12 % pitch with a stop on the way? If result files exist, which?
2. Drive unit: weighed mass of gearmotor, brake, chain stage and wheel; brake torque and the time from power-off to full torque; motor constant and gearbox efficiency (the figures in M-8 are marked ASSUMED).
3. Drive wheel: make, tyre material and hardness, any stiffness figure.
4. Castor: make and type, swivel offset, tyre profile.
5. Battery protection: current limit and for how long; main fuse type.
6. Lane model: which of the 12 % pitch, the 40 mm step, the trench and the pothole were surveyed and which assumed.
7. The 21:00 limit: its source, and whether it applies to the bin at the road or the robot back on the dock. The companion assumes a 50-minute trip in that check (`c + 50.0`); please confirm that is intended.
8. Comb: how the nib is fixed to the comb plate in B2-F (welded, or screwed).
9. Your firmware model lifts at 30 mm/s; which actuator is that?

## Files

- `REPLY_and_REV4_2026-11-20.md`: this note.
- `BinRobo_rev4_drawings_A3_2026-11-20.pdf`: 17 sheets, A3. `BinRobo_rev4_drawings_png_2026-11-20.zip`: the same as PNG.
- `rev4_files_2026-11-20.zip`: scripts, switches, command lists, every result file, the tables behind this note, and a README.

## Sources

- LINAK LA36 data sheet (forces, self-locking force, speeds, IP rating, built-in dimension): https://media.distrelec.com/Web/Downloads/_e/ng/linear_actuator_la36_data_sheet_eng.pdf
- FDI 4000 N actuator, the two listings that disagree: https://botland.store/15868-linear-actuator-super-power-jack-4000n-6mms-24v-40cm-stroke.html and https://www.anodas.lt/en/fdi-linear-actuator-24v-400mm-6mm-s
- Safety bumper travel (a 150 mm bumper at 0.5 m/s: switching travel and after-travel): https://products.schmersal.com/upload/orig/10/00/20/01/DOC_MAN_MEC_mrl-ssg-sbl_SEN_AIN_V3.pdf
- Bumper test pieces and force limits for driverless vehicles, as summarised by NIST: https://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.8029.pdf
- Bumper list prices: https://cdn.automationdirect.com/static/specs/asosentirbumpers100x200.pdf (ASO, 100 x 200 mm section); ABB ASB 100/200 on voltimum.co.uk; ASO's PL d, category 3 statement on unchainedrobotics.de.
- Outdoor safety laser scanner list price: https://nl.rs-online.com/web/p/light-detection-and-ranging/2856778 and https://befr.rs-online.com/web/p/light-detection-and-ranging/2856789
- The three review reports of 14 November and the review package of 15 November (read, not run).
