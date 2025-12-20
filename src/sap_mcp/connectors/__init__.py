"""Database connectors for SAP MCP Server."""

from .base import BaseConnector
from .hana import HanaConnector
from .odbc import OdbcConnector
from ..config import Config


def create_connector(config: Config) -> BaseConnector:
    """Create a database connector based on configuration.

    Args:
        config: Server configuration

    Returns:
        Configured database connector

    Raises:
        ValueError: If connector type is unknown
    """
    connector_type = config.connector_type

    if connector_type == "hana":
        hana_config = config.get_hana_config()
        return HanaConnector(
            host=hana_config.host,
            port=hana_config.port,
            user=hana_config.user,
            password=hana_config.password,
            database_name=hana_config.database_name or None,
            encrypt=hana_config.encrypt,
            ssl_validate=hana_config.sslValidateCertificate,
        )
    elif connector_type == "odbc":
        odbc_config = config.get_odbc_config()
        return OdbcConnector(connection_string=odbc_config.connection_string)
    else:
        raise ValueError(f"Unknown connector type: {connector_type}")


__all__ = ["BaseConnector", "HanaConnector", "OdbcConnector", "create_connector"]
