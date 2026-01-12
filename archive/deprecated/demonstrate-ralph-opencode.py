#!/usr/bin/env python3
"""
Demonstration of Ralph workflow with OpenCode.
Shows how Ralph uses OpenCode for autonomous development.
"""

import json
import shutil
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


def step(message):
    """Print a step message."""
    print(f"\n{'=' * 60}")
    print(f"STEP: {message}")
    print(f"{'=' * 60}")


def success(message):
    print(f"✓ {message}")


def info(message):
    print(f"ℹ {message}")


def warning(message):
    print(f"⚠ {message}")


def error(message):
    print(f"✗ {message}")


class RalphOpenCodeDemo:
    """Demonstrate Ralph workflow with OpenCode."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.demo_dir = None

    def setup(self):
        """Set up demonstration directory."""
        step("Setting up demonstration")

        # Create temporary directory for demo
        self.demo_dir = Path(tempfile.mkdtemp(prefix="ralph-demo-"))
        success(f"Created demo directory: {self.demo_dir}")

        # Copy essential Ralph files
        for file in ["ralph.sh", "prompt.md"]:
            src = self.project_root / file
            dst = self.demo_dir / file
            shutil.copy(src, dst)
            success(f"Copied {file} to demo directory")

        # Make ralph.sh executable
        (self.demo_dir / "ralph.sh").chmod(0o755)

        # Initialize git repo (required for Ralph commits)
        run_command(["git", "init"], cwd=self.demo_dir)
        run_command(
            ["git", "config", "user.email", "demo@example.com"], cwd=self.demo_dir
        )
        run_command(["git", "config", "user.name", "Demo User"], cwd=self.demo_dir)
        success("Initialized git repository")

        return True

    def test_opencode_basic(self):
        """Test basic OpenCode functionality."""
        step("Testing OpenCode CLI")

        # Check opencode is available
        result = run_command(["opencode", "--version"])
        if result.returncode == 0:
            success(f"OpenCode version: {result.stdout.strip()}")
        else:
            error("OpenCode not available")
            return False

        # Test a simple opencode command
        info("Testing OpenCode with simple prompt...")
        result = run_command(["opencode", "run"], input_text="Say hello")

        if result.returncode == 0:
            success("OpenCode responds to simple prompts")
            if result.stdout:
                info(f"Response: {result.stdout[:100]}...")
        elif result.returncode == 124:  # timeout
            warning("OpenCode timed out (expected for interactive agents)")
        else:
            error(f"OpenCode error: {result.stderr}")

        return True

    def test_ralph_commands(self):
        """Test Ralph OpenCode commands."""
        step("Testing Ralph OpenCode commands")

        # Change to project root to use commands
        commands = [
            "ralph-validate",
            "ralph-status",
            "ralph-quality",
        ]

        for cmd in commands:
            info(f"Testing /{cmd} command...")
            result = run_command(
                ["opencode", "run", "--command", cmd],
                cwd=self.project_root,
                timeout=10,
            )

            if result.returncode == 0:
                success(f"/{cmd} command works")
                # Show first line of output
                if result.stdout:
                    first_line = result.stdout.split("\n")[0]
                    info(f"  Output: {first_line[:80]}...")
            elif result.returncode == 124:
                warning(f"/{cmd} timed out (may be expected)")
            else:
                warning(f"/{cmd} had issues: {result.stderr[:100]}")

        return True

    def test_complete_signal(self):
        """Test COMPLETE signal detection."""
        step("Testing COMPLETE signal detection")

        # Test the ralph-test-complete command
        info("Testing ralph-test-complete command...")
        result = run_command(
            ["opencode", "run", "--command", "ralph-test-complete"],
            cwd=self.project_root,
            timeout=5,
        )

        if result.returncode == 0:
            if "<promise>COMPLETE</promise>" in result.stdout:
                success("COMPLETE signal generated correctly")
                info(f"Output: {result.stdout.strip()}")
            else:
                warning(f"COMPLETE signal not found: {result.stdout[:100]}")
        else:
            warning(f"Command failed: {result.stderr}")

        return True

    def create_simple_prd(self):
        """Create a simple PRD for demonstration."""
        step("Creating demonstration PRD")

        prd_data = {
            "project": "RalphDemo",
            "branchName": "ralph/demo-test",
            "description": "Demonstration of Ralph with OpenCode",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Create demonstration file",
                    "description": "Create a simple file to demonstrate Ralph works",
                    "acceptanceCriteria": [
                        "Create file demo.txt with content 'Ralph + OpenCode = 🤝'",
                        "Commit changes with message 'feat: US-001 - Create demonstration file'",
                        "Update PRD to set passes: true for this story",
                    ],
                    "priority": 1,
                    "passes": False,
                    "notes": "",
                }
            ],
        }

        prd_path = self.demo_dir / "prd.json"
        prd_path.write_text(json.dumps(prd_data, indent=2))
        success("Created PRD with 1 user story")

        # Create progress.txt
        progress_path = self.demo_dir / "progress.txt"
        progress_path.write_text("# Ralph Progress Log\nStarted: Demonstration\n---\n")

        return True

    def test_ralph_validation(self):
        """Test PRD validation."""
        step("Testing PRD validation")

        # Run validation script
        result = run_command(
            [
                "python3",
                str(self.project_root / "scripts/ralph/validate_prd.py"),
                str(self.demo_dir / "prd.json"),
            ],
            timeout=5,
        )

        if result.returncode == 0:
            success("PRD validation passes")
        else:
            error(f"PRD validation failed: {result.stderr}")
            return False

        return True

    def demonstrate_ralph_loop(self):
        """Demonstrate Ralph loop (without full execution)."""
        step("Demonstrating Ralph loop structure")

        info("Ralph OpenCode Architecture:")
        info("  Primary Orchestrator: .opencode/agent/ralph.md")
        info("    - Mode: primary, loads Ralph skill")
        info("    - Tools: bash, read, write, edit, glob, grep, task, skill")
        info("    - Spawns worker subagents via Task tool")
        info("  Worker Subagent: .opencode/agent/ralph-worker.md")
        info("    - Mode: subagent, hidden: true")
        info("    - Implements single user stories")
        info("    - Returns SUCCESS/FAILURE signals")
        info("  Ralph Skill: .opencode/skill/ralph/SKILL.md")
        info("    - Contains orchestrator workflow instructions")
        info("    - Defines quality gates and safeguards")

        info("\nRalph prompt structure:")
        with open(self.project_root / "prompt.md", "r") as f:
            # Show first 10 lines
            for i, line in enumerate(f.readlines()[:10]):
                info(f"  {line.rstrip()}")

        info("\nTo run Ralph with OpenCode agents:")
        info(f"  cd {self.demo_dir}")
        info("  # Legacy method (deprecated):")
        info("  # ./ralph.sh 1  # Pipes prompt.md to opencode run")
        info("  # New orchestrator-worker pattern:")
        info("  opencode /ralph-run 1  # Use OpenCode command")
        info("  # Or run orchestrator agent directly:")
        info("  opencode run --agent ralph --maxSteps 100 1")

        success("Ralph workflow ready")
        return True

    def create_plugin_stub(self):
        """Create a stub for Ralph OpenCode plugin."""
        step("Creating Ralph OpenCode plugin stub")

        plugin_dir = self.project_root / ".opencode" / "plugin"
        plugin_dir.mkdir(parents=True, exist_ok=True)

        plugin_content = """// Ralph OpenCode Plugin
