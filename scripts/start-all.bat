@echo off
REM SAP MCP Server - Start Everything
REM This script starts both the MCP server and ngrok in separate windows

echo ========================================
echo    SAP MCP Server - Full Startup
echo ========================================
echo.

cd /d "%~dp0.."

REM Check prerequisites
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

ngrok version >nul 2>&1
if errorlevel 1 (
    echo ERROR: ngrok not found!
    pause
    exit /b 1
)

if not exist "config.yaml" (
    echo ERROR: config.yaml not found!
    pause
    exit /b 1
)

echo Starting MCP Server in new window...
start "SAP MCP Server" cmd /k "cd /d "%~dp0.." && python -m sap_mcp config.yaml --transport sse --port 8080"

echo Waiting 3 seconds for server to start...
timeout /t 3 /nobreak >nul

echo Starting ngrok tunnel in new window...
start "ngrok Tunnel" cmd /k "ngrok http 8080"

echo.
echo ========================================
echo Both services are starting!
echo.
echo 1. Check the MCP Server window for connection status
echo 2. Check the ngrok window for your public URL
echo 3. Copy the ngrok URL to Claude Desktop config
echo ========================================
echo.

pause
