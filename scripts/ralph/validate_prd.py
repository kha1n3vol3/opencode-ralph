#!/usr/bin/env python3
"""
PRD (Product Requirements Document) validation for Ralph OpenCode port.
"""

import json


def validate_prd_json(prd_path: str) -> bool:
    """
    Validate PRD JSON structure has required fields.

    Args:
        prd_path: Path to PRD JSON file

    Returns:
        True if valid, False otherwise
    """
    try:
        with open(prd_path, "r") as f:
            prd_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return False

    # Validate top-level required fields
    required_fields = ["project", "branchName", "description", "userStories"]
    for field in required_fields:
        if field not in prd_data:
            return False

    # Validate user stories structure
    user_stories = prd_data["userStories"]
    if not isinstance(user_stories, list):
        return False

    user_story_required = [
        "id",
        "title",
        "description",
        "acceptanceCriteria",
        "priority",
        "passes",
        "notes",
    ]

    for story in user_stories:
        if not isinstance(story, dict):
            return False

        for field in user_story_required:
            if field not in story:
                return False

        # Additional validation for acceptanceCriteria
        if not isinstance(story["acceptanceCriteria"], list):
            return False

    return True
