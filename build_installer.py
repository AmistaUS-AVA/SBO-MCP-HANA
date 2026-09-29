"""Build script for SAP MCP Server installer.

Creates a Python-based installer that bundles the server as a payload.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


def run_command(cmd, cwd=None):
    """Run a command and check for errors."""
    print(f"  > {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")


def main():
    root_dir = Path(__file__).parent
    src_dir = root_dir / "src"
    installer_dir = root_dir / "installer"
    dist_dir = root_dir / "dist"

    version = datetime.now().strftime("%Y.%m.%d")
    print(f"\n{'='*50}")
    print(f"Building SAP MCP Server Installer {version}")
    print(f"{'='*50}\n")

    # 1. Build the main server executable
    print("[1/4] Building server executable...")
    run_command(f"py -m PyInstaller sap_mcp.spec --noconfirm", cwd=root_dir)

    server_exe = dist_dir / "sap-mcp-server.exe"
    if not server_exe.exists():
        raise FileNotFoundError(f"Server build failed: {server_exe} not found")
    print(f"  Server built: {server_exe}")

    # 2. Build the config wizard
    print("\n[2/4] Building config wizard...")
    run_command(
        f"py -m PyInstaller --onefile --console --name sap-mcp-config "
        f"src/sap_mcp/config_wizard.py --paths src "
        f"--hidden-import hdbcli --hidden-import hdbcli.dbapi --hidden-import yaml "
        f"--noconfirm",
        cwd=root_dir
    )

    config_exe = dist_dir / "sap-mcp-config.exe"
    if not config_exe.exists():
        raise FileNotFoundError(f"Config wizard build failed: {config_exe} not found")
    print(f"  Config wizard built: {config_exe}")

    # 3. Prepare payload directory
    print("\n[3/4] Preparing payload...")
    payload_dir = installer_dir / "payload"
    if payload_dir.exists():
        shutil.rmtree(payload_dir)
    payload_dir.mkdir(parents=True)

    # Copy executables
    shutil.copy2(server_exe, payload_dir / "sap-mcp-server.exe")
    shutil.copy2(config_exe, payload_dir / "sap-mcp-config.exe")

    # Copy support files
    shutil.copy2(root_dir / "config.example.yaml", payload_dir / "config.example.yaml")
    shutil.copy2(root_dir / "README.md", payload_dir / "README.md")

    # Write version file
    with open(payload_dir / "VERSION", "w") as f:
        f.write(version)

    print(f"  Payload prepared: {payload_dir}")

    # 4. Build the installer
    print("\n[4/4] Building installer...")

    installer_spec = installer_dir / "installer.spec"
    installer_spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

INSTALLER_DIR = Path(r"{installer_dir}")
PAYLOAD_DIR = INSTALLER_DIR / "payload"

a = Analysis(
    [str(INSTALLER_DIR / 'installer_gui.py')],
    pathex=[str(INSTALLER_DIR)],
    binaries=[],
    datas=[(str(PAYLOAD_DIR), 'payload')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SAP-MCP-Server-Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,  # Console for now (Windows Defender blocks windowed)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    with open(installer_spec, "w") as f:
        f.write(installer_spec_content)

    run_command(f"py -m PyInstaller installer.spec --noconfirm --distpath \"{dist_dir}\"", cwd=installer_dir)

    installer_exe = dist_dir / "SAP-MCP-Server-Setup.exe"
    if not installer_exe.exists():
        raise FileNotFoundError(f"Installer build failed: {installer_exe} not found")

    # Rename with version
    final_name = f"SAP-MCP-Server-Setup-{version}.exe"
    final_path = dist_dir / final_name

    try:
        if final_path.exists():
            final_path.unlink()
        installer_exe.rename(final_path)
    except PermissionError:
        # If rename fails, just use the base name
        print(f"  Warning: Could not rename to {final_name}, using SAP-MCP-Server-Setup.exe")
        final_path = installer_exe

    print(f"\n{'='*50}")
    print(f"Build Complete!")
    print(f"{'='*50}")
    print(f"\nInstaller: {final_path}")
    print(f"Size: {final_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
