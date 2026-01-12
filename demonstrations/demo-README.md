# Ralph OpenCode Demo

This demonstration shows how to use Ralph autonomous development loop with OpenCode.

## Overview

Ralph is an autonomous AI agent loop that runs OpenCode repeatedly until all PRD items are complete. Each iteration is a fresh OpenCode agent with clean context.

## Quick Start

### 1. Create PRD
Create `prd.json` in your project root:
```json
{
  "project": "My Project",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add feature X",
      "description": "As a user, I want X so that Y.",
      "acceptanceCriteria": [
        "Create component X",
        "Add tests for X",
        "Commit with message 'feat: US-001 - Add feature X'"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### 2. Run Ralph
Invoke Ralph via OpenCode:

**Option A: Via @mention (recommended)**
```
@ralph run the autonomous development loop
```

**Option B: Via command**
```
/ralph-run [max_iterations]
```
Example: `/ralph-run 5` for 5 iterations maximum.

**Option C: Via OpenCode CLI**
```bash
opencode run --agent ralph --maxSteps 100
```

## Example PRD Structure

A valid PRD must include:
- `project`: Project name
- `branchName`: Git branch to work on (e.g., "ralph/feature-name")
- `description`: Brief description of the feature
- `userStories`: Array of stories, each with:
  - `id`: Unique identifier (e.g., "US-001")
  - `title`: Short title
  - `description`: User story format
  - `acceptanceCriteria`: List of verifiable criteria
  - `priority`: Number (lower = higher priority)
  - `passes`: Boolean (initially false)
  - `notes`: Optional notes

## Invocation Commands

OpenCode includes these Ralph commands:

- `/ralph-validate` - Validate PRD.json structure
- `/ralph-run` - Run Ralph loop with optional max iterations
- `/ralph-status` - Check current Ralph status and progress
- `/ralph-quality` - Run quality gates (tests, linting, formatting)
- `/ralph-test-complete` - Test COMPLETE signal detection

## Expected Output

When Ralph runs successfully:

1. **Creates progress.txt** - Tracks iterations and learnings
2. **Implements stories** - One story per iteration
3. **Runs quality gates** - Tests, linting, formatting
4. **Commits changes** - With story ID in commit message
5. **Updates PRD** - Sets `passes: true` for completed stories
6. **Outputs COMPLETE** - When all stories done: `<promise>COMPLETE</promise>`

## Workflow Example

```
## 2026-01-12 15:30:00 - US-001
- Created demonstration README file
- **Learnings for future iterations:**
  - OpenCode agents use native tools for PRD operations
  - Ralph orchestrator-worker pattern provides clean context isolation
---
```

## Troubleshooting

### PRD Validation Errors
Run `/ralph-validate` to check PRD structure.

### Ralph Not Starting
- Verify `.opencode/agent/ralph.md` exists
- Check `.opencode/skill/ralph/SKILL.md` exists
- Ensure `jq` is installed (`brew install jq` on macOS)

### Quality Gates Failing
- Run `/ralph-quality` to see test/lint/format results
- Fix any issues before committing

### COMPLETE Signal Not Detected
Agent must output exact text: `<promise>COMPLETE</promise>`

## Next Steps

After this demo, you can:
1. Create your own PRD with real user stories
2. Run Ralph to implement features autonomously
3. Monitor progress in `progress.txt`
4. Extend Ralph with custom skills and agents

## Resources

- [Ralph GitHub Repository](https://github.com/kha1n3vol3/opencode-ralph)
- [OpenCode Documentation](https://opencode.ai/docs)
- [AGENTS.md](./../AGENTS.md) - Project-specific patterns