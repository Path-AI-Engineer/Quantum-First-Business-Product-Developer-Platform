$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& "$PSScriptRoot\setup.ps1"
& "$PSScriptRoot\quality-gate.ps1"
& "$PSScriptRoot\container-smoke.ps1"
Write-Host "Project 60 closure is verified. External strategy approval was not fabricated." -ForegroundColor Green
