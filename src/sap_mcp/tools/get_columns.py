"""MCP Tool: Get list of columns for a table."""

from typing import Optional
from ..connectors.base import BaseConnector
from ..csv_utils import to_csv

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None


def register_get_columns_tool(mcp: "FastMCP", connector: BaseConnector, prefix: str) -> None:
    """Register the get_columns tool with the MCP server.

    Args:
        mcp: FastMCP server instance
        connector: Database connector
        prefix: Tool name prefix
    """

    @mcp.tool(name=f"{prefix}_get_columns")
    def get_columns(
        table: str,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
    ) -> str:
        """Retrieves a list of fields, dimensions, or measures (as columns) for an object, entity or collection (table).

        Use the get_tables tool to get a list of available tables.
        The output of the tool will be returned in CSV format, with the first line containing column headers.

        Args:
            table: The table name (required)
            catalog: Optional catalog name
            schema: Optional schema name

        Returns:
            CSV formatted list of columns with columns: Table, Column, DataType, Description
        """
        if not table:
            return "ERROR: table parameter is required"

        try:
            columns = connector.get_columns(table=table, catalog=catalog, schema=schema)

            if not columns:
                return f"No columns found for table: {table}"

            # Determine which columns to include based on data
            output_columns = []
            if any(c.get("Catalog") for c in columns):
                output_columns.append("Catalog")
            if any(c.get("Schema") for c in columns):
                output_columns.append("Schema")
            output_columns.extend(["Table", "Column", "DataType", "Description"])

            return to_csv(columns, output_columns)

        except Exception as e:
            return f"ERROR: {str(e)}"
