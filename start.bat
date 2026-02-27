@echo off
chcp 65001 > nul
title HALO-FIT 外贸进销存系统

echo ========================================
echo   🟢 HALO-FIT 外贸进销存系统
echo ========================================
echo.
echo 正在启动系统...
echo.

cd /d "%~dp0"

REM 启动 Streamlit 应用
streamlit run app.py

pause
