
import inspect
try:
    from mcp.server.fastmcp import FastMCP
    print("FastMCP.run signature:", inspect.signature(FastMCP.run))
except ImportError:
    print("Could not import FastMCP")
except Exception as e:
    print(f"Error: {e}")
