#!/usr/bin/env python3
"""
Integration tests for Ralph workflow with OpenCode.
Tests that ralph.sh correctly detects completion signal from opencode.
Issue: dgz
"""

import json
import os
import shutil
import subprocess
import pytest
from pathlib import Path


def create_mock_opencode_script(output_dir: Path) -> Path:
    """Create a mock opencode script that outputs COMPLETE signal."""
    script_path = output_dir / "opencode"
    script_content = """#!/bin/bash
# Mock opencode that outputs COMPLETE signal
echo '<promise>COMPLETE</promise>'
exit 0
"""
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    return script_path


def create_mock_prd(prd_path: Path) -> None:
    """Create a minimal valid PRD for testing."""
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


class TestRalphWorkflow:
    """Integration tests for Ralph workflow with OpenCode."""

    def test_ralph_completion_detection(self, tmp_path: Path):
        """Test that ralph.sh detects COMPLETE signal from opencode and exits successfully."""
        # Set up temporary directory
        test_dir = tmp_path / "ralph_test"
        test_dir.mkdir()

        # Copy ralph.sh and prompt.md to test directory
        project_root = Path(__file__).parent.parent.parent
        shutil.copy(project_root / "ralph.sh", test_dir)
        shutil.copy(project_root / "prompt.md", test_dir)

        # Create mock PRD
        prd_path = test_dir / "prd.json"
        create_mock_prd(prd_path)

        # Create mock opencode script
        mock_bin_dir = test_dir / "bin"
        mock_bin_dir.mkdir()
        mock_opencode = create_mock_opencode_script(mock_bin_dir)

        # Create progress.txt file
        progress_path = test_dir / "progress.txt"
        progress_path.write_text("# Ralph Progress Log\n")

        # Prepare environment with mock opencode in PATH
        env = os.environ.copy()
        env["PATH"] = f"{mock_bin_dir}:{env['PATH']}"

        # Run ralph.sh with max iterations 1
        ralph_script = test_dir / "ralph.sh"
        ralph_script.chmod(0o755)

        result = subprocess.run(
            [str(ralph_script), "1"],
            cwd=str(test_dir),
            env=env,
            capture_output=True,
            text=True,
        )

        # Debug output if test fails
        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")

        # Assert ralph.sh exited successfully (detected COMPLETE)
        assert result.returncode == 0, (
            f"ralph.sh failed with exit code {result.returncode}"
        )

        # Assert COMPLETE signal was processed (ralph.sh should print completion message)
        assert (
            "Ralph completed all tasks!" in result.stdout
            or "Ralph completed all tasks!" in result.stderr
        )

    def test_ralph_max_iterations(self, tmp_path: Path):
        """Test that ralph.sh stops after max iterations when no COMPLETE signal."""
        # Set up temporary directory
        test_dir = tmp_path / "ralph_test_max"
        test_dir.mkdir()

        # Copy ralph.sh and prompt.md
        project_root = Path(__file__).parent.parent.parent
        shutil.copy(project_root / "ralph.sh", test_dir)
        shutil.copy(project_root / "prompt.md", test_dir)

        # Create mock PRD
        prd_path = test_dir / "prd.json"
        create_mock_prd(prd_path)

        # Create mock opencode script that does NOT output COMPLETE
        mock_bin_dir = test_dir / "bin"
        mock_bin_dir.mkdir()
        mock_script = mock_bin_dir / "opencode"
        mock_script.write_text("#!/bin/bash\necho 'No COMPLETE signal'\nexit 0\n")
        mock_script.chmod(0o755)

        # Create progress.txt
        progress_path = test_dir / "progress.txt"
        progress_path.write_text("# Ralph Progress Log\n")

        # Prepare environment
        env = os.environ.copy()
        env["PATH"] = f"{mock_bin_dir}:{env['PATH']}"

        # Run ralph.sh with max iterations 2
        ralph_script = test_dir / "ralph.sh"
        ralph_script.chmod(0o755)

        result = subprocess.run(
            [str(ralph_script), "2"],
            cwd=str(test_dir),
            env=env,
            capture_output=True,
            text=True,
        )

        # Debug output if test fails
        if result.returncode == 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")

        # Assert ralph.sh exited with error (max iterations reached)
        assert result.returncode != 0, (
            "ralph.sh should exit with error when max iterations reached"
        )

        # Assert max iterations message appears
        assert (
            "Ralph reached max iterations" in result.stdout
            or "Ralph reached max iterations" in result.stderr
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
