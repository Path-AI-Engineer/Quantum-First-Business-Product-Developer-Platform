$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3.13 -m venv .venv
    }
    else {
        $bootstrap = Join-Path (Split-Path -Parent $root) '57-quantum-optimization-service-proposal\.venv\Scripts\python.exe'
        if (-not (Test-Path -LiteralPath $bootstrap)) {
            throw 'Python 3.13 was not found. Install Python or bootstrap Project 57 first.'
        }
        & $bootstrap -m venv .venv
    }
}
$python = '.venv\Scripts\python.exe'
& $python -m pip --version *> $null
if ($LASTEXITCODE -ne 0) {
    & $python -m ensurepip --upgrade
}
& $python -m pip install --upgrade 'pip==26.2.1'
& $python -m pip install -e '.[dev]'
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed with exit code $LASTEXITCODE." }

Push-Location 'apps\portal'
try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "Portal dependency installation failed with exit code $LASTEXITCODE." }
    npx playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw "Playwright browser installation failed with exit code $LASTEXITCODE." }
}
finally { Pop-Location }

Write-Host 'Quantum Developer Platform Reference Lab dependencies are ready.' -ForegroundColor Green
