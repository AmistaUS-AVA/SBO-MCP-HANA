"""SAP MCP Server - Main server module."""

import argparse
import logging
import sys
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .config import load_config, validate_config, Config
from .connectors import create_connector, BaseConnector
from .tools import register_all_tools


logger = logging.getLogger(__name__)

# Default HTTP settings
DEFAULT_HTTP_HOST = "0.0.0.0"
DEFAULT_HTTP_PORT = 8088


class SapMcpServer:
    """SAP MCP Server wrapper class."""

    def __init__(self, config: Config, connector: BaseConnector):
        """Initialize the SAP MCP Server.

        Args:
            config: Server configuration
            connector: Database connector
        """
        self.config = config
        self.connector = connector
        self.mcp = FastMCP(config.server.name)

        # Register all tools
        register_all_tools(self.mcp, connector, config.server.prefix)

    def run(self, transport: str = "stdio", host: str = "0.0.0.0", port: int = 8080) -> None:
        """Run the MCP server.

        Args:
            transport: Transport type ("stdio", "sse", or "streamable-http")
            host: Host to bind to (for HTTP transports)
            port: Port to listen on (for HTTP transports)
        """
        if transport == "stdio":
            self.mcp.run(transport=transport)
        else:
            # For HTTP-based transports (sse, streamable-http)
            # Inspect signature to support different versions of FastMCP
            import inspect
            sig = inspect.signature(self.mcp.run)
            kwargs = {"transport": transport}
            
            if "host" in sig.parameters:
                kwargs["host"] = host
            if "port" in sig.parameters:
                kwargs["port"] = port
                
            if "host" not in sig.parameters and (host != "0.0.0.0" or port != 8080):
                 logger.warning("FastMCP.run() does not accept host/port arguments. Using defaults.")
            
            # CRITICAL FIX for ngrok: Allow specific settings to bypass host validation if possible
            # or try to catch the ValueError. 
            try:
                self.mcp.settings.allowed_hosts = ["*"] 
            except (AttributeError, ValueError):
                logger.warning("Could not set allowed_hosts on FastMCP settings. Host validation might fail for ngrok.")
            
            self.mcp.run(**kwargs)


def create_server(config_path: str) -> SapMcpServer:
    """Create and configure an SAP MCP Server instance.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Configured SapMcpServer instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    # Load configuration
    config = load_config(config_path)

    # Validate configuration
    errors = validate_config(config)
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    # Setup logging if configured
    if config.log_file:
        logging.basicConfig(
            filename=config.log_file,
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info("SAP MCP Server starting with config: %s", config_path)

    # Create database connector
    connector = create_connector(config)

    # Test connection
    if not connector.test_connection():
        error_msg = "Failed to connect to database."
        if hasattr(connector, 'get_last_error'):
            error_msg += f"\nDetails: {connector.get_last_error()}"
        error_msg += "\n\nPlease check your configuration."
        raise ConnectionError(error_msg)

    logger.info("Database connection successful")

    # Create and return server
    return SapMcpServer(config, connector)


def main() -> None:
    """Main entry point for the SAP MCP Server."""
    parser = argparse.ArgumentParser(
        description="SAP MCP Server - Connect AI to SAP HANA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio (for Claude Desktop local)
  python -m sap_mcp config.yaml

  # Run with HTTP (for remote access via ngrok)
  python -m sap_mcp config.yaml --transport sse --port 8080

  # Then expose via ngrok:
  ngrok http 8080
        """
    )
    parser.add_argument("config", help="Path to YAML configuration file")
    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--host", "-H",
        default=DEFAULT_HTTP_HOST,
        help=f"Host to bind to for HTTP transports (default: {DEFAULT_HTTP_HOST})"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=DEFAULT_HTTP_PORT,
        help=f"Port for HTTP transports (default: {DEFAULT_HTTP_PORT})"
    )

    args = parser.parse_args()

    try:
        server = create_server(args.config)

        if args.transport != "stdio":
            print(f"Starting MCP server on http://{args.host}:{args.port}", file=sys.stderr)
            print(f"Transport: {args.transport}", file=sys.stderr)
            print("Use ngrok to expose: ngrok http {args.port}", file=sys.stderr)

        server.run(transport=args.transport, host=args.host, port=args.port)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error:\n{e}", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as e:
        print(f"Connection Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
        sys.exit(0)
