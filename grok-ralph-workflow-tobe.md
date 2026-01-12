### Overview of the Ralph Loop Workflow in OpenCode

The "Ralph" skill in OpenCode emulates the autonomous development loop from the Ralph-Claude-Code project, where an AI iteratively refines code based on requirements until completion or an exit condition is met. It's laid out as a modular, instruction-driven system using OpenCode's skills, tools, agents, and permissions. This allows for safe, invokable loops that chain actions like reading prompts, editing code, executing tests, analyzing results, and tracking progress.

The workflow is designed to be **iterative and self-contained**: It starts with invocation, enters a loop of action-analysis-refinement, and exits intelligently (e.g., on success, stagnation, or limits). This makes it useful for tasks like autonomous debugging, feature implementation, or project bootstrapping, where manual intervention is minimized but approvals ensure safety.

Below, I'll break down the workflow into its layout (structural components) and invocation (runtime process). I'll use a step-by-step explanation, followed by a simplified flowchart for clarity.

### Layout: Structural Components
The setup is file-based and configurable, ensuring the loop is reusable and customizable. All components are native to OpenCode and discovered automatically.

1. **Skill Definition (Core Logic)**:
   - **Location**: A dedicated directory (e.g., `.opencode/skill/ralph-loop/` in your project or globally in `~/.config/opencode/`).
   - **Key File**: `SKILL.md` – This is the "brain" of the loop. It contains:
     - YAML frontmatter (metadata like name, description, required tools).
     - Instructional body: Describes the loop's behavior, including initialization, iteration steps, exit conditions, and safeguards.
   - **Purpose**: When invoked, the agent loads this file and follows its instructions as a behavioral guide. This mirrors Ralph's scripted loop but is more flexible (e.g., you can tweak instructions for specific languages or domains like web dev vs. data science).
   - **Customization Tip**: For useful loops, add domain-specific logic (e.g., "Prioritize unit tests with pytest" or "Handle web APIs safely").

2. **Permissions Configuration (Safety Layer)**:
   - **Location**: `opencode.json` (or `.jsonc`) in the project root or global config.
   - **Key Elements**: Define tool access (e.g., `"bash": "ask"`) and skill permissions (e.g., `"ralph-loop": "allow"`).
   - **Purpose**: Prevents infinite or harmful loops by requiring user approval for actions like code execution or file writes. This acts as a "circuit breaker" similar to Ralph's rate limiting.
   - **Usefulness**: Set `"ask"` for production loops to catch issues early; use `"allow"` for trusted testing.

3. **Agent Integration (Execution Context)**:
   - **Location**: `.opencode/agent/` directory for custom agents (e.g., `ralph-agent.md`).
   - **Key File**: Agent Markdown file with YAML frontmatter (e.g., tools enabled, model, prompt) and body (additional instructions).
   - **Purpose**: Agents provide the runtime environment for the skill. A dedicated agent ensures session state (e.g., via todo files) and tool access tailored to loops.
   - **Built-in Option**: Use the default `build` agent for quick starts, but custom agents make loops more robust (e.g., specifying a strong model like Claude for analysis).

4. **Supporting Files and Tools**:
   - **Prompt Files**: E.g., `PROMPT.md` or `@fix_plan.md` – These hold initial requirements (like Ralph's input prompt).
   - **Tools Used in Loop**: Native OpenCode tools like `read` (load prompts), `write/edit` (modify code), `bash` (execute/test), `todowrite/todoread` (track tasks for state persistence).
   - **State Management**: Todo files act as a simple database for loop continuity, avoiding loss of progress if interrupted.

This layout keeps everything modular: Update `SKILL.md` to evolve the loop without redeploying.

### Invocation: Runtime Process
Invocation happens in the OpenCode TUI (Terminal User Interface) or via commands/agents. Once started, the workflow enters an autonomous loop until exit. Here's how it's triggered and runs:

1. **Preparation**:
   - Ensure setup is complete (skill directory, permissions, agent file).
   - Create a starting prompt file (e.g., `PROMPT.md` with "Implement a Python CLI for task X, including tests").

2. **Triggering the Loop**:
   - **Via Prompt**: In the TUI, address an agent (e.g., "@ralph-agent Use the ralph-loop skill to develop from PROMPT.md").
   - **Automatic Discovery**: The agent uses the `skill` tool to list and load `ralph-loop` (output as XML: `<skill><name>ralph-loop</name>...</skill>`).
   - **Explicit Call**: The agent invokes `skill({ name: "ralph-loop" })`, loading `SKILL.md` instructions into its context.

3. **Loop Execution**:
   - **Initialization**: Agent reads the prompt (via `read`), plans steps, and initializes a todo list (via `todowrite`, e.g., tasks: "Write code", "Run tests").
   - **Iteration Cycle** (Repeated until exit):
     - **Act**: Select next task (from `todoread`), modify files ( `write/edit` ), execute ( `bash`, e.g., "pytest" ).
     - **Analyze**: Capture output/errors, semantically evaluate (e.g., "Tests passed? Errors repeated?").
     - **Refine**: Update code or todo based on analysis; if risky, prompt for approval.
   - **State Handling**: Todo files preserve progress; agent context maintains short-term memory.
   - **Safeguards in Action**: Permissions trigger "ask" prompts (e.g., "Approve this bash command?"); built-in limits (e.g., max 10 iterations) prevent overuse.

4. **Exit and Cleanup**:
   - **Conditions**: Success (all todos done, "done" signal), stagnation (repeated errors), limits reached, or user interrupt.
   - **Post-Exit**: Summarize results (e.g., "Project complete: Code in main.py, tests passed"), clean up (e.g., commit via `bash: git commit`), and suggest next steps.
   - **Output**: Agent reports back in TUI, with logs for review.

For usefulness, start small: Test on a simple task (e.g., "Fix this buggy function") to tune iterations. Monitor via TUI for the first few runs.

### Simplified Flowchart of the Workflow
Here's a table-based representation of the workflow as a flowchart for visual clarity:

| Stage | Component Involved | Actions | Transitions/Conditions |
|-------|--------------------|---------|------------------------|
| **Setup (Layout)** | Skill Directory, `SKILL.md`, `opencode.json`, Agent File | Define instructions, set permissions, configure agent | Complete setup → Ready for invocation |
| **Invocation** | TUI/Agent Prompt | Address agent, mention skill (e.g., "@ralph-agent start ralph-loop") | Loads `SKILL.md` → Enter loop |
| **Initialization** | Tools: `read`, `todowrite` | Load prompt, create todo list | Setup done → First iteration |
| **Iteration Loop** | Tools: `todoread`, `write/edit`, `bash` | Act (modify/execute), Analyze (evaluate output), Refine (update todo) | More tasks? No stagnation/limits? → Next iteration<br>Else → Exit |
| **Exit** | Skill Instructions | Detect conditions, summarize, clean up | Loop ends → Final response in TUI |

This workflow ensures Ralph-like autonomy while leveraging OpenCode's ecosystem for flexibility and safety. If issues arise (e.g., loop stalls), refine `SKILL.md` with more explicit analysis prompts.
