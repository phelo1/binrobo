#!/bin/bash
# Revision 6.1: every table of the note from the result files. Run after chain_g, chain_h and chain_i. usage: mk_tables.sh
cd /home/claude/s0; T=r61/tables; O=/home/claude/sitl_out
python3 r61/stress_tab.py $T/stress_fast.json r61f:fast > $T/stress_fast.txt 2>&1
python3 r61/stress_tab.py $T/stress_start.json r61s:start > $T/stress_start.txt 2>&1
python3 r61/stress_tab.py $T/stress_v10.json r61v:v10 > $T/stress_v10.txt 2>&1
python3 r61/stress_tab.py $T/stress_b1.json r61b1:level1 > $T/stress_b1.txt 2>&1
python3 r61/stress_tab.py $T/stress_b2.json r61b2:level2 > $T/stress_b2.txt 2>&1
python3 r61/stress_md2.py $T/stress_r61.md $T/stress_rows_r61.json $T/stress_start.json,$T/stress_fast.json "start=Fast cruise off (start settings, 0.4 m/s and under)" "fast=Fast cruise on (up to 1.0 m/s)" > /dev/null
python3 r61/stress_md2.py $T/stress_bad_r61.md $T/stress_rows_bad_r61.json $T/stress_fast.json,$T/stress_b1.json,$T/stress_b2.json "fast=Clean lidar" "level1=Level 1" "level2=Level 2" --cases near26,near20,run26,child35,gapwalk26,behind,side,side14,flank,hug,hugstand31 > /dev/null
python3 r61/stress_md2.py $T/stress_v10_r61.md $T/stress_rows_v10_r61.json $T/stress_v10.json "v10=Every run at 1.0 m/s" > /dev/null
( source r61/env_r61_fast.sh; PIV_OUT=$T/turn_people_r61.json python3 r6/piv_an.py $O/r61f_turn_a $O/r61f_turn_a2 $O/r61f_turn_b $O/r61f_turn_c $O/r61f_turn_y $(ls -d $O/r61x_turn_c_nowalk $O/r61x_turn_y_nowalk 2>/dev/null) > $T/turn_people_r61.txt 2>&1 )
python3 r5/r5_score.py $O/r61f_suite/runs > $T/score_r61_fast.txt 2>&1
python3 r6/suite_extra.py r61f_suite $T/suite_extra_r61.json > $T/suite_extra_r61.txt 2>&1
python3 r6/pivot_rates.py r61f_suite > $T/pivot_rates_r61.txt 2>&1
python3 r6/trips_tab.py $T/trips_r61.json fast=r61f_suite start=r61s_trips level1=r61b1_trip level2=r61b2_trip leaf=r61f_leaf phantom=r61f_phantom mid=r61m_trip turn_a=r61f_turn_a turn_a2=r61f_turn_a2 turn_b=r61f_turn_b turn_c=r61f_turn_c turn_y=r61f_turn_y pick=r61f_pick > /dev/null 2>&1
python3 r6/show.py r61f_turn_a r61f_turn_a2 r61f_turn_b r61f_turn_c r61f_turn_y r61f_pick r61s_trips r61s_ret1630 r61b1_trip r61b2_trip r61f_leaf r61f_phantom r61f_leafnogo r61m_trip r61x_turn_c_nowalk r61x_turn_y_nowalk > $T/trips_show_r61.txt 2>&1
python3 r61/trips_md.py $T/trips_detail_r61.json fast_suite=r61f_suite start=r61s_trips start_1630=r61s_ret1630 level1=r61b1_trip level2=r61b2_trip leaf=r61f_leaf phantom=r61f_phantom leafnogo=r61f_leafnogo mid=r61m_trip turn_a=r61f_turn_a turn_a2=r61f_turn_a2 turn_b=r61f_turn_b turn_c=r61f_turn_c turn_y=r61f_turn_y pick=r61f_pick nowalk_c=r61x_turn_c_nowalk nowalk_y=r61x_turn_y_nowalk > $T/trips_detail_r61.txt 2>&1
python3 r61/react_tab.py $T/react_r61.json r6f:rev6 r61f:rev6.1 > $T/react_r61.txt 2>&1
python3 r61/react_tab.py $T/react_start_r61.json r6s2:rev6 r61s:rev6.1 > $T/react_start_r61.txt 2>&1
ls -la $T | awk '{print $5, $9}'
