---
description: Run Ralph with optional max iterations
---

Run Ralph autonomous agent loop using OpenCode orchestrator-worker pattern.

Max iterations: $ARGUMENTS (default: 10)

Check current PRD status:
!`jq '.project, .branchName, .description' prd.json 2>/dev/null || echo "No PRD found"`
!`echo "User stories:"; jq '.userStories[] | "\(.id): \(.title) - passes: \(.passes)"' prd.json 2>/dev/null || echo "  No user stories"`

Check Ralph setup:
!`[ -f ".opencode/agent/ralph.md" ] && echo "✓ Ralph subagent found" || echo "✗ Ralph subagent missing"`
!`[ -f ".opencode/agent/ralph-worker.md" ] && echo "✓ Ralph worker agent found" || echo "✗ Ralph worker agent missing"`
!`[ -f ".opencode/skill/ralph/SKILL.md" ] && echo "✓ Ralph skill found" || echo "✗ Ralph skill missing"`

## Usage Options

### 1. Invoke via @mention (recommended)
Simply mention `@ralph` in your conversation:

```
@ralph run the autonomous loop
```

The Ralph subagent will load the Ralph skill and start the iterative development loop.

### 2. Use OpenCode CLI directly
```bash
opencode run --agent ralph --maxSteps 100 $ARGUMENTS
```

### 3. Manual orchestration
You can also manually trigger the orchestrator via Task tool:
```
Task: Run Ralph orchestrator for demonstration
Prompt: "Load the Ralph skill and run one iteration to demonstrate the workflow"
Subagent type: general
```

## What Happens Next

The Ralph subagent (`.opencode/agent/ralph.md`) will:
1. Load the Ralph skill
2. Validate prerequisites (PRD, progress.txt) using OpenCode native tools
3. Spawn worker subagents for each user story via Task tool
4. Output COMPLETE signal when all stories are complete

## Notes
- Ralph now uses pure OpenCode tools (read/write/edit/todowrite/todoread) - no external Python scripts
- PRD processing and progress tracking done entirely within OpenCode
- Each story gets clean context isolation via worker subagents