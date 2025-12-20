"""SAP MCP Server - Configuration Wizard with Connection Testing."""

import os
import sys
import threading

# Hide console window on Windows when running as frozen exe
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    except Exception:
        pass

import tkinter as tk
from tkinter import ttk, messagebox
import yaml


class ConfigWizard:
    """GUI wizard for configuring SAP MCP Server with connection testing."""

    def __init__(self, root):
        self.root = root
        self.root.title("SAP MCP Server - Configuration")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 500) // 2
        self.root.geometry(f"500x500+{x}+{y}")

        # Variables
        self.host_var = tk.StringVar(value="")
        self.port_var = tk.StringVar(value="30013")
        self.database_var = tk.StringVar(value="")
        self.user_var = tk.StringVar(value="SYSTEM")
        self.password_var = tk.StringVar(value="")
        self.server_name_var = tk.StringVar(value="sap-hana")
        self.prefix_var = tk.StringVar(value="sap_hana")
        self.http_port_var = tk.StringVar(value="8088")

        self.create_widgets()

    def create_widgets(self):
        """Create the wizard UI."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="SAP HANA Connection Setup",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Details", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        # Host
        ttk.Label(conn_frame, text="Server Hostname:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(conn_frame, textvariable=self.host_var, width=40).grid(row=0, column=1, pady=5, padx=(10, 0))

        # Port
        ttk.Label(conn_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(conn_frame, textvariable=self.port_var, width=40).grid(row=1, column=1, pady=5, padx=(10, 0))
        ttk.Label(conn_frame, text="(30013 for multi-tenant system DB)", font=("Segoe UI", 8)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        # Database name
        ttk.Label(conn_frame, text="Database Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        db_entry = ttk.Entry(conn_frame, textvariable=self.database_var, width=40)
        db_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        ttk.Label(conn_frame, text="(Tenant DB for multi-tenant)", font=("Segoe UI", 8)).grid(row=4, column=1, sticky=tk.W, padx=(10, 0))

        # Credentials frame
        cred_frame = ttk.LabelFrame(main_frame, text="Credentials", padding="10")
        cred_frame.pack(fill=tk.X, pady=(0, 10))

        # Username
        ttk.Label(cred_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(cred_frame, textvariable=self.user_var, width=40).grid(row=0, column=1, pady=5, padx=(10, 0))

        # Password
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(cred_frame, textvariable=self.password_var, width=40, show="*").grid(row=1, column=1, pady=5, padx=(10, 0))

        # Server settings frame
        server_frame = ttk.LabelFrame(main_frame, text="MCP Server Settings", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 10))

        # Server name
        ttk.Label(server_frame, text="Server Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(server_frame, textvariable=self.server_name_var, width=40).grid(row=0, column=1, pady=5, padx=(10, 0))

        # Tool prefix
        ttk.Label(server_frame, text="Tool Prefix:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(server_frame, textvariable=self.prefix_var, width=40).grid(row=1, column=1, pady=5, padx=(10, 0))

        # HTTP Port
        ttk.Label(server_frame, text="HTTP Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(server_frame, textvariable=self.http_port_var, width=40).grid(row=2, column=1, pady=5, padx=(10, 0))
        ttk.Label(server_frame, text="(For remote access via ngrok)", font=("Segoe UI", 8)).grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="gray")
        self.status_label.pack(pady=5)

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # Test button
        self.test_btn = ttk.Button(btn_frame, text="Test Connection", command=self.test_connection)
        self.test_btn.pack(side=tk.LEFT)

        # Save button
        self.save_btn = ttk.Button(btn_frame, text="Save Configuration", command=self.save_config)
        self.save_btn.pack(side=tk.RIGHT)

        # Cancel button
        ttk.Button(btn_frame, text="Cancel", command=self.root.quit).pack(side=tk.RIGHT, padx=(0, 10))

    def validate_inputs(self):
        """Validate required inputs."""
        if not self.host_var.get().strip():
            messagebox.showerror("Validation Error", "Server hostname is required.")
            return False
        try:
            port = int(self.port_var.get())
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Port must be a number between 1 and 65535.")
            return False
        if not self.user_var.get().strip():
            messagebox.showerror("Validation Error", "Username is required.")
            return False
        try:
            http_port = int(self.http_port_var.get())
            if http_port < 1 or http_port > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "HTTP port must be a number between 1 and 65535.")
            return False
        return True

    def test_connection(self):
        """Test the database connection."""
        if not self.validate_inputs():
            return

        # Disable buttons during test
        self.test_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.status_var.set("Testing connection...")
        self.status_label.config(foreground="gray")
        self.root.update()

        # Run test in background thread
        thread = threading.Thread(target=self._do_connection_test)
        thread.start()

    def _do_connection_test(self):
        """Perform the actual connection test."""
        try:
            from hdbcli import dbapi

            connect_params = {
                "address": self.host_var.get().strip(),
                "port": int(self.port_var.get()),
                "user": self.user_var.get().strip(),
                "password": self.password_var.get(),
            }

            # Add database name for multi-tenant
            if self.database_var.get().strip():
                connect_params["databaseName"] = self.database_var.get().strip()

            # Attempt connection
            conn = dbapi.connect(**connect_params)

            # Test with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUMMY")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result and result[0] == 1:
                self._update_status("Connection successful!", "green")
            else:
                self._update_status("Connection succeeded but test query failed.", "orange")

        except ImportError:
            self._update_status("Error: hdbcli module not installed.", "red")
        except Exception as e:
            error_msg = str(e)
            # Truncate long error messages
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            self._update_status(f"Connection failed: {error_msg}", "red")
        finally:
            # Re-enable buttons
            self.root.after(0, lambda: self.test_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.save_btn.config(state=tk.NORMAL))

    def _update_status(self, message, color):
        """Update status label from background thread."""
        self.root.after(0, lambda: self.status_var.set(message))
        self.root.after(0, lambda: self.status_label.config(foreground=color))

    def get_config_path(self):
        """Get the configuration file path."""
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            config_dir = os.path.join(appdata, "SAP MCP Server")
        else:
            config_dir = os.path.expanduser("~/.config/sap-mcp-server")

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.yaml")

    def save_config(self):
        """Save the configuration to file."""
        if not self.validate_inputs():
            return

        config = {
            "server": {
                "name": self.server_name_var.get().strip(),
                "prefix": self.prefix_var.get().strip(),
                "version": "1.0",
                "http_port": int(self.http_port_var.get())
            },
            "connector": {
                "type": "hana",
                "host": self.host_var.get().strip(),
                "port": int(self.port_var.get()),
                "user": self.user_var.get().strip(),
                "password": self.password_var.get(),
            },
            "tables": []
        }

        # Add database_name if provided
        if self.database_var.get().strip():
            config["connector"]["database_name"] = self.database_var.get().strip()

        config_path = self.get_config_path()

        try:
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            messagebox.showinfo(
                "Configuration Saved",
                f"Configuration saved to:\n{config_path}\n\n"
                "You can now start the SAP MCP Server."
            )
            self.root.quit()

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration:\n{e}")


def main():
    """Main entry point for the configuration wizard."""
    root = tk.Tk()

    # Set Windows-like style if available
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass

    # Use native Windows style
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")

    app = ConfigWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
