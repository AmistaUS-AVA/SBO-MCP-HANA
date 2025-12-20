"""MCP Tools for SAP database access."""

from .get_tables import register_get_tables_tool
from .get_columns import register_get_columns_tool
from .run_query import register_run_query_tool
from ..connectors.base import BaseConnector

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None


def register_all_tools(mcp: "FastMCP", connector: BaseConnector, prefix: str) -> None:
    """Register all MCP tools with the server.

    Args:
        mcp: FastMCP server instance
        connector: Database connector
        prefix: Tool name prefix (e.g., "sap_hana")
    """
    register_get_tables_tool(mcp, connector, prefix)
    register_get_columns_tool(mcp, connector, prefix)
    register_run_query_tool(mcp, connector, prefix)


__all__ = [
    "register_all_tools",
    "register_get_tables_tool",
    "register_get_columns_tool",
    "register_run_query_tool",
]
