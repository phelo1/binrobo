#!/bin/bash
# Puts the working files and the raw result files into the clone of the public repository, cleaned by scrub.py. Usage: repo_add_work.sh
R=/home/claude/binrobo; W=$R/improved-version/work; RES=$R/improved-version/results/sitl; SC="python3 /home/claude/s0/r61/scrub.py"; REP=/home/claude/s0/r61/scrub_report_work.json
cd $R || exit 1; rm -f $REP; rm -rf $W $RES; mkdir -p $W/s0 $W/b2f_sitl_scripts $RES
tar -C /home/claude/s0 --exclude='__pycache__' --exclude='*.pyc' --exclude='./out' --exclude='*/out' --exclude='*_pack' --exclude='*_pack.old' --exclude='*.zip' --exclude='*.npz' \
    --exclude='./r61/note' --exclude='private_names.json' --exclude='scrub_report*.json' --exclude='./cad/sheets/*.png' --exclude='*.mp4' --exclude='nohup.out' --exclude='*.pkl' --exclude='*.gz' -cf - . | tar -C $W/s0 -xf -
# log lines marked for Brian only are not for the public copy
sed -i '/^\[for Brian only\]/d' $W/s0/r61/chain.log
cp /home/claude/b2f_run/sitl/b2f/scripts/b2f_companion_x*.py /home/claude/b2f_run/sitl/b2f/scripts/b2f_runner_x*.py /home/claude/b2f_run/sitl/b2f/scripts/b2f_r6*.py $W/b2f_sitl_scripts/
cat > $W/README.md <<'EOR'
# Working files of the improved version

- `s0/` is the working directory behind every delivery: command lists (`chain*.sh`), settings (`env_*.sh`), tabulation scripts, tables, the
  drawing model and scripts (`cad/`). One folder per revision: `r2` ... `r6`, `r61`. Each `R*_README.txt` says what its files are.
- `b2f_sitl_scripts/` are this agent's files that sit beside the other agent's B2-F scripts (`other-agent/2026-11-13_B2F/.../sitl/b2f/scripts`):
  `b2f_companion_x.py` (mission software with every change since revision 2), `b2f_runner_x.py` (test hooks), `b2f_r6.py` (lane watch,
  pause, fast cruise; revision 6 on). Files with `_r2` ... `_r60` in the name are the versions as each revision left them.
- Paths inside the scripts are those of the machine they ran on (`/home/claude/...`).
- Left out to save space: recordings of physics runs (`*.npz`), the drawing model cache (`*.pkl`), sheet pictures and videos (they are in
  the deliveries as PDF and MP4), and the zipped packs (unpacked under `deliveries/`).
EOR
cd /home/claude/sitl_out; find . -name result.json | while read f; do d=$RES/$(dirname "$f" | sed 's#^\./##; s#/runs/#/#'); mkdir -p "$d"; cp "$f" "$d/result.json"; done
cd $R; $SC $W --owner mine --report $REP; $SC $RES --owner mine --report $REP
python3 /home/claude/s0/r61/scrub.py --verify $W $RES | head -12
du -sh $W $RES; find $RES -name result.json | wc -l
