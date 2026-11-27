#!/bin/bash
# Puts the revision 6.1 delivery into the clone of the public repository, cleaned by scrub.py. Usage: repo_add_delivery.sh
R=/home/claude/binrobo; D=$R/improved-version/deliveries/2026-11-27_rev6.1; OUT=/mnt/user-data/outputs/rev6_1_2026-11-27; SC="python3 /home/claude/s0/r61/scrub.py"; REP=/home/claude/s0/r61/scrub_report_r61.json
rm -rf $D; rm -f $REP; mkdir -p $D/BinRobo_rev6_1_tests_2026-11-27
cp /home/claude/s0/r61/note/REV6_1_2026-11-27.public.md $D/REV6_1_2026-11-27.md      # the public copy of the note (see assemble.py)
cp $OUT/BinRobo_improved_rev6_1_drawings_2026-11-27.pdf $D/
( cd $D/BinRobo_rev6_1_tests_2026-11-27 && unzip -q $OUT/BinRobo_rev6_1_tests_2026-11-27.zip )
sed -i '/^\[for Brian only\]/d' $D/BinRobo_rev6_1_tests_2026-11-27/chains/chain.log
$SC $D --owner mine --report $REP
python3 /home/claude/s0/r61/scrub.py --verify $D | head -12
du -sh $D; find $D -type f | wc -l; find $D -size +20M -exec ls -la {} \; | awk '{print $5,$9}'
