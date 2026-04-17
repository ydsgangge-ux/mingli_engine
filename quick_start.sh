#!/bin/bash
# MingLi Engine - Quick Start (macOS/Linux)
cd "$(dirname "$0")/mingli_engine"

# Open browser after a short delay
(sleep 2 && open "http://localhost:18766" 2>/dev/null || xdg-open "http://localhost:18766" 2>/dev/null) &

python3 main.py
