#!/usr/bin/env bash
# Starts the dev server in background and saves PID to .devserver.pid
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
# start yarn dev in background
nohup yarn dev > devserver.log 2>&1 &
PID=$!
echo $PID > .devserver.pid
echo "Dev server started with PID $PID (logs: devserver.log)"
