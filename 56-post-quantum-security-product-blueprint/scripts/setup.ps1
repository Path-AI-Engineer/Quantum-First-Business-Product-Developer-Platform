param([switch]$SkipWeb)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$basePython = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
if (-not (Test-Path -LiteralPath $basePython)) {
    throw "Python 3.13 not found at $basePython. Install Python 3.13 before setup."
}
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $basePython -m venv (Join-Path $root ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
}
& $venvPython -m ensurepip --upgrade
if ($LASTEXITCODE -ne 0) { throw "ensurepip failed." }
& $venvPython -m pip install --disable-pip-version-check -e "$root[dev]"
if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }
if (-not $SkipWeb) {
    Push-Location (Join-Path $root "apps\web")
    try {
        if (Test-Path "package-lock.json") { npm ci --no-audit --no-fund }
        else { npm install --no-audit --no-fund }
        if ($LASTEXITCODE -ne 0) { throw "Web dependency installation failed." }
    } finally { Pop-Location }
}
Write-Host "Project 56 local dependencies are ready." -ForegroundColor Green
