"""SAP MCP Server - Python-based Installer GUI."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import shutil
import subprocess
from pathlib import Path
import threading
import time

# Hide console window on Windows
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    except Exception:
        pass


class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SAP MCP Server Setup")
        self.root.geometry("600x480")
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 600) // 2
        y = (self.root.winfo_screenheight() - 480) // 2
        self.root.geometry(f"600x480+{x}+{y}")

        # Variables
        self.install_dir = tk.StringVar(value="C:\\SAP_MCP_Server")
        self.host_var = tk.StringVar(value="")
        self.port_var = tk.StringVar(value="30013")
        self.database_var = tk.StringVar(value="")
        self.user_var = tk.StringVar(value="SYSTEM")
        self.password_var = tk.StringVar(value="")
        self.http_port_var = tk.StringVar(value="8088")

        # Styles
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))

        # Main Container
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Content Frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Buttons Frame
        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.pack(fill=tk.X, pady=10)

        self.step = 0
        self.show_step(0)

    def show_step(self, step):
        self.step = step
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.btn_frame.winfo_children():
            widget.destroy()

        if step == 0:
            self.step_welcome()
        elif step == 1:
            self.step_connection()
        elif step == 2:
            self.step_credentials()
        elif step == 3:
            self.step_install()
        elif step == 4:
            self.step_finish()

    def step_welcome(self):
        ttk.Label(self.content_frame, text="SAP MCP Server Setup", style='Header.TLabel').pack(pady=10)
        ttk.Label(self.content_frame, text="This wizard will install the SAP MCP Server on your computer.",
                  wraplength=450).pack(pady=5)

        frame = ttk.LabelFrame(self.content_frame, text="Installation Directory", padding=10)
        frame.pack(fill=tk.X, pady=15)

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill=tk.X)
        ttk.Entry(entry_frame, textvariable=self.install_dir, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(entry_frame, text="Browse...", command=self.browse_dir).pack(side=tk.LEFT, padx=5)

        ttk.Button(self.btn_frame, text="Next >", command=lambda: self.show_step(1)).pack(side=tk.RIGHT)
        ttk.Button(self.btn_frame, text="Cancel", command=self.root.quit).pack(side=tk.LEFT)

    def browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.install_dir.set(d)

    def step_connection(self):
        ttk.Label(self.content_frame, text="SAP HANA Connection", style='Header.TLabel').pack(pady=10)
        ttk.Label(self.content_frame, text="Enter your SAP HANA server connection details.",
                  wraplength=450).pack(pady=5)

        frame = ttk.LabelFrame(self.content_frame, text="Connection Details", padding=15)
        frame.pack(fill=tk.X, pady=20)

        ttk.Label(frame, text="Server Hostname:").grid(row=0, column=0, sticky=tk.W, pady=8)
        ttk.Entry(frame, textvariable=self.host_var, width=35).grid(row=0, column=1, pady=8, padx=10)

        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=8)
        ttk.Entry(frame, textvariable=self.port_var, width=35).grid(row=1, column=1, pady=8, padx=10)
        ttk.Label(frame, text="(30013 for multi-tenant system DB)", font=("Segoe UI", 8),
                  foreground="gray").grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Label(frame, text="Database Name:").grid(row=3, column=0, sticky=tk.W, pady=8)
        ttk.Entry(frame, textvariable=self.database_var, width=35).grid(row=3, column=1, pady=8, padx=10)
        ttk.Label(frame, text="(Tenant database name)", font=("Segoe UI", 8),
                  foreground="gray").grid(row=4, column=1, sticky=tk.W, padx=10)

        ttk.Button(self.btn_frame, text="< Back", command=lambda: self.show_step(0)).pack(side=tk.LEFT)
        ttk.Button(self.btn_frame, text="Next >", command=self.validate_connection).pack(side=tk.RIGHT)

    def validate_connection(self):
        if not self.host_var.get().strip():
            messagebox.showerror("Error", "Server hostname is required.")
            return
        try:
            port = int(self.port_var.get())
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid number (1-65535).")
            return
        self.show_step(2)

    def step_credentials(self):
        ttk.Label(self.content_frame, text="Credentials & Settings", style='Header.TLabel').pack(pady=10)
        ttk.Label(self.content_frame, text="Enter your database credentials and server settings.",
                  wraplength=450).pack(pady=5)

        # Credentials
        cred_frame = ttk.LabelFrame(self.content_frame, text="Database Credentials", padding=15)
        cred_frame.pack(fill=tk.X, pady=10)

        ttk.Label(cred_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=8)
        ttk.Entry(cred_frame, textvariable=self.user_var, width=35).grid(row=0, column=1, pady=8, padx=10)

        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=8)
        ttk.Entry(cred_frame, textvariable=self.password_var, width=35, show="*").grid(row=1, column=1, pady=8, padx=10)

        # HTTP Port
        http_frame = ttk.LabelFrame(self.content_frame, text="MCP Server Settings", padding=15)
        http_frame.pack(fill=tk.X, pady=10)

        ttk.Label(http_frame, text="HTTP Port:").grid(row=0, column=0, sticky=tk.W, pady=8)
        ttk.Entry(http_frame, textvariable=self.http_port_var, width=35).grid(row=0, column=1, pady=8, padx=10)
        ttk.Label(http_frame, text="(For remote access via ngrok)", font=("Segoe UI", 8),
                  foreground="gray").grid(row=1, column=1, sticky=tk.W, padx=10)

        ttk.Button(self.btn_frame, text="< Back", command=lambda: self.show_step(1)).pack(side=tk.LEFT)
        ttk.Button(self.btn_frame, text="Install", command=self.start_install).pack(side=tk.RIGHT)

    def start_install(self):
        if not self.user_var.get().strip():
            messagebox.showerror("Error", "Username is required.")
            return
        self.show_step(3)

    def step_install(self):
        ttk.Label(self.content_frame, text="Installing...", style='Header.TLabel').pack(pady=20)

        self.progress = ttk.Progressbar(self.content_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=20)

        self.status_label = ttk.Label(self.content_frame, text="Starting installation...")
        self.status_label.pack()

        # Start installation thread
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):
        try:
            target_dir = Path(self.install_dir.get())

            # 1. Locate Payload
            self.update_status("Locating installation files...", 10)

            if getattr(sys, 'frozen', False):
                # PyInstaller extracts data to sys._MEIPASS
                script_dir = Path(sys._MEIPASS)
            else:
                script_dir = Path(__file__).parent

            payload_path = script_dir / "payload"
            if not payload_path.exists():
                raise FileNotFoundError(f"Payload not found at {payload_path}")

            # 2. Create target directory
            self.update_status("Creating directories...", 20)
            target_dir.mkdir(parents=True, exist_ok=True)

            # 3. Copy files
            self.update_status("Copying files...", 40)
            for item in payload_path.iterdir():
                dst = target_dir / item.name
                if item.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(item, dst)
                else:
                    shutil.copy2(item, dst)

            # 4. Create config.yaml
            self.update_status("Creating configuration...", 70)
            config_dir = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "SAP MCP Server"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / "config.yaml"

            config_content = f"""# SAP MCP Server Configuration
