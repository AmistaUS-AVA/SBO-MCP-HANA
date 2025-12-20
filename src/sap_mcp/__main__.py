"""SAP MCP Server - Entry point for running as module."""

import sys
import os

# Handle both module execution and PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    from sap_mcp.server import main
else:
    # Running as module
    from .server import main

if __name__ == "__main__":
    main()
