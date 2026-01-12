---
description: Run Ralph quality gates (tests, linting, formatting)
---

Run Ralph quality gates for Python projects.

Check if UV is available:
!`which uv && echo "✓ UV found" || echo "✗ UV not found"`

Check if virtual environment exists:
!`[ -d ".venv" ] && echo "✓ Virtual environment found" || echo "✗ No virtual environment"`

Run tests:
!`uv run pytest tdd/ -v 2>&1 | tail -20`

Run linting:
!`uv run ruff check . --fix 2>&1 | tail -20`

Run formatting:
!`uv run ruff format . 2>&1 | tail -10`

Run type checking (if configured):
!`[ -f "pyproject.toml" ] && grep -q "ty" pyproject.toml && uv run ty . 2>&1 | tail -20 || echo "Type checking not configured"`

Summarize the quality check results and suggest fixes if needed.