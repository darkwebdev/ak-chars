#!/usr/bin/env bash
# Stops the dev server started by start-dev.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if [ ! -f .devserver.pid ]; then
  echo "No .devserver.pid file found. Is the dev server running?"
  exit 1
fi
PID=$(cat .devserver.pid)
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Sent TERM to $PID"
  sleep 1
  if kill -0 "$PID" 2>/dev/null; then
    kill -9 "$PID" || true
    echo "Sent KILL to $PID"
  fi
else
  echo "Process $PID not running"
fi
rm -f .devserver.pid
echo "Dev server stopped"
