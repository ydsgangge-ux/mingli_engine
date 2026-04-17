@echo off
chcp 65001 >nul 2>&1
title MingLi Engine
cd /d "%~dp0\mingli_engine"
start http://localhost:18766
python main.py
