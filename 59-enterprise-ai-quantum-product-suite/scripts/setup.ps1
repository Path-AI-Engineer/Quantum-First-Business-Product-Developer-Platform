$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $root ".venv"
$python = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $python)) {
    $bootstrap = Get-Command py -ErrorAction SilentlyContinue
    if ($bootstrap) {
        & py -3.13 -m venv $venv
    }
    else {
        $fallback = Join-Path (Split-Path -Parent $root) "58-quantum-developer-platform-design\.venv\Scripts\python.exe"
        if (-not (Test-Path $fallback)) { throw "Python 3.13 bootstrap was not found." }
        & $fallback -m venv $venv
    }
}

& $python -m ensurepip --upgrade
& $python -m pip install --disable-pip-version-check --upgrade pip
& $python -m pip install --disable-pip-version-check -e "$root[dev]"

Push-Location (Join-Path $root "apps\enterprise-portal")
try { npm install }
finally { Pop-Location }

Write-Host "Enterprise Quantum Intelligence Suite dependencies are ready." -ForegroundColor Green

