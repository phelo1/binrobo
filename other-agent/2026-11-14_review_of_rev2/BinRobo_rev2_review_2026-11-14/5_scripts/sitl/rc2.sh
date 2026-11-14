#!/bin/bash
# wrapper: one chunk + append the SAVED/QUEUE lines to the progress file
cd "$(dirname "$0")"; PF=../../docs/reviews/PROGRESS_rev2_sitl.md
o=$(./run_chunk_rev2.sh $1 $2 ${3:-92} 30); echo "$o" | grep -E "SAVED|QUEUE|checkpoint|Traceback|Error|BUSY|ALERT|gate MISS|waited"
echo "- $(date -u +%H:%M) UTC $1: $(echo "$o" | grep -E "SAVED|QUEUE|checkpoint|Traceback|BUSY" | sed 's/result=//' | tr '\n' ';')" >> $PF
