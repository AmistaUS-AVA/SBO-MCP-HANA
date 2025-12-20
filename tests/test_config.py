"""Tests for configuration loading."""

import pytest
import tempfile
import os
from pathlib import Path


def test_load_valid_config():
    """Test loading a valid configuration file."""
    from sap_mcp.config import load_config

    config_content = """
server:
  name: test-server
  prefix: test

connector:
  type: hana
  host: localhost
  port: 30015
  user: testuser
  password: testpass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        f.flush()

        try:
            config = load_config(f.name)
            assert config.server.name == "test-server"
            assert config.server.prefix == "test"
            assert config.connector_type == "hana"

            hana = config.get_hana_config()
            assert hana.host == "localhost"
            assert hana.port == 30015
            assert hana.user == "testuser"
        finally:
            os.unlink(f.name)


def test_load_missing_file():
    """Test loading a non-existent configuration file."""
    from sap_mcp.config import load_config

    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")


def test_validate_missing_host():
    """Test validation catches missing HANA host."""
    from sap_mcp.config import Config, ServerConfig, validate_config

    config = Config(
        server=ServerConfig(name="test", prefix="test"),
        connector={"type": "hana", "user": "user", "password": "pass"},
    )

    errors = validate_config(config)
    assert any("host" in e.lower() for e in errors)


def test_validate_odbc_config():
    """Test validation for ODBC configuration."""
    from sap_mcp.config import Config, ServerConfig, validate_config

    # Missing connection string
    config = Config(
        server=ServerConfig(name="test", prefix="test"),
        connector={"type": "odbc"},
    )

    errors = validate_config(config)
    assert any("connection_string" in e.lower() for e in errors)

    # Valid config
    config = Config(
        server=ServerConfig(name="test", prefix="test"),
        connector={"type": "odbc", "connection_string": "Driver={...}"},
    )

    errors = validate_config(config)
    assert len(errors) == 0
