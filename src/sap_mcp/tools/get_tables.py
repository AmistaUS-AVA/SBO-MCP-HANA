"""MCP Tool: Get list of database tables."""

from typing import Optional
from ..connectors.base import BaseConnector
from ..csv_utils import to_csv

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None


def register_get_tables_tool(mcp: "FastMCP", connector: BaseConnector, prefix: str) -> None:
    """Register the get_tables tool with the MCP server.

    Args:
        mcp: FastMCP server instance
        connector: Database connector
        prefix: Tool name prefix
    """

    @mcp.tool(name=f"{prefix}_get_tables")
    def get_tables(
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> str:
        """Retrieves a list of objects, entities, collections, etc. (as tables) available in the data source.

        Use the get_columns tool to list available columns on a table.
        Both catalog and schema are optional parameters.
        The output of the tool will be returned in CSV format, with the first line containing column headers.

        Args:
            catalog: Optional catalog name to filter tables
            schema: Optional schema name to filter tables
            search: Optional search term to filter table names (e.g., 'ITM', 'ORD')
            limit: Maximum number of tables to return (default: 50)

        Returns:
            CSV formatted list of tables with columns: Schema, Table, Description
        """
        try:
            # We are passing search and limit to the connector now, which must be updated as well
            tables = connector.get_tables(catalog=catalog, schema=schema, search=search, limit=limit)

            if not tables:
                return "No tables found."

            # Determine which columns to include based on data
            columns = []
            if any(t.get("Catalog") for t in tables):
                columns.append("Catalog")
            if any(t.get("Schema") for t in tables):
                columns.append("Schema")
            columns.extend(["Table", "Description"])

            return to_csv(tables, columns)

        except Exception as e:
            return f"ERROR: {str(e)}"
