#!/usr/bin/env python3
"""
TDD tests for Ralph skill installation and invocation.
These tests should fail initially for missing functionality.
Follows RED-GREEN-REFACTOR methodology.
"""

import json
import tempfile
import pytest
import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestRalphSkillInstallation:
    """Tests for Ralph skill installation functionality."""

    def test_ralph_skill_can_be_installed_to_target_directory(self):
        """Validate that Ralph skill files can be copied to a target project."""
        # Create temporary target directory
        with tempfile.TemporaryDirectory() as target_dir:
            target_path = Path(target_dir)

            # This import should fail initially (RED phase)
            from ralph.install import install_ralph_skill

            # Install Ralph skill to target directory
            result = install_ralph_skill(target_path)

            # Assert installation succeeded
            assert result is True, f"Skill installation failed: {result}"

            # Verify key files were copied
            expected_files = [
                target_path / "scripts" / "ralph" / "ralph.sh",
                target_path / "scripts" / "ralph" / "prompt.md",
                target_path / ".opencode" / "command" / "ralph-run.md",
                target_path / ".opencode" / "command" / "ralph-validate.md",
                target_path / ".opencode" / "command" / "ralph-status.md",
                target_path / ".opencode" / "command" / "ralph-quality.md",
                target_path / ".opencode" / "command" / "ralph-test-complete.md",
                target_path / ".opencode" / "skill" / "ralph" / "SKILL.md",
            ]

            for file_path in expected_files:
                assert file_path.exists(), f"Required file not found: {file_path}"
                assert file_path.is_file(), f"Not a file: {file_path}"

            # Verify ralph.sh is executable
            ralph_sh = target_path / "scripts" / "ralph" / "ralph.sh"
            assert os.access(ralph_sh, os.X_OK), f"ralph.sh not executable: {ralph_sh}"


class TestRalphSkillInvocation:
    """Tests for Ralph skill invocation functionality."""

    def test_installed_ralph_skills_support_basic_invocation(self):
        """Validate that installed Ralph skills support basic invocation of the Ralph loop."""
        # Create temporary project directory with installed Ralph skill
        with tempfile.TemporaryDirectory() as project_dir:
            project_path = Path(project_dir)

            # First install the skill (dependency for this test)
            from ralph.install import install_ralph_skill

            install_result = install_ralph_skill(project_path)
            assert install_result is True, "Skill installation failed"

            # Create a minimal PRD for testing
            prd_data = {
                "project": "TestProject",
                "branchName": "ralph/test-feature",
                "description": "Test feature for Ralph invocation",
                "userStories": [
                    {
                        "id": "US-001",
                        "title": "Test story",
                        "description": "As a tester, I want to verify Ralph works.",
                        "acceptanceCriteria": ["Typecheck passes"],
                        "priority": 1,
                        "passes": False,
                        "notes": "",
                    }
                ],
            }

            prd_path = project_path / "prd.json"
            with open(prd_path, "w") as f:
                json.dump(prd_data, f)

            # Test invocation setup using test_ralph_invocation diagnostic function
            from ralph.invoke import test_ralph_invocation

            results = test_ralph_invocation(project_path)

            # Assert basic setup is valid
            assert results["success"] is True, f"Ralph setup invalid: {results}"
            assert results["ralph_sh_exists"] is True, "ralph.sh not found"
            assert results["ralph_sh_executable"] is True, "ralph.sh not executable"
            assert results["prd_exists"] is True, "PRD not found"

            # Verify OpenCode commands were installed
            expected_commands = {
                "ralph-run.md",
                "ralph-validate.md",
                "ralph-status.md",
                "ralph-quality.md",
                "ralph-test-complete.md",
            }
            installed_commands = set(results["opencode_commands"])
            assert installed_commands.issuperset(expected_commands), (
                f"Missing OpenCode commands. Expected: {expected_commands}, Got: {installed_commands}"
            )

            # Verify skill was installed
            assert "ralph" in results["skills"], "Ralph skill not installed"

            # Note: We don't actually run the Ralph loop in unit tests
            # because that requires opencode CLI and is tested in integration tests


if __name__ == "__main__":
    # Simple runner for manual testing
    pytest.main([__file__, "-v"])
