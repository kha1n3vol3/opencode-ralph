---
description: Validate PRD.json for Ralph
---

Validate the PRD.json file for Ralph using OpenCode native tools or Python script.

## Validation Methods

### 1. Python script (legacy)
```bash
python3 scripts/ralph/validate_prd.py prd.json && echo "✓ PRD valid" || echo "✗ PRD invalid"
```

### 2. OpenCode native validation
The Ralph skill performs validation using OpenCode `read` tool to check:
- Required top-level fields: `project`, `branchName`, `description`, `userStories`
- Each user story has required fields: `id`, `title`, `description`, `acceptanceCriteria`, `priority`, `passes`, `notes`
- `userStories` is a list, `acceptanceCriteria` is a list

## Quick Check
!`jq '.project, .branchName, .description' prd.json 2>/dev/null || echo "No PRD found"`
!`echo "User story count:"; jq '.userStories | length' prd.json 2>/dev/null || echo "0"`

If the PRD is invalid, explain what's wrong and suggest fixes.