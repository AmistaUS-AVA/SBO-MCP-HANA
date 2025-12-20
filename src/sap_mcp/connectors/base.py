"""Abstract base class for database connectors."""

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Abstract base class for database connectors."""

    @abstractmethod
    def connect(self) -> Any:
        """Create and return a database connection.

        Returns:
            Database connection object
        """
        pass

    @abstractmethod
    def get_tables(
        self,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get list of tables in the database.

        Args:
            catalog: Optional catalog filter
            schema: Optional schema filter

        Returns:
            List of table dictionaries with keys: catalog, schema, table, description
        """
        pass

    @abstractmethod
    def get_columns(
        self,
        table: str,
        catalog: str | None = None,
        schema: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get list of columns for a table.

        Args:
            table: Table name
            catalog: Optional catalog filter
            schema: Optional schema filter

        Returns:
            List of column dictionaries with keys: table, column, data_type, description
        """
        pass

    @abstractmethod
    def execute_query(self, sql: str) -> list[dict[str, Any]]:
        """Execute a SQL SELECT query.

        Args:
            sql: SQL SELECT statement

        Returns:
            List of row dictionaries
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the database connection works.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    def quote_identifier(self, identifier: str) -> str:
        """Quote a SQL identifier.

        Args:
            identifier: Column or table name

        Returns:
            Quoted identifier
        """
        # Default implementation uses double quotes (SQL standard)
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'
