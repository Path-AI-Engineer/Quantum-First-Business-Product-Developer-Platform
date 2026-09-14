param([switch]$SkipWeb, [switch]$SkipE2E)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) { throw "Run .\scripts\setup.ps1 first." }

function Assert-Exit([string]$Label) {
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE." }
}

Push-Location $root
try {
    & $python -m ruff check src tests migrations scripts
    Assert-Exit "Ruff lint"
    & $python -m ruff format --check src tests migrations scripts
    Assert-Exit "Ruff format"
    & $python -m mypy src scripts
    Assert-Exit "mypy strict"
    & $python -m pytest -q
    Assert-Exit "Python tests"
    & $python scripts\scan_sensitive.py
    Assert-Exit "Sensitive-pattern scan"
    & $python -m json.tool contracts\standards-profile.v1.json *> $null
    Assert-Exit "Standards JSON contract"
    if (-not $SkipWeb) {
        Push-Location "apps\web"
        try {
            npm run typecheck
            Assert-Exit "Web TypeScript"
            npm run lint
            Assert-Exit "Web lint"
            npm run build
            Assert-Exit "Web production build"
            if (-not $SkipE2E) {
                npm run test:e2e
                Assert-Exit "Web Playwright"
            }
        } finally { Pop-Location }
    }
    & $python scripts\build_bundle.py --verify
    Assert-Exit "Technical candidate source snapshot"
    Write-Host "Project 56 local quality gates passed." -ForegroundColor Green
} finally { Pop-Location }
