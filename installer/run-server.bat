@echo off
title SAP MCP Server
cd /d "%~dp0"

set CONFIG_PATH=%APPDATA%\SAP MCP Server\config.yaml

echo ========================================
echo    SAP MCP Server
echo ========================================
echo.
echo Config: %CONFIG_PATH%
echo.

if not exist "%CONFIG_PATH%" (
    echo ERROR: config.yaml not found!
    echo.
    echo Expected location: %CONFIG_PATH%
    echo.
    echo Please use Start Menu ^> SAP MCP Server ^> Edit Configuration
    echo to create and edit your configuration.
    echo.
    pause
    exit /b 1
)

echo Starting server on http://localhost:8088
echo.
echo To connect remotely, run ngrok in another terminal:
echo   ngrok http 8088
echo.
echo Press Ctrl+C to stop.
echo ========================================
echo.

sap-mcp-server.exe "%CONFIG_PATH%" --transport sse --port 8088

pause
