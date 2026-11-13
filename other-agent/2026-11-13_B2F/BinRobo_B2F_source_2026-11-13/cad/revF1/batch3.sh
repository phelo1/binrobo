export PYTHONPATH=/workspace/work/pylib
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/cad/revF1
printf "F1 cycle rec\nF1 climb20 rec\nF1 climb15 rec\nF1 estop20 rec\nF1 bump60 rec\nF1 camber30 rec\nF1 turn_closed rec\nF0 climb15\nF0 camber30\nF0 turn_open\nF0 bump60 rec\n" | xargs -P2 -L1 python3 study.py > batch3.log 2>&1
echo ALLDONE >> batch3.log
