---
description: Run Ralph with optional max iterations
---

Run Ralph autonomous agent loop using OpenCode orchestrator-worker pattern.

Max iterations: $ARGUMENTS (default: 10)

Check current PRD status:
!`jq '.project, .branchName, .description' prd.json 2>/dev/null || echo "No PRD found"`
!`echo "User stories:"; jq '.userStories[] | "\(.id): \(.title) - passes: \(.passes)"' prd.json 2>/dev/null || echo "  No user stories"`

Check Ralph setup:
!`[ -f ".opencode/agent/ralph.md" ] && echo "✓ Ralph orchestrator agent found" || echo "✗ Ralph orchestrator agent missing"`
!`[ -f ".opencode/agent/ralph-worker.md" ] && echo "✓ Ralph worker agent found" || echo "✗ Ralph worker agent missing"`
!`[ -f ".opencode/skill/ralph/SKILL.md" ] && echo "✓ Ralph skill found" || echo "✗ Ralph skill missing"`

To run Ralph with the OpenCode agent workflow:

```bash
# Method 1: Use OpenCode directly
opencode run --agent ralph --maxSteps 100 $ARGUMENTS

# Method 2: Use Task tool to spawn orchestrator
# (This is what the orchestrator does internally)
```

The Ralph orchestrator agent (`.opencode/agent/ralph.md`) will:
1. Load the Ralph skill
2. Validate prerequisites (PRD, progress.txt, core.py)
3. Spawn worker subagents for each user story
4. Output COMPLETE signal when all stories are complete

For demonstration, you can also manually trigger the orchestrator:
```
Task: Run Ralph orchestrator for demonstration
Prompt: "Load the Ralph skill and run one iteration to demonstrate the workflow"
Subagent type: general
```