server:
  name: sap-hana
  prefix: sap_hana
  version: "1.0"
  http_port: {self.http_port_var.get()}

connector:
  type: hana
  host: {self.host_var.get().strip()}
  port: {self.port_var.get()}
  user: {self.user_var.get().strip()}
  password: "{self.password_var.get()}"
"""
            if self.database_var.get().strip():
                config_content += f"  database_name: {self.database_var.get().strip()}\n"

            config_content += "\ntables: []\n"

            with open(config_path, "w") as f:
                f.write(config_content)

            # 5. Create batch files
            self.update_status("Creating launch scripts...", 85)

            http_port = self.http_port_var.get()

            # run-server.bat
            run_server = target_dir / "run-server.bat"
            with open(run_server, "w") as f:
                f.write(f'''@echo off
title SAP MCP Server
cd /d "%~dp0"
set CONFIG_PATH=%APPDATA%\\SAP MCP Server\\config.yaml

echo Starting SAP MCP Server on http://localhost:{http_port}
echo.
echo To connect via ngrok: ngrok http {http_port}
echo.

sap-mcp-server.exe "%CONFIG_PATH%" --transport sse --port {http_port}
pause
''')

            # 6. Create Start Menu shortcuts (using PowerShell)
            self.update_status("Creating shortcuts...", 95)
            try:
                start_menu = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Start Menu" / "Programs" / "SAP MCP Server"
                start_menu.mkdir(parents=True, exist_ok=True)

                # Create shortcut using PowerShell
                ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{start_menu / 'Start Server.lnk'}")
$Shortcut.TargetPath = "{target_dir / 'run-server.bat'}"
$Shortcut.WorkingDirectory = "{target_dir}"
$Shortcut.Save()
'''
                subprocess.run(["powershell", "-Command", ps_script],
                             capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception:
                pass  # Shortcut creation is optional

            self.update_status("Installation complete!", 100)
            self.root.after(500, lambda: self.show_step(4))

        except Exception as e:
            messagebox.showerror("Installation Failed", str(e))
            self.show_step(0)

    def update_status(self, text, value):
        self.root.after(0, lambda: self._update_ui(text, value))

    def _update_ui(self, text, value):
        self.status_label.config(text=text)
        self.progress['value'] = value

    def step_finish(self):
        ttk.Label(self.content_frame, text="Installation Complete!", style='Header.TLabel').pack(pady=20)

        target_dir = Path(self.install_dir.get())
        config_dir = Path(os.environ.get("APPDATA", "")) / "SAP MCP Server"

        ttk.Label(self.content_frame, text="SAP MCP Server has been installed successfully.",
                  wraplength=450).pack(pady=10)

        ttk.Label(self.content_frame, text=f"Installation: {target_dir}", font=("Segoe UI", 9)).pack(pady=2)
        ttk.Label(self.content_frame, text=f"Configuration: {config_dir / 'config.yaml'}", font=("Segoe UI", 9)).pack(pady=2)

        self.run_now = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.content_frame, text="Start Server Now", variable=self.run_now).pack(pady=15)

        ttk.Button(self.btn_frame, text="Finish", command=self.finish_install).pack(side=tk.RIGHT)

    def finish_install(self):
        if self.run_now.get():
            target_dir = Path(self.install_dir.get())
            bat_path = target_dir / "run-server.bat"
            if bat_path.exists():
                subprocess.Popen(["cmd", "/c", str(bat_path)], cwd=str(target_dir))
        self.root.destroy()


def main():
    root = tk.Tk()

    # Use native Windows style
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")

    app = InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
