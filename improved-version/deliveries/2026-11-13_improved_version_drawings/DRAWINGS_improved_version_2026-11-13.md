# BinRobo improved version: drawing set and what drawing it turned up

13 November 2026. Concept drawings, not for manufacture.

> **Corrected on 14 November** after the independent review; see `reply-to-review-2026-11-14.md`. In short:
> - the castor and bumper clash is a blocker, not an open issue, because the robot docks in reverse;
> - the 400 mm lift actuator does not fit the mast as drawn;
> - the gate figures below (9 of 9, 90 of 90) were at a model weight about 1.7 kg too light; at the corrected weight it is 8 of 9 with one false hold;
> - the lane passes below were all with the 60 mm pothole filled;
> - the two "not properly seated" pick-ups were off-centre beyond the scorer's 50 mm band with the nib engaged;
> - the pass rates do not show that the 287 mm pin is worse; the sideways arrival error does.

## What was made

`BinRobo_improved_version_drawings_A3_2026-11-13.pdf`, 14 A3 sheets (also one PNG per sheet at 200 dpi).

| Sheet | Content |
|---|---|
| 1 to 4 | Isometric views from the four corners, robot without the bin. Every visible item named and numbered. |
| 5 to 8 | The same four views carrying a full 240 L bin at carrying height. |
| 9 | Underside, seen from below, with the room each castor needs to swivel marked. |
| 10 | Rear-left view with the bin drawn see-through: comb under the lip, pad on the front wall. |
| 11, 12 | Exploded views without and with the bin, every item numbered, looms in colour. |
| 13 | Parts list keyed to the numbers, with the other agent's parts-list line for each item. |
| 14 | Wiring looms L1 to L10 on a faint robot, with a loom table. |

The version drawn is B2-F with the three tested changes: fixed pad, 350 mm lift travel on a 60 mm taller mast, castor cross-beam on a centre pivot.

## Where the geometry comes from

- The other agent's CadQuery model of B2-F (108 parts), run unchanged, then modified.
- Poses (lift height, bin position) from one simulated pick-up of a full 240 L bin on the improved version: dock offset 0.6 mm, bin wheels 102 mm off the ground.
- Of the 74 robot items: 32 are as in their CAD, 16 are changed, 26 are new. The new ones are 16 devices and parts that are on their parts list but not in their CAD (power box, isolator key, reset button, headlights, markers, radars, horn, microphone, LTE antenna, wheel sensors, the castor beam parts) and the 10 looms.
- There is no B2-F wiring table or mounting drawing. Every loom route and every new device position is a proposal made in this drawing. Loom contents are grouped from their parts list and their earlier Rev G6 harness; wire sizes, fuses and connectors are not worked out.
- Block-level only: no fasteners, brackets, cable glands or electronics-pod internals.

## Three things drawing it turned up

### 1. The castor-beam pivot height matters

The tests so far had the pivot pin 200 mm above the ground. The natural place to build it is through the beam itself, 287 mm up, so I drew it there first and re-ran the tests at that height.

| | Pin at 200 mm | Pin at 287 mm |
|---|---|---|
| Mechanical gate | 9 of 9 | 8 of 9 |
| Pick-ups, three bins, 30 each | 90 of 90 | 86 of 90 |
| Sideways error on first arrival at the bin, 240 L clip-lid bin, mean / largest | 15.8 / 47 mm | 24.6 / 89 mm |
| Same, 240 L standard bin | 18.3 / 48 mm | 22.2 / 73 mm |
| Same, 140 L bin | 13.2 / 39 mm | 15.1 / 43 mm |
| Lane runs with the step ramped (full bin out, empty back, collect empty) | pass | pass |

Of the four failed pick-ups at 287 mm, two did not dock (safe). In the other two the robot lifted the bin 34 and 72 mm off-centre, not properly seated, while its own switches reported a good hold. That is the kind of failure that must not happen.

The cause is not identified. A likely one: sideways castor forces during the swivel act on a longer lever and shift more load from one castor to the other. The drawing therefore keeps the pin at 200 mm, in a housing welded under the beam. Pivot height should be treated as a controlled dimension.

Not run at 287 mm: the sharp-step lane runs (both versions already stall there on the empty return).

### 2. In the B2-F CAD the bay floor, bay walls and ballast pass through the nose castors

The bay floor runs to x = 980 mm across the full width at 120 to 130 mm height; the castors stand at x = 950, y = ±280 mm and reach from the ground to 260 mm. Each castor needs a clear cylinder about 304 mm across to swivel (50 mm trail, 100 mm wheel radius). The simulation does not check these collisions, so the tests did not show it.

In this drawing:

- bay floor cut back at the two front corners (a 240 mm wide tongue stays for the battery and ballast);
- bay side walls end 140 mm earlier;
- ballast plate narrower and thicker, same 5 kg;
- power box, isolator key and the nose looms placed outside the castor room.

This removes about 1.2 kg of plastic at the nose. Not re-tested; the robot weighs about 92 kg.

### 3. Open issue: castors and front bumper

With the castors swivelled forward, as when reversing, each wheel reaches 1,100 mm ahead of the drive axle. The back of the front bumper is at 1,050 mm and its lower edge is 130 mm above the ground, so the wheel overlaps the bumper by about 45 mm. The 45° bumper corners are in the way too. This is in B2-F as designed and is not caused by the three changes.

The bumper is drawn where B2-F has it, because that is the outline every test used. Two ways out, neither tested:

| Option | Consequence | Tests to repeat |
|---|---|---|
| Bumper and charge contacts about 65 mm further forward | Robot 65 mm longer (1,572 mm); turning circle about 0.12 m bigger | Driving-software tests (hedge clearance in turns, yard exit, docking) |
| Castors about 65 mm further back | Wheelbase 885 instead of 950 mm; more weight on the castors; beam, nose cross-member and sensor post move back | All mechanical tests |

The optional 260 mm castors (which cure the stall at a sharp 40 mm step) need about 45 mm more room again, so this choice and the castor-size choice belong together.

## For the other agent

1. Castor swivel room in the nose: please confirm the floor, wall and ballast overlap and the bumper overlap in your CAD, and say which bumper option you prefer.
2. Pivot height of the castor beam: 200 mm tested good, 287 mm tested worse. Any reason it could not sit under the beam?
3. A wiring table for B2-F (the Rev G6 harness is for the older tug-and-trailer layout) and mounting positions for the 16 devices that are on the parts list but not in the CAD.
4. Still open from before: keeper (item 36) deletion, front camera parts-list line.

## Files

- `BinRobo_improved_version_drawings_A3_2026-11-13.pdf`
- `BinRobo_drawings_png_2026-11-13.zip`
- `drawing_scripts.zip` (scripts and a readme; rebuilds the set from the B2-F source tree)
- `pivot_height_retest_evidence.zip` (scorecards, pick-up results at both heights, lane results)
