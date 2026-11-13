export PYTHONPATH=/workspace/work/pylib
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/cad/revF1
python3 recovery.py R1 > rec_R1.log 2>&1 &
python3 recovery.py R2 > rec_R2.log 2>&1 &
wait
python3 recovery.py R1a > rec_R1a.log 2>&1 &
python3 recovery.py R1b > rec_R1b.log 2>&1 &
wait
echo RECDONE >> rec_R1b.log
