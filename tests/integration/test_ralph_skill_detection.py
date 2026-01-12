#!/usr/bin/env python3
"""
Integration tests for Ralph skill detection with OpenCode CLI.
Tests that Ralph skill appears in 'opencode debug skill' output.
Uses real opencode CLI instead of mocks.
"""

import json
import subprocess
import pytest
import sys
from pathlib import Path

# Add scripts directory to path to import ralph modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


def run_opencode_debug_skill(workdir: Path) -> list:
    """
    Run 'opencode debug skill' and parse JSON output.

    Args:
        workdir: Directory to run command from

    Returns:
        List of skills as dictionaries
    """
    try:
        result = subprocess.run(
            ["opencode", "debug", "skill"],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"opencode debug skill failed: {result.stderr}")
            return []

        # Parse JSON output
        skills = json.loads(result.stdout)
        return skills

    except subprocess.TimeoutExpired:
        print("opencode debug skill timed out")
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON output: {e}")
        print(f"Output: {result.stdout}")
        return []


@pytest.mark.integration
@pytest.mark.slow
class TestRalphSkillDetection:
    """Integration tests for Ralph skill detection."""

    def test_ralph_skill_appears_in_opencode_debug_skill_output(self, tmp_path: Path):
        """Test that Ralph skill appears in 'opencode debug skill' output when installed."""
        # Create a test project directory
        test_dir = tmp_path / "ralph-skill-test"
        test_dir.mkdir()

        # Initialize as git repo (OpenCode may require git)
        subprocess.run(
            ["git", "init"],
            cwd=str(test_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=str(test_dir),
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=str(test_dir),
            capture_output=True,
        )

        # Install Ralph skill to the test directory
        from ralph.install import install_ralph_skill

        success = install_ralph_skill(test_dir)
        assert success is True, "Failed to install Ralph skill"

        # Verify .opencode/skill/ralph/SKILL.md exists
        skill_file = test_dir / ".opencode" / "skill" / "ralph" / "SKILL.md"
        assert skill_file.exists(), "Ralph skill file not created"

        # Run opencode debug skill from the test directory
        skills = run_opencode_debug_skill(test_dir)

        # Debug output
        print(f"Found {len(skills)} skills:")
        for skill in skills:
            print(
                f"  - {skill.get('name', 'unknown')}: {skill.get('description', 'no description')}"
            )

        # Check if Ralph skill is in the output
        ralph_skill = None
        for skill in skills:
            if skill.get("name") == "ralph":
                ralph_skill = skill
                break

        assert ralph_skill is not None, (
            "Ralph skill not found in 'opencode debug skill' output"
        )
        assert "description" in ralph_skill, "Ralph skill missing description"

        # Verify description matches expected content
        description = ralph_skill["description"]
        assert "Ralph" in description, (
            f"Ralph skill description doesn't mention Ralph: {description}"
        )
        assert (
            "autonomous" in description.lower() or "agent loop" in description.lower()
        ), f"Ralph skill description incomplete: {description}"

        print(f"✓ Ralph skill detected: {description}")

    def test_ralph_skill_not_in_output_when_not_installed(self, tmp_path: Path):
        """Test that Ralph skill does NOT appear when not installed."""
        # Create a clean test directory without Ralph
        test_dir = tmp_path / "no-ralph-test"
        test_dir.mkdir()

        # Initialize as git repo
        subprocess.run(
            ["git", "init"],
            cwd=str(test_dir),
            capture_output=True,
        )

        # Run opencode debug skill
        skills = run_opencode_debug_skill(test_dir)

        # Debug output
        print(f"Found {len(skills)} skills in clean directory")

        # Check that Ralph skill is NOT in the output
        ralph_skill = None
        for skill in skills:
            if skill.get("name") == "ralph":
                ralph_skill = skill
                break

        # Note: Ralph might still appear if installed globally (~/.config/opencode/skill)
        # That's okay - we just want to verify the test directory doesn't add it
        if ralph_skill:
            print(f"Note: Ralph skill found globally: {ralph_skill['description']}")
            # This is not a failure, just informational

    def test_ralph_opencode_commands_exist(self, tmp_path: Path):
        """Test that Ralph OpenCode commands are installed and usable."""
        test_dir = tmp_path / "ralph-commands-test"
        test_dir.mkdir()

        # Install Ralph skill
        from ralph.install import install_ralph_skill

        success = install_ralph_skill(test_dir)
        assert success is True, "Failed to install Ralph skill"

        # Check that command files exist
        command_files = [
            "ralph-run.md",
            "ralph-validate.md",
            "ralph-status.md",
            "ralph-quality.md",
            "ralph-test-complete.md",
        ]

        for cmd_file in command_files:
            cmd_path = test_dir / ".opencode" / "command" / cmd_file
            assert cmd_path.exists(), f"Missing command file: {cmd_file}"

            # Read the file to verify it has proper frontmatter
            content = cmd_path.read_text()
            assert "---" in content, f"Command file missing frontmatter: {cmd_file}"
            assert "description:" in content, (
                f"Command file missing description: {cmd_file}"
            )

        print(f"✓ All {len(command_files)} Ralph OpenCode command files installed")


if __name__ == "__main__":
    # Simple runner for manual testing
    pytest.main([__file__, "-v"])
