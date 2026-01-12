# Ralph OpenCode Skill Design

**Date**: 2026-01-12  
**Status**: Implemented (US-004)  
**Author**: OpenCode Agent  
**Related**: PRD US-004, Ralph orchestrator-worker architecture

## Overview

The Ralph OpenCode skill implements an autonomous development loop using orchestrator-worker pattern with clean context isolation per story iteration. It replaces the bash script (`ralph.sh`) with native OpenCode skill/agent integration.

## Architecture

### Components
1. **Ralph Skill** (`.opencode/skill/ralph/SKILL.md`): Defines orchestrator behavior
2. **Ralph Agent** (`.opencode/agent/ralph.md`): Primary agent that loads skill (US-005)
3. **Worker Subagents**: Spawned via Task tool with `prompt.md` instructions
4. **Core Modules** (`scripts/ralph/core.py`): Python utilities for PRD processing

### Data Flow
```
[Ralph Agent] → [Loads Ralph Skill] → [Orchestrator Loop] → [Spawn Worker via Task] → [Worker implements story] → [Update PRD/Progress] → [Loop until complete]
```

## Skill Design Details

### YAML Frontmatter
```yaml
name: ralph
description: "Ralph autonomous AI agent loop for OpenCode..."
license: MIT
compatibility: opencode
metadata:
  tools: bash, read, write, edit, glob, grep, task, skill
  requires:
    - prd.json
    - progress.txt
    - scripts/ralph/core.py
```

### Key Sections
1. **Prerequisites**: Verifies required files exist
2. **Orchestrator Workflow**: Step-by-step loop instructions
3. **Safeguards**: Max iterations, stagnation detection, error handling
4. **Quality Gates**: Test/lint/format/typecheck requirements
5. **Progress Tracking**: progress.txt format and Codebase Patterns
6. **Commands Integration**: Works with `/ralph-run`, `/ralph-status`, etc.
7. **Output Signals**: COMPLETE signal, partial completion, error messages

### Orchestrator Workflow Steps
1. **Initialize**: Validate PRD, check completion, set counters
2. **Main Loop** (while iteration < max_iterations):
   - Get next story via `get_next_story()`
   - Check stagnation (skip after 3 failures)
   - Spawn worker subagent via Task tool
   - Monitor worker result (SUCCESS/FAILURE)
   - Update PRD and progress accordingly
   - Check branch consistency
   - Increment iteration
3. **Exit Conditions**:
   - Success: All stories complete → `<promise>COMPLETE</promise>`
   - Partial: Max iterations reached → status message
   - Error: Critical failure → error description

### Safeguards
- **Max Iterations**: Default 10, configurable
- **Stagnation Detection**: Skip story after 3 failures
- **Error Isolation**: Worker failures don't stop loop
- **Context Isolation**: Clean context per worker via Task tool

## Integration Points

### With Existing Ralph Components
- Uses `scripts/ralph/core.py` for PRD operations
- References `prompt.md` for worker instructions
- Updates `prd.json` and `progress.txt`
- Compatible with existing OpenCode commands (`/ralph-run`, etc.)

### OpenCode Ecosystem
- Skill discoverable via `opencode debug skill`
- Can be invoked via `/ralph-run [max_iterations]`
- Works with OpenCode permission system

## Implementation Notes

### Skill Creation (US-004 Completed)
- Created `.opencode/skill/ralph/SKILL.md` with detailed instructions
- Created `scripts/ralph/skill_template.md` for installation
- Updated `scripts/ralph/install.py` to use new template
- All tests pass, skill loads correctly

### Agent Definitions (US-005 Pending)
- Need to create `.opencode/agent/ralph.md` (primary)
- Need to create `.opencode/agent/ralph-worker.md` (optional hidden subagent)
- Configure tool permissions and agent modes

### Command Updates (Future)
- Update `/ralph-run` to invoke Ralph agent instead of bash script
- Maintain backward compatibility

## Testing

### Skill Loading
✅ Skill appears in `opencode debug skill` output  
✅ Skill file has valid YAML frontmatter  
✅ Skill content is readable and properly structured

### Installation
✅ `install_ralph_skill()` copies skill template  
✅ Target project receives functional skill  
✅ All Python dependencies copied

### Core Logic
✅ All TDD tests pass (14/14)  
✅ Core modules handle PRD operations correctly  
✅ Quality gates (ruff linting/formatting) pass

## Next Steps

1. **US-005**: Create OpenCode agent definitions
   - Ralph primary agent (loads skill)
   - Ralph worker agent (optional, for cleaner worker definitions)
2. **Update `/ralph-run` command**: Switch from bash script to agent invocation
3. **Integration testing**: Verify end-to-end workflow
4. **Backward compatibility**: Maintain support for existing bash script workflow

## Design Decisions

### Orchestrator-Worker Pattern
Chosen over single-agent loop because:
- Clean context isolation per story (matches research findings)
- Worker failures don't corrupt orchestrator state
- Matches original Ralph pattern (fresh OpenCode agent per iteration)
- Enables parallelization potential in future

### Skill vs Agent Separation
- **Skill** defines behavior (reusable across agents)
- **Agent** provides execution context and permissions
- Separation allows different agents to use Ralph skill with different configurations

### Python Integration
Skill uses Python commands (`python3 -c "...") to call core modules because:
- Core logic already implemented in Python
- Reuse existing tested code
- More reliable than reimplementing in natural language instructions
- Agent can execute bash commands with Python

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Skill too complex for agents to follow | Test with actual OpenCode agent execution |
| Python command injection vulnerabilities | Story IDs are safe (US-XXX format) |
| Installation path issues | Use relative paths, test installation |
| Permission conflicts | Configure `opencode.json` appropriately |

## Conclusion

The Ralph skill successfully encapsulates the autonomous development loop in OpenCode-native format. It maintains compatibility with existing Ralph components while providing cleaner integration via skills and agents. The orchestrator-worker pattern ensures context isolation and robust error handling.