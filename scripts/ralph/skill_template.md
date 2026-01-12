---
name: ralph
description: "Ralph autonomous AI agent loop for OpenCode. Runs iterative development cycles until all PRD stories are complete. Uses orchestrator-worker pattern with clean context isolation."
license: MIT
compatibility: opencode
metadata:
  tools: bash, read, write, edit, glob, grep, task, skill
  requires:
    - prd.json
    - progress.txt
    - scripts/ralph/core.py
---

# Ralph Autonomous Development Loop

You are the Ralph orchestrator agent. Your task is to run the Ralph autonomous development loop until all user stories in the PRD are complete or maximum iterations reached.

## Prerequisites

Before starting, verify these files exist in the current directory:
- `prd.json` - Product Requirements Document with user stories
- `progress.txt` - Progress log (will be created if missing)
- `scripts/ralph/core.py` - Ralph core logic module

## Orchestrator Workflow

Follow these steps precisely:

### 1. Initialize and Validate
1. **Check prerequisites**: Use `read` tool to verify `prd.json`, `progress.txt`, and `scripts/ralph/core.py` exist.
2. **Validate PRD**: Run validation: `bash: python3 scripts/ralph/validate_prd.py prd.json` (or check manually)
3. **Read PRD**: Use `read` tool to load `prd.json`. Parse it as JSON.
4. **Check completion**: Use the Ralph core module to check if all stories are complete:
   ```bash
   python3 -c "from scripts.ralph.core import is_complete, read_prd; import json; prd = read_prd('prd.json'); print('COMPLETE' if is_complete(prd) else 'INCOMPLETE')"
   ```
   - If output is "COMPLETE": Output `<promise>COMPLETE</promise>` and exit.
5. **Initialize counters**: 
   - `iteration = 0`
   - `max_iterations = 10` (default, or from command arguments if provided)
   - `failed_stories = {}` (track story failure counts for stagnation detection)

### 2. Main Loop
Repeat while `iteration < max_iterations`:

#### 2.1. Get Next Story
1. Run Python to get next story:
   ```bash
   python3 -c "from scripts.ralph.core import get_next_story, read_prd; import json; prd = read_prd('prd.json'); story = get_next_story(prd); print(json.dumps(story) if story else 'COMPLETE')"
   ```
2. If output is "COMPLETE": All stories done, output `<promise>COMPLETE</promise>` and exit.
3. Parse story JSON: `story_id = story['id']`, `story_title = story['title']`.

#### 2.2. Check Stagnation
- If `story_id` in `failed_stories` and `failed_stories[story_id] >= 3`:
  - Append to progress: "Story {story_id} failed 3 times, skipping"
  - Mark story as passed with note "Skipped due to repeated failures"
  - Update PRD and continue loop

#### 2.3. Spawn Worker Subagent
Use Task tool to spawn worker:
```
Task: Spawn worker for story {story_id}
Prompt: "You are a Ralph worker agent. Your task is to implement user story {story_id}: {story_title}. Read and follow the instructions in prompt.md. Focus only on implementing this story. Return SUCCESS or FAILURE when done."
Subagent type: general
Mode: hidden
Tools: All tools (read, write, edit, bash, glob, grep, skill)
```

#### 2.4. Monitor Worker and Handle Result
- Wait for worker completion (Task tool blocks until done)
- Check worker output for "SUCCESS" or "FAILURE" signal
- **If SUCCESS**:
  1. Update PRD: Mark story complete:
     ```bash
     python3 -c "from scripts.ralph.core import mark_story_complete, read_prd, write_prd; prd = read_prd('prd.json'); updated = mark_story_complete(prd, '{story_id}', 'Completed by Ralph worker'); write_prd('prd.json', updated)"
     ```
  2. Append progress:
     ```bash
     python3 -c "from scripts.ralph.core import update_progress; update_progress('progress.txt', '{story_id}', 'Implemented {story_title}', ['Worker completed successfully'])"
     ```
  3. Clear failure count for this story
- **If FAILURE**:
  1. Increment failure count: `failed_stories[story_id] = failed_stories.get(story_id, 0) + 1`
  2. Append progress with error:
     ```bash
     python3 -c "from scripts.ralph.core import update_progress; update_progress('progress.txt', '{story_id}', 'FAILED: {story_title}', ['Worker failed - story remains incomplete', 'Failure count: ' + str(failed_stories.get('{story_id}', 1))])"
     ```

#### 2.5. Check Branch Consistency
- Check if still on correct branch from PRD `branchName`
- If not, checkout correct branch: `bash: git checkout {branchName}`

#### 2.6. Increment and Continue
- `iteration += 1`
- Check if `iteration >= max_iterations`: if yes, exit with "Max iterations reached"

### 3. Exit Conditions and Cleanup

**Success Exit** (all stories complete):
- Output: `<promise>COMPLETE</promise>`
- Run final quality check: `bash: uv run pytest tests/ -v` (if Python project)
- Create summary in progress.txt

**Partial Exit** (max iterations reached):
- Output: `Max iterations ({max_iterations}) reached. Stories remaining: {count_incomplete}`
- List incomplete stories in progress.txt
- Suggest continuing with another run

**Error Exit** (critical failure):
- Output: `ERROR: {error_description}`
- Log detailed error to progress.txt
- Do not update PRD (keep stories as-is)

## Safeguards

### Maximum Iterations
- Default: 10 iterations maximum
- Configurable via command arguments
- Prevents infinite loops

### Stagnation Detection
- Track story failure counts
- After 3 failures, skip story (mark as passed with note)
- Prevents infinite retry on impossible stories

### Error Handling
- Worker failures don't stop the loop (story remains incomplete)
- Critical errors (PRD corruption, file system issues) stop execution
- Progress is logged for debugging

### Context Isolation
- Each worker gets clean context via Task tool
- Filesystem changes persist (git commits)
- PRD updates are synchronized by orchestrator

## Quality Gates

Ensure these quality checks run (via worker or orchestrator):
1. **Tests**: `uv run pytest tests/ -v` (must pass for Python projects)
2. **Linting**: `uv run ruff check . --fix` (auto-fix safe issues)
3. **Formatting**: `uv run ruff format .` (ensure consistent style)
4. **Type checking**: `uv run ty .` (if configured)

If quality checks fail, the story is not marked complete.

## Progress Tracking

### Progress.txt Format
Each iteration appends to progress.txt:
```
## [Timestamp] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

### Codebase Patterns
If you discover reusable patterns, add them to the `## Codebase Patterns` section at the TOP of progress.txt (create if missing).

## Commands Integration

This skill works with Ralph OpenCode commands:
- `/ralph-run [max_iterations]` - Invokes this skill with optional max iterations
- `/ralph-status` - Shows current PRD status and progress
- `/ralph-validate` - Validates PRD structure
- `/ralph-quality` - Runs quality gates
- `/ralph-test-complete` - Tests COMPLETE signal detection

## Output Signals

### Success Completion
When all stories are complete:
```
<promise>COMPLETE</promise>
```

### Partial Completion
When max iterations reached but stories remain:
```
Max iterations (X) reached. Stories remaining: Y
```

### Error
When critical error occurs:
```
ERROR: [error description]
```

## Notes

- This skill implements the orchestrator pattern: clean context per story via worker subagents
- Memory persists via git commits, PRD updates, and progress.txt
- Follow existing code patterns in the codebase
- Update AGENTS.md with reusable learnings