#!/bin/sh
set -e

# Whitelist of allowed commands
ALLOWED_COMMANDS=\"uvicorn\"

# Get the command from the arguments
COMMAND=$1

# Check if the command is in the whitelist
if ! echo "$ALLOWED_COMMANDS" | grep -w "$COMMAND" > /dev/null; then
echo "Error: Command not allowed: $COMMAND" >&2
    exit 1
fi

# Execute the command
exec "$@"
