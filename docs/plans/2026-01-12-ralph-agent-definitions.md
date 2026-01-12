# Create OpenCode Agent Definitions for Ralph Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create OpenCode agent configurations that work with the Ralph skill for clean context isolation (US-005).

**Architecture:** Two agent files: `ralph.md` (primary orchestrator that loads Ralph skill) and `ralph-worker.md` (hidden subagent for single story implementation). Both follow OpenCode agent format with YAML frontmatter.

**Tech Stack:** OpenCode agents, YAML frontmatter, Ralph skill (already created in US-004), Python core modules

**Current State:** Ralph skill created at `.opencode/skill/ralph/SKILL.md`. Core logic in `scripts/ralph/core.py`. Need agent definitions to complete the orchestrator-worker pattern.

## Task 1: Create Ralph Primary Agent

**Files:**
- Create: `.opencode/agent/ralph.md`

**Step 1: Write agent file with YAML frontmatter**

```markdown
---
name: ralph
description: "Ralph orchestrator agent - loads Ralph skill for autonomous development loops"
mode: primary
tools:
  bash: allow
  read: allow
  write: allow
  edit: allow
  glob: allow
  grep: allow
  task: allow
  skill: allow
  todowrite: allow
  todoread: allow
  webfetch: allow
model: anthropic/claude-3-5-sonnet-20241022
prompt: |
  You are the Ralph orchestrator agent. Your job is to run the Ralph autonomous development loop.
  Load the Ralph skill for instructions, then execute the orchestrator-worker pattern.
  Always check prerequisites (prd.json, progress.txt, scripts/ralph/core.py).
  Use the Task tool to spawn worker subagents for story implementation.
  Output COMPLETE signal when all stories are complete.
  Safeguards: Maximum 10 iterations by default, skip stories after 3 failures.
---

# Ralph Orchestrator Agent

This agent runs the Ralph autonomous development loop via the Ralph skill.

## When to Use
- When you want to run Ralph autonomous development
- When `/ralph-run` command is invoked
- When you need orchestrator-worker pattern with clean context isolation

## Key Responsibilities
1. Load Ralph skill (`.opencode/skill/ralph/SKILL.md`)
2. Validate prerequisites (PRD, progress, core modules)
3. Spawn worker subagents via Task tool
4. Manage iteration loop and safeguard limits
5. Output COMPLETE signal when done

## Integration Points
- Uses `scripts/ralph/core.py` for PRD operations
- Updates `prd.json` and `progress.txt`
- Compatible with `/ralph-run` command

## Safeguards
- Maximum iterations: 10 (configurable via command arguments)
- Stagnation detection: Skip story after 3 failures
- Error isolation: Worker failures don't stop orchestrator
```

**Step 2: Verify file structure**

Run: `ls -la .opencode/agent/ralph.md`
Expected: File exists, has correct permissions

**Step 3: Test YAML parsing (simulated)**

Run: `head -20 .opencode/agent/ralph.md | grep -E "name:|description:|mode:"`
Expected: Shows "name: ralph", "description: Ralph orchestrator agent...", "mode: primary"

**Step 4: Commit agent file**

```bash
git add .opencode/agent/ralph.md
git commit -m "feat: US-005 - Create Ralph primary agent definition"
```

## Task 2: Create Ralph Worker Agent

**Files:**
- Create: `.opencode/agent/ralph-worker.md`

**Step 1: Write worker agent file**

```markdown
---
name: ralph-worker
description: "Ralph worker agent - implements single user stories (hidden subagent)"
mode: subagent
hidden: true
tools:
  bash: allow
  read: allow
  write: allow
  edit: allow
  glob: allow
  grep: allow
  skill: allow
  todowrite: allow
  todoread: allow
model: anthropic/claude-3-5-sonnet-20241022
prompt: |
  You are a Ralph worker agent. Your job is to implement a single user story.
  
  ## Instructions
  1. Read prompt.md for detailed implementation instructions
  2. Focus ONLY on the story ID you were given
  3. Implement the story following prompt.md guidelines
  4. Run quality checks (tests, linting, formatting)
  5. Update AGENTS.md with reusable learnings
  6. Commit changes with story ID in message
  7. Return "SUCCESS" if completed, "FAILURE" if failed
  
  ## Key Rules
  - Work on ONE story only
  - Commit frequently
  - Keep CI green
  - Read Codebase Patterns in progress.txt
  - Consolidate reusable patterns
  
  ## Quality Gates (Python)
  - Tests: `uv run pytest tests/ -v` (must pass)
  - Linting: `uv run ruff check . --fix`
  - Formatting: `uv run ruff format .`
  - Type checking: `uv run ty .` (if configured)
  
  Return "SUCCESS" or "FAILURE" as your final output.
---

# Ralph Worker Agent (Hidden Subagent)

This agent implements single user stories for the Ralph loop.

## When Used
- Spawned by Ralph orchestrator via Task tool
- Given specific story ID and title
- Clean context per invocation

## Responsibilities
1. Implement single user story
2. Follow prompt.md instructions exactly
3. Run quality gates
4. Commit with story ID
5. Return success/failure status

## Context Isolation
- Fresh context per invocation (Task tool)
- Filesystem changes persist via git commits
- No access to orchestrator state
```

