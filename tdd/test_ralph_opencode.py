#!/usr/bin/env python3
"""
TDD tests for Ralph OpenCode port functionality.
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


class TestPRDValidation:
    """Tests for PRD (Product Requirements Document) validation."""

    def test_prd_json_validation(self):
        """Validate PRD JSON structure has required fields."""
        # Create temporary PRD JSON file
        prd_data = {
            "project": "test-project",
            "branchName": "test-branch",
            "description": "Test project description",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Test User Story",
                    "description": "Test description",
                    "acceptanceCriteria": ["Criterion 1", "Criterion 2"],
                    "priority": "P1",
                    "passes": True,
                    "notes": "Test notes",
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(prd_data, f)
            prd_path = f.name

        try:
            # This import should fail initially (RED phase)
            from ralph.validate_prd import validate_prd_json

            # Validate the PRD
            result = validate_prd_json(prd_path)

            # Assert validation passes
            assert result is True, f"PRD validation failed for valid PRD: {result}"
        finally:
            # Clean up temporary file
            Path(prd_path).unlink(missing_ok=True)

    def test_prd_json_validation_missing_fields(self):
        """Validate PRD JSON validation catches missing required fields."""
        # Create PRD with missing required field
        prd_data = {
            "project": "test-project",
            # Missing branchName
            "description": "Test description",
            "userStories": [],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(prd_data, f)
            prd_path = f.name

        try:
            from ralph.validate_prd import validate_prd_json

            result = validate_prd_json(prd_path)

            # Should return False for invalid PRD
            assert result is False, (
                f"PRD validation should fail for missing field: {result}"
            )
        finally:
            Path(prd_path).unlink(missing_ok=True)

    def test_prd_user_story_validation(self):
        """Validate user story structure within PRD."""
        prd_data = {
            "project": "test-project",
            "branchName": "test-branch",
            "description": "Test description",
            "userStories": [
                {
                    "id": "US-001",
                    "title": "Test User Story",
                    # Missing description
                    "acceptanceCriteria": ["Criterion"],
                    "priority": "P1",
                    "passes": True,
                    "notes": "",
                }
            ],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(prd_data, f)
            prd_path = f.name

        try:
            from ralph.validate_prd import validate_prd_json

            result = validate_prd_json(prd_path)

            # Should return False for invalid user story
            assert result is False, (
                f"PRD validation should fail for invalid user story: {result}"
            )
        finally:
            Path(prd_path).unlink(missing_ok=True)


if __name__ == "__main__":
    # Simple runner for manual testing
    pytest.main([__file__, "-v"])
