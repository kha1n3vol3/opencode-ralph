---
description: Run Ralph with optional max iterations
---

Run Ralph autonomous agent loop.

Max iterations: $ARGUMENTS (default: 10)

Check current PRD status:
!`jq '.project, .branchName, .description' prd.json 2>/dev/null || echo "No PRD found"`
!`echo "User stories:"; jq '.userStories[] | "\(.id): \(.title) - passes: \(.passes)"' prd.json 2>/dev/null || echo "  No user stories"`

Run Ralph with $ARGUMENTS iterations:
!`[ -f "./ralph.sh" ] && echo "Ralph script found" || echo "Ralph script not found"`
!`[ -f "prd.json" ] && echo "PRD found" || echo "PRD not found"`

If you want to run Ralph, execute: `./ralph.sh $ARGUMENTS`

Check if Ralph is properly set up before running.