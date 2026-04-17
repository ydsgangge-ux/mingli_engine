#!/bin/bash
# MingLi Prediction Engine - macOS/Linux Launcher

echo "========================================"
echo "  MingLi Prediction Engine"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "[1/3] Checking Python3..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.9+"
    echo "macOS: brew install python3"
    echo "Linux: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[2/3] Installing dependencies..."
pip3 install -r mingli_engine/requirements.txt -q 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: Some dependencies failed, trying to continue..."
fi

echo "[3/3] Starting server..."
echo ""
echo "========================================"
echo "  Server: http://localhost:18766"
echo "  Press Ctrl+C to stop"
echo "========================================"
echo ""

cd mingli_engine
python3 main.py
