# HANDOVER – sap-mcp-server-python (SBO-MCP-HANA)

## Purpose / business context
Python MCP (Model Context Protocol) server that gives AI clients (Claude Desktop etc.) read access to SAP HANA (SAP Business One on HANA) or SQL Server / ODBC databases. Exposes three tools: `{prefix}_get_tables`, `{prefix}_get_columns`, `{prefix}_run_query` (SELECT). Based on the CData "MCP Server for SAP Business One" (MIT). Built by AMISTA for internal/customer use; a Windows installer exists for deploying at customer sites. No specific client named in code.

## Tech stack
- Python >= 3.10, `mcp` (FastMCP), `pyyaml`; optional `hdbcli` (HANA), `pyodbc` (ODBC/SQL Server)
- Transports: stdio and HTTP/SSE (default port 8088, intended to be tunnelled via ngrok)
- Packaging: PyInstaller (`*.spec`, gitignored by pattern), Tk config wizard, Inno Setup (`installer/setup.iss`)

## Repository layout
| Path | Purpose |
|---|---|
| `src/sap_mcp/` | Package: `__main__.py` (entry `sap-mcp`), `server.py`, `config.py`, `config_wizard.py`, `connectors/` (`hana.py`, `odbc.py`, `base.py`), `tools/`, `csv_utils.py` |
| `tests/` | pytest (`test_config.py`, `test_csv_utils.py`) |
| `config.example.yaml`, `config.sqlserver.example.yaml` | Config templates |
| `scripts/` | `install.bat`, `start-all.bat` |
| `build.bat`, `build_installer.py` | Build exe + installer |
| `installer/` | `installer_gui.py`, `setup.iss`, `run-server.bat`, `run-with-ngrok.bat`, `payload/` (README, VERSION, example config; built exes are gitignored) |
| `test_connection.py`, `test_sse_local.py`, `inspect_mcp.py` | Ad-hoc dev scripts |

## Setup & running locally
```bash
pip install -e ".[all,dev]"
copy config.example.yaml config.yaml    # edit connection
python -m sap_mcp config.yaml           # stdio server
python test_connection.py               # check DB connectivity
pytest
```
Claude Desktop: add `"command": "python", "args": ["-m", "sap_mcp", "<path>\\config.yaml"]` under `mcpServers`.
HANA requires the SAP HANA client (`hdbcli`).

## Configuration
`config.yaml` (gitignored). Keys: `server.name`, `server.prefix`, `server.version`, `server.http_port`; `connector.type` (`hana` | `odbc`); HANA: `connector.host`, `port`, `database_name`, `user`, `password`; ODBC: `connector.connection_string`; `tables` (allow-list), `log_file`.

## Deployment
- Local: stdio via Claude Desktop.
- Customer: `build.bat` -> PyInstaller exes (`sap-mcp-server.exe`, `sap-mcp-config.exe`) -> Inno Setup installer; `run-with-ngrok.bat` starts the HTTP server and an ngrok tunnel (`ngrok http 8088`) for remote AI clients. Payload VERSION: 2025.12.19.
- `sap-mcp-server-deploy.zip` / `sap-mcp-server-source.zip` in the root are old local packages (gitignored).

## Current status & open items
- Last commits Jan 2026 (config example scrubbed of real host/tenant). Installer, SQL Server example and dev scripts were uncommitted until this handover.
- No TODO list. Unknown whether the installer is currently deployed anywhere.

## Known gotchas
- `.gitignore` ignores `*.spec`, so the PyInstaller spec files are **not** in git – rebuilding from a fresh clone needs them recreated (or remove that ignore rule).
- HTTP/SSE mode has no authentication; exposing it via ngrok exposes DB query access. Use a read-only DB user.
- `installer_gui.py` writes the DB password in plaintext into the generated `config.yaml`.
- Multi-tenant HANA uses the SystemDB port `3<NN>13` plus `database_name`.

## Related projects
- `teamwork-mcp`, `cli_project` (other MCP work)
- `boyumdemotest`, `proactive-intercompany`, `securosys-intercompany` (SAP B1)
