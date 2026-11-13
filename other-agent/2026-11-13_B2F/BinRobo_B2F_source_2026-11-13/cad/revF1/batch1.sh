export PYTHONPATH=/workspace/work/pylib
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/cad/revF1
for v in F0 Bfwd B2fwd Light D4 Clong T40 T35 Hsoft; do for t in cycle climb20 bump60 estop20; do echo "$v $t"; done; done | xargs -P2 -n2 python3 study.py > batch1.log 2>&1
echo ALLDONE >> batch1.log
