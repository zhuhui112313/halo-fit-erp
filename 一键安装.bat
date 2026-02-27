@echo off
chcp 65001 > nul
title HALO-FIT 一键安装

echo ========================================
echo   🟢 HALO-FIT 一键安装程序
echo ========================================
echo.

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到 Python，开始自动安装...
    echo.
    
    echo 下载 Python 安装程序...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'"
    
    echo 正在安装 Python（请稍候...）
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    echo Python 安装完成！
    del python-installer.exe
) else (
    echo 已检测到 Python
    python --version
)

echo.
echo [2/4] 检查 Streamlit...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 正在安装 Streamlit...
    pip install streamlit
) else (
    echo Streamlit 已安装
)

echo.
echo [3/4] 检查依赖包...
pip install pandas openpyxl Pillow -q

echo.
echo [4/4] 创建快捷方式...
echo @echo off > start-halo-fit.bat
echo cd /d "%%~dp0" >> start-halo-fit.bat
echo title HALO-FIT 外贸进销存系统 >> start-halo-fit.bat
echo streamlit run app.py >> start-halo-fit.bat

echo.
echo ========================================
echo   ✅ 安装完成！
echo ========================================
echo.
echo 使用方法：
echo   双击 "start-halo-fit.bat" 启动系统
echo.
echo 默认账号：admin
echo 默认密码：admin123
echo.
echo 按任意键启动系统...
pause >nul

start-halo-fit.bat
