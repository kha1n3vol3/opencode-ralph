#!/usr/bin/env python3
"""
Demonstration script for Ralph PRD validation workflow.

This script demonstrates how to create a test PRD and run Ralph validation.
Shows both valid and invalid PRD examples with error handling and logging.
"""

import json
import logging
import sys
import tempfile
from pathlib import Path

# Import Ralph validation function
# Add repo root to sys.path to allow importing scripts.ralph
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from scripts.ralph.validate_prd import validate_prd_json  # noqa: E402


def setup_logging():
    """Configure basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(__name__)


def create_valid_prd(prd_path: Path):
    """Create a valid PRD JSON file for testing."""
    valid_prd = {
        "project": "Ralph Validation Demo",
        "branchName": "demo/validation-test",
        "description": "Demonstrate PRD validation with Ralph",
        "userStories": [
            {
                "id": "US-001",
                "title": "Test validation script",
                "description": "As a developer, I want to validate PRD structure.",
                "acceptanceCriteria": [
                    "Create valid PRD JSON",
                    "Run validation script",
                    "Verify validation passes",
                ],
                "priority": 1,
                "passes": False,
                "notes": "",
            }
        ],
    }
    with open(prd_path, "w") as f:
        json.dump(valid_prd, f, indent=2)
    return prd_path


def create_invalid_prd(prd_path: Path):
    """Create an invalid PRD JSON file (missing required fields)."""
    invalid_prd = {
        "project": "Invalid Demo",
        # Missing branchName, description, userStories
    }
    with open(prd_path, "w") as f:
        json.dump(invalid_prd, f, indent=2)
    return prd_path


def create_partially_invalid_prd(prd_path: Path):
    """Create PRD with valid structure but invalid user story (missing fields)."""
    invalid_prd = {
        "project": "Partial Invalid Demo",
        "branchName": "demo/partial",
        "description": "PRD with invalid user story structure",
        "userStories": [
            {
                "id": "US-001",
                "title": "Missing required fields",
                # Missing description, acceptanceCriteria, priority, passes, notes
            }
        ],
    }
    with open(prd_path, "w") as f:
        json.dump(invalid_prd, f, indent=2)
    return prd_path


def run_validation(prd_path: Path, logger):
    """Run Ralph validation on PRD file and log result."""
    logger.info(f"Validating PRD: {prd_path.name}")
    try:
        result = validate_prd_json(str(prd_path))
        if result:
            logger.info("✓ Validation PASSED")
        else:
            logger.error("✗ Validation FAILED")
        return result
    except Exception as e:
        logger.exception(f"Validation error: {e}")
        return False


def main():
    """Main demonstration workflow."""
    logger = setup_logging()

    print("=" * 60)
    print("Ralph PRD Validation Demonstration")
    print("=" * 60)
    print("\nThis script demonstrates Ralph PRD validation workflow.")
    print("It creates test PRDs (valid and invalid) and runs validation.")
    print("=" * 60)

    # Create temporary directory for test PRDs
    with tempfile.TemporaryDirectory(prefix="ralph-validation-demo-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        logger.info(f"Created temporary directory: {tmpdir_path}")

        # Test 1: Valid PRD
        print("\n1. Testing VALID PRD")
        valid_prd_path = tmpdir_path / "valid_prd.json"
        create_valid_prd(valid_prd_path)
        logger.info(f"Created valid PRD at {valid_prd_path}")
        valid_result = run_validation(valid_prd_path, logger)

        # Test 2: Invalid PRD (missing top-level fields)
        print("\n2. Testing INVALID PRD (missing required fields)")
        invalid_prd_path = tmpdir_path / "invalid_prd.json"
        create_invalid_prd(invalid_prd_path)
        logger.info(f"Created invalid PRD at {invalid_prd_path}")
        invalid_result = run_validation(invalid_prd_path, logger)

        # Test 3: Partially invalid PRD (invalid user story)
        print("\n3. Testing PARTIALLY INVALID PRD (invalid user story)")
        partial_prd_path = tmpdir_path / "partial_invalid_prd.json"
        create_partially_invalid_prd(partial_prd_path)
        logger.info(f"Created partially invalid PRD at {partial_prd_path}")
        partial_result = run_validation(partial_prd_path, logger)

        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Valid PRD: {'PASS' if valid_result else 'FAIL'} (expected: PASS)")
        print(
            f"Invalid PRD (missing fields): {'PASS' if invalid_result else 'FAIL'} (expected: FAIL)"
        )
        print(
            f"Partially invalid PRD: {'PASS' if partial_result else 'FAIL'} (expected: FAIL)"
        )

        all_expected = valid_result and not invalid_result and not partial_result

        if all_expected:
            print("\n✅ All tests passed as expected!")
            print("Ralph validation correctly identifies valid and invalid PRDs.")
        else:
            print("\n❌ Some tests did not pass as expected.")
            print("Check the validation logic in scripts/ralph/validate_prd.py")
            return 1

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey takeaways:")
    print("✅ Ralph validation checks PRD structure")
    print("✅ Identifies missing required fields")
    print("✅ Validates user story structure")
    print("✅ Can be integrated into CI/CD pipelines")
    print("\nTo use in your project:")
    print("  from scripts.ralph.validate_prd import validate_prd_json")
    print("  is_valid = validate_prd_json('path/to/prd.json')")

    return 0


if __name__ == "__main__":
    sys.exit(main())
