param([switch]$SkipSetup)
$ErrorActionPreference = 'Stop'
if (-not $SkipSetup) { & (Join-Path $PSScriptRoot 'setup.ps1') }
& (Join-Path $PSScriptRoot 'quality-gate.ps1')
Write-Host 'Project 55 technical delivery is verified; company-vision-v1 is a review candidate.' -ForegroundColor Green
Write-Host 'No approval, interview, commit, publication, deployment or Project 56 action was performed.'
