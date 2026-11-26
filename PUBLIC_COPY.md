# About this public copy

This repository is public, so it is a cleaned copy of the project files. The place where the robot runs must not be findable from it.

## What was changed

- **Coordinates.** Every latitude and longitude of the site is moved to a made-up origin, 53.000000 N, 8.000000 W. The move keeps every distance in metres exactly as it was: the lane has the same shape, slopes and length, and the tests run on the same geometry. 172 files changed.
- **Map references.** The OpenStreetMap way numbers of the lane are replaced by 0 (15 files). Raw OpenStreetMap extracts are left out.
- **Place names.** The village, the county, the council, the road number, nearby towns, postcodes and the waste collector are replaced by neutral words in square brackets, such as `[village]` and `[county]` (105 files, two file names). The council's web links are replaced by `[county council website]`.
- **Latitude in prose** (used for daylight and solar estimates) is rounded to 53 N.

So some text in the code differs from what ran: comments and message strings only. Simulated missions started from this copy sit at the made-up origin. The magnetic field and the like differ slightly there; the geometry does not.

## What was left out

| Reason | Files | Size |
|---|---:|---:|
| picture, video or binary of the other agent: not checked | 256 | 278 MB |
| map extract, flight log or firmware file | 151 | 56 MB |
| PDF replaced by its text | 36 | 20 MB |

- Pictures, videos and PDFs of the other agent are left out because they cannot be cleaned or checked by a program. Some show the lane on a map background or carry the road name. Each PDF is replaced by its text (`<name>.pdf.txt`), cleaned like any other text.
- Flight logs and the simulator's own files hold positions in binary form.
- The ArduPilot Rover firmware binary is left out. Get ArduPilot Rover 4.7.2 from ardupilot.org to run the mission simulation.
- The other agent's three older archives (project docs Rev 3.0, "full" and "core", about 840 MB) are not here at all. Brian has them.

The full list is in `removed_from_public_copy.txt`.

## What cleaning cannot hide

The lane's shape and its height profile are still in the data, because every test needs them. Someone determined could in principle match that shape against a map. If that matters, make the repository private.

## How it was done and checked

`improved-version/work/r61/scrub.py` does the cleaning before each commit, and its `--verify` mode checks the whole tree afterwards with separate patterns: 443 files removed, 275 changed, none left with a coordinate pair, a way number or a place name. The real origin and the list of names are read from private files that are not in the repository.
