#!/usr/bin/env python3
"""
Ralph skill installation module.
Copies Ralph files to target project for use with OpenCode.
"""

import shutil
from pathlib import Path


def install_ralph_skill(target_dir: Path) -> bool:
    """
    Install Ralph skill files to target project directory.

    Args:
        target_dir: Path to target project directory

    Returns:
        True if installation successful, False otherwise
    """
    try:
        # Get the source directory (this project)
        source_dir = Path(__file__).parent.parent.parent

        # Create necessary directories in target
        target_scripts_dir = target_dir / "scripts" / "ralph"
        target_opencode_dir = target_dir / ".opencode" / "command"
        target_skill_dir = target_dir / ".opencode" / "skill" / "ralph"

        target_scripts_dir.mkdir(parents=True, exist_ok=True)
        target_opencode_dir.mkdir(parents=True, exist_ok=True)
        target_skill_dir.mkdir(parents=True, exist_ok=True)

        # Copy core Ralph files
        core_files = [
            ("ralph.sh", target_scripts_dir / "ralph.sh"),
            ("prompt.md", target_scripts_dir / "prompt.md"),
            ("prd.json.example", target_dir / "prd.json.example"),
            ("ralph-loop.sh", target_dir / "ralph-loop.sh"),
        ]

        for src_name, dst_path in core_files:
            src_path = source_dir / src_name
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                # Make ralph.sh executable
                if src_name == "ralph.sh":
                    dst_path.chmod(0o755)

        # Copy OpenCode command files
        opencode_src = source_dir / ".opencode" / "command"
        if opencode_src.exists():
            for cmd_file in opencode_src.iterdir():
                if cmd_file.is_file():
                    shutil.copy2(cmd_file, target_opencode_dir / cmd_file.name)

        # Create OpenCode skill file in .opencode/skill/ralph/SKILL.md
        skill_content = """---
name: ralph
description: "Use Ralph (autonomous AI agent loop) with OpenCode. Ralph runs OpenCode agents repeatedly until all PRD items are complete. Each iteration is a fresh OpenCode agent with clean context. Triggers on: run ralph, start ralph loop, use ralph for this project, set up ralph."
---

# Ralph OpenCode Skill

Ralph is an autonomous AI agent loop that runs OpenCode repeatedly until all PRD items are complete.

## Available Commands

After installing Ralph, you get these OpenCode commands:

- `/ralph-run` - Run Ralph loop with optional max iterations
- `/ralph-validate` - Validate PRD.json structure
- `/ralph-status` - Check current Ralph status and progress
- `/ralph-quality` - Run quality gates (tests, linting, formatting)
- `/ralph-test-complete` - Test COMPLETE signal detection

## Quick Start

1. **Create a PRD:**
   ```bash
   # Copy prd.json.example to prd.json and edit
   cp prd.json.example prd.json
   ```

2. **Run Ralph:**
   ```bash
   ./scripts/ralph/ralph.sh [max_iterations]
   ```

## Key Files

- `scripts/ralph/ralph.sh` - Main Ralph loop script
- `scripts/ralph/prompt.md` - OpenCode agent instructions
- `prd.json` - Product Requirements Document
- `progress.txt` - Agent memory across iterations
- `.opencode/command/` - Ralph OpenCode commands
- `.opencode/skill/ralph/` - Ralph skill definition

## Source

Repository: [opencode-ralph](https://github.com/kha1n3vol3/opencode-ralph)

Contains full implementation, tests, and examples.
"""

        skill_file = target_skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        # Copy Python utilities
        scripts_src = source_dir / "scripts" / "ralph"
        if scripts_src.exists():
            for py_file in scripts_src.iterdir():
                if py_file.is_file() and py_file.suffix == ".py":
                    shutil.copy2(py_file, target_scripts_dir / py_file.name)

        # Copy validation script
        validate_src = scripts_src / "validate_prd.py"
        if validate_src.exists():
            shutil.copy2(validate_src, target_scripts_dir / "validate_prd.py")

        # Copy __init__.py if exists
        init_src = scripts_src / "__init__.py"
        if init_src.exists():
            shutil.copy2(init_src, target_scripts_dir / "__init__.py")

        return True

    except Exception as e:
        print(f"Error installing Ralph skill: {e}")
        return False


