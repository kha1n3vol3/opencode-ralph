To configure an invokable "Ralph" skill in the OpenCode platform—mimicking the autonomous AI development loop from the Ralph-Claude-Code project (which builds on Claude's code interpreter for iterative, self-improving code development with safeguards)—you can leverage OpenCode's native skills system. This involves defining a reusable behavior via a `SKILL.md` file that instructs an agent to run an iterative loop: processing project requirements (e.g., from a PROMPT.md equivalent), using tools for code execution/editing, analyzing outputs, and detecting completion or errors to exit gracefully. The skill can be invoked on-demand using the built-in `skill` tool, allowing agents to load and follow its instructions dynamically.

OpenCode doesn't have a direct built-in autonomous loop like Ralph's CLI script, but its tools (e.g., `bash` for execution, `write`/`edit`/`read` for file manipulation, `todowrite`/`todoread` for task tracking) and agent modes enable similar usability. The skill can guide the agent to chain these tools in a loop-like fashion, with semantic analysis for exit conditions (e.g., detecting "done" signals or stagnation). Permissions ensure safe, controlled execution, preventing infinite loops via approval prompts or timeouts.

Here's a step-by-step guide to configuring this, based on OpenCode's native features for skills, tools, agents, and permissions. This approximates Ralph's key aspects: autonomous iteration, intelligent exit detection, session continuity, and rate limiting.

### Step 1: Set Up the Skill Directory and `SKILL.md` File
Skills are discovered automatically from specific directories. Choose a location:
- Project-local: Create a folder like `.opencode/skill/ralph-loop/` (recommended for per-project use).
- Global: Use `~/.config/opencode/skill/ralph-loop/` for reuse across projects.

Inside the folder, create `SKILL.md` (exact capitalization required) with YAML frontmatter for metadata, followed by instructional content. The file body describes the skill's behavior, which the agent will follow when invoked—emphasizing an autonomous loop similar to Ralph's.

Example `SKILL.md` content for a Ralph-like autonomous development loop skill:
```
---
name: ralph-loop
description: Implements an autonomous AI development loop for iterative code improvement, with intelligent exit detection and safeguards, similar to Ralph for Claude Code.
license: MIT
compatibility: opencode
metadata:
  tools: bash, write, edit, read, todowrite, todoread
---

## What I Do
I act as an autonomous development agent:
- Read project requirements from a starting file (e.g., PROMPT.md or @fix_plan.md).
- Iteratively execute code tasks: Write/edit files, run via bash (e.g., tests or builds), analyze outputs/errors.
- Track progress with a todo list (using todowrite/todoread for session continuity).
- Detect completion: Look for "done" signals, successful tests, or no further changes needed.
- Implement safeguards: Limit iterations (e.g., max 10 loops), detect stagnation (e.g., repeated errors), and prompt for approval on risky actions.
- Preserve state across invocations via todo files or session context.

## When to Use Me
Invoke me for:
- Autonomous project development from requirements.
- Iterative debugging/fixing until tests pass.
- If no starting file is specified, assume PROMPT.md in the project root.
- Always start by reading the prompt, planning steps, then looping: act → analyze → refine.
- Exit early if complete, errors persist (e.g., 3 consecutive failures), or user interrupts.

## How to Execute the Loop
1. **Initialize**: Use 'read' to load PROMPT.md or @fix_plan.md. Create a todo list with 'todowrite' (e.g., tasks like "Implement feature X", "Run tests").
2. **Iterate (Loop Logic)**:
   - Pick next task from todo (todoread).
   - Use 'write'/'edit' to modify code files.
   - Execute with 'bash' (e.g., 'python tests.py' or 'git commit').
   - Capture output/errors.
   - Analyze semantically: If success (e.g., tests pass), mark done in todo. If error, suggest fix and retry.
   - Update todo with 'todowrite' for next iteration.
3. **Exit Detection**:
   - Complete: All todos done or "done" in output.
   - Stagnation: 3+ consecutive similar errors (compare outputs).
   - Limits: Max 10 iterations; prompt user if exceeded.
   - On exit, summarize progress and clean up (e.g., commit changes via bash).
4. **Safeguards**: Use 'ask' permissions for bash/write. Simulate rate limiting by pausing (e.g., via bash sleep if needed).
```

This setup mirrors Ralph's autonomous loop by guiding the agent through iterative tool use, with built-in analysis for exits, akin to Ralph's response analyzer and circuit breaker.

### Step 2: Configure Permissions for Safe Invocation
To prevent runaway loops (like Ralph's rate limiting and circuit breaker), edit your `opencode.json` (or `opencode.jsonc`) file in the project root or global config. Use pattern-based rules to control the `skill` tool and loop-related tools.

Example configuration snippet:
```
{
  "$schema": "https://opencode.ai/config.json",
  "tools": {
    "bash": "ask",    // Require approval for executions to avoid unsafe loops
    "write": "ask",   // Approval for file changes
    "edit": "allow",  // Allow edits for iterations
    "read": "allow",  // Allow reading prompts/outputs
    "todowrite": "allow", // For task tracking
    "todoread": "allow"
  },
  "skill": {
    "ralph-loop": "allow", // Auto-load this specific skill
    "autonomous-*": "ask", // Prompt for similar loop skills
    "*": "allow"           // Default for others
  }
}
```

- `"allow"`: The skill loads and runs automatically.
- `"ask"`: Prompts the user for approval before key actions (e.g., each bash call), simulating Ralph's safeguards.
- `"deny"`: Blocks if needed.
- Wildcards (e.g., `loop-*`) can group related skills.
- For timeouts, add agent-level configs (e.g., max iterations via model params if supported).

This provides granular control, ensuring loops don't overuse resources, unlike Claude's more implicit safeguards.

### Step 3: Integrate with Agents for Invocation
Assign the skill to an agent for contextual use. Agents (e.g., the built-in `build` or a custom one) can invoke skills via the `skill` tool and maintain session state.

- **Using a Built-in Agent**: The `build` agent has full tool access by default, making it ideal for development loops. Invoke the skill by mentioning it in a prompt (e.g., "Use the ralph-loop skill to autonomously develop this project from PROMPT.md").

- **Custom Agent Configuration**: Create a dedicated agent for autonomous loops. Use a Markdown file in `.opencode/agent/` (e.g., `ralph-agent.md`):
  ```
  ---
  description: Agent for Ralph-like autonomous development loops
  mode: subagent
  tools: { bash: true, write: true, edit: true, read: true, todowrite: true, todoread: true }
  skill: { "ralph-loop": "allow", "*": "allow" }
  model: anthropic/claude-3-5-sonnet-20241022  // Or your preferred model for analysis
  prompt: You are an autonomous development agent. Always use the ralph-loop skill for iterative tasks. Maintain session continuity via todo files.
  ---
  Follow loop principles: iterate safely, detect exits semantically, and prioritize tasks from @fix_plan.md.
  ```

  - Invoke this agent with `@ralph-agent` in the TUI, then trigger the skill.

Agents can override global permissions, ensuring the Ralph skill is only usable in controlled contexts. For session continuity (like Ralph's .ralph_session), rely on persistent todo files or agent context.

### Step 4: Invoke and Use the Skill
- In the OpenCode TUI, agents discover skills automatically via the `skill` tool, which lists them in XML format (e.g., `<skill><name>ralph-loop</name><description>...</description></skill>`).
- Invoke explicitly: The agent calls `skill({ name: "ralph-loop" })` in its workflow, loading the `SKILL.md` content.
- Example interaction:
  1. Prepare a PROMPT.md with requirements (e.g., "Build a Python app that...").
  2. Prompt the agent: "Start autonomous development using ralph-loop on this project."
  3. Agent loads the skill instructions.
  4. Reads PROMPT.md, creates todo (e.g., "Write main.py", "Run tests").
  5. Loops: Writes code → Executes bash → Analyzes → Updates todo.
  6. Exits on completion (e.g., "All tasks done") or limits, summarizing results.

This creates an iterative loop similar to Ralph's, where the agent self-improves code until done.

### Key Differences and Enhancements Compared to Ralph for Claude Code
- **Similarities**: Both enable autonomous loops with tool chaining (e.g., write/execute/analyze), exit detection (semantic analysis of outputs), and safeguards (limits/approvals). OpenCode's approach is instruction-based via skills, while Ralph is a CLI script.
- **Differences**: Ralph uses Claude Code's JSON outputs for parsing and has built-in tmux monitoring; OpenCode relies on agent prompts and tools for similar logic, without native JSON enforcement (but you can instruct the model to output structured responses).
- **Enhancements**: Integrate OpenCode's commands (e.g., for CI/CD-like testing) or extend the skill with PRD import logic (e.g., convert docs via bash). For better monitoring, use agent logging or external tools. Test in a sample project to refine the `SKILL.md` based on loop performance.

If your setup needs Ralph's exact CLI features (e.g., import or monitor), you could wrap them in a custom OpenCode command, but the native skill approach provides equivalent invokable usability.
