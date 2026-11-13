#!/usr/bin/env python3
"""S0 helper: run an EXISTING runner (cmp/runCMP.py or b2/runB2.py) unchanged except that results go to $H2_RES
(so stored jsons in cmp/res and b2/res are never overwritten). usage: rerun.py <runner.py> <args...>"""
import os, sys
src_path=os.path.abspath(sys.argv[1]); src=open(src_path).read()
old="RES=os.path.join(HERE,'res')"; assert src.count(old)==1
src=src.replace(old,"RES=os.environ['H2_RES']")
sys.argv=[src_path]+sys.argv[2:]
g=dict(__name__='__main__',__file__=src_path); exec(compile(src,src_path,'exec'),g)
