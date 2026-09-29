; SAP MCP Server - Inno Setup Installer Script
; Uses Python-based configuration wizard with connection testing

#define MyAppName "SAP MCP Server"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Your Company"
#define MyAppURL "https://github.com/your-repo"
#define MyAppExeName "sap-mcp-server.exe"
#define MyAppConfigExe "sap-mcp-config.exe"
#define MyAppDataDir "SAP MCP Server"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist\installer
OutputBaseFilename=SAP-MCP-Server-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "runconfig"; Description: "Run configuration wizard after installation"; Flags: checkedonce

[Dirs]
Name: "{userappdata}\{#MyAppDataDir}"

[Files]
Source: "..\dist\sap-mcp-server.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\sap-mcp-config.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config.example.yaml"; DestDir: "{app}"; DestName: "config.example.yaml"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "run-server.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "run-with-ngrok.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Configure Server"; Filename: "{app}\{#MyAppConfigExe}"
Name: "{group}\Start Server (HTTP mode)"; Filename: "{app}\run-server.bat"
Name: "{group}\Start with ngrok"; Filename: "{app}\run-with-ngrok.bat"
Name: "{group}\Edit Configuration"; Filename: "notepad.exe"; Parameters: "{userappdata}\{#MyAppDataDir}\config.yaml"
Name: "{group}\Open Config Folder"; Filename: "{userappdata}\{#MyAppDataDir}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\run-server.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppConfigExe}"; Description: "Configure SAP HANA connection"; Flags: postinstall nowait skipifsilent; Tasks: runconfig
