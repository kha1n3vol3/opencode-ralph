#!/usr/bin/env python3
"""
TDD tests for Ralph loop core logic.
These tests should fail initially for missing functionality.
Follows RED-GREEN-REFACTOR methodology.
"""

import json
import tempfile
import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestRalphCoreLogic:
    """Tests for Ralph core logic functions."""

    def test_get_next_story_returns_highest_priority_incomplete(self):
        """get_next_story should return highest priority incomplete story."""
        prd_data = {
            "project": "test",
            "branchName": "test-branch",
            "description": "Test",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Low priority",
                    "description": "Low",
                    "acceptanceCriteria": [],
                    "priority": 3,
                    "passes": False,
                    "notes": "",
                },
                {
                    "id": "US-002",
                    "title": "High priority incomplete",
                    "description": "High",
                    "acceptanceCriteria": [],
                    "priority": 1,
                    "passes": False,
                    "notes": "",
                },
                {
                    "id": "US-003",
                    "title": "Medium priority completed",
                    "description": "Medium",
                    "acceptanceCriteria": [],
                    "priority": 2,
                    "passes": True,  # Already completed
                    "notes": "",
                },
            ],
        }

        # This import should fail initially (RED phase)
        from ralph.core import get_next_story

        result = get_next_story(prd_data)

        # Should return US-002 (priority 1, incomplete)
        assert result is not None, "Should return a story"
        assert result["id"] == "US-002", f"Expected US-002, got {result.get('id')}"
        assert result["priority"] == 1, (
            f"Expected priority 1, got {result.get('priority')}"
        )
        assert result["passes"] is False, "Should be incomplete"

    def test_get_next_story_returns_none_when_all_complete(self):
        """get_next_story should return None when all stories have passes: true."""
        prd_data = {
            "project": "test",
            "branchName": "test-branch",
            "description": "Test",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Completed story",
                    "description": "Done",
                    "acceptanceCriteria": [],
                    "priority": 1,
                    "passes": True,  # Completed
                    "notes": "",
                },
                {
                    "id": "US-002",
                    "title": "Another completed",
                    "description": "Also done",
                    "acceptanceCriteria": [],
                    "priority": 2,
                    "passes": True,  # Completed
                    "notes": "",
                },
            ],
        }

        from ralph.core import get_next_story

        result = get_next_story(prd_data)

        assert result is None, f"Should return None when all complete, got {result}"

    def test_is_complete_detects_all_stories_done(self):
        """is_complete should return True when all stories have passes: true."""
        prd_data = {
            "project": "test",
            "branchName": "test-branch",
            "description": "Test",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Done",
                    "description": "Done",
                    "acceptanceCriteria": [],
                    "priority": 1,
                    "passes": True,
                    "notes": "",
                },
                {
                    "id": "US-002",
                    "title": "Also done",
                    "description": "Done",
                    "acceptanceCriteria": [],
                    "priority": 2,
                    "passes": True,
                    "notes": "",
                },
            ],
        }

        from ralph.core import is_complete

        result = is_complete(prd_data)

        assert result is True, f"Should return True when all complete, got {result}"

    def test_is_complete_detects_incomplete_stories(self):
        """is_complete should return False when any story has passes: false."""
        prd_data = {
            "project": "test",
            "branchName": "test-branch",
            "description": "Test",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Done",
                    "description": "Done",
                    "acceptanceCriteria": [],
                    "priority": 1,
                    "passes": True,
                    "notes": "",
                },
                {
                    "id": "US-002",
                    "title": "Not done",
                    "description": "Not done",
                    "acceptanceCriteria": [],
                    "priority": 2,
                    "passes": False,  # Incomplete
                    "notes": "",
                },
            ],
        }

        from ralph.core import is_complete

        result = is_complete(prd_data)

        assert result is False, (
            f"Should return False when incomplete stories exist, got {result}"
        )

    def test_update_progress_appends_to_file(self):
        """update_progress should append progress to file with correct format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# Ralph Progress Log\nStarted: Test\n---\n")
            progress_path = f.name

        try:
            from ralph.core import update_progress

            story_id = "US-001"
            implementation_notes = "Implemented feature X\nChanged files: a.py, b.py"
            learnings = ["Use pattern Y for Z", "Always check configuration first"]

            update_progress(progress_path, story_id, implementation_notes, learnings)

            # Read file and verify
            with open(progress_path) as f:
                content = f.read()

            # Should contain story ID
            assert "## " in content, "Should have section header"
            assert story_id in content, f"Should contain story ID {story_id}"
            assert "Implemented feature X" in content, (
                "Should contain implementation notes"
            )
            assert "Learnings for future iterations:" in content, (
                "Should have learnings section"
            )
            assert "Use pattern Y for Z" in content, "Should contain learnings"
            assert "Always check configuration first" in content, (
                "Should contain learnings"
            )

            # Original content should still be there
            assert "# Ralph Progress Log" in content, "Should preserve original content"

        finally:
            Path(progress_path).unlink(missing_ok=True)

    def test_consolidate_patterns_adds_to_codebase_patterns_section(self):
        """consolidate_patterns should add patterns to Codebase Patterns section."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# Ralph Progress Log\nStarted: Test\n---\n")
            progress_path = f.name

        try:
            from ralph.core import consolidate_patterns

            patterns = [
                "Use sql<number> template for aggregations",
                "Always use IF NOT EXISTS for migrations",
            ]

            consolidate_patterns(progress_path, patterns)

            # Read file and verify
            with open(progress_path) as f:
                content = f.read()

            # Should have Codebase Patterns section
            assert "## Codebase Patterns" in content, (
                "Should have Codebase Patterns section"
            )
            assert "Use sql<number> template for aggregations" in content, (
                "Should contain pattern 1"
            )
            assert "Always use IF NOT EXISTS for migrations" in content, (
                "Should contain pattern 2"
            )

            # Original content should still be there
            assert "# Ralph Progress Log" in content, "Should preserve original content"

        finally:
            Path(progress_path).unlink(missing_ok=True)

    def test_consolidate_patterns_creates_section_if_missing(self):
        """consolidate_patterns should create Codebase Patterns section if it doesn't exist."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# Ralph Progress Log\nStarted: Test\n---\n")
            progress_path = f.name

        try:
            from ralph.core import consolidate_patterns

            patterns = ["New pattern to add"]

            consolidate_patterns(progress_path, patterns)

            with open(progress_path) as f:
                content = f.read()

            # Should add section at top (after initial header)
            lines = content.split("\n")
            # Find Codebase Patterns line
            pattern_line_index = -1
            for i, line in enumerate(lines):
                if "## Codebase Patterns" in line:
                    pattern_line_index = i
                    break

            assert pattern_line_index > 0, "Codebase Patterns section should exist"
            # Should be near top (after initial header lines)
            assert pattern_line_index < 10, (
                f"Codebase Patterns should be near top, found at line {pattern_line_index}"
            )

        finally:
            Path(progress_path).unlink(missing_ok=True)


class TestRalphFileOperations:
    """Tests for Ralph file operations."""

    def test_read_prd_loads_valid_json(self):
        """read_prd should load and parse PRD JSON file."""
        prd_data = {
            "project": "test-project",
            "branchName": "test-branch",
            "description": "Test description",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Test",
                    "description": "Test",
                    "acceptanceCriteria": [],
                    "priority": 1,
                    "passes": False,
                    "notes": "",
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(prd_data, f)
            prd_path = f.name

        try:
            from ralph.core import read_prd

            result = read_prd(prd_path)

            assert result is not None, "Should load PRD data"
            assert result["project"] == "test-project", (
                f"Wrong project: {result.get('project')}"
            )
            assert result["branchName"] == "test-branch", (
                f"Wrong branch: {result.get('branchName')}"
            )
            assert len(result["userStories"]) == 1, (
                f"Wrong number of stories: {len(result.get('userStories', []))}"
            )
            assert result["userStories"][0]["id"] == "US-001", (
                f"Wrong story ID: {result['userStories'][0].get('id')}"
            )

        finally:
            Path(prd_path).unlink(missing_ok=True)

    def test_write_prd_updates_file(self):
        """write_prd should write PRD data to file."""
        prd_data = {
            "project": "updated-project",
            "branchName": "updated-branch",
            "description": "Updated description",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Updated",
                    "description": "Updated",
                    "acceptanceCriteria": ["New criterion"],
                    "priority": 1,
                    "passes": True,  # Mark as completed
                    "notes": "Completed in test",
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"old": "data"}, f)  # Initial content
            prd_path = f.name

        try:
            from ralph.core import write_prd

            write_prd(prd_path, prd_data)

            # Read back and verify
            with open(prd_path) as f:
                loaded = json.load(f)

            assert loaded["project"] == "updated-project", (
                f"Project not updated: {loaded.get('project')}"
            )
            assert loaded["branchName"] == "updated-branch", (
                f"Branch not updated: {loaded.get('branchName')}"
            )
            assert loaded["userStories"][0]["passes"] is True, (
                f"Story not marked complete: {loaded['userStories'][0].get('passes')}"
            )
            assert loaded["userStories"][0]["notes"] == "Completed in test", (
                f"Notes not updated: {loaded['userStories'][0].get('notes')}"
            )

        finally:
            Path(prd_path).unlink(missing_ok=True)


if __name__ == "__main__":
    # Simple runner for manual testing
    pytest.main([__file__, "-v"])
