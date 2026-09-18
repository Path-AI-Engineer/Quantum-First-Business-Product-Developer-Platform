param([switch]$IncludeContainers)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& "$root\scripts\setup.ps1"
& "$root\scripts\quality-gate.ps1" -RequireFinal -IncludeContainers:$IncludeContainers
Write-Host 'Project 58 technical closure is verified. No cloud job, release, or deployment was executed.' -ForegroundColor Green

