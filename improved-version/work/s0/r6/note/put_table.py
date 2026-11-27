#!/usr/bin/env python3
"""put the people table (tables/stress_r6.md) into the note, replacing the one that is there"""
p = '/home/claude/s0/r6/note/REPLY_and_REV6_2026-11-24.md'; s = open(p).read()
tab = open('/home/claude/s0/r6/tables/stress_r6.md').read().strip().replace('TOUCHED', '**touched**').replace('(scenario as written)', '(the scenario as written)')
i = s.index('| Case | Runs | Fast cruise off'); j = s.index('\n', s.index('\nRuns: ', i) + 1)
s = s[:i] + tab + s[j:]
open(p, 'w').write(s); print('table in the note:', tab.count('\n') - 3, 'rows;', tab.split('\n')[-1])
