# Ralph Agent Instructions

## Overview

Ralph is an autonomous AI agent loop that runs OpenCode repeatedly until all PRD items are complete. Each iteration is a fresh OpenCode agent with clean context.

## Setup

### Prerequisites

- [OpenCode CLI](https://opencode.ai) installed and authenticated
- `jq` installed (`brew install jq` on macOS, `apt-get install jq` on Ubuntu)
- A git repository for your project

### Installation Steps

1. **Clone Ralph repository or copy files:**
   ```bash
   # Option 1: Clone as subdirectory
   git clone https://github.com/kha1n3vol3/opencode-ralph.git
   cd opencode-ralph
   
   # Option 2: Install via Python script
   python3 -c "from ralph.install import install_ralph_skill; from pathlib import Path; install_ralph_skill(Path('.'))"
   ```

2. **Verify OpenCode CLI installation:**
   ```bash
   opencode --version
   opencode debug skill | grep -i ralph  # Should show Ralph skill
   ```

3. **Verify jq installation:**
   ```bash
   jq --version
   ```

4. **Create PRD file:**
   ```bash
   cp prd.json.example prd.json
   # Edit prd.json with your user stories
   ```

5. **Run Ralph to verify setup:**
   ```bash
   ./ralph.sh 1  # Run one iteration
   ```
   
   Expected behavior:
   - Ralph creates `progress.txt` if not exists
   - Picks highest priority story from `prd.json`
   - Runs OpenCode agent to implement the story
   - Runs quality gates (tests, linting, formatting)
   - Commits changes with story ID in message
   - Updates `prd.json` with `passes: true` for completed story

### Troubleshooting

- **OpenCode not found**: Install via `npm install -g opencode` or follow [opencode.ai](https://opencode.ai)
- **jq not found**: Install via package manager (`brew install jq`, `apt-get install jq`, etc.)
- **Permission denied on ralph.sh**: Run `chmod +x ralph.sh`
- **PRD validation errors**: Use `/ralph-validate` command or `python scripts/ralph/validate_prd.py`

## OpenCode Integration

Ralph now uses OpenCode tools instead of Amp. The `ralph.sh` script pipes `prompt.md` to `opencode run`. The prompt contains detailed instructions for the OpenCode agent, including tool usage and quality gates.

## OpenCode Agent Configuration

Ralph uses two OpenCode agent configurations for the orchestrator-worker pattern:

### Ralph Subagent (`.opencode/agent/ralph.md`)
- **Mode**: `subagent` (invokable via `@ralph` or `/ralph-run`)
- **Role**: Loads Ralph skill, validates prerequisites, spawns worker subagents
- **Frontmatter**: `mode: subagent`, `model: anthropic/claude-3-5-sonnet-20241022`
- **Tools**: Full access including Task, Skill, todowrite/todoread for state management
- **Behavior**: Implements orchestrator loop with stagnation detection and quality gates using pure OpenCode tools

### Worker Subagent (`.opencode/agent/ralph-worker.md`)
- **Mode**: `subagent` with `hidden: true`
- **Role**: Implements single user story, reads `prompt.md`, runs quality checks
- **Frontmatter**: `mode: subagent`, `hidden: true`, restricted tools (no Task)
- **Behavior**: Returns SUCCESS/FAILURE signal to orchestrator

These agents implement the orchestrator-worker pattern with clean context isolation per US-002 research.

## Idiomatic OpenCode Integration

Ralph now uses **pure OpenCode native tools** instead of external Python scripts:

### Key Changes
1. **Subagent Invocation**: Users invoke Ralph via `@ralph` (idiomatic OpenCode pattern)
2. **Native Tool Usage**: Uses `read`/`write`/`edit`/`todowrite`/`todoread` for all operations
3. **jq for JSON Processing**: Uses `jq` for PRD querying (instead of Python scripts)
4. **No External Dependencies**: Ralph skill works entirely within OpenCode tool ecosystem

### PRD Processing with jq
Ralph uses `jq` commands for PRD operations:
- Check completion: `jq '.userStories | all(.passes == true)' prd.json`
- Get incomplete stories: `jq '.userStories[] | select(.passes == false)' prd.json`
- Get next story: `jq '.userStories[] | select(.passes == false) | {id: .id, title: .title, priority: .priority}' prd.json | jq -s 'sort_by(.priority) | first'`

### State Management with todowrite/todoread
- Iteration counters and failure tracking stored via `todowrite`/`todoread`
- Clean state isolation between orchestrator runs

## Using Ralph (Idiomatic OpenCode Approach)

### Invocation Methods

1. **Via @mention (recommended)**:
   ```bash
   @ralph run the autonomous development loop
   ```
   The Ralph subagent loads the Ralph skill and starts iterating through PRD stories.

2. **Via command**:
   ```bash
   /ralph-run [max_iterations]
   ```
   Example: `/ralph-run 5` for 5 iterations maximum.

3. **Manual orchestration**:
   You can also spawn Ralph via Task tool for testing.

### Workflow
1. Ralph subagent loads Ralph skill
2. Validates PRD using OpenCode `read` tool and `jq`
3. Spawns worker subagents for each story via Task tool
4. Each worker implements a single story, runs quality gates, commits changes
5. Orchestrator updates PRD and progress.txt
6. Loop continues until all stories complete or max iterations reached

## Commands

```bash
# Run the flowchart dev server (optional visualization)
cd flowchart && npm run dev

# Build the flowchart
cd flowchart && npm run build

# Run Ralph via @mention (recommended)
@ralph start development loop

# Alternative: Use legacy bash script (deprecated)
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

- `/ralph-validate` - Validate PRD.json structure (uses both Python script and OpenCode native validation)
- `/ralph-run` - Run Ralph subagent with optional max iterations (`/ralph-run 5`)
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

## Production Demonstration

Ralph + OpenCode workflow has been demonstrated to work:

### ✅ Verified Components
1. **OpenCode CLI Integration** - `ralph.sh` pipes `prompt.md` to `opencode run`
2. **Tool Usage** - Ralph agents use OpenCode tools (Read, Edit, Write, Bash, Glob, Grep, Task, Skill)
3. **PRD Validation** - `scripts/ralph/validate_prd.py` validates PRD structure
4. **Commands** - 5 Ralph commands created in `.opencode/command/`:
   - `/ralph-validate` - Validate PRD
   - `/ralph-run` - Run Ralph loop
   - `/ralph-status` - Check progress
   - `/ralph-quality` - Run quality gates
   - `/ralph-test-complete` - Test COMPLETE signal
5. **COMPLETE Signal** - Ralph detects `<promise>COMPLETE</promise>` to exit loop
6. **Integration Tests** - Tests use real OpenCode CLI (not mocks)

### 🚀 New: Idiomatic OpenCode Approach (Current)
Ralph has been redesigned for pure OpenCode integration:
- **Subagent Invocation**: Users invoke via `@ralph` (idiomatic OpenCode pattern)
- **Pure OpenCode Tools**: Uses `read`/`write`/`edit`/`todowrite`/`todoread` for all operations
- **jq for JSON Processing**: Replaces Python scripts with `jq` commands
- **No External Dependencies**: Works entirely within OpenCode tool ecosystem
- **Skill-Driven**: Ralph skill guides subagent through iterative development

### 🧪 Test Architecture
- **Unit Tests**: PRD validation (3 passing tests)
- **Integration Tests**: Ralph workflow with real OpenCode (marked `@pytest.mark.integration`)
- **Test Markers**: `pytest.ini` defines `integration` and `slow` markers
- **Quality Gates**: Tests, linting, formatting must pass

### 🔧 Example Usage
```bash
# Manual Ralph loop (alternative to ralph.sh)
./ralph-loop.sh 20 "COMPLETE" "Build a Flask API with tests"

# Run demonstration
python3 demonstrate-ralph-opencode.py

# Test integration
uv run pytest tests/ -m integration -v
```

### 📁 Key Files Demonstrated
- `ralph.sh` - Main Ralph loop using `opencode run`
- `prompt.md` - OpenCode agent instructions
- `ralph-loop.sh` - Example bash implementation
- `demonstrate-ralph-opencode.py` - Full workflow demonstration
- `.opencode/plugin/ralph.js` - Plugin stub for future extension

### 🚀 Next Steps
1. **Polish Commands** - Enhance command functionality
2. **Plugin Development** - Extend to full OpenCode plugin
3. **Skill Creation** - Package as reusable OpenCode skill
4. **Performance Optimization** - Reduce iteration overhead

## Issue Tracking

This project uses **bd (beads)** for issue tracking.
Run `bd prime` for workflow context, or install hooks (`bd hooks install`) for auto-injection.

**Quick reference:**
- `bd ready` - Find unblocked work
- `bd create "Title" --type task --priority 2` - Create issue
- `bd close <id>` - Complete work
- `bd sync` - Sync with git (run at session end)

For full workflow details: `bd prime`

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
