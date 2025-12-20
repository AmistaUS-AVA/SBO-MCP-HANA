@echo off
REM SAP MCP Server - Installation Script for Windows
REM Run this once to set up the environment

echo ========================================
echo    SAP MCP Server - Installation
echo ========================================
echo.

cd /d "%~dp0.."

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install the package
echo Installing SAP MCP Server with HANA support...
echo.
pip install -e ".[hana]"

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation complete!
echo.
echo Next steps:
echo   1. Copy config.example.yaml to config.yaml
echo   2. Edit config.yaml with your HANA connection details
echo   3. Run start-server.bat to start the MCP server
echo   4. Run start-ngrok.bat to create the tunnel
echo ========================================
echo.

REM Create config if it doesn't exist
if not exist "config.yaml" (
    echo Creating config.yaml from example...
    copy config.example.yaml config.yaml
    echo.
    echo IMPORTANT: Edit config.yaml with your HANA credentials!
)

pause
