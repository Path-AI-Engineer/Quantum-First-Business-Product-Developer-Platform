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

Invoke-Checked 'Ruff lint' { & $python -m ruff check src tests scripts cli sdks/python }
Invoke-Checked 'Ruff format' { & $python -m ruff format --check src tests scripts cli sdks/python }
Invoke-Checked 'Python syntax compilation' { & $python scripts/verify_syntax.py }
Invoke-Checked 'mypy strict' { & $python -m mypy src }
Invoke-Checked 'Unit, property, API, security, and contract tests' { & $python -m pytest }
Invoke-Checked 'Sensitive-pattern scan' { & $python scripts/scan_sensitive.py }
Invoke-Checked 'Docker Compose model' { docker compose config --quiet }

if ($RequireFinal) {
    Invoke-Checked 'Locked platform evaluation campaign' { & $python scripts/run_evaluation.py }
    Invoke-Checked 'Developer platform candidate build' { & $python scripts/build_final_bundle.py }
    Invoke-Checked 'Frozen candidate verification' { & $python scripts/build_final_bundle.py --verify }
}

Push-Location 'apps\portal'
try {
    Invoke-Checked 'Portal TypeScript' { npm run typecheck }
    Invoke-Checked 'Portal lint' { npm run lint }
    Invoke-Checked 'Portal production build' { npm run build }
    Invoke-Checked 'Portal Playwright evidence, accessibility, and responsive flows' { npm run test:e2e }
}
finally { Pop-Location }

if ($IncludeContainers) {
    Invoke-Checked 'Container integration smoke' { & "$root\scripts\container-smoke.ps1" }
}
Write-Host 'All Project 58 local quality gates passed.' -ForegroundColor Green

