# Working files of the improved version

- `s0/` is the working directory behind every delivery: command lists (`chain*.sh`), settings (`env_*.sh`), tabulation scripts, tables, the
  drawing model and scripts (`cad/`). One folder per revision: `r2` ... `r6`, `r61`. Each `R*_README.txt` says what its files are.
- `b2f_sitl_scripts/` are this agent's files that sit beside the other agent's B2-F scripts (`other-agent/2026-11-13_B2F/.../sitl/b2f/scripts`):
  `b2f_companion_x.py` (mission software with every change since revision 2), `b2f_runner_x.py` (test hooks), `b2f_r6.py` (lane watch,
  pause, fast cruise; revision 6 on). Files with `_r2` ... `_r60` in the name are the versions as each revision left them.
- Paths inside the scripts are those of the machine they ran on (`/home/claude/...`).
- Left out to save space: recordings of physics runs (`*.npz`), the drawing model cache (`*.pkl`), sheet pictures and videos (they are in
  the deliveries as PDF and MP4), and the zipped packs (unpacked under `deliveries/`).
