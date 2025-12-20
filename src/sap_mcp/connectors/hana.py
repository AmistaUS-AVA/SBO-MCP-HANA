"""SAP HANA database connector using hdbcli."""

from typing import Any
from .base import BaseConnector


class HanaConnector(BaseConnector):
    """SAP HANA database connector using hdbcli."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database_name: str | None = None,
        encrypt: bool = False,
        ssl_validate: bool = True,
    ):
        """Initialize HANA connector.

        Args:
            host: HANA server hostname
            port: HANA port (e.g., 30013 for multi-tenant system DB)
            user: Database username
            password: Database password
            database_name: Tenant database name (for multi-tenant HANA)
            encrypt: Enable SSL encryption
            ssl_validate: Validate SSL certificate
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database_name = database_name
        self.encrypt = encrypt
        self.ssl_validate = ssl_validate
        self._connection = None

    def connect(self) -> Any:
        """Create and return a HANA database connection."""
        try:
            from hdbcli import dbapi
        except ImportError:
            raise ImportError(
                "hdbcli is required for HANA connections. "
                "Install with: pip install hdbcli"
            )

        connect_params = {
            "address": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
        }

        # Add database name for multi-tenant connections
        if self.database_name:
            connect_params["databaseName"] = self.database_name

        # Add encryption settings if enabled
        if self.encrypt:
            connect_params["encrypt"] = True
            connect_params["sslValidateCertificate"] = self.ssl_validate

        self._connection = dbapi.connect(**connect_params)
        return self._connection

    def _get_connection(self) -> Any:
        """Get existing connection or create new one."""
        if self._connection is None:
            self.connect()
        return self._connection

    def get_tables(
        self,
        catalog: str | None = None,
        schema: str | None = None,
        search: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get list of tables from HANA.

        Uses HANA's TABLES system view to retrieve table metadata.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Build query for HANA system tables
        sql = """
            SELECT
                SCHEMA_NAME as "Schema",
                TABLE_NAME as "Table",
                COMMENTS as "Description"
            FROM SYS.TABLES
            WHERE 1=1
        """
        params = []

        if schema:
            sql += " AND SCHEMA_NAME = ?"
            params.append(schema)

        if search:
            # Case-insensitive search
            sql += " AND upper(TABLE_NAME) LIKE ?"
            params.append(f"%{search.upper()}%")

        sql += " ORDER BY SCHEMA_NAME, TABLE_NAME"
        
        # Add LIMIT clause
        sql += f" LIMIT {limit}"

        cursor.execute(sql, params)

        tables = []
        for row in cursor:
            tables.append({
                "Schema": row[0],
                "Table": row[1],
                "Description": row[2] or "",
            })

        cursor.close()
        return tables

    def get_columns(
        self,
        table: str,
        catalog: str | None = None,
        schema: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get list of columns for a HANA table.

        Uses HANA's TABLE_COLUMNS system view.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT
                SCHEMA_NAME as "Schema",
                TABLE_NAME as "Table",
                COLUMN_NAME as "Column",
                DATA_TYPE_NAME as "DataType",
                COMMENTS as "Description"
            FROM SYS.TABLE_COLUMNS
            WHERE TABLE_NAME = ?
        """
        params = [table]

        if schema:
            sql += " AND SCHEMA_NAME = ?"
            params.append(schema)

        sql += " ORDER BY POSITION"

        cursor.execute(sql, params)

        columns = []
        for row in cursor:
            columns.append({
                "Schema": row[0],
                "Table": row[1],
                "Column": row[2],
                "DataType": row[3],
                "Description": row[4] or "",
            })

        cursor.close()
        return columns

    def execute_query(self, sql: str) -> list[dict[str, Any]]:
        """Execute a SQL SELECT query on HANA."""
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
        """Test HANA connection by querying DUMMY table."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUMMY")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            # Store the error for later retrieval
            self._last_error = str(e)
            return False

    def get_last_error(self) -> str:
        """Get the last connection error message."""
        return getattr(self, '_last_error', 'Unknown error')

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
