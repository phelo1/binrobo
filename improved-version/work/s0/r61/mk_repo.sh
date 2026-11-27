#!/bin/bash
# Builds the git repository of the whole BinRobo project: every delivery of the improved version and everything received from the other
# agent and from Brian, one commit per delivery, in the order and at the dates they happened. Usage: mk_repo.sh [repo dir]
R=${1:-/home/claude/repo/binrobo}; O=/mnt/user-data/outputs; U=/mnt/user-data/uploads; H=/home/claude
rm -rf "$R"; mkdir -p "$R"; cd "$R" || exit 1; git init -q -b main
TR=$'\n\nCo-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_018krABpmSDbhz6BWpyDfDcC'
ci() { git add -A; if git diff --cached --quiet; then echo "nothing to commit: $2"; return; fi
       GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2$TR"; echo "committed $(date +%T): $2"; }
unz() { mkdir -p "$2"; unzip -q -o "$1" -d "$2" >/dev/null 2>&1 || echo "WARN unzip $1"
        find "$2" -name '.git' -prune -exec rm -rf {} + 2>/dev/null; find "$2" -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null
        find "$2" -type l -delete 2>/dev/null; chmod -R u+rwX "$2"; }
IV=improved-version/deliveries; OA=other-agent; FB=from-brian
cat > .gitignore <<'EOG'
__pycache__/
*.pyc
.DS_Store
MUJOCO_LOG.TXT
EOG
echo "# BinRobo" > README.md; ci "2026-11-11T15:00:00+03:00" "Start of the repository"

unz "$U/Bin_Tug_Project_Docs_Rev3_0__1_.zip" $OA/2026-11-11_project_docs_rev3.0
ci "2026-11-11T15:08:00+03:00" "Other agent: Bin Tug project docs Rev 3.0, as received"

unz $O/BinTug_RevH_package.zip $IV/2026-11-11_revH/BinTug_RevH_package; cp -a $O/revH_isometric $IV/2026-11-11_revH/
ci "2026-11-11T17:03:00+03:00" "Rev H: concept package and isometric views"

unz "$U/BinRobo_full.zip" $OA/2026-11-12_BinRobo_full; unz "$U/BinRobo_core__1_.zip" $OA/2026-11-12_BinRobo_core
ci "2026-11-12T07:42:00+03:00" "Other agent: BinRobo full and core archives, as received"

unz $O/BinTug_handover_2026-11-12.zip $IV/2026-11-12_revH2_handover/BinTug_handover_2026-11-12; cp -a $O/revH2_drawings $IV/2026-11-12_revH2_handover/
ci "2026-11-12T12:17:00+03:00" "Rev H2: handover pack, tests and drawings"

D=$OA/2026-11-13_B2F; mkdir -p $D
unz "$U/3af9d7e9-BinRobo_B2F_package_2026-11-13.zip" $D/BinRobo_B2F_package_2026-11-13; unz "$U/2a981e72-BinRobo_B2F_source_2026-11-13.zip" $D/BinRobo_B2F_source_2026-11-13
cp "$U/a21a489a-HANDOVER_Rev4.0.pdf" $D/HANDOVER_Rev4.0.pdf; cp "$U/e0895069-BinRobo_B2F_drawings_A3.pdf" $D/BinRobo_B2F_drawings_A3.pdf; cp "$U/ea7ead06-BinRobo_B2F_BOM_2026-11-12.xlsx" $D/BinRobo_B2F_BOM_2026-11-12.xlsx
ci "2026-11-13T09:50:00+03:00" "Other agent: B2-F design (package, source, drawings, parts list, handover Rev 4.0)"

D=$IV/2026-11-13_B2F_review_and_tests; mkdir -p $D
cp $O/REVIEW_B2F_2026-11-13.md $O/RESULTS_B2F_tests_2026-11-13.md $O/RESULTS_B2F_tests_part2_2026-11-13.md $O/FINDING_kerb_step_simulator_2026-11-13.md $O/cost_b2f_lean.py $O/cost_b2f_lean.json $O/cost_b2f_lean_changes.csv $O/cost_b2f_changes_v2_2026-11-13.csv $D/
for z in b2f_tests_evidence_2026-11-13 b2f_tests_part2_evidence_2026-11-13 kerb_finding_evidence; do unz $O/$z.zip $D/$z; done
mkdir -p $FB/2026-11-13; for f in 4f38ae8b d67ca710 9d6f33d3; do cp "$U/$f-image.png" $FB/2026-11-13/image_$f.png; done
ci "2026-11-13T16:19:00+03:00" "Review of B2-F, test results parts 1 and 2, kerb-step finding, cost comparison"

D=$IV/2026-11-13_improved_version_drawings; mkdir -p $D
cp $O/drawings_2026-11-13/*.pdf $O/drawings_2026-11-13/*.md $D/; unz $O/drawings_2026-11-13/drawing_scripts.zip $D/drawing_scripts; unz $O/drawings_2026-11-13/pivot_height_retest_evidence.zip $D/pivot_height_retest_evidence
cp -a $O/videos_2026-11-13 $D/videos; [ -f $D/videos/video_scripts.zip ] && { unz $D/videos/video_scripts.zip $D/videos/video_scripts; rm $D/videos/video_scripts.zip; }
ci "2026-11-13T18:58:00+03:00" "Improved version: first drawings (14 sheets) and four simulation videos"

D=$OA/2026-11-13_review_of_improved_version; mkdir -p $D
cp "$U/34c0c9c6-SITL_improved_version_2026-11-13.pdf" $D/SITL_improved_version_2026-11-13.pdf; cp "$U/7727a1a1-COLDEYE_improved_drawings_2026-11-13.pdf" $D/COLDEYE_improved_drawings_2026-11-13.pdf; cp "$U/e27a3c18-TEST_improved_version_2026-11-13.pdf" $D/TEST_improved_version_2026-11-13.pdf
cp "$U/ae3e378a-attachment.txt" $FB/2026-11-13/attachment.txt
ci "2026-11-13T23:26:00+03:00" "Other agent: review of the improved version (mission simulation, physics tests, cold-eye)"

D=$IV/2026-11-14_reply; mkdir -p $D; cp $O/reply_2026-11-14/*.md $D/; unz $O/reply_2026-11-14/for_the_other_agent_2026-11-14.zip $D/for_the_other_agent_2026-11-14
ci "2026-11-14T00:41:00+03:00" "Reply to the first review"
D=$IV/2026-11-14_rev2; mkdir -p $D; cp $O/rev2_2026-11-14/*.md $O/rev2_2026-11-14/*drawings_A3*.pdf $D/; unz $O/rev2_2026-11-14/rev2_files_2026-11-14.zip $D/rev2_files_2026-11-14
ci "2026-11-14T03:17:00+03:00" "Improved version, revision 2: results, drawings, test files"

D=$OA/2026-11-14_review_of_rev2; unz "$U/BinRobo_rev2_review_full_2026-11-14.zip" $D; cp "$U/563ee703-FEEDBACK_to_other_agent_rev2_2026-11-14.txt" $D/FEEDBACK_to_other_agent_rev2_2026-11-14.txt
ci "2026-11-14T20:27:00+03:00" "Other agent: review of revision 2 (full pack) and feedback"

D=$IV/2026-11-14_rev3; mkdir -p $D; cp $O/rev3_2026-11-14/*.md $O/rev3_2026-11-14/*drawings_A3*.pdf $D/; unz $O/rev3_2026-11-14/rev3_files_2026-11-14.zip $D/rev3_files_2026-11-14
ci "2026-11-14T23:06:00+03:00" "Improved version, revision 3: reply, drawings, test files"

D=$OA/2026-11-15_review_of_rev3; unz "$U/BinRobo_rev3_review_2026-11-15__1_.zip" $D
cp "$U/4359417e-COLDEYE_rev3_2026-11-14.pdf" $D/COLDEYE_rev3_2026-11-14.pdf; cp "$U/58ead337-TEST_rev3_2026-11-14.pdf" $D/TEST_rev3_2026-11-14.pdf; cp "$U/965d6370-SITL_rev3_2026-11-14.pdf" $D/SITL_rev3_2026-11-14.pdf
ci "2026-11-15T20:43:00+03:00" "Other agent: review of revision 3"

D=$IV/2026-11-20_rev4; mkdir -p $D; cp $O/rev4_2026-11-20/*.md $O/rev4_2026-11-20/*drawings_A3*.pdf $D/; unz $O/rev4_2026-11-20/rev4_files_2026-11-20.zip $D/rev4_files_2026-11-20
ci "2026-11-20T20:05:00+03:00" "Improved version, revision 4: reply, drawings, test files"

D=$OA/2026-11-21_review_of_rev4; unz "$U/BinRobo_rev4_review_2026-11-21__1_.zip" $D
cp "$U/29b763b4-SITL_rev4_2026-11-21.pdf" $D/SITL_rev4_2026-11-21.pdf; cp "$U/324f86e8-COLDEYE_rev4_2026-11-21_1.pdf" $D/COLDEYE_rev4_2026-11-21.pdf; cp "$U/a605a4f5-TEST_rev4_2026-11-21.pdf" $D/TEST_rev4_2026-11-21.pdf
ci "2026-11-21T18:59:00+03:00" "Other agent: review of revision 4"

D=$IV/2026-11-21_rev5; mkdir -p $D; cp $O/rev5_2026-11-21/*.md $O/rev5_2026-11-21/*drawings_2026*.pdf $D/; unz $O/rev5_2026-11-21/BinRobo_rev5_tests_2026-11-21.zip $D/BinRobo_rev5_tests_2026-11-21
ci "2026-11-21T23:44:00+03:00" "Improved version, revision 5: reply, drawings (18 sheets), test pack"
D=$IV/2026-11-22_rev5.1; mkdir -p $D; cp $O/rev5_1_2026-11-22/*.md $O/rev5_1_2026-11-22/*drawings_2026*.pdf $D/; unz $O/rev5_1_2026-11-22/BinRobo_rev5_1_tests_2026-11-22.zip $D/BinRobo_rev5_1_tests_2026-11-22
ci "2026-11-22T21:57:00+03:00" "Improved version, revision 5.1: follow-up, drawings, test pack"

D=$OA/2026-11-23_review_of_rev5.1; unz "$U/BinRobo_rev51_review_2026-11-23.zip" $D
cp "$U/1473b86a-TEST_rev51_2026-11-23.pdf" $D/TEST_rev51_2026-11-23.pdf; cp "$U/99bc9f13-SITL_rev51_2026-11-23.pdf" $D/SITL_rev51_2026-11-23.pdf; cp "$U/f7c5c096-COLDEYE_rev51_2026-11-23.pdf" $D/COLDEYE_rev51_2026-11-23.pdf
ci "2026-11-24T08:08:00+03:00" "Other agent: re-test of revision 5.1"

D=$IV/2026-11-24_rev6; mkdir -p $D; cp $O/rev6_2026-11-24/*.md $O/rev6_2026-11-24/*drawings_2026*.pdf $D/; unz $O/rev6_2026-11-24/BinRobo_rev6_tests_2026-11-24.zip $D/BinRobo_rev6_tests_2026-11-24
ci "2026-11-24T17:44:00+03:00" "Improved version, revision 6: people avoidance reworked, fast cruise; reply, drawings, test pack"
echo "history done $(date +%T)"; du -sh .git; git log --oneline | wc -l
