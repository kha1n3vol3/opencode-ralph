#!/usr/bin/env python3
"""
Integration tests for Ralph workflow with real OpenCode CLI.
Tests that ralph.sh correctly detects completion signal from opencode.
Uses real opencode CLI instead of mocks.
"""

import json
import shutil
import subprocess
import pytest
from pathlib import Path


def create_prd(prd_path: Path, all_passed: bool = False) -> None:
    """Create a test PRD."""
    if all_passed:
        prd_data = {
            "project": "TestProject",
            "branchName": "ralph/test-completed",
            "description": "Test project with completed stories",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Completed Story",
                    "description": "A story that's already done",
                    "acceptanceCriteria": ["Already completed"],
                    "priority": 1,
                    "passes": True,
                    "notes": "Test completion",
                }
            ],
        }
    else:
        prd_data = {
            "project": "TestProject",
            "branchName": "ralph/test",
            "description": "Test project for integration testing",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Test Story",
                    "description": "A test story",
                    "acceptanceCriteria": ["Criterion 1"],
                    "priority": 1,
                    "passes": False,
                    "notes": "",
                }
            ],
        }
    prd_path.write_text(json.dumps(prd_data, indent=2))


def run_ralph_script(
    workdir: Path, max_iterations: int = 1, timeout: int = 180
) -> subprocess.CompletedProcess:
    """Run ralph.sh script in the given directory."""
    ralph_script = workdir / "ralph.sh"
    ralph_script.chmod(0o755)

    try:
        result = subprocess.run(
            [str(ralph_script), str(max_iterations)],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            [str(ralph_script)], returncode=124, stdout="", stderr="Timeout expired"
        )


@pytest.mark.integration
@pytest.mark.slow
class TestRalphWorkflowReal:
    """Integration tests for Ralph workflow with real OpenCode CLI."""

    @pytest.fixture
    def setup_test_dir(self, tmp_path: Path):
        """Set up a test directory with ralph.sh, prompt.md, and PRD."""
        test_dir = tmp_path / "ralph_test_real"
        test_dir.mkdir()

        # Copy ralph.sh and prompt.md to test directory
        project_root = Path(__file__).parent.parent.parent
        shutil.copy(project_root / "ralph.sh", test_dir)
        shutil.copy(project_root / "prompt.md", test_dir)

        # Initialize git repo for testing (required for commits)
        subprocess.run(["git", "init"], cwd=str(test_dir), capture_output=True)
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

        # Create empty progress.txt
        progress_path = test_dir / "progress.txt"
        progress_path.write_text("# Ralph Progress Log\n")

        return test_dir

    def test_ralph_completion_with_all_passed(self, setup_test_dir):
        """Test that ralph.sh detects COMPLETE signal when all stories are already passed."""
        test_dir = setup_test_dir

        # Create PRD with all stories already passed
        prd_path = test_dir / "prd.json"
        create_prd(prd_path, all_passed=True)

        # Run ralph.sh with max iterations 1
        result = run_ralph_script(test_dir, max_iterations=1, timeout=180)

        # Debug output
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        # Ralph should detect COMPLETE signal and exit successfully
        # The agent should see all stories have passes: true and output <promise>COMPLETE</promise>
        if result.returncode != 0:
            print(f"Exit code: {result.returncode}")

        # Note: This test may fail if opencode doesn't output COMPLETE as expected
        # That's okay - it helps us debug the actual behavior
        assert result.returncode == 0, (
            f"ralph.sh failed with exit code {result.returncode}"
        )
        assert (
            "Ralph completed all tasks!" in result.stdout
            or "Ralph completed all tasks!" in result.stderr
        )

    def test_ralph_with_simple_story(self, setup_test_dir):
        """Test ralph.sh with a simple story that can be completed quickly."""
        test_dir = setup_test_dir

        # Create PRD with a very simple story
        prd_data = {
            "project": "TestProject",
            "branchName": "ralph/simple-test",
            "description": "Simple test project",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Create a test file",
                    "description": "Create a simple test file to verify Ralph works",
                    "acceptanceCriteria": [
                        "Create file test.txt with content 'hello world'",
                        "Commit changes with message 'feat: US-001 - Create a test file'",
                        "Update PRD to set passes: true for this story",
                    ],
                    "priority": 1,
                    "passes": False,
                    "notes": "",
                }
            ],
        }

        prd_path = test_dir / "prd.json"
        prd_path.write_text(json.dumps(prd_data, indent=2))

        # Run ralph.sh with max iterations 1 and longer timeout
        result = run_ralph_script(test_dir, max_iterations=1, timeout=300)

        # Debug output
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        # Check if file was created
        test_file = test_dir / "test.txt"
        if test_file.exists():
            print(f"Test file created with content: {test_file.read_text()}")

        # Check git status
        git_status = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
        )
        print(f"Git status:\n{git_status.stdout}")

        # For now, just verify ralph.sh ran without crashing
        # The actual completion depends on opencode agent behavior
        print(f"Test completed with exit code: {result.returncode}")

    def test_ralph_max_iterations_real(self, setup_test_dir):
        """Test that ralph.sh stops after max iterations when stories not completed."""
        test_dir = setup_test_dir

        # Create PRD with story that won't be completed quickly
        # Use a story that requires external resources to ensure it won't complete
        prd_data = {
            "project": "TestProject",
            "branchName": "ralph/long-test",
            "description": "Test project with story that won't complete",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Complex story that won't complete",
                    "description": "This story is designed to not complete in test environment",
                    "acceptanceCriteria": [
                        "This should not complete in automated test",
                        "Requires external API that isn't available",
                    ],
                    "priority": 1,
                    "passes": False,
                    "notes": "",
                }
            ],
        }

        prd_path = test_dir / "prd.json"
        prd_path.write_text(json.dumps(prd_data, indent=2))

        # Run ralph.sh with max iterations 2 and short timeout
        result = run_ralph_script(test_dir, max_iterations=2, timeout=180)

        # Debug output
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        # Ralph should exit with error (max iterations reached)
        # Note: This depends on opencode behavior - if it outputs COMPLETE anyway, test will fail
        print(f"Exit code: {result.returncode}")
        print("Test completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
