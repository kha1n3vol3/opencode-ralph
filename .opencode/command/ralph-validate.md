---
description: Validate PRD.json for Ralph
---

Validate the PRD.json file for Ralph.

Check if the PRD has required fields and valid user stories.

Run the validation script:
!`python3 scripts/ralph/validate_prd.py prd.json && echo "✓ PRD valid" || echo "✗ PRD invalid"`

If the PRD is invalid, explain what's wrong and suggest fixes.