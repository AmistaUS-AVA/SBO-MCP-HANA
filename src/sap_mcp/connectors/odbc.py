"""Generic ODBC database connector using pyodbc."""

from typing import Any
from .base import BaseConnector


class OdbcConnector(BaseConnector):
    """Generic ODBC database connector using pyodbc."""

    def __init__(self, connection_string: str):
        """Initialize ODBC connector.

        Args:
            connection_string: ODBC connection string
        """
        self.connection_string = connection_string
        self._connection = None

    def connect(self) -> Any:
        """Create and return an ODBC database connection."""
        try:
            import pyodbc
        except ImportError:
            raise ImportError(
                "pyodbc is required for ODBC connections. "
                "Install with: pip install pyodbc"
            )

        self._connection = pyodbc.connect(self.connection_string)
        return self._connection

    def _get_connection(self) -> Any:
        """Get existing connection or create new one."""
        if self._connection is None:
            self.connect()
        return self._connection

    def get_tables(
        self, catalog: str | None = None, schema: str | None = None
    ) -> list[dict[str, Any]]:
        """Get list of tables using ODBC metadata.

        Uses the pyodbc cursor.tables() method which queries
        ODBC catalog functions.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Use ODBC catalog function
        tables_cursor = cursor.tables(catalog=catalog, schema=schema)

        tables = []
        for row in tables_cursor:
            # row format: (table_cat, table_schem, table_name, table_type, remarks)
            tables.append({
                "Catalog": row.table_cat or "",
                "Schema": row.table_schem or "",
                "Table": row.table_name,
                "Description": row.remarks or "",
            })

        cursor.close()
        return tables

    def get_columns(
        self,
        table: str,
        catalog: str | None = None,
        schema: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get list of columns using ODBC metadata.

        Uses the pyodbc cursor.columns() method.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Use ODBC catalog function
        columns_cursor = cursor.columns(table=table, catalog=catalog, schema=schema)

        columns = []
        for row in columns_cursor:
            # row contains: table_cat, table_schem, table_name, column_name,
            #               data_type, type_name, column_size, ...
            columns.append({
                "Catalog": row.table_cat or "",
                "Schema": row.table_schem or "",
                "Table": row.table_name,
                "Column": row.column_name,
                "DataType": row.type_name,
                "Description": getattr(row, "remarks", "") or "",
            })

        cursor.close()
        return columns

    def execute_query(self, sql: str) -> list[dict[str, Any]]:
        """Execute a SQL SELECT query via ODBC."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(sql)

        # Get column names from cursor description
        column_names = [desc[0] for desc in cursor.description]

        rows = []
        for row in cursor:
            row_dict = {}
            for i, value in enumerate(row):
                row_dict[column_names[i]] = value
            rows.append(row_dict)

        cursor.close()
        return rows

    def test_connection(self) -> bool:
        """Test ODBC connection with a simple query."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
