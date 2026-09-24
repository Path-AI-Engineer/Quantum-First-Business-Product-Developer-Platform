$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $root ".venv"
$python = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $python)) {
    $bootstrap = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $bootstrap) {
        $bootstrap = Join-Path (Split-Path -Parent $root) "59-enterprise-ai-quantum-product-suite\.venv\Scripts\python.exe"
    }
    if (-not (Test-Path $bootstrap)) { throw "Python 3.13 bootstrap runtime was not found." }
    & $bootstrap -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}
& $python -m pip --version *> $null
if ($LASTEXITCODE -ne 0) {
    & $python -m ensurepip --upgrade
}
& $python -m pip install --upgrade pip
& $python -m pip install -e "$root[dev]"
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }

$env:PYTHONPATH = "$root\src;$root"
& $python "$root\scripts\materialize_repository.py"
if ($LASTEXITCODE -ne 0) { throw "Canonical repository materialization failed." }

Push-Location (Join-Path $root "apps\control-tower")
try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "Web dependency installation failed." }
    npx playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw "Playwright browser installation failed." }
}
finally { Pop-Location }

Write-Host "Quantum-First Strategy Control Tower dependencies are ready." -ForegroundColor Green
