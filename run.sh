#!/usr/bin/env bash

# Resolve Python 3 executable
if command -v python3 &>/dev/null; then
    PY_CMD=python3
elif command -v python &>/dev/null; then
    PY_CMD=python
else
    echo "[ERROR] Python is not installed. Please install Python 3.9+."
    exit 1
fi

# Install dependencies quietly
echo "Checking dependencies..."
$PY_CMD -m pip install -r requirements.txt --quiet

# Launch app
echo "Launching Avii's YT Grabber..."
$PY_CMD main.py
