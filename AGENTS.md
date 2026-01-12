# Ralph Agent Instructions

## Overview

Ralph is an autonomous AI agent loop that runs OpenCode repeatedly until all PRD items are complete. Each iteration is a fresh OpenCode agent with clean context.

## OpenCode Integration

Ralph now uses OpenCode tools instead of Amp. The `ralph.sh` script pipes `prompt.md` to `opencode run`. The prompt contains detailed instructions for the OpenCode agent, including tool usage and quality gates.

## Commands

```bash
# Run the flowchart dev server (optional visualization)
cd flowchart && npm run dev

# Build the flowchart
cd flowchart && npm run build

# Run Ralph (requires prd.json in current directory)
./ralph.sh [max_iterations]

# Run Python quality checks (if working on Python projects)
uv run pytest tdd/ -v
uv run ruff check . --fix
uv run ruff format .
```

## Key Files

- `ralph.sh` - The bash loop that spawns fresh OpenCode agents
- `prompt.md` - Instructions given to each OpenCode agent (detailed tool usage)
- `prd.json.example` - Example PRD format
- `flowchart/` - Interactive React Flow diagram explaining how Ralph works
- `scripts/ralph/validate_prd.py` - PRD validation utility
- `tdd/test_ralph_opencode.py` - TDD tests for Ralph core functionality

## Python Environment

For Python projects, Ralph uses UV for environment management:

1. **Setup environment**:
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

2. **Quality gates** (run before committing):
   - `uv run pytest tdd/ -v` (tests must pass)
   - `uv run ruff check . --fix` (linting)
   - `uv run ruff format .` (formatting)
   - `uv run ty .` (type checking, if configured)

See `prompt.md` for full agent instructions.

## Flowchart

The `flowchart/` directory contains an interactive visualization built with React Flow. It's designed for presentations - click through to reveal each step with animations.

To run locally:
```bash
cd flowchart
npm install
npm run dev
```

 ## Patterns

- Each iteration spawns a fresh OpenCode agent with clean context
- Memory persists via git history, `progress.txt`, and `prd.json`
- Stories should be small enough to complete in one context window
- Always update AGENTS.md with discovered patterns for future iterations
- Use OpenCode tools (Read, Edit, Write, Bash, Glob, Grep, Task, Skill) as described in prompt.md

## OpenCode Commands for Ralph

Ralph includes custom OpenCode commands for common tasks:

- `/ralph-validate` - Validate PRD.json structure
- `/ralph-run` - Run Ralph with optional max iterations (`/ralph-run 5`)
- `/ralph-status` - Check current Ralph status and progress
- `/ralph-quality` - Run quality gates (tests, linting, formatting)
- `/ralph-test-complete` - Test command that outputs COMPLETE signal

Commands are defined in `.opencode/command/` directory.

## Testing

### Unit Tests
```bash
uv run pytest tdd/ -v
```

### Integration Tests (slow - require OpenCode CLI)
```bash
# Run all tests including integration
uv run pytest tests/ -v

# Run only integration tests (marked with @pytest.mark.integration)
uv run pytest tests/ -m integration -v

# Skip slow integration tests
uv run pytest tests/ -m "not integration" -v
```

### Quality Gates
```bash
uv run ruff check . --fix
uv run ruff format .
```
