param([switch]$IncludeContainers)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& "$root\scripts\setup.ps1"
if ($LASTEXITCODE -ne 0) { throw 'Setup failed.' }
$gateArguments = @{ RequireFinal = $true }
if ($IncludeContainers) { $gateArguments['IncludeContainers'] = $true }
& "$root\scripts\quality-gate.ps1" @gateArguments
if ($LASTEXITCODE -ne 0) { throw 'Quality gate failed.' }
Write-Host 'Project 57 technical candidate is complete and verified locally.' -ForegroundColor Green
