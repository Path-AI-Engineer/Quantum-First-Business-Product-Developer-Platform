param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run scripts/setup.ps1 first.' }
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'apps\web\.next\BUILD_ID'))) {
    throw 'Run scripts/quality-gate.ps1 to produce and verify the local production build first.'
}
foreach ($port in @(8955, 3055)) {
    if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) {
        throw "Port $port is already in use. No process has been stopped."
    }
}
$runtime = Join-Path $projectRoot '.validation-site\preview'
$null = New-Item -ItemType Directory -Path $runtime -Force
$apiProcess = Start-Process -FilePath $python -ArgumentList @('-m','uvicorn','venture_evidence.api:app','--host','127.0.0.1','--port','8955') -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'api.stdout.log') -RedirectStandardError (Join-Path $runtime 'api.stderr.log')
Push-Location (Join-Path $projectRoot 'apps\web')
try {
    Write-Host 'App: http://127.0.0.1:3055 | Swagger: http://127.0.0.1:8955/docs' -ForegroundColor Cyan
    Write-Host 'Keep this terminal open. Ctrl+C stops the preview and its own API process.'
    & npm.cmd run start
    if ($LASTEXITCODE -ne 0) { throw "Web preview exited with code $LASTEXITCODE." }
} finally {
    Pop-Location
    if (-not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue }
}
