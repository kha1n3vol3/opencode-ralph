# Ralph

![Ralph](ralph.webp)

Ralph is an autonomous AI agent loop that runs [OpenCode](https://opencode.ai) repeatedly until all PRD items are complete. Each iteration is a fresh OpenCode agent with clean context. Memory persists via git history, `progress.txt`, and `prd.json`.

Based on [Geoffrey Huntley's Ralph pattern](https://ghuntley.com/ralph/).

## Architecture: Orchestrator-Worker Pattern

Ralph uses an **orchestrator-worker pattern** with two specialized OpenCode agents:

### Ralph Subagent (`ralph.md`)
- **Mode**: `subagent` (invokable via `@ralph`) with full tool access (including `task` and `skill`)
- **Role**: Loads Ralph skill, validates prerequisites, spawns worker subagents
- **Location**: `.opencode/agent/ralph.md`
- **Behavior**: Implements orchestrator loop with stagnation detection and quality gates using pure OpenCode tools

### Worker Subagent (`ralph-worker.md`)
- **Mode**: `subagent` with `hidden: true` (restricted tools - no `task`)
- **Role**: Implements single user story, reads `prompt.md`, runs quality checks
- **Location**: `.opencode/agent/ralph-worker.md`
- **Behavior**: Returns SUCCESS/FAILURE signal to orchestrator

This architecture provides **clean context isolation** per user story while maintaining persistence via git commits and file updates.

## Idiomatic OpenCode Integration

Ralph now uses **pure OpenCode native tools** for idiomatic integration:

- **Subagent Invocation**: Users invoke Ralph via `@ralph` or `/ralph-run` command
- **Native Tool Usage**: Uses `read`/`write`/`edit`/`todowrite`/`todoread` for all operations
- **jq for JSON Processing**: Uses `jq` commands for PRD querying (replaces Python scripts)
- **No External Dependencies**: Ralph skill works entirely within OpenCode tool ecosystem

## Key Features

- **Autonomous Development Loop**: Runs OpenCode agents until all PRD stories are complete
- **Orchestrator-Worker Pattern**: Clean context isolation with fresh subagents per story
- **Quality Gates**: Automated testing, linting, and formatting checks
- **Progress Tracking**: Append-only `progress.txt` with learnings and patterns
- **PRD-Driven**: JSON-based Product Requirements Document guides development
- **Git Integration**: Automatic commits with story IDs and branch management

## Prerequisites

- [OpenCode CLI](https://opencode.ai) installed and authenticated
- `jq` installed (`brew install jq` on macOS, `apt-get install jq` on Ubuntu)
- A git repository for your project

## Setup

### Prerequisites Verification

First, verify OpenCode CLI and jq are installed:

```bash
# Check OpenCode CLI
opencode --version

# Check jq
jq --version
```

### Installation Steps

1. **Clone Ralph repository or copy files:**
   ```bash
   # Option 1: Clone as subdirectory
   git clone https://github.com/kha1n3vol3/opencode-ralph.git
   cd opencode-ralph
   
   # Option 2: Install via Python script
   python3 -c "from ralph.install import install_ralph_skill; from pathlib import Path; install_ralph_skill(Path('.'))"
   ```

2. **Verify OpenCode agent integration:**
   ```bash
   opencode debug skill | grep -i ralph  # Should show Ralph skill
   ```

3. **Create PRD file:**
   ```bash
   cp prd.json.example prd.json
   # Edit prd.json with your user stories
   ```

4. **Run Ralph to verify setup:**
   ```bash
   # Method 1: Use OpenCode command
   opencode /ralph-run 1
   
   # Method 2: Run orchestrator agent directly
   opencode run --agent ralph --maxSteps 100 1
   ```
   
   Expected behavior:
   - Ralph orchestrator agent loads Ralph skill
   - Validates prerequisites (PRD, progress.txt, core.py)
   - Spawns worker subagent for highest priority story
   - Worker implements the story using `prompt.md` instructions
   - Runs quality gates (tests, linting, formatting)
   - Commits changes with story ID in message
   - Updates `prd.json` with `passes: true` for completed story
   - Outputs `<promise>COMPLETE</promise>` when all stories done

### OpenCode Agent Configuration

Ralph uses two OpenCode agent configurations (already included in the repository):

- **Primary Orchestrator**: `.opencode/agent/ralph.md` - Spawns worker subagents, manages iterations
- **Worker Subagent**: `.opencode/agent/ralph-worker.md` - Implements single user stories (hidden)

The Ralph skill (`.opencode/skill/ralph/SKILL.md`) contains detailed orchestrator instructions.

## Workflow

### 1. Create PRD

Create a `prd.json` file in your project root (use `prd.json.example` as template):

```json
{
  "project": "MyProject",
  "branchName": "ralph/feature-name",
  "description": "Feature description",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add database migration",
      "description": "As a developer, I need to store user preferences",
      "acceptanceCriteria": [
        "Create migration file with timestamp",
        "Add preferences column to users table",
        "Run migration successfully"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### 2. Run Ralph Loop

```bash
# Use OpenCode command (recommended)
opencode /ralph-run [max_iterations]

# Or run orchestrator agent directly
opencode run --agent ralph --maxSteps 100 [max_iterations]
```

Default max iterations: 10. Use `5` for 5 iterations.

### 3. Orchestrator-Worker Execution Flow

1. **Orchestrator Initialization**:
   - Primary agent (`ralph.md`) loads Ralph skill
   - Validates prerequisites (PRD, progress.txt, core modules)
   - Checks if all stories complete → outputs `<promise>COMPLETE</promise>` if done

2. **Main Loop** (while iterations < max_iterations):
   - **Get next story**: Highest priority incomplete story from PRD
   - **Stagnation check**: Skip story after 3 failures
   - **Spawn worker**: Use Task tool to spawn `ralph-worker.md` subagent
   - **Worker execution**: Implements single story using `prompt.md` instructions
   - **Quality gates**: Runs tests, linting, formatting (project-specific)
   - **Result handling**: Worker returns SUCCESS or FAILURE
   - **Update PRD**: Mark story complete on SUCCESS
   - **Progress tracking**: Append learnings to `progress.txt`

3. **Exit Conditions**:
   - **Success**: All stories complete → `<promise>COMPLETE</promise>`
   - **Partial**: Max iterations reached → reports remaining stories
   - **Error**: Critical failure → error message with details

### 4. Quality Gates

Ralph enforces quality checks via the worker agent:

- **Tests**: `uv run pytest tests/ -v` (must pass for Python projects)
- **Linting**: `uv run ruff check . --fix` (auto-fix safe issues)
- **Formatting**: `uv run ruff format .` (ensure consistent style)
- **Type checking**: `uv run ty .` (if project uses type hints)

If quality checks fail, the story is not marked complete.

## Key Files

| File | Purpose |
|------|---------|
| `ralph.sh` | **DEPRECATED** - Legacy bash loop (use OpenCode agents instead) |
| `prompt.md` | Detailed instructions for OpenCode agents (tool usage, quality gates) |
| `prd.json` | Product Requirements Document with user stories and completion status |
| `prd.json.example` | Example PRD format |
| `progress.txt` | Append-only log with learnings and codebase patterns |
| `.opencode/agent/ralph.md` | Primary orchestrator agent (spawns workers) |
| `.opencode/agent/ralph-worker.md` | Hidden worker subagent (implements single stories) |
| `.opencode/skill/ralph/SKILL.md` | Ralph skill with orchestrator instructions |
| `scripts/ralph/core.py` | Core logic for PRD processing and progress tracking |
| `scripts/ralph/validate_prd.py` | PRD validation utility |
| `flowchart/` | Interactive React Flow diagram explaining Ralph workflow |

## Flowchart

[![Ralph Flowchart](ralph-flowchart.png)](https://snarktank.github.io/ralph/)

**[View Interactive Flowchart](https://snarktank.github.io/ralph/)** - Click through to see each step with animations.

The `flowchart/` directory contains the source code. To run locally:

```bash
cd flowchart
npm install
npm run dev
```

## Critical Concepts

### Orchestrator-Worker Pattern

Ralph uses an **orchestrator-worker pattern** with clean context isolation:

- **Primary Orchestrator**: Manages the loop, spawns workers, tracks progress
- **Worker Subagents**: Fresh context per story implementation (hidden subagents)
- **Context Isolation**: Each worker gets clean context via OpenCode Task tool
- **Persistence**: Memory via git commits, PRD updates, and progress.txt

This pattern prevents context pollution and allows each story to be implemented independently.

### Small, Focused Stories

Each PRD item should be small enough to complete in one context window (2-3 sentences to describe). Oversized stories cause poor results.

**Right-sized stories:**
- Add a database column and migration
- Create a new API endpoint with tests
- Add a UI component to existing page
- Update validation logic with error handling

**Too big (split these):**
- "Build the entire dashboard"
- "Add authentication system"
- "Refactor the entire API layer"

### AGENTS.md Updates Are Critical

After each iteration, Ralph updates relevant `AGENTS.md` files with learnings. OpenCode agents automatically read these files, so future iterations benefit from discovered patterns.

**Examples of what to add to AGENTS.md:**
- Patterns discovered ("this codebase uses X for Y")
- Gotchas ("do not forget to update Z when changing W")
- Useful context ("the settings panel is in component X")
- API conventions ("endpoints follow pattern /api/v1/resource")

### Quality Gates as Feedback Loops

Ralph requires robust feedback loops:
- **Tests must pass**: Automated test suite catches regressions
- **Linting and formatting**: Consistent code style across iterations
- **Type checking**: Catches type errors before they compound
- **CI must stay green**: Broken code blocks future iterations

### Stop Condition Detection

When all stories have `passes: true`, the orchestrator outputs `<promise>COMPLETE</promise>` and exits. The COMPLETE signal indicates successful completion of all user stories.

## Debugging

Check current state:

```bash
# See which stories are done
cat prd.json | jq '.userStories[] | {id, title, passes}'

# See learnings from previous iterations
cat progress.txt

# Check git history
git log --oneline -10
```

## Customizing prompt.md

Edit `prompt.md` to customize Ralph's behavior for your project:
- Add project-specific quality check commands
- Include codebase conventions
- Add common gotchas for your stack

## Archiving

Ralph automatically archives previous runs when you start a new feature (different `branchName`). Archives are saved to `archive/YYYY-MM-DD-feature-name/`.

## References

- [Geoffrey Huntley's Ralph article](https://ghuntley.com/ralph/)
- [OpenCode documentation](https://opencode.ai)
- [Ralph OpenCode port repository](https://github.com/kha1n3vol3/opencode-ralph)