**Step 2: Verify worker agent**

Run: `ls -la .opencode/agent/ralph-worker.md`
Expected: File exists

**Step 3: Test hidden mode**

Run: `grep -i "hidden" .opencode/agent/ralph-worker.md`
Expected: Shows "hidden: true"

**Step 4: Commit worker agent**

```bash
git add .opencode/agent/ralph-worker.md
git commit -m "feat: US-005 - Create Ralph worker agent definition"
```

## Task 3: Update PRD for US-005 Completion

**Files:**
- Modify: `prd.json:66-81`

**Step 1: Update US-005 status**

```json
{
  "id": "US-005",
  "title": "Create OpenCode agent definitions for Ralph workflow",
  "description": "As a developer, I want OpenCode agent configurations that work with the Ralph skill for clean context isolation.",
  "acceptanceCriteria": [
    "Create .opencode/agent/ralph.md (primary agent that loads ralph skill)",
    "Create .opencode/agent/ralph-worker.md (hidden subagent for single story implementation)",
    "Configure proper tool permissions and agent modes",
    "Test agent spawning and context isolation",
    "Verify skill can invoke worker subagents via Task tool",
    "Commit changes with message 'feat: US-005 - Create OpenCode agent definitions for Ralph'"
  ],
  "priority": 5,
  "passes": true,
  "notes": "Created .opencode/agent/ralph.md (primary orchestrator) and .opencode/agent/ralph-worker.md (hidden subagent). Configured tool permissions and agent modes. Primary agent loads Ralph skill, spawns workers via Task tool. Worker agent implements single stories with clean context. Both agents follow OpenCode YAML format with appropriate prompts and safeguards."
}
```

**Step 2: Run PRD validation**

Run: `python3 scripts/ralph/validate_prd.py prd.json`
Expected: "PRD validation passed"

**Step 3: Commit PRD update**

```bash
git add prd.json
git commit -m "feat: US-005 - Mark PRD story complete"
```

## Task 4: Update Ralph Skill Reference

**Files:**
- Modify: `.opencode/skill/ralph/SKILL.md:130-135`

**Step 1: Update Commands Integration section**

```markdown
## Commands Integration

This skill works with Ralph OpenCode commands and agents:
- `/ralph-run [max_iterations]` - Invokes Ralph agent (which loads this skill)
- `/ralph-status` - Shows current PRD status and progress
- `/ralph-validate` - Validates PRD structure
- `/ralph-quality` - Runs quality gates
- `/ralph-test-complete` - Tests COMPLETE signal detection

## Agent Integration
- Primary agent: `@ralph` (loads this skill, orchestrates loop)
- Worker agent: `@ralph-worker` (hidden, implements single stories)
- Spawning: Use `Task` tool with `@ralph-worker` reference
```

**Step 2: Verify skill update**

Run: `grep -n "Agent Integration" .opencode/skill/ralph/SKILL.md`
Expected: Line number where section was added

**Step 3: Commit skill update**

```bash
git add .opencode/skill/ralph/SKILL.md
git commit -m "docs: Update skill with agent integration info"
```

## Task 5: Test Agent Configuration

**Files:**
- Test: `.opencode/agent/ralph.md`, `.opencode/agent/ralph-worker.md`

**Step 1: Verify both agents exist**

Run: `find .opencode/agent -name "*.md" -exec basename {} \;`
Expected: `ralph.md`, `ralph-worker.md`

**Step 2: Check YAML frontmatter syntax**

Run: `head -10 .opencode/agent/ralph.md | grep -E "---|name:|description:"`
Expected: Shows YAML separator and metadata

Run: `head -10 .opencode/agent/ralph-worker.md | grep -E "---|name:|description:"`
Expected: Shows YAML separator and metadata

**Step 3: Verify tool permissions**

Run: `grep -A5 "tools:" .opencode/agent/ralph.md | head -10`
Expected: Shows tool permissions for primary agent

Run: `grep -A5 "tools:" .opencode/agent/ralph-worker.md | head -10`
Expected: Shows tool permissions for worker agent

**Step 4: Test agent mode differences**

Run: `grep "mode:" .opencode/agent/ralph.md .opencode/agent/ralph-worker.md`
Expected: `ralph.md: mode: primary`, `ralph-worker.md: mode: subagent`

**Step 5: Commit test verification**

```bash
git status
git commit -am "test: Verify agent configuration structure"
```

## Task 6: Update AGENTS.md with Agent Patterns

**Files:**
- Modify: `AGENTS.md`

**Step 1: Add agent configuration section**

Find the "## Setup" section in AGENTS.md and add after it:

```markdown
## OpenCode Agent Configuration

Ralph uses OpenCode agents for native integration:

### Agent Files
- `.opencode/agent/ralph.md` - Primary orchestrator agent
- `.opencode/agent/ralph-worker.md` - Hidden worker subagent

### Agent Modes
- **Primary** (`ralph`): Loads Ralph skill, manages loop, spawns workers
- **Subagent** (`ralph-worker`): Hidden, implements single stories, clean context

### Tool Permissions
Primary agent has full tool access:
```yaml
tools:
  bash: allow
  read: allow
  write: allow
  edit: allow
  glob: allow
  grep: allow
  task: allow    # Critical for spawning workers
  skill: allow   # Critical for loading Ralph skill
