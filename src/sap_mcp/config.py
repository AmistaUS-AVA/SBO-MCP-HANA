"""Configuration loader for SAP MCP Server."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class ServerConfig:
    """Server configuration."""
    name: str
    prefix: str
    version: str = "1.0"
    http_port: int = 8088  # Default HTTP port for SSE transport


@dataclass
class HanaConnectorConfig:
    """SAP HANA connection configuration."""
    type: str = "hana"
    host: str = ""
    port: int = 30013  # System DB port for multi-tenant
    user: str = ""
    password: str = ""
    database_name: str = ""  # Tenant database name for multi-tenant HANA
    encrypt: bool = False
    sslValidateCertificate: bool = True


@dataclass
class OdbcConnectorConfig:
    """ODBC connection configuration."""
    type: str = "odbc"
    connection_string: str = ""


@dataclass
class Config:
    """Main configuration."""
    server: ServerConfig
    connector: dict
    tables: list[str] = field(default_factory=list)
    log_file: Optional[str] = None

    @property
    def connector_type(self) -> str:
        return self.connector.get("type", "hana")

    def get_hana_config(self) -> HanaConnectorConfig:
        """Get HANA connector configuration."""
        return HanaConnectorConfig(
            type="hana",
            host=self.connector.get("host", ""),
            port=self.connector.get("port", 30013),
            user=self.connector.get("user", ""),
            password=self.connector.get("password", ""),
            database_name=self.connector.get("database_name", ""),
            encrypt=self.connector.get("encrypt", False),
            sslValidateCertificate=self.connector.get("sslValidateCertificate", True),
        )

    def get_odbc_config(self) -> OdbcConnectorConfig:
        """Get ODBC connector configuration."""
        return OdbcConnectorConfig(
            type="odbc",
            connection_string=self.connector.get("connection_string", ""),
        )


def load_config(config_path: str) -> Config:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Validate required fields
    if "server" not in data:
        raise ValueError("Missing 'server' section in configuration")
    if "connector" not in data:
        raise ValueError("Missing 'connector' section in configuration")

    server_data = data["server"]
    if "name" not in server_data:
        raise ValueError("Missing 'server.name' in configuration")
    if "prefix" not in server_data:
        raise ValueError("Missing 'server.prefix' in configuration")

    server = ServerConfig(
        name=server_data["name"],
        prefix=server_data["prefix"],
        version=server_data.get("version", "1.0"),
        http_port=server_data.get("http_port", 8088),
    )

    return Config(
        server=server,
        connector=data["connector"],
        tables=data.get("tables", []),
        log_file=data.get("log_file"),
    )


def validate_config(config: Config) -> list[str]:
    """Validate configuration and return list of errors."""
    errors = []

    if not config.server.name:
        errors.append("Server name is required")
    if not config.server.prefix:
        errors.append("Server prefix is required")

    connector_type = config.connector_type

    if connector_type == "hana":
        hana = config.get_hana_config()
        if not hana.host:
            errors.append("HANA host is required")
        if not hana.user:
            errors.append("HANA user is required")
        if not hana.password:
            errors.append("HANA password is required")
    elif connector_type == "odbc":
        odbc = config.get_odbc_config()
        if not odbc.connection_string:
            errors.append("ODBC connection_string is required")
    else:
        errors.append(f"Unknown connector type: {connector_type}")

    return errors
