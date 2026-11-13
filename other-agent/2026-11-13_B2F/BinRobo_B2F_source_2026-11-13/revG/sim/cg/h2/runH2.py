#!/usr/bin/env python3
"""H2 campaign gate runner = the live b2/runB2.py test definitions UNCHANGED (G1-G9 sub-commands, perturbation env), executed
with: sim module from h2/ (env CMP_SIM: simH2 | simB2h), results in h2/res/ (env CMP_PREFIX names the design, IT1_TAG the variant).
usage: runH2.py <runB2 sub-command and args>"""
import os, sys
H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H)
src_path=os.path.join(H,'..','b2','runB2.py'); src=open(src_path).read()
old="RES=os.path.join(HERE,'res')"; assert src.count(old)==1
src=src.replace(old,"RES=os.environ.get('H2_RES',os.path.join(%r,'res'))"%H)
sys.argv=[src_path]+sys.argv[1:]
exec(compile(src,src_path,'exec'),dict(__name__='__main__',__file__=src_path))
