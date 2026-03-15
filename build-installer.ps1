$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

powershell -ExecutionPolicy Bypass -File .\build.ps1

$iscc = $null

$cmd = Get-Command ISCC -ErrorAction SilentlyContinue
if ($cmd) {
  $iscc = $cmd.Source
}

if (-not $iscc) {
  $candidates = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
  )

  foreach ($candidate in $candidates) {
    if (Test-Path $candidate) {
      $iscc = $candidate
      break
    }
  }
}

if (-not $iscc) {
  throw "ISCC.exe was not found. Install Inno Setup 6 first."
}

& $iscc .\installer.iss
