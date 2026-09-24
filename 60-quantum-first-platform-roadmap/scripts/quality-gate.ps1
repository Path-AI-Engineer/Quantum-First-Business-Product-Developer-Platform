$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$web = Join-Path $root "apps\control-tower"

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
Invoke-Gate "437-case test suite" { & $python -m pytest }
Invoke-Gate "Locked strategy evaluation" { & $python "$root\scripts\run_evaluation.py" }
Invoke-Gate "Canonical repository and reports" { & $python "$root\scripts\materialize_repository.py" }
Invoke-Gate "OpenAPI snapshot" { & $python -c "import json; from strategy_control_tower.api import app; from pathlib import Path; p=Path(r'$root')/'contracts'/'openapi'/'openapi.v1.json'; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True)+'\n', encoding='utf-8'); print({'openapi': app.openapi()['openapi'], 'paths': len(app.openapi()['paths'])})" }
Invoke-Gate "Docker Compose model" { docker compose -f "$root\compose.yaml" config --quiet }

Push-Location $web
try {
    Invoke-Gate "Web TypeScript" { npm run typecheck }
    Invoke-Gate "Web lint" { npm run lint }
    $buildDirectory = ".next-quality-$PID"
    $previousDist = $env:NEXT_DIST_DIR
    $tsconfig = Join-Path $web "tsconfig.json"
    $tsconfigBackup = Join-Path $env:TEMP "p60-tsconfig-$PID.json"
    Copy-Item -LiteralPath $tsconfig -Destination $tsconfigBackup -Force
    try {
        $env:NEXT_DIST_DIR = $buildDirectory
        Invoke-Gate "Web production build" { npm run build }
    }
    finally {
        $env:NEXT_DIST_DIR = $previousDist
        Copy-Item -LiteralPath $tsconfigBackup -Destination $tsconfig -Force
        Remove-Item -LiteralPath $tsconfigBackup -Force
    }
    Invoke-Gate "Web Playwright evidence, accessibility, and responsive flows" { npm run test:e2e }
}
finally { Pop-Location }

Invoke-Gate "Frozen quantum-first-roadmap-v1 candidate" { & $python "$root\scripts\build_final_bundle.py" }
Write-Host "All Project 60 quality gates passed." -ForegroundColor Green
