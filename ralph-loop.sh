#!/bin/bash

# Usage: ./ralph-loop.sh <max_iterations> <completion_promise> <prompt>
# Example: ./ralph-loop.sh 20 "COMPLETE" "Build a todo app REST API with tests in Python."

set -e

MAX_ITER=$1
COMPLETION_PROMISE=$2
PROMPT=$3

if [ -z "$MAX_ITER" ] || [ -z "$COMPLETION_PROMISE" ] || [ -z "$PROMPT" ]; then
  echo "Usage: $0 <max_iterations> <completion_promise> <prompt>"
  exit 1
fi

# Optional: Specify model/agent (e.g., --model claude/opus)
OPENCODE_OPTS="--model claude/sonnet"  # Adjust as needed

# Start the initial session
echo "Starting initial iteration..."
RESULT=$(opencode run $OPENCODE_OPTS "$PROMPT")
echo "$RESULT"

if [[ "$RESULT" == *"$COMPLETION_PROMISE"* ]]; then
  echo "Task complete on first iteration."
  exit 0
fi

# Loop for subsequent iterations using --continue
for ((i=1; i<MAX_ITER; i++)); do
  echo "Iteration $i of $MAX_ITER..."
  RESULT=$(opencode run $OPENCODE_OPTS --continue "$PROMPT")
  echo "$RESULT"
  
  if [[ "$RESULT" == *"$COMPLETION_PROMISE"* ]]; then
    echo "Task complete."
    exit 0
  fi
done

echo "Max iterations reached. Check progress manually."
