$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$web = Join-Path $root "apps\enterprise-portal"

function Invoke-Gate([string]$Label, [scriptblock]$Action) {
    Write-Host "  -> $Label" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE." }
}

if (-not (Test-Path $python)) { throw "Run .\scripts\setup.ps1 first." }
$env:PYTHONPATH = "$root\src;$root"

Invoke-Gate "Ruff lint" { & $python -m ruff check $root }
Invoke-Gate "Ruff format" { & $python -m ruff format --check $root }
Invoke-Gate "Python syntax compilation" { & $python "$root\scripts\verify_syntax.py" }
Invoke-Gate "mypy strict" { & $python -m mypy }
Invoke-Gate "Unit, API, authorization, and security tests" { & $python -m pytest }
Invoke-Gate "687-case frozen evaluation" { & $python "$root\scripts\run_evaluation.py" }
Invoke-Gate "Sensitive-material scan" { & $python "$root\scripts\scan_sensitive.py" }
Invoke-Gate "OpenAPI snapshot" { & $python -c "import json; from enterprise_suite.api import app; from pathlib import Path; p=Path(r'$root')/'contracts'/'openapi'/'openapi.v1alpha1.json'; p.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True)+'\n', encoding='utf-8'); print({'openapi': app.openapi()['openapi'], 'paths': len(app.openapi()['paths'])})" }
Invoke-Gate "Docker Compose model" { docker compose -f "$root\compose.yaml" config --quiet }

Push-Location $web
try {
    Invoke-Gate "Web TypeScript" { npm run typecheck }
    Invoke-Gate "Web lint" { npm run lint }
    $buildDirectory = ".next-quality-$PID"
    $previousDist = $env:NEXT_DIST_DIR
    try {
        $env:NEXT_DIST_DIR = $buildDirectory
        Invoke-Gate "Web production build" { npm run build }
    }
    finally {
        $env:NEXT_DIST_DIR = $previousDist
    }
    Invoke-Gate "Web Playwright evidence, accessibility, and responsive flows" { npm run test:e2e }
}
finally { Pop-Location }

Invoke-Gate "Frozen enterprise-suite-contracts-v1 candidate" { & $python "$root\scripts\build_final_bundle.py" }
Write-Host "All Project 59 quality gates passed." -ForegroundColor Green