def install_ralph_as_opencode_skill(skill_name: str = "ralph") -> bool:
    """
    Install Ralph as an OpenCode skill to user's skill directory.

    Args:
        skill_name: Name for the skill (default: "ralph")

    Returns:
        True if installation successful, False otherwise
    """
    try:
        # Get user's OpenCode skills directory (global installation)
        user_skills_dir = Path.home() / ".config" / "opencode" / "skill"
        user_skills_dir.mkdir(parents=True, exist_ok=True)

        # Create target skill directory
        target_skill_dir = user_skills_dir / skill_name
        target_skill_dir.mkdir(parents=True, exist_ok=True)

        # Create skill file following OpenCode skill format
        skill_content = """---
name: ralph
description: "Use Ralph (autonomous AI agent loop) with OpenCode. Ralph runs OpenCode agents repeatedly until all PRD items are complete. Each iteration is a fresh OpenCode agent with clean context. Triggers on: run ralph, start ralph loop, use ralph for this project, set up ralph."
---

# Ralph OpenCode Skill

Ralph is an autonomous AI agent loop that runs OpenCode repeatedly until all PRD items are complete.

## Installation

To use Ralph in your project:

### Option 1: Clone the repository
```bash
git clone https://github.com/kha1n3vol3/opencode-ralph.git
cd opencode-ralph
```

### Option 2: Install via Python script
```bash
python3 -c "from ralph.install import install_ralph_skill; from pathlib import Path; install_ralph_skill(Path('.'))"
```

## Available Commands

After installing Ralph to your project, you get these OpenCode commands:

- `/ralph-run` - Run Ralph loop with optional max iterations
- `/ralph-validate` - Validate PRD.json structure
- `/ralph-status` - Check current Ralph status and progress
- `/ralph-quality` - Run quality gates (tests, linting, formatting)
- `/ralph-test-complete` - Test COMPLETE signal detection

## Quick Start

1. **Create a PRD:**
   ```bash
   cp prd.json.example prd.json
   # Edit prd.json with your user stories
   ```

2. **Run Ralph:**
   ```bash
   ./scripts/ralph/ralph.sh [max_iterations]
   ```

## How Ralph Works

1. Reads PRD (`prd.json`) - contains user stories with `passes: false`
2. Reads progress (`progress.txt`) - agent memory from previous iterations
3. Picks highest priority incomplete story
4. Implements that single story using OpenCode tools
5. Runs quality checks (tests, linting, formatting)
6. Commits changes with story ID in message
7. Updates PRD to set `passes: true` for completed story
8. Appends progress to `progress.txt`
9. Continues until all stories complete or max iterations reached

## Key Files

- `scripts/ralph/ralph.sh` - Main Ralph loop script
- `scripts/ralph/prompt.md` - OpenCode agent instructions
- `prd.json` - Product Requirements Document
- `progress.txt` - Agent memory across iterations
- `.opencode/command/` - Ralph OpenCode commands
- `.opencode/skill/ralph/` - Ralph skill definition

## Source

Repository: [opencode-ralph](https://github.com/kha1n3vol3/opencode-ralph)

Contains full implementation, tests, and examples.
"""

        # Write skill file
        skill_file = target_skill_dir / "SKILL.md"
        skill_file.write_text(skill_content)

        return True

    except Exception as e:
        print(f"Error installing Ralph as OpenCode skill: {e}")
        return False


if __name__ == "__main__":
    # Simple CLI for installation
    import argparse

    parser = argparse.ArgumentParser(description="Install Ralph skill")
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target project directory (default: current directory)",
    )
    parser.add_argument(
        "--opencode-skill",
        action="store_true",
        help="Install as OpenCode skill to user directory",
    )

    args = parser.parse_args()

    if args.opencode_skill:
        success = install_ralph_as_opencode_skill()
        if success:
            print("✓ Ralph installed as OpenCode skill")
            print("  Run 'opencode debug skill' to verify")
        else:
            print("✗ Failed to install Ralph as OpenCode skill")
    else:
        target_path = Path(args.target_dir).resolve()
        success = install_ralph_skill(target_path)
        if success:
            print(f"✓ Ralph skill installed to {target_path}")
            print("  Files copied:")
            print("    - scripts/ralph/ralph.sh (executable)")
            print("    - scripts/ralph/prompt.md")
            print("    - .opencode/command/*.md")
            print("    - skills/ralph/SKILL.md")
            print("    - skills/prd/SKILL.md")
            print("    - prd.json.example")
            print("    - ralph-loop.sh")
        else:
            print(f"✗ Failed to install Ralph skill to {target_path}")
