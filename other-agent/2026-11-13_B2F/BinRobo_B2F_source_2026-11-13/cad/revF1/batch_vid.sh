export PYTHONPATH=/workspace/work/pylib
cd /workspace/projects/847c6e2d-79fb-41ac-8eca-c75df6a92b0c/cad/revF1
python3 -u make_videos_f1.py 1,4,5,2,3 > vlogA.txt 2>&1 &
python3 -u make_videos_f1.py 8,9,7,6,10 > vlogB.txt 2>&1 &
wait
echo VIDDONE >> vlogB.txt
