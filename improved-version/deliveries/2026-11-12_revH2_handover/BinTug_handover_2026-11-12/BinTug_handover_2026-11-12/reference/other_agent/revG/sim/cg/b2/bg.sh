#!/bin/bash
# usage: bg.sh <name> <cmd...>  : run in background (setsid, nice 10), pid -> b2/<name>.pid, log -> b2/<name>.log
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/revG/sim/cg
n=$1; shift
PYTHONPATH=/workspace/work/pylib setsid nohup nice -n 10 "$@" > b2/$n.log 2>&1 < /dev/null &
echo $! > b2/$n.pid; echo started $n pid $(cat b2/$n.pid)
