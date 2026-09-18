param([switch]$RequireFinal, [switch]$IncludeContainers)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$python = '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run scripts/setup.ps1 first.' }

function Invoke-Checked {
    param([string]$Label, [scriptblock]$Action)
    Write-Host "  -> $Label" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE." }
}

Invoke-Checked 'Ruff lint' { & $python -m ruff check src tests scripts }
Invoke-Checked 'Ruff format' { & $python -m ruff format --check src tests scripts }
Invoke-Checked 'Python syntax compilation' { & $python scripts/verify_syntax.py }
Invoke-Checked 'mypy strict' { & $python -m mypy src }
Invoke-Checked 'Unit, property, API, red-team, and pilot tests' { & $python -m pytest }
Invoke-Checked 'Sensitive-pattern scan' { & $python scripts/scan_sensitive.py }
if ($RequireFinal) {
    Invoke-Checked 'Locked 90-instance final benchmark and contracts' { & $python scripts/materialize_evidence.py }
    Invoke-Checked 'Final proposal candidate build' { & $python scripts/build_final_bundle.py }
    Invoke-Checked 'Final proposal candidate verification' { & $python scripts/build_final_bundle.py --verify }
}

Push-Location 'apps\web'
try {
    Invoke-Checked 'Web TypeScript' { npm run typecheck }
    Invoke-Checked 'Web lint' { npm run lint }
    Invoke-Checked 'Web production build' { npm run build }
    Invoke-Checked 'Web Playwright evidence, accessibility, and responsive flows' { npm run test:e2e }
}
finally { Pop-Location }

if ($IncludeContainers) {
    Invoke-Checked 'Container smoke' { & "$root\scripts\container-smoke.ps1" }
}
Write-Host 'All Project 57 local quality gates passed.' -ForegroundColor Green
