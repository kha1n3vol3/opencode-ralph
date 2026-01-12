---
description: Check Ralph current status and progress
---

Check Ralph's current status.

PRD info:
!`[ -f "prd.json" ] && jq '.project, .branchName, .description' prd.json || echo "No PRD.json found"`

Current branch:
!`git branch --show-current 2>/dev/null || echo "Not a git repo"`

User stories status:
!`[ -f "prd.json" ] && jq -r '.userStories[] | "\(.id): \(.title) - passes: \(.passes) (priority: \(.priority))"' prd.json || echo "No user stories"`

Progress file:
!`[ -f "progress.txt" ] && echo "progress.txt exists (last 5 lines):" && tail -5 progress.txt || echo "No progress.txt"`

Last branch file:
!`[ -f ".last-branch" ] && echo "Last branch: $(cat .last-branch)" || echo "No .last-branch"`

Archive directory:
!`[ -d "archive" ] && echo "Archive exists with $(find archive -type f -name "*.json" | wc -l) PRD files" || echo "No archive directory"`

Provide a summary of Ralph's current state.