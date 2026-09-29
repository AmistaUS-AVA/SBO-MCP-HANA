@echo off
title SAP MCP Server + ngrok
cd /d "%~dp0"

set CONFIG_PATH=%APPDATA%\SAP MCP Server\config.yaml

echo ========================================
echo    SAP MCP Server + ngrok Launcher
echo ========================================
echo.
echo Config: %CONFIG_PATH%
echo.

REM Check for config
if not exist "%CONFIG_PATH%" (
    echo ERROR: config.yaml not found!
    echo.
    echo Expected location: %CONFIG_PATH%
    echo.
    echo Please use Start Menu ^> SAP MCP Server ^> Edit Configuration
    pause
    exit /b 1
)

REM Check for ngrok
where ngrok >nul 2>&1
if errorlevel 1 (
    echo WARNING: ngrok not found in PATH
    echo.
    echo Please install ngrok:
    echo   1. Download from https://ngrok.com/download
    echo   2. Extract to C:\ngrok\ or add to PATH
    echo   3. Run: ngrok config add-authtoken YOUR_TOKEN
    echo.
    echo Starting server only without ngrok...
    echo.
    sap-mcp-server.exe "%CONFIG_PATH%" --transport sse --port 8088
    pause
    exit /b 1
)

echo Starting MCP Server...
start "SAP MCP Server" cmd /k ""%~dp0sap-mcp-server.exe" "%CONFIG_PATH%" --transport sse --port 8088"

echo Waiting for server to start...
timeout /t 3 /nobreak >nul

echo Starting ngrok tunnel...
echo.
echo ========================================
echo Copy the https://xxx.ngrok.io URL below
echo and add to Claude Desktop config:
echo.
echo   {
echo     "mcpServers": {
echo       "sap-hana": {
echo         "url": "https://YOUR-URL/sse"
echo       }
echo     }
echo   }
echo ========================================
echo.

ngrok http 8088
