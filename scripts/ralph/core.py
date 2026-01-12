#!/usr/bin/env python3
"""
Ralph core logic module.
Provides functions for PRD processing, progress tracking, and loop management.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import datetime


def get_next_story(prd_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get the highest priority incomplete story from PRD.

    Args:
        prd_data: PRD dictionary with userStories list

    Returns:
        Story dictionary with highest priority where passes is False,
        or None if all stories are complete
    """
    if "userStories" not in prd_data:
        return None

    incomplete_stories = [
        story for story in prd_data["userStories"] if not story.get("passes", False)
    ]

    if not incomplete_stories:
        return None

    # Sort by priority (lower number = higher priority)
    # Handle both string and numeric priorities
    def get_priority(story):
        priority = story.get("priority", 999)
        if isinstance(priority, str) and priority.startswith("P"):
            try:
                return int(priority[1:])
            except ValueError:
                return 999
        try:
            return int(priority)
        except (ValueError, TypeError):
            return 999

    return sorted(incomplete_stories, key=get_priority)[0]


def is_complete(prd_data: Dict[str, Any]) -> bool:
    """
    Check if all user stories in PRD are complete.

    Args:
        prd_data: PRD dictionary with userStories list

    Returns:
        True if all stories have passes: True, False otherwise
    """
    if "userStories" not in prd_data:
        return True  # No stories = complete

    return all(story.get("passes", False) for story in prd_data["userStories"])


def update_progress(
    progress_path: str | Path,
    story_id: str,
    implementation_notes: str,
    learnings: List[str],
) -> None:
    """
    Append progress entry to progress.txt file.

    Args:
        progress_path: Path to progress.txt file
        story_id: Story ID (e.g., "US-001")
        implementation_notes: What was implemented
        learnings: List of learnings for future iterations
    """
    progress_path = Path(progress_path)

    # Create file if it doesn't exist
    if not progress_path.exists():
        progress_path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now()
        progress_path.write_text(f"# Ralph Progress Log\nStarted: {now}\n---\n")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = f"""## {timestamp} - {story_id}
- {implementation_notes}
- **Learnings for future iterations:**
"""

    for learning in learnings:
        entry += f"  - {learning}\n"

    entry += "---\n"

    # Append to file
    with open(progress_path, "a") as f:
        f.write(entry)


def consolidate_patterns(progress_path: str | Path, patterns: List[str]) -> None:
    """
    Add or update Codebase Patterns section in progress.txt.

    Args:
        progress_path: Path to progress.txt file
        patterns: List of pattern strings to add
    """
    progress_path = Path(progress_path)

    if not progress_path.exists():
        # Create file with patterns section
        content = f"""# Ralph Progress Log
Started: {datetime.datetime.now()}

## Codebase Patterns
"""
        for pattern in patterns:
            content += f"- {pattern}\n"

        content += "\n---\n"
        progress_path.write_text(content)
        return

    # Read existing content
    with open(progress_path) as f:
        lines = f.readlines()

    # Find or create Codebase Patterns section
    pattern_section_index = -1
    for i, line in enumerate(lines):
        if "## Codebase Patterns" in line:
            pattern_section_index = i
            break

    if pattern_section_index == -1:
        # Insert after initial header (after "Started:" line)
        insert_index = 0
        for i, line in enumerate(lines):
            if "---" in line:
                insert_index = i
                break
            if i > 10:  # Safety limit
                insert_index = 2
                break

        # Insert patterns section
        patterns_section = ["\n## Codebase Patterns\n"]
        for pattern in patterns:
            patterns_section.append(f"- {pattern}\n")
        patterns_section.append("\n")

        lines = lines[:insert_index] + patterns_section + lines[insert_index:]
    else:
        # Add to existing section
        # Find where to insert (after section header, before next section or end)
        insert_index = pattern_section_index + 1
        for i in range(pattern_section_index + 1, len(lines)):
            if lines[i].startswith("## "):
                insert_index = i
                break
            if i == len(lines) - 1:
                insert_index = len(lines)
                break

        # Add patterns
        new_patterns = []
        for pattern in patterns:
            new_patterns.append(f"- {pattern}\n")

        lines = lines[:insert_index] + new_patterns + lines[insert_index:]

    # Write back
    with open(progress_path, "w") as f:
        f.writelines(lines)


def read_prd(prd_path: str | Path) -> Dict[str, Any]:
    """
    Read and parse PRD JSON file.

    Args:
        prd_path: Path to prd.json file

    Returns:
        PRD data as dictionary
    """
    prd_path = Path(prd_path)

    if not prd_path.exists():
        raise FileNotFoundError(f"PRD file not found: {prd_path}")

    with open(prd_path) as f:
        return json.load(f)


def write_prd(prd_path: str | Path, prd_data: Dict[str, Any]) -> None:
    """
    Write PRD data to JSON file.

    Args:
        prd_path: Path to prd.json file
        prd_data: PRD data dictionary to write
    """
    prd_path = Path(prd_path)

    # Ensure directory exists
    prd_path.parent.mkdir(parents=True, exist_ok=True)

    with open(prd_path, "w") as f:
        json.dump(prd_data, f, indent=2)


def validate_story_completion(prd_data: Dict[str, Any], story_id: str) -> bool:
    """
    Validate that a story's acceptance criteria are met.
    Placeholder for future implementation.

    Args:
        prd_data: PRD data
        story_id: Story ID to validate

    Returns:
        True if story completion can be validated
    """
    # For now, just check if story exists
    for story in prd_data.get("userStories", []):
        if story.get("id") == story_id:
            return True
    return False


def mark_story_complete(
    prd_data: Dict[str, Any], story_id: str, notes: str = ""
) -> Dict[str, Any]:
    """
    Mark a story as complete in PRD data.

    Args:
        prd_data: PRD data
        story_id: Story ID to mark complete
        notes: Optional completion notes

    Returns:
        Updated PRD data
    """
    updated_prd = prd_data.copy()

    for i, story in enumerate(updated_prd.get("userStories", [])):
        if story.get("id") == story_id:
            updated_prd["userStories"][i] = story.copy()
            updated_prd["userStories"][i]["passes"] = True
            if notes:
                updated_prd["userStories"][i]["notes"] = notes
            break

    return updated_prd
