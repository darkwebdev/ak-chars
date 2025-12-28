#!/bin/bash

# Auto-activate test skill hook
# Detects test-related keywords and instructs Claude to use the test skill

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')

# Check for test-related keywords
if echo "$PROMPT" | grep -qiE '\b(run test|runt test|run the test|execute test|test this|run tests|run the tests|execute tests|yarn test|npm test|test suite)\b'; then
  echo "INSTRUCTION: Use Skill(test) to handle this test request."
fi
