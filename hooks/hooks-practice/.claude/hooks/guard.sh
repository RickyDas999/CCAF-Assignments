#!/bin/bash
# 1. Read the event Claude Code sends in
EVENT=$(cat)
# 2. Take out just the command Claude wants to run
COMMAND=$(echo "$EVENT" | jq -r '.tool_input.command')
# 3. If the command contains "rm", refuse it
if echo "$COMMAND" | grep -q "rm "; then
    echo "Blocked: deleting files is not allowed in this project" >&2
    exit 2
fi
# 4. Anything else is fine
exit 0