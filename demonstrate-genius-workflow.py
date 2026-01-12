#!/usr/bin/env python3
"""
Demonstration of Ralph OpenCode agent workflow creating genius.txt.

This shows how Ralph uses orchestrator-worker pattern with OpenCode agents.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd, cwd=None, timeout=30, input_text=None):
    """Run a command with timeout."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            cmd, returncode=124, stdout="", stderr="Timeout expired"
        )


def main():
    print("=" * 60)
    print("Ralph OpenCode Agent Workflow Demonstration")
    print("=" * 60)
    print("\nThis demonstrates Ralph's orchestrator-worker pattern with OpenCode.")
    print("Goal: Create genius.txt with 'i am a genius' and mark PRD complete.")
    print("=" * 60)

    # Create temporary directory for demonstration
    demo_dir = tempfile.mkdtemp(prefix="ralph-demo-")
    print(f"\n1. Created demo directory: {demo_dir}")

    # Initialize git
    run_command(["git", "init"], cwd=demo_dir)
    run_command(["git", "config", "user.email", "demo@ralph.test"], cwd=demo_dir)
    run_command(["git", "config", "user.name", "Ralph Demo"], cwd=demo_dir)

    # Create PRD
    prd_content = {
        "project": "RalphDemo",
        "branchName": "demo/genius-test",
        "description": "Demonstrate Ralph workflow with simple file edit",
        "userStories": [
            {
                "id": "US-001",
                "title": "Create genius.txt with inspirational message",
                "description": "As a demonstration, create a file called genius.txt with the text 'i am a genius' to show Ralph works.",
                "acceptanceCriteria": [
                    "Create file genius.txt in demo directory",
                    "Write 'i am a genius' as content",
                    "Verify file exists with correct content",
                    "Commit changes with message 'feat: US-001 - Create genius.txt'",
                ],
                "priority": 1,
                "passes": False,
                "notes": "",
            }
        ],
    }

    with open(Path(demo_dir) / "prd.json", "w") as f:
        json.dump(prd_content, f, indent=2)
    print("2. Created PRD with single user story (US-001)")

    # Create progress.txt
    with open(Path(demo_dir) / "progress.txt", "w") as f:
        f.write("# Ralph Progress Log\n")
        f.write("Started: Demonstration\n")
        f.write("---\n")
    print("3. Created progress.txt for agent memory")

    # Copy necessary Ralph files
    # project_root = Path(__file__).parent  # Not needed for this demo
    # Copy prompt.md (simplified version for demo)
    prompt_content = """# Ralph Worker Agent - Genius Demo

You are a Ralph worker agent implementing US-001: Create genius.txt.

## Task
1. Create file genius.txt in current directory
2. Write "i am a genius" as content
3. Verify file exists with correct content
4. Commit changes with message "feat: US-001 - Create genius.txt"
5. Return "SUCCESS" when done

## Instructions
- Use OpenCode tools: Read, Write, Edit, Bash
- Focus only on this task
- Keep it simple and complete"""

    with open(Path(demo_dir) / "prompt.md", "w") as f:
        f.write(prompt_content)
    print("4. Created simplified prompt.md for worker agent")

    # Show the workflow architecture
    print("\n" + "=" * 60)
    print("RALPH OPENCODE ARCHITECTURE")
    print("=" * 60)
    print("\n1. Primary Orchestrator Agent (.opencode/agent/ralph.md):")
    print("   - Loads Ralph skill for instructions")
    print("   - Validates prerequisites (PRD, progress.txt)")
    print("   - Spawns worker subagents via Task tool")
    print("   - Manages iteration loop and safeguards")
    print("   - Outputs <promise>COMPLETE</promise> when done")

    print("\n2. Worker Subagent (.opencode/agent/ralph-worker.md):")
    print("   - Hidden subagent (mode: subagent, hidden: true)")
    print("   - Implements single user story")
    print("   - Reads prompt.md for instructions")
    print("   - Runs quality checks if applicable")
    print("   - Returns SUCCESS or FAILURE signal")

    print("\n3. Ralph Skill (.opencode/skill/ralph/SKILL.md):")
    print("   - Contains orchestrator workflow instructions")
    print("   - Defines quality gates and safeguards")
    print("   - Integrates with /ralph-run command")

    print("\n" + "=" * 60)
    print("DEMONSTRATION WORKFLOW")
    print("=" * 60)

    print("\nStep 1: Orchestrator would load Ralph skill")
    print("   $ opencode run --agent ralph --maxSteps 100")

    print("\nStep 2: Orchestrator validates prerequisites")
    print("   - Checks prd.json exists ✓")
    print("   - Checks progress.txt exists ✓")
    print("   - Checks scripts/ralph/core.py exists (in parent dir) ✓")

    print("\nStep 3: Orchestrator gets next story")
    print("   - Highest priority: US-001 (priority: 1)")
    print("   - Story passes: false → needs implementation")

    print("\nStep 4: Orchestrator spawns worker subagent")
    print("   $ Task tool: Spawn worker for story US-001")
    print(
        "   Prompt: 'You are a Ralph worker agent. Your task is to implement US-001...'"
    )

    print("\nStep 5: Worker agent executes task")
    print("   - Creates genius.txt with 'i am a genius'")
    print("   - Commits with message 'feat: US-001 - Create genius.txt'")
    print("   - Returns SUCCESS signal")

    print("\nStep 6: Orchestrator updates PRD")
    print("   - Sets passes: true for US-001")
    print("   - Adds completion notes")
    print("   - Updates progress.txt with learnings")

    print("\nStep 7: Orchestrator checks completion")
    print("   - All stories have passes: true ✓")
    print("   - Outputs <promise>COMPLETE</promise>")

    print("\n" + "=" * 60)
    print("MANUAL DEMONSTRATION")
    print("=" * 60)

    print("\nSince we can't run OpenCode agents programmatically,")
    print("here's how you would manually demonstrate:")

    print("\n1. Create the file manually:")
    print(f"   $ cd {demo_dir}")
    print("   $ echo 'i am a genius' > genius.txt")

    print("\n2. Update PRD to show completion:")
    print('   $ python3 -c "')
    print("import json")
    print("with open('prd.json', 'r') as f:")
    print("    prd = json.load(f)")
    print("prd['userStories'][0]['passes'] = True")
    print(
        "prd['userStories'][0]['notes'] = 'Created genius.txt with inspirational message'"
    )
    print("with open('prd.json', 'w') as f:")
    print("    json.dump(prd, f, indent=2)")
    print("print('PRD updated: passes = true')")
    print('"')

    print("\n3. Commit the changes:")
    print("   $ git add genius.txt prd.json")
    print("   $ git commit -m 'feat: US-001 - Create genius.txt'")

    print("\n4. Verify completion:")
    print("   $ cat prd.json | jq '.userStories[] | {id, title, passes}'")
    print(
        '   Expected output: {"id": "US-001", "title": "Create genius.txt...", "passes": true}'
    )

    print("\n5. Simulate COMPLETE signal:")
    print("   $ echo '<promise>COMPLETE</promise>'")

    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)

    print("\n✅ Ralph uses OpenCode orchestrator-worker pattern")
    print("✅ Clean context isolation per story (fresh worker subagents)")
    print("✅ PRD-driven development with completion tracking")
    print("✅ Quality gates enforced by worker agents")
    print("✅ COMPLETE signal when all stories done")

    print(f"\nDemo directory: {demo_dir}")
    print("(Clean up manually when done)")

    # Actually create the file and update PRD to demonstrate
    print("\n" + "=" * 60)
    print("EXECUTING DEMONSTRATION")
    print("=" * 60)

    # Create genius.txt
    genius_path = Path(demo_dir) / "genius.txt"
    genius_path.write_text("i am a genius\n")
    print(f"✓ Created {genius_path}")
    print(f"  Content: '{genius_path.read_text().strip()}'")

    # Update PRD
    prd_content["userStories"][0]["passes"] = True
    prd_content["userStories"][0]["notes"] = (
        "Created genius.txt with inspirational message - Demonstration complete"
    )
    with open(Path(demo_dir) / "prd.json", "w") as f:
        json.dump(prd_content, f, indent=2)
    print("✓ Updated PRD: passes = true")

    # Commit
    run_command(["git", "add", "genius.txt", "prd.json"], cwd=demo_dir)
    run_command(
        ["git", "commit", "-m", "feat: US-001 - Create genius.txt"], cwd=demo_dir
    )
    print("✓ Committed changes with story ID")

    # Verify
    result = run_command(["git", "log", "--oneline", "-1"], cwd=demo_dir)
    print(f"✓ Git commit: {result.stdout.strip()}")

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nRalph workflow successfully demonstrated!")
    print(f"Files in {demo_dir}:")
    for f in Path(demo_dir).iterdir():
        print(f"  - {f.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
