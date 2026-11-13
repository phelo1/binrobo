export PYTHONPATH=/workspace/work/pylib
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/cad/revF1
for v in AT100 F1a F1c F1b B3fwd; do for t in bump60 climb20 estop20 cycle; do echo "$v $t"; done; done | xargs -P2 -n2 python3 study.py > batch2.log 2>&1
echo ALLDONE >> batch2.log
