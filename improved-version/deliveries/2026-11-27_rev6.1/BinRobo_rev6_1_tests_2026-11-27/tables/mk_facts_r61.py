#!/usr/bin/env python3
"""Revision 6.1 (27 Nov): texts and tables for sheet 18. Sheet 17 and the rest are the revision 6 facts unchanged.
The test rows come from r61/tables/stress_rows_r61.json (stress_md2.py: start settings and fast cruise, frozen 6.1 code)."""
import json, os
F = json.load(open('/home/claude/s0/r6/facts_r6.json')); T = '/home/claude/s0/r61/tables/'
R = F['people_rules']
def sub(i, a, b):
    assert a in R[i], (i, a); R[i] = R[i].replace(a, b)
sub(0, 'or is joined to it;', 'or is joined to it, unless it is compact (0.8 m wide at most) and stands 0.55 m or more proud of the face [6.1];')
R[0] += ' [6.1] Every scan is first cleaned of lone returns (rain, insects, blown leaves): a return counts only if a neighbouring ray agrees with it or the three scans before showed it too.'
sub(6, 'Three times in two minutes: hold and call the owner.', 'Three times in two minutes: hold and call the owner. [6.1] It acts on two scans running, not on one.')
sub(7, 'It then stops turning and stands still.', 'It then stops turning and stands still. [6.1] Whoever walked a metre or more while the robot stood is a walker from then on: no turn while they are within 3 m, standing or not, and none for 30 s after they drop out of sight inside 3 m.')
F['people_rules'] = R
rows_f = T + 'stress_rows_r61.json'
if os.path.exists(rows_f):
    SR = json.load(open(rows_f)); by = {r[-1]: r for r in SR['rows']}
    keep = ['near26', 'near20', 'run26', 'run20', 'nearhedge30', 'gapwalk26', 'behind', 'side', 'side14', 'flank', 'hug']      # the rows the sheet has room for; the note has all of them
    short = {'near26': "Walks out of the far hedge into the path; nose 1.0 m from their line (the reviewers' case)", 'near20': 'Walks out of the far hedge into the path; nose 0.4 m from their line',
             'side': "Walks up from the far hedge and stands about 0.45 m from the robot's side for 30 s", 'side14': "Walks from the far hedge straight at the robot's side, setting off when it is already beside them",
             'hug': 'Walker comes up the lane 0.35 m from the far hedge and walks past the robot', 'hugstand': 'The same walker stops against the far hedge beside or near the robot for 30 s'}
    F['tests_rows'] = [[short.get(k, by[k][0]), by[k][1], by[k][2]] for k in keep if k in by]
    F['tests_intro'] = 'Mission simulation on the revision 6.1 code, a loaded robot in the lane at night, three seeds each. "Nose 1.0 m from their line": the person sets off from the hedge when the nose is that far from where they will cross; they walk on without looking. Touch = any contact while the robot is still moving. Camera: a person found in 60 % of pictures. The full table, and the same cases on a worse lidar, are in the revision 6.1 note.'
notes_f = T + 'sheet18_notes_r61.json'
if os.path.exists(notes_f): F['people_notes'] = json.load(open(notes_f))
json.dump(F, open('/home/claude/s0/r61/facts_r61.json', 'w'), indent=1); print('facts_r61.json written;', len(F['tests_rows']), 'test rows')