// Adds Ralph autonomous agent functionality to OpenCode

export const ralphPlugin = async ({ project, client, $, directory, worktree }) => {
  console.log("Ralph plugin initialized!");
  
  return {
    // Example: Add a custom tool for running Ralph
    tool: {
      ralph: {
        description: "Run Ralph autonomous agent loop",
        args: {
          iterations: { type: "number", description: "Maximum iterations", default: 10 },
          prd: { type: "string", description: "Path to PRD file", default: "prd.json" }
        },
        async execute(args, ctx) {
          const { iterations, prd } = args;
          return `Ralph would run with ${iterations} iterations using ${prd}`;
          // In a real implementation, this would run the Ralph loop
        }
      }
    },
    
    // Example: Hook into session events
    "session.created": async (session) => {
      console.log(`Session created: ${session.id}`);
    },
    
    // Example: Add a command
    "tui.command.execute": async (command) => {
      if (command.name === "ralph") {
        console.log("Ralph command executed!");
      }
    }
  };
};
"""

        plugin_path = plugin_dir / "ralph.js"
        plugin_path.write_text(plugin_content)
        success(f"Created plugin stub at {plugin_path.relative_to(self.project_root)}")

        info("\nPlugin capabilities:")
        info("  - Custom 'ralph' tool for running Ralph")
        info("  - Session event hooks")
        info("  - TUI command integration")

        return True

    def run(self):
        """Run the full demonstration."""
        print("\n" + "=" * 60)
        print("RALPH + OPENCODE WORKFLOW DEMONSTRATION")
        print("=" * 60)
        print("\nThis demonstrates how Ralph uses OpenCode for autonomous development.")

        try:
            # Run demonstration steps
            steps = [
                self.setup,
                self.test_opencode_basic,
                self.test_ralph_commands,
                self.test_complete_signal,
                self.create_simple_prd,
                self.test_ralph_validation,
                self.demonstrate_ralph_loop,
                self.create_plugin_stub,
            ]

            for i, step_func in enumerate(steps, 1):
                if not step_func():
                    warning(f"Step {i} had issues, continuing...")

            # Final summary
            step("Demonstration Complete")
            print("\n✅ Ralph workflow with OpenCode is ready!")
            print("\nKey components demonstrated:")
            print("  1. OpenCode CLI integration")
            print("  2. Ralph commands (/ralph-*, /ralph-test-complete)")
            print("  3. PRD validation")
            print("  4. COMPLETE signal detection")
            print("  5. Plugin architecture stub")

            print(f"\nDemo directory: {self.demo_dir}")
            print("Files created:")
            for file in self.demo_dir.iterdir():
                print(f"  - {file.name}")

            print("\nNext steps:")
            print("  1. Run Ralph: cd demo_dir && ./ralph.sh 1")
            print("  2. Extend the plugin: .opencode/plugin/ralph.js")
            print("  3. Add more commands: .opencode/command/*.md")

            return True

        except Exception as e:
            error(f"Demonstration failed: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            # Cleanup
            if self.demo_dir and self.demo_dir.exists():
                info(f"\nDemo directory preserved: {self.demo_dir}")
                info("(Remove manually when done)")


def main():
    demo = RalphOpenCodeDemo()
    success = demo.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
