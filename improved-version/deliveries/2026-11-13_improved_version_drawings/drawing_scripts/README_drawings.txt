BinRobo, improved version: drawing set of 2026-11-13
====================================================
What it is
  14 A3 sheets (PDF, and one PNG per sheet at 200 dpi) of the improved version = B2-F with three tested changes:
  fixed pad, 350 mm lift travel on a 60 mm taller mast, castor cross-beam on a centre pivot.
  CONCEPT, NOT FOR MANUFACTURE. Block-level model: no fasteners, brackets, cable glands or pod internals.

Sheets
  1-4    isometric from the four corners, without the bin        5-8   the same four views carrying a full 240 L bin
  9      underside, from below                                   10    rear-left with the bin drawn see-through
  11-12  exploded views without / with the bin, items numbered   13    parts list     14  wiring looms (proposed routing)

Where the geometry comes from
  cad_B2F_src.py   unchanged copy of the other agent's work/revB2F/cad_B2F.py (108 CadQuery parts)
  get_poses.py     one simulated pick-up of a full 240 L bin on the improved version; gives the pose of every body
                   at the start (no bin) and at carrying height (rec_B2F.json / .npz)
  build_model.py   applies the changes to their parts, adds the electrical devices that are on their parts list but
                   not in their CAD (positions proposed), adds ten wiring looms (routing proposed), writes model.pkl
  render.py        true isometric (parallel) projection of the meshes, with outlines
  draw_sheets.py   sheets, labels, balloons, parts list, loom table

Status of each item (also on sheet 13)
  32 robot items as in their CAD, 16 changed, 26 new (16 devices/parts plus 10 looms). Items 101-104 are the bin.
  There is no B2-F wiring table or mounting drawing yet, so every loom route and every "new" position is a proposal.

Two things found while drawing (both on sheet 9)
  1. In the B2-F CAD the bay floor, bay side walls and ballast plate pass through the nose castors. They are cut back here
     (about 1.2 kg less plastic at the nose; not re-tested, the robot weighs about 92 kg).
  2. OPEN ISSUE: with the castors swivelled forward (reversing) the wheels overlap the front bumper by about 45 mm.
     Bumper about 65 mm forward, or castors about 65 mm back. Neither is tested. Bumper drawn where B2-F has it.
  The castor-beam pivot pin is drawn 200 mm above the ground, the tested height. A re-test with the pin at 287 mm
  (through the beam) passed the lane runs over a ramped step but docked less accurately: 86 of 90 pick-ups against 90 of 90.

To rebuild:  python3 get_poses.py ; python3 build_model.py ; python3 draw_sheets.py   (needs the B2-F source tree, MuJoCo, CadQuery, Pillow)
