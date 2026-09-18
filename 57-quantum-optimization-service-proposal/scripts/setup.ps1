param([switch]$SkipWeb)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3.13 -m venv .venv
    }
    else {
        $bootstrap = Join-Path (Split-Path -Parent $root) '56-post-quantum-security-product-blueprint\.venv\Scripts\python.exe'
        if (-not (Test-Path -LiteralPath $bootstrap)) {
            throw 'Python 3.13 was not found. Install Python or run the Project 56 setup first.'
        }
        & $bootstrap -m venv .venv
    }
}
$python = '.venv\Scripts\python.exe'
& $python -m pip --version *> $null
if ($LASTEXITCODE -ne 0) {
    & $python -m ensurepip --upgrade
}
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& $python -m pip install -e '.[dev]'
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }

if (-not $SkipWeb) {
    Push-Location 'apps\web'
    try {
        npm install
        if ($LASTEXITCODE -ne 0) { throw 'Web dependency installation failed.' }
        npx playwright install chromium
        if ($LASTEXITCODE -ne 0) { throw 'Chromium installation failed.' }
    }
    finally { Pop-Location }
}
Write-Host 'Optimization Value Validation Lab dependencies are ready.' -ForegroundColor Green