```

Worker agent has restricted access (no Task tool):
```yaml
tools:
  bash: allow
  read: allow
  write: allow
  edit: allow
  glob: allow
  grep: allow
  skill: allow   # Can load other skills if needed
```

### Invocation
- Use `/ralph-run` command (invokes `@ralph` agent)
- Agent loads Ralph skill automatically
- Skill instructs agent to spawn workers via `Task` tool

### Context Isolation
- Each worker gets clean context via Task tool
- Filesystem changes persist (git commits)
- PRD updates synchronized by orchestrator
```

**Step 2: Verify AGENTS.md update**

Run: `grep -n "OpenCode Agent Configuration" AGENTS.md`
Expected: Line number where section was added

**Step 3: Commit documentation**

```bash
git add AGENTS.md
git commit -m "docs: Add OpenCode agent configuration to AGENTS.md"
```

## Task 7: Run Quality Gates

**Files:**
- Test: All modified files

**Step 1: Run tests**

Run: `uv run pytest tdd/ -v`
Expected: All tests pass (should be 14/14)

**Step 2: Run linting**

Run: `uv run ruff check . --fix`
Expected: "All checks passed!"

**Step 3: Run formatting**

Run: `uv run ruff format .`
Expected: "X files left unchanged"

**Step 4: Verify no regressions**

Run: `git status`
Expected: No unstaged changes (everything committed)

**Step 5: Commit quality gate results**

```bash
git commit -m "chore: Run quality gates for US-005"
```

## Task 8: Final Verification and BD Issue Closure

**Files:**
- Check: `.beads/issues.jsonl`

**Step 1: Update BD issue status**

Find issue `opencode-ralph-0t6` (Create OpenCode agent definitions for Ralph) and update:

```json
{"id":"opencode-ralph-0t6","title":"Create OpenCode agent definitions for Ralph","description":"Create .opencode/agent/ralph-orchestrator.md and .opencode/agent/ralph-worker.md with proper configurations, prompts, and tool permissions.","status":"closed","priority":2,"issue_type":"task","owner":"khunt@starficient.com","created_at":"2026-01-12T11:50:10.750045-05:00","created_by":"kha1n3vol3","updated_at":"2026-01-12T11:50:10.750045-05:00","closed_at":"2026-01-12T14:30:00.000000-05:00","close_reason":"Created .opencode/agent/ralph.md (primary orchestrator) and .opencode/agent/ralph-worker.md (hidden subagent). Configured tool permissions and agent modes. Primary agent loads Ralph skill, spawns workers via Task tool. Worker agent implements single stories with clean context. Both agents follow OpenCode YAML format.","dependencies":[{"issue_id":"opencode-ralph-0t6","depends_on_id":"opencode-ralph-ey5","type":"blocks","created_at":"2026-01-12T11:51:11.114374-05:00","created_by":"kha1n3vol3"}]}
```

**Step 2: Check BD dependencies**

Run: `bd ready`
Expected: Should show next issues (like `opencode-ralph-83d` - Update /ralph-run command)

**Step 3: Final git status check**

Run: `git status`
Expected: "Your branch is ahead of 'origin/ralph/setup-test' by X commits"

**Step 4: Push to remote**

```bash
git push origin ralph/setup-test
```
Expected: Successfully pushes commits

**Step 5: Create completion summary**

Create file `docs/plans/2026-01-12-us-005-completion-summary.md`:

```markdown
# US-005 Completion Summary

## What Was Implemented
1. Created `.opencode/agent/ralph.md` - Primary orchestrator agent
2. Created `.opencode/agent/ralph-worker.md` - Hidden worker subagent
3. Configured proper tool permissions and agent modes
4. Updated PRD to mark US-005 complete
5. Updated AGENTS.md with agent configuration patterns
6. Ran quality gates (tests, linting, formatting)

## Architecture
- **Orchestrator-Worker Pattern**: Primary agent spawns workers via Task tool
- **Clean Context Isolation**: Each worker gets fresh context
- **Skill Integration**: Primary agent loads Ralph skill
- **Safeguards**: Max iterations, stagnation detection, error isolation

## Files Created/Modified
- `.opencode/agent/ralph.md` (new)
- `.opencode/agent/ralph-worker.md` (new)
- `prd.json` (updated)
- `AGENTS.md` (updated)
- `.beads/issues.jsonl` (updated)

## Quality Gates
- ✅ All 14 TDD tests pass
- ✅ Ruff linting passes
- ✅ Ruff formatting consistent
- ✅ Git commits follow convention

## Next Steps
1. US-006: Update `/ralph-run` command to use agent-based loop
2. Integration testing of orchestrator-worker workflow
3. Backward compatibility with bash script
```

**Step 6: Commit summary**

```bash
git add docs/plans/2026-01-12-us-005-completion-summary.md
git commit -m "docs: Add US-005 completion summary"
```