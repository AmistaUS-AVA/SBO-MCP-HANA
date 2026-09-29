"""Quick script to test database connection from config.yaml"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sap_mcp.config import load_config
from sap_mcp.connectors import create_connector


def main():
    config_path = Path(__file__).parent / "config.yaml"

    if not config_path.exists():
        print(f"Error: {config_path} not found")
        print("Copy config.sqlserver.example.yaml to config.yaml and edit it")
        return 1

    print(f"Loading config from: {config_path}")
    config = load_config(str(config_path))
    print(f"Connector type: {config.connector_type}")

    print("\nCreating connector...")
    connector = create_connector(config)

    print("Testing connection...")
    try:
        conn = connector.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        success = True
    except Exception as e:
        print(f"\n[FAILED] {e}")
        return 1

    if success:
        print("\n[OK] Connection successful!")

        # Try listing some tables
        print("\nFetching tables (first 5)...")
        try:
            tables = connector.get_tables()[:5]
            if tables:
                for t in tables:
                    schema = t.get("Schema", t.get("Catalog", ""))
                    table = t.get("Table", "")
                    print(f"  - {schema}.{table}")
            else:
                print("  (no tables found)")
        except Exception as e:
            print(f"  Error listing tables: {e}")
        return 0
    else:
        print("\n[FAILED] Connection test returned False")
        return 1


if __name__ == "__main__":
    sys.exit(main())
