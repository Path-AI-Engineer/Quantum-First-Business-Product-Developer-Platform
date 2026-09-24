$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& "$PSScriptRoot\setup.ps1"
& "$PSScriptRoot\quality-gate.ps1"
Write-Host "Project 59 technical closure candidate is verified. External approval and executive decisions remain pending." -ForegroundColor Green

