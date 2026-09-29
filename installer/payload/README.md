# SAP MCP Server (Python)

A Python-based Model Context Protocol (MCP) Server for SAP HANA and SQL databases. This allows AI clients like Claude Desktop to query live data from SAP systems.

## Features

- **SAP HANA support** via `hdbcli` (SAP's official Python client)
- **Generic SQL support** via ODBC for other databases
- **Read-only access** - Only SELECT queries are allowed
- **CSV output** - Results formatted for easy AI consumption
- **Simple YAML configuration**

## Prerequisites

- Python 3.10 or higher
- SAP HANA client libraries (for HANA connections)
- ODBC drivers (for ODBC connections)

## Installation

### 1. Clone or download this project

```bash
cd D:\_projects\sap-mcp-server-python
```

### 2. Install the package

**For SAP HANA:**
```bash
pip install -e ".[hana]"
```

**For ODBC connections:**
```bash
pip install -e ".[odbc]"
```

**For both:**
```bash
pip install -e ".[all]"
```

### 3. Install SAP HANA Client (for HANA connections)

The `hdbcli` package requires the SAP HANA Client to be installed:

1. Download from [SAP Development Tools](https://tools.hana.ondemand.com/#hanatools)
2. Install the SAP HANA Client
3. The `hdbcli` package will be available

Alternatively, install directly via pip (if available):
```bash
pip install hdbcli
```

## Configuration

### 1. Create a configuration file

Copy the example configuration:
```bash
cp config.example.yaml config.yaml
```

### 2. Edit the configuration

**For SAP HANA:**
```yaml
server:
  name: sap-hana
  prefix: sap_hana
  version: "1.0"

connector:
  type: hana
  host: your-hana-server.example.com
  port: 30015
  user: SYSTEM
  password: your-password

tables: []
```

**For SAP HANA Cloud:**
```yaml
server:
  name: hana-cloud
  prefix: hana_cloud
  version: "1.0"

connector:
  type: hana
  host: your-instance.hana.ondemand.com
  port: 443
  user: DBADMIN
  password: your-password
  encrypt: true
  sslValidateCertificate: true

tables: []
```

**For ODBC (SQL Server, etc.):**
```yaml
server:
  name: sql-server
  prefix: sql
  version: "1.0"

connector:
  type: odbc
  connection_string: "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=mydb;UID=user;PWD=password"

tables: []
```

## Running the Server

### Standalone test

```bash
python -m sap_mcp config.yaml
```

If the configuration is correct, the server will start and wait for MCP requests via stdin.

### With Claude Desktop

1. Edit Claude Desktop's configuration file:

   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

   **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "sap-hana": {
      "command": "python",
      "args": [
        "-m",
        "sap_mcp",
        "D:\\_projects\\sap-mcp-server-python\\config.yaml"
      ]
    }
  }
}
```

3. Restart Claude Desktop (fully quit and reopen)

4. Look for the MCP tools icon (hammer) in Claude Desktop

## Available Tools

Once configured, the AI client will have access to these tools:

| Tool | Description |
|------|-------------|
| `{prefix}_get_tables` | List all tables/views in the database |
| `{prefix}_get_columns` | List columns for a specific table |
| `{prefix}_run_query` | Execute a SQL SELECT statement |

### Example Usage

Ask Claude:
- "What tables are available in SAP HANA?"
- "Show me the columns in the CUSTOMERS table"
- "Get the top 10 orders by value"

## Configuration Reference

| Field | Required | Description |
|-------|----------|-------------|
| `server.name` | Yes | Name of the MCP server |
| `server.prefix` | Yes | Prefix for tool names (e.g., `sap_hana`) |
| `server.version` | No | Server version (default: "1.0") |
| `connector.type` | Yes | Connector type: `hana` or `odbc` |
| `connector.host` | HANA | HANA server hostname |
| `connector.port` | HANA | HANA server port (default: 30015) |
| `connector.user` | HANA | Database username |
| `connector.password` | HANA | Database password |
| `connector.encrypt` | No | Enable SSL encryption (default: false) |
| `connector.sslValidateCertificate` | No | Validate SSL cert (default: true) |
| `connector.connection_string` | ODBC | ODBC connection string |
| `tables` | No | List of tables to expose (empty = all) |
| `log_file` | No | Path to debug log file |

## Troubleshooting

### Server won't start

1. Check that Python 3.10+ is installed: `python --version`
2. Verify the package is installed: `pip show sap-mcp-server`
3. Check configuration file syntax: `python -c "import yaml; yaml.safe_load(open('config.yaml'))"`

### Connection fails

1. Test connectivity to your SAP HANA server
2. Verify credentials are correct
3. For HANA Cloud, ensure `encrypt: true` is set
4. Check firewall rules allow the port

### Tools not showing in Claude Desktop

1. Fully quit Claude Desktop (check Task Manager / Activity Monitor)
2. Verify the config path in `claude_desktop_config.json`
3. Check for typos in the JSON configuration
4. Look at Claude Desktop logs for errors

### Debug logging

Enable logging in your config:
```yaml
log_file: /path/to/debug.log
```

Then check the log file for detailed information.

## Project Structure

```
sap-mcp-server-python/
├── pyproject.toml          # Package configuration
├── config.example.yaml     # Example configuration
├── README.md               # This file
└── src/sap_mcp/
    ├── __init__.py
    ├── __main__.py         # Entry point
    ├── server.py           # MCP server setup
    ├── config.py           # Configuration loader
    ├── csv_utils.py        # CSV formatting
    ├── connectors/
    │   ├── base.py         # Abstract connector
    │   ├── hana.py         # SAP HANA connector
    │   └── odbc.py         # ODBC connector
    └── tools/
        ├── get_tables.py   # List tables tool
        ├── get_columns.py  # List columns tool
        └── run_query.py    # SQL query tool
```

## License

MIT License - See LICENSE file for details.

## Credits

Based on the [CData MCP Server for SAP Business One](https://github.com/cdatasoftware/sap-business-one-mcp-server-by-cdata).
