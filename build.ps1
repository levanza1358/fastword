$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name FastWord `
  --icon fastword\assets\app.ico `
  --version-file version_info.txt `
  --add-data "fastword\assets;assets" `
  main.py
