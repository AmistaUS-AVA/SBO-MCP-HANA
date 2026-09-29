@echo off
REM SAP MCP Server - Build Script
REM Creates standalone executable and installer

echo ========================================
echo    SAP MCP Server - Build Process
echo ========================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Install build dependencies
echo Installing build dependencies...
pip install pyinstaller

REM Build executable
echo.
echo Building executable with PyInstaller...
pyinstaller --clean sap_mcp.spec

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo.
echo Executable: dist\sap-mcp-server.exe
echo.
echo To create installer:
echo   1. Install Inno Setup from https://jrsoftware.org/isinfo.php
echo   2. Open installer\setup.iss in Inno Setup
echo   3. Click Build ^> Compile
echo.
echo Or run: iscc installer\setup.iss
echo ========================================
echo.

REM Try to build installer if Inno Setup is available
where iscc >nul 2>&1
if not errorlevel 1 (
    echo Inno Setup found, building installer...
    iscc installer\setup.iss
    echo.
    echo Installer created: dist\installer\SAP-MCP-Server-Setup-1.0.0.exe
)

pause
