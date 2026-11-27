# BinRobo

A robot that takes a 140 L or 240 L wheelie bin down a 635 m private lane to the road and brings it back, by itself, at any time of day.

This repository holds the whole project to date: every design revision, every review, every test and the simulation code they ran on.

**Keep this repository private.** The lane file (`route.json`, and the many result files derived from it) holds the exact latitude and longitude of the house and lane, and other files name the area. See "Before making this public" at the end.

## Where to start

| You want | Read |
|---|---|
| The current design and what is still open | The newest note under `improved-version/deliveries/` (the folder with the latest date). Start at "Summary for Brian". |
| The drawings | The PDF in the same folder (18 sheets). |
| To re-run a test | `README.txt` inside the test pack of that delivery, then `improved-version/work/`. |
| What the other agent said about a revision | `other-agent/<date>_review_of_<revision>/` |
| How the project got here | `git log`. One commit per delivery, at the date it was made. |

## Who did what

Two AI agents work on this for Brian, who relays files between them.

- **The other agent** designed the earlier robots (revisions A to G, then B2-F) and reviews each revision of the improved version. Its material is under `other-agent/`.
- **This agent (Claude)** reviewed and tested B2-F, then designed the "improved version" and tests it. Its material is under `improved-version/`.
- `from-brian/` holds the few files Brian sent himself.

## Layout

```
improved-version/
  deliveries/<date>_<name>/   each delivery as it was sent: the note, the drawings PDF, the test pack (unpacked)
  work/                       the working files behind the deliveries: scripts, command lists, tables, the drawing model
  results/sitl/               the result file of every mission-simulation run still on disk
other-agent/
  <date>_<name>/              each archive and review as it was received (archives unpacked)
from-brian/
```

The history, oldest first:

| Date | What |
|---|---|
| 11 Nov 2026 | Other agent: project docs Rev 3.0. This agent: Rev H concept. |
| 12 Nov | Other agent: full and core archives. This agent: Rev H2 handover. |
| 13 Nov | Other agent: B2-F design. This agent: review and tests of B2-F, the kerb-step finding, first drawings of the improved version. Other agent: first review of it. |
| 14 Nov | Reply; revision 2; the other agent's review of it; revision 3. |
| 15 Nov | Other agent: review of revision 3. |
| 20 to 22 Nov | Revision 4; its review; revisions 5 and 5.1. |
| 23 to 24 Nov | Other agent: re-test of 5.1. Revision 6: people avoidance reworked, fast cruise. |
| 27 Nov | Revision 6.1. |

## What the tests are

- **Physics (MuJoCo):** stopping distances by slope, load and grip; kerb, step and pothole strikes; holding on the hill; the bin on the comb.
- **Missions (ArduPilot Rover in simulation, firmware 4.7.2):** whole trips on a model of the lane, with faults, obstacles and people. The other agent's suite is 20 scenarios by three seeds.
- **People:** walkers, runners, children and things left in the lane, at night, from every side.

Everything is simulation. Nothing has been built or measured yet. Each note lists the tests to do on the built robot.

## What is not in the repository

- The PNG copies of the drawings (the same sheets as the PDFs).
- The full time traces of the mission runs, about 13 GB. The traces of the runs that a note relies on are in that delivery's test pack.
- Raw runs of revisions 2 to 5 that were deleted to free disk space on 24 November. Their results are in the test packs.
- The ArduPilot build tree and the MuJoCo viewer.

## Before making this public

1. Replace the real coordinates. `route.json` (in the other agent's source and in `improved-version/work`) has the latitude and longitude of every 5 m of the lane and the OpenStreetMap way numbers. Result files carry positions derived from it. About 800 files match.
2. Check the place names: one supplier list of the other agent names the village and nearby firms, and the notes name the county council.
3. The other agent's source includes an ArduPilot Rover binary (GPL version 3). Publishing it means offering its source as well, or removing it.
4. Read through the other agent's archives. This agent has scanned them for passwords, keys and personal contact details and found none (the only contact details are those of local metal fabricators in a supplier list), but it has not read all 18,000 files.
