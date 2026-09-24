param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $python = Join-Path $projectRoot '.venv\Scripts\python.exe'
    function Invoke-Checked {
        param([string]$Label, [scriptblock]$Action)
        Write-Host "  -> $Label" -ForegroundColor Cyan
        & $Action
        if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE." }
    }
    if (-not (Test-Path -LiteralPath $python)) {
        $basePython = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'
        if (Test-Path -LiteralPath $basePython) {
            Invoke-Checked 'Python 3.13 virtual environment' { & $basePython -m venv .venv }
        } else {
            Invoke-Checked 'Python 3.13 virtual environment' { & py -3.13 -m venv .venv }
        }
    }
    Invoke-Checked 'Python version' { & $python -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 1)' }
    # This probe writes no stderr when pip is absent: safe with Windows PowerShell 5.1 Stop.
    $pipPresent = & $python -c "import importlib.util; print(int(importlib.util.find_spec('pip') is not None))"
    if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the virtual environment.' }
    if ($pipPresent -ne '1') {
        Invoke-Checked 'Bootstrap missing pip' { & $python -m ensurepip --upgrade }
    }
    Invoke-Checked 'Pinned Python dependencies' { & $python -m pip install -r requirements.lock.txt }
    Invoke-Checked 'Install local CLI' { & $python -m pip install --no-deps -e . }
    Invoke-Checked 'Dependency consistency' { & $python -m pip check }
    Push-Location (Join-Path $projectRoot 'apps\web')
    try {
        Invoke-Checked 'Locked frontend dependencies' { & npm.cmd ci --no-fund }
        Invoke-Checked 'Chromium test runtime' { & node node_modules/@playwright/test/cli.js install chromium }
    } finally { Pop-Location }
    Write-Host 'Project 55 dependencies are ready. No training or cloud deployment is required.' -ForegroundColor Green
} finally { Pop-Location }
