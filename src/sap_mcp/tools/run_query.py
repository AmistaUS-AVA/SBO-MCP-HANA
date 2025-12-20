"""MCP Tool: Execute SQL SELECT query."""

from ..connectors.base import BaseConnector
from ..csv_utils import to_csv

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None


def register_run_query_tool(mcp: "FastMCP", connector: BaseConnector, prefix: str) -> None:
    """Register the run_query tool with the MCP server.

    Args:
        mcp: FastMCP server instance
        connector: Database connector
        prefix: Tool name prefix
    """

    @mcp.tool(name=f"{prefix}_run_query")
    def run_query(sql: str) -> str:
        """Execute a SQL SELECT statement.

        Use the get_tables tool to get a list of available tables,
        and the get_columns tool to list table columns.

        The SQL dialect is based on SQL-92.
        Identifiers should be quoted using double quotes ("").
        Valid clauses: SELECT, FROM, WHERE, INNER JOIN, LEFT JOIN, GROUP BY, ORDER BY, LIMIT/OFFSET.

        The output of the tool will be returned in CSV format, with the first line containing column headers.

        Args:
            sql: The SELECT statement to execute

        Returns:
            CSV formatted query results
        """
        if not sql:
            return "ERROR: sql parameter is required"

        # Basic safety check - only allow SELECT statements
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            return "ERROR: Only SELECT statements are allowed"

        # Block dangerous keywords
        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return f"ERROR: {keyword} statements are not allowed"

        try:
            # SAFETY: Enforce a limit if not provided to prevent "compaction failed" on client
            limit_applied = False
            if "LIMIT" not in sql_upper and "TOP" not in sql_upper:
                sql += " LIMIT 50"
                limit_applied = True

            rows = connector.execute_query(sql)

            if not rows:
                return "Query returned no results."

            result_csv = to_csv(rows)
            
            if limit_applied:
                 return f"Note: Query result limited to 50 rows for performance. Use explicit LIMIT to change this.\n\n{result_csv}"
            
            return result_csv

        except Exception as e:
            return f"ERROR: {str(e)}"
