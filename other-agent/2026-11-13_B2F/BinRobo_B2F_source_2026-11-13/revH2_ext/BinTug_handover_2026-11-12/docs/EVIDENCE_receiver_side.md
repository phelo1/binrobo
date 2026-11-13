# Which side of the bin carries the EN 840 comb receiver

12 November 2026. This is the point on which Rev H / Rev H2 and the other agent's B1 / B2 disagree, and everything else follows from it.

**Finding: the comb receiver is on the FRONT wall of the bin, the wall opposite the handle, the lid hinge and the wheels.** Rev H and Rev H2 dock on that side. B1 and B2 dock on the handle side, on the stated premise that "the EN 840 comb receiver is under the handle". No source found supports that premise and several contradict it.

It still has to be confirmed on Brian's own three bins before any steel is cut: test B0 in `TESTS_AND_SIMULATIONS.md` takes five minutes and costs nothing.

## 1. Evidence

| # | Source | What it shows | Where to look |
|---|---|---|---|
| 1 | SULO Citybac 240 data sheet, drawing page | Callout C, "DIN comb lifting system", points at the face that carries the sticker panel, opposite the handle bar (callout B is the handle bar, listed as a separate feature) | `reference/other_agent/web/downloads/g5bins/sulods-2.png` |
| 2 | SULO Citybac 240 data sheet, dimension page | "B Upper comb edge ~ 998" is dimensioned at the front of the side elevation; the handle is at the other end | `.../g5bins/sulods-3.png` |
| 3 | Craemer MGBneo 240 side elevation | "min. 860 - max. 1030" (the EN 840-1 comb height band) is dimensioned at the front wall; hinge, handle and wheels are drawn at the rear | `.../g5bins/craemer240_side.png` |
| 4 | Weber 140 side elevation | Comb height 1001 dimensioned at the front | `.../g5bins/weber140_side_crop.png` |
| 5 | EN 840-1 nomenclature (Annex A) | Separate terms: "Front face", "Back face", "Handle", and "Frontal receiver / Prise frontale / Frontaufnahme" | research report, `RESEARCH_2026-11-12.md` |
| 6 | GGAWB application guidelines 03/2025, s.3.5 | Calls it the "obere vordere Behälteraufnahme" (upper front container receiver), to be supported over its full width by comb teeth | same |
| 7 | ESE operating manual, July 2022 | The lifter's retention stop may touch only the rear surface of the bin, ideally the wheels, and must not touch the rear handle of 2-wheel bins. So wheels and handle are at the rear, away from the comb | `.../g5bins/ese_manual.pdf` and the research report |
| 8 | Lifter maker (Compact & Bale / Durapac) | The comb mechanism picks bins up "from the front lip" | research report |

Rows 1 to 4 are the other agent's own downloaded data sheets. I read the drawings by eye; the research task could not machine-read drawings and rests on the text in rows 5 to 8. The two lines of evidence agree.

## 2. What the handle side is rated for

Nothing in EN 840 qualifies the handle or the handle-side rim to carry a full 2-wheel bin.

- EN 840-5 tests the **frontal receiver**: at least 100 loaded lift-tilt cycles on a standard comb lifter at 0.4 kg/dm³ x nominal volume (96 kg fill, 110 kg gross for 240 L), receiver deflection no more than 1.5 % of its length for plastic, at 23 °C and at -18 °C.
- The handle of a 2-wheel bin is tested for pulling the tilted bin (handle force 20 % of the weight). The 1,000-lift handle test applies to lifting handles on 4-wheel containers only.
- GGAWB s.3.7: move the bin only by the push handles and roll it; it is not intended to be carried.

So B2's "frozen gate" result (8 of 9) is a pass on a bin model that has a rated receiver where real bins have a handle. It says little about what B2 would do on a real bin.

## 3. A second modelling error that follows from the first

The other agent tested Rev H in MuJoCo by adding a lip to the front wall of its bin model (`reference/other_agent/revG/sim/cg/cmp/simH.py`). That bin hull gives the **front** wall a 170 mm taper from rim to base (line 132, `xfb=xf+170*sc`). The manufacturer drawings show the opposite: the front wall is close to plumb (about 35 mm of taper on the Craemer 240 drawing, scaled at 1.25 mm per pixel) and the large taper and the wheel recess are at the rear.

With a 170 mm front taper and a rest pad flush with the comb face, the bin has to swing about 75 mm before it meets the pad, hangs 11 to 12 degrees, and its wheels drop about 80 mm. That is the cause of the "false holds" reported for Rev H. `revH2/sim/hang.py` reproduces their figure with their assumptions (10.0 degrees, 82 mm) and gives 0.2 to 1.1 degrees with the drawn geometry and a pad set 25 mm back. See `drawings/bin_interface.png`.

This does not excuse Rev H. Its pad position was not a controlled dimension, and it had no check that the bin's wheels had left the ground. Rev H2 fixes both (adjustable pad set from measured bins; firmware FH1 and FH2).

## 4. What is still not known

| Unknown | Why it matters | How to close it |
|---|---|---|
| The receiver profile (EN 840-1 dimensions 13 to 27 and the Annex B comb) | Tooth height, tooth pitch against the receiver ribs (180 mm pitch, 6 mm ribs) and seat depth | Buy EN 840-1:2020 before cutting the comb (test B0b) |
| Front-wall set-back of Brian's bins, 450 to 550 mm below the comb | Sets the pad depth; not published anywhere | Measure (test B1); pad has +/-25 mm of slot |
| Strength of an aged, cold receiver under this robot's shock loads | EN 840-5 covers truck lifting, not a 40 mm kerb at 0.8 m/s | Proof-load and drop tests B2 and B3 |
| Whether Brian's bins are EN 840 bins at all | A non-standard bin may have no frontal receiver | Test B0 |
